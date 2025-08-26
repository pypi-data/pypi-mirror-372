"""
独立的数据访问模块，不依赖 integrated_gradio_app.py
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 设置日志
logger = logging.getLogger(__name__)


class RedisConfig:
    """Redis配置"""
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
    
    @classmethod
    def from_env(cls):
        import os
        return cls(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD')
        )


class PostgreSQLConfig:
    """PostgreSQL配置"""
    def __init__(self, host='localhost', port=5432, user='postgres', password='', database='jettask'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
    
    @property
    def dsn(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @classmethod
    def from_env(cls):
        import os
        return cls(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            user=os.getenv('POSTGRES_USER', 'jettask'),
            password=os.getenv('POSTGRES_PASSWORD', '123456'),
            database=os.getenv('POSTGRES_DB', 'jettask')
        )


class JetTaskDataAccess:
    """JetTask数据访问类"""
    
    def __init__(self):
        self.redis_config = RedisConfig.from_env()
        self.pg_config = PostgreSQLConfig.from_env()
        self.redis_prefix = "jettask"
        self.async_engine = None
        self.AsyncSessionLocal = None
        self._redis_pool = None
        
    async def initialize(self):
        """初始化数据库连接"""
        try:
            # 初始化PostgreSQL引擎
            dsn = self.pg_config.dsn
            if dsn.startswith('postgresql://'):
                dsn = dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
            
            self.async_engine = create_async_engine(
                dsn,
                pool_size=10,
                max_overflow=5,
                pool_pre_ping=True,
                echo=False
            )
            
            self.AsyncSessionLocal = sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 初始化Redis连接池
            self._redis_pool = redis.ConnectionPool(
                host=self.redis_config.host,
                port=self.redis_config.port,
                db=self.redis_config.db,
                password=self.redis_config.password,
                encoding='utf-8',
                decode_responses=True
            )
            
            logger.info("数据库连接初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    async def close(self):
        """关闭数据库连接"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self._redis_pool:
            await self._redis_pool.disconnect()
    
    async def get_redis_client(self):
        """获取Redis客户端"""
        return redis.Redis(connection_pool=self._redis_pool)
    
    async def fetch_queues_data(self) -> List[Dict]:
        """获取队列数据（基于Redis Stream）"""
        try:
            redis_client = await self.get_redis_client()
            
            # 获取所有Stream类型的队列 - JetTask使用 jettask:QUEUE:队列名 格式
            all_keys = await redis_client.keys(f"{self.redis_prefix}:QUEUE:*")
            queues_data = []
            queue_names = set()
            
            for key in all_keys:
                # 检查是否是Stream类型
                key_type = await redis_client.type(key)
                if key_type == 'stream':
                    # 解析队列名称 - 格式: jettask:QUEUE:队列名
                    parts = key.split(':')
                    if len(parts) >= 3 and parts[0] == self.redis_prefix and parts[1] == 'QUEUE':
                        queue_name = ':'.join(parts[2:])  # 支持带冒号的队列名
                        queue_names.add(queue_name)
            
            # 获取每个队列的详细信息
            for queue_name in queue_names:
                stream_key = f"{self.redis_prefix}:QUEUE:{queue_name}"
                
                try:
                    # 获取Stream信息
                    stream_info = await redis_client.xinfo_stream(stream_key)
                    
                    # 获取消费者组信息
                    groups_info = await redis_client.xinfo_groups(stream_key)
                    
                    pending_count = 0
                    processing_count = 0
                    
                    # 统计各消费者组的待处理消息
                    for group in groups_info:
                        pending_count += group.get('pending', 0)
                        
                        # 获取消费者信息
                        try:
                            consumers = await redis_client.xinfo_consumers(stream_key, group['name'])
                            for consumer in consumers:
                                processing_count += consumer.get('pending', 0)
                        except:
                            pass
                    
                    # Stream的长度即为总消息数
                    total_messages = stream_info.get('length', 0)
                    
                    # 完成的消息数 = 总消息数 - 待处理 - 处理中
                    completed_count = max(0, total_messages - pending_count - processing_count)
                    
                    queues_data.append({
                        '队列名称': queue_name,
                        '待处理': pending_count,
                        '处理中': processing_count,
                        '已完成': completed_count,
                        '失败': 0,  # Stream中没有直接的失败计数
                        '总计': total_messages
                    })
                    
                except Exception as e:
                    logger.warning(f"获取队列 {queue_name} 信息失败: {e}")
                    # 如果获取详细信息失败，至少返回队列名称
                    queues_data.append({
                        '队列名称': queue_name,
                        '待处理': 0,
                        '处理中': 0,
                        '已完成': 0,
                        '失败': 0,
                        '总计': 0
                    })
            
            await redis_client.close()
            return sorted(queues_data, key=lambda x: x['队列名称'])
            
        except Exception as e:
            logger.error(f"获取队列数据失败: {e}")
            return []
    
    async def fetch_queue_timeline_data(self, 
                                      queues: List[str], 
                                      start_time: datetime, 
                                      end_time: datetime) -> List[Dict]:
        """获取队列时间线数据 - 返回真实的任务触发时间"""
        try:
            await asyncio.sleep(1)
            if not self.AsyncSessionLocal:
                await self.initialize()
            
            async with self.AsyncSessionLocal() as session:
                # 构建SQL查询
                queue_names_str = "', '".join(queues)
                
                # 计算时间跨度
                duration = (end_time - start_time).total_seconds()
                
                # 根据时间跨度决定聚合粒度
                # 短时间范围：返回每个任务的真实时间
                # 长时间范围：按适当的时间窗口聚合
                
                if duration <= 3600:  # 1小时以内，返回每个任务的真实时间
                    print(f'一小时内')
                    # 查询每个任务的真实创建时间
                    query = text(f"""
                        SELECT 
                            created_at as time_point,
                            queue_name,
                            COUNT(*) OVER (
                                PARTITION BY queue_name, created_at
                            ) as task_count
                        FROM tasks 
                        WHERE queue_name IN ('{queue_names_str}')
                            AND created_at >= :start_time 
                            AND created_at <= :end_time
                        ORDER BY created_at, queue_name
                    """)
                    
                elif duration <= 86400:  # 1天以内，按分钟聚合
                    query = text(f"""
                        SELECT 
                            date_trunc('minute', created_at) as time_point,
                            queue_name,
                            COUNT(*) as task_count
                        FROM tasks 
                        WHERE queue_name IN ('{queue_names_str}')
                            AND created_at >= :start_time 
                            AND created_at <= :end_time
                        GROUP BY time_point, queue_name
                        ORDER BY time_point, queue_name
                    """)
                    
                elif duration <= 604800:  # 7天以内，按小时聚合
                    query = text(f"""
                        SELECT 
                            date_trunc('hour', created_at) as time_point,
                            queue_name,
                            COUNT(*) as task_count
                        FROM tasks 
                        WHERE queue_name IN ('{queue_names_str}')
                            AND created_at >= :start_time 
                            AND created_at <= :end_time
                        GROUP BY time_point, queue_name
                        ORDER BY time_point, queue_name
                    """)
                    
                else:  # 超过7天，按天聚合
                    query = text(f"""
                        SELECT 
                            date_trunc('day', created_at) as time_point,
                            queue_name,
                            COUNT(*) as task_count
                        FROM tasks 
                        WHERE queue_name IN ('{queue_names_str}')
                            AND created_at >= :start_time 
                            AND created_at <= :end_time
                        GROUP BY time_point, queue_name
                        ORDER BY time_point, queue_name
                    """)
                
                result = await session.execute(query, {
                    'start_time': start_time,
                    'end_time': end_time
                })
                
                # 处理查询结果，返回真实的时间点
                timeline_data = []
                seen_points = set()  # 用于去重（对于窗口函数的结果）
                
                for row in result:
                    # 创建唯一键避免重复
                    unique_key = f"{row.time_point.isoformat()}_{row.queue_name}"
                    if unique_key not in seen_points:
                        seen_points.add(unique_key)
                        timeline_data.append({
                            'time': row.time_point.isoformat(),
                            'queue': row.queue_name,
                            'value': row.task_count
                        })
                
                logger.info(f"从DB查询到 {len(timeline_data)} 个真实数据点")
                
                return timeline_data
                
        except Exception as e:
            logger.error(f"获取队列时间线数据失败: {e}")
            return []
    
    
    async def fetch_global_stats(self) -> Dict:
        """获取全局统计信息"""
        try:
            redis_client = await self.get_redis_client()
            
            # 获取所有队列的统计信息
            queues_data = await self.fetch_queues_data()
            
            total_pending = sum(q['待处理'] for q in queues_data)
            total_processing = sum(q['处理中'] for q in queues_data)
            total_completed = sum(q['已完成'] for q in queues_data)
            total_failed = sum(q['失败'] for q in queues_data)
            
            # 获取活跃worker数量
            worker_keys = await redis_client.keys(f"{self.redis_prefix}:worker:*")
            active_workers = len(worker_keys)
            
            await redis_client.close()
            
            return {
                'total_queues': len(queues_data),
                'total_pending': total_pending,
                'total_processing': total_processing,
                'total_completed': total_completed,
                'total_failed': total_failed,
                'active_workers': active_workers,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取全局统计信息失败: {e}")
            return {}