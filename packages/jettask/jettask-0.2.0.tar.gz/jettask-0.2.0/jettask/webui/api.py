import asyncio
import json
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketState
from redis import asyncio as aioredis
import uvicorn
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.dialects import postgresql

from jettask.webui.pg_consumer import PostgreSQLConsumer
from jettask.webui.config import PostgreSQLConfig, RedisConfig
from jettask.webui.models import Base, Task, QueueStats, Worker

logger = logging.getLogger(__name__)

# SQLAlchemy异步引擎和会话（独立于consumer）
async_engine = None
AsyncSessionLocal = None

def parse_iso_datetime(time_str: str) -> datetime:
    """解析ISO格式的时间字符串，确保返回 UTC 时间"""
    if time_str.endswith('Z'):
        # Z 表示 UTC 时间
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    else:
        dt = datetime.fromisoformat(time_str)
    
    # 如果没有时区信息，假定为 UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # 如果有时区信息，转换为 UTC
    elif dt.tzinfo != timezone.utc:
        dt = dt.astimezone(timezone.utc)
    
    return dt

async def get_db_engine():
    """获取SQLAlchemy异步引擎（用于读取数据）"""
    global async_engine, AsyncSessionLocal
    
    if async_engine:
        return async_engine
    
    # 尝试从环境变量或配置获取PostgreSQL连接信息
    import os
    
    pg_config = PostgreSQLConfig.from_env()
    
    if not pg_config.dsn:
        logger.warning("PostgreSQL connection not configured")
        return None
    
    try:
        # 将 DSN 转换为 SQLAlchemy 格式
        # 如果是 postgresql:// 开头，改为 postgresql+psycopg://
        if pg_config.dsn.startswith('postgresql://'):
            dsn = pg_config.dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            dsn = pg_config.dsn
            
        async_engine = create_async_engine(
            dsn,
            pool_size=10,
            max_overflow=5,
            pool_pre_ping=True,
            echo=False
        )
        
        # 创建异步会话工厂
        AsyncSessionLocal = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("SQLAlchemy async engine created for WebUI")
        return async_engine
    except Exception as e:
        logger.error(f"Failed to create SQLAlchemy async engine: {e}")
        return None

async def get_db_session():
    """获取数据库会话"""
    if not AsyncSessionLocal:
        await get_db_engine()
    
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            yield session
    else:
        yield None

