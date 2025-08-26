#!/usr/bin/env python
"""测试版本的 PostgreSQL Consumer - 用于测试 pending 消息恢复"""

import asyncio
import json
import logging
import os
import time
import signal
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from collections import defaultdict

import redis.asyncio as redis
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from jettask.webui.config import PostgreSQLConfig, RedisConfig
from jettask.core.consumer_manager import ConsumerManager, ConsumerStrategy
from jettask.core.offline_worker_recovery import OfflineWorkerRecovery

logger = logging.getLogger(__name__)


class TestPostgreSQLConsumer:
    """测试版本的PostgreSQL消费者，用于测试pending消息恢复"""
    
    def __init__(self, pg_config: PostgreSQLConfig, redis_config: RedisConfig, 
                 prefix: str = "jettask", node_id: str = None, 
                 consumer_strategy: ConsumerStrategy = ConsumerStrategy.HEARTBEAT,
                 test_mode: str = None,
                 processing_delay: float = 0,
                 crash_after_messages: int = 0):
        """
        Args:
            test_mode: 测试模式 
                - "slow_process": 模拟缓慢处理
                - "crash_after_n": 处理N条消息后崩溃
                - "normal": 正常处理
            processing_delay: 每条消息的处理延迟（秒）
            crash_after_messages: 处理多少条消息后崩溃（仅在crash_after_n模式下有效）
        """
        self.pg_config = pg_config
        self.redis_config = redis_config
        self.prefix = prefix
        self.redis_client: Optional[Redis] = None
        self.async_engine = None
        self.AsyncSessionLocal = None
        self.consumer_group = f"{prefix}_pg_consumer1"
        
        # 测试配置
        self.test_mode = test_mode or "normal"
        self.processing_delay = processing_delay
        self.crash_after_messages = crash_after_messages
        self.processed_count = 0
        self.queue_processed_count = defaultdict(int)
        self.changes_processed_count = 0
        
        # 节点标识
        import socket
        hostname = socket.gethostname()
        self.node_id = node_id or f"{hostname}_{os.getpid()}"
        
        # 使用 ConsumerManager 来管理 consumer_id
        self.consumer_strategy = consumer_strategy
        self.consumer_manager = None
        self.consumer_id = None
        
        self._running = False
        self._tasks = []
        self._known_queues = set()
        self._consecutive_errors = defaultdict(int)
        
        # 内存中维护已处理的任务ID集合
        self._processed_task_ids = set()
        self._processed_ids_lock = asyncio.Lock()
        self._processed_ids_max_size = 100000
        
        # 待重试的任务更新
        self._pending_updates = {}
        self._pending_updates_lock = asyncio.Lock()
        self._max_pending_updates = 10000
        self._retry_interval = 5
        
        # 动态批次大小
        self.batch_size = 100  # 减小批次便于测试
        self.min_batch_size = 10
        self.max_batch_size = 200
        
    async def start(self):
        """启动消费者"""
        logger.info(f"Starting TEST PostgreSQL consumer on node: {self.node_id}")
        logger.info(f"Test mode: {self.test_mode}, delay: {self.processing_delay}s, crash after: {self.crash_after_messages}")
        
        # 连接Redis
        self.redis_client = await redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=False
        )
        
        # 初始化 ConsumerManager
        import redis as sync_redis
        sync_redis_client = sync_redis.StrictRedis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=True
        )
        
        # 配置 ConsumerManager
        initial_queues = ['TASK_CHANGES']
        consumer_config = {
            'redis_prefix': self.prefix,
            'queues': initial_queues,
            'worker_prefix': 'PG_CONSUMER',
        }
        
        self.consumer_manager = ConsumerManager(
            redis_client=sync_redis_client,
            strategy=self.consumer_strategy,
            config=consumer_config
        )
        
        # 获取稳定的 consumer_id
        self.consumer_id = self.consumer_manager.get_consumer_name('TASK_CHANGES')
        logger.info(f"Using consumer_id: {self.consumer_id} with strategy: {self.consumer_strategy.value}")
        
        # 创建SQLAlchemy异步引擎
        if self.pg_config.dsn.startswith('postgresql://'):
            dsn = self.pg_config.dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            dsn = self.pg_config.dsn
            
        self.async_engine = create_async_engine(
            dsn,
            pool_size=10,
            max_overflow=5,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        # 创建异步会话工厂
        self.AsyncSessionLocal = sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # 初始化数据库架构
        await self._init_database()
        
        self._running = True
        
        # 先进行一次队列发现
        await self._initial_queue_discovery()
        
        # 创建离线worker恢复器
        self.offline_recovery = OfflineWorkerRecovery(
            async_redis_client=self.redis_client,
            redis_prefix=self.prefix,
            worker_prefix='PG_CONSUMER',
            consumer_manager=self.consumer_manager
        )
        
        # 启动消费任务（简化版：只保留必要的任务）
        self._tasks = [
            asyncio.create_task(self._consume_queues()),           # 消费新任务
            asyncio.create_task(self._consume_task_changes()),     # 消费任务变更事件
            asyncio.create_task(self._start_offline_recovery())    # 离线worker恢复服务
        ]
        
        logger.info("TEST PostgreSQL consumer started successfully")
        
    async def stop(self):
        """停止消费者"""
        logger.info("Stopping TEST PostgreSQL consumer...")
        self._running = False
        
        # 停止离线恢复服务
        if hasattr(self, 'offline_recovery'):
            self.offline_recovery.stop()
        
        # 取消所有任务
        for task in self._tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # 清理 ConsumerManager
        if self.consumer_manager:
            try:
                self.consumer_manager.cleanup()
                logger.info(f"Cleaned up ConsumerManager for consumer: {self.consumer_id}")
            except Exception as e:
                logger.error(f"Error cleaning up ConsumerManager: {e}")
        
        # 关闭连接
        if self.redis_client:
            await self.redis_client.close()
        
        if self.async_engine:
            await self.async_engine.dispose()
            
        logger.info("TEST PostgreSQL consumer stopped")
        
    async def _init_database(self):
        """初始化数据库架构"""
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, "schema.sql")
        try:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            async with self.AsyncSessionLocal() as session:
                await session.execute(text(schema_sql))
                await session.commit()
                logger.info("Database schema initialized")
        except FileNotFoundError:
            logger.warning(f"Schema file not found at {schema_path}, skipping initialization")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            
    async def _initial_queue_discovery(self):
        """初始队列发现"""
        try:
            pattern = f"{self.prefix}:QUEUE:*"
            new_queues = set()
            
            async for key in self.redis_client.scan_iter(match=pattern, count=100):
                queue_name = key.decode('utf-8').split(":")[-1]
                new_queues.add(queue_name)
            
            if new_queues:
                all_queues = list(new_queues) + ['TASK_CHANGES']
                
                if self.consumer_manager:
                    self.consumer_manager.config['queues'] = all_queues
                    
                    if self.consumer_strategy == ConsumerStrategy.HEARTBEAT and hasattr(self.consumer_manager, '_heartbeat_strategy'):
                        actual_consumer_id = self.consumer_manager._heartbeat_strategy.consumer_id
                    else:
                        actual_consumer_id = self.consumer_id.rsplit('-', 1)[0] if '-' in self.consumer_id else self.consumer_id
                    
                    worker_key = f"{self.prefix}:{self.consumer_manager.config.get('worker_prefix', 'PG_CONSUMER')}:{actual_consumer_id}"
                    try:
                        self.consumer_manager.redis_client.hset(
                            worker_key, 
                            'queues', 
                            ','.join(all_queues)
                        )
                        logger.info(f"Initial queue discovery - found queues: {all_queues}")
                    except Exception as e:
                        logger.error(f"Error updating initial worker queues: {e}")
                
                self._known_queues = new_queues
                
        except Exception as e:
            logger.error(f"Error in initial queue discovery: {e}")
    
    async def _simulate_processing_delay(self, queue_name: str = None):
        """模拟处理延迟"""
        if self.test_mode == "slow_process" and self.processing_delay > 0:
            logger.info(f"[TEST] Simulating {self.processing_delay}s processing delay for {queue_name or 'message'}")
            await asyncio.sleep(self.processing_delay)
    
    async def _check_crash_condition(self, queue_name: str = None):
        """检查是否应该崩溃"""
        if self.test_mode == "crash_after_n":
            self.processed_count += 1
            if queue_name:
                self.queue_processed_count[queue_name] += 1
                count = self.queue_processed_count[queue_name]
            else:
                self.changes_processed_count += 1
                count = self.changes_processed_count
            
            logger.info(f"[TEST] Processed {count} messages from {queue_name or 'TASK_CHANGES'}")
            
            if self.crash_after_messages > 0 and count >= self.crash_after_messages:
                logger.error(f"[TEST] CRASHING after processing {count} messages from {queue_name or 'TASK_CHANGES'}!")
                # 强制退出进程
                os._exit(1)
    
    async def _consume_queue(self, queue_name: str):
        """消费单个队列的任务（带测试逻辑）"""
        stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        check_backlog = True
        lastid = "0-0"
        
        consumer_name = self.consumer_id
        
        while self._running and queue_name in self._known_queues:
            try:
                myid = lastid if check_backlog else ">"
                
                # 减小批次大小便于测试
                count = 50 if self.test_mode != "normal" else 10000
                
                messages = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    consumer_name,
                    {stream_key: myid},
                    count=count,
                    block=1000 if not check_backlog else 0
                )
                
                if not messages or (messages and len(messages[0][1]) == 0):
                    check_backlog = False
                    continue
                
                if messages:
                    # 模拟处理延迟
                    await self._simulate_processing_delay(queue_name)
                    
                    await self._process_messages(messages)
                    self._consecutive_errors[queue_name] = 0
                    
                    # 检查崩溃条件
                    await self._check_crash_condition(queue_name)
                    
                    if messages[0] and messages[0][1]:
                        lastid = messages[0][1][-1][0].decode('utf-8') if isinstance(messages[0][1][-1][0], bytes) else messages[0][1][-1][0]
                        check_backlog = len(messages[0][1]) >= count
                    
            except redis.ResponseError as e:
                if "NOGROUP" in str(e):
                    try:
                        await self.redis_client.xgroup_create(
                            stream_key, self.consumer_group, id='0', mkstream=True
                        )
                        logger.info(f"Recreated consumer group for queue: {queue_name}")
                        check_backlog = True
                        lastid = "0-0"
                    except:
                        pass
                else:
                    logger.error(f"Redis error for queue {queue_name}: {e}")
                    self._consecutive_errors[queue_name] += 1
                    
                if self._consecutive_errors[queue_name] > 10:
                    logger.warning(f"Too many errors for queue {queue_name}, will retry later")
                    await asyncio.sleep(30)
                    self._consecutive_errors[queue_name] = 0
                    
            except Exception as e:
                logger.error(f"Error consuming queue {queue_name}: {e}", exc_info=True)
                self._consecutive_errors[queue_name] += 1
                await asyncio.sleep(1)
    
    async def _consume_queues(self):
        """启动所有队列的消费任务"""
        queue_tasks = {}
        
        while self._running:
            try:
                for queue in self._known_queues:
                    if queue not in queue_tasks or queue_tasks[queue].done():
                        queue_tasks[queue] = asyncio.create_task(self._consume_queue(queue))
                        logger.info(f"Started consumer task for queue: {queue}")
                
                for queue in list(queue_tasks.keys()):
                    if queue not in self._known_queues:
                        queue_tasks[queue].cancel()
                        del queue_tasks[queue]
                        logger.info(f"Stopped consumer task for removed queue: {queue}")
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in consume_queues manager: {e}")
                await asyncio.sleep(5)
        
        for task in queue_tasks.values():
            task.cancel()
        
        await asyncio.gather(*queue_tasks.values(), return_exceptions=True)
                
    async def _process_messages(self, messages: List):
        """处理消息并保存到PostgreSQL（简化版）"""
        tasks_to_insert = []
        ack_batch = []
        
        for stream_key, stream_messages in messages:
            if not stream_messages:
                continue
                
            stream_key_str = stream_key.decode('utf-8') if isinstance(stream_key, bytes) else stream_key
            queue_name = stream_key_str.split(":")[-1]
            msg_ids_to_ack = []
            
            for msg_id, data in stream_messages:
                try:
                    if not msg_id or not data:
                        continue
                    
                    msg_id_str = msg_id.decode('utf-8') if isinstance(msg_id, bytes) else str(msg_id)
                    
                    logger.info(f"[TEST] Processing message {msg_id_str} from queue {queue_name}")
                    
                    # 简化处理，主要用于测试
                    task_info = {
                        'id': msg_id_str,
                        'queue_name': queue_name,
                        'task_name': 'test_task',
                        'task_data': '{}',
                        'priority': 0,
                        'retry_count': 0,
                        'max_retry': 3,
                        'status': 'pending',
                        'metadata': '{}',
                        'created_at': datetime.now(tz=timezone.utc)
                    }
                    tasks_to_insert.append(task_info)
                    msg_ids_to_ack.append(msg_id)
                    
                except Exception as e:
                    logger.error(f"Error processing message {msg_id}: {e}")
            
            if msg_ids_to_ack:
                ack_batch.append((stream_key, msg_ids_to_ack))
        
        if tasks_to_insert:
            # 简化：不真正插入数据库，只记录日志
            logger.info(f"[TEST] Would insert {len(tasks_to_insert)} tasks to PostgreSQL")
            
            if ack_batch:
                pipeline = self.redis_client.pipeline()
                for stream_key, msg_ids in ack_batch:
                    pipeline.xack(stream_key, self.consumer_group, *msg_ids)
                
                try:
                    await pipeline.execute()
                    total_acked = sum(len(msg_ids) for _, msg_ids in ack_batch)
                    logger.info(f"[TEST] Successfully ACKed {total_acked} messages")
                except Exception as e:
                    logger.error(f"Error executing batch ACK: {e}")
    
    async def _consume_task_changes(self):
        """消费任务变更事件流（支持pending消息恢复）"""
        change_stream_key = f"{self.prefix}:TASK_CHANGES"
        consumer_group = f"{self.prefix}_changes_consumer"
        
        consumer_name = self.consumer_manager.get_consumer_name('pg_consumer')
        
        # 创建消费者组
        try:
            await self.redis_client.xgroup_create(
                change_stream_key, consumer_group, id='0', mkstream=True
            )
            logger.info(f"Created consumer group for task changes stream")
        except redis.ResponseError:
            pass
        
        # 模仿 listen_event_by_task 的写法
        check_backlog = True
        lastid = "0-0"
        batch_size = 20 if self.test_mode != "normal" else 100
        
        while self._running:
            try:
                if check_backlog:
                    myid = lastid
                else:
                    myid = ">"
                
                messages = await self.redis_client.xreadgroup(
                    consumer_group,
                    consumer_name,
                    {change_stream_key: myid},
                    count=batch_size,
                    block=1000 if not check_backlog else 0
                )
                
                if not messages:
                    check_backlog = False
                    continue
                
                if messages and len(messages[0][1]) > 0:
                    check_backlog = len(messages[0][1]) >= batch_size
                else:
                    check_backlog = False
                
                task_ids_to_update = set()
                ack_ids = []
                
                for _, stream_messages in messages:
                    for msg_id, data in stream_messages:
                        try:
                            if isinstance(msg_id, bytes):
                                lastid = msg_id.decode('utf-8')
                            else:
                                lastid = str(msg_id)
                            
                            event_id = data.get(b'event_id')
                            if event_id:
                                if isinstance(event_id, bytes):
                                    event_id = event_id.decode('utf-8')
                                logger.info(f"[TEST] Processing TASK_CHANGES event: {event_id}")
                                task_ids_to_update.add(event_id)
                            ack_ids.append(msg_id)
                        except Exception as e:
                            logger.error(f"Error processing change event {msg_id}: {e}")
                
                if task_ids_to_update:
                    # 模拟处理延迟
                    await self._simulate_processing_delay("TASK_CHANGES")
                    
                    # 简化：不真正更新数据库
                    logger.info(f"[TEST] Would update {len(task_ids_to_update)} tasks from change events")
                    
                    # 检查崩溃条件
                    await self._check_crash_condition("TASK_CHANGES")
                
                if ack_ids:
                    await self.redis_client.xack(change_stream_key, consumer_group, *ack_ids)
                    logger.info(f"[TEST] ACKed {len(ack_ids)} TASK_CHANGES messages")
                
            except redis.ResponseError as e:
                if "NOGROUP" in str(e):
                    try:
                        await self.redis_client.xgroup_create(
                            change_stream_key, consumer_group, id='0', mkstream=True
                        )
                        logger.info(f"Recreated consumer group for task changes stream")
                        check_backlog = True
                        lastid = "0-0"
                    except:
                        pass
                else:
                    logger.error(f"Redis error in consume_task_changes: {e}")
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in consume_task_changes: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def _start_offline_recovery(self):
        """启动离线worker恢复服务"""
        logger.info("Starting offline worker recovery service for PG_CONSUMER")
        
        while self._running:
            try:
                total_recovered = 0
                
                # 恢复普通队列的消息
                for queue in self._known_queues:
                    try:
                        recovered = await self.offline_recovery.recover_offline_workers(
                            queue=queue,
                            current_consumer_name=self.consumer_id,
                            process_message_callback=self._process_recovered_message
                        )
                        
                        if recovered > 0:
                            logger.info(f"[TEST] Recovered {recovered} messages from queue {queue}")
                            total_recovered += recovered
                            
                    except Exception as e:
                        logger.error(f"Error recovering queue {queue}: {e}")
                
                if total_recovered > 0:
                    logger.info(f"[TEST] Total recovered {total_recovered} messages in this cycle")
                
                # 减少扫描频率便于测试
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in offline recovery service: {e}")
                await asyncio.sleep(10)
    
    async def _process_recovered_message(self, msg_id, msg_data, queue, consumer_id):
        """处理恢复的消息"""
        try:
            logger.info(f"[TEST] Processing recovered message {msg_id} from queue {queue}, offline worker {consumer_id}")
            
            # ACK消息
            if queue == 'TASK_CHANGES':
                stream_key = f"{self.prefix}:TASK_CHANGES"
                consumer_group = f"{self.prefix}_changes_consumer"
            else:
                stream_key = f"{self.prefix}:QUEUE:{queue}"
                consumer_group = self.consumer_group
                
            await self.redis_client.xack(stream_key, consumer_group, msg_id)
            logger.info(f"[TEST] ACKed recovered message {msg_id}")
            
        except Exception as e:
            logger.error(f"Error processing recovered message {msg_id}: {e}")


