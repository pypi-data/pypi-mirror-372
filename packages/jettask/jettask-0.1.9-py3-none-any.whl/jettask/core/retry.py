"""
高性能任务重试机制
"""

import asyncio
import time
import random
from typing import Optional, List, Type, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """重试策略"""
    FIXED = "fixed"  # 固定间隔
    LINEAR = "linear"  # 线性增长
    EXPONENTIAL = "exponential"  # 指数退避
    RANDOM_JITTER = "random_jitter"  # 带随机抖动的指数退避


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3  # 最大重试次数
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL  # 重试策略
    base_delay: float = 1.0  # 基础延迟（秒）
    max_delay: float = 60.0  # 最大延迟（秒）
    exponential_base: float = 2.0  # 指数基数
    jitter: bool = True  # 是否添加随机抖动
    jitter_range: float = 0.1  # 抖动范围（0-1）
    
    # 可重试的异常类型
    retryable_exceptions: Optional[List[Type[Exception]]] = None
    # 不可重试的异常类型（优先级高于retryable）
    non_retryable_exceptions: Optional[List[Type[Exception]]] = None
    # 自定义重试判断函数
    retry_predicate: Optional[Callable[[Exception], bool]] = None
    
    def should_retry(self, exception: Exception) -> bool:
        """判断是否应该重试"""
        # 先检查不可重试的异常
        if self.non_retryable_exceptions:
            for exc_type in self.non_retryable_exceptions:
                if isinstance(exception, exc_type):
                    return False
        
        # 使用自定义判断函数
        if self.retry_predicate:
            return self.retry_predicate(exception)
        
        # 检查可重试的异常
        if self.retryable_exceptions:
            for exc_type in self.retryable_exceptions:
                if isinstance(exception, exc_type):
                    return True
            return False
        
        # 默认：所有异常都重试
        return True
    
    def calculate_delay(self, attempt: int) -> float:
        """计算重试延迟"""
        if self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * attempt
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        elif self.strategy == RetryStrategy.RANDOM_JITTER:
            # 指数退避加随机抖动
            delay = self.base_delay * (self.exponential_base ** (attempt - 1))
            if self.jitter:
                jitter = random.uniform(-self.jitter_range, self.jitter_range) * delay
                delay += jitter
        else:
            delay = self.base_delay
        
        # 确保不超过最大延迟
        return min(delay, self.max_delay)