class RedisMonitor:
    def __init__(self, redis_url: str = "redis://localhost:6379", redis_prefix: str = "jettask"):
        self.redis_url = redis_url
        self.redis_prefix = redis_prefix
        self.redis: Optional[aioredis.Redis] = None
        self.scanner_task: Optional[asyncio.Task] = None
        self.scanner_interval = 5  # 5秒扫描一次
        self.default_heartbeat_timeout = 30  # 默认30秒心跳超时
        self._queues_cache = None
        self._queues_cache_time = 0
        self._queues_cache_ttl = 60  # 缓存60秒
        self._workers_cache = None
        self._workers_cache_time = 0
        self._workers_cache_ttl = 5  # worker缓存5秒，因为更新频繁
        self._scanner_running = False  # 标记扫描器是否正在运行
        
    async def connect(self):
        # 使用项目中的连接池模式，优化连接参数
        pool = aioredis.ConnectionPool.from_url(
            self.redis_url,
            decode_responses=True,
            max_connections=100,  # 增加最大连接数
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_connect_timeout=5,  # 减少连接超时时间
            socket_timeout=10,  # 设置socket超时
            health_check_interval=30
        )
        self.redis = aioredis.Redis(connection_pool=pool)
        
    async def close(self):
        # 停止扫描器任务
        if self.scanner_task and not self.scanner_task.done():
            self.scanner_task.cancel()
            try:
                await self.scanner_task
            except asyncio.CancelledError:
                pass
        
        if self.redis:
            await self.redis.close()
    
    def get_prefixed_queue_name(self, queue_name: str) -> str:
        """为队列名称添加前缀"""
        return f"{self.redis_prefix}:QUEUE:{queue_name}"
  
            
    async def get_task_info(self, event_id: str) -> Dict[str, Any]:
        """获取任务详细信息"""
        status_key = f"{self.redis_prefix}:STATUS:{event_id}"
        result_key = f"{self.redis_prefix}:RESULT:{event_id}"
        
        status = await self.redis.get(status_key)
        result = await self.redis.get(result_key)
        
        task_info = {
            "event_id": event_id,
            "status": status,
            "result": result
        }
        
        # 如果有状态信息，尝试从对应的队列stream中获取详细信息
        if status:
            try:
                status_data = json.loads(status)
                queue_name = status_data.get("queue")
                
                if queue_name:
                    # 从stream中查找该任务
                    # 使用 xrange 扫描最近的消息
                    prefixed_queue_name = self.get_prefixed_queue_name(queue_name)
                    messages = await self.redis.xrange(prefixed_queue_name, count=1000)
                    
                    for msg_id, data in messages:
                        # 检查消息数据中的event_id是否匹配
                        if (data.get("event_id") == event_id or 
                            data.get("id") == event_id or
                            data.get("task_id") == event_id):
                            task_info["stream_data"] = {
                                "message_id": msg_id,
                                "data": data,
                                "queue": queue_name
                            }
                            break
                    
                    # 如果消息ID就是event_id，直接尝试获取
                    if not task_info.get("stream_data"):
                        try:
                            direct_messages = await self.redis.xrange(
                                prefixed_queue_name, 
                                min=event_id, 
                                max=event_id, 
                                count=1
                            )
                            if direct_messages:
                                msg_id, data = direct_messages[0]
                                task_info["stream_data"] = {
                                    "message_id": msg_id,
                                    "data": data,
                                    "queue": queue_name
                                }
                        except:
                            pass
                            
            except Exception as e:
                print(f"Error parsing status for task {event_id}: {e}")
                
        return task_info
        
    async def get_stream_info(self, queue_name: str, event_id: str) -> Optional[Dict[str, Any]]:
        """从Stream中获取任务详细信息"""
        try:
            prefixed_queue_name = self.get_prefixed_queue_name(queue_name)
            # 先尝试按event_id直接查找
            messages = await self.redis.xrange(prefixed_queue_name, min=event_id, max=event_id, count=1)
            if messages:
                msg_id, data = messages[0]
                return {
                    "message_id": msg_id,
                    "data": data,
                    "queue": queue_name
                }
            
            # 如果没找到，可能event_id是消息内容的一部分，扫描最近的消息
            messages = await self.redis.xrange(prefixed_queue_name, count=100)
            for msg_id, data in messages:
                if data.get("event_id") == event_id or data.get("id") == event_id:
                    return {
                        "message_id": msg_id,
                        "data": data,
                        "queue": queue_name
                    }
        except Exception as e:
            print(f"Error reading from stream {prefixed_queue_name}: {e}")
        return None
        
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务状态"""
        tasks = []
        
        # 扫描所有状态键
        cursor = 0
        pattern = f"{self.redis_prefix}:STATUS:*"
        
        while True:
            cursor, keys = await self.redis.scan(
                cursor, match=pattern, count=100
            )
            
            for status_key in keys:
                event_id = status_key.split(":")[-1]
                task_info = await self.get_task_info(event_id)
                
                # 尝试获取Stream信息
                # 这里需要知道任务所在的队列，可能需要从状态信息中解析
                if task_info.get("status"):
                    try:
                        status_data = json.loads(task_info["status"])
                        queue_name = status_data.get("queue")
                        if queue_name:
                            stream_info = await self.get_stream_info(queue_name, event_id)
                            if stream_info:
                                task_info["stream_info"] = stream_info
                    except:
                        pass
                        
                tasks.append(task_info)
                
            if cursor == 0:
                break
                
        return tasks
    
    async def get_queue_tasks(self, queue_name: str, start_time: Optional[str] = None, 
                             end_time: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """获取指定队列的任务（基于时间范围）
        
        Args:
            queue_name: 队列名称
            start_time: 开始时间（Redis Stream ID格式或时间戳）
            end_time: 结束时间（Redis Stream ID格式或时间戳）
            limit: 返回的最大任务数
        """
        all_tasks = []
        
        try:
            # 处理时间参数
            # 如果没有指定结束时间，使用 '+' 表示到最新
            if not end_time:
                end_time = '+'
            
            # 如果没有指定开始时间，使用 '-' 表示从最早开始
            if not start_time:
                start_time = '-'
                
            # 从队列的stream中读取消息
            # 使用 xrevrange 按时间倒序获取（最新的在前）
            prefixed_queue_name = self.get_prefixed_queue_name(queue_name)
            messages = await self.redis.xrevrange(
                prefixed_queue_name, 
                max=end_time,
                min=start_time,
                count=limit
            )
            
            for msg_id, data in messages:
                # 在easy_task中，event_id就是Redis生成的stream消息ID
                event_id = msg_id
                
                # 构建任务信息
                task_info = {
                    "event_id": event_id,
                    "message_id": msg_id,
                    "stream_data": data,
                    "task_name": data.get("name", "unknown"),
                    "queue": data.get("queue", queue_name),
                    "trigger_time": data.get("trigger_time")
                }
                
                # 尝试解析args和kwargs，并组合成参数字符串
                params_str = ""
                try:
                    args_list = []
                    kwargs_dict = {}
                    
                    if data.get("args"):
                        args_list = json.loads(data["args"])
                        task_info["args"] = args_list
                    
                    if data.get("kwargs"):
                        kwargs_dict = json.loads(data["kwargs"])
                        task_info["kwargs"] = kwargs_dict
                    
                    # 构建参数字符串
                    params_parts = []
                    if args_list:
                        params_parts.extend([str(arg) for arg in args_list])
                    if kwargs_dict:
                        params_parts.extend([f"{k}={v}" for k, v in kwargs_dict.items()])
                    
                    params_str = ", ".join(params_parts) if params_parts else "无参数"
                    
                except Exception as e:
                    params_str = "解析失败"
                    
                task_info["params_str"] = params_str
                
                # 从状态键获取信息（不默认获取结果）
                status_key = f"{self.redis_prefix}:STATUS:{event_id}"
                
                # 获取状态
                status = await self.redis.get(status_key)
                
                if status:
                    task_info["status"] = status
                    try:
                        parsed_status = json.loads(status)
                        task_info["parsed_status"] = parsed_status
                        # 从状态中获取消费者信息
                        task_info["consumer"] = parsed_status.get("consumer", "-")
                    except:
                        task_info["parsed_status"] = {"status": "unknown"}
                        task_info["consumer"] = "-"
                else:
                    # 如果没有状态，显示未知
                    task_info["status"] = json.dumps({
                        "status": "未知", 
                        "queue": queue_name,
                        "created_at": datetime.fromtimestamp(float(data.get("trigger_time", 0))).isoformat() if data.get("trigger_time") else None
                    })
                    task_info["parsed_status"] = {
                        "status": "未知", 
                        "queue": queue_name,
                        "created_at": datetime.fromtimestamp(float(data.get("trigger_time", 0))).isoformat() if data.get("trigger_time") else None
                    }
                    task_info["consumer"] = "-"
                
                all_tasks.append(task_info)
                
        except Exception as e:
            print(f"Error reading queue {queue_name}: {e}")
            # 如果stream不存在或出错，返回空结果
            return {
                "tasks": [],
                "count": 0,
                "oldest_id": None,
                "newest_id": None,
                "has_more": False,
                "limit": limit
            }
        
        # 获取最早和最晚的消息ID用于分页导航
        oldest_id = all_tasks[-1]["message_id"] if all_tasks else None
        newest_id = all_tasks[0]["message_id"] if all_tasks else None
        
        # 检查是否还有更多数据
        has_more = len(messages) >= limit
        
        # 获取队列总长度
        total_count = 0
        try:
            queue_info = await self.redis.xinfo_stream(prefixed_queue_name)
            total_count = queue_info.get("length", 0)
        except Exception as e:
            print(f"Error getting queue info for {queue_name}: {e}")
            total_count = len(all_tasks)
        
        return {
            "tasks": all_tasks,
            "count": len(all_tasks),
            "total_count": total_count,
            "oldest_id": oldest_id,
            "newest_id": newest_id,
            "has_more": has_more,
            "limit": limit
        }
        
    async def get_worker_heartbeats(self, queue_name: str) -> List[Dict[str, Any]]:
        """获取指定队列的Worker心跳信息 - 直接扫描WORKER键"""
        worker_list = []
        current_time = datetime.now(timezone.utc).timestamp()
        
        # 直接扫描所有WORKER键（排除HISTORY相关的键）
        pattern = f"{self.redis_prefix}:WORKER:*"
        cursor = 0
        worker_keys = []
        
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            # 过滤掉HISTORY相关的键
            for key in keys:
                if ':HISTORY:' not in key:
                    worker_keys.append(key)
            if cursor == 0:
                break
        
        # 批量获取所有worker数据
        if worker_keys:
            pipe = self.redis.pipeline()
            for key in worker_keys:
                pipe.hgetall(key)
            all_workers_data = await pipe.execute()
            
            for i, worker_data in enumerate(all_workers_data):
                if not worker_data:
                    continue
                
                # 检查worker是否属于指定队列
                worker_queues = worker_data.get('queues', '')
                if queue_name not in worker_queues.split(','):
                    continue
                
                worker_id = worker_keys[i].split(':')[-1]
                last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                consumer_id = worker_data.get('consumer_id', worker_id)
                
                # 构建显示数据
                display_data = {
                    'consumer_id': consumer_id,
                    'consumer_name': f"{consumer_id}-{queue_name}",  # 保持兼容性
                    'host': worker_data.get('host', 'unknown'),
                    'pid': int(worker_data.get('pid', 0)),
                    'queue': queue_name,
                    'last_heartbeat': last_heartbeat,
                    'last_heartbeat_time': datetime.fromtimestamp(last_heartbeat).isoformat(),
                    'seconds_ago': int(current_time - last_heartbeat),
                    'is_alive': is_alive,
                    # 队列特定的统计信息
                    'success_count': int(worker_data.get(f'{queue_name}:success_count', 0)),
                    'failed_count': int(worker_data.get(f'{queue_name}:failed_count', 0)),
                    'total_count': int(worker_data.get(f'{queue_name}:total_count', 0)),
                    'running_tasks': int(worker_data.get(f'{queue_name}:running_tasks', 0)),
                    'avg_processing_time': float(worker_data.get(f'{queue_name}:avg_processing_time', 0.0)),
                    'avg_latency_time': float(worker_data.get(f'{queue_name}:avg_latency_time', 0.0))
                }
                
                # 如果离线时间存在，添加离线时间信息
                if 'offline_time' in worker_data:
                    display_data['offline_time'] = float(worker_data['offline_time'])
                    display_data['offline_time_formatted'] = datetime.fromtimestamp(float(worker_data['offline_time'])).isoformat()
                
                worker_list.append(display_data)
                
        return worker_list
    
    async def get_queue_worker_summary(self, queue_name: str) -> Dict[str, Any]:
        """获取队列的worker汇总统计信息"""
        try:
            # 直接扫描所有WORKER键并过滤（排除HISTORY相关的键）
            pattern = f"{self.redis_prefix}:WORKER:*"
            cursor = 0
            worker_keys = []
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                # 过滤掉HISTORY相关的键
                for key in keys:
                    if ':HISTORY:' not in key:
                        worker_keys.append(key)
                if cursor == 0:
                    break
            
            if not worker_keys:
                return {
                    'total_workers': 0,
                    'online_workers': 0,
                    'offline_workers': 0,
                    'total_success_count': 0,
                    'total_failed_count': 0,
                    'total_count': 0,
                    'total_running_tasks': 0,
                    'avg_processing_time': 0.0,
                'avg_latency_time': 0.0
                }
            
            # 批量获取worker数据
            pipe = self.redis.pipeline()
            for key in worker_keys:
                pipe.hgetall(key)
            all_workers_data = await pipe.execute()
            
            # 过滤属于该队列的worker
            queue_workers_data = []
            for i, worker_data in enumerate(all_workers_data):
                if worker_data and queue_name in worker_data.get('queues', '').split(','):
                    queue_workers_data.append(worker_data)
            
            # 汇总统计
            total_workers = len(queue_workers_data)
            online_workers = 0
            offline_workers = 0
            total_success_count = 0
            total_failed_count = 0
            total_count = 0
            total_running_tasks = 0
            total_processing_time = 0.0
            processing_time_count = 0
            total_latency_time = 0.0
            latency_time_count = 0
            
            current_time = datetime.now(timezone.utc).timestamp()
            offline_worker_ids = []  # 记录离线worker的ID，避免从历史中重复统计
            
            for worker_data in queue_workers_data:
                try:
                    # 检查worker状态
                    last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                    is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                    worker_id = worker_data.get('consumer_id', '')
                    
                    if is_alive and (current_time - last_heartbeat) < 30:
                        online_workers += 1
                        # 只统计在线worker的数据
                        success_count = int(worker_data.get(f'{queue_name}:success_count', 0))
                        failed_count = int(worker_data.get(f'{queue_name}:failed_count', 0))
                        running_tasks = int(worker_data.get(f'{queue_name}:running_tasks', 0))
                        avg_processing_time = float(worker_data.get(f'{queue_name}:avg_processing_time', 0.0))
                        avg_latency_time = float(worker_data.get(f'{queue_name}:avg_latency_time', 0.0))
                        
                        total_success_count += success_count
                        total_failed_count += failed_count
                        total_count += success_count + failed_count
                        total_running_tasks += running_tasks
                        
                        if avg_processing_time > 0:
                            total_processing_time += avg_processing_time
                            processing_time_count += 1
                        
                        if avg_latency_time > 0:
                            total_latency_time += avg_latency_time
                            latency_time_count += 1
                    else:
                        offline_workers += 1
                        # 记录离线worker的ID，从历史中统计
                        if worker_id:
                            offline_worker_ids.append(worker_id)
                        
                except Exception as e:
                    print(f"Error processing worker summary: {e}")
                    continue
            
            # 统计离线worker的数据（从WORKER键中）
            for worker_data in queue_workers_data:
                try:
                    # 检查是否是离线worker
                    is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                    worker_id = worker_data.get('consumer_id', '')
                    
                    if not is_alive and worker_id in offline_worker_ids:
                        # 统计离线worker的数据
                        success_count = int(worker_data.get(f'{queue_name}:success_count', 0))
                        failed_count = int(worker_data.get(f'{queue_name}:failed_count', 0))
                        
                        total_success_count += success_count
                        total_failed_count += failed_count
                        total_count += success_count + failed_count
                        
                        # 处理时间统计
                        avg_processing_time = float(worker_data.get(f'{queue_name}:avg_processing_time', 0.0))
                        if avg_processing_time > 0:
                            total_processing_time += avg_processing_time
                            processing_time_count += 1
                        
                        # 延迟时间统计
                        avg_latency_time = float(worker_data.get(f'{queue_name}:avg_latency_time', 0.0))
                        if avg_latency_time > 0:
                            total_latency_time += avg_latency_time
                            latency_time_count += 1
                            
                except Exception as e:
                    print(f"Error processing offline worker stats: {e}")
                    continue
            
            # 计算平均处理时间（包含历史）
            overall_avg_processing_time = 0.0
            if processing_time_count > 0:
                overall_avg_processing_time = total_processing_time / processing_time_count
            
            # 计算平均延迟时间
            overall_avg_latency_time = 0.0
            if latency_time_count > 0:
                overall_avg_latency_time = total_latency_time / latency_time_count
            
            return {
                'total_workers': total_workers,
                'online_workers': online_workers,
                'offline_workers': offline_workers,
                'total_success_count': total_success_count,
                'total_failed_count': total_failed_count,
                'total_count': total_count,
                'total_running_tasks': total_running_tasks,
                'avg_processing_time': round(overall_avg_processing_time, 3),
                'avg_latency_time': round(overall_avg_latency_time, 3),
                'history_included': True
            }
            
        except Exception as e:
            print(f"Error getting queue worker summary for {queue_name}: {e}")
            return {
                'total_workers': 0,
                'online_workers': 0,
                'offline_workers': 0,
                'total_success_count': 0,
                'total_failed_count': 0,
                'total_count': 0,
                'total_running_tasks': 0,
                'avg_processing_time': 0.0,
                'avg_latency_time': 0.0
            }
    
    async def get_queue_worker_summary_fast(self, queue_name: str) -> Dict[str, Any]:
        """获取队列的worker汇总统计信息（快速版，不包含历史）"""
        try:
            # 直接扫描所有WORKER键（排除HISTORY相关的键）
            pattern = f"{self.redis_prefix}:WORKER:*"
            cursor = 0
            worker_keys = []
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                # 过滤掉HISTORY相关的键
                for key in keys:
                    if ':HISTORY:' not in key:
                        worker_keys.append(key)
                if cursor == 0:
                    break
            
            if not worker_keys:
                return {
                    'total_workers': 0,
                    'online_workers': 0,
                    'offline_workers': 0,
                    'total_success_count': 0,
                    'total_failed_count': 0,
                    'total_count': 0,
                    'total_running_tasks': 0,
                    'avg_processing_time': 0.0,
                'avg_latency_time': 0.0
                }
            
            # 使用pipeline批量获取worker数据
            pipe = self.redis.pipeline()
            for worker_key in worker_keys:
                pipe.hgetall(worker_key)
            
            all_workers_data = await pipe.execute()
            
            # 过滤属于该队列的worker
            worker_data_list = []
            for worker_data in all_workers_data:
                if worker_data and queue_name in worker_data.get('queues', '').split(','):
                    worker_data_list.append(worker_data)
            
            # 汇总统计
            total_workers = len(worker_data_list)
            online_workers = 0
            offline_workers = 0
            total_success_count = 0
            total_failed_count = 0
            total_count = 0
            total_running_tasks = 0
            total_processing_time = 0.0
            processing_time_count = 0
            total_latency_time = 0.0
            latency_time_count = 0
            
            current_time = datetime.now(timezone.utc).timestamp()
            
            for worker_data in worker_data_list:
                if not worker_data:
                    continue
                
                # 检查worker状态
                last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                
                if is_alive and (current_time - last_heartbeat) < 30:
                    online_workers += 1
                    # 只统计在线worker的数据（快速版不包含历史，所以只统计在线的）
                    success_count = int(worker_data.get(f'{queue_name}:success_count', 0))
                    failed_count = int(worker_data.get(f'{queue_name}:failed_count', 0))
                    running_tasks = int(worker_data.get(f'{queue_name}:running_tasks', 0))
                    avg_processing_time = float(worker_data.get(f'{queue_name}:avg_processing_time', 0.0))
                    avg_latency_time = float(worker_data.get(f'{queue_name}:avg_latency_time', 0.0))
                    
                    total_success_count += success_count
                    total_failed_count += failed_count
                    total_count += success_count + failed_count
                    total_running_tasks += running_tasks
                    
                    if avg_processing_time > 0:
                        total_processing_time += avg_processing_time
                        processing_time_count += 1
                    
                    if avg_latency_time > 0:
                        total_latency_time += avg_latency_time
                        latency_time_count += 1
                else:
                    offline_workers += 1
                    # 快速版不统计离线worker的数据
            
            # 计算平均处理时间
            avg_processing_time = 0.0
            if processing_time_count > 0:
                avg_processing_time = total_processing_time / processing_time_count
            
            # 计算平均延迟时间
            avg_latency_time = 0.0
            if latency_time_count > 0:
                avg_latency_time = total_latency_time / latency_time_count
            
            return {
                'total_workers': total_workers,
                'online_workers': online_workers,
                'offline_workers': offline_workers,
                'total_success_count': total_success_count,
                'total_failed_count': total_failed_count,
                'total_count': total_count,
                'total_running_tasks': total_running_tasks,
                'avg_processing_time': round(avg_processing_time, 3),
                'avg_latency_time': round(avg_latency_time, 3)
            }
            
        except Exception as e:
            print(f"Error getting queue worker summary for {queue_name}: {e}")
            return {
                'total_workers': 0,
                'online_workers': 0,
                'offline_workers': 0,
                'total_success_count': 0,
                'total_failed_count': 0,
                'total_count': 0,
                'total_running_tasks': 0,
                'avg_processing_time': 0.0,
                'avg_latency_time': 0.0
            }
    
    async def get_worker_offline_history(self, limit: int = 100, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取worker下线历史记录 - 直接从WORKER键读取离线worker信息"""
        try:
            # 扫描所有WORKER键（排除HISTORY相关的键）
            pattern = f"{self.redis_prefix}:WORKER:*"
            cursor = 0
            worker_keys = []
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                # 过滤掉HISTORY相关的键（虽然已经不再创建，但以防万一）
                for key in keys:
                    if ':HISTORY:' not in key:
                        worker_keys.append(key)
                if cursor == 0:
                    break
            
            if not worker_keys:
                return []
            
            # 批量获取所有worker数据
            pipe = self.redis.pipeline()
            for key in worker_keys:
                pipe.hgetall(key)
            all_workers_data = await pipe.execute()
            
            # 收集离线的worker
            offline_workers = []
            current_time = time.time()
            
            for i, worker_data in enumerate(all_workers_data):
                if not worker_data:
                    continue
                
                # 检查是否离线
                is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                if not is_alive and 'offline_time' in worker_data:
                    offline_time = float(worker_data.get('offline_time', 0))
                    
                    # 时间范围过滤
                    if start_time and offline_time < start_time:
                        continue
                    if end_time and offline_time > end_time:
                        continue
                    
                    # 计算运行时长
                    online_time = float(worker_data.get('created_at', offline_time))
                    duration_seconds = int(offline_time - online_time)
                    
                    # 构建离线记录
                    record = {
                        'consumer_id': worker_data.get('consumer_id', ''),
                        'host': worker_data.get('host', 'unknown'),
                        'pid': int(worker_data.get('pid', 0)),
                        'queues': worker_data.get('queues', ''),
                        'online_time': online_time,
                        'offline_time': offline_time,
                        'duration_seconds': duration_seconds,
                        'last_heartbeat': float(worker_data.get('last_heartbeat', 0)),
                        'shutdown_reason': worker_data.get('shutdown_reason', 'unknown'),
                        'online_time_str': datetime.fromtimestamp(online_time).isoformat(),
                        'offline_time_str': datetime.fromtimestamp(offline_time).isoformat(),
                    }
                    
                    # 格式化运行时长
                    hours = duration_seconds // 3600
                    minutes = (duration_seconds % 3600) // 60
                    seconds = duration_seconds % 60
                    record['duration_str'] = f"{hours}h {minutes}m {seconds}s"
                    
                    # 添加统计信息（聚合所有队列的数据）
                    queues = worker_data.get('queues', '').split(',') if worker_data.get('queues') else []
                    total_success = 0
                    total_failed = 0
                    total_count = 0
                    
                    for queue in queues:
                        if queue.strip():
                            queue = queue.strip()
                            total_success += int(worker_data.get(f'{queue}:success_count', 0))
                            total_failed += int(worker_data.get(f'{queue}:failed_count', 0))
                            total_count += int(worker_data.get(f'{queue}:total_count', 0))
                    
                    record['total_success_count'] = total_success
                    record['total_failed_count'] = total_failed
                    record['total_count'] = total_count
                    record['total_running_tasks'] = 0  # 离线worker没有运行中的任务
                    
                    # 计算平均处理时间
                    if total_count > 0:
                        total_processing_time = 0.0
                        for queue in queues:
                            if queue.strip():
                                queue = queue.strip()
                                avg_time = float(worker_data.get(f'{queue}:avg_processing_time', 0))
                                count = int(worker_data.get(f'{queue}:total_count', 0))
                                if avg_time > 0 and count > 0:
                                    total_processing_time += avg_time * count
                        record['avg_processing_time'] = total_processing_time / total_count
                    else:
                        record['avg_processing_time'] = 0.0
                    
                    offline_workers.append((offline_time, record))
            
            # 按离线时间倒序排序
            offline_workers.sort(key=lambda x: x[0], reverse=True)
            
            # 返回指定数量的记录
            return [record for _, record in offline_workers[:limit]]
            
        except Exception as e:
            print(f"Error getting worker offline history: {e}")
            return []
    
    async def get_global_stats_with_history(self) -> Dict[str, Any]:
        """获取全局统计信息（优化版）- 注：不再重复统计历史数据"""
        try:
            # 获取所有队列
            queues = await self.get_all_queues()
            
            # 并行获取所有队列的汇总信息和队列统计
            queue_summaries_task = asyncio.gather(
                *[self.get_queue_worker_summary_fast(queue) for queue in queues],
                return_exceptions=True
            )
            queue_stats_task = asyncio.gather(
                *[self.get_queue_stats(queue) for queue in queues],
                return_exceptions=True
            )
            
            queue_summaries, queue_stats = await asyncio.gather(
                queue_summaries_task, queue_stats_task
            )
            
            # 初始化统计
            total_success = 0
            total_failed = 0
            total_tasks = 0
            total_running = 0
            total_workers = 0
            online_workers = 0
            offline_workers = 0
            total_processing_time = 0.0
            total_processing_count = 0
            total_latency_time = 0.0
            total_latency_count = 0
            
            # RabbitMQ风格指标
            total_messages = 0
            total_messages_ready = 0
            total_messages_unacknowledged = 0
            total_consumers = 0
            total_publish = 0
            total_deliver_get = 0
            total_ack = 0
            
            # 汇总统计信息
            for i, summary in enumerate(queue_summaries):
                if isinstance(summary, Exception):
                    print(f"Error getting stats for queue {queues[i]}: {summary}")
                    continue
                    
                total_workers += summary.get('total_workers', 0)
                online_workers += summary.get('online_workers', 0)
                offline_workers += summary.get('offline_workers', 0)
                total_success += summary.get('total_success_count', 0)
                total_failed += summary.get('total_failed_count', 0)
                total_tasks += summary.get('total_count', 0)
                total_running += summary.get('total_running_tasks', 0)
                
                # 累加平均处理时间（需要根据任务数加权）
                avg_time = summary.get('avg_processing_time', 0)
                task_count = summary.get('total_count', 0)
                if avg_time > 0 and task_count > 0:
                    total_processing_time += avg_time * task_count
                    total_processing_count += task_count
                
                # 累加平均延迟时间
                avg_latency = summary.get('avg_latency_time', 0)
                if avg_latency > 0 and task_count > 0:
                    total_latency_time += avg_latency * task_count
                    total_latency_count += task_count
            
            # 汇总RabbitMQ风格指标
            for i, stats in enumerate(queue_stats):
                if isinstance(stats, Exception):
                    continue
                    
                total_messages += stats.get('messages', 0)
                total_messages_ready += stats.get('messages_ready', 0)
                total_messages_unacknowledged += stats.get('messages_unacknowledged', 0)
                total_consumers += stats.get('consumers', 0)
                
                message_stats = stats.get('message_stats', {})
                total_publish += message_stats.get('publish', 0)
                total_deliver_get += message_stats.get('deliver_get', 0)
                total_ack += message_stats.get('ack', 0)
            
            # 计算全局平均处理时间
            global_avg_processing_time = 0.0
            if total_processing_count > 0:
                global_avg_processing_time = total_processing_time / total_processing_count
            
            # 计算全局平均延迟时间
            global_avg_latency_time = 0.0
            if total_latency_count > 0:
                global_avg_latency_time = total_latency_time / total_latency_count
            
            return {
                # 原有指标
                'total_queues': len(queues),
                'total_workers': total_workers,
                'online_workers': online_workers,
                'offline_workers': offline_workers,
                'total_success_count': total_success,
                'total_failed_count': total_failed,
                'total_count': total_tasks,
                'total_running_tasks': total_running,
                'avg_processing_time': round(global_avg_processing_time, 3),
                'avg_latency_time': round(global_avg_latency_time, 3),
                'history_included': False,
                # RabbitMQ风格指标
                'messages': total_messages,
                'messages_ready': total_messages_ready,
                'messages_unacknowledged': total_messages_unacknowledged,
                'consumers': total_consumers,
                'message_stats': {
                    'publish': total_publish,
                    'deliver_get': total_deliver_get,
                    'ack': total_ack
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"Error getting global stats: {e}")
            return {
                'total_queues': 0,
                'total_workers': 0,
                'online_workers': 0,
                'offline_workers': 0,
                'total_success_count': 0,
                'total_failed_count': 0,
                'total_count': 0,
                'total_running_tasks': 0,
                'avg_processing_time': 0.0,
                'avg_latency_time': 0.0,
                'history_included': False,
                'messages': 0,
                'messages_ready': 0,
                'messages_unacknowledged': 0,
                'consumers': 0,
                'message_stats': {
                    'publish': 0,
                    'deliver_get': 0,
                    'ack': 0
                },
                'error': str(e)
            }
        
    async def get_all_queues(self) -> List[str]:
        """获取所有队列名称 - 优先从global:queues集合获取，带缓存"""
        try:
            # 检查缓存是否有效
            current_time = time.time()
            if self._queues_cache is not None and (current_time - self._queues_cache_time) < self._queues_cache_ttl:
                return self._queues_cache
            
            # 优先尝试从全局队列集合获取
            global_queues_key = f'{self.redis_prefix}:global:queues'
            queues = await self.redis.smembers(global_queues_key)
            
            if queues:
                # 如果有全局队列集合，直接使用
                result = sorted(list(queues))
                self._queues_cache = result
                self._queues_cache_time = current_time
                return result
            
            # 如果没有全局队列集合，回退到扫描方式
            queues = set()
            
            # 优化：更精确的扫描模式，只扫描QUEUE:*键
            pattern = f"{self.redis_prefix}:QUEUE:*"
            cursor = 0
            
            # 使用pipeline批量检查类型
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=500)  # 增加扫描批次大小
                
                if keys:
                    # 批量检查键类型
                    pipe = self.redis.pipeline()
                    for key in keys:
                        pipe.type(key)
                    
                    types = await pipe.execute()
                    
                    for i, key in enumerate(keys):
                        if types[i] == 'stream':
                            # 提取队列名（去掉前缀）
                            if key.startswith(f"{self.redis_prefix}:QUEUE:"):
                                queue_name = key[len(f"{self.redis_prefix}:QUEUE:"):]
                                queues.add(queue_name)
                
                if cursor == 0:
                    break
            
            # 返回排序后的队列列表并更新缓存
            result = sorted(list(queues))
            self._queues_cache = result
            self._queues_cache_time = current_time
            return result
            
        except Exception as e:
            print(f"Error scanning queues: {e}")
            return []
        
    async def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """获取队列统计信息 (RabbitMQ兼容格式)"""
        prefixed_queue_name = self.get_prefixed_queue_name(queue_name)
        
        try:
            info = await self.redis.xinfo_stream(prefixed_queue_name)
            groups = await self.redis.xinfo_groups(prefixed_queue_name)
        except Exception as e:
            # 如果队列不存在，返回默认值
            return {
                "queue": queue_name,
                "messages": 0,
                "messages_ready": 0, 
                "messages_unacknowledged": 0,
                "consumers": 0,
                "message_stats": {
                    "publish": 0,
                    "deliver_get": 0,
                    "ack": 0
                },
                "consumer_groups": [],
                "error": str(e)
            }
        
        # 计算基础指标
        total_messages = info["length"]
        total_pending = 0
        total_consumers = 0
        total_delivered = 0
        
        consumer_groups_info = []
        
        for group in groups:
            group_pending = group["pending"]
            group_consumers_count = group["consumers"]
            
            total_pending += group_pending
            total_consumers += group_consumers_count
            
            group_info = {
                "name": group["name"],
                "consumers": group_consumers_count,
                "pending": group_pending,
                "last_delivered_id": group["last-delivered-id"]
            }
            
            # 获取消费者详情
            try:
                consumers = await self.redis.xinfo_consumers(prefixed_queue_name, group["name"])
                group_info["consumer_details"] = consumers
                
                # 从消费者统计中计算deliver和ack数量
                for consumer in consumers:
                    total_delivered += consumer.get("pel-count", 0)
                    
            except Exception as e:
                group_info["consumer_details"] = []
                print(f"Error getting consumers for group {group['name']}: {e}")
            
            consumer_groups_info.append(group_info)
        
        # 从Worker统计中获取更精确的消息统计
        worker_summary = await self.get_queue_worker_summary_fast(queue_name)
        publish_count = worker_summary.get('total_count', 0)  # 总处理数作为发布数的近似
        deliver_count = worker_summary.get('total_success_count', 0) + worker_summary.get('total_failed_count', 0)
        ack_count = worker_summary.get('total_success_count', 0)
        
        # 计算就绪消息数 (队列总长度 - 未确认消息数)
        messages_ready = max(0, total_messages - total_pending)
        
        # RabbitMQ风格的统计信息
        stats = {
            "queue": queue_name,
            # RabbitMQ兼容指标
            "messages": total_messages,  # 队列中消息总数
            "messages_ready": messages_ready,  # 就绪状态的消息数
            "messages_unacknowledged": total_pending,  # 未确认的消息数
            "consumers": total_consumers,  # 消费者数量
            "message_stats": {
                "publish": publish_count,  # 发布到队列的消息数量
                "deliver_get": deliver_count,  # 被消费的消息数量
                "ack": ack_count  # 被确认的消息数量
            },
            # 原有详细信息保持兼容性
            "length": info["length"],
            "first_entry": info.get("first-entry"),
            "last_entry": info.get("last-entry"),
            "consumer_groups": consumer_groups_info,
            # 额外的性能指标
            "performance_stats": {
                "avg_processing_time": worker_summary.get('avg_processing_time', 0.0),
                "avg_latency_time": worker_summary.get('avg_latency_time', 0.0),
                "total_running_tasks": worker_summary.get('total_running_tasks', 0)
            }
        }
        
        return stats
    
    async def _heartbeat_scanner(self):
        """心跳扫描器任务，定期检查worker心跳状态"""
        logger = logging.getLogger('webui.heartbeat')
        logger.info("心跳扫描器启动")
        
        while self._scanner_running:
            try:
                # 扫描所有worker
                pattern = f"{self.redis_prefix}:WORKER:*"
                cursor = 0
                worker_keys = []
                
                while True:
                    cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                    # 过滤掉HISTORY相关的键
                    for key in keys:
                        if ':HISTORY:' not in key:
                            worker_keys.append(key)
                    if cursor == 0:
                        break
                
                if worker_keys:
                    # 批量获取worker数据
                    pipe = self.redis.pipeline()
                    for key in worker_keys:
                        pipe.hgetall(key)
                    all_workers_data = await pipe.execute()
                    
                    current_time = time.time()
                    
                    # 检查每个worker的心跳
                    for i, worker_data in enumerate(all_workers_data):
                        if not worker_data:
                            continue
                        
                        try:
                            # 获取心跳相关信息
                            last_heartbeat = float(worker_data.get('last_heartbeat', 0))
                            is_alive = worker_data.get('is_alive', 'true').lower() == 'true'
                            heartbeat_timeout = float(worker_data.get('heartbeat_timeout', self.default_heartbeat_timeout))
                            consumer_id = worker_data.get('consumer_id', '')
                            
                            # 检查是否超时
                            if is_alive and (current_time - last_heartbeat) > heartbeat_timeout:
                                logger.info(f"Worker {consumer_id} 心跳超时，标记为离线")
                                
                                # 更新worker状态为离线
                                worker_key = worker_keys[i]
                                await self.redis.hset(worker_key, 'is_alive', 'false')
                                
                        except Exception as e:
                            logger.error(f"检查worker心跳时出错: {e}")
                
                # 等待下一次扫描
                await asyncio.sleep(self.scanner_interval)
                
            except asyncio.CancelledError:
                logger.info("心跳扫描器收到取消信号")
                break
            except Exception as e:
                logger.error(f"心跳扫描器出错: {e}")
                await asyncio.sleep(self.scanner_interval)
        
        logger.info("心跳扫描器已停止")
    
    async def start_heartbeat_scanner(self):
        """启动心跳扫描器"""
        if not self._scanner_running:
            self._scanner_running = True
            self.scanner_task = asyncio.create_task(self._heartbeat_scanner())
            logging.getLogger('webui').info("心跳扫描器任务已创建")
    
    async def stop_heartbeat_scanner(self):
        """停止心跳扫描器"""
        self._scanner_running = False
        if self.scanner_task and not self.scanner_task.done():
            self.scanner_task.cancel()
            try:
                await self.scanner_task
            except asyncio.CancelledError:
                pass

