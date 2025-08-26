import multiprocessing
import logging
import time
import os
import signal
from typing import Dict, List
from multiprocessing import Process, Event
from dataclasses import dataclass

from .base import BaseExecutor

logger = logging.getLogger('app')


@dataclass
class ProcessConfig:
    """Configuration for AsyncIO executor process"""
    executor_id: int
    redis_url: str
    queues: List[str]
    app_tasks: Dict
    consumer_strategy: str
    consumer_config: Dict
    max_connections: int
    prefetch_multiplier: int
    concurrency_per_process: int = 10000


class MultiAsyncioExecutor(BaseExecutor):
    """
    Multi-asyncio executor that manages multiple AsyncioExecutor instances
    Each instance runs in its own process with its own event loop
    
    Features:
    - Automatic process restart on failure
    - Graceful shutdown with timeout
    - Process health monitoring
    - Configurable concurrency per process
    """
    
    def __init__(self, event_queue, app, concurrency=3):
        super().__init__(event_queue, app, concurrency)
        self.processes: Dict[int, Process] = {}
        self.process_configs: Dict[int, ProcessConfig] = {}
        self.shutdown_event = Event()
        self._monitor_interval = 1  # seconds
        self._status_log_interval = 30  # seconds
        self._restart_delay = 2  # seconds
        self._max_restart_attempts = 3
        self._restart_counts: Dict[int, int] = {}
        self._main_received_signal = False  # Track if main process received signal
        
    def logic(self):
        """
        Logic method for BaseExecutor interface.
        Not used in MultiAsyncioExecutor as it delegates to AsyncioExecutor instances.
        """
        pass
        
    @staticmethod
    def _run_asyncio_executor(config: ProcessConfig, shutdown_event):
        """Run an AsyncioExecutor in a separate process"""
        # Set process name for debugging
        multiprocessing.current_process().name = f"AsyncioExecutor-{config.executor_id}"
        
        # Configure logging for subprocess
        logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s - %(levelname)s - [Executor-{config.executor_id}] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logger = logging.getLogger('app')
        
        # Handle signals gracefully
        def signal_handler(signum, _frame):
            logger.info(f"AsyncioExecutor #{config.executor_id} received signal {signum}")
            shutdown_event.set()
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Import inside process to avoid pickle issues
            from ..core.app import Jettask
            
            # Create app instance for this process
            app = Jettask(
                redis_url=config.redis_url,
                max_connections=config.max_connections,
                consumer_strategy=config.consumer_strategy,
                consumer_config=config.consumer_config,
                tasks=config.app_tasks
            )
            
            logger.info(f"Started AsyncioExecutor #{config.executor_id} in process {os.getpid()}")
            
            # Check shutdown event before starting
            if shutdown_event.is_set():
                logger.info(f"AsyncioExecutor #{config.executor_id} shutdown before start")
                return
            
            # Start the executor
            app._start(
                execute_type="asyncio",
                queues=config.queues,
                concurrency=config.concurrency_per_process,
                prefetch_multiplier=config.prefetch_multiplier
            )
            
        except KeyboardInterrupt:
            logger.info(f"AsyncioExecutor #{config.executor_id} received interrupt")
        except Exception as e:
            logger.error(f"AsyncioExecutor #{config.executor_id} error: {e}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise to trigger restart mechanism
        finally:
            logger.info(f"AsyncioExecutor #{config.executor_id} stopped")
    
    def _create_process_config(self, executor_id: int, queues: List[str], 
                              prefetch_multiplier: int) -> ProcessConfig:
        """Create configuration for a process"""
        return ProcessConfig(
            executor_id=executor_id,
            redis_url=self.app.redis_url,
            queues=queues,
            app_tasks=self.app._tasks,
            consumer_strategy=self.app.consumer_strategy,
            consumer_config=self.app.consumer_config,
            max_connections=self.app.max_connections,
            prefetch_multiplier=prefetch_multiplier,
            concurrency_per_process=10000
        )
    
    def _start_process(self, executor_id: int, config: ProcessConfig) -> Process:
        """Start a single AsyncioExecutor process"""
        process = Process(
            target=self._run_asyncio_executor,
            args=(config, self.shutdown_event),
            name=f"AsyncioExecutor-{executor_id}"
        )
        process.start()
        logger.info(f"Started AsyncioExecutor process #{executor_id} (PID: {process.pid})")
        return process
    
    def _restart_process(self, executor_id: int):
        """Restart a failed process with exponential backoff"""
        if self.shutdown_event.is_set():
            return
            
        restart_count = self._restart_counts.get(executor_id, 0)
        if restart_count >= self._max_restart_attempts:
            logger.error(f"Process #{executor_id} exceeded max restart attempts ({self._max_restart_attempts})")
            return
            
        self._restart_counts[executor_id] = restart_count + 1
        delay = self._restart_delay * (2 ** restart_count)  # Exponential backoff
        
        logger.info(f"Restarting process #{executor_id} (attempt {restart_count + 1}/{self._max_restart_attempts}) "
                   f"after {delay}s delay")
        time.sleep(delay)
        
        config = self.process_configs[executor_id]
        process = self._start_process(executor_id, config)
        self.processes[executor_id] = process
    
    def _monitor_processes(self):
        """Monitor process health and restart failed processes"""
        alive_count = 0
        for executor_id, process in list(self.processes.items()):
            if process.is_alive():
                alive_count += 1
                # Reset restart count for healthy processes
                self._restart_counts[executor_id] = 0
            else:
                exit_code = process.exitcode
                # 如果正在关闭，不要重启进程
                if self.shutdown_event.is_set():
                    logger.info(f"Process #{executor_id} stopped during shutdown")
                # 如果进程收到SIGTERM（exit_code == -15）或SIGINT（exit_code == -2），认为是正常关闭
                elif exit_code == -15 or exit_code == -2:
                    logger.info(f"Process #{executor_id} received termination signal, marking as shutdown")
                    # 设置shutdown事件，避免重启其他进程
                    self.shutdown_event.set()
                # 如果所有进程都同时停止（正常退出），认为是收到了关闭信号
                elif exit_code == 0 or exit_code is None:
                    # 如果主进程已经收到信号，不要重启
                    if self._main_received_signal:
                        logger.info(f"Process #{executor_id} stopped after main received signal")
                    else:
                        # 检查是否所有进程都停止了
                        all_stopped = True
                        for _, p in self.processes.items():
                            if p.is_alive():
                                all_stopped = False
                                break
                        
                        if all_stopped:
                            logger.info(f"All processes stopped simultaneously, marking as shutdown")
                            self.shutdown_event.set()
                        else:
                            logger.warning(f"Process #{executor_id} stopped unexpectedly with exit code {exit_code}")
                            self._restart_process(executor_id)
                else:
                    logger.warning(f"Process #{executor_id} exited with code {exit_code}")
                    self._restart_process(executor_id)
        
        return alive_count
    
    def loop(self):
        """Main loop that starts and monitors AsyncioExecutor processes"""
        logger.info(f"Starting MultiAsyncioExecutor with {self.concurrency} asyncio processes")
        
        # Set up signal handler to track when main process receives signal
        def signal_handler(signum, frame):
            logger.info(f"MultiAsyncioExecutor received signal {signum}")
            self._main_received_signal = True
            self.shutdown_event.set()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Get configuration
            queues = getattr(self.app.ep, 'queues', ['robust_bench'])
            prefetch_multiplier = getattr(self, 'prefetch_multiplier', 100)
            
            # Start AsyncioExecutor processes
            for i in range(self.concurrency):
                config = self._create_process_config(i, queues, prefetch_multiplier)
                self.process_configs[i] = config
                
                process = self._start_process(i, config)
                self.processes[i] = process
                
                # Small delay to avoid thundering herd
                time.sleep(0.1)
            
            logger.info(f"All {self.concurrency} AsyncioExecutor processes started")
            
            # Monitor executor processes
            last_status_log = time.time()
            
            while not self.shutdown_event.is_set():
                # Monitor process health
                alive_count = self._monitor_processes()
                
                if alive_count == 0:
                    if self._main_received_signal or self.shutdown_event.is_set():
                        logger.info("All AsyncioExecutor processes have stopped during shutdown")
                    else:
                        logger.error("All AsyncioExecutor processes have stopped unexpectedly")
                    break
                
                # Log status periodically
                current_time = time.time()
                if current_time - last_status_log > self._status_log_interval:
                    dead_count = self.concurrency - alive_count
                    logger.info(f"MultiAsyncioExecutor status - Active: {alive_count}/{self.concurrency}, "
                              f"Dead: {dead_count}, Restart attempts: {sum(self._restart_counts.values())}")
                    last_status_log = current_time
                
                time.sleep(self._monitor_interval)
                
        except KeyboardInterrupt:
            logger.info("MultiAsyncioExecutor received KeyboardInterrupt")
            self._main_received_signal = True
            self.shutdown_event.set()
        except Exception as e:
            logger.error(f"MultiAsyncioExecutor error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown all executor processes"""
        logger.info("Shutting down MultiAsyncioExecutor...")
        
        # Signal shutdown - this prevents any restart attempts
        self.shutdown_event.set()
        
        # 快速关闭模式 - 减少等待时间
        shutdown_timeout = 1.0  # 减少到1秒
        terminate_timeout = 0.5  # 减少到0.5秒
        
        # 先发送终止信号给所有进程
        for executor_id, process in self.processes.items():
            if process.is_alive():
                logger.info(f"Sending TERM signal to process #{executor_id} (PID: {process.pid})")
                process.terminate()
        
        # 短暂等待所有进程自行退出
        time.sleep(shutdown_timeout)
        
        # 强制杀死仍在运行的进程
        for executor_id, process in self.processes.items():
            if process.is_alive():
                logger.warning(f"Process #{executor_id} did not terminate, killing...")
                process.kill()
                # 不再等待join，让操作系统清理
        
        # Clear process tracking
        self.processes.clear()
        self.process_configs.clear()
        self._restart_counts.clear()
        
        logger.info("MultiAsyncioExecutor shutdown complete")