"""
过滤框架层堆栈信息的工具函数
"""
import traceback
import sys
from typing import Optional


def filter_framework_traceback(exc_type=None, exc_value=None, exc_traceback=None) -> str:
    """
    过滤框架层的堆栈信息，只保留业务代码的异常信息
    
    Args:
        exc_type: 异常类型
        exc_value: 异常值
        exc_traceback: 异常回溯对象
    
    Returns:
        过滤后的堆栈信息字符串
    """
    if exc_type is None:
        # 如果没有提供参数，获取当前异常信息
        exc_type, exc_value, exc_traceback = sys.exc_info()
    
    if exc_traceback is None:
        return "No traceback available"
    
    # 需要过滤的框架文件路径关键词
    framework_paths = [
        '/jettask/executors/',
        '/jettask/core/',
        '/jettask/monitoring/',
        '/jettask/utils/',
        'asyncio/',
        'concurrent/',
        'multiprocessing/',
    ]
    
    # 提取堆栈帧
    tb_frames = []
    tb = exc_traceback
    
    # 遍历堆栈，找到第一个非框架代码的帧
    business_frames = []
    while tb is not None:
        frame = tb.tb_frame
        filename = frame.f_code.co_filename
        
        # 检查是否是框架代码
        is_framework = any(path in filename for path in framework_paths)
        
        # 收集业务代码帧
        if not is_framework:
            business_frames.append(tb)
        
        tb = tb.tb_next
    
    # 如果找到了业务代码帧，只使用这些帧
    if business_frames:
        # 格式化业务代码的堆栈
        lines = []
        for tb in business_frames:
            frame = tb.tb_frame
            filename = frame.f_code.co_filename
            lineno = tb.tb_lineno
            name = frame.f_code.co_name
            
            lines.append(f'  File "{filename}", line {lineno}, in {name}\n')
            
            # 尝试获取源代码行
            try:
                import linecache
                line = linecache.getline(filename, lineno, frame.f_globals)
                if line:
                    lines.append(f'    {line.strip()}\n')
            except:
                pass
        
        # 添加异常信息
        if lines:
            result = "Traceback (most recent call last):\n"
            result += "".join(lines)
            result += f"{exc_type.__name__}: {exc_value}"
            return result
    
    # 如果没有找到业务代码帧，返回简化的错误信息
    return f"{exc_type.__name__}: {exc_value}"


def get_clean_exception_message() -> str:
    """
    获取清理后的异常信息（不包含框架层堆栈）
    
    Returns:
        清理后的异常信息
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    if exc_type is None:
        return "No exception"
    
    # 如果是简单的异常，直接返回异常信息
    if exc_value:
        return f"{exc_type.__name__}: {exc_value}"
    
    return f"{exc_type.__name__}"