# 创建全局监控器实例
monitor = RedisMonitor()
pg_consumer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pg_consumer
    
    # Startup
    await monitor.connect()
    # 启动心跳扫描器
    await monitor.start_heartbeat_scanner()
    
    # 启动PostgreSQL消费者（如果配置了且显式启用）
    if hasattr(app.state, 'pg_config') and getattr(app.state, 'enable_consumer', False):
        redis_config = RedisConfig.from_env()
        pg_consumer = PostgreSQLConsumer(app.state.pg_config, redis_config)
        await pg_consumer.start()
        logging.info("PostgreSQL consumer started")
    else:
        logging.info("PostgreSQL consumer disabled (use --with-consumer to enable)")
    
    yield
    
    # Shutdown
    await monitor.stop_heartbeat_scanner()
    await monitor.close()
    
    # 停止PostgreSQL消费者
    if pg_consumer:
        await pg_consumer.stop()
    
    # 关闭SQLAlchemy引擎
    global async_engine
    if async_engine:
        await async_engine.dispose()
        async_engine = None
        logger.info("SQLAlchemy async engine closed")

app = FastAPI(title="Jettask Monitor", lifespan=lifespan)

@app.get("/api/tasks")
async def get_tasks():
    """获取所有任务"""
    tasks = await monitor.get_all_tasks()
    return {"tasks": tasks}

@app.get("/api/queue/{queue_name}/tasks")
async def get_queue_tasks(
    queue_name: str, 
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 50
):
    """获取指定队列的任务（基于时间范围）"""
    print(f'{queue_name=} {start_time=} {end_time=} {limit=}')
    result = await monitor.get_queue_tasks(queue_name, start_time, end_time, limit)
    return result

@app.get("/api/queue/{queue_name}/timeline/pg")
async def get_queue_timeline_from_pg(
    queue_name: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    interval: str = "5m"
):
    """从PostgreSQL获取队列任务的时间分布数据"""
    # 如果没有提供时间范围，默认最近1小时
    if not end_time:
        end_dt = datetime.now(timezone.utc)
    else:
        end_dt = parse_iso_datetime(end_time)
    
    if not start_time:
        start_dt = end_dt - timedelta(hours=1)
    else:
        start_dt = parse_iso_datetime(start_time)
    
    # 解析时间间隔
    interval_minutes = 5  # 默认5分钟
    if interval.endswith('m'):
        interval_minutes = int(interval[:-1])
    elif interval.endswith('h'):
        interval_minutes = int(interval[:-1]) * 60
    
    # 获取数据库引擎
    engine = await get_db_engine()
    if not engine:
        return {
            "timeline": [],
            "interval": interval,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "error": "PostgreSQL connection not configured"
        }
    
    try:
        async with AsyncSessionLocal() as session:
            # 使用 SQLAlchemy 的原生 SQL 查询（因为复杂的时间分组）
            query = text(f"""
            SELECT 
                DATE_TRUNC('minute', created_at) - 
                INTERVAL '{interval_minutes} minutes' * (EXTRACT(MINUTE FROM created_at)::int % {interval_minutes}) as time_bucket,
                COUNT(*) as count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                AVG(CASE WHEN status = 'completed' AND processing_time IS NOT NULL 
                    THEN processing_time ELSE NULL END) as avg_processing_time
            FROM tasks
            WHERE queue_name = :queue_name
                AND created_at >= :start_dt
                AND created_at < :end_dt
            GROUP BY time_bucket
            ORDER BY time_bucket
            """)
            
            result = await session.execute(query, {
                'queue_name': queue_name,
                'start_dt': start_dt,
                'end_dt': end_dt
            })
            rows = result.mappings().all()  # Use mappings() to get dict-like results
            
            # 构建时间轴数据
            timeline = []
            for row in rows:
                timeline.append({
                    "time": row['time_bucket'].isoformat(),
                    "count": row['count'],
                    "completed_count": row['completed_count'],
                    "failed_count": row['failed_count'],
                    "avg_processing_time": float(row['avg_processing_time']) if row['avg_processing_time'] else 0
                })
            
            # 填充缺失的时间点
            filled_timeline = []
            current_time = start_dt
            timeline_dict = {item['time']: item for item in timeline}
            
            while current_time < end_dt:
                time_key = current_time.isoformat()
                if time_key in timeline_dict:
                    filled_timeline.append(timeline_dict[time_key])
                else:
                    filled_timeline.append({
                        "time": time_key,
                        "count": 0,
                        "completed_count": 0,
                        "failed_count": 0,
                        "avg_processing_time": 0
                    })
                current_time += timedelta(minutes=interval_minutes)
            
            return {
                "timeline": filled_timeline,
                "interval": interval,
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error fetching timeline from PostgreSQL: {e}")
        return {
            "timeline": [],
            "interval": interval,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "error": str(e)
        }

@app.get("/api/queues/timeline/pg")
async def get_queues_timeline_from_pg(
    queues: str = Query(..., description="Comma-separated list of queue names"),
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """从PostgreSQL获取多个队列的任务时间分布数据"""
    # 解析队列列表
    if not queues or queues.strip() == "":
        # 如果没有提供队列，返回空结果
        # 计算默认时间范围
        end_dt = datetime.now(timezone.utc) if not end_time else parse_iso_datetime(end_time)
        start_dt = (end_dt - timedelta(hours=1)) if not start_time else parse_iso_datetime(start_time)
        
        return {
            "queues": [],
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "interval": interval,
            "message": "No queues selected"
        }
    
    queue_list = [q.strip() for q in queues.split(',') if q.strip()][:10]  # 最多10个队列
    
    # 如果没有提供时间范围，默认最近1小时
    if not end_time:
        end_dt = datetime.now(timezone.utc)
    else:
        end_dt = parse_iso_datetime(end_time)
    
    if not start_time:
        start_dt = end_dt - timedelta(hours=1)
    else:
        start_dt = parse_iso_datetime(start_time)
    
    logger.info(f'{start_dt=} {end_dt=}')
    
    # 根据时间范围自动计算合适的时间间隔
    duration = (end_dt - start_dt).total_seconds()
    
    # 动态计算时间间隔
    if duration <= 300:  # <= 5分钟
        interval_seconds = 0.5  # 500毫秒
        interval_type = 'millisecond'
        interval = '500ms'
    elif duration <= 900:  # <= 15分钟
        interval_seconds = 1  # 1秒
        interval_type = 'second'
        interval = '1s'
    elif duration <= 1800:  # <= 30分钟
        interval_seconds = 2  # 2秒
        interval_type = 'second'
        interval = '2s'
    elif duration <= 3600:  # <= 1小时
        interval_seconds = 30  # 30秒
        interval_type = 'second'
        interval = '30s'
    elif duration <= 10800:  # <= 3小时
        interval_seconds = 300  # 5分钟
        interval_type = 'minute'
        interval = '5m'
    elif duration <= 21600:  # <= 6小时
        interval_seconds = 600  # 10分钟
        interval_type = 'minute'
        interval = '10m'
    elif duration <= 43200:  # <= 12小时
        interval_seconds = 1800  # 30分钟
        interval_type = 'minute'
        interval = '30m'
    elif duration <= 86400:  # <= 24小时
        interval_seconds = 3600  # 1小时
        interval_type = 'hour'
        interval = '1h'
    elif duration <= 172800:  # <= 2天
        interval_seconds = 7200  # 2小时
        interval_type = 'hour'
        interval = '2h'
    elif duration <= 604800:  # <= 7天
        interval_seconds = 21600  # 6小时
        interval_type = 'hour'
        interval = '6h'
    else:  # > 7天
        interval_seconds = 86400  # 1天
        interval_type = 'hour'
        interval = '24h'
    
    # 转换为分钟数（用于兼容旧代码）
    interval_minutes = interval_seconds / 60
    
    logger.info(f"Time range: {duration}s, using interval: {interval} -> {interval_seconds} seconds, type: {interval_type}")
    
    # 获取数据库引擎
    engine = await get_db_engine()
    if not engine:
        return {
            "queues": [],
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "interval": interval,
            "error": "PostgreSQL connection not configured"
        }
    
    result = []
    
    for queue_name in queue_list:
        try:
            async with AsyncSessionLocal() as session:
                # 使用更简单直接的时间分组方法
                if interval_type == 'millisecond':
                    # 对于毫秒级别的间隔
                    query = text(f"""
                    SELECT 
                        DATE_TRUNC('second', created_at) + 
                        INTERVAL '{interval_seconds} seconds' * FLOOR(EXTRACT(MILLISECONDS FROM created_at) / ({interval_seconds} * 1000)) as time_bucket,
                        COUNT(*) as count
                    FROM tasks
                    WHERE queue_name = :queue_name
                        AND created_at >= :start_dt
                        AND created_at < :end_dt
                    GROUP BY time_bucket
                    ORDER BY time_bucket
                    """)
                elif interval_type == 'second':
                    # 对于秒级别的间隔
                    query = text(f"""
                    SELECT 
                        DATE_TRUNC('minute', created_at) + 
                        INTERVAL '{interval_seconds} seconds' * FLOOR(EXTRACT(SECOND FROM created_at) / {interval_seconds}) as time_bucket,
                        COUNT(*) as count
                    FROM tasks
                    WHERE queue_name = :queue_name
                        AND created_at >= :start_dt
                        AND created_at < :end_dt
                    GROUP BY time_bucket
                    ORDER BY time_bucket
                    """)
                elif interval_type == 'minute' and interval_minutes < 60:
                    # 对于分钟级别的间隔（小于1小时）
                    query = text(f"""
                    SELECT 
                        DATE_TRUNC('hour', created_at) + 
                        INTERVAL '{interval_minutes} minutes' * FLOOR(EXTRACT(MINUTE FROM created_at) / {interval_minutes}) as time_bucket,
                        COUNT(*) as count
                    FROM tasks
                    WHERE queue_name = :queue_name
                        AND created_at >= :start_dt
                        AND created_at < :end_dt
                    GROUP BY time_bucket
                    ORDER BY time_bucket
                    """)
                elif interval_minutes == 60:
                    # 对于1小时间隔，直接使用小时截断
                    query = text("""
                    SELECT 
                        DATE_TRUNC('hour', created_at) as time_bucket,
                        COUNT(*) as count
                    FROM tasks
                    WHERE queue_name = :queue_name
                        AND created_at >= :start_dt
                        AND created_at < :end_dt
                    GROUP BY time_bucket
                    ORDER BY time_bucket
                    """)
                else:
                    # 对于大于1小时的间隔，使用小时级别的计算
                    interval_hours = int(interval_minutes // 60)
                    query = text(f"""
                    SELECT 
                        DATE_TRUNC('day', created_at) + 
                        INTERVAL '{interval_hours} hours' * FLOOR(EXTRACT(HOUR FROM created_at) / {interval_hours}) as time_bucket,
                        COUNT(*) as count
                    FROM tasks
                    WHERE queue_name = :queue_name
                        AND created_at >= :start_dt
                        AND created_at < :end_dt
                    GROUP BY time_bucket
                    ORDER BY time_bucket
                    """)
                params = {
                    'queue_name': queue_name,
                    'start_dt': start_dt,
                    'end_dt': end_dt
                }

                # 先绑定参数
                bound_query = query.bindparams(**params)

                # 生成可直接执行的 SQL（带参数值）
                compiled_sql = bound_query.compile(
                    dialect=postgresql.dialect(),
                    compile_kwargs={"literal_binds": True}
                ).string
                compiled_sql = compiled_sql.replace("%%", "%")

                print("可直接复制到 Navicat 执行的 SQL：\n", compiled_sql)

                # 再执行
                result_obj = await session.execute(query, params)
                rows = result_obj.mappings().all()  # Use mappings() to get dict-like results
                logger.info(f'{rows=}')
                # 构建时间轴数据
                timeline = []
                for row in rows:
                    timeline.append({
                        "time": row['time_bucket'].isoformat(),
                        "count": row['count']
                    })
                
                # 填充缺失的时间点
                filled_timeline = []
                
                # 构建一个时间到数据的映射，用于快速查找
                # 由于可能存在时区或微小时间差异，我们需要更灵活的匹配
                timeline_data = []
                for item in timeline:
                    dt = datetime.fromisoformat(item['time'])
                    timeline_data.append((dt, item['count']))
                
                # 对timeline_data按时间排序
                timeline_data.sort(key=lambda x: x[0])
                
                # 生成完整的时间序列
                filled_timeline = []
                
                # 对齐到interval
                def align_to_interval(dt, interval_seconds):
                    """对齐时间到interval_seconds的整数倍"""
                    if interval_seconds >= 3600:  # 大于等于1小时
                        # 按小时对齐
                        dt = dt.replace(minute=0, second=0, microsecond=0)
                        interval_hours = interval_seconds // 3600
                        aligned_hour = (dt.hour // interval_hours) * interval_hours
                        return dt.replace(hour=aligned_hour)
                    elif interval_seconds >= 60:  # 大于等于1分钟
                        # 按分钟对齐
                        dt = dt.replace(second=0, microsecond=0)
                        interval_minutes = interval_seconds // 60
                        total_minutes = dt.hour * 60 + dt.minute
                        aligned_total_minutes = (total_minutes // interval_minutes) * interval_minutes
                        aligned_hour = aligned_total_minutes // 60
                        aligned_minute = aligned_total_minutes % 60
                        return dt.replace(hour=aligned_hour, minute=aligned_minute)
                    elif interval_seconds >= 1:  # 秒级别
                        # 按秒对齐
                        dt = dt.replace(microsecond=0)
                        aligned_second = int(dt.second // interval_seconds) * int(interval_seconds)
                        return dt.replace(second=aligned_second)
                    else:  # 毫秒级别
                        # 按毫秒对齐
                        total_ms = dt.microsecond / 1000  # 转换为毫秒
                        interval_ms = interval_seconds * 1000
                        aligned_ms = int(total_ms // interval_ms) * interval_ms
                        aligned_microsecond = int(aligned_ms * 1000)
                        return dt.replace(microsecond=aligned_microsecond)
                
                current_time = align_to_interval(start_dt, interval_seconds)
                
                # 用于追踪我们在timeline_data中的位置
                timeline_index = 0
                
                while current_time < end_dt:
                    # 查找是否有匹配的数据点
                    # 允许最多interval_seconds/2的误差
                    tolerance = timedelta(seconds=interval_seconds/2)
                    found = False
                    
                    # 从当前位置开始查找
                    while timeline_index < len(timeline_data):
                        data_time, count = timeline_data[timeline_index]
                        
                        # 计算时间差（秒）
                        time_diff = abs((data_time - current_time).total_seconds())
                        
                        if time_diff < interval_seconds / 2:
                            # 找到匹配的数据
                            filled_timeline.append({
                                "time": current_time.isoformat(),
                                "count": count
                            })
                            found = True
                            timeline_index += 1
                            break
                        elif data_time > current_time + tolerance:
                            # 数据时间已经超过当前时间太多，停止查找
                            break
                        else:
                            # 这个数据点太早了，继续查找下一个
                            timeline_index += 1
                    
                    if not found:
                        # 没有找到匹配的数据，填充0
                        filled_timeline.append({
                            "time": current_time.isoformat(),
                            "count": 0
                        })
                    
                    current_time += timedelta(seconds=interval_seconds)
                result.append({
                    "queue": queue_name,
                    "timeline": {
                        "timeline": filled_timeline,
                        "interval": interval
                    }
                })
                
        except Exception as e:
            logger.error(f"Error fetching timeline for queue {queue_name}: {e}")
            result.append({
                "queue": queue_name,
                "timeline": {
                    "timeline": [],
                    "interval": interval,
                    "error": str(e)
                }
            })
    # logger.info(f'{result=}')
    return {
        "queues": result,
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "interval": interval
    }

@app.get("/api/queue/{queue_name}/timeline")
async def get_queue_timeline(
    queue_name: str, 
    interval: str = "1m", 
    duration: str = "1h",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    context: str = "detail"  # 'overview' for homepage, 'detail' for queue detail page
):
    """获取队列任务的时间分布（用于时间轴）"""
    try:
        # 解析时间间隔和持续时间
        interval_seconds = parse_time_duration(interval)
        
        # 根据上下文设置不同的数据限制
        if context == "overview":
            # 首页概览：固定获取最近1小时的所有数据
            duration_seconds = 3600  # 1小时
            now = int(datetime.now(timezone.utc).timestamp() * 1000)
            start = now - duration_seconds * 1000
            min_id = f"{start}-0"
            max_id = "+"
            max_count = 100000  # 首页概览获取所有数据
        else:
            # 队列详情页：根据参数获取，但限制最多10000条
            if start_time and end_time:
                # 使用提供的时间范围
                min_id = start_time
                max_id = end_time if end_time != '+' else '+'
            else:
                # 使用duration参数计算时间范围
                duration_seconds = parse_time_duration(duration)
                now = int(datetime.now(timezone.utc).timestamp() * 1000)
                start = now - duration_seconds * 1000
                min_id = f"{start}-0"
                max_id = "+"
            max_count = 10000  # 详情页限制10000条
        
        # 获取指定时间范围内的消息
        prefixed_queue_name = monitor.get_prefixed_queue_name(queue_name)
        print(f'{prefixed_queue_name=} {min_id=} {max_id=} {max_count=}')
        messages = await monitor.redis.xrange(
            prefixed_queue_name,
            min=min_id,
            max=max_id,
            count=max_count
        )
        
        # 按时间间隔统计任务数量
        buckets = {}
        bucket_size = interval_seconds * 1000  # 转换为毫秒
        
        # 计算实际的时间范围用于生成时间轴
        if start_time and end_time:
            # 从参数中解析时间范围
            if start_time != '-':
                actual_start = int(start_time.split('-')[0])
            else:
                actual_start = int(datetime.now(timezone.utc).timestamp() * 1000) - 86400000  # 默认24小时前
            
            if end_time != '+':
                actual_end = int(end_time.split('-')[0])
            else:
                actual_end = int(datetime.now(timezone.utc).timestamp() * 1000)
        else:
            # 使用duration参数计算的时间范围
            actual_start = start
            actual_end = now
        
        for msg_id, _ in messages:
            # 从消息ID提取时间戳
            timestamp = int(msg_id.split('-')[0])
            bucket_key = (timestamp // bucket_size) * bucket_size
            buckets[bucket_key] = buckets.get(bucket_key, 0) + 1
        
        # 转换为时间序列数据
        timeline_data = []
        current_bucket = (actual_start // bucket_size) * bucket_size
        
        while current_bucket <= actual_end:
            timeline_data.append({
                "timestamp": current_bucket,
                "count": buckets.get(current_bucket, 0)
            })
            current_bucket += bucket_size
        
        # 计算实际任务总数
        total_tasks = len(messages)
        
        # 检查是否达到数据限制
        has_more = False
        if context == "detail" and total_tasks >= max_count:
            has_more = True
        
        return {
            "timeline": timeline_data,
            "interval": interval,
            "duration": duration,
            "start": actual_start,
            "end": actual_end,
            "total_tasks": total_tasks,  # 添加实际任务总数
            "message_count": len(messages),  # 实际获取到的消息数量
            "has_more": has_more,  # 是否还有更多数据
            "limit": max_count if context == "detail" else None  # 数据限制
        }
        
    except Exception as e:
        print(f"Error getting timeline for queue {queue_name}: {e}")
        return {
            "timeline": [],
            "error": str(e)
        }

def parse_time_duration(duration_str: str) -> int:
    """解析时间字符串为秒数 (如 '1h', '10m', '30s')"""
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    if duration_str[-1] in units:
        value = int(duration_str[:-1])
        unit = duration_str[-1]
        return value * units[unit]
    
    # 默认为秒
    return int(duration_str)

@app.get("/api/task/{event_id}/result")
async def get_task_result(event_id: str):
    """获取单个任务的结果"""
    result_key = f"{monitor.redis_prefix}:RESULT:{event_id}"
    result = await monitor.redis.get(result_key)
    return {"event_id": event_id, "result": result}

@app.get("/api/queues")
async def get_queues():
    """获取所有队列"""
    queues = await monitor.get_all_queues()
    return {"queues": queues}

@app.get("/api/queue/{queue_name}/stats")
async def get_queue_stats(queue_name: str):
    """获取队列统计信息"""
    try:
        stats = await monitor.get_queue_stats(queue_name)
        return stats
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/queue/{queue_name}/workers")
async def get_queue_workers(queue_name: str):
    """获取队列的Worker信息"""
    workers = await monitor.get_worker_heartbeats(queue_name)
    return {"queue": queue_name, "workers": workers}

@app.get("/api/queue/{queue_name}/worker-summary")
async def get_queue_worker_summary(queue_name: str):
    """获取队列的Worker汇总统计信息"""
    summary = await monitor.get_queue_worker_summary(queue_name)
    return {"queue": queue_name, "summary": summary}

@app.get("/api/workers/offline-history")
async def get_workers_offline_history(
    limit: int = 100,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None
):
    """获取所有worker的下线历史记录"""
    history = await monitor.get_worker_offline_history(limit, start_time, end_time)
    return {"history": history, "total": len(history)}

@app.get("/api/global-stats")
async def get_global_stats():
    """获取全局统计信息（包含历史记录）"""
    stats = await monitor.get_global_stats_with_history()
    return stats

@app.get("/api/global-stats/light")
async def get_global_stats_light():
    """获取轻量级全局统计信息（不包含历史记录）"""
    try:
        # 获取所有队列
        queues = await monitor.get_all_queues()
        
        # 并行获取所有队列的快速汇总和简单统计
        summaries_task = asyncio.gather(
            *[monitor.get_queue_worker_summary_fast(queue) for queue in queues],
            return_exceptions=True
        )
        
        # 获取基础队列信息（不获取完整stats以提高性能）
        queue_lengths_task = asyncio.gather(
            *[monitor.redis.xlen(monitor.get_prefixed_queue_name(queue)) for queue in queues],
            return_exceptions=True
        )
        
        summaries, queue_lengths = await asyncio.gather(
            summaries_task, queue_lengths_task
        )
        
        # 汇总数据
        total_workers = 0
        online_workers = 0
        total_running_tasks = 0
        total_messages = 0
        total_consumers = 0
        
        for summary in summaries:
            if not isinstance(summary, Exception):
                total_workers += summary.get('total_workers', 0)
                online_workers += summary.get('online_workers', 0)
                total_running_tasks += summary.get('total_running_tasks', 0)
                total_consumers += summary.get('total_workers', 0)  # 近似使用worker数作为消费者数
        
        # 汇总消息数
        for length in queue_lengths:
            if not isinstance(length, Exception):
                total_messages += length
        
        return {
            'total_queues': len(queues),
            'total_workers': total_workers,
            'online_workers': online_workers,
            'total_running_tasks': total_running_tasks,
            'messages': total_messages,
            'consumers': total_consumers,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'total_queues': 0,
            'total_workers': 0,
            'online_workers': 0,
            'total_running_tasks': 0,
            'messages': 0,
            'consumers': 0
        }


@app.get("/api/queue/{queue_name}/workers/offline-history")
async def get_queue_workers_offline_history(
    queue_name: str,
    limit: int = 100,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None
):
    """获取指定队列的worker下线历史记录"""
    # 获取所有历史记录，然后过滤出该队列的
    all_history = await monitor.get_worker_offline_history(limit * 10, start_time, end_time)
    queue_history = [
        record for record in all_history 
        if queue_name in record.get('queues', '').split(',')
    ][:limit]
    return {"queue": queue_name, "history": queue_history, "total": len(queue_history)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时更新（优化版）"""
    await websocket.accept()
    
    try:
        # 标记是否是首次连接
        is_first_load = True
        
        while True:
            try:
                # 检查WebSocket连接状态
                if websocket.client_state != WebSocketState.CONNECTED:
                    break
                    
                # 首次连接时发送基础信息
                if is_first_load:
                    # 只发送队列列表，不发送任务信息
                    data = {
                        "queues": await monitor.get_all_queues(),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "initial_load": True
                    }
                    await websocket.send_json(data)
                    is_first_load = False
                else:
                    # 后续更新：并行获取所有worker信息
                    queues = await monitor.get_all_queues()
                    
                    # 使用 asyncio.gather 并行获取所有队列的worker信息
                    worker_tasks = [monitor.get_worker_heartbeats(queue) for queue in queues]
                    worker_results = await asyncio.gather(*worker_tasks, return_exceptions=True)
                    
                    # 构建队列worker映射
                    queue_workers = {}
                    for i, queue in enumerate(queues):
                        if isinstance(worker_results[i], Exception):
                            print(f"Error getting workers for queue {queue}: {worker_results[i]}")
                            queue_workers[queue] = []
                        else:
                            queue_workers[queue] = worker_results[i]
                    
                    data = {
                        "queues": queues,
                        "workers": queue_workers,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "initial_load": False
                    }
                    
                    # 再次检查连接状态后发送
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_json(data)
                    else:
                        break
                
                await asyncio.sleep(2)  # 每2秒更新一次
                
            except WebSocketDisconnect:
                # WebSocket已断开，退出循环
                break
            except Exception as e:
                # 检查是否是因为连接已关闭导致的错误
                if "close message has been sent" in str(e) or "WebSocket is not connected" in str(e):
                    break
                print(f"Error in websocket loop: {e}")
                # 对于其他错误，等待一段时间后继续
                await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # 确保WebSocket正确关闭
        try:
            await websocket.close()
        except:
            pass

# 挂载静态文件
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def read_index():
    """返回主页HTML"""
    html_path = static_dir / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Jettask Monitor</h1><p>Static files not found</p>")

@app.get("/queue.html")
async def read_queue():
    """返回队列详情页HTML"""
    html_path = static_dir / "queue.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Queue Details</h1><p>Page not found</p>")

@app.get("/queues.html")
async def read_queues():
    """返回队列列表页HTML"""
    html_path = static_dir / "queues.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Queues</h1><p>Page not found</p>")

@app.get("/workers.html")
async def read_workers():
    """返回Workers页HTML"""
    html_path = static_dir / "workers.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Workers</h1><p>Page not found</p>")


# PostgreSQL相关的API端点
@app.get("/api/pg/tasks")
async def get_pg_tasks(
    status: Optional[str] = None,
    queue_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """从PostgreSQL获取任务列表"""
    engine = await get_db_engine()
    if not engine:
        return {"error": "PostgreSQL not configured"}
    
    try:
        async with AsyncSessionLocal() as session:
            # 构建查询
            query = select(Task)
            
            if status:
                query = query.where(Task.status == status)
                
            if queue_name:
                query = query.where(Task.queue_name == queue_name)
                
            query = query.order_by(Task.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            result = await session.execute(query)
            tasks_obj = result.scalars().all()
            
        tasks = []
        for task_obj in tasks_obj:
            task = {
                'id': task_obj.id,
                'queue_name': task_obj.queue_name,
                'task_name': task_obj.task_name,
                'task_data': task_obj.task_data,
                'priority': task_obj.priority,
                'retry_count': task_obj.retry_count,
                'max_retry': task_obj.max_retry,
                'status': task_obj.status,
                'result': task_obj.result,
                'error_message': task_obj.error_message,
                'created_at': task_obj.created_at,
                'started_at': task_obj.started_at,
                'completed_at': task_obj.completed_at,
                'worker_id': task_obj.worker_id,
                'execution_time': task_obj.execution_time,
                'duration': task_obj.duration,
                'metadata': task_obj.task_metadata,
                'next_sync_time': task_obj.next_sync_time,
                'sync_check_count': task_obj.sync_check_count
            }
            # 转换时间戳为ISO格式（确保是 UTC）
            for field in ['created_at', 'started_at', 'completed_at']:
                if task.get(field):
                    # PostgreSQL 的 TIMESTAMP WITH TIME ZONE 会返回 aware datetime
                    if task[field].tzinfo is None:
                        # 如果没有时区信息，假定为 UTC
                        task[field] = task[field].replace(tzinfo=timezone.utc)
                    task[field] = task[field].isoformat()
            # 解析JSON字段
            for field in ['task_data', 'result', 'metadata']:
                if task.get(field) and isinstance(task[field], str):
                    try:
                        task[field] = json.loads(task[field])
                    except:
                        pass
            tasks.append(task)
            
        return {"tasks": tasks, "total": len(tasks)}
        
    except Exception as e:
        logging.error(f"Error fetching tasks from PostgreSQL: {e}")
        return {"error": str(e)}


@app.get("/api/pg/stats")
async def get_pg_stats():
    """获取PostgreSQL中的统计信息"""
    engine = await get_db_engine()
    if not engine:
        return {"error": "PostgreSQL not configured"}
    
    try:
        async with AsyncSessionLocal() as session:
            # 获取任务统计
            task_stats_query = text("""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_tasks,
                    COUNT(CASE WHEN status = 'success' THEN 1 END) as completed_tasks,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tasks
                FROM tasks
            """)
            
            task_stats_result = await session.execute(task_stats_query)
            task_stats = task_stats_result.mappings().fetchone()
            
            # 获取队列统计
            queue_stats_query = text("""
                SELECT 
                    queue_name,
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_tasks,
                    COUNT(CASE WHEN status = 'success' THEN 1 END) as completed_tasks,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tasks
                FROM tasks
                GROUP BY queue_name
                ORDER BY total_tasks DESC
            """)
            
            queue_stats_result = await session.execute(queue_stats_query)
            queue_stats = queue_stats_result.mappings().all()
            
        return {
            "task_stats": dict(task_stats) if task_stats else {},
            "queue_stats": [dict(row) for row in queue_stats]
        }
        
    except Exception as e:
        logging.error(f"Error fetching stats from PostgreSQL: {e}")
        return {"error": str(e)}


@app.get("/api/pg/task/{task_id}")
async def get_pg_task(task_id: str):
    """从PostgreSQL获取单个任务的详细信息"""
    engine = await get_db_engine()
    if not engine:
        return {"error": "PostgreSQL not configured"}
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Task).where(Task.id == task_id))
            task_obj = result.scalar_one_or_none()
            
        if not task_obj:
            return {"error": "Task not found"}
            
        task = {
            'id': task_obj.id,
            'queue_name': task_obj.queue_name,
            'task_name': task_obj.task_name,
            'task_data': task_obj.task_data,
            'priority': task_obj.priority,
            'retry_count': task_obj.retry_count,
            'max_retry': task_obj.max_retry,
            'status': task_obj.status,
            'result': task_obj.result,
            'error_message': task_obj.error_message,
            'created_at': task_obj.created_at,
            'started_at': task_obj.started_at,
            'completed_at': task_obj.completed_at,
            'worker_id': task_obj.worker_id,
            'execution_time': task_obj.execution_time,
            'duration': task_obj.duration,
            'metadata': task_obj.task_metadata,
            'next_sync_time': task_obj.next_sync_time,
            'sync_check_count': task_obj.sync_check_count
        }
        # 转换时间戳为ISO格式（确保是 UTC）
        for field in ['created_at', 'started_at', 'completed_at']:
            if task.get(field):
                # PostgreSQL 的 TIMESTAMP WITH TIME ZONE 会返回 aware datetime
                if task[field].tzinfo is None:
                    # 如果没有时区信息，假定为 UTC
                    task[field] = task[field].replace(tzinfo=timezone.utc)
                task[field] = task[field].isoformat()
        # 解析JSON字段
        for field in ['task_data', 'result', 'metadata']:
            if task.get(field) and isinstance(task[field], str):
                try:
                    task[field] = json.loads(task[field])
                except:
                    pass
                    
        return {"task": task}
        
    except Exception as e:
        logging.error(f"Error fetching task from PostgreSQL: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    uvicorn.run(app, host="0.0.0.0", port=8000)