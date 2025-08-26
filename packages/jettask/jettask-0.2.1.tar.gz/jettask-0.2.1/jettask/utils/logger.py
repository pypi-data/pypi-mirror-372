"""
任务日志工具
"""
import logging


def get_task_logger(name: str = None) -> logging.Logger:
    """
    获取任务专用的logger
    
    Args:
        name: logger名称，如果不指定则使用'jettask.task'
    
    Returns:
        配置好的logger实例
    """
    if name is None:
        name = 'jettask.task'
    elif not name.startswith('jettask.'):
        name = f'jettask.task.{name}'
    
    logger = logging.getLogger(name)
    
    # 如果logger还没有处理器，添加默认处理器
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger