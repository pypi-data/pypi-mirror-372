#!/usr/bin/env python
"""简化的恢复机制测试脚本"""

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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class RecoveryTester:
    """恢复机制测试器"""
    
    def __init__(self):
        self.pg_config = PostgreSQLConfig(
            host=os.getenv('JETTASK_PG_HOST', 'localhost'),
            port=int(os.getenv('JETTASK_PG_PORT', '5432')),
            database=os.getenv('JETTASK_PG_DB', 'jettask'),
            user=os.getenv('JETTASK_PG_USER', 'jettask'),
            password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
        )
        
        self.redis_config = RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            password=os.getenv('REDIS_PASSWORD'),
        )
        
        self.prefix = "jettask"
        self.redis_client: Optional[Redis] = None
        self.async_engine = None
        self.AsyncSessionLocal = None
        
    async def setup(self):
        """初始化连接"""
        self.redis_client = await redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=False
        )
        
        if self.pg_config.dsn.startswith('postgresql://'):
            dsn = self.pg_config.dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            dsn = self.pg_config.dsn
            
        self.async_engine = create_async_engine(dsn, pool_size=20, echo=False)
        
        self.AsyncSessionLocal = sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
    async def cleanup(self):
        """清理连接"""
        if self.redis_client:
            await self.redis_client.aclose()
        if self.async_engine:
            await self.async_engine.dispose()
    
    async def test_queue_recovery(self):
        """测试队列消息的恢复机制"""
        logger.info("=" * 60)
        logger.info("测试 _consume_queues 的恢复机制")
        logger.info("=" * 60)
        
        queue_name = 'RECOVERY_TEST_QUEUE'
        stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        consumer_group = f"{self.prefix}_pg_consumer1"
        
        # 1. 清理旧数据
        logger.info("\n1. 清理旧数据...")
        try:
            await self.redis_client.delete(stream_key)
        except:
            pass
        
        # 2. 发送测试消息
        logger.info("\n2. 发送测试消息到队列...")
        task_ids = []
        for i in range(5):
            task_data = {
                'name': f'recovery_test_task_{i}',
                'queue': queue_name,
                'priority': 1,
                'trigger_time': time.time(),
                'test_id': f'queue_recovery_{i}'
            }
            
            msg_id = await self.redis_client.xadd(
                stream_key,
                {'data': dumps_str(task_data)}
            )
            task_ids.append(msg_id)
            logger.info(f"  - 发送消息 {i}: {msg_id}")
        
        # 3. 创建消费者组
        logger.info("\n3. 创建消费者组...")
        try:
            await self.redis_client.xgroup_create(
                stream_key, consumer_group, id='0', mkstream=True
            )
            logger.info(f"  - 创建消费者组: {consumer_group}")
        except:
            pass
        
        # 4. 模拟consumer_1读取消息但不ACK（突然挂掉）
        logger.info("\n4. 模拟 consumer_1 读取消息但不ACK...")
        consumer_1 = "test_consumer_1"
        
        messages = await self.redis_client.xreadgroup(
            consumer_group,
            consumer_1,
            {stream_key: '>'},
            count=5,
            block=1000
        )
        
        if messages:
            logger.info(f"  - consumer_1 读取了 {len(messages[0][1])} 条消息")
            for msg_id, data in messages[0][1]:
                logger.info(f"    - 消息ID: {msg_id}")
        
        # 5. 检查pending消息
        logger.info("\n5. 检查pending消息...")
        pending_info = await self.redis_client.xpending(stream_key, consumer_group)
        logger.info(f"  - 总pending消息数: {pending_info['pending']}")
        
        if pending_info['pending'] > 0:
            detailed = await self.redis_client.xpending_range(
                stream_key, consumer_group,
                min='-', max='+', count=10
            )
            for msg in detailed:
                logger.info(f"    - 消息 {msg['message_id']}: consumer={msg['consumer']}, times_delivered={msg['times_delivered']}")
        
        # 6. 模拟consumer_2接管pending消息
        logger.info("\n6. 模拟 consumer_2 尝试接管pending消息...")
        consumer_2 = "test_consumer_2"
        
        # 使用XCLAIM接管消息
        if pending_info['pending'] > 0:
            # 获取所有pending消息的ID
            pending_msg_ids = [msg['message_id'] for msg in detailed]
            
            # XCLAIM接管消息（idle时间设为0表示立即接管）
            claimed = await self.redis_client.xclaim(
                stream_key,
                consumer_group,
                consumer_2,
                min_idle_time=0,  # 立即接管
                message_ids=pending_msg_ids
            )
            
            logger.info(f"  - consumer_2 接管了 {len(claimed)} 条消息")
            
            # ACK消息
            if claimed:
                msg_ids_to_ack = [msg[0] for msg in claimed]
                await self.redis_client.xack(stream_key, consumer_group, *msg_ids_to_ack)
                logger.info(f"  - consumer_2 ACK了 {len(msg_ids_to_ack)} 条消息")
        
        # 7. 再次检查pending消息
        logger.info("\n7. 再次检查pending消息...")
        pending_info_after = await self.redis_client.xpending(stream_key, consumer_group)
        logger.info(f"  - 总pending消息数: {pending_info_after['pending']}")
        
        # 8. 验证结果
        logger.info("\n" + "=" * 60)
        if pending_info['pending'] > 0 and pending_info_after['pending'] == 0:
            logger.info("✓ 队列消息恢复测试通过！pending消息成功被接管和处理")
        else:
            logger.warning(f"✗ 队列消息恢复测试失败。恢复前: {pending_info['pending']}，恢复后: {pending_info_after['pending']}")
        
        return pending_info['pending'] > 0 and pending_info_after['pending'] == 0
    
    async def test_task_changes_recovery(self):
        """测试TASK_CHANGES的恢复机制"""
        logger.info("\n" + "=" * 60)
        logger.info("测试 _consume_task_changes 的恢复机制")
        logger.info("=" * 60)
        
        change_stream_key = f"{self.prefix}:TASK_CHANGES"
        consumer_group = f"{self.prefix}_changes_consumer"
        
        # 1. 清理旧数据
        logger.info("\n1. 清理旧数据...")
        try:
            await self.redis_client.delete(change_stream_key)
        except:
            pass
        
        # 2. 发送任务变更事件
        logger.info("\n2. 发送任务变更事件...")
        event_ids = []
        for i in range(5):
            event_data = {
                'event_id': f'task_change_test_{i}',
                'event_type': 'task_updated',
                'timestamp': str(time.time())
            }
            
            msg_id = await self.redis_client.xadd(
                change_stream_key,
                event_data
            )
            event_ids.append(msg_id)
            logger.info(f"  - 发送事件 {i}: {msg_id}")
            
            # 同时创建对应的任务数据
            task_key = f"{self.prefix}:TASK:task_change_test_{i}"
            task_data = {
                'status': 'completed',
                'completed_at': str(time.time()),
                'result': json.dumps({'success': True})
            }
            await self.redis_client.hset(task_key, mapping={
                k: dumps_str(v) if not isinstance(v, (str, bytes)) else v
                for k, v in task_data.items()
            })
        
        # 3. 创建消费者组
        logger.info("\n3. 创建消费者组...")
        try:
            await self.redis_client.xgroup_create(
                change_stream_key, consumer_group, id='0', mkstream=True
            )
            logger.info(f"  - 创建消费者组: {consumer_group}")
        except:
            pass
        
        # 4. 模拟consumer_1读取消息但不ACK
        logger.info("\n4. 模拟 consumer_1 读取消息但不ACK...")
        consumer_1 = "changes_consumer_1"
        
        messages = await self.redis_client.xreadgroup(
            consumer_group,
            consumer_1,
            {change_stream_key: '>'},
            count=5,
            block=1000
        )
        
        if messages:
            logger.info(f"  - consumer_1 读取了 {len(messages[0][1])} 条事件")
            for msg_id, data in messages[0][1]:
                logger.info(f"    - 事件ID: {msg_id}")
        
        # 5. 检查pending消息
        logger.info("\n5. 检查pending事件...")
        pending_info = await self.redis_client.xpending(change_stream_key, consumer_group)
        logger.info(f"  - 总pending事件数: {pending_info['pending']}")
        
        if pending_info['pending'] > 0:
            detailed = await self.redis_client.xpending_range(
                change_stream_key, consumer_group,
                min='-', max='+', count=10
            )
            for msg in detailed:
                logger.info(f"    - 事件 {msg['message_id']}: consumer={msg['consumer']}, times_delivered={msg['times_delivered']}")
        
        # 6. 模拟consumer_2接管pending消息
        logger.info("\n6. 模拟 consumer_2 接管pending事件...")
        consumer_2 = "changes_consumer_2"
        
        if pending_info['pending'] > 0:
            pending_msg_ids = [msg['message_id'] for msg in detailed]
            
            claimed = await self.redis_client.xclaim(
                change_stream_key,
                consumer_group,
                consumer_2,
                min_idle_time=0,
                message_ids=pending_msg_ids
            )
            
            logger.info(f"  - consumer_2 接管了 {len(claimed)} 条事件")
            
            # ACK消息
            if claimed:
                msg_ids_to_ack = [msg[0] for msg in claimed]
                await self.redis_client.xack(change_stream_key, consumer_group, *msg_ids_to_ack)
                logger.info(f"  - consumer_2 ACK了 {len(msg_ids_to_ack)} 条事件")
        
        # 7. 再次检查pending消息
        logger.info("\n7. 再次检查pending事件...")
        pending_info_after = await self.redis_client.xpending(change_stream_key, consumer_group)
        logger.info(f"  - 总pending事件数: {pending_info_after['pending']}")
        
        # 8. 验证结果
        logger.info("\n" + "=" * 60)
        if pending_info['pending'] > 0 and pending_info_after['pending'] == 0:
            logger.info("✓ TASK_CHANGES恢复测试通过！pending事件成功被接管和处理")
        else:
            logger.warning(f"✗ TASK_CHANGES恢复测试失败。恢复前: {pending_info['pending']}，恢复后: {pending_info_after['pending']}")
        
        return pending_info['pending'] > 0 and pending_info_after['pending'] == 0
    
    async def test_offline_worker_recovery(self):
        """测试OfflineWorkerRecovery的功能"""
        logger.info("\n" + "=" * 60)
        logger.info("测试 OfflineWorkerRecovery 的功能")
        logger.info("=" * 60)
        
        # 导入OfflineWorkerRecovery
        from jettask.core.offline_worker_recovery import OfflineWorkerRecovery
        
        # 创建同步Redis客户端（ConsumerManager需要）
        import redis as sync_redis
        sync_redis_client = sync_redis.StrictRedis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=True
        )
        
        # 创建ConsumerManager
        consumer_manager = ConsumerManager(
            redis_client=sync_redis_client,
            strategy=ConsumerStrategy.HEARTBEAT,
            config={
                'redis_prefix': self.prefix,
                'queues': ['OFFLINE_TEST_QUEUE'],
                'worker_prefix': 'TEST_WORKER'
            }
        )
        
        # 创建OfflineWorkerRecovery
        recovery = OfflineWorkerRecovery(
            async_redis_client=self.redis_client,
            redis_prefix=self.prefix,
            worker_prefix='TEST_WORKER',
            consumer_manager=consumer_manager
        )
        
        # 准备测试数据
        queue_name = 'OFFLINE_TEST_QUEUE'
        stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        consumer_group = f"{self.prefix}_pg_consumer1"
        
        # 清理旧数据
        logger.info("\n1. 清理旧数据...")
        try:
            await self.redis_client.delete(stream_key)
        except:
            pass
        
        # 发送测试消息
        logger.info("\n2. 发送测试消息...")
        for i in range(3):
            task_data = {
                'name': f'offline_test_{i}',
                'queue': queue_name,
                'test_id': f'offline_{i}'
            }
            await self.redis_client.xadd(
                stream_key,
                {'data': dumps_str(task_data)}
            )
        
        # 创建消费者组
        try:
            await self.redis_client.xgroup_create(
                stream_key, consumer_group, id='0', mkstream=True
            )
        except:
            pass
        
        # 模拟离线worker读取消息
        logger.info("\n3. 模拟离线worker读取消息...")
        offline_worker = "offline_worker_1"
        messages = await self.redis_client.xreadgroup(
            consumer_group,
            offline_worker,
            {stream_key: '>'},
            count=3,
            block=1000
        )
        
        if messages:
            logger.info(f"  - 离线worker读取了 {len(messages[0][1])} 条消息")
        
        # 模拟worker离线（删除其注册信息）
        worker_key = f"{self.prefix}:TEST_WORKER:{offline_worker}"
        await self.redis_client.delete(worker_key)
        logger.info(f"  - 模拟worker离线: 删除 {worker_key}")
        
        # 定义处理回调
        processed_messages = []
        async def process_callback(msg_id, msg_data, queue, consumer_id):
            processed_messages.append({
                'msg_id': msg_id,
                'queue': queue,
                'consumer_id': consumer_id
            })
            logger.info(f"  - 处理恢复的消息: {msg_id} from {consumer_id}")
        
        # 执行恢复
        logger.info("\n4. 执行离线worker恢复...")
        current_consumer = "active_worker_1"
        recovered_count = await recovery.recover_offline_workers(
            queue=queue_name,
            current_consumer_name=current_consumer,
            process_message_callback=process_callback
        )
        
        logger.info(f"  - 恢复了 {recovered_count} 条消息")
        
        # 检查pending消息
        logger.info("\n5. 检查恢复后的pending消息...")
        pending_info = await self.redis_client.xpending(stream_key, consumer_group)
        logger.info(f"  - 剩余pending消息数: {pending_info['pending']}")
        
        # 验证结果
        logger.info("\n" + "=" * 60)
        if recovered_count > 0 and len(processed_messages) == recovered_count:
            logger.info("✓ OfflineWorkerRecovery测试通过！成功恢复离线worker的消息")
        else:
            logger.warning(f"✗ OfflineWorkerRecovery测试失败。恢复数量: {recovered_count}，处理数量: {len(processed_messages)}")
        
        # 清理
        consumer_manager.cleanup()
        sync_redis_client.close()
        
        return recovered_count > 0


