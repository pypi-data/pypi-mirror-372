"""
任务日志管理器
提供结构化日志输出，自动注入任务上下文信息
"""
import logging
import json
import sys
import contextvars
from typing import Optional, Dict, Any
from datetime import datetime


# 使用 contextvars 存储任务上下文，支持异步并发
task_context = contextvars.ContextVar('task_context', default={})


class TaskContextFilter(logging.Filter):
    """
    日志过滤器，自动添加任务上下文信息
    """
    def filter(self, record):
        """为日志记录添加任务上下文"""
        ctx = task_context.get()
        if ctx:
            # 添加任务相关字段
            record.task_id = ctx.get('task_id', '')
            record.task_name = ctx.get('task_name', '')
            record.queue = ctx.get('queue', '')
            record.event_id = ctx.get('event_id', '')
            record.worker_id = ctx.get('worker_id', '')
            
            # 添加所有自定义字段到 extra_fields
            custom_fields = {}
            for key, value in ctx.items():
                if key not in ('task_id', 'task_name', 'queue', 'event_id', 'worker_id'):
                    custom_fields[key] = value
            
            if custom_fields:
                # 如果record已有extra_fields，合并它们
                if hasattr(record, 'extra_fields'):
                    record.extra_fields = {**custom_fields, **record.extra_fields}
                else:
                    record.extra_fields = custom_fields
        else:
            # 没有任务上下文时使用空值
            record.task_id = ''
            record.task_name = ''
            record.queue = ''
            record.event_id = ''
            record.worker_id = ''
        return True


class ExtendedTextFormatter(logging.Formatter):
    """
    扩展的文本格式化器，支持输出额外字段
    """
    def format(self, record):
        """格式化日志，包含额外字段"""
        # 先使用标准格式化
        result = super().format(record)
        
        # 收集所有额外字段
        extra_parts = []
        
        # 添加 extra_fields 中的字段
        if hasattr(record, 'extra_fields') and record.extra_fields:
            for key, value in record.extra_fields.items():
                extra_parts.append(f"{key}={value}")
        
        # 如果有额外字段，添加到日志末尾
        if extra_parts:
            result += f" | {', '.join(extra_parts)}"
        
        return result


class JSONFormatter(logging.Formatter):
    """
    JSON格式化器，输出结构化JSON日志
    """
    def format(self, record):
        """格式化日志为JSON"""
        log_obj = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # 添加任务上下文（如果存在）
        if hasattr(record, 'task_id') and record.task_id:
            log_obj['task_id'] = record.task_id
        if hasattr(record, 'task_name') and record.task_name:
            log_obj['task_name'] = record.task_name
        if hasattr(record, 'queue') and record.queue:
            log_obj['queue'] = record.queue
        if hasattr(record, 'event_id') and record.event_id:
            log_obj['event_id'] = record.event_id
        if hasattr(record, 'worker_id') and record.worker_id:
            log_obj['worker_id'] = record.worker_id
        
        # 添加异常信息（如果存在）
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        # 添加额外字段（如果有）
        if hasattr(record, 'extra_fields'):
            log_obj.update(record.extra_fields)
        
        return json.dumps(log_obj, ensure_ascii=False)


