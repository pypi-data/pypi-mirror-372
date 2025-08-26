"""
错误处理工具
"""
import sys
import functools
from contextlib import contextmanager
from ..exceptions import TaskExecutionError


@contextmanager
def clean_task_errors():
    """
    上下文管理器，用于清理任务执行错误的堆栈
    
    使用示例:
        with clean_task_errors():
            result = await app.get_result(event_id, wait=True)
    """
    try:
        yield
    except TaskExecutionError as e:
        # 直接打印错误信息，不显示框架堆栈
        print(f"\n任务执行失败 (Task ID: {e.task_id}):", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        if e.error_traceback and e.error_traceback != "Task execution failed":
            print(e.error_traceback, file=sys.stderr)
        else:
            print("Task execution failed (no detailed error information available)", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n操作被用户中断", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        # 其他异常正常抛出
        raise


def handle_task_error(func):
    """
    装饰器，用于处理任务执行错误
    
    使用示例:
        @handle_task_error
        async def main():
            result = await app.get_result(event_id, wait=True)
    """
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TaskExecutionError as e:
            print(f"\n任务执行失败 (Task ID: {e.task_id}):", file=sys.stderr)
            print("-" * 60, file=sys.stderr)
            if e.error_traceback and e.error_traceback != "Task execution failed":
                print(e.error_traceback, file=sys.stderr)
            else:
                print("Task execution failed (no detailed error information available)", file=sys.stderr)
            print("-" * 60, file=sys.stderr)
            sys.exit(1)
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TaskExecutionError as e:
            print(f"\n任务执行失败 (Task ID: {e.task_id}):", file=sys.stderr)
            print("-" * 60, file=sys.stderr)
            if e.error_traceback and e.error_traceback != "Task execution failed":
                print(e.error_traceback, file=sys.stderr)
            else:
                print("Task execution failed (no detailed error information available)", file=sys.stderr)
            print("-" * 60, file=sys.stderr)
            sys.exit(1)
    
    # 根据函数类型返回对应的包装器
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper