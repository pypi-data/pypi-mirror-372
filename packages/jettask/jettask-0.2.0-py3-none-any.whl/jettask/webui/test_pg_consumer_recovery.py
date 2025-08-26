#!/usr/bin/env python
"""测试PG Consumer的恢复机制"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone

import redis.asyncio as redis
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from jettask.webui.config import PostgreSQLConfig, RedisConfig
from jettask.core.consumer_manager import ConsumerManager, ConsumerStrategy
from jettask.utils.serializer import dumps_str

logger = logging.getLogger(__name__)

class TestHelper:
    """测试辅助类"""
    
    def __init__(self, pg_config: PostgreSQLConfig, redis_config: RedisConfig, prefix: str = "jettask"):
        self.pg_config = pg_config
        self.redis_config = redis_config
        self.prefix = prefix
        self.redis_client: Optional[Redis] = None
        self.async_engine = None
        self.AsyncSessionLocal = None
        
    async def setup(self):
        """初始化连接"""
        # 连接Redis
        self.redis_client = await redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=False
        )
        
        # 创建SQLAlchemy异步引擎
        if self.pg_config.dsn.startswith('postgresql://'):
            dsn = self.pg_config.dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            dsn = self.pg_config.dsn
            
        self.async_engine = create_async_engine(
            dsn,
            pool_size=20,
            echo=False
        )
        
        self.AsyncSessionLocal = sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
    async def cleanup(self):
        """清理连接"""
        if self.redis_client:
            await self.redis_client.close()
        if self.async_engine:
            await self.async_engine.dispose()
    
    async def send_test_messages(self, queue_name: str, count: int = 10, delay: float = 0.1):
        """发送测试消息到指定队列"""
        stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        
        for i in range(count):
            task_data = {
                'name': f'test_task_{i}',
                'queue': queue_name,
                'priority': 1,
                'trigger_time': time.time(),
                'test_id': f'recovery_test_{i}',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # 使用XADD添加消息到stream
            msg_id = await self.redis_client.xadd(
                stream_key,
                {'data': dumps_str(task_data)}
            )
            
            logger.info(f"Sent test message {i} to {queue_name}: {msg_id}")
            
            if delay > 0:
                await asyncio.sleep(delay)
    
    async def send_task_change_events(self, count: int = 10, delay: float = 0.1):
        """发送任务变更事件"""
        change_stream_key = f"{self.prefix}:TASK_CHANGES"
        
        for i in range(count):
            event_data = {
                'event_id': f'task_change_{i}',
                'event_type': 'task_updated',
                'timestamp': time.time()
            }
            
            # 添加到TASK_CHANGES stream
            msg_id = await self.redis_client.xadd(
                change_stream_key,
                event_data
            )
            
            # 同时在Redis中创建对应的任务数据（模拟真实场景）
            task_key = f"{self.prefix}:TASK:task_change_{i}"
            task_data = {
                'status': 'running',
                'started_at': str(time.time()),
                'worker_id': 'test_worker_1'
            }
            await self.redis_client.hset(task_key, mapping={
                k: dumps_str(v) if not isinstance(v, (str, bytes)) else v 
                for k, v in task_data.items()
            })
            
            logger.info(f"Sent task change event {i}: {msg_id}")
            
            if delay > 0:
                await asyncio.sleep(delay)
    
    async def check_pending_messages(self, queue_name: str = None, check_task_changes: bool = False):
        """检查pending消息数量"""
        results = {}
        
        if queue_name:
            # 检查指定队列的pending消息
            stream_key = f"{self.prefix}:QUEUE:{queue_name}"
            consumer_group = f"{self.prefix}_pg_consumer1"
            
            try:
                info = await self.redis_client.xpending(stream_key, consumer_group)
                results[queue_name] = {
                    'total_pending': info['pending'],
                    'consumers': {}
                }
                
                # 获取每个consumer的pending消息详情
                if info['pending'] > 0:
                    detailed = await self.redis_client.xpending_range(
                        stream_key, consumer_group, 
                        min='-', max='+', count=100
                    )
                    
                    for msg in detailed:
                        consumer = msg['consumer'].decode('utf-8') if isinstance(msg['consumer'], bytes) else msg['consumer']
                        if consumer not in results[queue_name]['consumers']:
                            results[queue_name]['consumers'][consumer] = []
                        
                        msg_id = msg['message_id'].decode('utf-8') if isinstance(msg['message_id'], bytes) else msg['message_id']
                        results[queue_name]['consumers'][consumer].append({
                            'message_id': msg_id,
                            'time_since_delivered': msg['time_since_delivered'],
                            'times_delivered': msg['times_delivered']
                        })
                        
            except Exception as e:
                logger.error(f"Error checking pending for queue {queue_name}: {e}")
        
        if check_task_changes:
            # 检查TASK_CHANGES的pending消息
            change_stream_key = f"{self.prefix}:TASK_CHANGES"
            consumer_group = f"{self.prefix}_changes_consumer"
            
            try:
                info = await self.redis_client.xpending(change_stream_key, consumer_group)
                results['TASK_CHANGES'] = {
                    'total_pending': info['pending'],
                    'consumers': {}
                }
                
                # 获取每个consumer的pending消息详情
                if info['pending'] > 0:
                    detailed = await self.redis_client.xpending_range(
                        change_stream_key, consumer_group,
                        min='-', max='+', count=100
                    )
                    
                    for msg in detailed:
                        consumer = msg['consumer'].decode('utf-8') if isinstance(msg['consumer'], bytes) else msg['consumer']
                        if consumer not in results['TASK_CHANGES']['consumers']:
                            results['TASK_CHANGES']['consumers'][consumer] = []
                        
                        msg_id = msg['message_id'].decode('utf-8') if isinstance(msg['message_id'], bytes) else msg['message_id']
                        results['TASK_CHANGES']['consumers'][consumer].append({
                            'message_id': msg_id,
                            'time_since_delivered': msg['time_since_delivered'],
                            'times_delivered': msg['times_delivered']
                        })
                        
            except Exception as e:
                logger.error(f"Error checking pending for TASK_CHANGES: {e}")
        
        return results
    
    async def check_database_tasks(self, queue_name: str = None, limit: int = 100):
        """检查数据库中的任务"""
        async with self.AsyncSessionLocal() as session:
            if queue_name:
                query = text("""
                    SELECT id, queue_name, task_name, status, created_at, worker_id
                    FROM tasks
                    WHERE queue_name = :queue_name
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                result = await session.execute(query, {'queue_name': queue_name, 'limit': limit})
            else:
                query = text("""
                    SELECT id, queue_name, task_name, status, created_at, worker_id
                    FROM tasks
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                result = await session.execute(query, {'limit': limit})
            
            tasks = []
            for row in result:
                tasks.append({
                    'id': row[0],
                    'queue_name': row[1],
                    'task_name': row[2],
                    'status': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'worker_id': row[5]
                })
            
            return tasks
    
    async def get_online_workers(self, worker_prefix: str = 'PG_CONSUMER'):
        """获取在线的worker列表"""
        pattern = f"{self.prefix}:{worker_prefix}:*"
        workers = []
        
        async for key in self.redis_client.scan_iter(match=pattern, count=100):
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            worker_id = key_str.split(':')[-1]
            
            # 获取worker信息
            worker_info = await self.redis_client.hgetall(key_str)
            if worker_info:
                info = {}
                for k, v in worker_info.items():
                    k_str = k.decode('utf-8') if isinstance(k, bytes) else k
                    v_str = v.decode('utf-8') if isinstance(v, bytes) else v
                    info[k_str] = v_str
                
                workers.append({
                    'worker_id': worker_id,
                    'info': info
                })
        
        return workers
    
    async def kill_worker_by_id(self, worker_id: str, worker_prefix: str = 'PG_CONSUMER'):
        """模拟worker突然挂掉（删除其在Redis中的信息）"""
        worker_key = f"{self.prefix}:{worker_prefix}:{worker_id}"
        
        # 删除worker的注册信息
        result = await self.redis_client.delete(worker_key)
        
        if result:
            logger.info(f"Killed worker {worker_id} (deleted Redis key: {worker_key})")
        else:
            logger.warning(f"Worker {worker_id} not found")
        
        return result > 0


async def test_single_consumer_recovery():
    """测试单个consumer挂掉后重启的恢复"""
    logger.info("=" * 60)
    logger.info("Test 1: Single Consumer Recovery")
    logger.info("=" * 60)
    
    # 初始化测试辅助类
    helper = TestHelper(
        PostgreSQLConfig(
            host=os.getenv('JETTASK_PG_HOST', 'localhost'),
            port=int(os.getenv('JETTASK_PG_PORT', '5432')),
            database=os.getenv('JETTASK_PG_DB', 'jettask'),
            user=os.getenv('JETTASK_PG_USER', 'jettask'),
            password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
        ),
        RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            password=os.getenv('REDIS_PASSWORD'),
        )
    )
    
    await helper.setup()
    
    try:
        # 1. 发送测试消息
        logger.info("\n1. Sending test messages...")
        await helper.send_test_messages('TEST_QUEUE', count=5)
        await helper.send_task_change_events(count=5)
        
        # 2. 启动PG Consumer（会在另一个进程中运行）
        logger.info("\n2. Starting PG Consumer process...")
        import subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/yuyang/easy-task'
        consumer_process = subprocess.Popen([
            sys.executable, '-m', 'jettask.webui.pg_consumer_slow'
        ], env=env)
        
        # 等待consumer开始处理
        await asyncio.sleep(3)
        
        # 3. 检查pending消息状态
        logger.info("\n3. Checking pending messages before kill...")
        pending_before = await helper.check_pending_messages('TEST_QUEUE', check_task_changes=True)
        logger.info(f"Pending messages: {json.dumps(pending_before, indent=2)}")
        
        # 4. 强制终止consumer（模拟突然挂掉）
        logger.info("\n4. Killing consumer process...")
        consumer_process.kill()
        consumer_process.wait()
        
        # 等待一下
        await asyncio.sleep(2)
        
        # 5. 检查pending消息（应该还在）
        logger.info("\n5. Checking pending messages after kill...")
        pending_after_kill = await helper.check_pending_messages('TEST_QUEUE', check_task_changes=True)
        logger.info(f"Pending messages after kill: {json.dumps(pending_after_kill, indent=2)}")
        
        # 6. 重新启动consumer
        logger.info("\n6. Restarting consumer...")
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/yuyang/easy-task'
        consumer_process2 = subprocess.Popen([
            sys.executable, '-m', 'jettask.webui.pg_consumer'
        ], env=env)
        
        # 等待恢复处理
        await asyncio.sleep(10)
        
        # 7. 再次检查pending消息（应该被处理了）
        logger.info("\n7. Checking pending messages after restart...")
        pending_after_restart = await helper.check_pending_messages('TEST_QUEUE', check_task_changes=True)
        logger.info(f"Pending messages after restart: {json.dumps(pending_after_restart, indent=2)}")
        
        # 8. 检查数据库中的任务
        logger.info("\n8. Checking database tasks...")
        db_tasks = await helper.check_database_tasks('TEST_QUEUE')
        logger.info(f"Found {len(db_tasks)} tasks in database")
        for task in db_tasks[:5]:
            logger.info(f"  - {task['task_name']}: {task['status']}")
        
        # 清理
        consumer_process2.terminate()
        consumer_process2.wait()
        
        # 验证结果
        logger.info("\n" + "=" * 60)
        logger.info("Test Result:")
        
        # 检查TEST_QUEUE的恢复
        if 'TEST_QUEUE' in pending_before and 'TEST_QUEUE' in pending_after_restart:
            before_count = pending_before['TEST_QUEUE']['total_pending']
            after_count = pending_after_restart['TEST_QUEUE']['total_pending']
            if before_count > 0 and after_count == 0:
                logger.info("✓ TEST_QUEUE: Pending messages recovered successfully!")
            else:
                logger.warning(f"✗ TEST_QUEUE: Recovery may have issues. Before: {before_count}, After: {after_count}")
        
        # 检查TASK_CHANGES的恢复
        if 'TASK_CHANGES' in pending_before and 'TASK_CHANGES' in pending_after_restart:
            before_count = pending_before['TASK_CHANGES']['total_pending']
            after_count = pending_after_restart['TASK_CHANGES']['total_pending']
            if before_count > 0 and after_count == 0:
                logger.info("✓ TASK_CHANGES: Pending messages recovered successfully!")
            else:
                logger.warning(f"✗ TASK_CHANGES: Recovery may have issues. Before: {before_count}, After: {after_count}")
        
    finally:
        await helper.cleanup()


async def test_multiple_consumers_takeover():
    """测试多个consumer时的接管机制"""
    logger.info("=" * 60)
    logger.info("Test 2: Multiple Consumers Takeover")
    logger.info("=" * 60)
    
    # 初始化测试辅助类
    helper = TestHelper(
        PostgreSQLConfig(
            host=os.getenv('JETTASK_PG_HOST', 'localhost'),
            port=int(os.getenv('JETTASK_PG_PORT', '5432')),
            database=os.getenv('JETTASK_PG_DB', 'jettask'),
            user=os.getenv('JETTASK_PG_USER', 'jettask'),
            password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
        ),
        RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            password=os.getenv('REDIS_PASSWORD'),
        )
    )
    
    await helper.setup()
    
    try:
        # 1. 启动第一个consumer（慢速版本）
        logger.info("\n1. Starting first consumer (slow version)...")
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/yuyang/easy-task'
        env['CONSUMER_ID'] = 'consumer_1'
        consumer1 = subprocess.Popen([
            sys.executable, '-m', 'jettask.webui.pg_consumer_slow'
        ], env=env)
        
        await asyncio.sleep(2)
        
        # 2. 发送测试消息
        logger.info("\n2. Sending test messages...")
        await helper.send_test_messages('MULTI_TEST_QUEUE', count=10)
        await helper.send_task_change_events(count=10)
        
        # 等待第一个consumer开始处理
        await asyncio.sleep(3)
        
        # 3. 检查当前状态
        logger.info("\n3. Checking current state...")
        workers_before = await helper.get_online_workers()
        logger.info(f"Online workers: {len(workers_before)}")
        for worker in workers_before:
            logger.info(f"  - {worker['worker_id']}: {worker['info'].get('queues', 'N/A')}")
        
        pending_before = await helper.check_pending_messages('MULTI_TEST_QUEUE', check_task_changes=True)
        logger.info(f"Pending messages: {json.dumps(pending_before, indent=2)}")
        
        # 4. 启动第二个consumer（正常速度）
        logger.info("\n4. Starting second consumer...")
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/yuyang/easy-task'
        env['CONSUMER_ID'] = 'consumer_2'
        consumer2 = subprocess.Popen([
            sys.executable, '-m', 'jettask.webui.pg_consumer'
        ], env=env)
        
        await asyncio.sleep(2)
        
        # 5. 强制终止第一个consumer
        logger.info("\n5. Killing first consumer...")
        consumer1.kill()
        consumer1.wait()
        
        # 6. 等待第二个consumer接管
        logger.info("\n6. Waiting for takeover...")
        await asyncio.sleep(10)
        
        # 7. 检查接管后的状态
        logger.info("\n7. Checking state after takeover...")
        workers_after = await helper.get_online_workers()
        logger.info(f"Online workers: {len(workers_after)}")
        for worker in workers_after:
            logger.info(f"  - {worker['worker_id']}: {worker['info'].get('queues', 'N/A')}")
        
        pending_after = await helper.check_pending_messages('MULTI_TEST_QUEUE', check_task_changes=True)
        logger.info(f"Pending messages after takeover: {json.dumps(pending_after, indent=2)}")
        
        # 8. 检查数据库
        logger.info("\n8. Checking database...")
        db_tasks = await helper.check_database_tasks('MULTI_TEST_QUEUE')
        logger.info(f"Found {len(db_tasks)} tasks in database")
        
        # 清理
        consumer2.terminate()
        consumer2.wait()
        
        # 验证结果
        logger.info("\n" + "=" * 60)
        logger.info("Test Result:")
        
        # 检查MULTI_TEST_QUEUE的接管
        if 'MULTI_TEST_QUEUE' in pending_before and 'MULTI_TEST_QUEUE' in pending_after:
            before_count = pending_before['MULTI_TEST_QUEUE']['total_pending']
            after_count = pending_after['MULTI_TEST_QUEUE']['total_pending']
            if before_count > 0 and after_count == 0:
                logger.info("✓ MULTI_TEST_QUEUE: Messages taken over successfully!")
            else:
                logger.warning(f"✗ MULTI_TEST_QUEUE: Takeover may have issues. Before: {before_count}, After: {after_count}")
        
        # 检查TASK_CHANGES的接管
        if 'TASK_CHANGES' in pending_before and 'TASK_CHANGES' in pending_after:
            before_count = pending_before['TASK_CHANGES']['total_pending']
            after_count = pending_after['TASK_CHANGES']['total_pending']
            if before_count > 0 and after_count == 0:
                logger.info("✓ TASK_CHANGES: Messages taken over successfully!")
            else:
                logger.warning(f"✗ TASK_CHANGES: Takeover may have issues. Before: {before_count}, After: {after_count}")
        
    finally:
        await helper.cleanup()


async def main():
    """主测试函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # 运行测试
    try:
        # 测试1：单个consumer的恢复
        await test_single_consumer_recovery()
        
        # 等待一下再进行下一个测试
        await asyncio.sleep(5)
        
        # 测试2：多个consumer的接管
        await test_multiple_consumers_takeover()
        
        logger.info("\n" + "=" * 60)
        logger.info("All tests completed!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)


if __name__ == '__main__':
    import subprocess
    asyncio.run(main())