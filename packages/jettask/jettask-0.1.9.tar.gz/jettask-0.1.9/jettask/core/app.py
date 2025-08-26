import os
import sys
import time
from datetime import datetime
from ..utils.serializer import dumps, loads, dumps_str, loads_str
import signal
import socket
import asyncio
import logging
import contextlib
import importlib
import multiprocessing
from typing import List
from collections import defaultdict, deque

import redis
from redis import asyncio as aioredis
from watchdog.observers import Observer

from .task import Task
from .event_pool import EventPool
from ..executors import AsyncioExecutor, MultiAsyncioExecutor
from ..monitoring import FileChangeHandler
from ..utils import gen_task_name
from ..exceptions import TaskTimeoutError, TaskExecutionError, TaskNotFoundError

logger = logging.getLogger('app')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 尝试导入性能优化库
try:
    import uvloop
    UVLOOP_AVAILABLE = True
    # 自动启用uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.debug("Using uvloop for better performance")
except ImportError:
    UVLOOP_AVAILABLE = False

_on_app_finalizers = set()

# 全局连接池复用
_redis_pools = {}
_async_redis_pools = {}
# 专门用于二进制数据的连接池（用于Stream操作）
_binary_redis_pools = {}
_async_binary_redis_pools = {}

def get_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建Redis连接池"""
    if redis_url not in _redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _redis_pools[redis_url] = redis.ConnectionPool.from_url(
            redis_url, 
            decode_responses=True,
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _redis_pools[redis_url]

def get_async_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建异步Redis连接池"""
    if redis_url not in _async_redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _async_redis_pools[redis_url] = aioredis.ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _async_redis_pools[redis_url]

