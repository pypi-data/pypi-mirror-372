from .core.app import Jettask
from .core.task import Task, Request, ExecuteResponse
from .core.context import TaskContext
from .router import TaskRouter
from .exceptions import JetTaskException, TaskTimeoutError, TaskExecutionError, TaskNotFoundError, RetryableError
from .utils.error_handler import clean_task_errors, handle_task_error
from .utils.task_logger import (
    configure_task_logging,
    get_task_logger,
    TaskContextManager,
    set_task_context,
    clear_task_context,
    LogContext
)

# 自动安装简化的异常显示（用户可通过环境变量 JETTASK_FULL_TRACEBACK=1 禁用）
from .utils import exception_hook  # 这会自动安装 excepthook

__version__ = "0.1.0"
__all__ = [
    "Jettask", 
    "Task",
    "TaskContext",
    "TaskRouter", 
    "Request", 
    "ExecuteResponse",
    "JetTaskException",
    "TaskTimeoutError",
    "TaskExecutionError",
    "TaskNotFoundError",
    "RetryableError",
    "clean_task_errors",
    "handle_task_error",
    "configure_task_logging",
    "get_task_logger",
    "TaskContextManager",
    "set_task_context",
    "clear_task_context",
    "LogContext"
]