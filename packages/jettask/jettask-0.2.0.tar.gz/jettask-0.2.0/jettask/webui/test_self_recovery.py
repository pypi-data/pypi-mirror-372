#!/usr/bin/env python
"""测试单个worker重启后自动恢复pending消息的机制"""

import asyncio
import json
import logging
import os
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
from jettask.utils.serializer import dumps_str

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SelfRecoveryTester:
    """测试单个worker自我恢复机制"""
    
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
        
    async def setup(self):
        """初始化连接"""
        self.redis_client = await redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=False
        )
        
    async def cleanup(self):
        """清理连接"""
        if self.redis_client:
            await self.redis_client.aclose()
    
    async def test_queue_self_recovery(self):
        """测试队列消息的自我恢复机制"""
        logger.info("=" * 60)
        logger.info("测试单个worker重启后自动恢复自己的pending消息")
        logger.info("=" * 60)
        
        queue_name = 'SELF_RECOVERY_QUEUE'
        stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        consumer_group = f"{self.prefix}_pg_consumer1"
        consumer_name = "self_recovery_worker"
        
        # 1. 清理旧数据
        logger.info("\n1. 清理旧数据...")
        try:
            await self.redis_client.delete(stream_key)
        except:
            pass
        
        # 2. 发送测试消息
        logger.info("\n2. 发送测试消息到队列...")
        message_ids = []
        for i in range(5):
            task_data = {
                'name': f'self_recovery_task_{i}',
                'queue': queue_name,
                'priority': 1,
                'trigger_time': time.time(),
                'test_id': f'self_recovery_{i}'
            }
            
            msg_id = await self.redis_client.xadd(
                stream_key,
                {'data': dumps_str(task_data)}
            )
            message_ids.append(msg_id)
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
        
        # 4. 模拟worker第一次读取消息（读取新消息）
        logger.info(f"\n4. 模拟 {consumer_name} 第一次读取新消息但不ACK（模拟突然挂掉）...")
        
        messages = await self.redis_client.xreadgroup(
            consumer_group,
            consumer_name,
            {stream_key: '>'},  # '>' 表示读取新消息
            count=5,
            block=1000
        )
        
        first_read_ids = []
        if messages:
            logger.info(f"  - {consumer_name} 读取了 {len(messages[0][1])} 条新消息")
            for msg_id, data in messages[0][1]:
                first_read_ids.append(msg_id)
                logger.info(f"    - 消息ID: {msg_id}")
        
        # 5. 检查pending消息
        logger.info("\n5. 检查pending消息状态...")
        pending_info = await self.redis_client.xpending(stream_key, consumer_group)
        logger.info(f"  - 总pending消息数: {pending_info['pending']}")
        
        if pending_info['pending'] > 0:
            detailed = await self.redis_client.xpending_range(
                stream_key, consumer_group,
                min='-', max='+', count=10
            )
            for msg in detailed:
                logger.info(f"    - 消息 {msg['message_id']}: consumer={msg['consumer']}, times_delivered={msg['times_delivered']}")
        
        # 6. 模拟同一个worker重启后读取pending消息（不使用XCLAIM）
        logger.info(f"\n6. 模拟 {consumer_name} 重启后读取自己的pending消息...")
        logger.info("  - 使用 '0' 作为起始ID，这会让consumer读取自己的pending消息")
        
        # 先读取pending消息（使用0作为起始ID）
        pending_messages = await self.redis_client.xreadgroup(
            consumer_group,
            consumer_name,  # 同一个consumer name
            {stream_key: '0'},  # '0' 或 '0-0' 表示从头读取pending消息
            count=10,
            block=0  # 不阻塞
        )
        
        recovered_ids = []
        if pending_messages:
            logger.info(f"  - {consumer_name} 成功读取到 {len(pending_messages[0][1])} 条自己的pending消息")
            for msg_id, data in pending_messages[0][1]:
                recovered_ids.append(msg_id)
                logger.info(f"    - 恢复消息ID: {msg_id}")
                
            # ACK这些消息
            if recovered_ids:
                await self.redis_client.xack(stream_key, consumer_group, *recovered_ids)
                logger.info(f"  - {consumer_name} ACK了 {len(recovered_ids)} 条恢复的消息")
        else:
            logger.info(f"  - {consumer_name} 没有读取到pending消息")
        
        # 7. 再次检查pending消息
        logger.info("\n7. 再次检查pending消息状态...")
        pending_info_after = await self.redis_client.xpending(stream_key, consumer_group)
        logger.info(f"  - 总pending消息数: {pending_info_after['pending']}")
        
        # 8. 验证结果
        logger.info("\n" + "=" * 60)
        if pending_info['pending'] > 0 and pending_info_after['pending'] == 0:
            logger.info("✓ 单个worker自我恢复测试通过！")
            logger.info("  worker重启后成功读取并处理了自己的pending消息，无需XCLAIM")
            return True
        else:
            logger.warning(f"✗ 单个worker自我恢复测试失败。")
            logger.warning(f"  恢复前pending: {pending_info['pending']}，恢复后pending: {pending_info_after['pending']}")
            return False
    
    async def test_task_changes_self_recovery(self):
        """测试TASK_CHANGES的自我恢复机制"""
        logger.info("\n" + "=" * 60)
        logger.info("测试TASK_CHANGES单个worker自我恢复机制")
        logger.info("=" * 60)
        
        change_stream_key = f"{self.prefix}:TASK_CHANGES"
        consumer_group = f"{self.prefix}_changes_consumer"
        consumer_name = "changes_self_recovery_worker"
        
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
                'event_id': f'self_recovery_change_{i}',
                'event_type': 'task_updated',
                'timestamp': str(time.time())
            }
            
            msg_id = await self.redis_client.xadd(
                change_stream_key,
                event_data
            )
            event_ids.append(msg_id)
            logger.info(f"  - 发送事件 {i}: {msg_id}")
        
        # 3. 创建消费者组
        logger.info("\n3. 创建消费者组...")
        try:
            await self.redis_client.xgroup_create(
                change_stream_key, consumer_group, id='0', mkstream=True
            )
            logger.info(f"  - 创建消费者组: {consumer_group}")
        except:
            pass
        
        # 4. 模拟worker第一次读取消息但不ACK
        logger.info(f"\n4. 模拟 {consumer_name} 第一次读取事件但不ACK...")
        
        messages = await self.redis_client.xreadgroup(
            consumer_group,
            consumer_name,
            {change_stream_key: '>'},
            count=5,
            block=1000
        )
        
        if messages:
            logger.info(f"  - {consumer_name} 读取了 {len(messages[0][1])} 条事件")
        
        # 5. 检查pending事件
        logger.info("\n5. 检查pending事件...")
        pending_info = await self.redis_client.xpending(change_stream_key, consumer_group)
        logger.info(f"  - 总pending事件数: {pending_info['pending']}")
        
        # 6. 模拟同一个worker重启后恢复
        logger.info(f"\n6. 模拟 {consumer_name} 重启后读取自己的pending事件...")
        
        # 读取pending消息
        pending_messages = await self.redis_client.xreadgroup(
            consumer_group,
            consumer_name,
            {change_stream_key: '0'},  # 从头读取pending
            count=10,
            block=0
        )
        
        recovered_ids = []
        if pending_messages:
            logger.info(f"  - {consumer_name} 成功恢复 {len(pending_messages[0][1])} 条pending事件")
            for msg_id, data in pending_messages[0][1]:
                recovered_ids.append(msg_id)
                
            # ACK消息
            if recovered_ids:
                await self.redis_client.xack(change_stream_key, consumer_group, *recovered_ids)
                logger.info(f"  - {consumer_name} ACK了 {len(recovered_ids)} 条恢复的事件")
        
        # 7. 再次检查pending事件
        logger.info("\n7. 再次检查pending事件...")
        pending_info_after = await self.redis_client.xpending(change_stream_key, consumer_group)
        logger.info(f"  - 总pending事件数: {pending_info_after['pending']}")
        
        # 8. 验证结果
        logger.info("\n" + "=" * 60)
        if pending_info['pending'] > 0 and pending_info_after['pending'] == 0:
            logger.info("✓ TASK_CHANGES自我恢复测试通过！")
            return True
        else:
            logger.warning(f"✗ TASK_CHANGES自我恢复测试失败")
            return False
    
    async def demonstrate_pg_consumer_recovery_flow(self):
        """演示pg_consumer实际的恢复流程"""
        logger.info("\n" + "=" * 60)
        logger.info("演示pg_consumer的实际恢复流程")
        logger.info("=" * 60)
        
        queue_name = 'PG_CONSUMER_DEMO'
        stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        consumer_group = f"{self.prefix}_pg_consumer1"
        consumer_name = "pg_consumer_worker_1"
        
        # 清理
        try:
            await self.redis_client.delete(stream_key)
        except:
            pass
        
        # 发送消息
        logger.info("\n1. 发送5条消息...")
        for i in range(5):
            await self.redis_client.xadd(
                stream_key,
                {'data': dumps_str({'name': f'demo_task_{i}'})}
            )
        
        # 创建消费者组
        try:
            await self.redis_client.xgroup_create(
                stream_key, consumer_group, id='0', mkstream=True
            )
        except:
            pass
        
        # 模拟pg_consumer的消费逻辑
        logger.info(f"\n2. {consumer_name} 开始消费...")
        
        check_backlog = True
        lastid = "0-0"
        processed_count = 0
        
        while True:
            # 这是pg_consumer的实际逻辑
            myid = lastid if check_backlog else ">"
            
            logger.info(f"  - 读取消息，myid={myid}, check_backlog={check_backlog}")
            
            messages = await self.redis_client.xreadgroup(
                consumer_group,
                consumer_name,
                {stream_key: myid},
                count=2,  # 批量读取
                block=0 if check_backlog else 1000
            )
            
            if not messages or len(messages[0][1]) == 0:
                if check_backlog:
                    logger.info("  - 没有更多backlog消息，切换到读取新消息模式")
                    check_backlog = False
                    continue
                else:
                    logger.info("  - 没有新消息")
                    break
            
            # 处理消息
            msg_count = len(messages[0][1])
            logger.info(f"  - 读取到 {msg_count} 条消息")
            
            # 模拟处理失败（第一次只处理2条就"挂掉"）
            if processed_count < 2:
                processed_count += msg_count
                if processed_count >= 2:
                    logger.info("  - 模拟worker挂掉，不ACK剩余消息")
                    break
            
            # 正常ACK
            msg_ids = [msg[0] for msg in messages[0][1]]
            await self.redis_client.xack(stream_key, consumer_group, *msg_ids)
            logger.info(f"  - ACK了 {len(msg_ids)} 条消息")
            
            # 更新lastid
            lastid = messages[0][1][-1][0].decode('utf-8') if isinstance(messages[0][1][-1][0], bytes) else messages[0][1][-1][0]
            
            # 检查是否还有更多backlog
            check_backlog = msg_count >= 2
        
        # 检查pending
        pending_info = await self.redis_client.xpending(stream_key, consumer_group)
        logger.info(f"\n3. Worker挂掉后，pending消息数: {pending_info['pending']}")
        
        # 模拟重启后恢复
        logger.info(f"\n4. {consumer_name} 重启，继续消费...")
        
        check_backlog = True
        lastid = "0-0"  # 重新从0开始，会读取pending消息
        
        while True:
            myid = lastid if check_backlog else ">"
            
            logger.info(f"  - 读取消息，myid={myid}, check_backlog={check_backlog}")
            
            messages = await self.redis_client.xreadgroup(
                consumer_group,
                consumer_name,
                {stream_key: myid},
                count=10,
                block=0 if check_backlog else 1000
            )
            
            if not messages or len(messages[0][1]) == 0:
                if check_backlog:
                    logger.info("  - 没有更多pending/backlog消息")
                    check_backlog = False
                    continue
                else:
                    logger.info("  - 没有新消息，完成")
                    break
            
            msg_count = len(messages[0][1])
            logger.info(f"  - 恢复并处理 {msg_count} 条消息")
            
            # ACK消息
            msg_ids = [msg[0] for msg in messages[0][1]]
            await self.redis_client.xack(stream_key, consumer_group, *msg_ids)
            logger.info(f"  - ACK了 {len(msg_ids)} 条消息")
            
            # 更新lastid
            lastid = messages[0][1][-1][0].decode('utf-8') if isinstance(messages[0][1][-1][0], bytes) else messages[0][1][-1][0]
            check_backlog = msg_count >= 10
        
        # 最终检查
        pending_info_after = await self.redis_client.xpending(stream_key, consumer_group)
        logger.info(f"\n5. 恢复完成后，pending消息数: {pending_info_after['pending']}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ 演示完成：pg_consumer使用check_backlog机制自动恢复pending消息")
        logger.info("  关键点：重启后设置lastid='0-0'和check_backlog=True")
        logger.info("  这样会先处理所有pending和未读消息，然后再读取新消息")


