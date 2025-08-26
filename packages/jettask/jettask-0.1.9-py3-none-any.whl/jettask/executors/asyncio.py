import asyncio
import time
import logging
import traceback
from ..utils.traceback_filter import filter_framework_traceback
from ..utils.task_logger import TaskContextManager, configure_task_logging
from ..utils.serializer import dumps_str
from typing import Optional, Union
from collections import defaultdict, deque
import os
# 按队列分组以优化批量操作
from collections import defaultdict
from .base import BaseExecutor
import random
from ..exceptions import RetryableError

logger = logging.getLogger('app')

# Try to use uvloop for better performance
try:
    import uvloop
    uvloop.install()
    logger.info("Using uvloop for better performance")
except ImportError:
    pass


class AsyncioExecutor(BaseExecutor):
    """High-performance asyncio executor"""
    
    def __init__(self, event_queue, app, concurrency=100):
        super().__init__(event_queue, app, concurrency)
        
        # Caching for pending count
        self.pending_cache = {}
        self.pending_cache_expire = 0
        
        # 统一 Pipeline 管理器配置
        self.pipeline_config = {
            'ack': {'max_batch': 1000, 'max_delay': 0.05},  # 50ms
            'task_info': {'max_batch': 2000, 'max_delay': 0.1},  # 100ms
            'status': {'max_batch': 1000, 'max_delay': 0.15},  # 150ms
            'data': {'max_batch': 1000, 'max_delay': 0.15},  # 150ms
            'stats': {'max_batch': 5000, 'max_delay': 0.2}  # 200ms
        }
        
        # 统一的 Pipeline 缓冲区
        self.pending_acks = []
        self.status_updates = []  
        self.data_updates = []
        self.task_info_updates = {}  # 使用字典存储每个任务的Hash更新
        self.stats_updates = []  # 新增：统计信息缓冲区
        
        # Pipeline 时间跟踪
        self.last_pipeline_flush = {
            'ack': time.time(),
            'task_info': time.time(),
            'status': time.time(),
            'data': time.time(),
            'stats': time.time()
        }
        
        # 兼容旧代码的设置
        self.ack_buffer_size = self.pipeline_config['ack']['max_batch']
        self.max_ack_buffer_size = 2000
        self.status_batch_size = self.pipeline_config['status']['max_batch']
        self.data_batch_size = self.pipeline_config['data']['max_batch']
        
        # 添加前缀
        self.prefix = self.app.ep.redis_prefix or 'jettask'
        
        # 统一 Pipeline 刷新策略
        self.last_flush_time = time.time()
        self.pipeline_operation_count = 0  # 统计总操作数
        
        # 配置任务日志格式（根据环境变量）
        log_format = os.environ.get('JETTASK_LOG_FORMAT', 'text').lower()
        if log_format == 'json':
            configure_task_logging(format='json')
        else:
            # 可以自定义文本格式
            format_string = os.environ.get('JETTASK_LOG_FORMAT_STRING')
            if format_string:
                configure_task_logging(format='text', format_string=format_string)
        self.max_flush_interval = 0.05  # 50ms最大刷新间隔
        self.min_flush_interval = 0.005  # 5ms最小刷新间隔
        
        # 性能优化4: 预编译常量和缓存
        self._status_prefix = self.app._status_prefix
        self._result_prefix = self.app._result_prefix
        self._prefixed_queue_cache = {}  # 缓存队列名称
        
        # 默认启用高性能模式
        self._stats_lock = asyncio.Lock()
        self._high_performance_mode = True  # 始终启用高性能模式
        
    def _get_prefixed_queue_cached(self, queue: str) -> str:
        """缓存队列名称以避免重复字符串拼接"""
        if queue not in self._prefixed_queue_cache:
            self._prefixed_queue_cache[queue] = self.app.ep.get_prefixed_queue_name(queue)
        return self._prefixed_queue_cache[queue]
        
    
    async def get_pending_count_cached(self, queue: str) -> int:
        """Get cached pending count"""
        current_time = time.time()
        
        if (current_time - self.pending_cache_expire > 30 or  # 优化：延长缓存时间
            queue not in self.pending_cache):
            try:
                pending_info = await self.app.ep.async_redis_client.xpending(queue, queue)
                self.pending_cache[queue] = pending_info.get("pending", 0)
                self.pending_cache_expire = current_time
            except Exception:
                self.pending_cache[queue] = 0
                
        return self.pending_cache.get(queue, 0)
    
    async def _quick_ack(self, queue: str, event_id: str, group_name: str = None):
        """Quick ACK with unified pipeline management"""
        # 如果没有提供group_name，使用queue作为默认值（兼容旧代码）
        group_name = group_name or queue
        self.pending_acks.append((queue, event_id, group_name))
        current_time = time.time()
        
        # 检查是否需要刷新统一 Pipeline
        ack_config = self.pipeline_config['ack']
        time_since_flush = current_time - self.last_pipeline_flush['ack']
        
        should_flush = (
            len(self.pending_acks) >= ack_config['max_batch'] or  # 达到批量大小
            (len(self.pending_acks) >= 50 and  # 或有50个且超时
             time_since_flush >= ack_config['max_delay']) or
            len(self.pending_acks) >= self.max_ack_buffer_size * 0.1  # 达到最大缓冲区10%
        )
        
        if should_flush:
            await self._flush_all_buffers()  # 使用统一的刷新
        
    async def _flush_all_buffers(self):
        """统一 Pipeline 刷新 - 一次提交所有操作"""
        # 创建统一的 pipeline（使用二进制客户端，避免编码问题）
        pipeline = self.app.ep.async_binary_redis_client.pipeline()
        
        operations_count = 0
        
        # 1. 处理 ACK 操作（使用二进制客户端）
        if self.pending_acks:
            acks_by_queue_group = defaultdict(lambda: defaultdict(list))
            for item in self.pending_acks:
                if len(item) == 3:
                    queue, event_id, group_name = item
                else:
                    queue, event_id = item
                    group_name = queue
                
                prefixed_queue = self._get_prefixed_queue_cached(queue)
                acks_by_queue_group[prefixed_queue][group_name].append(event_id)
            
            for prefixed_queue, groups in acks_by_queue_group.items():
                for group_name, event_ids in groups.items():
                    stream_key = prefixed_queue.encode() if isinstance(prefixed_queue, str) else prefixed_queue
                    group_key = group_name.encode() if isinstance(group_name, str) else group_name
                    batch_bytes = [b.encode() if isinstance(b, str) else b for b in event_ids]
                    
                    # 添加到统一 pipeline
                    logger.info(f'准备ack {batch_bytes=}')
                    pipeline.xack(stream_key, group_key, *batch_bytes)
                    operations_count += 1
            
            self.pending_acks.clear()
        
        # 2. 处理任务信息更新（Hash）
        task_change_events = []  # 收集变更的任务ID
        if self.task_info_updates:
            for event_id, updates in self.task_info_updates.items():
                key = f"{self.prefix}:TASK:{event_id}".encode()  # 转为 bytes
                if updates:
                    # 将更新的值编码为 bytes
                    encoded_updates = {k.encode(): v.encode() if isinstance(v, str) else v for k, v in updates.items()}
                    pipeline.hset(key, mapping=encoded_updates)
                    pipeline.expire(key, 3600)
                    operations_count += 2
                    
                    # 收集变更的任务ID
                    task_change_events.append(event_id)
            
            # 发送变更事件到专门的 Stream 队列
            if task_change_events:
                change_stream_key = f"{self.prefix}:TASK_CHANGES".encode()
                for event_id in task_change_events:
                    # 只发送事件ID
                    change_data = {
                        b'event_id': event_id.encode() if isinstance(event_id, str) else event_id
                    }
                    pipeline.xadd(change_stream_key, change_data, maxlen=10000)  # 保留最近10000条变更
                    operations_count += 1
            
            self.task_info_updates.clear()
        
        # 3. 处理统计信息（如果有）
        if hasattr(self, 'stats_updates') and self.stats_updates:
            # 批量更新统计信息
            for stat_op in self.stats_updates:
                # 执行统计操作
                if 'queue' in stat_op and 'field' in stat_op:
                    stats_key = f"{self.prefix}:STATS:{stat_op['queue']}".encode()  # 转为 bytes
                    field = stat_op['field'].encode() if isinstance(stat_op['field'], str) else stat_op['field']
                    pipeline.hincrby(stats_key, field, stat_op.get('value', 1))
                    operations_count += 1
            self.stats_updates.clear()
        
        # 统一执行所有 pipeline 操作
        if operations_count > 0:
            try:
                # 执行统一的 pipeline
                results = await pipeline.execute()
                
                # 检查结果
                if isinstance(results, Exception):
                    logger.error(f"Pipeline execution error: {results}")
                else:
                    # 检查各个操作的结果
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"Pipeline operation {i} error: {result}")
                
                logger.debug(f"Unified pipeline executed {operations_count} operations")
                self.pipeline_operation_count += operations_count
                
            except Exception as e:
                logger.error(f"Pipeline flush error: {e}")
        
        # 更新所有刷新时间
        current_time = time.time()
        for key in self.last_pipeline_flush:
            self.last_pipeline_flush[key] = current_time
        self.last_flush_time = current_time
    
    async def _collect_stats_async(self, queue: str, success: bool, processing_time: float, total_latency: float):
        """高性能异步统计收集 - 加入 Pipeline 缓冲区"""
        try:
            if hasattr(self.app, 'consumer_manager') and self.app.consumer_manager:
                # 将统计信息加入缓冲区而不是立即发送
                if hasattr(self, 'stats_updates'):
                    self.stats_updates.append({
                        'queue': queue,
                        'field': 'success_count' if success else 'error_count',
                        'value': 1
                    })
                    self.stats_updates.append({
                        'queue': queue,
                        'field': 'total_processing_time',
                        'value': int(processing_time * 1000)  # 转换为毫秒
                    })
                    
                    # 检查是否需要刷新统计缓冲区
                    if len(self.stats_updates) >= self.pipeline_config['stats']['max_batch']:
                        asyncio.create_task(self._flush_all_buffers())
                else:
                    # 兼容旧方式
                    asyncio.create_task(self._update_stats_nonblocking(queue, success, processing_time, total_latency))
        except Exception:
            pass  # 统计错误不应影响主流程
    
    async def _update_stats_nonblocking(self, queue: str, success: bool, processing_time: float, total_latency: float):
        """非阻塞统计更新"""
        try:
            self.app.consumer_manager.task_finished(queue)
            self.app.consumer_manager.update_stats(
                queue=queue,
                success=success,
                processing_time=processing_time,
                total_latency=total_latency
            )
        except Exception as e:
            logger.debug(f"Stats collection error (non-critical): {e}")
    
        
    async def logic(self, semaphore: asyncio.Semaphore, event_id: str, event_data: dict, queue: str, routing: dict = None, consumer: str = None, group_name: str = None, **kwargs):
        """Process a single task"""
        # 初始化所有变量，避免在 finally 块中未定义
        execution_start_time = time.time()
        status = "error"  # 默认状态
        exception = None
        error_msg = None
        ret = None
        task = None  # 初始化 task 变量
        args = ()    # 初始化参数
        kwargs_inner = {}  # 初始化关键字参数（避免与函数参数 kwargs 冲突）
        
        # 获取任务名称（尽早获取，以便设置日志上下文）
        task_name = event_data.get("_task_name") or event_data.get("name", "unknown")
        
        # 设置任务日志上下文 - 包含整个任务处理流程
        async with TaskContextManager(
            event_id=event_id,
            task_name=task_name,
            queue=queue,
            worker_id=consumer  # 使用consumer作为worker_id
        ):
            try:
                # 检查是否是恢复的消息
                if kwargs.get('_recovery'):
                    logger.info(f"Processing recovered message {event_id} from {kwargs.get('_claimed_from', 'unknown')}")
                # print(f'{event_data=}')
                # 检查是否是延迟任务
                if event_data.get('is_delayed') and 'execute_at' in event_data:
                    execute_at = float(event_data['execute_at'])
                    current_time = time.time()
                    
                    if execute_at > current_time:
                        # 任务还没到执行时间，直接丢弃
                        # 不ACK消息，让它保持在pending状态
                        # event_pool会通过zset检查并在时间到期后通过xclaim认领
                        logger.info(f"Task {event_id} delayed until {execute_at}, keeping in pending state")
                        return
                
                # 获取重试配置（来自任务装饰器或apply_async）
                retry_config = event_data.get('retry_config', {})
                max_retries = retry_config.get('max_retries', 0)
                

                # async with semaphore:
                # 任务名称已经在外层获取过了
                
                if not task_name:
                    logger.error(f"No task name found! event_data keys: {list(event_data.keys())}, event_id: {event_id}")
                
                task = self.app.get_task_by_name(task_name)
                if not task:
                    exception = f"{task_name=} {queue=} {routing=} 未绑定任何task"
                    logger.error(exception)
                    await self._quick_ack(queue, event_id, group_name)
                    
                    # 任务不存在时也记录started_at（使用当前时间）
                    current_time = time.time()
                    # 恢复的消息可能没有trigger_time，使用当前时间作为默认值
                    trigger_time_float = float(event_data.get('trigger_time', current_time))
                    duration = current_time - trigger_time_float
                    # 使用Hash更新
                    self.task_info_updates[event_id] = {
                        "status": "error",
                        "exception": exception,
                        "started_at": str(current_time),
                        "completed_at": str(current_time),
                        "duration": str(duration),
                        "consumer": consumer,
                        "result": "null"  # 任务不存在时没有结果
                    }
                    # 使用统一的 pipeline 刷新
                    await self._flush_all_buffers()
                    return
                
                self.pedding_count = await self.get_pending_count_cached(queue)
                
                # 重置状态为 success（默认是 error）
                status = "success"
                
                # 更新执行开始时间（之前已经初始化过）
                execution_start_time = time.time()
                
                # 获取参数（现在直接是对象，不需要反序列化）
                args = event_data.get("args", ()) or ()
                
                # 统一处理kwargs（现在直接是对象，不需要反序列化）
                kwargs_inner = event_data.get("kwargs", {}) or {}
                
                # 对于广播消息，检查是否需要提取特定字段作为参数
                if event_data.get("_broadcast"):
                    # 如果消息包含 event_type 和 customer_data，将它们作为参数传递
                    if "event_type" in event_data and "customer_data" in event_data:
                        # 将这些字段作为位置参数传递，其他字段作为kwargs
                        args = (event_data["event_type"], event_data["customer_data"])
                        # 保留其他字段在kwargs中，但排除已作为args的字段
                        broadcast_kwargs = {k: v for k, v in event_data.items() 
                                          if k not in ["event_type", "customer_data", "_broadcast", "_target_tasks", "_timestamp", "trigger_time", "name", "_task_name"]}
                        kwargs_inner.update(broadcast_kwargs)
                
                # Execute lifecycle methods
                result = task.on_before(
                event_id=event_id,
                pedding_count=self.pedding_count,
                args=args,
                kwargs=kwargs_inner,
                )
                if asyncio.iscoroutine(result):
                    result = await result
                
                if result and result.reject:
                    # 任务被reject，使用Hash更新
                    self.task_info_updates[event_id] = {
                    "status": "rejected",
                        "consumer": consumer,
                        "started_at": str(execution_start_time),
                        "completed_at": str(time.time()),
                        "error_msg": "Task rejected by on_before"
                    }
                    # 使用统一的 pipeline 刷新
                    await self._flush_all_buffers()
                    return
                
                # 标记任务开始执行
                if hasattr(self.app, 'consumer_manager') and self.app.consumer_manager:
                    self.app.consumer_manager.task_started(queue)
                
                # 更新任务真正开始执行的时间（在on_before之后）
                execution_start_time = time.time()
                
                # 使用Hash更新running状态
                # 为了让用户能看到任务正在运行，立即写入running状态
                # running_key = f"{self.prefix}:TASK:{event_id}"
                # 保存开始信息，但不设置status为running，避免竞态条件
                self.task_info_updates[event_id] = {
                    "status": "running",  # 不在这里设置status
                    "consumer": consumer,
                    "started_at": str(execution_start_time)
                }
                # await self.app.ep.async_redis_client.hset(running_key, mapping={
                #     "status": "running",
                #     "consumer": consumer,
                #     "started_at": str(execution_start_time)
                # })
                
                # 在worker内部进行重试循环
                current_retry = 0
                last_exception = None
                
                while current_retry <= max_retries:
                    try:
                        # 如果当前是重试，记录日志
                        if current_retry > 0:
                            logger.info(f"Retry attempt {current_retry}/{max_retries} for task {event_id}")
                        
                        task_result = task(event_id, event_data['trigger_time'], *args, **kwargs_inner)
                        if asyncio.iscoroutine(task_result):
                            ret = await task_result
                        else:
                            ret = task_result
                        result = task.on_success(
                            event_id=event_id,
                            args=args,
                            kwargs=kwargs_inner,
                            result=ret,
                        )
                        if asyncio.iscoroutine(result):
                            await result
                        
                        # 任务成功执行，现在可以ACK消息了
                        await self._quick_ack(queue, event_id, group_name)
                        
                        # 任务成功，跳出重试循环
                        break
                            
                    except SystemExit:
                        # 处理系统退出信号，不重试
                        logger.info('Task interrupted by system exit')
                        status = "interrupted"
                        exception = "System exit"
                        error_msg = "Task interrupted by shutdown"
                        # 系统退出时也需要ACK消息
                        await self._quick_ack(queue, event_id, group_name)
                        break
                        
                    except Exception as e:
                        last_exception = e
                    
                        # 检查是否应该重试
                        should_retry = False
                        if current_retry < max_retries:
                            # 检查异常类型是否可重试
                            retry_on_exceptions = retry_config.get('retry_on_exceptions')
                            
                            if retry_on_exceptions:
                                # retry_on_exceptions 是异常类名字符串列表
                                exc_type_name = type(e).__name__
                                should_retry = exc_type_name in retry_on_exceptions
                            else:
                                # 默认重试所有异常
                                should_retry = True
                        
                        if should_retry:
                            current_retry += 1
                            
                            # 计算重试延迟
                            delay = None
                            
                            # 如果是RetryableError并且指定了retry_after，使用指定的延迟
                            if isinstance(e, RetryableError) and e.retry_after is not None:
                                delay = e.retry_after
                                logger.info(f"Using RetryableError suggested delay: {delay:.1f}s")
                            else:
                                # 使用配置的重试策略
                                retry_backoff = retry_config.get('retry_backoff', True)
                                
                                if retry_backoff:
                                    # 指数退避：1s, 2s, 4s, 8s, ...
                                    base_delay = 1.0
                                    delay = min(base_delay * (2 ** (current_retry - 1)), 
                                              retry_config.get('retry_backoff_max', 60))
                                else:
                                    # 固定延迟：始终1秒
                                    delay = 1.0
                            
                            logger.info(f"Task {event_id} will retry after {delay:.2f} seconds (attempt {current_retry}/{max_retries})")
                            
                            # 在worker内部等待，而不是重新发送到队列
                            await asyncio.sleep(delay)
                            continue  # 继续下一次重试
                        else:
                            # 不再重试，记录错误并退出
                            logger.error(f'任务执行出错: {str(e)}')
                            status = "error"
                            exception = filter_framework_traceback()
                            error_msg = str(e)
                            logger.error(exception)
                            # 任务失败且不重试，需要ACK消息
                            await self._quick_ack(queue, event_id, group_name)
                            break
            
                # 如果所有重试都失败了
                if current_retry > max_retries and last_exception:
                    logger.error(f'任务在 {max_retries} 次重试后仍然失败')
                    status = "error"
                    exception = filter_framework_traceback()
                    error_msg = str(last_exception)
                    # 任务最终失败，也需要ACK消息
                    await self._quick_ack(queue, event_id, group_name)
                    
                # except块已经移到while循环内部，这里不需要了
            finally:
                # 计算完成时间和消耗时间
                completed_at = time.time()
                # 恢复的消息可能没有trigger_time，使用执行开始时间作为默认值
                trigger_time_float = float(event_data.get('trigger_time', execution_start_time))
                # 计算两个时间指标，确保不会出现负数
                execution_time = max(0, completed_at - execution_start_time)  # 实际执行时间
                total_latency = max(0, completed_at - trigger_time_float)     # 总延迟时间（包含等待）
                
                # 异步收集统计信息（高性能模式下非阻塞）
                await self._collect_stats_async(
                    queue=queue,
                    success=(status == "success"),
                    processing_time=execution_time,
                    total_latency=total_latency
                )
                
                # 使用Hash原子更新所有信息
                # 重要：先设置result，再设置status，确保不会出现status=success但result还没写入的情况
                task_info = {
                    "completed_at": str(completed_at),
                    "execution_time": str(execution_time),
                    "duration": str(total_latency),
                    "consumer": consumer,
                    'status': status
                }
                
                # 先写入结果
                if ret is None:
                    task_info["result"] = "null"  # JSON null
                else:
                    task_info["result"] = ret if isinstance(ret, str) else dumps_str(ret)
                
                # 再写入错误信息（如果有）
                if exception:
                    task_info["exception"] = exception
                if error_msg:
                    task_info["error_msg"] = error_msg
                    
                
                # 更新到缓冲区
                if event_id in self.task_info_updates:
                    # 合并更新（保留started_at等之前的信息）
                    # 重要：确保最终状态覆盖之前的running状态
                    self.task_info_updates[event_id].update(task_info)
                else:
                    self.task_info_updates[event_id] = task_info
                
                # 只有在 task 存在时才调用 on_end
                if task:
                    result = task.on_end(
                        event_id=event_id,
                        args=args,
                        kwargs=kwargs_inner,
                        result=ret,
                        pedding_count=self.pedding_count,
                    )
                    if asyncio.iscoroutine(result):
                        await result
                # Handle routing
                if routing:
                    agg_key = routing.get("agg_key")
                    routing_key = routing.get("routing_key")
                    if routing_key and agg_key:
                        # 避免在多进程环境下使用跨进程的锁
                        # 直接操作，依赖 Python GIL 和原子操作
                        if queue in self.app.ep.solo_running_state and routing_key in self.app.ep.solo_running_state[queue]:
                            self.app.ep.solo_running_state[queue][routing_key] -= 1
                    try:
                        if result and result.urgent_retry:
                            self.app.ep.solo_urgent_retry[routing_key] = True
                    except:
                        pass
                    if result and result.delay:
                        self.app.ep.task_scheduler[queue][routing_key] = time.time() + result.delay
                            
                self.batch_counter -= 1
    
    async def loop(self):
        """Optimized main loop with dynamic batching"""
        # semaphore = asyncio.Semaphore(self.concurrency)  # 当前未使用，保留以备后用
        
        
        # Dynamic batch processing
        min_batch_size = 10   # 优化：降低最小批次
        max_batch_size = 500  # 优化：提高最大批次
        batch_size = 100
        tasks_batch = []
        
        # Performance tracking
        # last_periodic_flush = time.time()  # 已被统一 pipeline 管理替代
        last_batch_adjust = time.time()
        # last_buffer_check = time.time()  # 当前未使用
        
        # 高性能缓冲区监控阈值
        max_buffer_size = 5000
        
        try:
            while True:
                # 检查是否需要退出
                if hasattr(self.app, '_should_exit') and self.app._should_exit:
                    logger.info("AsyncioExecutor detected shutdown signal, exiting...")
                    break
                    
                # # 动态调整批处理大小
                current_time = time.time()
                if current_time - last_batch_adjust > 1.0:
                    # 根据队列类型获取长度
                    if isinstance(self.event_queue, deque):
                        queue_len = len(self.event_queue)
                    elif isinstance(self.event_queue, asyncio.Queue):
                        queue_len = self.event_queue.qsize()
                    else:
                        queue_len = 0
                    
                    # 优化：更智能的动态调整
                    if queue_len > 5000:
                        batch_size = min(max_batch_size, batch_size + 50)
                    elif queue_len > 1000:
                        batch_size = min(max_batch_size, batch_size + 20)
                    elif queue_len < 100:
                        batch_size = max(min_batch_size, batch_size - 20)
                    elif queue_len < 500:
                        batch_size = max(min_batch_size, batch_size - 10)
                    last_batch_adjust = current_time
                    
                # 从队列获取事件
                event = None
                try:
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    event = None
                        
                if event:
                    event.pop("execute_time", None)
                    tasks_batch.append(event)
                # 批量创建协程任务
                if tasks_batch:
                    for event in tasks_batch:
                        self.batch_counter += 1
                        asyncio.create_task(self.logic(None, **event))  # semaphore 参数暂时传 None
                    
                    tasks_batch.clear()
                
                # 智能缓冲区管理和刷新
                buffer_full = (
                    len(self.pending_acks) >= max_buffer_size or
                    len(self.status_updates) >= max_buffer_size or 
                    len(self.data_updates) >= max_buffer_size or
                    len(self.task_info_updates) >= max_buffer_size  # 新增：检查Hash缓冲区
                )
                
                # 定期或缓冲区满时刷新 - 使用统一 Pipeline 策略
                should_flush_periodic = False
                has_pending_data = (self.pending_acks or self.status_updates or self.data_updates or self.task_info_updates)
                
                # 检查每种类型的数据是否需要刷新
                if has_pending_data:
                    for data_type, config in self.pipeline_config.items():
                        if data_type == 'ack' and self.pending_acks:
                            if current_time - self.last_pipeline_flush[data_type] >= config['max_delay']:
                                should_flush_periodic = True
                                break
                        elif data_type == 'task_info' and self.task_info_updates:
                            if current_time - self.last_pipeline_flush[data_type] >= config['max_delay']:
                                should_flush_periodic = True
                                break
                        elif data_type == 'status' and self.status_updates:
                            if current_time - self.last_pipeline_flush[data_type] >= config['max_delay']:
                                should_flush_periodic = True
                                break
                        elif data_type == 'data' and self.data_updates:
                            if current_time - self.last_pipeline_flush[data_type] >= config['max_delay']:
                                should_flush_periodic = True
                                break
                        elif data_type == 'stats' and hasattr(self, 'stats_updates') and self.stats_updates:
                            if current_time - self.last_pipeline_flush[data_type] >= config['max_delay']:
                                should_flush_periodic = True
                                break
                
                if buffer_full or should_flush_periodic:
                    asyncio.create_task(self._flush_all_buffers())
                    # 刷新时间已在 _flush_all_buffers 中更新
                
                
                # 智能休眠策略
                has_events = False
                if isinstance(self.event_queue, deque):
                    has_events = bool(self.event_queue)
                elif isinstance(self.event_queue, asyncio.Queue):
                    has_events = not self.event_queue.empty()
                    
                if has_events:
                    await asyncio.sleep(0)  # 有任务时立即切换
                else:
                    # 检查是否需要立即刷新缓冲区
                    if (self.pending_acks or self.status_updates or self.data_updates or self.task_info_updates):
                        await self._flush_all_buffers()
                    await asyncio.sleep(0.001)  # 无任务时短暂休眠
        
        except KeyboardInterrupt:
            logger.info("AsyncioExecutor received KeyboardInterrupt")
        except Exception as e:
            logger.error(f"AsyncioExecutor loop error: {e}")
        finally:
            # 确保清理逻辑总是执行
            logger.info("AsyncioExecutor cleaning up...")
            
            # 1. 刷新所有缓冲区（设置超时避免卡住）
            try:
                await asyncio.wait_for(self._flush_all_buffers(), timeout=2.0)
                logger.info("Buffers flushed successfully")
            except asyncio.TimeoutError:
                logger.warning("Buffer flush timeout, some data may be lost")
            except Exception as e:
                logger.error(f"Error flushing buffers: {e}")
            
            # 2. 标记worker为离线（最重要的清理操作）
            if self.app.consumer_manager:
                try:
                    self.app.consumer_manager.cleanup()
                    logger.info("Worker marked as offline")
                except Exception as e:
                    logger.error(f"Error marking worker offline: {e}")
            
            logger.info("AsyncioExecutor stopped")