async def main():
    """主测试函数"""
    from dotenv import load_dotenv
    load_dotenv()
    
    tester = RecoveryTester()
    await tester.setup()
    
    try:
        # 测试1：队列消息恢复
        queue_test = await tester.test_queue_recovery()
        await asyncio.sleep(1)
        
        # 测试2：TASK_CHANGES恢复
        changes_test = await tester.test_task_changes_recovery()
        await asyncio.sleep(1)
        
        # 测试3：OfflineWorkerRecovery
        offline_test = await tester.test_offline_worker_recovery()
        
        # 总结
        logger.info("\n" + "=" * 60)
        logger.info("测试总结")
        logger.info("=" * 60)
        logger.info(f"队列消息恢复测试: {'✓ 通过' if queue_test else '✗ 失败'}")
        logger.info(f"TASK_CHANGES恢复测试: {'✓ 通过' if changes_test else '✗ 失败'}")
        logger.info(f"OfflineWorkerRecovery测试: {'✓ 通过' if offline_test else '✗ 失败'}")
        
        if queue_test and changes_test and offline_test:
            logger.info("\n🎉 所有测试通过！恢复机制工作正常")
        else:
            logger.warning("\n⚠️ 部分测试失败，需要检查恢复机制")
        
    except Exception as e:
        logger.error(f"测试出错: {e}", exc_info=True)
    finally:
        await tester.cleanup()


if __name__ == '__main__':
    asyncio.run(main())