class LocalRetryManager:
    """本地重试管理器 - 高性能实现"""
    
    def __init__(self):
        # 使用字典存储待重试的任务，按执行时间排序
        self._retry_tasks: Dict[str, Dict[str, Any]] = {}
        # 延迟重试队列（使用list实现简单的优先队列）
        self._delayed_retries: List[tuple[float, str, Dict]] = []
        self._lock = asyncio.Lock()
        self._running = True
        self._process_task = None
        
    async def start(self):
        """启动重试处理器"""
        if not self._process_task:
            self._process_task = asyncio.create_task(self._process_delayed_retries())
    
    async def stop(self):
        """停止重试处理器"""
        self._running = False
        if self._process_task:
            await self._process_task
    
    async def schedule_retry(
        self, 
        task_id: str,
        task_func: Callable,
        args: tuple,
        kwargs: dict,
        config: RetryConfig,
        attempt: int,
        last_exception: Exception
    ) -> Optional[Any]:
        """调度重试任务"""
        
        if attempt > config.max_retries:
            logger.error(f"Task {task_id} exceeded max retries ({config.max_retries})")
            raise last_exception
        
        # 计算延迟
        delay = config.calculate_delay(attempt)
        
        if delay <= 0.1:  # 小于100ms的延迟直接重试
            logger.info(f"Immediately retrying task {task_id}, attempt {attempt}/{config.max_retries}")
            return await self._execute_with_retry(
                task_id, task_func, args, kwargs, config, attempt
            )
        else:
            # 延迟重试
            execute_at = time.time() + delay
            logger.info(f"Scheduling retry for task {task_id}, attempt {attempt}/{config.max_retries}, delay {delay:.2f}s")
            
            async with self._lock:
                # 插入到延迟队列，保持按时间排序
                task_info = {
                    'task_id': task_id,
                    'task_func': task_func,
                    'args': args,
                    'kwargs': kwargs,
                    'config': config,
                    'attempt': attempt,
                    'execute_at': execute_at
                }
                
                # 二分查找插入位置
                left, right = 0, len(self._delayed_retries)
                while left < right:
                    mid = (left + right) // 2
                    if self._delayed_retries[mid][0] <= execute_at:
                        left = mid + 1
                    else:
                        right = mid
                self._delayed_retries.insert(left, (execute_at, task_id, task_info))
            
            # 返回一个Future，调用者可以等待
            future = asyncio.Future()
            task_info['future'] = future
            return await future
    
    async def _execute_with_retry(
        self,
        task_id: str,
        task_func: Callable,
        args: tuple,
        kwargs: dict,
        config: RetryConfig,
        attempt: int
    ) -> Any:
        """执行任务并处理重试"""
        try:
            # 执行任务
            if asyncio.iscoroutinefunction(task_func):
                result = await task_func(*args, **kwargs)
            else:
                result = task_func(*args, **kwargs)
            
            logger.debug(f"Task {task_id} succeeded on attempt {attempt}")
            return result
            
        except Exception as e:
            if config.should_retry(e) and attempt < config.max_retries:
                # 需要重试
                return await self.schedule_retry(
                    task_id, task_func, args, kwargs, 
                    config, attempt + 1, e
                )
            else:
                # 不重试或已达最大次数
                logger.error(f"Task {task_id} failed after {attempt} attempts: {e}")
                raise
    
    async def _process_delayed_retries(self):
        """处理延迟重试队列"""
        while self._running:
            try:
                current_time = time.time()
                tasks_to_execute = []
                
                # 获取所有到期的任务
                async with self._lock:
                    while self._delayed_retries and self._delayed_retries[0][0] <= current_time:
                        _, task_id, task_info = self._delayed_retries.pop(0)
                        tasks_to_execute.append(task_info)
                
                # 并发执行所有到期任务
                if tasks_to_execute:
                    execute_tasks = []
                    for task_info in tasks_to_execute:
                        task = asyncio.create_task(
                            self._execute_delayed_retry(task_info)
                        )
                        execute_tasks.append(task)
                    
                    # 等待所有任务完成
                    await asyncio.gather(*execute_tasks, return_exceptions=True)
                
                # 计算下次唤醒时间
                async with self._lock:
                    if self._delayed_retries:
                        next_wake = self._delayed_retries[0][0]
                        sleep_time = max(0.01, min(0.1, next_wake - time.time()))
                    else:
                        sleep_time = 0.1
                
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in retry processor: {e}")
                await asyncio.sleep(0.1)
    
    async def _execute_delayed_retry(self, task_info: Dict[str, Any]):
        """执行延迟重试任务"""
        future = task_info.get('future')
        try:
            result = await self._execute_with_retry(
                task_info['task_id'],
                task_info['task_func'],
                task_info['args'],
                task_info['kwargs'],
                task_info['config'],
                task_info['attempt']
            )
            if future and not future.done():
                future.set_result(result)
        except Exception as e:
            if future and not future.done():
                future.set_exception(e)


# 全局重试管理器实例
_retry_manager = None


def get_retry_manager() -> LocalRetryManager:
    """获取全局重试管理器"""
    global _retry_manager
    if _retry_manager is None:
        _retry_manager = LocalRetryManager()
    return _retry_manager


async def retry_task(
    task_func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    config: RetryConfig = None,
    task_id: str = None
) -> Any:
    """
    便捷的重试函数
    
    Example:
        # 简单使用
        result = await retry_task(
            my_async_func,
            args=(1, 2),
            config=RetryConfig(max_retries=3)
        )
        
        # 自定义配置
        config = RetryConfig(
            max_retries=5,
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=0.5,
            retryable_exceptions=[TimeoutError, ConnectionError],
            non_retryable_exceptions=[ValueError]
        )
        result = await retry_task(my_func, config=config)
    """
    if kwargs is None:
        kwargs = {}
    
    if config is None:
        config = RetryConfig()
    
    if task_id is None:
        task_id = f"task_{id(task_func)}_{time.time()}"
    
    manager = get_retry_manager()
    
    # 确保管理器已启动
    await manager.start()
    
    # 执行任务
    return await manager._execute_with_retry(
        task_id, task_func, args, kwargs, config, 1
    )