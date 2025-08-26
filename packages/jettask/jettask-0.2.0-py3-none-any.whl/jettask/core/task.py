from ..utils.serializer import dumps_str, loads_str
import time
import inspect
from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING, get_type_hints

if TYPE_CHECKING:
    from .app import Jettask

from .context import TaskContext


@dataclass
class ExecuteResponse:
    delay: Optional[float] = None 
    urgent_retry: bool = False 
    reject: bool = False
    retry_time: Optional[float] = None


class Request:
    id: str = None
    name: str = None
    app: "Jettask" = None

    def __init__(self, *args, **kwargs) -> None:
        self._update(*args, **kwargs)

    def _update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)


class Task:
    _app: "Jettask" = None
    name: str = None
    queue: str = None
    trigger_time: float = None
    retry_config: Optional[dict] = None  # 存储任务级别的重试配置

    def __call__(self, event_id: str, trigger_time: float, *args: Any, **kwds: Any) -> Any:
        # 检查函数签名以进行依赖注入
        injected_args, injected_kwargs = self._inject_dependencies(
            event_id, trigger_time, args, kwds
        )
        return self.run(*injected_args, **injected_kwargs)
    
    def _inject_dependencies(self, event_id: str, trigger_time: float, args: tuple, kwargs: dict) -> tuple:
        """
        基于类型注解自动注入TaskContext
        """
        # 获取run方法的签名
        try:
            sig = inspect.signature(self.run)
            type_hints = get_type_hints(self.run)
        except (ValueError, TypeError, NameError):
            # 如果获取签名失败，返回原始参数
            return args, kwargs
        
        # 创建TaskContext实例
        context = TaskContext(
            event_id=event_id,
            name=self.name,
            trigger_time=trigger_time,
            app=self._app,
            queue=self.queue,
            # worker_id和retry_count可以从其他地方获取
            # 暂时使用默认值
        )
        
        # 收集所有需要TaskContext的参数位置
        context_params = []
        params_list = list(sig.parameters.items())
        
        for idx, (param_name, param) in enumerate(params_list):
            # 跳过self参数
            if param_name == 'self':
                continue
                
            # 检查参数类型是否是TaskContext
            param_type = type_hints.get(param_name)
            if param_type is TaskContext:
                # 计算实际的参数索引（排除self）
                actual_idx = idx - 1 if params_list[0][0] == 'self' else idx
                context_params.append((actual_idx, param_name, param))
        
        # 如果没有TaskContext参数，直接返回
        if not context_params:
            return args, kwargs
        
        # 处理TaskContext注入
        new_args = list(args)
        new_kwargs = dict(kwargs)
        
        for param_idx, param_name, param in context_params:
            # 如果是关键字参数
            if param.kind == param.KEYWORD_ONLY:
                if param_name not in new_kwargs:
                    new_kwargs[param_name] = context
            # 如果是位置参数
            elif param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                # 在对应位置插入TaskContext
                new_args.insert(param_idx, context)
                # 只处理第一个TaskContext（通常只有一个）
                break
        
        return tuple(new_args), new_kwargs

    def run(self, *args, **kwargs):
        """The body of the task executed by workers."""
        raise NotImplementedError("Tasks must define the run method.")

    @classmethod
    def bind_app(cls, app):
        cls._app = app

    def apply_async(
        self,
        args: tuple = None,
        kwargs: dict = None,
        queue: str = None,
        at_once: bool = True,
        asyncio: bool = False,
        routing: dict = None,
        delay: int = None,
        timeout: int = None,
    ):
        """
        异步执行任务
        
        Args:
            args: 位置参数
            kwargs: 关键字参数
            queue: 队列名
            at_once: 是否立即发送
            asyncio: 是否使用异步模式
            routing: 路由信息
            delay: 延迟执行秒数（最多86400秒/1天）
            timeout: 任务超时时间
        
        Returns:
            任务ID或任务消息
        """
        queue = queue or self.queue
        message = {
            "queue": queue,
            "name": self.name,
            "args": args or (),
            "kwargs": kwargs or {},
            'trigger_time': time.time()
        }
        
        if routing:
            message['routing'] = routing or {}
        
        # 添加任务选项
        if timeout:
            message['timeout'] = timeout
        
        # 如果有延迟参数，添加到消息中
        if delay:
            message['delay'] = delay
        
        if not at_once:
            return message
        
        # 处理延迟任务
        if delay:
            if asyncio:
                import asyncio as aio
                return aio.create_task(self._send_delayed_task(queue, message, delay))
            else:
                return self.send_delayed_task(queue, message, delay)
        
        # 立即发送任务
        if asyncio:
            import asyncio as aio
            return aio.create_task(self._send_task(queue, message))
        else:
            return self.send_task(queue, message)

    def on_before(self, event_id, pedding_count, args, kwargs) -> ExecuteResponse:
        return ExecuteResponse()

    def on_end(self, event_id, pedding_count, args, kwargs, result) -> ExecuteResponse:
        return ExecuteResponse()

    def on_success(self, event_id, args, kwargs, result) -> ExecuteResponse:
        return ExecuteResponse()

    def send_task(self, queue, message):
        # 如果queue为None，使用任务名作为队列名
        actual_queue = queue or self.name
        message['queue'] = actual_queue
        
        # 如果任务有默认重试配置且消息中没有重试配置，则添加默认配置
        if self.retry_config and 'retry_config' not in message:
            message['retry_config'] = self.retry_config
        
        event_id = self._app.ep.send_event(actual_queue, message, False)
        # 只设置status，其他信息从Stream消息获取
        key = f"{self._app.ep.redis_prefix or 'jettask'}:TASK:{event_id}"
        self._app.redis.hset(key, "status", "pending")
        self._app.redis.expire(key, 3600)
        return event_id

    async def _send_task(self, queue, message):
        # 如果queue为None，使用任务名作为队列名
        actual_queue = queue or self.name
        message['queue'] = actual_queue
        
        # 如果任务有默认重试配置且消息中没有重试配置，则添加默认配置
        if self.retry_config and 'retry_config' not in message:
            message['retry_config'] = self.retry_config
        
        event_id = await self._app.ep.send_event(actual_queue, message, True)
        # 只设置status，其他信息从Stream消息获取
        key = f"{self._app.ep.redis_prefix or 'jettask'}:TASK:{event_id}"
        await self._app.async_redis.hset(key, "status", "pending")
        await self._app.async_redis.expire(key, 3600)
        return event_id
    
    def send_delayed_task(self, queue, message, delay_seconds):
        """发送延迟任务（同步）- 使用Redis zset管理延迟队列"""
        # 添加执行时间到消息中
        current_time = time.time()
        execute_at = current_time + delay_seconds
        message['execute_at'] = execute_at
        message['is_delayed'] = 1  # 使用1代替True
        message['trigger_time'] = current_time  # 添加trigger_time字段
        
        # 如果queue为None，使用任务名作为队列名
        actual_queue = queue or self.name
        
        # 更新message中的queue字段
        message['queue'] = actual_queue
        
        # 直接发送到正常的队列（Stream），使用stream_id作为event_id
        stream_id = self._app.ep.send_event(actual_queue, message, asyncio=False)
        
        # 将stream_id保存到message中，供worker使用
        message['event_id'] = stream_id
        
        # 将任务添加到延迟队列zset中
        # key格式: {prefix}:DELAYED_QUEUE:{queue}
        delayed_queue_key = f"{self._app.ep.redis_prefix or 'jettask'}:DELAYED_QUEUE:{actual_queue}"
        # 使用执行时间作为score，stream_id作为member
        self._app.redis.zadd(delayed_queue_key, {stream_id: execute_at})
        
        # 只设置status，其他信息从Stream消息获取
        # 确保stream_id是字符串
        stream_id_str = stream_id.decode() if isinstance(stream_id, bytes) else stream_id
        key = f"{self._app.ep.redis_prefix or 'jettask'}:TASK:{stream_id_str}"
        self._app.redis.hset(key, "status", "delayed")
        # 确保过期时间是整数（Redis EXPIRE要求整数秒）
        expire_seconds = max(1, int(delay_seconds + 3600))
        self._app.redis.expire(key, expire_seconds)
        
        return stream_id  # 返回stream_id作为event_id
    
    async def _send_delayed_task(self, queue, message, delay_seconds):
        """发送延迟任务（异步）- 使用Redis zset管理延迟队列"""
        # 添加执行时间到消息中
        current_time = time.time()
        execute_at = current_time + delay_seconds
        message['execute_at'] = execute_at
        message['is_delayed'] = 1  # 使用1代替True
        message['trigger_time'] = current_time  # 添加trigger_time字段
        
        # 如果queue为None，使用任务名作为队列名
        actual_queue = queue or self.name
        
        # 更新message中的queue字段
        message['queue'] = actual_queue
        
        # 直接发送到正常的队列（Stream），使用stream_id作为event_id
        stream_id = await self._app.ep.send_event(actual_queue, message, asyncio=True)
        
        # 将stream_id保存到message中，供worker使用
        message['event_id'] = stream_id
        
        # 将任务添加到延迟队列zset中
        # key格式: {prefix}:DELAYED_QUEUE:{queue}
        delayed_queue_key = f"{self._app.ep.redis_prefix or 'jettask'}:DELAYED_QUEUE:{actual_queue}"
        # 使用执行时间作为score，stream_id作为member
        await self._app.async_redis.zadd(delayed_queue_key, {stream_id: execute_at})
        
        # 只设置status，其他信息从Stream消息获取
        # 确保stream_id是字符串
        stream_id_str = stream_id.decode() if isinstance(stream_id, bytes) else stream_id
        key = f"{self._app.ep.redis_prefix or 'jettask'}:TASK:{stream_id_str}"
        await self._app.async_redis.hset(key, "status", "delayed")
        # 确保过期时间是整数（Redis EXPIRE要求整数秒）
        expire_seconds = max(1, int(delay_seconds + 3600))
        await self._app.async_redis.expire(key, expire_seconds)
        
        return stream_id  # 返回stream_id作为event_id

    def read_pending(
        self,
        queue: str = None,
        asyncio: bool = False,
    ):
        queue = queue or self.queue
        if asyncio:
            return self._get_pending(queue)
        return self._app.ep.read_pending(queue, queue)

    async def _get_pending(self, queue: str):
        return await self._app.ep.read_pending(queue, queue, asyncio=True)