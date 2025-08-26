"""
Worker 扫描器 - 高效检测超时 Worker
使用 Redis Sorted Set 实现 O(log N) 复杂度
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional

logger = logging.getLogger('app')


class WorkerScanner:
    """
    使用 Redis Sorted Set 优化的 Worker 扫描器
    
    核心优化：
    1. O(log N) 的超时检测复杂度
    2. 自动一致性维护
    3. 原子性操作保证数据一致
    """
    
    def __init__(self, sync_redis, async_redis, redis_prefix: str = 'jettask',
                 heartbeat_timeout: float = 3.0):
        self.redis = sync_redis
        self.async_redis = async_redis
        self.redis_prefix = redis_prefix
        self.heartbeat_timeout = heartbeat_timeout
        self.active_workers_key = f"{redis_prefix}:ACTIVE_WORKERS"
        
        # 一致性维护
        self._initialized = False
        self._last_full_sync = 0
        self._full_sync_interval = 60  # 每60秒完整同步
        self._scan_counter = 0
        self._partial_check_interval = 10  # 每10次扫描做部分检查
        
    async def ensure_initialized(self):
        """确保 Sorted Set 已初始化并保持一致"""
        current_time = time.time()
        
        # 首次初始化或定期完整同步
        if not self._initialized or (current_time - self._last_full_sync > self._full_sync_interval):
            await self._full_sync()
            self._initialized = True
            self._last_full_sync = current_time
            
    async def _full_sync(self):
        """完整同步 Hash 和 Sorted Set"""
        try:
            logger.debug("Starting full synchronization of ACTIVE_WORKERS")
            
            # 1. 收集所有活跃 worker 的 Hash 数据
            pattern = f"{self.redis_prefix}:WORKER:*"
            hash_workers = {}
            
            async for key in self.async_redis.scan_iter(match=pattern, count=100):
                if ':HISTORY:' not in key and ':REUSE:' not in key:
                    worker_id = key.split(':')[-1]
                    worker_data = await self.async_redis.hgetall(key)
                    
                    if worker_data and worker_data.get('is_alive', 'true').lower() == 'true':
                        try:
                            heartbeat = float(worker_data.get('last_heartbeat', 0))
                            hash_workers[worker_id] = heartbeat
                        except (ValueError, TypeError):
                            continue
            
            # 2. 获取 Sorted Set 中的数据
            zset_workers = await self.async_redis.zrange(
                self.active_workers_key, 0, -1, withscores=True
            )
            zset_dict = {worker_id: score for worker_id, score in zset_workers}
            
            # 3. 计算差异
            hash_ids = set(hash_workers.keys())
            zset_ids = set(zset_dict.keys())
            
            to_add = hash_ids - zset_ids  # Hash有但ZSet无
            to_remove = zset_ids - hash_ids  # ZSet有但Hash无
            to_update = {}  # 时间戳不一致的
            
            for worker_id in hash_ids & zset_ids:
                if abs(hash_workers[worker_id] - zset_dict[worker_id]) > 0.1:
                    to_update[worker_id] = hash_workers[worker_id]
            
            # 4. 批量修复
            if to_add or to_remove or to_update:
                pipeline = self.async_redis.pipeline()
                
                if to_add:
                    members = {worker_id: hash_workers[worker_id] for worker_id in to_add}
                    pipeline.zadd(self.active_workers_key, members)
                    
                if to_remove:
                    pipeline.zrem(self.active_workers_key, *to_remove)
                    
                if to_update:
                    pipeline.zadd(self.active_workers_key, to_update)
                    
                await pipeline.execute()
                logger.info(f"Full sync: +{len(to_add)}, -{len(to_remove)}, ~{len(to_update)}")
                
        except Exception as e:
            logger.error(f"Full sync failed: {e}")
    
    async def scan_timeout_workers(self) -> List[Dict]:
        """
        快速扫描超时的 worker - O(log N) 复杂度
        注意：需要考虑每个worker自己的heartbeat_timeout
        """
        await self.ensure_initialized()
        
        # 定期部分检查
        self._scan_counter += 1
        if self._scan_counter >= self._partial_check_interval:
            self._scan_counter = 0
            asyncio.create_task(self._partial_check())
        
        current_time = time.time()
        # 使用最大可能的超时时间作为初始筛选（避免遗漏）
        # 实际超时判断会在后面使用每个worker自己的timeout
        max_possible_timeout = 300  # 5分钟，足够覆盖大多数情况
        cutoff_time = current_time - max_possible_timeout
        
        # O(log N) 获取可能超时的 workers（宽松筛选）
        potential_timeout_worker_ids = await self.async_redis.zrangebyscore(
            self.active_workers_key, 
            min=0, 
            max=current_time - 1  # 至少1秒没更新的
        )
        
        if not potential_timeout_worker_ids:
            return []
        
        # 批量获取 worker 详细信息
        pipeline = self.async_redis.pipeline()
        for worker_id in potential_timeout_worker_ids:
            worker_key = f"{self.redis_prefix}:WORKER:{worker_id}"
            pipeline.hgetall(worker_key)
        
        workers_data = await pipeline.execute()
        
        # 验证并构造结果
        result = []
        cleanup_pipeline = self.async_redis.pipeline()
        need_cleanup = False
        
        for worker_id, worker_data in zip(potential_timeout_worker_ids, workers_data):
            if not worker_data:
                # Hash 不存在，清理 ZSet
                cleanup_pipeline.zrem(self.active_workers_key, worker_id)
                need_cleanup = True
                continue
            
            # 获取该worker自己的heartbeat_timeout
            worker_heartbeat_timeout = float(worker_data.get('heartbeat_timeout', self.heartbeat_timeout))
            
            # 双重检查实际心跳时间（使用worker自己的timeout）
            last_heartbeat = float(worker_data.get('last_heartbeat', 0))
            worker_cutoff_time = current_time - worker_heartbeat_timeout
            
            if last_heartbeat >= worker_cutoff_time:
                # 未超时，更新 ZSet 并跳过
                cleanup_pipeline.zadd(self.active_workers_key, {worker_id: last_heartbeat})
                need_cleanup = True
                continue
            
            # 检查存活状态
            is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
            if not is_alive:
                # 已离线，清理 ZSet
                cleanup_pipeline.zrem(self.active_workers_key, worker_id)
                need_cleanup = True
                continue
            
            # 确认超时（使用worker自己的timeout判断）
            logger.debug(f"Worker {worker_id} timeout: last_heartbeat={last_heartbeat}, "
                        f"timeout={worker_heartbeat_timeout}s, cutoff={worker_cutoff_time}")
            worker_key = f"{self.redis_prefix}:WORKER:{worker_id}"
            result.append({
                'worker_key': worker_key,
                'worker_data': worker_data,
                'worker_id': worker_id
            })
        
        if need_cleanup:
            await cleanup_pipeline.execute()
        
        if result:
            logger.info(f"Found {len(result)} timeout workers")
        
        return result
    
    async def update_heartbeat(self, worker_id: str, heartbeat_time: Optional[float] = None):
        """原子性更新心跳（同时更新 Hash 和 ZSet）"""
        if heartbeat_time is None:
            heartbeat_time = time.time()
            
        pipeline = self.async_redis.pipeline()
        worker_key = f"{self.redis_prefix}:WORKER:{worker_id}"
        
        # 同时更新两个数据结构
        pipeline.hset(worker_key, 'last_heartbeat', str(heartbeat_time))
        pipeline.zadd(self.active_workers_key, {worker_id: heartbeat_time})
        
        await pipeline.execute()
    
    async def add_worker(self, worker_id: str, worker_data: Dict):
        """添加新 worker（同时加入 Hash 和 ZSet）"""
        heartbeat_time = float(worker_data.get('last_heartbeat', time.time()))
        
        pipeline = self.async_redis.pipeline()
        worker_key = f"{self.redis_prefix}:WORKER:{worker_id}"
        
        # 创建 Hash
        pipeline.hset(worker_key, mapping=worker_data)
        # 加入 ZSet
        pipeline.zadd(self.active_workers_key, {worker_id: heartbeat_time})
        
        await pipeline.execute()
        logger.debug(f"Added worker {worker_id} to system")
    
    async def remove_worker(self, worker_id: str):
        """移除 worker（同时更新 Hash 和 ZSet）"""
        pipeline = self.async_redis.pipeline()
        worker_key = f"{self.redis_prefix}:WORKER:{worker_id}"
        
        # 标记 Hash 为离线
        pipeline.hset(worker_key, 'is_alive', 'false')
        # 从 ZSet 移除
        pipeline.zrem(self.active_workers_key, worker_id)
        
        await pipeline.execute()
        logger.debug(f"Removed worker {worker_id} from active set")
    
    async def _partial_check(self):
        """部分一致性检查"""
        try:
            # 随机检查10个 worker
            sample_size = min(10, await self.async_redis.zcard(self.active_workers_key))
            if sample_size == 0:
                return
            
            # 随机抽样
            random_workers = await self.async_redis.zrandmember(
                self.active_workers_key, sample_size, withscores=True
            )
            
            for worker_id, zset_score in random_workers:
                worker_key = f"{self.redis_prefix}:WORKER:{worker_id}"
                hash_heartbeat = await self.async_redis.hget(worker_key, 'last_heartbeat')
                
                if not hash_heartbeat:
                    # Hash 不存在，删除 ZSet 条目
                    await self.async_redis.zrem(self.active_workers_key, worker_id)
                    logger.debug(f"Partial check: removed {worker_id}")
                else:
                    # 检查时间戳一致性
                    hash_time = float(hash_heartbeat)
                    if abs(hash_time - zset_score) > 1.0:
                        await self.async_redis.zadd(self.active_workers_key, {worker_id: hash_time})
                        logger.debug(f"Partial check: synced {worker_id}")
                        
        except Exception as e:
            logger.debug(f"Partial check error: {e}")
    
    async def get_active_count(self) -> int:
        """获取活跃 worker 数量 - O(1)"""
        return await self.async_redis.zcard(self.active_workers_key)