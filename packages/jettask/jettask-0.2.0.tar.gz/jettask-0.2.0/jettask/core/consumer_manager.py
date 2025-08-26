import os
import time
import uuid
import json
import logging
import threading
import asyncio
import multiprocessing
from typing import Dict, Any
from enum import Enum
from collections import defaultdict, namedtuple

import redis
from redis.asyncio.lock import Lock as AsyncLock

from ..utils.serializer import dumps_str

logger = logging.getLogger('app')

from .heartbeat_process import HeartbeatProcessManager
from .worker_scanner import WorkerScanner


class ConsumerStrategy(Enum):
    """消费者名称策略
    
    策略选择指南：
    
    ⚠️  POD (仅推荐单进程使用):
       - 基于K8s Pod名称的固定consumer
       - 适用场景: 单进程应用 (asyncio/thread执行器)
       - 优点: 语义清晰，便于监控
       - 缺点: 多进程下会产生冲突
       
    🔧 FIXED (高级用户):
       - 完全自定义的consumer名称
       - 适用场景: 有特殊命名需求的场景 
       - 优点: 完全可控
       - 缺点: 需要用户确保唯一性
    
    🔥 HEARTBEAT (推荐用于生产环境):
       - 基于心跳的简化策略
       - 适用场景: 无状态服务平台（Cloud Run、Serverless、K8s）
       - 优点: 逻辑简单，稳定可靠，自动故障恢复
       - 特点: 使用随机consumer name，通过有序集合维护心跳
    """
    FIXED = "fixed"      # 固定名称
    POD = "pod"          # K8s Pod名称 (⚠️ 多进程下不推荐)
    HEARTBEAT = "heartbeat"  # 心跳策略 (推荐用于生产环境)


class ConsumerManager:
    """消费者名称管理器"""
    
    def __init__(
        self, 
        redis_client: redis.StrictRedis,
        strategy: ConsumerStrategy = ConsumerStrategy.HEARTBEAT,
        config: Dict[str, Any] = None
    ):
        self.redis_client = redis_client
        self.strategy = strategy
        self.config = config or {}
        self._consumer_name = None
        
        # Redis prefix configuration
        self.redis_prefix = config.get('redis_prefix', 'jettask')
        
        # 验证策略配置的合理性
        self._validate_strategy_configuration()
        
        # 心跳策略实例 - 如果是HEARTBEAT策略，立即初始化
        if self.strategy == ConsumerStrategy.HEARTBEAT:
            # 传递队列信息到心跳策略
            heartbeat_config = self.config.copy()
            heartbeat_config['queues'] = self.config.get('queues', [])
            self._heartbeat_strategy = HeartbeatConsumerStrategy(
                self.redis_client,
                heartbeat_config
            )
        else:
            self._heartbeat_strategy = None
    
    def get_prefixed_queue_name(self, queue: str) -> str:
        """为队列名称添加前缀"""
        return f"{self.redis_prefix}:QUEUE:{queue}"
    
    def _validate_strategy_configuration(self):
        """验证消费者策略配置的合理性"""
        # 检查是否在多进程环境中
        current_process = multiprocessing.current_process()
        is_multiprocess = current_process.name != 'MainProcess'
        
        if self.strategy == ConsumerStrategy.POD and is_multiprocess:
            # POD策略在多进程环境下是不允许的，直接退出
            error_msg = (
                "\n"
                "❌ 错误: POD策略不能在多进程环境中使用！\n"
                "\n"
                "原因: POD策略使用固定的consumer名称，多进程会导致消息重复消费。\n"
                "\n"
                "解决方案:\n"
                "  1. 使用 ConsumerStrategy.HEARTBEAT - 心跳策略 (推荐)\n"
                "  2. 使用 ConsumerStrategy.FIXED - 自定义固定名称\n"
                "  3. 使用单进程执行器 (asyncio/thread)\n"
                "\n"
                f"当前环境: {current_process.name} (PID: {os.getpid()})\n"
            )
            logger.error(error_msg)
            # 立即退出程序
            import sys
            sys.exit(1)
        
        # 记录策略选择用于调试
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Consumer strategy: {self.strategy.value}, Process: {current_process.name}")
        
    def get_consumer_name(self, queue: str) -> str:
        """获取消费者名称"""
        # print(f'获取消费者名称: {self.strategy} {queue}')
        if self.strategy == ConsumerStrategy.FIXED:
            return self._get_fixed_name(queue)
        elif self.strategy == ConsumerStrategy.POD:
            return self._get_pod_name(queue)
        elif self.strategy == ConsumerStrategy.HEARTBEAT:
            return self._get_heartbeat_name(queue)
        else:
            raise ValueError(f"Unknown consumer strategy: {self.strategy}")
    
    def _get_fixed_name(self, queue: str) -> str:
        """获取固定的消费者名称"""
        if not self._consumer_name:
            # 可以从配置、环境变量或文件中读取
            self._consumer_name = self.config.get('consumer_name') or \
                                  os.environ.get('EASYTASK_CONSUMER_NAME') or \
                                  f"worker-{os.getpid()}"
        return f"{self._consumer_name}-{queue}"
    
    def _get_pod_name(self, queue: str) -> str:
        """获取基于K8s Pod的消费者名称
        
        注意：POD策略只能在单进程环境下使用
        """
        if not self._consumer_name:
            # 在K8s中，通常通过环境变量获取Pod名称
            pod_name = os.environ.get('HOSTNAME') or \
                       os.environ.get('POD_NAME') or \
                       os.environ.get('K8S_POD_NAME')
            
            if not pod_name:
                logger.warning("Pod name not found, falling back to hostname")
                import socket
                pod_name = socket.gethostname()
            
            # 由于已经在_validate_strategy_configuration中验证过，
            # 这里应该只会在MainProcess中执行
            self._consumer_name = pod_name
            logger.info(f"使用Pod策略的consumer名称: {self._consumer_name}")
                
        return f"{self._consumer_name}-{queue}"
    
    
    def _get_heartbeat_name(self, queue: str) -> str:
        """基于心跳策略获取消费者名称"""
        if not self._heartbeat_strategy:
            raise RuntimeError("Heartbeat strategy not initialized properly")
        
        return self._heartbeat_strategy.get_consumer_name(queue)
    
    def cleanup(self):
        """清理资源（优雅关闭时调用）"""
        # 处理心跳策略的清理
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            self._heartbeat_strategy.cleanup()
    
    def update_stats(self, queue: str, success: bool = True, processing_time: float = 0.0,
                    total_latency: float = None):
        """更新消费者的统计信息（仅对HEARTBEAT策略有效）"""
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            self._heartbeat_strategy.update_stats(queue, success, processing_time, total_latency)
    
    def task_started(self, queue: str):
        """任务开始执行时调用（仅对HEARTBEAT策略有效）"""
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            self._heartbeat_strategy.task_started(queue)
    
    def task_finished(self, queue: str):
        """任务完成时调用（仅对HEARTBEAT策略有效）"""
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            self._heartbeat_strategy.task_finished(queue)
    
    def is_heartbeat_timeout(self) -> bool:
        """检查心跳是否已超时（仅对HEARTBEAT策略有效）"""
        if self.strategy == ConsumerStrategy.HEARTBEAT and self._heartbeat_strategy:
            return self._heartbeat_strategy.is_heartbeat_timeout()
        return False
    
    def cleanup_expired_consumers(self, queue: str):
        """清理过期的消费者（可选功能）"""
        try:
            # 获取消费者组的pending消息信息
            prefixed_queue = self.get_prefixed_queue_name(queue)
            pending_info = self.redis_client.xpending(prefixed_queue, prefixed_queue)
            if not pending_info:
                return
                
            # 获取详细的pending消息
            consumers = self.redis_client.xpending_range(
                prefixed_queue, prefixed_queue, min='-', max='+', count=100
            )
            
            for consumer_info in consumers:
                consumer_name = consumer_info['consumer']
                idle_time = consumer_info['time_since_delivered']
                
                # 如果消息空闲时间超过阈值，可能消费者已经死亡
                # 使用120秒作为默认的死亡检测阈值
                if idle_time > 120 * 1000:  # 120秒
                    logger.warning(
                        f"Consumer {consumer_name} has pending messages "
                        f"idle for {idle_time/1000}s, may be dead"
                    )
                    # 这里可以实现消息重新分配逻辑
                    
        except Exception as e:
            logger.error(f"Error cleaning up expired consumers: {e}")

