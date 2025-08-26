#!/usr/bin/env python
"""
独立的延迟队列扫描器进程
用于扫描延迟任务并投递到执行队列
"""

import asyncio
import time
import logging
import signal
import sys
from typing import Optional
import uuid

import redis.asyncio as aioredis
from redis.asyncio.lock import Lock

logger = logging.getLogger(__name__)


class DelayQueueScanner:
    """
    独立的延迟队列扫描器
    使用分布式锁确保只有一个扫描器实例在运行
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        redis_prefix: str = "jettask",
        scan_interval: float = 1.0,
        batch_size: int = 100,
        lock_ttl: int = 10
    ):
        """
        初始化扫描器
        
        Args:
            redis_url: Redis连接URL
            redis_prefix: Redis键前缀
            scan_interval: 扫描间隔（秒）
            batch_size: 每次处理的任务数
            lock_ttl: 分布式锁TTL（秒）
        """
        self.redis_url = redis_url
        self.redis_prefix = redis_prefix
        self.scan_interval = scan_interval
        self.batch_size = batch_size
        self.lock_ttl = lock_ttl
        
        self.redis: Optional[aioredis.Redis] = None
        self.running = False
        self.scanner_id = f"scanner-{uuid.uuid4().hex[:8]}"
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"Received signal {signum}, stopping scanner...")
        self.running = False
    
    async def connect(self):
        """建立Redis连接"""
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False
            )
            logger.info(f"Scanner {self.scanner_id} connected to Redis")
    
    async def disconnect(self):
        """关闭Redis连接"""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    def _get_queue_key(self) -> str:
        """获取延迟队列键名"""
        return f"{self.redis_prefix}:DELAYED:QUEUE"
    
    def _get_task_key(self, task_id: str) -> str:
        """获取任务详情键名"""
        return f"{self.redis_prefix}:DELAYED:TASK:{task_id}"
    
    def _get_lock_key(self) -> str:
        """获取分布式锁键名"""
        return f"{self.redis_prefix}:DELAYED:SCANNER_LOCK"
    
    def get_lock(self) -> Lock:
        """
        获取Redis分布式锁对象
        
        Returns:
            Redis Lock对象
        """
        return Lock(
            self.redis, 
            self._get_lock_key(),
            timeout=self.lock_ttl,  # 锁的自动过期时间
            blocking=True,  # 阻塞获取
            blocking_timeout=0.1  # 最多等待0.1秒
        )
    
    async def scan_and_deliver(self) -> int:
        """
        扫描并投递到期任务
        
        Returns:
            处理的任务数
        """
        # 使用Redis原生锁
        lock = self.get_lock()
        
        # 尝试获取锁
        async with lock:
            now = time.time()
            processed_count = 0
            
            # 使用ZPOPMIN原子地获取并移除到期任务
            for _ in range(self.batch_size):
                # 获取分数最小的任务
                result = await self.redis.zpopmin(self._get_queue_key(), 1)
                
                if not result:
                    break
                
                for item in result:
                    if len(item) == 2:
                        task_id_bytes, score = item
                        task_id = task_id_bytes.decode() if isinstance(task_id_bytes, bytes) else task_id_bytes
                        
                        # 检查是否到期
                        if score > now:
                            # 还没到期，放回队列
                            await self.redis.zadd(self._get_queue_key(), {task_id: score})
                            break  # 后面的任务肯定也没到期
                        
                        # 处理到期任务
                        try:
                            await self.deliver_task(task_id)
                            processed_count += 1
                        except Exception as e:
                            logger.error(f"Failed to deliver task {task_id}: {e}")
                            # 失败的任务延迟10秒重试
                            retry_time = time.time() + 10
                            await self.redis.zadd(self._get_queue_key(), {task_id: retry_time})
            
            if processed_count > 0:
                logger.info(f"Scanner {self.scanner_id} delivered {processed_count} tasks")
            
            return processed_count
    
    async def deliver_task(self, task_id: str):
        """
        投递任务到执行队列
        
        Args:
            task_id: 任务ID
        """
        # 获取任务详情
        task_json = await self.redis.get(self._get_task_key(task_id))
        
        if not task_json:
            logger.warning(f"Task {task_id} not found, skipping")
            return
        
        import json
        task_info = json.loads(task_json)
        
        queue_name = task_info['queue_name']
        task_data = task_info['task_data']
        
        # 写入到执行队列（Redis Stream）
        stream_key = f"{self.redis_prefix}:{queue_name}"
        await self.redis.xadd(stream_key, {'data': json.dumps(task_data)})
        
        # 更新任务状态
        event_id = task_data.get('event_id', task_id)
        status_key = f"{self.redis_prefix}:TASK:{event_id}"
        await self.redis.hset(status_key, "status", "pending")
        
        # 删除任务详情
        await self.redis.delete(self._get_task_key(task_id))
        
        logger.info(f"Delivered task {task_id} to queue {queue_name}")
    
    async def run(self):
        """运行扫描器"""
        await self.connect()
        
        self.running = True
        logger.info(f"Delay queue scanner {self.scanner_id} started")
        logger.info(f"Scan interval: {self.scan_interval}s, Batch size: {self.batch_size}")
        
        try:
            while self.running:
                try:
                    # 扫描并投递任务
                    await self.scan_and_deliver()
                except Exception as e:
                    logger.error(f"Scanner error: {e}", exc_info=True)
                
                # 等待下一次扫描
                await asyncio.sleep(self.scan_interval)
                
        finally:
            logger.info(f"Scanner {self.scanner_id} stopped")
            await self.disconnect()


async def main():
    """主函数"""
    import argparse
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Jettask Delay Queue Scanner')
    parser.add_argument('--redis-url', default='redis://localhost:6379/0',
                        help='Redis connection URL')
    parser.add_argument('--redis-prefix', default='jettask',
                        help='Redis key prefix')
    parser.add_argument('--scan-interval', type=float, default=1.0,
                        help='Scan interval in seconds')
    parser.add_argument('--batch-size', type=int, default=100,
                        help='Number of tasks to process per scan')
    parser.add_argument('--lock-ttl', type=int, default=10,
                        help='Distributed lock TTL in seconds')
    
    args = parser.parse_args()
    
    # 创建并运行扫描器
    scanner = DelayQueueScanner(
        redis_url=args.redis_url,
        redis_prefix=args.redis_prefix,
        scan_interval=args.scan_interval,
        batch_size=args.batch_size,
        lock_ttl=args.lock_ttl
    )
    
    try:
        await scanner.run()
    except KeyboardInterrupt:
        logger.info("Scanner interrupted by user")


if __name__ == '__main__':
    asyncio.run(main())