"""SQLAlchemy models for JetTask WebUI database."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, JSON, 
    ARRAY, UniqueConstraint, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


class Task(Base):
    """任务表模型"""
    __tablename__ = 'tasks'
    
    id = Column(String(255), primary_key=True)  # Redis Stream的事件ID
    queue_name = Column(String(255), nullable=False)
    task_name = Column(String(255), nullable=False)
    task_data = Column(JSONB)  # 任务的原始数据
    priority = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retry = Column(Integer, default=3)
    status = Column(String(50), default='pending')  # pending, running, success, failed, timeout
    result = Column(JSONB)  # 执行结果
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    worker_id = Column(String(255))
    execution_time = Column(Float)  # 任务执行时间（秒）
    duration = Column(Float)  # 任务总持续时间（秒）
    task_metadata = Column('metadata', JSONB)  # 额外的元数据，在数据库中仍叫metadata
    
    __table_args__ = (
        Index('idx_tasks_queue_name', 'queue_name'),
        Index('idx_tasks_status', 'status'),
        # 组合索引：优化按队列和状态查询
        Index('idx_tasks_queue_status', 'queue_name', 'status'),
        # 时间索引：优化时间范围查询
        Index('idx_tasks_created_at', 'created_at'),
        # Worker索引：优化查询特定worker的任务
        Index('idx_tasks_worker_id', 'worker_id', 
              postgresql_where=(worker_id.isnot(None))),
    )


# QueueStats 和 Worker 表已废弃，不再使用