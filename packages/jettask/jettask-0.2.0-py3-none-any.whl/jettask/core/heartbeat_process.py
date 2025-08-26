"""
独立的心跳上报进程，避免被CPU密集型任务阻塞
"""
import multiprocessing
import time
import os
import logging
import signal
import redis
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)


class HeartbeatProcess:
    """独立的心跳上报进程"""
    
    def __init__(self, redis_url: str, worker_key: str, consumer_id: str, 
                 heartbeat_interval: float = 5.0, heartbeat_timeout: float = 15.0):
        self.redis_url = redis_url
        self.worker_key = worker_key
        self.consumer_id = consumer_id
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.process: Optional[multiprocessing.Process] = None
        self.stop_event = multiprocessing.Event()
        # 使用共享内存记录最后心跳时间
        self.last_heartbeat_time = multiprocessing.Value('d', time.time())
        
    def start(self):
        """启动心跳进程"""
        if self.process and self.process.is_alive():
            logger.warning("Heartbeat process already running")
            return
            
        self.stop_event.clear()
        self.process = multiprocessing.Process(
            target=self._heartbeat_loop,
            args=(self.redis_url, self.worker_key, self.consumer_id, 
                  self.heartbeat_interval, self.heartbeat_timeout, self.stop_event,
                  self.last_heartbeat_time),
            daemon=True,
            name=f"heartbeat-{self.consumer_id}"
        )
        self.process.start()
        logger.debug(f"Started heartbeat process for {self.consumer_id}, PID: {self.process.pid}")
        
    def stop(self):
        """停止心跳进程"""
        if not self.process:
            return
            
        try:
            # 检查process是否有必要的属性
            if hasattr(self.process, 'is_alive') and callable(self.process.is_alive):
                if self.process.is_alive():
                    self.stop_event.set()
                    if hasattr(self.process, 'terminate'):
                        self.process.terminate()
                        self.process.join(timeout=5)
                        if self.process.is_alive():
                            logger.warning("Heartbeat process did not stop gracefully, forcing kill")
                            if hasattr(self.process, 'kill'):
                                self.process.kill()
                                self.process.join()
                    logger.debug(f"Stopped heartbeat process for {self.consumer_id}")
            else:
                logger.debug(f"Heartbeat process for {self.consumer_id} is not a valid process object")
        except AttributeError as e:
            logger.debug(f"Heartbeat process attributes error: {e}")
        except Exception as e:
            logger.warning(f"Error stopping heartbeat process: {e}")
        finally:
            self.process = None
    
    def get_last_heartbeat_time(self) -> float:
        """获取最后一次心跳时间"""
        with self.last_heartbeat_time.get_lock():
            return self.last_heartbeat_time.value
            
    @staticmethod
    def _heartbeat_loop(redis_url: str, worker_key: str, consumer_id: str,
                        heartbeat_interval: float, heartbeat_timeout: float, 
                        stop_event: multiprocessing.Event,
                        last_heartbeat_time: multiprocessing.Value):
        """心跳循环 - 在独立进程中运行"""
        # 忽略中断信号，让主进程处理
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        
        # 创建独立的Redis连接
        redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # 获取主机信息
        import socket
        try:
            hostname = socket.gethostname()
            if not hostname or hostname == 'localhost':
                hostname = socket.gethostbyname(socket.gethostname())
        except:
            hostname = os.environ.get('HOSTNAME', 'unknown')
            
        logger.debug(f"Heartbeat process started for {consumer_id} in PID {os.getpid()}")
        
        heartbeat_count = 0
        last_log_time = time.time()
        
        while not stop_event.is_set():
            try:
                current_time = time.time()
                
                # 更新心跳信息
                redis_client.hset(worker_key, mapping={
                    'last_heartbeat': str(current_time),
                    'heartbeat_pid': str(os.getpid()),  # 记录心跳进程PID
                    'is_alive': 'true'
                })
                
                # 同时更新 sorted set
                redis_prefix = worker_key.split(':')[0]  # 获取前缀（如 'jettask'）
                worker_id = worker_key.split(':')[-1]  # 获取 worker ID
                redis_client.zadd(f"{redis_prefix}:ACTIVE_WORKERS", {worker_id: current_time})
                
                # 更新本地心跳时间记录
                with last_heartbeat_time.get_lock():
                    last_heartbeat_time.value = current_time
                
                heartbeat_count += 1
                
                # 每30秒记录一次日志
                if current_time - last_log_time >= 30:
                    logger.debug(f"Heartbeat process for {consumer_id} sent {heartbeat_count} heartbeats")
                    last_log_time = current_time
                    heartbeat_count = 0
                
                # 等待下一次心跳
                stop_event.wait(heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat process for {consumer_id}: {e}")
                time.sleep(1)  # 出错时短暂等待
                
        logger.debug(f"Heartbeat process for {consumer_id} exiting")


class HeartbeatProcessManager:
    """管理worker的心跳进程（只需要一个进程）"""
    
    def __init__(self, redis_url: str, consumer_id: str, heartbeat_interval: float = 5.0,
                 heartbeat_timeout: float = 15.0):
        self.redis_url = redis_url
        self.consumer_id = consumer_id
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.heartbeat_process: Optional[HeartbeatProcess] = None
        self.worker_key: Optional[str] = None
        self.queues: Set[str] = set()  # 记录worker处理的队列
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
    def add_queue(self, queue: str, worker_key: str):
        """添加队列（只在第一次时启动心跳进程）"""
        self.queues.add(queue)
        
        # 只需要启动一次心跳进程
        if self.heartbeat_process is not None:
            logger.debug(f"Heartbeat process already running, added queue {queue}")
            return
            
        # 第一次调用时启动心跳进程
        self.worker_key = worker_key
        self.heartbeat_process = HeartbeatProcess(
            redis_url=self.redis_url,
            worker_key=worker_key,
            consumer_id=self.consumer_id,
            heartbeat_interval=self.heartbeat_interval,
            heartbeat_timeout=self.heartbeat_timeout
        )
        self.heartbeat_process.start()
        logger.debug(f"Started single heartbeat process for worker {self.consumer_id}")
        
    def remove_queue(self, queue: str):
        """移除队列"""
        if queue in self.queues:
            self.queues.remove(queue)
            logger.debug(f"Removed queue {queue} from heartbeat monitoring")
            
            # 如果没有队列了，停止心跳进程
            if not self.queues and self.heartbeat_process:
                self.heartbeat_process.stop()
                self.heartbeat_process = None
                logger.debug("No more queues, stopped heartbeat process")
            
    def stop_all(self):
        """停止心跳进程"""
        if self.heartbeat_process:
            self.heartbeat_process.stop()
            self.heartbeat_process = None
        self.queues.clear()
        
    def is_healthy(self) -> bool:
        """检查心跳进程是否健康"""
        if not self.heartbeat_process:
            return len(self.queues) == 0  # 如果没有队列，则是健康的
            
        if not self.heartbeat_process.process or not self.heartbeat_process.process.is_alive():
            logger.error(f"Heartbeat process for worker {self.consumer_id} is not alive")
            return False
        return True
    
    def get_last_heartbeat_time(self) -> Optional[float]:
        """获取最后一次心跳时间"""
        if self.heartbeat_process:
            return self.heartbeat_process.get_last_heartbeat_time()
        return None
    
    def is_heartbeat_timeout(self) -> bool:
        """检查心跳是否已超时"""
        last_heartbeat = self.get_last_heartbeat_time()
        if last_heartbeat is None:
            return False  # 心跳进程未启动
        
        current_time = time.time()
        return (current_time - last_heartbeat) > self.heartbeat_timeout