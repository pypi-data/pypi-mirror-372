"""
自定义异常钩子，用于简化任务执行错误的显示
"""
import sys
import os
from ..exceptions import TaskExecutionError


# 保存原始的 excepthook
_original_excepthook = sys.excepthook


def custom_excepthook(exc_type, exc_value, exc_traceback):
    """
    自定义异常钩子，用于处理 TaskExecutionError
    只显示业务层的错误信息，隐藏框架层堆栈
    """
    if isinstance(exc_value, TaskExecutionError):
        # 对于任务执行错误，只显示业务层错误信息
        print(f"\n任务执行失败 (Task ID: {exc_value.task_id}):", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        if exc_value.error_traceback and exc_value.error_traceback != "Task execution failed":
            print(exc_value.error_traceback, file=sys.stderr)
        else:
            print("Task execution failed (no detailed error information available)", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        sys.exit(1)
    else:
        # 其他异常使用原始的 excepthook
        _original_excepthook(exc_type, exc_value, exc_traceback)


def install_clean_traceback():
    """
    安装简化的异常显示钩子
    
    这会替换默认的异常显示，对于 TaskExecutionError 只显示业务错误
    """
    sys.excepthook = custom_excepthook


def uninstall_clean_traceback():
    """
    卸载简化的异常显示钩子，恢复默认行为
    """
    sys.excepthook = _original_excepthook


# 检查环境变量，决定是否自动安装
# 用户可以通过设置 JETTASK_FULL_TRACEBACK=1 来禁用简化显示
if os.environ.get('JETTASK_FULL_TRACEBACK', '').lower() not in ('1', 'true', 'yes'):
    # 默认自动安装简化的异常显示
    install_clean_traceback()