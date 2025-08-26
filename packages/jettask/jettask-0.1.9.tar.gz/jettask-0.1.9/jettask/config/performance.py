"""
高性能配置
针对不同使用场景的性能优化配置
"""

import os
import socket
import multiprocessing

# 获取CPU核心数
CPU_COUNT = multiprocessing.cpu_count()

class PerformanceConfig:
    """性能配置类"""
    
    # Redis连接池配置
    REDIS_MAX_CONNECTIONS = min(200, CPU_COUNT * 20)
    REDIS_SOCKET_KEEPALIVE = True
    # 动态构建socket keepalive选项
    REDIS_SOCKET_KEEPALIVE_OPTIONS = {}
    if hasattr(socket, 'TCP_KEEPIDLE'):
        REDIS_SOCKET_KEEPALIVE_OPTIONS[socket.TCP_KEEPIDLE] = 1
    if hasattr(socket, 'TCP_KEEPINTVL'):
        REDIS_SOCKET_KEEPALIVE_OPTIONS[socket.TCP_KEEPINTVL] = 3
    if hasattr(socket, 'TCP_KEEPCNT'):
        REDIS_SOCKET_KEEPALIVE_OPTIONS[socket.TCP_KEEPCNT] = 5
    
    REDIS_SOCKET_CONNECT_TIMEOUT = 2
    REDIS_SOCKET_TIMEOUT = 2
    REDIS_HEALTH_CHECK_INTERVAL = 30
    REDIS_RETRY_ON_TIMEOUT = True
    
    # 事件循环配置
    EVENT_LOOP_SLEEP_WHEN_BUSY = 0.0001
    EVENT_LOOP_SLEEP_WHEN_IDLE = 0.001
    
    # 批处理配置
    BATCH_SIZE_ASYNCIO = 50
    BATCH_SIZE_PROCESS = 20
    BATCH_SIZE_THREAD = 10
    
    # 预取配置
    PREFETCH_MULTIPLIER_HIGH = 50
    PREFETCH_MULTIPLIER_MEDIUM = 20
    PREFETCH_MULTIPLIER_LOW = 10
    
    # 并发配置
    DEFAULT_ASYNCIO_CONCURRENCY = min(1000, CPU_COUNT * 100)
    DEFAULT_THREAD_CONCURRENCY = min(100, CPU_COUNT * 10)  
    DEFAULT_PROCESS_CONCURRENCY = CPU_COUNT
    DEFAULT_PROCESS_COROUTINES = min(100, CPU_COUNT * 10)
    
    # 缓存配置
    PENDING_CACHE_EXPIRE_TIME = 10  # 秒
    TASK_STATUS_CACHE_SIZE = 10000
    
    # 内存优化配置
    USE_ORJSON = True  # 优先使用orjson
    USE_UJSON_FALLBACK = True  # 备选ujson
    USE_MSGPACK = False  # 可选msgpack序列化
    
    @classmethod
    def get_config_for_workload(cls, workload_type: str) -> dict:
        """根据工作负载类型获取优化配置"""
        configs = {
            'io_intensive': {
                'concurrency': cls.DEFAULT_ASYNCIO_CONCURRENCY,
                'prefetch_multiplier': cls.PREFETCH_MULTIPLIER_HIGH,
                'batch_size': cls.BATCH_SIZE_ASYNCIO,
                'executor_type': 'asyncio',
                'sleep_busy': 0.0001,
                'sleep_idle': 0.001,
            },
            'cpu_intensive': {
                'concurrency': cls.DEFAULT_PROCESS_CONCURRENCY,
                'prefetch_multiplier': cls.PREFETCH_MULTIPLIER_MEDIUM,
                'batch_size': cls.BATCH_SIZE_PROCESS,
                'executor_type': 'process',
                'max_coroutines_per_process': cls.DEFAULT_PROCESS_COROUTINES,
                'sleep_busy': 0.001,
                'sleep_idle': 0.01,
            },
            'mixed': {
                'concurrency': cls.DEFAULT_THREAD_CONCURRENCY,
                'prefetch_multiplier': cls.PREFETCH_MULTIPLIER_MEDIUM,
                'batch_size': cls.BATCH_SIZE_THREAD,
                'executor_type': 'thread',
                'sleep_busy': 0.0005,
                'sleep_idle': 0.005,
            },
            'low_latency': {
                'concurrency': cls.DEFAULT_ASYNCIO_CONCURRENCY // 2,
                'prefetch_multiplier': cls.PREFETCH_MULTIPLIER_LOW,
                'batch_size': cls.BATCH_SIZE_ASYNCIO // 2,
                'executor_type': 'asyncio',
                'sleep_busy': 0.00001,  # 极低延迟
                'sleep_idle': 0.0001,
            },
            'high_throughput': {
                'concurrency': cls.DEFAULT_ASYNCIO_CONCURRENCY * 2,
                'prefetch_multiplier': cls.PREFETCH_MULTIPLIER_HIGH * 2,
                'batch_size': cls.BATCH_SIZE_ASYNCIO * 2,
                'executor_type': 'asyncio',
                'sleep_busy': 0.001,
                'sleep_idle': 0.01,
            }
        }
        
        return configs.get(workload_type, configs['mixed'])
    
    @classmethod
    def get_redis_config(cls, max_connections: int = None) -> dict:
        """获取Redis连接配置"""
        return {
            'max_connections': max_connections or cls.REDIS_MAX_CONNECTIONS,
            'socket_keepalive': cls.REDIS_SOCKET_KEEPALIVE,
            'socket_keepalive_options': cls.REDIS_SOCKET_KEEPALIVE_OPTIONS if cls.REDIS_SOCKET_KEEPALIVE_OPTIONS else None,
            'socket_connect_timeout': cls.REDIS_SOCKET_CONNECT_TIMEOUT,
            'socket_timeout': cls.REDIS_SOCKET_TIMEOUT,
            'health_check_interval': cls.REDIS_HEALTH_CHECK_INTERVAL,
            'retry_on_timeout': cls.REDIS_RETRY_ON_TIMEOUT,
            'decode_responses': True,
        }

# 环境变量覆盖
def load_config_from_env():
    """从环境变量加载配置"""
    config = {}
    
    # Redis配置
    if os.getenv('EASYTASK_REDIS_MAX_CONNECTIONS'):
        config['redis_max_connections'] = int(os.getenv('EASYTASK_REDIS_MAX_CONNECTIONS'))
    
    # 并发配置
    if os.getenv('EASYTASK_ASYNCIO_CONCURRENCY'):
        config['asyncio_concurrency'] = int(os.getenv('EASYTASK_ASYNCIO_CONCURRENCY'))
        
    if os.getenv('EASYTASK_PROCESS_CONCURRENCY'):
        config['process_concurrency'] = int(os.getenv('EASYTASK_PROCESS_CONCURRENCY'))
        
    if os.getenv('EASYTASK_THREAD_CONCURRENCY'):
        config['thread_concurrency'] = int(os.getenv('EASYTASK_THREAD_CONCURRENCY'))
    
    # 批处理配置
    if os.getenv('EASYTASK_BATCH_SIZE'):
        config['batch_size'] = int(os.getenv('EASYTASK_BATCH_SIZE'))
        
    if os.getenv('EASYTASK_PREFETCH_MULTIPLIER'):
        config['prefetch_multiplier'] = int(os.getenv('EASYTASK_PREFETCH_MULTIPLIER'))
    
    return config

# 全局配置实例
perf_config = PerformanceConfig()
env_config = load_config_from_env()