async def main():
    """主测试函数"""
    from dotenv import load_dotenv
    load_dotenv()
    
    tester = SelfRecoveryTester()
    await tester.setup()
    
    try:
        # 测试1：队列消息自我恢复
        queue_test = await tester.test_queue_self_recovery()
        await asyncio.sleep(1)
        
        # 测试2：TASK_CHANGES自我恢复
        changes_test = await tester.test_task_changes_self_recovery()
        await asyncio.sleep(1)
        
        # 演示pg_consumer的实际恢复流程
        await tester.demonstrate_pg_consumer_recovery_flow()
        
        # 总结
        logger.info("\n" + "=" * 60)
        logger.info("测试总结")
        logger.info("=" * 60)
        logger.info(f"队列消息自我恢复测试: {'✓ 通过' if queue_test else '✗ 失败'}")
        logger.info(f"TASK_CHANGES自我恢复测试: {'✓ 通过' if changes_test else '✗ 失败'}")
        
        if queue_test and changes_test:
            logger.info("\n🎉 所有测试通过！")
            logger.info("\n关键发现：")
            logger.info("1. 单个worker重启后，使用相同的consumer_name读取")
            logger.info("2. 设置起始ID为'0'或'0-0'，可以读取自己的pending消息")
            logger.info("3. 不需要XCLAIM，直接xreadgroup即可恢复")
            logger.info("4. pg_consumer的check_backlog机制完美支持这种恢复方式")
        
    except Exception as e:
        logger.error(f"测试出错: {e}", exc_info=True)
    finally:
        await tester.cleanup()


if __name__ == '__main__':
    asyncio.run(main())