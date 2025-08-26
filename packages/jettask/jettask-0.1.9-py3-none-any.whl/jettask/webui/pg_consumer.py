#!/usr/bin/env python
"""简化版的 PostgreSQL Consumer - 只保留必要功能"""

import asyncio
import json
import logging
import os
import time
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


class PostgreSQLConsumer:
    """PostgreSQL消费者，从Redis队列消费任务并持久化到PostgreSQL"""
    
    def __init__(self, pg_config: PostgreSQLConfig, redis_config: RedisConfig, prefix: str = "jettask", 
                 node_id: str = None, consumer_strategy: ConsumerStrategy = ConsumerStrategy.HEARTBEAT):
        self.pg_config = pg_config
        self.redis_config = redis_config
        self.prefix = prefix
        self.redis_client: Optional[Redis] = None
        self.async_engine = None
        self.AsyncSessionLocal = None
        self.consumer_group = f"{prefix}_pg_consumer1"
        
        # 节点标识
        import socket
        hostname = socket.gethostname()
        self.node_id = node_id or f"{hostname}_{os.getpid()}"
        
        # 使用 ConsumerManager 来管理 consumer_id
        self.consumer_strategy = consumer_strategy
        self.consumer_manager = None  # 将在 start() 中初始化
        self.consumer_id = None  # 将从 ConsumerManager 获取
        
        self._running = False
        self._tasks = []
        self._known_queues = set()
        self._consecutive_errors = defaultdict(int)
        
        # 内存中维护已处理的任务ID集合（用于优化查询）
        self._processed_task_ids = set()
        self._processed_ids_lock = asyncio.Lock()  # 保护并发访问
        # 定期清理过期的ID（防止内存无限增长）
        self._processed_ids_max_size = 100000  # 最多保存10万个ID
        self._processed_ids_cleanup_interval = 300  # 每5分钟清理一次
        
        # 待重试的任务更新（任务ID -> 更新信息）
        self._pending_updates = {}
        self._pending_updates_lock = asyncio.Lock()
        self._max_pending_updates = 10000  # 最多保存1万个待重试更新
        self._retry_interval = 5  # 每5秒重试一次
        
        # 动态批次大小
        self.batch_size = 2000
        self.min_batch_size = 500
        self.max_batch_size = 5000
        
    async def start(self):
        """启动消费者"""
        logger.info(f"Starting PostgreSQL consumer (simplified) on node: {self.node_id}")
        
        # 连接Redis
        self.redis_client = await redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=False
        )
        
        # 初始化 ConsumerManager（需要同步的 Redis 客户端）
        import redis as sync_redis
        sync_redis_client = sync_redis.StrictRedis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=True  # 使用字符串模式，与其他组件保持一致
        )
        
        # 配置 ConsumerManager
        # 初始队列列表包含TASK_CHANGES，其他队列会动态添加
        initial_queues = ['TASK_CHANGES']  # TASK_CHANGES是固定的
        consumer_config = {
            'redis_prefix': self.prefix,
            'queues': initial_queues,
            'worker_prefix': 'PG_CONSUMER',  # 使用不同的前缀，与task worker区分开
        }
        
        self.consumer_manager = ConsumerManager(
            redis_client=sync_redis_client,
            strategy=self.consumer_strategy,
            config=consumer_config
        )
        
        # 获取稳定的 consumer_id（使用TASK_CHANGES作为基准队列）
        self.consumer_id = self.consumer_manager.get_consumer_name('TASK_CHANGES')
        logger.info(f"Using consumer_id: {self.consumer_id} with strategy: {self.consumer_strategy.value}")
        
        # 创建SQLAlchemy异步引擎
        if self.pg_config.dsn.startswith('postgresql://'):
            dsn = self.pg_config.dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            dsn = self.pg_config.dsn
            
        self.async_engine = create_async_engine(
            dsn,
            pool_size=50,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        # 预热连接池
        logger.info("Pre-warming database connection pool...")
        async with self.async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        # 创建异步会话工厂
        self.AsyncSessionLocal = sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # 初始化数据库架构
        await self._init_database()
        
        self._running = True
        
        # 先进行一次队列发现，确保ConsumerManager有正确的队列列表
        await self._initial_queue_discovery()
        
        # 创建离线worker恢复器（用于恢复TASK_CHANGES stream的离线消息）
        self.offline_recovery = OfflineWorkerRecovery(
            async_redis_client=self.redis_client,
            redis_prefix=self.prefix,
            worker_prefix='PG_CONSUMER',  # 使用PG_CONSUMER前缀
            consumer_manager=self.consumer_manager
        )
        
        # 启动消费任务（简化版：只保留必要的任务）
        self._tasks = [
            asyncio.create_task(self._consume_queues()),           # 消费新任务
            asyncio.create_task(self._consume_task_changes()),     # 消费任务变更事件
            asyncio.create_task(self._database_maintenance()),     # 数据库维护
            asyncio.create_task(self._retry_pending_updates()),    # 重试待更新的任务
            asyncio.create_task(self._start_offline_recovery())    # 离线worker恢复服务
        ]
        
        # 如果使用 HEARTBEAT 策略，ConsumerManager 会自动管理心跳
        if self.consumer_strategy == ConsumerStrategy.HEARTBEAT and self.consumer_manager:
            # 启动心跳（ConsumerManager 内部会处理）
            logger.info("Heartbeat is managed by ConsumerManager")
        
        logger.info("PostgreSQL consumer started successfully")
        
    async def stop(self):
        """停止消费者"""
        logger.info("Stopping PostgreSQL consumer...")
        self._running = False
        
        # 停止离线恢复服务
        if hasattr(self, 'offline_recovery'):
            self.offline_recovery.stop()  # stop() 不是异步方法
        
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
            
        logger.info("PostgreSQL consumer stopped")
        
    async def _init_database(self):
        """初始化数据库架构"""
        # 使用相对于当前文件的路径
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
        """初始队列发现，在启动时执行一次"""
        try:
            pattern = f"{self.prefix}:QUEUE:*"
            new_queues = set()
            
            async for key in self.redis_client.scan_iter(match=pattern, count=100):
                queue_name = key.decode('utf-8').split(":")[-1]
                new_queues.add(queue_name)
            
            if new_queues:
                # 合并所有队列：TASK_CHANGES + 动态发现的队列
                all_queues = list(new_queues) + ['TASK_CHANGES']
                
                # 更新ConsumerManager的配置
                if self.consumer_manager:
                    self.consumer_manager.config['queues'] = all_queues
                    
                    # 更新worker的队列信息
                    # 获取实际的consumer_id（从心跳策略中）
                    if self.consumer_strategy == ConsumerStrategy.HEARTBEAT and hasattr(self.consumer_manager, '_heartbeat_strategy'):
                        actual_consumer_id = self.consumer_manager._heartbeat_strategy.consumer_id
                    else:
                        # 从consumer_name中提取（格式：consumer_id-queue）
                        actual_consumer_id = self.consumer_id.rsplit('-', 1)[0] if '-' in self.consumer_id else self.consumer_id
                    
                    worker_key = f"{self.prefix}:{self.consumer_manager.config.get('worker_prefix', 'PG_CONSUMER')}:{actual_consumer_id}"
                    try:
                        # 使用同步Redis客户端更新
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
    
    async def _discover_queues(self):
        """定期发现新队列"""
        while self._running:
            try:
                pattern = f"{self.prefix}:QUEUE:*"
                new_queues = set()
                
                async for key in self.redis_client.scan_iter(match=pattern, count=100):
                    queue_name = key.decode('utf-8').split(":")[-1]
                    new_queues.add(queue_name)
                
                # 为新发现的队列创建消费者组
                for queue in new_queues - self._known_queues:
                    stream_key = f"{self.prefix}:QUEUE:{queue}"
                    try:
                        await self.redis_client.xgroup_create(
                            stream_key, self.consumer_group, id='0', mkstream=True
                        )
                        logger.info(f"Created consumer group for new queue: {queue}")
                    except redis.ResponseError:
                        pass
                
                # 更新ConsumerManager的队列列表（同步操作）
                if new_queues != self._known_queues:
                    # 合并所有队列：TASK_CHANGES + 动态发现的队列
                    all_queues = list(new_queues) + ['TASK_CHANGES']
                    
                    # 更新ConsumerManager的配置
                    if self.consumer_manager:
                        self.consumer_manager.config['queues'] = all_queues
                        
                        # 更新worker的队列信息
                        # 获取实际的consumer_id（从心跳策略中）
                        if self.consumer_strategy == ConsumerStrategy.HEARTBEAT and hasattr(self.consumer_manager, '_heartbeat_strategy'):
                            actual_consumer_id = self.consumer_manager._heartbeat_strategy.consumer_id
                        else:
                            # 从consumer_name中提取（格式：consumer_id-queue）
                            actual_consumer_id = self.consumer_id.rsplit('-', 1)[0] if '-' in self.consumer_id else self.consumer_id
                        
                        worker_key = f"{self.prefix}:{self.consumer_manager.config.get('worker_prefix', 'PG_CONSUMER')}:{actual_consumer_id}"
                        try:
                            # 使用同步Redis客户端更新
                            self.consumer_manager.redis_client.hset(
                                worker_key, 
                                'queues', 
                                ','.join(all_queues)
                            )
                            logger.info(f"Updated ConsumerManager queues: {all_queues}")
                        except Exception as e:
                            logger.error(f"Error updating worker queues: {e}")
                
                self._known_queues = new_queues
                await asyncio.sleep(30)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Error discovering queues: {e}")
                await asyncio.sleep(10)
    
    async def _consume_queue(self, queue_name: str):
        """消费单个队列的任务"""
        stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        check_backlog = True
        lastid = "0-0"
        
        # pg_consumer 应该使用统一的 consumer_id，而不是为每个队列创建新的
        # 因为 pg_consumer 的职责是消费所有队列的消息并写入数据库
        # 它不是真正的任务执行者，所以不需要为每个队列创建独立的 consumer
        consumer_name = self.consumer_id
        
        # ConsumerManager会自动处理离线worker的pending消息恢复
        # 不需要手动恢复
        
        while self._running and queue_name in self._known_queues:
            try:
                myid = lastid if check_backlog else ">"
                
                messages = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    consumer_name,  # 使用ConsumerManager管理的consumer_name
                    {stream_key: myid},
                    count=10000,
                    block=1000 if not check_backlog else 0
                )
                
                if not messages or (messages and len(messages[0][1]) == 0):
                    check_backlog = False
                    continue
                
                if messages:
                    await self._process_messages(messages)
                    self._consecutive_errors[queue_name] = 0
                    
                    if messages[0] and messages[0][1]:
                        lastid = messages[0][1][-1][0].decode('utf-8') if isinstance(messages[0][1][-1][0], bytes) else messages[0][1][-1][0]
                        check_backlog = len(messages[0][1]) >= 2000
                    
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
        discover_task = asyncio.create_task(self._discover_queues())
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
        
        discover_task.cancel()
        for task in queue_tasks.values():
            task.cancel()
        
        await asyncio.gather(discover_task, *queue_tasks.values(), return_exceptions=True)
                
    async def _process_messages(self, messages: List):
        """处理消息并保存到PostgreSQL"""
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
                    
                    # 使用公共方法解析消息
                    task_info = self._parse_stream_message(msg_id_str, data, queue_name)
                    if task_info:
                        tasks_to_insert.append(task_info)
                        msg_ids_to_ack.append(msg_id)
                    
                except Exception as e:
                    logger.error(f"Error processing message {msg_id}: {e}")
            
            if msg_ids_to_ack:
                ack_batch.append((stream_key, msg_ids_to_ack))
        
        if tasks_to_insert:
            await self._insert_tasks(tasks_to_insert)
            
            # 将成功插入的任务ID添加到内存集合中
            async with self._processed_ids_lock:
                for task in tasks_to_insert:
                    self._processed_task_ids.add(task['id'])
                
                # 如果集合过大，清理最早的一半
                if len(self._processed_task_ids) > self._processed_ids_max_size:
                    # 只保留最新的一半ID
                    ids_list = list(self._processed_task_ids)
                    keep_count = self._processed_ids_max_size // 2
                    self._processed_task_ids = set(ids_list[-keep_count:])
                    logger.debug(f"Cleaned processed IDs cache, kept {keep_count} most recent IDs")
            
            if ack_batch:
                pipeline = self.redis_client.pipeline()
                for stream_key, msg_ids in ack_batch:
                    pipeline.xack(stream_key, self.consumer_group, *msg_ids)
                
                try:
                    await pipeline.execute()
                    total_acked = sum(len(msg_ids) for _, msg_ids in ack_batch)
                    logger.debug(f"Successfully ACKed {total_acked} messages")
                except Exception as e:
                    logger.error(f"Error executing batch ACK: {e}")
            
    async def _insert_tasks(self, tasks: List[Dict[str, Any]]):
        """批量插入任务到PostgreSQL"""
        if not tasks:
            return
            
        try:
            async with self.AsyncSessionLocal() as session:
                query = text("""
                    INSERT INTO tasks (id, queue_name, task_name, task_data, priority, 
                                     retry_count, max_retry, status, metadata, created_at)
                    VALUES (:id, :queue_name, :task_name, CAST(:task_data AS jsonb), :priority, 
                           :retry_count, :max_retry, :status, CAST(:metadata AS jsonb), :created_at)
                    ON CONFLICT (id) DO NOTHING;
                """)
                
                await session.execute(query, tasks)
                await session.commit()
                logger.info(f"Batch inserted {len(tasks)} tasks to PostgreSQL")
                
        except Exception as e:
            logger.error(f"Error inserting tasks to PostgreSQL: {e}")
    
    async def _consume_task_changes(self):
        """消费任务变更事件流 - 基于事件驱动的更新（支持pending消息恢复）"""
        change_stream_key = f"{self.prefix}:TASK_CHANGES"
        consumer_group = f"{self.prefix}_changes_consumer"
        
        # 使用 ConsumerManager 管理的 consumer name
        # 这样 ConsumerManager 才能正确跟踪和恢复这个流的待处理消息
        consumer_name = self.consumer_manager.get_consumer_name('pg_consumer')
        
        # 创建消费者组
        try:
            await self.redis_client.xgroup_create(
                change_stream_key, consumer_group, id='0', mkstream=True
            )
            logger.info(f"Created consumer group for task changes stream")
        except redis.ResponseError:
            pass
        
        # 模仿 listen_event_by_task 的写法：先处理pending消息，再处理新消息
        check_backlog = True
        lastid = "0-0"
        batch_size = 100
        
        while self._running:
            try:
                # 决定读取位置：如果有backlog，从lastid开始；否则读取新消息
                if check_backlog:
                    myid = lastid
                else:
                    myid = ">"
                
                messages = await self.redis_client.xreadgroup(
                    consumer_group,
                    consumer_name,  # 使用 ConsumerManager 管理的 consumer name
                    {change_stream_key: myid},
                    count=batch_size,
                    block=1000 if not check_backlog else 0  # backlog时不阻塞
                )
                
                if not messages:
                    check_backlog = False
                    continue
                
                # 检查是否还有更多backlog消息
                if messages and len(messages[0][1]) > 0:
                    check_backlog = len(messages[0][1]) >= batch_size
                else:
                    check_backlog = False
                
                task_ids_to_update = set()
                ack_ids = []
                
                for _, stream_messages in messages:
                    for msg_id, data in stream_messages:
                        try:
                            # 更新lastid（无论消息是否处理成功）
                            if isinstance(msg_id, bytes):
                                lastid = msg_id.decode('utf-8')
                            else:
                                lastid = str(msg_id)
                            
                            event_id = data.get(b'event_id')
                            if event_id:
                                if isinstance(event_id, bytes):
                                    event_id = event_id.decode('utf-8')
                                task_ids_to_update.add(event_id)
                            ack_ids.append(msg_id)
                        except Exception as e:
                            logger.error(f"Error processing change event {msg_id}: {e}")
                
                if task_ids_to_update:
                    await self._update_tasks_by_event(list(task_ids_to_update))
                    logger.info(f"Updated {len(task_ids_to_update)} tasks from change events")
                
                if ack_ids:
                    await self.redis_client.xack(change_stream_key, consumer_group, *ack_ids)
                
            except redis.ResponseError as e:
                if "NOGROUP" in str(e):
                    # 如果消费者组不存在，重新创建
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
    
    async def _update_tasks_by_event(self, task_ids: List[str]):
        """基于事件ID批量更新任务状态"""
        if not task_ids:
            return
        
        try:
            pipeline = self.redis_client.pipeline()
            for task_id in task_ids:
                task_key = f"{self.prefix}:TASK:{task_id}"
                pipeline.hgetall(task_key)
            
            redis_values = await pipeline.execute()
            updates = []
            
            for i, task_id in enumerate(task_ids):
                hash_data = redis_values[i]
                
                if not hash_data:
                    continue
                
                update_info = self._parse_task_hash(task_id, hash_data)
                if update_info:
                    updates.append(update_info)
            
            if updates:
                await self._update_tasks(updates)
                logger.debug(f"Updated {len(updates)} tasks from change events")
                
        except Exception as e:
            logger.error(f"Error updating tasks by event: {e}", exc_info=True)
    
    def _parse_task_hash(self, task_id: str, hash_data: dict) -> Optional[dict]:
        """解析Redis Hash数据"""
        update_info = {
            'id': task_id,
            'status': None,
            'result': None,
            'error_message': None,
            'started_at': None,
            'completed_at': None,
            'worker_id': None,
            'execution_time': None,
            'duration': None
        }
        
        try:
            from jettask.utils.serializer import loads_str
            
            hash_dict = {}
            for k, v in hash_data.items():
                key = k.decode('utf-8') if isinstance(k, bytes) else k
                if isinstance(v, bytes):
                    try:
                        value = loads_str(v)
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, ensure_ascii=False)
                        else:
                            value = str(value)
                    except:
                        try:
                            value = v.decode('utf-8')
                        except:
                            value = str(v)
                else:
                    value = v
                hash_dict[key] = value
            
            update_info['status'] = hash_dict.get('status')
            update_info['error_message'] = hash_dict.get('error_msg') or hash_dict.get('exception')
            
            # 转换时间戳
            for time_field in ['started_at', 'completed_at']:
                if hash_dict.get(time_field):
                    try:
                        time_str = hash_dict[time_field]
                        if isinstance(time_str, str) and time_str.startswith("b'") and time_str.endswith("'"):
                            time_str = time_str[2:-1]
                        update_info[time_field] = datetime.fromtimestamp(float(time_str), tz=timezone.utc)
                    except:
                        pass
            
            update_info['worker_id'] = hash_dict.get('consumer') or hash_dict.get('worker_id')
            
            # 转换数值
            for num_field in ['execution_time', 'duration']:
                if hash_dict.get(num_field):
                    try:
                        num_str = hash_dict[num_field]
                        if isinstance(num_str, str) and num_str.startswith("b'") and num_str.endswith("'"):
                            num_str = num_str[2:-1]
                        update_info[num_field] = float(num_str)
                    except:
                        pass
            
            # 处理result
            if 'result' in hash_dict:
                result_str = hash_dict['result']
                if result_str == 'null':
                    update_info['result'] = None
                else:
                    update_info['result'] = result_str
            
            # 只返回有数据的更新
            if any(v is not None for k, v in update_info.items() if k != 'id'):
                return update_info
            
        except Exception as e:
            logger.error(f"Failed to parse hash data for task {task_id}: {e}")
        
        return None
    
    async def _update_tasks(self, updates: List[Dict[str, Any]]):
        """批量更新任务状态（处理竞态条件）"""
        if not updates:
            return
            
        try:
            async with self.AsyncSessionLocal() as session:
                # 使用 executemany 批量更新
                update_query = text("""
                    UPDATE tasks SET
                        status = COALESCE(:status, status),
                        result = COALESCE(CAST(:result AS jsonb), result),
                        error_message = COALESCE(:error_message, error_message),
                        started_at = COALESCE(:started_at, started_at),
                        completed_at = COALESCE(:completed_at, completed_at),
                        worker_id = COALESCE(:worker_id, worker_id),
                        execution_time = COALESCE(:execution_time, execution_time),
                        duration = COALESCE(:duration, duration)
                    WHERE id = :id
                """)
                
                # 批量执行更新
                result = await session.execute(update_query, updates)
                
                # 检查受影响的行数
                updated_count = result.rowcount
                expected_count = len(updates)
                
                # 只有当受影响行数与预期不一致时，才去查询具体哪些记录不存在
                if updated_count < expected_count:
                    task_ids = [u['id'] for u in updates]
                    
                    # 先使用内存集合进行快速过滤
                    async with self._processed_ids_lock:
                        # 过滤出可能存在的ID（在内存集合中的肯定存在）
                        known_existing_ids = set(task_ids) & self._processed_task_ids
                    
                    # 计算可能缺失的ID（不在内存集合中的需要查询确认）
                    potential_missing_ids = set(task_ids) - known_existing_ids
                    
                    if len(known_existing_ids) + updated_count >= expected_count:
                        # 如果已知存在的ID数量加上更新成功的数量已经达到预期，说明没有缺失
                        missing_ids = set()
                        logger.debug(f"Memory cache hit: avoided DB query for {len(known_existing_ids)} IDs")
                    elif potential_missing_ids:
                        # 只查询不在内存集合中的ID，减少查询范围
                        logger.debug(f"Memory cache partial hit: checking {len(potential_missing_ids)} IDs in DB (skipped {len(known_existing_ids)} cached IDs)")
                        check_query = text("""
                            SELECT id FROM tasks WHERE id = ANY(:ids)
                        """)
                        check_result = await session.execute(check_query, {'ids': list(potential_missing_ids)})
                        existing_in_db = {row[0] for row in check_result}
                        
                        # 更新内存集合（发现的新ID加入集合）
                        async with self._processed_ids_lock:
                            self._processed_task_ids.update(existing_in_db)
                        
                        # 找出确实不存在的记录
                        missing_ids = potential_missing_ids - existing_in_db
                    else:
                        missing_ids = set()
                else:
                    # 所有记录都更新成功
                    missing_ids = set()
                
                if missing_ids:
                    # 将缺失的任务更新加入待重试队列，而不是立即创建
                    async with self._pending_updates_lock:
                        # 创建更新信息映射
                        update_map = {u['id']: u for u in updates if u['id'] in missing_ids}
                        
                        for task_id in missing_ids:
                            if task_id in update_map:
                                # 如果已经有旧的更新在队列中，新的更新会覆盖它
                                # 这确保了只有最新的更新会被重试
                                if task_id in self._pending_updates:
                                    logger.debug(f"Replacing old pending update for task {task_id} with newer one")
                                
                                # 保存更新信息，等待重试（会覆盖旧的）
                                self._pending_updates[task_id] = update_map[task_id]
                        
                        # 如果待重试队列过大，清理最早的一半
                        if len(self._pending_updates) > self._max_pending_updates:
                            items = list(self._pending_updates.items())
                            keep_count = self._max_pending_updates // 2
                            self._pending_updates = dict(items[-keep_count:])
                            logger.warning(f"Pending updates queue full, kept {keep_count} most recent items")
                    
                    logger.info(f"Added {len(missing_ids)} task updates to retry queue")
                
                await session.commit()
                
                # if updated_count > 0:
                #     logger.info(f"Updated {updated_count} task statuses {updates=}")
                
        except Exception as e:
            logger.error(f"Error updating task statuses: {e}")
    
    async def _retry_pending_updates(self):
        """定期重试待更新的任务"""
        while self._running:
            try:
                await asyncio.sleep(self._retry_interval)  # 等待一段时间
                
                # 获取待重试的更新
                async with self._pending_updates_lock:
                    if not self._pending_updates:
                        continue
                    
                    # 取出所有待重试的更新
                    pending_items = list(self._pending_updates.items())
                    self._pending_updates.clear()
                
                if pending_items:
                    logger.info(f"Retrying {len(pending_items)} pending task updates")
                    
                    # 重新尝试更新
                    updates = [update_info for _, update_info in pending_items]
                    await self._update_tasks(updates)
                    
            except Exception as e:
                logger.error(f"Error in retry pending updates: {e}")
                await asyncio.sleep(5)
    
    async def _start_offline_recovery(self):
        """启动离线worker恢复服务，恢复离线PG_CONSUMER的消息"""
        logger.info("Starting offline worker recovery service for PG_CONSUMER")
        
        # 等待consumer manager初始化和队列发现
        # await asyncio.sleep(5)
        
        while self._running:
            try:
                total_recovered = 0
                
                # 1. 恢复普通队列的消息
                for queue in self._known_queues:
                    # logger.info(f'{queue=}')
                    try:
                        recovered = await self.offline_recovery.recover_offline_workers(
                            queue=queue,
                            current_consumer_name=self.consumer_id,
                            process_message_callback=self._process_recovered_queue_message
                        )
                        
                        if recovered > 0:
                            logger.info(f"Recovered {recovered} messages from queue {queue}")
                            total_recovered += recovered
                            
                    except Exception as e:
                        logger.error(f"Error recovering queue {queue}: {e}")
                
                # 2. 恢复TASK_CHANGES stream的消息
                recovered = await self._recover_task_changes_offline_messages()
                if recovered > 0:
                    logger.info(f"Recovered {recovered} TASK_CHANGES messages")
                    total_recovered += recovered
                
                if total_recovered > 0:
                    logger.info(f"Total recovered {total_recovered} messages in this cycle")
                
                # 每30秒扫描一次
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in offline recovery service: {e}")
                await asyncio.sleep(10)
    
    async def _recover_task_changes_offline_messages(self) -> int:
        """恢复TASK_CHANGES stream的离线消息"""
        # 使用 OfflineWorkerRecovery 的标准接口
        try:
            # 为TASK_CHANGES定义自定义的队列格式化器
            def task_changes_formatter(queue):
                # 对于TASK_CHANGES，直接返回stream key（不加QUEUE:前缀）
                if queue == 'TASK_CHANGES':
                    return f"{self.prefix}:TASK_CHANGES"
                else:
                    return f"{self.prefix}:QUEUE:{queue}"
            
            # 创建专门用于TASK_CHANGES的恢复器
            task_changes_recovery = OfflineWorkerRecovery(
                async_redis_client=self.redis_client,
                redis_prefix=self.prefix,
                worker_prefix='PG_CONSUMER',
                queue_formatter=task_changes_formatter
            )
            
            # 调用标准的恢复方法
            # TASK_CHANGES作为队列名传入，会被正确处理
            recovered = await task_changes_recovery.recover_offline_workers(
                queue='TASK_CHANGES',  # 这个队列名会用于查找离线worker
                current_consumer_name=self.consumer_id,
                process_message_callback=self._process_recovered_task_change_v2
            )
            
            return recovered
            
        except Exception as e:
            logger.error(f"Error in recover_task_changes_offline_messages: {e}")
            return 0
    
    async def _process_recovered_queue_message(self, msg_id, msg_data, queue, consumer_id):
        """处理恢复的普通队列消息（符合OfflineWorkerRecovery的回调接口）"""
        try:
            logger.info(f"Processing recovered message {msg_id} from queue {queue}, offline worker {consumer_id}")
            
            # 解析任务信息
            task_info = self._parse_stream_message(msg_id, msg_data, queue)
            if task_info:
                # 批量插入到数据库
                await self._batch_insert_tasks([task_info])
                
                # ACK消息
                stream_key = f"{self.prefix}:QUEUE:{queue}"
                await self.redis_client.xack(stream_key, self.consumer_group, msg_id)
                
        except Exception as e:
            logger.error(f"Error processing recovered queue message {msg_id}: {e}")
    
    async def _process_recovered_task_change_v2(self, msg_id, msg_data, queue, consumer_id):
        """处理恢复的TASK_CHANGES消息（符合OfflineWorkerRecovery的回调接口）"""
        try:
            # 解析消息
            event_id = msg_data.get(b'event_id')
            if event_id:
                if isinstance(event_id, bytes):
                    event_id = event_id.decode('utf-8')
                
                logger.info(f"Processing recovered TASK_CHANGES message: {event_id} from offline worker {consumer_id}")
                
                # 更新任务状态
                await self._update_tasks_by_event([event_id])
                
                # ACK消息
                change_stream_key = f"{self.prefix}:TASK_CHANGES"
                consumer_group = f"{self.prefix}_changes_consumer"
                await self.redis_client.xack(change_stream_key, consumer_group, msg_id)
                
        except Exception as e:
            logger.error(f"Error processing recovered task change {msg_id}: {e}")
    
    async def _database_maintenance(self):
        """定期执行数据库维护任务"""
        last_analyze_time = 0
        analyze_interval = 7200  # 每2小时执行一次ANALYZE
        
        while self._running:
            try:
                current_time = time.time()
                
                if current_time - last_analyze_time > analyze_interval:
                    async with self.AsyncSessionLocal() as session:
                        logger.info("Running ANALYZE on tasks table...")
                        await session.execute(text("ANALYZE tasks"))
                        await session.commit()
                        logger.info("ANALYZE completed successfully")
                        last_analyze_time = current_time
                
                await asyncio.sleep(300)  # 每5分钟检查一次
                
            except Exception as e:
                logger.error(f"Error in database maintenance: {e}")
                await asyncio.sleep(60)
    
    def _parse_stream_message(self, task_id: str, data: dict, queue_name: str) -> Optional[dict]:
        """解析Stream消息为任务信息（返回完整的字段）"""
        try:
            from jettask.utils.serializer import loads_str
            
            if b'data' in data:
                task_data = loads_str(data[b'data'])
            else:
                task_data = {}
                for k, v in data.items():
                    key = k.decode('utf-8') if isinstance(k, bytes) else k
                    if isinstance(v, bytes):
                        try:
                            value = loads_str(v)
                        except:
                            value = str(v)
                    else:
                        value = v
                    task_data[key] = value
            
            task_name = task_data.get('name', task_data.get('task', 'unknown'))
            created_at = None
            if 'trigger_time' in task_data:
                try:
                    timestamp = float(task_data['trigger_time'])
                    created_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                except:
                    pass
            
            # 返回完整的字段，包括所有可能为None的字段
            return {
                'id': task_id,
                'queue_name': queue_name,
                'task_name': task_name,
                'task_data': json.dumps(task_data),
                'priority': int(task_data.get('priority', 0)),
                'retry_count': int(task_data.get('retry', 0)),
                'max_retry': int(task_data.get('max_retry', 3)),
                'status': 'pending',
                'result': None,  # 新任务没有结果
                'error_message': None,  # 新任务没有错误信息
                'created_at': created_at,
                'started_at': None,  # 新任务还未开始
                'completed_at': None,  # 新任务还未完成
                'worker_id': None,  # 新任务还未分配worker
                'execution_time': None,  # 新任务还没有执行时间
                'duration': None,  # 新任务还没有持续时间
                'metadata': json.dumps(task_data.get('metadata', {}))
            }
        except Exception as e:
            logger.error(f"Error parsing stream message for task {task_id}: {e}")
            return None
    