class TaskLogger:
    """
    任务日志管理器
    """
    def __init__(self, name: str = 'jettask.worker', level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self._configured = False
        
    def configure_json_output(self, stream=None):
        """
        配置JSON格式输出
        
        Args:
            stream: 输出流，默认为 sys.stdout
        """
        if self._configured:
            return
        
        # 移除现有的处理器
        self.logger.handlers.clear()
        
        # 创建JSON格式的处理器
        handler = logging.StreamHandler(stream or sys.stdout)
        handler.setFormatter(JSONFormatter())
        
        # 添加任务上下文过滤器
        handler.addFilter(TaskContextFilter())
        
        self.logger.addHandler(handler)
        self._configured = True
        
        # 禁止传播到父logger，避免重复输出
        self.logger.propagate = False
    
    def configure_text_output(self, stream=None, format_string=None):
        """
        配置文本格式输出（带任务ID）
        
        Args:
            stream: 输出流，默认为 sys.stderr
            format_string: 日志格式字符串
        """
        if self._configured:
            return
        
        # 移除现有的处理器
        self.logger.handlers.clear()
        
        # 默认格式
        if format_string is None:
            format_string = '%(asctime)s - %(levelname)s - [%(task_id)s] - %(name)s - %(message)s'
        
        # 创建文本格式的处理器
        handler = logging.StreamHandler(stream or sys.stderr)
        handler.setFormatter(ExtendedTextFormatter(format_string))
        
        # 添加任务上下文过滤器
        handler.addFilter(TaskContextFilter())
        
        self.logger.addHandler(handler)
        self._configured = True
        
        # 禁止传播到父logger
        self.logger.propagate = False
    
    def get_logger(self):
        """获取配置好的logger实例"""
        if not self._configured:
            # 默认配置文本输出
            self.configure_text_output()
        return self.logger


class TaskContextManager:
    """
    任务上下文管理器，用于设置和清理任务上下文
    """
    def __init__(self, event_id: str, task_name: str, queue: str, 
                 worker_id: Optional[str] = None, **extra):
        """
        初始化任务上下文
        
        Args:
            event_id: 任务事件ID
            task_name: 任务名称
            queue: 队列名称
            worker_id: Worker ID
            **extra: 额外的上下文信息
        """
        self.context = {
            'event_id': event_id,
            'task_id': event_id,  # 兼容性：task_id 等同于 event_id
            'task_name': task_name,
            'queue': queue,
            'worker_id': worker_id or '',
            **extra
        }
        self.token = None
    
    def __enter__(self):
        """进入上下文，设置任务信息"""
        self.token = task_context.set(self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，清理任务信息"""
        if self.token:
            task_context.reset(self.token)
    
    async def __aenter__(self):
        """异步进入上下文"""
        self.token = task_context.set(self.context)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步退出上下文"""
        if self.token:
            task_context.reset(self.token)


def set_task_context(event_id: str, task_name: str, queue: str, 
                     worker_id: Optional[str] = None, **extra):
    """
    设置当前任务上下文
    
    Args:
        event_id: 任务事件ID
        task_name: 任务名称  
        queue: 队列名称
        worker_id: Worker ID
        **extra: 额外的上下文信息
    
    Returns:
        上下文token，用于后续重置
    """
    context = {
        'event_id': event_id,
        'task_id': event_id,
        'task_name': task_name,
        'queue': queue,
        'worker_id': worker_id or '',
        **extra
    }
    return task_context.set(context)


def clear_task_context(token=None):
    """
    清除任务上下文
    
    Args:
        token: 上下文token
    """
    if token:
        task_context.reset(token)
    else:
        task_context.set({})


class LogContext:
    """
    灵活的日志上下文管理器，用于临时添加额外的日志字段
    
    特点:
    - 不需要必填字段
    - 可在同步和异步函数中使用
    - 会合并而不是覆盖现有的上下文
    - 退出时自动恢复原始上下文
    
    Example:
        # 在同步函数中使用
        def sync_func():
            with LogContext(user_id='123', action='login'):
                logger.info("用户登录")  # 自动带上 user_id 和 action
        
        # 在异步函数中使用（直接用 with，不需要 async with）
        async def async_func():
            with LogContext(request_id='req-001'):
                logger.info("处理请求")  # 自动带上 request_id
                await some_async_operation()
            
        # 嵌套使用
        with LogContext(user_id='123'):
            logger.info("外层日志")  # 带 user_id
            with LogContext(action='update', item_id='456'):
                logger.info("内层日志")  # 带 user_id, action, item_id
            logger.info("回到外层")  # 只带 user_id
    """
    
    def __init__(self, **fields):
        """
        初始化日志上下文
        
        Args:
            **fields: 要添加到日志的额外字段
        """
        self.fields = fields
        self.token = None
        self.original_context = None
    
    def __enter__(self):
        """进入上下文，合并新字段到现有上下文"""
        # 获取当前上下文
        current_ctx = task_context.get()
        self.original_context = current_ctx.copy() if current_ctx else {}
        
        # 合并新字段
        new_ctx = {**self.original_context, **self.fields}
        
        # 设置新上下文
        self.token = task_context.set(new_ctx)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，恢复原始上下文"""
        if self.token:
            task_context.set(self.original_context)


def get_task_logger(name: str = None) -> logging.Logger:
    """
    获取带任务上下文的logger
    
    Args:
        name: logger名称，默认使用调用者的模块名
    
    Returns:
        配置好的logger实例
    """
    import inspect
    if name is None:
        # 自动获取调用者的模块名
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'jettask.worker')
        else:
            name = 'jettask.worker'
    
    logger = logging.getLogger(name)
    
    # 如果logger还没有处理器，添加默认处理器
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ExtendedTextFormatter(
            '%(asctime)s - %(levelname)s - [%(task_id)s] - %(name)s - %(message)s'
        ))
        handler.addFilter(TaskContextFilter())
        logger.addHandler(handler)
        logger.propagate = False
    
    return logger


# 全局任务日志管理器实例
task_logger_manager = TaskLogger()


def configure_task_logging(format: str = 'text', level: int = logging.INFO, **kwargs):
    """
    配置任务日志
    
    Args:
        format: 日志格式，'json' 或 'text'
        level: 日志级别
        **kwargs: 其他配置参数
    
    Example:
        # 配置JSON格式日志
        configure_task_logging(format='json')
        
        # 配置文本格式日志
        configure_task_logging(format='text', format_string='%(asctime)s [%(task_id)s] %(message)s')
    """
    task_logger_manager.logger.setLevel(level)
    
    if format == 'json':
        task_logger_manager.configure_json_output(
            stream=kwargs.get('stream', sys.stdout)
        )
    else:
        task_logger_manager.configure_text_output(
            stream=kwargs.get('stream', sys.stderr),
            format_string=kwargs.get('format_string')
        )
    
    # 配置所有存在的logger
    for logger_name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        
        # 更新所有现有handler
        for handler in logger.handlers:
            # 移除旧的filter和formatter
            handler.filters.clear()
            
            # 添加任务上下文过滤器
            handler.addFilter(TaskContextFilter())
            
            # 设置格式化器
            if format == 'json':
                handler.setFormatter(JSONFormatter())
            else:
                format_string = kwargs.get('format_string', 
                    '%(asctime)s - %(levelname)s - [%(task_id)s] - %(name)s - %(message)s')
                handler.setFormatter(ExtendedTextFormatter(format_string))
    
    # 同时配置根logger的所有处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        # 添加任务上下文过滤器到所有处理器
        handler.addFilter(TaskContextFilter())
        
        # 如果要求JSON格式，替换格式化器
        if format == 'json':
            handler.setFormatter(JSONFormatter())