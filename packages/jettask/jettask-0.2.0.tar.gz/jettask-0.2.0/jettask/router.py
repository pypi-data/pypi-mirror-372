"""
Task Router for modular task organization
Similar to FastAPI's APIRouter
"""

from typing import Optional, Dict, List, Any, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class TaskRouter:
    """
    任务路由器，用于模块化组织任务
    
    使用示例：
        # tasks/email_tasks.py
        from jettask import TaskRouter
        
        router = TaskRouter(prefix="email", queue="emails")
        
        @router.task()
        async def send_welcome_email(user_id: str):
            # 实际任务名会是: email.send_welcome_email
            # 默认队列会是: emails
            pass
        
        # main.py
        from jettask import Jettask
        from tasks.email_tasks import router as email_router
        
        app = Jettask(redis_url="redis://localhost:6379/0")
        app.register_router(email_router)
    """
    
    def __init__(
        self,
        prefix: str = None,
        queue: str = None,
        tags: List[str] = None,
        default_timeout: int = None,
        default_max_retries: int = None,
        default_retry_delay: int = None,
    ):
        """
        初始化任务路由器
        
        Args:
            prefix: 任务名称前缀
            queue: 默认队列名
            tags: 标签列表，用于任务分组
            default_timeout: 默认超时时间
            default_max_retries: 默认最大重试次数
            default_retry_delay: 默认重试延迟
        """
        self.prefix = prefix
        self.default_queue = queue
        self.tags = tags or []
        self.default_timeout = default_timeout
        self.default_max_retries = default_max_retries
        self.default_retry_delay = default_retry_delay
        
        # 存储注册的任务
        self._tasks: Dict[str, Dict[str, Any]] = {}
        
    def task(
        self,
        name: str = None,
        queue: str = None,
        timeout: int = None,
        max_retries: int = None,
        retry_delay: int = None,
        **kwargs
    ):
        """
        任务装饰器
        
        Args:
            name: 任务名称（可选，默认使用函数名）
            queue: 队列名（可选，默认使用路由器的默认队列）
            timeout: 超时时间
            max_retries: 最大重试次数
            retry_delay: 重试延迟
            **kwargs: 其他任务参数
        """
        def decorator(func: Callable):
            # 生成任务名
            task_name = name or func.__name__
            if self.prefix:
                full_task_name = f"{self.prefix}.{task_name}"
            else:
                full_task_name = task_name
            
            # 合并参数（优先使用任务级别的参数）
            task_config = {
                'func': func,
                'name': full_task_name,
                'queue': queue or self.default_queue,
                'timeout': timeout or self.default_timeout,
                'max_retries': max_retries or self.default_max_retries,
                'retry_delay': retry_delay or self.default_retry_delay,
                'tags': self.tags,
                **kwargs
            }
            
            # 移除None值
            task_config = {k: v for k, v in task_config.items() if v is not None}
            
            # 存储任务配置
            self._tasks[full_task_name] = task_config
            
            # 返回原函数，保持函数可以被直接调用
            return func
            
        return decorator
    
    def include_router(self, router: 'TaskRouter', prefix: str = None):
        """
        包含另一个路由器（子路由器）
        
        Args:
            router: 要包含的路由器
            prefix: 额外的前缀
        """
        # 合并前缀
        if prefix:
            if self.prefix:
                combined_prefix = f"{self.prefix}.{prefix}"
            else:
                combined_prefix = prefix
        else:
            combined_prefix = self.prefix
        
        # 复制任务时更新前缀
        for task_name, task_config in router._tasks.items():
            # 更新任务名
            if combined_prefix and not task_name.startswith(combined_prefix):
                if router.prefix and task_name.startswith(router.prefix):
                    # 替换原有前缀
                    new_name = task_name.replace(router.prefix, combined_prefix, 1)
                else:
                    new_name = f"{combined_prefix}.{task_name}"
            else:
                new_name = task_name
            
            # 复制配置
            new_config = task_config.copy()
            new_config['name'] = new_name
            
            # 如果没有指定队列，使用当前路由器的默认队列
            if 'queue' not in new_config or new_config['queue'] is None:
                new_config['queue'] = self.default_queue
            
            self._tasks[new_name] = new_config
    
    def get_tasks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有注册的任务"""
        return self._tasks