async def run_pg_consumer(pg_config: PostgreSQLConfig, redis_config: RedisConfig, 
                         consumer_strategy: ConsumerStrategy = ConsumerStrategy.HEARTBEAT):
    """运行PostgreSQL消费者"""
    consumer = PostgreSQLConsumer(pg_config, redis_config, consumer_strategy=consumer_strategy)
    
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
    from dotenv import load_dotenv
    
    load_dotenv()
    
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
    
    # 从环境变量获取消费者策略，默认使用 HEARTBEAT
    strategy_name = os.getenv('JETTASK_CONSUMER_STRATEGY', 'HEARTBEAT').upper()
    consumer_strategy = ConsumerStrategy.HEARTBEAT  # 默认
    
    if strategy_name == 'FIXED':
        consumer_strategy = ConsumerStrategy.FIXED
    elif strategy_name == 'POD':
        consumer_strategy = ConsumerStrategy.POD
    elif strategy_name == 'HEARTBEAT':
        consumer_strategy = ConsumerStrategy.HEARTBEAT
    else:
        logger.warning(f"Unknown consumer strategy: {strategy_name}, using HEARTBEAT")
    
    logger.info(f"Using consumer strategy: {consumer_strategy.value}")
    
    asyncio.run(run_pg_consumer(pg_config, redis_config, consumer_strategy))


if __name__ == '__main__':
    main()