async def run_test_pg_consumer(pg_config: PostgreSQLConfig, redis_config: RedisConfig,
                               test_mode: str = "normal",
                               processing_delay: float = 0,
                               crash_after_messages: int = 0,
                               node_id: str = None):
    """运行测试版PostgreSQL消费者"""
    consumer = TestPostgreSQLConsumer(
        pg_config, 
        redis_config,
        node_id=node_id,
        consumer_strategy=ConsumerStrategy.HEARTBEAT,
        test_mode=test_mode,
        processing_delay=processing_delay,
        crash_after_messages=crash_after_messages
    )
    
    try:
        await consumer.start()
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await consumer.stop()


def main():
    """主入口函数"""
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Test PostgreSQL Consumer')
    parser.add_argument('--mode', choices=['normal', 'slow_process', 'crash_after_n'], 
                       default='normal', help='Test mode')
    parser.add_argument('--delay', type=float, default=0, 
                       help='Processing delay in seconds')
    parser.add_argument('--crash-after', type=int, default=0,
                       help='Crash after processing N messages')
    parser.add_argument('--node-id', type=str, default=None,
                       help='Node ID for this consumer')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    pg_config = PostgreSQLConfig(
        host=os.getenv('JETTASK_PG_HOST', 'localhost'),
        port=int(os.getenv('JETTASK_PG_PORT', '5432')),
        database=os.getenv('JETTASK_PG_DB', 'jettask'),
        user=os.getenv('JETTASK_PG_USER', 'jettask'),
        password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
    )
    
    redis_config = RedisConfig(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        db=int(os.getenv('REDIS_DB', '0')),
        password=os.getenv('REDIS_PASSWORD'),
    )
    
    logger.info(f"Starting test consumer with mode={args.mode}, delay={args.delay}, crash_after={args.crash_after}")
    
    asyncio.run(run_test_pg_consumer(
        pg_config, 
        redis_config,
        test_mode=args.mode,
        processing_delay=args.delay,
        crash_after_messages=args.crash_after,
        node_id=args.node_id
    ))


if __name__ == '__main__':
    main()