def get_binary_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建用于二进制数据的Redis连接池（不解码响应）"""
    if redis_url not in _binary_redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _binary_redis_pools[redis_url] = redis.ConnectionPool.from_url(
            redis_url, 
            decode_responses=False,  # 不解码，保持二进制
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _binary_redis_pools[redis_url]

def get_async_binary_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建用于二进制数据的异步Redis连接池（不解码响应）"""
    if redis_url not in _async_binary_redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _async_binary_redis_pools[redis_url] = aioredis.ConnectionPool.from_url(
            redis_url,
            decode_responses=False,  # 不解码，保持二进制
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _async_binary_redis_pools[redis_url]


def connect_on_app_finalize(callback):
    """Connect callback to be called when any app is finalized."""
    _on_app_finalizers.add(callback)
    return callback


class Jettask(object):
    # Lua脚本定义为类常量，避免重复定义
    _LUA_SCRIPT_DELAYED_TASKS = """
    local prefix = ARGV[1]
    local current_time = tonumber(ARGV[2])
    local results = {}
    
    -- 从ARGV[3]开始，每5个参数为一组任务信息
    -- [stream_key, stream_data, execute_at, delay_seconds, queue]
    for i = 3, #ARGV, 5 do
        local stream_key = ARGV[i]
        local stream_data = ARGV[i+1]
        local execute_at = tonumber(ARGV[i+2])
        local delay_seconds = tonumber(ARGV[i+3])
        local queue = ARGV[i+4]
        
        -- 1. 添加消息到Stream
        local stream_id = redis.call('XADD', stream_key, '*', 'data', stream_data)
        
        -- 2. 添加到延迟队列ZSET
        local delayed_queue_key = prefix .. ':DELAYED_QUEUE:' .. queue
        redis.call('ZADD', delayed_queue_key, execute_at, stream_id)
        
        -- 3. 设置任务状态Hash（只存储status，其他信息从Stream获取）
        local task_key = prefix .. ':TASK:' .. stream_id
        redis.call('HSET', task_key, 'status', 'delayed')
        
        -- 4. 设置过期时间
        local expire_seconds = math.max(1, math.floor(delay_seconds + 3600))
        redis.call('EXPIRE', task_key, expire_seconds)
        
        -- 保存stream_id到结果
        table.insert(results, stream_id)
    end
    
    return results
    """
    
    _LUA_SCRIPT_NORMAL_TASKS = """
    local prefix = ARGV[1]
    local current_time = ARGV[2]
    local results = {}
    
    -- 从ARGV[3]开始，每2个参数为一组任务信息
    -- [stream_key, stream_data]
    for i = 3, #ARGV, 2 do
        local stream_key = ARGV[i]
        local stream_data = ARGV[i+1]
        
        -- 1. 添加消息到Stream
        local stream_id = redis.call('XADD', stream_key, '*', 'data', stream_data)
        
        -- 2. 设置任务状态Hash（只存储status）
        local task_key = prefix .. ':TASK:' .. stream_id
        redis.call('HSET', task_key, 'status', 'pending')
        
        -- 3. 设置过期时间（1小时）
        redis.call('EXPIRE', task_key, 3600)
        
        -- 保存stream_id到结果
        table.insert(results, stream_id)
    end
    
    return results
    """

    def __init__(self, redis_url: str = None, include: list = None, max_connections: int = 200, 
                 consumer_strategy: str = None, consumer_config: dict = None, tasks=None,
                 redis_prefix: str = None, scheduler_config: dict = None, pg_url: str = None) -> None:
        self._tasks = tasks or {}
        self.asyncio = False
        self.include = include or []
        self.redis_url = redis_url
        self.pg_url = pg_url  # 存储PostgreSQL URL
        self.max_connections = max_connections
        self.consumer_strategy = consumer_strategy
        self.consumer_config = consumer_config or {}
        self.scheduler_config = scheduler_config or {}
        
        # Redis prefix configuration
        self.redis_prefix = redis_prefix or "jettask"
        
        # Update prefixes with the configured prefix using colon namespace
        self.STATUS_PREFIX = f"{self.redis_prefix}:STATUS:"
        self.RESULT_PREFIX = f"{self.redis_prefix}:RESULT:"
        
        # 预编译常用操作，减少运行时开销
        self._loads = loads
        self._dumps = dumps
        
        # 调度器相关
        self.scheduler = None
        self.scheduler_manager = None
        
        self._status_prefix = self.STATUS_PREFIX
        self._result_prefix = self.RESULT_PREFIX
        
        # 初始化清理状态，但不注册处理器
        self._cleanup_done = False
        self._should_exit = False
        self._worker_started = False
        self._handlers_registered = False
    
    def _setup_cleanup_handlers(self):
        """设置清理处理器"""
        # 避免重复注册
        if self._handlers_registered:
            return
        
        self._handlers_registered = True
        
        def signal_cleanup_handler(signum=None, frame=None):
            """信号处理器"""
            if self._cleanup_done:
                return
            # 只有启动过worker才需要打印清理信息
            if self._worker_started:
                logger.info("Received shutdown signal, cleaning up...")
            self.cleanup()
            if signum:
                # 设置标记表示需要退出
                self._should_exit = True
                # 对于多进程环境，不直接操作事件循环
                # 让执行器自己检测退出标志并优雅关闭
        
        def atexit_cleanup_handler():
            """atexit处理器"""
            if self._cleanup_done:
                return
            # atexit时不重复打印日志，静默清理
            self.cleanup()
        
        # 注册信号处理器
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_cleanup_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_cleanup_handler)
        
        # 注册atexit处理器
        import atexit
        atexit.register(atexit_cleanup_handler)
    
    def cleanup(self):
        """清理应用资源"""
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        # 只有真正启动过worker才打印日志
        if self._worker_started:
            logger.info("Cleaning up Jettask resources...")
            
            # 清理EventPool
            if hasattr(self, 'ep') and self.ep:
                self.ep.cleanup()
            
            logger.info("Jettask cleanup completed")
        else:
            # 如果只是实例化但没有启动，静默清理
            if hasattr(self, 'ep') and self.ep:
                self.ep.cleanup()
            logger.debug("Jettask instance cleanup (no worker started)")
    
    @property
    def consumer_manager(self):
        """获取消费者管理器"""
        return self.ep.consumer_manager if hasattr(self.ep, 'consumer_manager') else None

    @property
    def async_redis(self):
        """优化：复用连接池"""
        name = "_async_redis"
        if hasattr(self, name):
            return getattr(self, name)
        
        pool = get_async_redis_pool(self.redis_url, self.max_connections)
        async_redis = aioredis.StrictRedis(connection_pool=pool)
        setattr(self, name, async_redis)
        return async_redis

    @property
    def redis(self):
        """优化：复用连接池"""
        name = "_redis"
        if hasattr(self, name):
            return getattr(self, name)
            
        pool = get_redis_pool(self.redis_url, self.max_connections)
        redis_cli = redis.StrictRedis(connection_pool=pool)
        setattr(self, name, redis_cli)
        return redis_cli

    @property
    def ep(self):
        name = "_ep"
        if hasattr(self, name):
            ep = getattr(self, name)
        else:
            # 传递redis_prefix到consumer_config
            consumer_config = self.consumer_config.copy() if self.consumer_config else {}
            consumer_config['redis_prefix'] = self.redis_prefix
            
            ep = EventPool(
                self.redis, 
                self.async_redis, 
                redis_url=self.redis_url,
                consumer_strategy=self.consumer_strategy,
                consumer_config=consumer_config,
                redis_prefix=self.redis_prefix,
                app=self
            )
            setattr(self, name, ep)
        return ep

    def clear(self):
        if hasattr(self, "process"):
            delattr(self, "process")
        if hasattr(self, "_ep"):
            delattr(self, "_ep")

    def get_task_by_name(self, name: str) -> Task:
        # 1. 直接查找完整名称
        task = self._tasks.get(name)
        if task:
            return task
        
        # 2. 如果是简单名称（不含.），尝试匹配所有以该名称结尾的任务
        if '.' not in name:
            for task_key, task_obj in self._tasks.items():
                # 匹配 "module.function_name" 形式，提取函数名部分
                if '.' in task_key:
                    _, func_name = task_key.rsplit('.', 1)
                    if func_name == name:
                        return task_obj
                elif task_key == name:
                    # 完全匹配（可能没有模块前缀）
                    return task_obj
        
        return None

    def include_module(self, modules: list):
        self.include += modules

    def _task_from_fun(
        self, fun, name=None, base=None, queue=None, bind=False, retry_config=None, **options
    ) -> Task:
        name = name or gen_task_name(fun.__name__, fun.__module__)
        base = base or Task
        if name not in self._tasks:
            run = staticmethod(fun)
            task: Task = type(
                fun.__name__,
                (base,),
                dict(
                    {
                        "app": self,
                        "name": name,
                        "run": run,
                        "queue": queue,
                        "retry_config": retry_config,  # 存储重试配置
                        "_decorated": True,
                        "__doc__": fun.__doc__,
                        "__module__": fun.__module__,
                        "__annotations__": fun.__annotations__,
                        "__wrapped__": run,
                    },
                    **options,
                ),
            )()
            task.bind_app(self)
            with contextlib.suppress(AttributeError):
                task.__qualname__ = fun.__qualname__
            self._tasks[task.name] = task
        else:
            task = self._tasks[name]
        return task
    
    def task(
        self,
        name: str = None,
        queue: str = None,
        base: Task = None,
        # 重试相关参数
        max_retries: int = 0,
        retry_backoff: bool = True,  # 是否使用指数退避
        retry_backoff_max: float = 60,  # 最大退避时间（秒）
        retry_on_exceptions: tuple = None,  # 可重试的异常类型
        *args,
        **kwargs,
    ):
        def _create_task_cls(fun):
            # 将重试配置传递给_task_from_fun
            retry_config = None
            if max_retries > 0:
                retry_config = {
                    'max_retries': max_retries,
                    'retry_backoff': retry_backoff,
                    'retry_backoff_max': retry_backoff_max,
                }
                # 将异常类转换为类名字符串，以便序列化
                if retry_on_exceptions:
                    retry_config['retry_on_exceptions'] = [
                        exc if isinstance(exc, str) else exc.__name__ 
                        for exc in retry_on_exceptions
                    ]
            return self._task_from_fun(fun, name, base, queue, retry_config=retry_config, *args, **kwargs)

        return _create_task_cls
    
    def publish_broadcast(
        self,
        queue: str,
        message: dict,
        target_tasks: list = None,
        asyncio_mode: bool = False
    ):
        """
        发布广播消息到队列
        
        Args:
            queue: 目标队列名
            message: 消息内容
            target_tasks: 目标任务列表（None表示所有监听该队列的任务）
            asyncio_mode: 是否使用异步模式
        
        Returns:
            消息ID或协程对象
        
        使用示例：
            # 同步模式
            app.publish_broadcast(
                queue="events",
                message={"type": "customer_registered", "data": {...}}
            )
            
            # 异步模式
            await app.publish_broadcast(
                queue="events",
                message={"type": "order_created", "data": {...}},
                target_tasks=["send_email", "update_inventory"],
                asyncio_mode=True
            )
        """
        # 构建广播消息，直接序列化整个消息
        from ..utils.serializer import dumps_str
        
        # 创建完整的广播消息
        broadcast_message = {
            **message,  # 用户的原始消息
            "_broadcast": True,
            "_target_tasks": target_tasks,
            "_timestamp": time.time(),
            "trigger_time": time.time()
        }
        # 使用EventPool的send_event方法，保持和apply_async一致的格式
        if asyncio_mode:
            return self.ep.send_event(queue, broadcast_message, asyncio=True)
        else:
            return self.ep.send_event(queue, broadcast_message, asyncio=False)
    
    def register_router(self, router, prefix: str = None):
        """
        注册任务路由器
        
        Args:
            router: TaskRouter实例
            prefix: 额外的前缀（可选）
        
        使用示例：
            from jettask import Jettask, TaskRouter
            
            # 创建路由器
            email_router = TaskRouter(prefix="email", queue="emails")
            
            @email_router.task()
            async def send_email(to: str):
                pass
            
            # 注册到主应用
            app = Jettask(redis_url="redis://localhost:6379/0")
            app.register_router(email_router)
        """
        from ..router import TaskRouter
        
        if not isinstance(router, TaskRouter):
            raise TypeError("router must be a TaskRouter instance")
        
        # 注册所有任务
        for task_name, task_config in router.get_tasks().items():
            # 如果指定了额外前缀，添加到任务名
            if prefix:
                if task_config.get('name'):
                    task_config['name'] = f"{prefix}.{task_config['name']}"
                task_name = f"{prefix}.{task_name}"
            
            # 获取任务函数
            func = task_config.pop('func')
            name = task_config.pop('name', task_name)
            queue = task_config.pop('queue', None)
            
            # 注册任务
            task = self._task_from_fun(func, name, None, queue, **task_config)
            logger.info(f"Registered task: {name} (queue: {queue or self.redis_prefix})")
        
        return self

    def _mount_module(self):
        for module in self.include:
            module = importlib.import_module(module)
            for attr_name in dir(module):
                obj = getattr(module, attr_name)
                if hasattr(obj, "app"):
                    self._tasks.update(getattr(obj, "app")._tasks)

    def _validate_tasks_for_executor(self, execute_type: str, queues: List[str]):
        """验证任务类型是否与执行器兼容"""
        if execute_type in ["asyncio", "multi_asyncio"]:
            return  # AsyncIO和MultiAsyncio可以处理异步任务
        
        # 只有Thread执行器不能处理异步任务
        incompatible_tasks = []
        for task_name, task in self._tasks.items():
            # 检查任务是否属于指定队列
            if task.queue not in queues:
                continue
                
            # 检查是否是异步任务
            if asyncio.iscoroutinefunction(task.run):
                incompatible_tasks.append({
                    'name': task_name,
                    'queue': task.queue,
                    'type': 'async'
                })
        
        if incompatible_tasks:
            error_msg = f"\n错误：{execute_type} 执行器不能处理异步任务！\n"
            error_msg += "发现以下异步任务：\n"
            for task in incompatible_tasks:
                error_msg += f"  - {task['name']} (队列: {task['queue']})\n"
            error_msg += f"\n解决方案：\n"
            error_msg += f"1. 使用 asyncio 或 process 执行器\n"
            error_msg += f"2. 或者将这些任务改为同步函数（去掉 async/await）\n"
            error_msg += f"3. 或者将这些任务的队列从监听列表中移除\n"
            raise ValueError(error_msg)
    
    def _start(
        self,
        execute_type: str = "asyncio",
        queues: List[str] = None,
        concurrency: int = 1,
        prefetch_multiplier: int = 1,
        **kwargs
    ):
        # 设置默认队列
        if not queues:
            queues = [self.redis_prefix]
        
        self.ep.queues = queues
        self.ep.init_routing()
        self._mount_module()
        # 验证任务兼容性 
        self._validate_tasks_for_executor(execute_type, queues)
        
        # 收集每个队列上的所有任务（用于广播支持）
        self._tasks_by_queue = {}
        for task_name, task in self._tasks.items():
            task_queue = task.queue or self.redis_prefix
            if task_queue in queues:
                if task_queue not in self._tasks_by_queue:
                    self._tasks_by_queue[task_queue] = []
                self._tasks_by_queue[task_queue].append(task_name)
                logger.debug(f"Task {task_name} listening on queue {task_queue}")
        
        event_queue = deque()
        
        # 创建消费者组
        try:
            self.ep.create_group()
        except Exception as e:
            logger.warning(f"创建消费者组时出错: {e}")
            # 继续执行，listening_event会自动处理
        
        # 根据执行器类型创建对应的执行器
        if execute_type == "asyncio":
            # 对于asyncio执行器，使用asyncio.Queue
            async_event_queue = asyncio.Queue()
            
            async def run_asyncio_executor():
                # 启动异步事件监听
                asyncio.create_task(self.ep.listening_event(async_event_queue, prefetch_multiplier))
                # 创建并运行执行器
                executor = AsyncioExecutor(async_event_queue, self, concurrency)
                await executor.loop()
            
            # try:
            loop = asyncio.get_event_loop()
            # except RuntimeError:
            #     # 如果当前线程没有事件循环，创建一个新的
            #     loop = asyncio.new_event_loop()
            #     asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(run_asyncio_executor())
            except RuntimeError as e:
                if "Event loop stopped" in str(e):
                    logger.info("Event loop stopped, shutting down gracefully")
                else:
                    raise
        elif execute_type == "multi_asyncio":
            # multi_asyncio在每个子进程中会启动自己的监听器
            executor = MultiAsyncioExecutor(event_queue, self, concurrency)
            executor.prefetch_multiplier = prefetch_multiplier
            
            # 设置信号处理器以正确响应Ctrl+C
            def multi_asyncio_signal_handler(signum, _frame):
                logger.info(f"Multi-asyncio mode received signal {signum}")
                executor._main_received_signal = True
                executor.shutdown_event.set()
                # 强制退出主循环
                raise KeyboardInterrupt()
            
            signal.signal(signal.SIGINT, multi_asyncio_signal_handler)
            signal.signal(signal.SIGTERM, multi_asyncio_signal_handler)
            
            try:
                executor.loop()
            except KeyboardInterrupt:
                logger.info("Multi-asyncio mode interrupted")
            finally:
                executor.shutdown()
        else:
            raise ValueError(f"不支持的执行器类型：{execute_type}，仅支持 'asyncio' 和 'multi_asyncio'")

    def _run_subprocess(self, *args, **kwargs):
        # logger.info("Started Worker Process")
        process = multiprocessing.Process(target=self._start, args=args, kwargs=kwargs)
        process.start()
        return process

    def start(
        self,
        execute_type: str = "asyncio",
        queues: List[str] = None,
        concurrency: int = 1,
        prefetch_multiplier: int = 1,
        reload: bool = False,
    ):
        # 标记worker已启动
        self._worker_started = True
        
        # 注册清理处理器（只在启动worker时注册）
        self._setup_cleanup_handlers()
        
        if execute_type == "multi_asyncio" and self.consumer_strategy == "pod":
            raise ValueError("multi_asyncio模式下无法使用pod策略")
        self.process = self._run_subprocess(
            execute_type=execute_type,
            queues=queues,
            concurrency=concurrency,
            prefetch_multiplier=prefetch_multiplier,
        )
        if reload:
            event_handler = FileChangeHandler(
                self,
                execute_type=execute_type,
                queues=queues,
                concurrency=concurrency,
                prefetch_multiplier=prefetch_multiplier,
            )
            observer = Observer()
            observer.schedule(event_handler, ".", recursive=True)
            observer.start()
        # 使用事件来等待，而不是无限循环
        try:
            while not self._should_exit:
                time.sleep(0.1)  # 短暂睡眠，快速响应退出信号
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.cleanup()
            if self.process and self.process.is_alive():
                self.process.terminate()
                self.process.join(timeout=2)
                if self.process.is_alive():
                    logger.warning("Process did not terminate, killing...")
                    self.process.kill()

    def bulk_write(self, tasks: list, asyncio: bool = None):
        """
        统一的批量写入方法，支持同步和异步模式，以及延迟任务
        
        Args:
            tasks: 任务列表
            asyncio: 是否使用异步模式。如果为None，自动检测
        
        Returns:
            同步模式: 返回event_ids列表
            异步模式: 如果在异步环境中调用，返回协程对象
        """
        if not tasks:
            raise ValueError("tasks 参数不能为空！")
        
        # 自动检测异步模式
        if asyncio is None:
            import asyncio as aio
            try:
                loop = aio.get_running_loop()
                asyncio = True
            except RuntimeError:
                asyncio = False
        
        # 如果需要异步执行
        if asyncio:
            return self._bulk_write_async(tasks)
        
        # 同步执行
        import asyncio as aio
        # 在同步模式下，使用 asyncio.run 来运行异步函数
        return aio.run(self._bulk_write_impl(tasks, asyncio_mode=False))
    
    async def _bulk_write_impl(self, tasks: list, asyncio_mode: bool):
        """批量写入的内部实现，支持同步和异步"""
        # 获取对应的Redis客户端
        redis_client = self.get_redis_client(asyncio=asyncio_mode)
        
        # 分离延迟任务和普通任务
        delayed_tasks = []
        normal_tasks = []
        
        for task in tasks:
            if 'delay' in task:
                delayed_tasks.append(task)
            else:
                normal_tasks.append(task)
        
        event_ids = []
        
        # 处理延迟任务 - 使用Lua脚本原子性处理
        if delayed_tasks:
            
            # 准备Lua脚本参数
            current_time = time.time()
            lua_args = [self.redis_prefix, str(current_time)]
            
            for task in delayed_tasks:
                delay_seconds = task.pop('delay')  # 移除delay参数
                queue = task.get("queue")
                
                # 添加执行时间到消息中
                execute_at = current_time + delay_seconds
                task['execute_at'] = execute_at
                task['is_delayed'] = 1  # 使用1代替True
                task['trigger_time'] = current_time  # 添加trigger_time
                
                # 如果queue为None，使用任务名作为队列名
                task_name = task.get("name", "")
                actual_queue = queue or task_name
                task['queue'] = actual_queue
                
                # 准备Stream数据
                prefixed_queue = self.ep.get_prefixed_queue_name(actual_queue)
                from ..utils.serializer import dumps_str
                stream_data = dumps_str(task)
                
                # 添加到Lua脚本参数
                lua_args.extend([
                    prefixed_queue,
                    stream_data,
                    str(execute_at),
                    str(delay_seconds),
                    actual_queue
                ])
            
            # 注册并执行Lua脚本（使用类常量）
            script_attr = '_bulk_delayed_script_async' if asyncio_mode else '_bulk_delayed_script_sync'
            if not hasattr(self, script_attr):
                setattr(self, script_attr, redis_client.register_script(self._LUA_SCRIPT_DELAYED_TASKS))
            
            script = getattr(self, script_attr)
            if asyncio_mode:
                # 异步执行需要await
                stream_ids = await script(keys=[], args=lua_args)
            else:
                stream_ids = script(keys=[], args=lua_args)
            
            event_ids.extend(stream_ids)
        
        # 处理普通任务 - 使用Lua脚本原子性处理
        if normal_tasks:
            
            # 准备Lua脚本参数
            current_time = str(time.time())
            lua_args = [self.redis_prefix, current_time]
            
            # 按队列分组并准备参数
            from ..utils.serializer import dumps_str
            for task in normal_tasks:
                queue = task.get("queue")
                task_name = task.get("name", "")
                actual_queue = queue or task_name
                
                # 准备Stream数据
                prefixed_queue = self.ep.get_prefixed_queue_name(actual_queue)
                stream_data = dumps_str(task)
                
                # 添加到Lua脚本参数
                lua_args.extend([prefixed_queue, stream_data])
            
            # 注册并执行Lua脚本（使用类常量）
            script_attr = '_bulk_normal_script_async' if asyncio_mode else '_bulk_normal_script_sync'
            if not hasattr(self, script_attr):
                setattr(self, script_attr, redis_client.register_script(self._LUA_SCRIPT_NORMAL_TASKS))
            
            script = getattr(self, script_attr)
            if asyncio_mode:
                # 异步执行需要await
                stream_ids = await script(keys=[], args=lua_args)
            else:
                stream_ids = script(keys=[], args=lua_args)
            
            event_ids.extend(stream_ids)
            
        return event_ids

    
    async def _bulk_write_async(self, tasks: list):
        """异步批量写入，直接调用统一的实现"""
        return await self._bulk_write_impl(tasks, asyncio_mode=True)

    def get_task_info(self, event_id: str, asyncio: bool = False):
        """获取任务信息（从TASK:hash）"""
        client = self.get_redis_client(asyncio)
        key = f"{self.redis_prefix}:TASK:{event_id}"
        if asyncio:
            return client.hgetall(key)
        else:
            return client.hgetall(key)
    
    def get_task_status(self, event_id: str, asyncio: bool = False):
        """获取任务状态（从TASK:hash的status字段）"""
        if asyncio:
            return self._get_task_status_async(event_id)
        else:
            client = self.redis
            key = f"{self.redis_prefix}:TASK:{event_id}"
            return client.hget(key, "status")

    async def _get_task_status_async(self, event_id: str):
        """异步获取任务状态"""
        key = f"{self.redis_prefix}:TASK:{event_id}"
        return await self.async_redis.hget(key, "status")

    def set_task_status(self, event_id: str, status: str, asyncio: bool = False):
        """设置任务状态（写入TASK:hash的status字段）"""
        if asyncio:
            return self._set_task_status_async(event_id, status)
        else:
            client = self.redis
            key = f"{self.redis_prefix}:TASK:{event_id}"
            return client.hset(key, "status", status)
    
    async def _set_task_status_async(self, event_id: str, status: str):
        """异步设置任务状态"""
        key = f"{self.redis_prefix}:TASK:{event_id}"
        return await self.async_redis.hset(key, "status", status)

    def set_task_status_by_batch(self, mapping: dict, asyncio: bool = False):
        """批量设置任务状态（写入TASK:hash）"""
        if asyncio:
            return self._set_task_status_by_batch_async(mapping)
        else:
            pipeline = self.redis.pipeline()
            for event_id, status in mapping.items():
                key = f"{self.redis_prefix}:TASK:{event_id}"
                pipeline.hset(key, "status", status)
            return pipeline.execute()
    
    async def _set_task_status_by_batch_async(self, mapping: dict):
        """异步批量设置任务状态"""
        pipeline = self.async_redis.pipeline()
        for event_id, status in mapping.items():
            key = f"{self.redis_prefix}:TASK:{event_id}"
            pipeline.hset(key, "status", status)
        return await pipeline.execute()

    def del_task_status(self, event_id: str, asyncio: bool = False):
        """删除任务状态（删除整个TASK:hash）"""
        client = self.get_redis_client(asyncio)
        key = f"{self.redis_prefix}:TASK:{event_id}"
        return client.delete(key)

    def get_redis_client(self, asyncio: bool = False):
        return self.async_redis if asyncio else self.redis

    def set_data(
        self, event_id: str, result: str, ex: int = 3600, asyncio: bool = False
    ):
        """设置任务结果（写入TASK:hash的result字段）"""
        client = self.get_redis_client(asyncio)
        key = f"{self.redis_prefix}:TASK:{event_id}"
        if asyncio:
            return self._set_data_async(key, result, ex)
        else:
            client.hset(key, "result", result)
            return client.expire(key, ex)
    
    async def _set_data_async(self, key: str, result: str, ex: int):
        """异步设置任务结果"""
        await self.async_redis.hset(key, "result", result)
        return await self.async_redis.expire(key, ex)
    
    async def get_and_delayed_deletion(self, key: str, ex: int):
        """获取结果并延迟删除（从hash中）"""
        result = await self.async_redis.hget(key, "result")
        await self.async_redis.expire(key, ex)
        return result
    
    async def _get_result_async(self, key: str, delete: bool, delayed_deletion_ex: int):
        """异步获取任务结果"""
        client = self.async_redis
        if delayed_deletion_ex is not None:
            result = await client.hget(key, "result")
            await client.expire(key, delayed_deletion_ex)
            return result
        elif delete:
            # 获取结果并删除整个hash
            result = await client.hget(key, "result")
            await client.delete(key)
            return result
        else:
            return await client.hget(key, "result")
    
    def get_result(self, event_id: str, delete: bool = False, asyncio: bool = False, 
                   delayed_deletion_ex: int = None, wait: bool = False, timeout: int = 300,
                   poll_interval: float = 0.5, suppress_traceback: bool = False):
        """获取任务结果（从TASK:hash的result字段）
        
        Args:
            event_id: 任务ID
            delete: 是否删除结果
            asyncio: 是否使用异步模式
            delayed_deletion_ex: 延迟删除时间（秒）
            wait: 是否阻塞等待直到任务完成
            timeout: 等待超时时间（秒），默认300秒
            poll_interval: 轮询间隔（秒），默认0.5秒
            suppress_traceback: 是否抑制框架层堆栈（直接打印错误并退出）
        
        Returns:
            任务结果字符串
            
        Raises:
            TaskTimeoutError: 等待超时
            TaskExecutionError: 任务执行失败
            TaskNotFoundError: 任务不存在
        """
        if asyncio:
            key = f"{self.redis_prefix}:TASK:{event_id}"
            if wait:
                return self._get_result_async_wait(event_id, key, delete, delayed_deletion_ex, timeout, poll_interval)
            else:
                return self._get_result_async(key, delete, delayed_deletion_ex)
        else:
            # 同步模式
            if wait:
                return self._get_result_sync_wait(event_id, delete, delayed_deletion_ex, timeout, poll_interval)
            else:
                client = self.redis
                key = f"{self.redis_prefix}:TASK:{event_id}"
                if delayed_deletion_ex is not None:
                    result = client.hget(key, "result")
                    client.expire(key, delayed_deletion_ex)
                    return result
                elif delete:
                    # 获取结果并删除整个hash
                    result = client.hget(key, "result")
                    client.delete(key)
                    return result
                else:
                    return client.hget(key, "result")
    
    def _get_result_sync_wait(self, event_id: str, delete: bool, delayed_deletion_ex: int, 
                              timeout: int, poll_interval: float):
        """同步模式下阻塞等待任务结果"""
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise TaskTimeoutError(f"Task {event_id} timed out after {timeout} seconds")
            
            # 获取任务状态
            status = self.get_task_status(event_id)
            
            if status is None:
                raise TaskNotFoundError(f"Task {event_id} not found")
            
            if status == 'success':
                # 任务成功，获取结果
                key = f"{self.redis_prefix}:TASK:{event_id}"
                if delayed_deletion_ex is not None:
                    result = self.redis.hget(key, "result")
                    self.redis.expire(key, delayed_deletion_ex)
                    return result
                elif delete:
                    result = self.redis.hget(key, "result")
                    self.redis.delete(key)
                    return result
                else:
                    return self.redis.hget(key, "result")
            
            elif status == 'error':
                # 任务失败，获取错误信息并抛出异常
                key = f"{self.redis_prefix}:TASK:{event_id}"
                # 从 exception 字段获取错误信息
                error_msg = self.redis.hget(key, "exception") or "Task execution failed"
                # 抛出自定义异常
                raise TaskExecutionError(event_id, error_msg)
            
            # 任务还在执行中，继续等待
            time.sleep(poll_interval)
    
    async def _get_result_async_wait(self, event_id: str, key: str, delete: bool, 
                                     delayed_deletion_ex: int, timeout: int, poll_interval: float):
        """异步模式下等待任务结果"""
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise TaskTimeoutError(f"Task {event_id} timed out after {timeout} seconds")
            
            # 获取任务状态
            status = await self._get_task_status_async(event_id)
            
            if status is None:
                raise TaskNotFoundError(f"Task {event_id} not found")
            
            if status == 'success':
                # 任务成功，获取结果
                if delayed_deletion_ex is not None:
                    result = await self.async_redis.hget(key, "result")
                    await self.async_redis.expire(key, delayed_deletion_ex)
                    return result
                elif delete:
                    result = await self.async_redis.hget(key, "result")
                    await self.async_redis.delete(key)
                    return result
                else:
                    return await self.async_redis.hget(key, "result")
            
            elif status == 'error':
                # 任务失败，获取错误信息并抛出异常
                # 从 exception 字段获取错误信息
                error_msg = await self.async_redis.hget(key, "exception") or "Task execution failed"
                # 抛出自定义异常
                raise TaskExecutionError(event_id, error_msg)
            
            # 任务还在执行中，继续等待
            await asyncio.sleep(poll_interval)
    
    # ==================== 定时任务调度相关 ====================
    
    async def _ensure_scheduler_initialized(self, db_url: str = None):
        """确保调度器已初始化（内部方法）"""
        if not self.scheduler_manager:
            logger.info("Auto-initializing scheduler...")
            # 优先使用传入的db_url，然后是实例化时的pg_url，最后是环境变量
            if not db_url:
                db_url = self.pg_url or os.environ.get('JETTASK_PG_URL')
            if not db_url:
                raise ValueError(
                    "Database URL not provided. Please provide pg_url when initializing Jettask, "
                    "or set JETTASK_PG_URL environment variable\n"
                    "Example: app = Jettask(redis_url='...', pg_url='postgresql://...')\n"
                    "Or: export JETTASK_PG_URL='postgresql://user:password@localhost:5432/jettask'"
                )
            
            from ..scheduler import TaskScheduler, ScheduledTaskManager
            
            # 创建数据库管理器
            self.scheduler_manager = ScheduledTaskManager(db_url)
            await self.scheduler_manager.connect()
            await self.scheduler_manager.init_schema()
            
            # 创建调度器
            scheduler_config = self.scheduler_config.copy()
            scheduler_config.setdefault('redis_prefix', f"{self.redis_prefix}:SCHEDULER")
            scheduler_config.setdefault('scan_interval', 0.1)
            scheduler_config.setdefault('batch_size', 100)
            scheduler_config.setdefault('leader_ttl', 10)
            
            self.scheduler = TaskScheduler(
                app=self,
                redis_url=self.redis_url,
                db_manager=self.scheduler_manager,
                **scheduler_config
            )
            
            await self.scheduler.connect()
            logger.info("Scheduler initialized")
    
    async def start_scheduler(self):
        """启动定时任务调度器（自动初始化）"""
        # 自动初始化调度器
        await self._ensure_scheduler_initialized()
        
        try:
            await self.scheduler.run()
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            raise
    
    def stop_scheduler(self):
        """停止定时任务调度器"""
        if self.scheduler:
            self.scheduler.stop()
            logger.info("Scheduler stopped")
    
    async def add_scheduled_task(
        self,
        task_name: str,
        scheduler_id: str,  # 必填参数
        queue_name: str = None,
        task_type: str = "interval",
        interval_seconds: float = None,
        cron_expression: str = None,
        task_args: list = None,
        task_kwargs: dict = None,
        next_run_time: datetime = None,
        skip_if_exists: bool = True,
        at_once: bool = True,  # 是否立即保存到数据库
        **extra_params
    ):
        """
        添加定时任务
        
        Args:
            task_name: 要执行的函数名（必须对应已经通过@app.task注册的任务）
            scheduler_id: 任务的唯一标识符（必填，用于去重）
            queue_name: 目标队列名（可选，从task_name对应的任务自动获取）
            task_type: 任务类型 ('once', 'interval', 'cron')
            interval_seconds: 间隔秒数 (task_type='interval'时使用)
            cron_expression: Cron表达式 (task_type='cron'时使用)
            task_args: 任务参数列表
            task_kwargs: 任务关键字参数
            next_run_time: 首次执行时间 (task_type='once'时使用)
            skip_if_exists: 如果任务已存在是否跳过（默认True）
            at_once: 是否立即保存到数据库（默认True），如果False则返回任务对象用于批量写入
            **extra_params: 其他参数 (如 max_retries, timeout, description 等)
        """
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        from ..scheduler.models import ScheduledTask, TaskType
        
        # 尝试从已注册的任务中获取信息
        registered_task = None
        
        # 1. 直接匹配
        registered_task = self._tasks.get(task_name)
        
        # 2. 如果没找到，尝试查找以task_name结尾的任务（如 "module.task_name"）
        if not registered_task:
            for task_key, task_obj in self._tasks.items():
                if task_key.endswith(f".{task_name}") or task_key == task_name:
                    registered_task = task_obj
                    break
        
        if not registered_task:
            # 任务必须已注册
            available_tasks = list(self._tasks.keys())
            error_msg = f"Task '{task_name}' not found in registered tasks.\n"
            error_msg += "All scheduled tasks must be registered with @app.task decorator.\n"
            if available_tasks:
                error_msg += f"Available tasks: {', '.join(available_tasks)}"
            raise ValueError(error_msg)
        
        # 自动填充信息
        if not queue_name:
            queue_name = registered_task.queue or self.redis_prefix
        
        # 使用注册时的完整任务名称（包含模块前缀）
        # 查找任务的完整注册名称
        full_task_name = None
        for task_key, task_obj in self._tasks.items():
            if task_obj == registered_task:
                full_task_name = task_key
                break
        
        if not full_task_name:
            # 如果没找到，使用用户提供的名称
            full_task_name = task_name
        
        # 处理 next_run_time（主要用于 once 类型）
        if task_type == "once" and extra_params.get("next_run_time"):
            # 如果在 extra_params 中，移到正确位置
            next_run_time = extra_params.pop("next_run_time", None)
        
        # 移除不属于ScheduledTask的参数
        extra_params.pop("skip_if_exists", None)
        
        # scheduler_id是必填参数，必须由用户提供
        if not scheduler_id:
            raise ValueError("scheduler_id is required and must be provided")
        
        # 创建任务对象
        task = ScheduledTask(
            scheduler_id=scheduler_id,
            task_name=full_task_name,  # 使用完整的任务名称（包含模块前缀）
            task_type=TaskType(task_type),
            queue_name=queue_name,
            task_args=task_args or [],
            task_kwargs=task_kwargs or {},
            interval_seconds=interval_seconds,
            cron_expression=cron_expression,
            next_run_time=next_run_time,
            **extra_params
        )
        
        # 如果不立即保存，返回任务对象供批量写入
        if not at_once:
            # 设置skip_if_exists标记供批量写入时使用
            task._skip_if_exists = skip_if_exists
            return task
        
        # 保存到数据库（支持去重）
        task, created = await self.scheduler_manager.create_or_get_task(task, skip_if_exists=skip_if_exists)
        
        if created:
            logger.info(f"Scheduled task {task.id} created for function {task_name}")
        else:
            logger.info(f"Scheduled task {task.id} already exists for function {task_name}")
        
        return task
    
    async def remove_scheduled_task(self, scheduler_id: str):
        """移除定时任务"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        # 先获取任务
        task = await self.scheduler_manager.get_task_by_scheduler_id(scheduler_id)
        if not task:
            return False
        
        success = await self.scheduler_manager.delete_task(task.id)
        
        if success and self.scheduler:
            # 从Redis中也移除
            await self.scheduler.loader.remove_task(task.id)
        
        return success
    
    async def batch_add_scheduled_tasks(
        self,
        tasks: list,
        skip_existing: bool = True
    ):
        """
        批量添加定时任务
        
        Args:
            tasks: 任务配置列表，每个元素是一个字典，包含add_scheduled_task的参数
            skip_existing: 是否跳过已存在的任务
            
        Returns:
            成功创建的任务列表
        """
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        from ..scheduler.models import ScheduledTask, TaskType
        
        task_objects = []
        for task_config in tasks:
            # 获取任务名称
            task_name = task_config.get('task_name')
            if not task_name:
                logger.warning("Task config missing task_name, skipping")
                continue
            
            # 查找注册的任务
            registered_task = self._tasks.get(task_name)
            if not registered_task:
                for task_key, task_obj in self._tasks.items():
                    if task_key.endswith(f".{task_name}") or task_key == task_name:
                        registered_task = task_obj
                        task_name = task_key  # 使用完整名称
                        break
            
            if not registered_task:
                logger.warning(f"Task '{task_name}' not found in registered tasks, skipping")
                continue
            
            # 准备任务参数
            queue_name = task_config.get('queue_name') or registered_task.queue or self.redis_prefix
            task_type = task_config.get('task_type', 'interval')
            
            # 处理next_run_time
            next_run_time = task_config.get('next_run_time')
            if task_type == 'once' and not next_run_time:
                next_run_time = datetime.now()
            
            # scheduler_id是必填参数
            scheduler_id = task_config.get('scheduler_id')
            if not scheduler_id:
                raise ValueError(f"Task config for '{task_name}' missing required scheduler_id")
            
            # 创建任务对象
            task_obj = ScheduledTask(
                scheduler_id=scheduler_id,
                task_name=task_name,
                task_type=TaskType(task_type),
                queue_name=queue_name,
                task_args=task_config.get('task_args', []),
                task_kwargs=task_config.get('task_kwargs', {}),
                interval_seconds=task_config.get('interval_seconds'),
                cron_expression=task_config.get('cron_expression'),
                next_run_time=next_run_time,
                enabled=task_config.get('enabled', True),
                max_retries=task_config.get('max_retries', 3),
                retry_delay=task_config.get('retry_delay', 60),
                timeout=task_config.get('timeout', 300),
                description=task_config.get('description'),
                tags=task_config.get('tags', []),
                metadata=task_config.get('metadata', {})
            )
            task_objects.append(task_obj)
        
        # 批量创建
        created_tasks = await self.scheduler_manager.batch_create_tasks(task_objects, skip_existing)
        
        logger.info(f"Batch created {len(created_tasks)} scheduled tasks")
        return created_tasks
    
    async def bulk_write_scheduled_tasks(self, tasks: list):
        """
        批量写入定时任务（配合at_once=False使用）
        
        使用示例：
            # 收集任务对象
            tasks = []
            for i in range(100):
                task = await app.add_scheduled_task(
                    task_name="my_task",
                    scheduler_id=f"task_{i}",
                    task_type="interval",
                    interval_seconds=30,
                    at_once=False  # 不立即保存
                )
                tasks.append(task)
            
            # 批量写入
            created_tasks = await app.bulk_write_scheduled_tasks(tasks)
        
        Args:
            tasks: 通过add_scheduled_task(at_once=False)创建的任务对象列表
        
        Returns:
            成功创建的任务列表
        """
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        if not tasks:
            return []
        
        # 准备批量创建的任务列表
        task_objects = []
        for task in tasks:
            if not hasattr(task, 'scheduler_id'):
                logger.warning("Invalid task object, skipping")
                continue
            
            
            task_objects.append(task)
        
        # 批量创建（使用第一个任务的skip_if_exists设置）
        skip_existing = getattr(tasks[0], '_skip_if_exists', True) if tasks else True
        created_tasks = await self.scheduler_manager.batch_create_tasks(task_objects, skip_existing)
        
        logger.info(f"Bulk wrote {len(created_tasks)} scheduled tasks")
        return created_tasks
    
    async def list_scheduled_tasks(self, **filters):
        """列出定时任务"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        return await self.scheduler_manager.list_tasks(**filters)
    
    async def get_scheduled_task(self, scheduler_id: str):
        """获取定时任务详情"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        return await self.scheduler_manager.get_task_by_scheduler_id(scheduler_id)
    
    async def pause_scheduled_task(self, scheduler_id: str):
        """暂停/禁用定时任务"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        # 通过scheduler_id获取任务
        task = await self.scheduler_manager.get_task_by_scheduler_id(scheduler_id)
            
        if task:
            task.enabled = False
            await self.scheduler_manager.update_task(task)
            
            # 从Redis中移除
            if self.scheduler:
                await self.scheduler.loader.remove_task(task.id)
            
            logger.info(f"Task {task.id} (scheduler_id: {task.scheduler_id}) disabled")
            return True
        return False
    
    async def resume_scheduled_task(self, scheduler_id: str):
        """恢复/启用定时任务"""
        # 自动初始化
        await self._ensure_scheduler_initialized()
        
        # 通过scheduler_id获取任务
        task = await self.scheduler_manager.get_task_by_scheduler_id(scheduler_id)
            
        if task:
            task.enabled = True
            task.next_run_time = task.calculate_next_run_time()
            await self.scheduler_manager.update_task(task)
            
            # 触发重新加载
            if self.scheduler:
                await self.scheduler.loader.load_tasks()
            
            logger.info(f"Task {task.id} (scheduler_id: {task.scheduler_id}) enabled")
            return True
        return False
    
    # 别名，更直观
    async def disable_scheduled_task(self, scheduler_id: str):
        """禁用定时任务"""
        return await self.pause_scheduled_task(scheduler_id=scheduler_id)
    
    async def enable_scheduled_task(self, scheduler_id: str):
        """启用定时任务"""
        return await self.resume_scheduled_task(scheduler_id=scheduler_id)
    
