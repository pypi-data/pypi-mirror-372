from collections import deque
from abc import ABC, abstractmethod
import time
from typing import TYPE_CHECKING

from .common import CommonExecutorMixin

if TYPE_CHECKING:
    from ..core.app import Jettask


class BaseExecutor(CommonExecutorMixin, ABC):
    """Base class for all executors"""
    
    def __init__(self, event_queue: deque, app: "Jettask", concurrency: int = 1) -> None:
        self.event_queue = event_queue
        self.app = app
        self.concurrency = concurrency
        self.last_refresh_pending_time = 0
        self.pedding_count = 0
        self.batch_counter = 0

    def logic(self, *args, **kwargs):
        """Process a single task"""
        pass

    @abstractmethod
    def loop(self):
        """Main loop for the executor"""
        pass