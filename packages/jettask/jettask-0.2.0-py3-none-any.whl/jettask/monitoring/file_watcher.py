import time
import logging
from typing import TYPE_CHECKING
from watchdog.events import FileSystemEventHandler

if TYPE_CHECKING:
    from ..core.app import Jettask

logger = logging.getLogger('app')


class FileChangeHandler(FileSystemEventHandler):
    """监听文件变化的处理程序"""
    
    def __init__(self, app: "Jettask", **kwargs) -> None:
        super().__init__()
        self.app = app
        self.kwargs = kwargs
        self.last_modified = 0
        self.interval = 1  # 设置时间间隔为1秒

    def on_modified(self, event):
        current_time = time.time()
        if (
            event.src_path.endswith(".py")
            and current_time - self.last_modified > self.interval
        ):
            logging.warning(
                f'StatReload detected file change in "{event.src_path}". Reloading...'
            )
            try:
                self.app.process.terminate()
                self.app.process.join()
                self.app.clear()
                self.app.process = self.app._run_subprocess(**self.kwargs)
                self.last_modified = current_time
            except ImportError as e:
                logging.error(f"Error reloading: {e}")