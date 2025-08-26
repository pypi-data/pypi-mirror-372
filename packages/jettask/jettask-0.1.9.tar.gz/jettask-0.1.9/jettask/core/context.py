"""
Task Context - FastAPI风格的依赖注入
"""

from typing import TYPE_CHECKING, Optional, Any
from dataclasses import dataclass

if TYPE_CHECKING:
    from .app import Jettask


@dataclass
class TaskContext:
    """
    任务上下文信息
    
    通过类型注解自动注入到任务函数中：
    
    @app.task
    async def my_task(ctx: TaskContext, data: dict):
        print(f"Task ID: {ctx.event_id}")
        print(f"Task Name: {ctx.name}")
        return data
    """
    event_id: str
    name: str
    trigger_time: float
    app: "Jettask"
    queue: Optional[str] = None
    worker_id: Optional[str] = None
    retry_count: int = 0
    
    def __repr__(self) -> str:
        return f"TaskContext(event_id={self.event_id}, name={self.name}, queue={self.queue})"