class HeartbeatConsumerStrategy:
    """基于心跳的简化消费者策略
    
    特点：
    1. 使用随机consumer name
    2. 每个队列维护独立的心跳有序集合
    3. 心跳数据包含worker的详细信息
    4. 自动重置死亡worker的pending任务
    """
    
    def __init__(self, redis_client: redis.StrictRedis, config: Dict = None):
        self.redis = redis_client
        self.config = config or {}
        # 获取异步Redis客户端（从app模块）
        try:
            from ..core.app import get_async_redis_pool
            from redis import asyncio as aioredis
            redis_url = config.get('redis_url') or 'redis://localhost:6379'
            async_pool = get_async_redis_pool(redis_url)
            self.async_redis = aioredis.StrictRedis(connection_pool=async_pool)
        except Exception as e:
            logger.warning(f"Failed to create async redis client: {e}")
            self.async_redis = None
        # 配置参数
        self.heartbeat_interval = self.config.get('heartbeat_interval', 1)  # 5秒心跳
        self.heartbeat_timeout = self.config.get('heartbeat_timeout', 3)  # 30秒超时
        self.scan_interval = self.config.get('scan_interval', 5)  # 10秒扫描一次
        
        # 获取Redis前缀（从配置中）
        self.redis_prefix = config.get('redis_prefix', 'jettask')
        
        # 获取Worker前缀（从配置中，默认为WORKER）
        # 允许不同的服务使用不同的前缀来区分命名空间
        self.worker_prefix = config.get('worker_prefix', 'WORKER')
        
        # 保存配置中的队列列表
        self.configured_queues = config.get('queues', [])
        
        # 获取主机名前缀
        import socket
        try:
            # 首先尝试获取hostname
            hostname = socket.gethostname()
            # 尝试获取IP地址
            ip = socket.gethostbyname(hostname)
            # 优先使用hostname，如果hostname是localhost则使用IP
            prefix = hostname if hostname != 'localhost' else ip
        except:
            # 如果获取失败，使用环境变量或默认值
            prefix = os.environ.get('HOSTNAME', 'unknown')
        
        # 保存主机名前缀，延迟创建consumer_id
        self.hostname_prefix = prefix
        self.consumer_id = None  # 延迟创建，避免在主进程中创建
        
        # 新的数据结构设计 - worker_key 也延迟创建
        self._worker_key = None
        
        self.consumer_names = {}  # queue -> consumer_name mapping
        self.active_queues = set()  # 记录当前活跃的队列
        
        # 后台控制
        self._scanner_thread = None
        self._scanner_task = None
        self._scanner_stop = threading.Event()
        
        # 统计刷新线程/协程
        self._stats_flusher_thread = None
        self._stats_flusher_task = None
        self._stats_flusher_stop = threading.Event()
        
        # 心跳进程管理器
        self._heartbeat_process_manager = None
        self._heartbeat_processes = {}  # queue -> process mapping
        logger.debug("HeartbeatStrategy initialized with process-based heartbeat support")
        
        # 统计缓冲区 - 使用无锁设计
        # 定义统计事件类型
        self.StatsEvent = namedtuple('StatsEvent', ['type', 'queue', 'value', 'timestamp'])
        
        # 使用简单列表替代队列（现在是纯异步环境）
        self.stats_events = []  # 统计事件列表
        
        # 本地累积缓冲区（仅在flush时使用）
        self.stats_accumulator = {
            'running_tasks': defaultdict(int),
            'success_count': defaultdict(int),
            'failed_count': defaultdict(int),
            'total_time': defaultdict(float),
            'total_count': defaultdict(int),
            'total_latency': defaultdict(float)
        }
        
        self.stats_flush_interval = self.config.get('stats_flush_interval', 0.5)  # 更频繁地刷新
        self.last_stats_flush = time.time()
        
        # 延迟启动扫描线程，只有在真正需要时才启动
        self._scanner_started = False
        self._scanner_needs_start = False  # 标记是否需要在异步上下文中启动
        self._startup_time = time.time()  # 记录启动时间，用于心跳超时宽限期
        
        # Worker 扫描器 - 直接初始化
        self.scanner = WorkerScanner(
            self.redis, self.async_redis,
            self.redis_prefix, self.heartbeat_timeout
        )
        
        # 延迟启动统计刷新线程
        self._stats_flusher_started = False
        
        # 注册退出处理
        import atexit
        atexit.register(self.cleanup)
    
    def _find_reusable_worker_id(self, prefix: str) -> str:
        """查找可以复用的离线worker ID
        
        使用分布式锁来防止多个进程同时复用同一个worker ID
        
        Args:
            prefix: 主机名前缀
            
        Returns:
            可复用的consumer_id，如果没有找到则返回None
        """
        # 使用Redis的分布式锁，可以自动等待锁释放
        reuse_lock_key = f"{self.redis_prefix}:{self.worker_prefix}:REUSE:LOCK"
        # 创建Redis锁对象，超时时间5秒，阻塞等待最多2秒
        from redis.lock import Lock
        lock = Lock(self.redis, reuse_lock_key, timeout=5, blocking=True, blocking_timeout=2)
        
        try:
            acquired = lock.acquire()
            if not acquired:
                logger.debug("Could not acquire worker reuse lock, creating new ID")
                return None
            
            # 扫描所有worker键
            pattern = f"{self.redis_prefix}:{self.worker_prefix}:*"
            worker_keys = []
            cursor = 0
            
            # 使用SCAN迭代获取所有worker键
            while True:
                cursor, keys = self.redis.scan(cursor, match=pattern, count=100)
                # 过滤掉HISTORY相关的键、锁键和REUSING标记键
                for key in keys:
                    # key 是 bytes 类型，需要解码或使用 bytes 进行比较
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                    if ':HISTORY:' not in key_str and ':REUSE:LOCK' not in key_str and ':REUSING' not in key_str:
                        worker_keys.append(key)
                if cursor == 0:
                    break
            
            if not worker_keys:
                logger.info("No worker keys found during scan")
                return None
            else:
                logger.info(f"Found {len(worker_keys)} worker keys to check")
            
            # 查找符合条件的离线worker
            offline_workers = []
            
            for worker_key in worker_keys:
                try:
                    # 获取worker数据
                    worker_data = self.redis.hgetall(worker_key)
                    # logger.info(f'{worker_key=} {worker_data=}')
                    if not worker_data:
                        continue
                    # 获取worker的状态信息
                    is_alive_val = worker_data.get('is_alive', 'true')
                    if isinstance(is_alive_val, bytes):
                        is_alive_val = is_alive_val.decode('utf-8')
                    is_alive = is_alive_val.lower() == 'true'
                    
                    last_heartbeat_val = worker_data.get('last_heartbeat', 0)
                    if isinstance(last_heartbeat_val, bytes):
                        last_heartbeat_val = last_heartbeat_val.decode('utf-8')
                    last_heartbeat = float(last_heartbeat_val)
                    current_time = time.time()
                    
                    # 获取离线时间
                    offline_time_str = worker_data.get('offline_time', '0')
                    if isinstance(offline_time_str, bytes):
                        offline_time_str = offline_time_str.decode('utf-8')
                    try:
                        offline_time = float(offline_time_str) if offline_time_str else last_heartbeat
                    except:
                        offline_time = last_heartbeat
                    
                    # 判断worker是否真的离线
                    # 1. is_alive标记为false，或者
                    # 2. 最后心跳时间超过了heartbeat_timeout
                    is_truly_offline = (not is_alive) or (current_time - last_heartbeat > self.heartbeat_timeout)
                    # logger.info(f'{is_truly_offline=} {worker_data=}')
                    if not is_truly_offline:
                        logger.info(f"Worker {is_alive=} {current_time - last_heartbeat} {self.heartbeat_timeout} {worker_data.get('consumer_id')} is still active (last_heartbeat: {current_time - last_heartbeat:.1f}s ago)")
                        continue
                    
                    # 需要离线超过heartbeat_timeout才能被复用（与离线检测保持一致）
                    # min_offline_duration = self.heartbeat_timeout
                    # if offline_time > 0 and (current_time - offline_time) < min_offline_duration:
                    #     logger.info(f"Worker {worker_data.get('consumer_id')} offline for only {current_time - offline_time:.1f}s, need {min_offline_duration}s")
                    #     continue
                    
                    # 获取consumer_id
                    consumer_id = worker_data.get('consumer_id', '')
                    if isinstance(consumer_id, bytes):
                        consumer_id = consumer_id.decode('utf-8')
                    if not consumer_id:
                        continue
                    
                    # 不再检查前缀，允许复用任何离线的worker
                        
                    # 使用离线时间或最后心跳时间
                    if 'offline_time' in worker_data:
                        offline_time = float(worker_data.get('offline_time'))
                    else:
                        # 如果没有offline_time，使用最后心跳时间
                        offline_time = last_heartbeat
                        logger.debug(f"Worker {consumer_id} has no offline_time, using last_heartbeat")
                 
                    offline_workers.append((consumer_id, offline_time, worker_key))
                        
                except Exception as e:
                    logger.debug(f"Error checking worker {worker_key}: {e}")
                    continue
            
            if not offline_workers:
                logger.debug(f"No offline workers found matching prefix {prefix}")
                return None
            else:
                logger.debug(f"Found {len(offline_workers)} offline workers: {[w[0] for w in offline_workers]}")
            
            # 按离线时间排序，选择离线时间最长的（最早离线的）
            offline_workers.sort(key=lambda x: x[1])
            selected_consumer_id, selected_offline_time, selected_worker_key = offline_workers[0]
            
            # 重置该worker的状态 - 保留所有统计数据，但不保留queues
            pipeline = self.redis.pipeline()
            
            # 更新基本信息，保留原有的queues字段
            pipeline.hset(selected_worker_key, mapping={
                'consumer_id': selected_consumer_id,
                'is_alive': 'true',
                'last_heartbeat': str(time.time()),
                'pid': str(os.getpid()),
                'created_at': str(time.time()),
                'messages_transferred': 'false'  # 重置消息转移标记，这是新的生命周期
            })
            
            # 注意：不删除queues字段，让心跳线程根据实际情况更新
            # 这避免了在复用时清空queues导致的显示问题
            
            # 保留所有统计数据，不清空
            
            pipeline.execute()
            
            logger.info(f"Found reusable worker: {selected_consumer_id}, offline since {time.time() - selected_offline_time:.1f}s ago")
            return selected_consumer_id
            
        except Exception as e:
            logger.error(f"Error finding reusable worker ID: {e}")
            return None
        finally:
            try:
                lock.release()
            except:
                pass
    
    def get_prefixed_queue_name(self, queue: str) -> str:
        """为队列名称添加前缀"""
        return f"{self.redis_prefix}:QUEUE:{queue}"
    
    def update_stats(self, queue: str, success: bool = True, processing_time: float = 0.0, 
                    total_latency: float = None):
        """更新worker的统计信息 - 使用无锁队列
        
        Args:
            queue: 队列名称
            success: 是否执行成功
            processing_time: 处理时间（秒） - 实际执行时间
            total_latency: 总延迟时间（秒） - 从任务创建到完成的总时间
        """
        try:
            # 创建统计事件并添加到列表
            timestamp = time.time()
            
            # 成功/失败计数
            event_type = 'success' if success else 'failed'
            self.stats_events.append(
                self.StatsEvent(event_type, queue, 1, timestamp)
            )
            
            # 处理时间
            if processing_time > 0:
                self.stats_events.append(
                    self.StatsEvent('processing_time', queue, processing_time, timestamp)
                )
            
            # 总延迟时间
            if total_latency is not None and total_latency > 0:
                self.stats_events.append(
                    self.StatsEvent('total_latency', queue, total_latency, timestamp)
                )
                
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    def task_started(self, queue: str):
        """任务开始执行时调用 - 添加到事件列表"""
        self.stats_events.append(
            self.StatsEvent('task_started', queue, 1, time.time())
        )
    
    def task_finished(self, queue: str):
        """任务完成时调用 - 添加到事件列表"""
        self.stats_events.append(
            self.StatsEvent('task_finished', queue, -1, time.time())
        )
    
    async def flush_stats_buffer(self):
        """刷新统计缓冲到 Redis - 优化版本（异步版本）"""
        # 如果worker从未初始化，直接返回
        if self.consumer_id is None or self._worker_key is None:
            logger.debug("Worker not initialized, skipping stats flush")
            return
            
        # 直接获取所有待处理的事件
        events = self.stats_events.copy()  # 复制当前事件列表
        self.stats_events.clear()  # 清空原列表
        start_time = time.time()
        
        try:
            if not events:
                return
            
            # 清空累积器
            for buffer in self.stats_accumulator.values():
                buffer.clear()
            
            # 处理所有事件，累积到本地缓冲区
            for event in events:
                if event.type == 'success':
                    self.stats_accumulator['success_count'][event.queue] += event.value
                    self.stats_accumulator['total_count'][event.queue] += event.value
                elif event.type == 'failed':
                    self.stats_accumulator['failed_count'][event.queue] += event.value
                    self.stats_accumulator['total_count'][event.queue] += event.value
                elif event.type == 'processing_time':
                    self.stats_accumulator['total_time'][event.queue] += event.value
                elif event.type == 'total_latency':
                    self.stats_accumulator['total_latency'][event.queue] += event.value
                elif event.type == 'task_started':
                    self.stats_accumulator['running_tasks'][event.queue] += event.value
                elif event.type == 'task_finished':
                    self.stats_accumulator['running_tasks'][event.queue] += event.value  # 注意：task_finished的value是-1
            
            # 批量更新到 Redis
            pipeline = self.async_redis.pipeline()
            processed_queues = set()
            
            # 收集所有需要更新的队列
            for buffer in self.stats_accumulator.values():
                processed_queues.update(buffer.keys())
            
            # 为每个队列构建批量更新
            for queue in processed_queues:
                # 运行中任务数（可能为负数，表示减少）
                if queue in self.stats_accumulator['running_tasks']:
                    delta = self.stats_accumulator['running_tasks'][queue]
                    if delta != 0:
                        pipeline.hincrby(self._worker_key, f'{queue}:running_tasks', delta)
                
                # 成功计数
                if queue in self.stats_accumulator['success_count']:
                    pipeline.hincrby(self._worker_key, f'{queue}:success_count', 
                                   self.stats_accumulator['success_count'][queue])
                
                # 失败计数
                if queue in self.stats_accumulator['failed_count']:
                    pipeline.hincrby(self._worker_key, f'{queue}:failed_count', 
                                   self.stats_accumulator['failed_count'][queue])
                
                # 总计数
                if queue in self.stats_accumulator['total_count']:
                    pipeline.hincrby(self._worker_key, f'{queue}:total_count', 
                                   self.stats_accumulator['total_count'][queue])
                
                # 处理时间
                if queue in self.stats_accumulator['total_time']:
                    pipeline.hincrbyfloat(self._worker_key, f'{queue}:total_processing_time', 
                                        self.stats_accumulator['total_time'][queue])
                
                # 延迟时间
                if queue in self.stats_accumulator['total_latency']:
                    pipeline.hincrbyfloat(self._worker_key, f'{queue}:total_latency_time', 
                                        self.stats_accumulator['total_latency'][queue])
            
            # 执行所有更新
            redis_start = time.time()
            await pipeline.execute()
            redis_duration = time.time() - redis_start
            
            # 批量计算并更新平均值（使用单独的pipeline以提高效率）
            if processed_queues:
                # 批量获取所有需要的数据
                fields = []
                for queue in processed_queues:
                    fields.extend([
                        f'{queue}:total_count',
                        f'{queue}:total_processing_time',
                        f'{queue}:total_latency_time'
                    ])
                
                if fields:
                    values = await self.async_redis.hmget(self._worker_key, fields)
                    
                    # 计算平均值并批量更新
                    pipeline = self.async_redis.pipeline()
                    idx = 0
                    for queue in processed_queues:
                        total_count = values[idx] if values[idx] else '0'
                        total_time = values[idx + 1] if values[idx + 1] else '0'
                        total_latency = values[idx + 2] if values[idx + 2] else '0'
                        idx += 3
                        
                        if int(total_count) > 0:
                            # 计算平均处理时间
                            if float(total_time) > 0:
                                avg_time = float(total_time) / int(total_count)
                                pipeline.hset(self._worker_key, f'{queue}:avg_processing_time', f'{avg_time:.3f}')
                            
                            # 计算平均延迟时间
                            if float(total_latency) > 0:
                                avg_latency = float(total_latency) / int(total_count)
                                pipeline.hset(self._worker_key, f'{queue}:avg_latency_time', f'{avg_latency:.3f}')
                    
                    await pipeline.execute()
            
            # 性能统计日志
            total_duration = time.time() - start_time
            if total_duration > 0.05 or len(events) > 100:  # 超过50ms或处理超过100个事件时记录
                logger.info(
                    f"Stats flush performance: "
                    f"events={len(events)}, "
                    f"queues={len(processed_queues)}, "
                    f"total_time={total_duration:.3f}s, "
                    f"redis_time={redis_duration:.3f}s, "
                    f"events_remaining={len(self.stats_events)}, "
                    f"dropped=0"
                )
                
        except Exception as e:
            logger.error(f"Failed to flush stats buffer: {e}")
            # 将未处理的事件放回列表（尽力而为）
            # 只放回后半部分，避免无限循环
            self.stats_events.extend(events[len(events) - len(events) // 2:])
    
    def get_stats(self, queue: str) -> dict:
        """获取队列的统计信息 - 从Redis Hash读取"""
        try:
            # 如果worker未初始化，返回空统计
            if self.consumer_id is None or self._worker_key is None:
                return {
                    'success_count': 0,
                    'failed_count': 0,
                    'total_count': 0,
                    'running_tasks': 0,
                    'avg_processing_time': 0.0
                }
                
            # 批量获取该队列的所有统计字段
            fields = [
                f'{queue}:success_count',
                f'{queue}:failed_count', 
                f'{queue}:total_count',
                f'{queue}:running_tasks',
                f'{queue}:avg_processing_time'
            ]
            
            values = self.redis.hmget(self._worker_key, fields)
            
            return {
                'success_count': int(values[0] or 0),
                'failed_count': int(values[1] or 0),
                'total_count': int(values[2] or 0),
                'running_tasks': int(values[3] or 0),
                'avg_processing_time': float(values[4] or 0.0)
            }
        except Exception as e:
            logger.error(f"Failed to get stats for queue {queue}: {e}")
            return {
                'success_count': 0,
                'failed_count': 0,
                'total_count': 0,
                'running_tasks': 0,
                'avg_processing_time': 0.0
            }
    
    def _ensure_consumer_id(self):
        """确保consumer_id已创建"""
        if self.consumer_id is None:
            # 延迟创建consumer_id
            self.consumer_id = self._find_reusable_worker_id(self.hostname_prefix)
            if not self.consumer_id:
                # 如果没有可复用的，生成新的consumer ID
                self.consumer_id = f"{self.hostname_prefix}-{uuid.uuid4().hex[:8]}-{os.getpid()}"
                logger.info(f"Created new consumer ID: {self.consumer_id}")
            else:
                logger.info(f"Reusing offline worker ID: {self.consumer_id}")
            
            # 更新worker_key
            self._worker_key = f'{self.redis_prefix}:{self.worker_prefix}:{self.consumer_id}'
    
    @property
    def worker_key(self):
        """获取worker_key，确保consumer_id已初始化"""
        self._ensure_consumer_id()
        return self._worker_key
    
    def get_consumer_name(self, queue: str) -> str:
        """获取消费者名称"""
        # 确保consumer_id已创建
        self._ensure_consumer_id()
        
        # 第一次调用时启动扫描器
        if not self._scanner_started:
            self._start_scanner()
            self._scanner_started = True
        
        # 第一次调用时启动统计刷新器
        if not self._stats_flusher_started:
            self._start_stats_flusher()
            self._stats_flusher_started = True
            
        if queue not in self.consumer_names:
            # 为每个队列生成唯一的consumer name
            self.consumer_names[queue] = f"{self.consumer_id}-{queue}"
            self.active_queues.add(queue)
            
            # 为这个队列启动心跳进程
            if queue not in self._heartbeat_processes:
                self._start_heartbeat_process_for_queue(queue)
            
            logger.info(f"Created consumer name for queue {queue}: {self.consumer_names[queue]}")
        return self.consumer_names[queue]
    
    def _ensure_worker_initialized(self):
        """确保worker已初始化"""
        if self.consumer_id is None:
            self._ensure_consumer_id()
        if self._worker_key is None:
            self._worker_key = f"{self.redis_prefix}:{self.worker_prefix}:{self.consumer_id}"
    
    def _start_heartbeat_process_for_queue(self, queue: str):
        """为特定队列启动心跳进程"""
        # 只需要启动一次心跳进程，不需要为每个队列都启动
        if self._heartbeat_process_manager is not None:
            # 心跳进程已经在运行，只需要记录这个队列
            self._heartbeat_processes[queue] = True
            return
        logger.info('启动心跳进程')
        # 第一次调用时创建心跳进程管理器
        if self._heartbeat_process_manager is None:
            # 获取Redis URL
            redis_url = None
            if hasattr(self.redis.connection_pool, 'connection_kwargs'):
                redis_url = self.redis.connection_pool.connection_kwargs.get('url')
            
            if not redis_url:
                # 构造Redis URL
                connection_kwargs = self.redis.connection_pool.connection_kwargs
                host = connection_kwargs.get('host', 'localhost')
                port = connection_kwargs.get('port', 6379)
                db = connection_kwargs.get('db', 0)
                password = connection_kwargs.get('password')
                if password:
                    redis_url = f"redis://:{password}@{host}:{port}/{db}"
                else:
                    redis_url = f"redis://{host}:{port}/{db}"
            
            self._heartbeat_process_manager = HeartbeatProcessManager(
                redis_url=redis_url,
                consumer_id=self.consumer_id,
                heartbeat_interval=self.heartbeat_interval,
                heartbeat_timeout=self.heartbeat_timeout
            )
        
        # 确保worker key存在并初始化
        self._ensure_worker_initialized()
        
        # 初始化worker信息（心跳进程只负责更新last_heartbeat）
        current_time = time.time()
        import socket
        try:
            hostname = socket.gethostname()
            if not hostname or hostname == 'localhost':
                hostname = socket.gethostbyname(socket.gethostname())
        except:
            hostname = os.environ.get('HOSTNAME', 'unknown')
        
        # 设置初始worker信息
        worker_info = {
            'consumer_id': self.consumer_id,
            'host': hostname,
            'pid': str(os.getpid()),
            'created_at': str(current_time),
            'last_heartbeat': str(current_time),
            'is_alive': 'true',
            'heartbeat_timeout': str(self.heartbeat_timeout),
            'queues': ','.join(sorted(self.configured_queues)) if self.configured_queues else queue,
            'messages_transferred': 'false'  # 新worker的消息未转移
        }
        
        # 使用hset直接设置，确保数据写入
        self.redis.hset(self._worker_key, mapping=worker_info)
        # 同时添加到 sorted set
        self.redis.zadd(f"{self.redis_prefix}:ACTIVE_WORKERS", {self.consumer_id: current_time})
        logger.info(f"Initialized worker {self.consumer_id} with key {self._worker_key}")
        
        self._heartbeat_process_manager.add_queue(queue, self._worker_key)
        self._heartbeat_processes[queue] = True
        # logger.info(f"Started heartbeat process for queue {queue}")
    
    def _start_scanner(self):
        """启动扫描器协程"""
        try:
            loop = asyncio.get_running_loop()
            self._scanner_task = loop.create_task(self._scanner_loop())
            # 立即执行一次扫描，清理可能存在的死亡worker
            loop.create_task(self._immediate_scan())
            # logger.info("Started heartbeat scanner coroutine")
        except RuntimeError:
            # 没有运行中的事件循环，标记为需要启动
            logger.debug("No running event loop, scanner will be started when async context is available")
            self._scanner_needs_start = True
    
    async def _immediate_scan(self):
        """启动时立即执行一次扫描（协程版本）"""
        try:
            # logger.info("Performing immediate scan for dead workers...")
            await self._perform_scan()
            # logger.info("Immediate scan completed")
        except Exception as e:
            logger.error(f"Error in immediate scan: {e}")
    
    
    async def _perform_scan(self):
        """执行扫描操作 - 使用高效的 O(log N) 算法"""
        try:
            # 使用 Worker 扫描器
            timeout_workers = await self.scanner.scan_timeout_workers()
            
            if timeout_workers:
                for worker_info in timeout_workers:
                    await self._mark_worker_offline(
                        worker_info['worker_key'],
                        worker_info['worker_data']
                    )
            return
        except Exception as e:
            logger.error(f"Scanner error: {e}")
        
        # 原始扫描逻辑作为后备
        current_time = time.time()
        # 注意：不再使用全局的heartbeat_timeout，而是使用每个worker自己的值
        
        try:
            # 扫描所有worker hash键
            pattern = f"{self.redis_prefix}:{self.worker_prefix}:*"
            worker_keys = []
            cursor = 0
            
            # 使用SCAN迭代获取所有worker键，排除HISTORY相关的键
            while True:
                cursor, keys = await self.async_redis.scan(cursor, match=pattern, count=100)
                # 过滤掉HISTORY相关的键、锁键和REUSING标记键
                for key in keys:
                    # key 是 bytes 类型，需要解码或使用 bytes 进行比较
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                    if ':HISTORY:' not in key_str and ':REUSE:LOCK' not in key_str and ':REUSING' not in key_str:
                        worker_keys.append(key)
                if cursor == 0:
                    break
            
            # 同时清理残留的recovery consumer
            await self._cleanup_stale_recovery_consumers()
            
            if not worker_keys:
                logger.debug("No worker keys found")
                return
            
            timeout_workers = []
            
            # 检查每个worker的心跳时间
            for worker_key in worker_keys:
                try:
                    # 先检查key的类型（现在应该不需要了，但保留作为安全检查）
                    key_type = await self.async_redis.type(worker_key)
                    if key_type != 'hash':
                        logger.warning(f"Worker key {worker_key} is not a hash, type: {key_type}, skipping")
                        continue
                    
                    worker_data = await self.async_redis.hgetall(worker_key)
                    if not worker_data:
                        continue
                        
                    last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                    consumer_id = worker_data.get('consumer_id')
                    is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                    
                    # 获取该worker自己的heartbeat_timeout
                    # 如果没有记录，使用默认值（兼容旧版本）
                    worker_heartbeat_timeout = float(worker_data.get('heartbeat_timeout', self.heartbeat_timeout))
                    
                    # 跳过自己（如果consumer_id已初始化）
                    if self.consumer_id and consumer_id == self.consumer_id:
                        continue
                    
                    # 使用该worker自己的超时时间来判断
                    worker_timeout_threshold = current_time - worker_heartbeat_timeout
                    
                    # 检查是否需要处理这个worker
                    # 只处理心跳超时的活跃worker
                    needs_processing = False
                    
                    if is_alive and last_heartbeat < worker_timeout_threshold:
                        # 心跳超时的活跃worker
                        logger.info(f"Worker {consumer_id} timeout detected: "
                                  f"last_heartbeat={last_heartbeat}, "
                                  f"timeout={worker_heartbeat_timeout}s, "
                                  f"threshold={worker_timeout_threshold}")
                        needs_processing = True
                    
                    if needs_processing:
                        timeout_workers.append((worker_key, worker_data))
                        
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing worker data from {worker_key}: {e}")
                    continue
            
            if timeout_workers:
                logger.info(f"Found {len(timeout_workers)} timeout workers")
                
                for worker_key, worker_data in timeout_workers:
                    consumer_id = worker_data.get('consumer_id')
                    # queues = worker_data.get('queues', '').split(',') if worker_data.get('queues') else []
                    
                    # 使用Redis原生分布式锁来避免多个scanner同时处理同一个worker
                    lock_key = f"{self.redis_prefix}:SCANNER:LOCK:{consumer_id}"
                    lock_ttl = max(1, int(self.scan_interval * 2))  # 确保是整数，最小1秒
                    
                    # 创建Redis锁
                    lock = AsyncLock(
                        self.async_redis,
                        lock_key,
                        timeout=lock_ttl,
                        blocking=False  # 不阻塞，直接跳过
                    )
                    
                    # 尝试获取锁
                    if not await lock.acquire():
                        logger.debug(f"Another scanner is processing worker {consumer_id}, skipping")
                        continue
                    
                    try:
                        # 再次检查worker是否真的超时（避免竞态条件）
                        current_heartbeat = await self.async_redis.hget(worker_key, 'last_heartbeat')
                        if current_heartbeat and float(current_heartbeat) >= timeout_threshold:
                            logger.info(f"Worker {consumer_id} is now alive, skipping")
                            continue
                        
                        logger.info(f"Processing timeout worker: {consumer_id}")
                        # 只标记worker为离线
                        await self._mark_worker_offline(worker_key, worker_data)
                        
                    except Exception as e:
                        logger.error(f"Error processing timeout worker {consumer_id}: {e}")
                    finally:
                        # 释放锁
                        await lock.release()
                        
        except Exception as e:
            logger.error(f"Error in scanner: {e}")
    
    async def _mark_worker_offline(self, worker_key: str, worker_data: dict):
        """只标记worker为离线状态"""
        consumer_id = worker_data.get('consumer_id')
        
        try:
            current_time = time.time()
            is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
            
            # 只有之前是在线的worker才需要初始化消息转移状态
            if is_alive:
                # 标记worker为离线状态，并设置消息转移状态为未转移
                await self.async_redis.hset(worker_key, mapping={
                    'is_alive': 'false',
                    'offline_time': str(current_time),
                    'shutdown_reason': 'heartbeat_timeout',
                    'messages_transferred': 'false'  # 初始状态：消息未转移
                })
                logger.info(f"Marked worker {consumer_id} as offline with messages_transferred=false")
            else:
                # 已经是离线状态的worker，只更新离线时间
                await self.async_redis.hset(worker_key, 'offline_time', str(current_time))
                logger.debug(f"Worker {consumer_id} was already offline, updated offline_time")
                    
        except Exception as e:
            logger.error(f"Error marking worker {consumer_id} offline: {e}")
    
    
    async def _scanner_loop(self):
        """扫描超时worker的循环（协程版本）"""
        while not self._scanner_stop.is_set():
            try:
                await self._perform_scan()
                await asyncio.sleep(self.scan_interval)
            except Exception as e:
                logger.error(f"Error in scanner loop: {e}")
                await asyncio.sleep(5)  # 错误时等待5秒后重试
    
    
    def _start_stats_flusher(self):
        """启动统计刷新器协程"""
        try:
            loop = asyncio.get_running_loop()
            self._stats_flusher_task = loop.create_task(self._stats_flusher_loop())
            logger.info("Started stats flusher coroutine")
        except RuntimeError:
            # 没有运行中的事件循环，标记为需要启动
            logger.debug("No running event loop for stats flusher, will be started when async context is available")
            self._stats_flusher_needs_start = True
    
    async def _stats_flusher_loop(self):
        """统计刷新循环（协程版本）"""
        while not self._stats_flusher_stop.is_set():
            try:
                # 周期性刷新统计缓冲区
                if len(self.stats_events) > 0:
                    # 直接调用异步的 flush_stats_buffer
                    await self.flush_stats_buffer()
                
                # 等待下一个刷新周期
                await asyncio.sleep(self.stats_flush_interval)
            except Exception as e:
                logger.error(f"Error in stats flusher loop: {e}")
                await asyncio.sleep(1)  # 错误时等待1秒后重试
    
    
    
    def _cleanup_stream_consumer(self, queue: str, consumer_name: str):
        """从Redis Stream消费者组中删除consumer"""
        try:
            # 删除消费者（这会阻止它重新加入后继续消费消息）
            prefixed_queue = self.get_prefixed_queue_name(queue)
            result = self.redis.execute_command('XGROUP', 'DELCONSUMER', prefixed_queue, prefixed_queue, consumer_name)
            if result > 0:
                logger.info(f"Deleted stream consumer {consumer_name} from group {queue}")
            else:
                logger.debug(f"Stream consumer {consumer_name} was not found in group {queue}")
        except Exception as e:
            logger.error(f"Error deleting stream consumer {consumer_name}: {e}")

    async def _handle_dead_worker(self, queue: str, worker_info: dict, worker_data: bytes):
        """处理死亡的worker（异步版本）"""
        consumer_name = worker_info.get('consumer_name', 'unknown')
        
        # 使用Redis原生分布式锁来避免多个scanner同时处理同一个consumer
        consumer_lock_key = f"{self.redis_prefix}:CONSUMER:LOCK:{consumer_name}"
        consumer_lock_ttl = 30  # 30秒锁超时
        
        # 创建Redis锁
        lock = AsyncLock(
            self.async_redis,
            consumer_lock_key,
            timeout=consumer_lock_ttl,
            blocking=False  # 不阻塞，直接返回
        )
        
        # 尝试获取锁
        if not await lock.acquire():
            logger.debug(f"Another scanner is handling consumer {consumer_name}, skipping")
            return
        
        try:
            heartbeat_key = f"{self.heartbeat_key_prefix}{queue}"
            
            # 再次检查worker是否真的超时（避免竞态条件）
            current_score = await self.async_redis.zscore(heartbeat_key, worker_data)
            if current_score and time.time() - current_score < self.heartbeat_timeout:
                logger.info(f"Worker {consumer_name} is now alive, skipping")
                return
            
            # 从有序集合中删除死亡的worker（使用原始的worker_data）
            removed = await self.async_redis.zrem(heartbeat_key, worker_data)
            if removed:
                logger.info(f"Removed dead worker {consumer_name} from heartbeat set for queue {queue}")
                
                # 重置该consumer的pending消息
                await self._reset_consumer_pending_messages(queue, consumer_name)
            else:
                logger.debug(f"Worker {consumer_name} already removed by another scanner")
            
        except Exception as e:
            logger.error(f"Error handling dead worker {consumer_name}: {e}")
        finally:
            # 释放锁
            await lock.release()
    
    async def _reset_consumer_pending_messages(self, queue: str, consumer_name: str):
        """重置指定consumer的pending消息 - 优化版本，确保任务不会丢失（异步版本）"""
        recovery_lock_key = f"RECOVERY:{queue}:{consumer_name}"
        max_retries = 3
        
        try:
            # 使用Redis原生分布式锁防止并发恢复同一个consumer
            recovery_lock = AsyncLock(
                self.async_redis,
                recovery_lock_key,
                timeout=300,  # 5分钟超时
                blocking=False  # 不阻塞
            )
            
            # 尝试获取锁
            if not await recovery_lock.acquire():
                logger.warning(f"Another process is recovering messages for {consumer_name}, skipping")
                return
            
            # 首先获取该consumer的所有pending消息
            consumer_messages = []
            try:
                # 分批获取该consumer的所有pending消息
                batch_size = 1000
                last_id = '-'
                
                while True:
                    # 获取一批pending消息
                    prefixed_queue = self.get_prefixed_queue_name(queue)
                    pending_batch = await self.async_redis.xpending_range(
                        prefixed_queue, prefixed_queue,
                        min=last_id, max='+',
                        count=batch_size
                    )
                    
                    if not pending_batch:
                        break
                    
                    # 过滤出属于该consumer的消息
                    for msg in pending_batch:
                        msg_consumer = msg['consumer']
                        # 处理bytes类型
                        if isinstance(msg_consumer, bytes):
                            msg_consumer = msg_consumer.decode('utf-8')
                        if msg_consumer == consumer_name:
                            consumer_messages.append(msg)
                    
                    # 如果获取的消息数小于batch_size，说明已经获取完所有消息
                    if len(pending_batch) < batch_size:
                        break
                    
                    # 更新last_id为最后一条消息的ID，用于下一批查询
                    last_id = pending_batch[-1]['message_id']
                
                if not consumer_messages:
                    logger.debug(f"No pending messages for consumer {consumer_name}")
                    # 仍然尝试删除consumer
                    try:
                        prefixed_queue = self.get_prefixed_queue_name(queue)
                        await self.async_redis.execute_command('XGROUP', 'DELCONSUMER', prefixed_queue, prefixed_queue, consumer_name)
                    except:
                        pass
                    return
                
                logger.info(f"Found {len(consumer_messages)} pending messages for dead consumer {consumer_name}")
                
                # 获取消息ID列表
                message_ids = [msg['message_id'] for msg in consumer_messages]
                
                # 使用一个特殊的consumer来claim这些消息
                temp_consumer = f"recovery-{consumer_name}-{uuid.uuid4().hex[:8]}"
                
                # 记录恢复开始
                await self.async_redis.hset(f"RECOVERY:STATUS:{temp_consumer}", mapping={
                    'start_time': str(time.time()),
                    'total_messages': str(len(message_ids)),
                    'queue': queue,
                    'original_consumer': consumer_name,
                    'status': 'in_progress'
                })
                await self.async_redis.expire(f"RECOVERY:STATUS:{temp_consumer}", 3600)  # 1小时过期
                
                # 分批处理消息，增加重试机制
                recovered_count = 0
                failed_messages = []
                
                for i in range(0, len(message_ids), 100):
                    batch = message_ids[i:i+100]
                    
                    for retry in range(max_retries):
                        try:
                            # 使用pipeline确保原子性
                            pipeline = self.async_redis.pipeline()
                            
                            # 1. Claim消息到临时consumer
                            prefixed_queue = self.get_prefixed_queue_name(queue)
                            claimed = await self.async_redis.xclaim(
                                prefixed_queue, prefixed_queue,
                                temp_consumer,
                                min_idle_time=0,
                                message_ids=batch,
                                force=True
                            )
                            
                            if claimed:
                                # 2. 准备批量添加的数据
                                messages_to_add = []
                                claimed_ids = []
                                
                                for msg_id, msg_data in claimed:
                                    messages_to_add.append((msg_data, msg_id))
                                    claimed_ids.append(msg_id)
                                
                                # 3. 在pipeline中执行所有操作
                                for msg_data, original_id in messages_to_add:
                                    # 添加恢复标记
                                    msg_data['_recovered_from'] = consumer_name
                                    msg_data['_recovery_time'] = str(time.time())
                                    msg_data['_original_id'] = original_id
                                    pipeline.xadd(prefixed_queue, msg_data)
                                
                                # 4. ACK原始消息
                                pipeline.xack(prefixed_queue, prefixed_queue, *claimed_ids)
                                
                                # 5. 执行pipeline
                                results = await pipeline.execute()
                                
                                # 验证所有操作都成功
                                new_ids = [r for r in results[:-1]]  # 前面的都是xadd的结果
                                if all(new_ids):
                                    recovered_count += len(claimed_ids)
                                    logger.debug(f"Successfully recovered batch of {len(claimed_ids)} messages")
                                    break
                                else:
                                    logger.error(f"Pipeline execution failed for some messages, retry {retry + 1}/{max_retries}")
                            else:
                                # 没有成功claim到消息，可能已经被其他进程处理
                                logger.warning(f"No messages claimed from batch, they may have been processed")
                                break
                                
                        except Exception as e:
                            logger.error(f"Error recovering batch (retry {retry + 1}/{max_retries}): {e}")
                            if retry == max_retries - 1:
                                failed_messages.extend(batch)
                    
                    # 更新恢复进度
                    if (i + len(batch)) % 1000 == 0 or i + len(batch) >= len(message_ids):
                        await self.async_redis.hset(f"RECOVERY:STATUS:{temp_consumer}", 
                                      'recovered_count', str(recovered_count))
                
                # 记录恢复结果
                await self.async_redis.hset(f"RECOVERY:STATUS:{temp_consumer}", mapping={
                    'end_time': str(time.time()),
                    'recovered_count': str(recovered_count),
                    'failed_count': str(len(failed_messages)),
                    'status': 'completed' if not failed_messages else 'completed_with_errors'
                })
                
                logger.info(f"Recovery completed: {recovered_count}/{len(message_ids)} messages recovered from {consumer_name}")
                
                if failed_messages:
                    logger.error(f"Failed to recover {len(failed_messages)} messages: {failed_messages[:10]}...")
                    # 将失败的消息ID记录到Redis供后续分析
                    await self.async_redis.rpush(f"RECOVERY:FAILED:{queue}", *[str(mid) for mid in failed_messages[:100]])
                    await self.async_redis.expire(f"RECOVERY:FAILED:{queue}", 86400)  # 保留24小时
                
            except Exception as e:
                logger.error(f"Error getting pending messages: {e}")
                await self.async_redis.hset(f"RECOVERY:STATUS:{temp_consumer}", mapping={
                    'error': str(e),
                    'status': 'failed'
                })
            
            # 清理临时consumer（如果创建了的话）
            if 'temp_consumer' in locals():
                try:
                    prefixed_queue = self.get_prefixed_queue_name(queue)
                    # 确保临时consumer没有新的pending消息
                    temp_pending = await self.async_redis.xpending(prefixed_queue, prefixed_queue)
                    
                    # 处理不同的返回格式
                    if temp_pending and isinstance(temp_pending, dict) and temp_pending.get('consumers'):
                        for consumer_info in temp_pending['consumers']:
                            # 处理不同的consumer_info格式
                            if isinstance(consumer_info, dict):
                                # 新格式：{'name': 'consumer_name', 'pending': count}
                                consumer_name_check = consumer_info.get('name', '')
                                pending_count = consumer_info.get('pending', 0)
                            elif isinstance(consumer_info, (list, tuple)) and len(consumer_info) >= 2:
                                # 旧格式：['consumer_name', count]
                                consumer_name_check = consumer_info[0]
                                pending_count = consumer_info[1]
                            else:
                                continue
                            
                            # 处理bytes类型
                            if isinstance(consumer_name_check, bytes):
                                consumer_name_check = consumer_name_check.decode('utf-8')
                            
                            if consumer_name_check == temp_consumer and int(pending_count) > 0:
                                logger.warning(f"Temp consumer {temp_consumer} still has {pending_count} pending messages")
                                # 递归恢复临时consumer的消息
                                await self._reset_consumer_pending_messages(queue, temp_consumer)
                    
                    # 删除临时consumer
                    await self.async_redis.execute_command('XGROUP', 'DELCONSUMER', prefixed_queue, prefixed_queue, temp_consumer)
                    logger.debug(f"Cleaned up temp consumer {temp_consumer}")
                except Exception as e:
                    logger.error(f"Error cleaning up temp consumer: {e}")
            
            # 最后删除死亡的consumer
            try:
                prefixed_queue = self.get_prefixed_queue_name(queue)
                await self.async_redis.execute_command('XGROUP', 'DELCONSUMER', prefixed_queue, prefixed_queue, consumer_name)
                logger.debug(f"Deleted consumer {consumer_name}")
            except:
                pass
                        
        except Exception as e:
            logger.error(f"Error resetting pending messages for {consumer_name}: {e}")
        finally:
            # 释放恢复锁
            await self.async_redis.delete(recovery_lock_key)
    
    async def _cleanup_stale_recovery_consumers(self):
        """清理残留的recovery consumer（异步版本）"""
        try:
            # 获取所有队列
            queues_pattern = f"{self.redis_prefix}:*"
            all_keys = []
            cursor = 0
            
            while True:
                cursor, keys = await self.async_redis.scan(cursor, match=queues_pattern, count=100)
                all_keys.extend(keys)
                if cursor == 0:
                    break
            
            # 筛选出stream类型的队列
            stream_queues = []
            for key in all_keys:
                try:
                    if await self.async_redis.type(key) == 'stream':
                        stream_queues.append(key)
                except:
                    continue
            
            cleaned_count = 0
            for queue in stream_queues:
                try:
                    # 跳过非队列的stream（比如可能的其他用途的stream）
                    if ':QUEUE:' not in queue:
                        continue
                    
                    # 获取该队列的所有consumer信息
                    # 在jettask中，consumer group名称和stream名称相同（都是带前缀的）
                    try:
                        pending_info = await self.async_redis.xpending(queue, queue)
                    except Exception as xpending_error:
                        # 如果xpending失败，可能是因为consumer group不存在
                        logger.debug(f"xpending failed for {queue}: {xpending_error}")
                        continue
                    
                    # 处理不同的返回格式
                    if not pending_info:
                        continue
                    
                    # 如果返回的是数字0，说明没有pending消息
                    if isinstance(pending_info, int) and pending_info == 0:
                        continue
                    
                    # 如果不是字典，跳过
                    if not isinstance(pending_info, dict):
                        logger.debug(f"Unexpected xpending response for {queue}: {type(pending_info)} - {pending_info}")
                        continue
                    
                    # 检查是否有consumers字段
                    consumers = pending_info.get('consumers')
                    if not consumers:
                        continue
                    
                    # 检查recovery consumer
                    for consumer_info in consumers:
                        # 处理不同的consumer_info格式
                        if isinstance(consumer_info, dict):
                            # 新格式：{'name': 'consumer_name', 'pending': count}
                            consumer_name = consumer_info.get('name', '')
                            pending_count = consumer_info.get('pending', 0)
                        elif isinstance(consumer_info, (list, tuple)) and len(consumer_info) >= 2:
                            # 旧格式：['consumer_name', count]
                            consumer_name = consumer_info[0]
                            pending_count = consumer_info[1]
                        else:
                            logger.warning(f"Unexpected consumer info format: {consumer_info}")
                            continue
                        
                        # 处理bytes类型
                        if isinstance(consumer_name, bytes):
                            consumer_name = consumer_name.decode('utf-8')
                        
                        # 确保pending_count是整数
                        try:
                            pending_count = int(pending_count)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid pending count for {consumer_name}: {pending_count}")
                            continue
                        
                        # 识别recovery consumer
                        if consumer_name.startswith('recovery-'):
                            
                            # 检查recovery状态
                            status_key = f"RECOVERY:STATUS:{consumer_name}"
                            status = await self.async_redis.hget(status_key, 'status')
                            
                            # 如果状态已完成或不存在状态信息（可能是旧的残留）
                            if not status or status in ['completed', 'completed_with_errors', 'failed']:
                                # 如果还有pending消息，先恢复它们
                                if pending_count > 0:
                                    logger.warning(f"Found stale recovery consumer {consumer_name} with {pending_count} pending messages")
                                    # 递归恢复这些消息
                                    queue_name = queue.split(':', 1)[-1] if ':' in queue else queue
                                    await self._reset_consumer_pending_messages(queue_name, consumer_name)
                                else:
                                    # 没有pending消息，直接删除
                                    try:
                                        await self.async_redis.execute_command('XGROUP', 'DELCONSUMER', queue, queue, consumer_name)
                                        logger.info(f"Cleaned up stale recovery consumer {consumer_name}")
                                        cleaned_count += 1
                                    except Exception as e:
                                        logger.error(f"Failed to delete recovery consumer {consumer_name}: {e}")
                        
                except Exception as e:
                    import traceback
                    logger.error(f"Error cleaning recovery consumers in queue {queue}: {e}")
                    logger.error(f"Traceback:\n{traceback.format_exc()}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} stale recovery consumers")
                
        except Exception as e:
            logger.error(f"Error in cleanup_stale_recovery_consumers: {e}")
    
    def is_heartbeat_timeout(self) -> bool:
        """检查心跳是否已超时"""
        # 给新启动的worker一个宽限期（15秒），避免误判
        if hasattr(self, '_startup_time'):
            if time.time() - self._startup_time < 15:
                return False
        
        if self._heartbeat_process_manager:
            return self._heartbeat_process_manager.is_heartbeat_timeout()
        return False
    
    def cleanup(self):
        """清理资源"""
        # 如果consumer_id从未被创建，说明这个实例从未真正运行
        if self.consumer_id is None:
            logger.debug("HeartbeatConsumerStrategy cleanup: never initialized, skipping")
            return
            
        logger.debug(f"Cleaning up heartbeat consumer {self.consumer_id}")
        
        # 先停止所有心跳进程，避免新的数据产生
        if self._heartbeat_process_manager and self._heartbeat_process_manager.heartbeat_process:
            logger.debug("Stopping heartbeat processes...")
            self._heartbeat_process_manager.stop_all()
            
        # 停止扫描器（如果已启动）
        if self._scanner_started:
            self._scanner_stop.set()
            # 如果是协程，取消它
            if self._scanner_task and not self._scanner_task.done():
                self._scanner_task.cancel()
        
        # 停止统计刷新线程/协程（如果已启动）
        if self._stats_flusher_started:
            self._stats_flusher_stop.set()
            # 如果是协程，取消它
            if self._stats_flusher_task and not self._stats_flusher_task.done():
                self._stats_flusher_task.cancel()
        
        # 在cleanup时简单记录未处理的统计事件数量
        try:
            events_count = len(self.stats_events)
            if events_count > 0:
                logger.warning(f"Dropped {events_count} stats events during cleanup (async flush not available)")
                self.stats_events.clear()  # 清空以避免内存泄露
        except Exception as e:
            logger.error(f"Failed to clear stats buffer during cleanup: {e}")
        
        # 立即将worker标记为离线状态
        worker_data = None
        try:
            current_time = time.time()
            
            # 只有在consumer_id已初始化的情况下才进行清理
            if self.consumer_id is None:
                logger.debug("Consumer ID was never initialized, skipping worker cleanup")
                return
                
            # 直接使用已有的worker_key，不要触发getter
            worker_key = self._worker_key
            if not worker_key:
                logger.debug("Worker key was never initialized, skipping worker cleanup")
                return
                
            # 获取当前worker的数据用于保存历史
            worker_data = self.redis.hgetall(worker_key)
            
            # 如果worker从未运行过（没有数据），则不需要处理
            if not worker_data:
                logger.info(f"Worker {self.consumer_id} never started, skipping cleanup")
                return
            
            # 更新worker状态为离线（保留所有现有数据）
            pipeline = self.redis.pipeline()
            pipeline.hset(worker_key, mapping={
                'is_alive': 'false',
                'offline_time': str(current_time),
                'shutdown_reason': 'graceful_shutdown',
                'messages_transferred': 'false'  # 标记消息需要转移
            })
            
            # 获取worker的队列列表
            queues = worker_data.get('queues', '').split(',') if worker_data.get('queues') else []
            
            # 将所有队列的运行中任务数归零
            for queue in queues:
                if queue.strip():
                    pipeline.hset(worker_key, f'{queue}:running_tasks', '0')
            
            # 执行批量更新
            pipeline.execute()
            
            # 不再保存历史记录，WORKER键本身就包含了所有信息
            
            logger.info(f"Marked worker {self.consumer_id} as offline immediately")
            
        except Exception as e:
            logger.error(f"Failed to mark worker as offline during cleanup: {e}")
        
        # 如果从未成功运行过，直接返回
        if not worker_data:
            logger.info(f"Heartbeat consumer {self.consumer_id} stopped gracefully (never started)")
            return
        
        # 等待扫描线程结束（非阻塞）
        if self._scanner_started and self._scanner_thread and self._scanner_thread.is_alive():
            max_wait_time = 0.5  # 最多等待0.5秒
            self._scanner_thread.join(timeout=max_wait_time)
            if self._scanner_thread.is_alive():
                logger.warning("Scanner thread did not stop in time")
        
        # 等待统计刷新线程结束（非阻塞）
        if self._stats_flusher_started and self._stats_flusher_thread and self._stats_flusher_thread.is_alive():
            max_wait_time = 0.5  # 最多等待0.5秒
            self._stats_flusher_thread.join(timeout=max_wait_time)
            if self._stats_flusher_thread.is_alive():
                logger.warning("Stats flusher thread did not stop in time")
        
        # 重要：不删除心跳记录！
        # 心跳记录必须保留，让scanner能够检测到worker离线并恢复pending消息
        # 心跳会因为超时自动被scanner清理
        logger.info(f"Heartbeat consumer {self.consumer_id} stopped")