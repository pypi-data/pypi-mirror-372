import time
import traceback
from ..utils.serializer import dumps_str, loads_str
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
from ..utils.traceback_filter import filter_framework_traceback

if TYPE_CHECKING:
    from ..core.app import Jettask
    from ..core.task import Task


class CommonExecutorMixin:
    """Mixin class containing common functionality for all executors"""
    
    app: "Jettask"
    last_refresh_pending_time: float
    pedding_count: int
    
    def parse_task_data(self, data: bytes) -> Tuple[str, str, str, list, dict]:
        """Parse task data from bytes"""
        data_str = data.decode("utf-8")
        parts = data_str.split("_____", 4)
        event_id = parts[0]
        task_name = parts[1]
        trigger_time = parts[2]
        args = loads_str(parts[3]) if parts[3] else []
        kwargs = loads_str(parts[4]) if parts[4] else {}
        return event_id, task_name, trigger_time, args, kwargs
    
    def get_task(self, task_name: str) -> Optional["Task"]:
        """Get task by name"""
        return self.app.get_task_by_name(task_name)
    
    def handle_task_error(self, event_id: str, task_name: str, error: Exception) -> Dict[str, Any]:
        """Handle task execution error"""
        # 使用过滤后的堆栈信息
        error_msg = filter_framework_traceback()
        result = {
            "status": "error",
            "task_name": task_name,
            "message": str(error),
            "traceback": error_msg
        }
        self.app.set_task_status(event_id, "error")
        self.app.set_data(event_id, dumps_str(result))
        return result
    
    def handle_task_success(self, event_id: str, task_name: str, result: Any) -> Dict[str, Any]:
        """Handle successful task execution"""
        result_data = {
            "status": "success",
            "task_name": task_name,
            "result": result
        }
        self.app.set_task_status(event_id, "success")
        self.app.set_data(event_id, dumps_str(result_data))
        return result_data
    
    def ack_message(self, data: bytes) -> None:
        """Acknowledge message processing"""
        self.app.ep.ack(data)
    
    def get_routing_data(self, kwargs: dict) -> Tuple[Optional[str], Optional[str]]:
        """Extract routing data from kwargs"""
        routing_key = kwargs.pop("routing_key", None)
        aggregation_key = kwargs.pop("aggregation_key", None)
        return routing_key, aggregation_key
    
    def should_process_routing(self, routing_key: Optional[str], aggregation_key: Optional[str]) -> bool:
        """Check if task should be processed based on routing"""
        if routing_key:
            # Check solo running state
            if self.app.is_solo_running_by_aggregation_key(aggregation_key):
                return False
            # Set solo running state
            self.app.set_solo_running_by_aggregation_key(aggregation_key)
        return True
    
    def clear_routing_state(self, routing_key: Optional[str], aggregation_key: Optional[str]) -> None:
        """Clear routing state after task completion"""
        if routing_key:
            self.app.clear_solo_running_by_aggregation_key(aggregation_key)
    
    def handle_urgent_retry(self, kwargs: dict, event_id: str, task_name: str, 
                          trigger_time: str, args: list) -> bool:
        """Handle urgent retry logic"""
        urgent_retry = kwargs.pop("urgent_retry", None)
        if urgent_retry:
            delay = kwargs.pop("delay", 0)
            self.app.delay(
                task_name=task_name,
                delay=delay,
                args=args,
                kwargs=kwargs,
                task_id=event_id,
                trigger_time=trigger_time,
                producer_type="urgent_retry",
            )
            self.app.set_task_status(event_id, "retry")
            return True
        return False
    
    def get_pending_count(self) -> int:
        """Get pending count with caching"""
        current_time = time.time()
        if current_time - self.last_refresh_pending_time > 1:
            self.pedding_count = self.app.ep.get_pending_count()
            self.last_refresh_pending_time = current_time
        return self.pedding_count
    
    def execute_task_lifecycle(self, task: "Task", event_id: str, trigger_time: str,
                             args: list, kwargs: dict, is_async: bool = False):
        """Execute task with lifecycle methods"""
        # This method will be implemented differently for sync/async executors
        raise NotImplementedError("Subclasses must implement execute_task_lifecycle")
    
    def format_batch_data(self, data: bytes) -> Tuple[str, str, list, dict]:
        """Parse batch task data"""
        data_str = data.decode("utf-8")
        parts = data_str.split("_____", 3)
        batch_id = parts[0]
        task_name = parts[1]
        args = loads_str(parts[2]) if parts[2] else []
        kwargs = loads_str(parts[3]) if parts[3] else {}
        return batch_id, task_name, args, kwargs
    
    def extract_batch_params(self, kwargs: dict) -> Tuple[list, list, str, Optional[str], Optional[str]]:
        """Extract batch-specific parameters from kwargs"""
        event_ids = kwargs.pop("event_ids", [])
        trigger_times = kwargs.pop("trigger_times", [])
        producer_type = kwargs.pop("producer_type", "normal")
        routing_key = kwargs.pop("routing_key", None)
        aggregation_key = kwargs.pop("aggregation_key", None)
        return event_ids, trigger_times, producer_type, routing_key, aggregation_key
    
    def ack_batch_events(self, event_ids: list) -> None:
        """Acknowledge multiple events in batch"""
        for event_id in event_ids:
            data = f"{event_id}_____batch_ack".encode()
            self.ack_message(data)
    
    def update_batch_status(self, event_ids: list, status: str, result: Any = None) -> None:
        """Update status for multiple events in batch"""
        result_str = dumps_str(result) if result is not None else None
        for event_id in event_ids:
            self.app.set_task_status(event_id, status)
            if result_str:
                self.app.set_data(event_id, result_str)