import os
import sys
import socket
import time
import inspect
import asyncio
from functools import lru_cache
from typing import Dict, Any, Optional

# 缓存主机名避免重复系统调用
@lru_cache(maxsize=1)
def get_hostname(timestamp_suffix=False) -> str:
    """获取当前主机名称"""
    host_name = socket.gethostname()
    return f"{host_name}-{int(time.time())}" if timestamp_suffix else host_name


def gen_task_name(name, module_name):
    """Generate task name from name/module pair."""
    module_name = module_name or "__main__"
    try:
        module = sys.modules[module_name]
    except KeyError:
        # Fix for manage.py shell_plus (Issue #366)
        module = None
    if module is not None and hasattr(module, '__file__') and module.__file__:
        base_name = os.path.basename(module.__file__)
        module_name = base_name.split(".")[0]
    return ".".join(p for p in (module_name, name) if p)


def is_async_function(func):
    """检查函数是否是async函数"""
    return inspect.iscoroutinefunction(func)

# 高性能JSON序列化
def get_json_serializer():
    """获取最优的JSON序列化器"""
    try:
        import orjson
        return {
            'loads': orjson.loads,
            'dumps': lambda obj: orjson.dumps(obj).decode('utf-8'),
            'name': 'orjson'
        }
    except ImportError:
        try:
            import ujson
            return {
                'loads': ujson.loads,
                'dumps': ujson.dumps,
                'name': 'ujson'
            }
        except ImportError:
            import json
            return {
                'loads': json.loads,
                'dumps': json.dumps,
                'name': 'json'
            }

# 全局JSON序列化器实例
_json_serializer = get_json_serializer()
json_loads = _json_serializer['loads']
json_dumps = _json_serializer['dumps']

class PerformanceStats:
    """性能统计"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.processed = 0
        self.errors = 0
        self.start_time = time.time()
        self.last_rate_check = self.start_time
        self.last_processed = 0
    
    def increment_processed(self):
        self.processed += 1
    
    def increment_errors(self):
        self.errors += 1
    
    def get_current_rate(self) -> float:
        """获取当前处理速率"""
        now = time.time()
        elapsed = now - self.last_rate_check
        if elapsed < 1.0:  # 至少1秒才计算速率
            return 0.0
        
        processed_delta = self.processed - self.last_processed
        rate = processed_delta / elapsed
        
        self.last_rate_check = now
        self.last_processed = self.processed
        
        return rate
    
    def get_overall_rate(self) -> float:
        """获取总体处理速率"""
        elapsed = time.time() - self.start_time
        return self.processed / elapsed if elapsed > 0 else 0.0

def batch_items(items: list, batch_size: int):
    """将列表分批处理"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

def adaptive_sleep(has_work: bool, base_sleep: float = 0.001):
    """自适应休眠时间"""
    if has_work:
        return base_sleep / 10  # 有工作时减少休眠
    else:
        return base_sleep  # 无工作时正常休眠