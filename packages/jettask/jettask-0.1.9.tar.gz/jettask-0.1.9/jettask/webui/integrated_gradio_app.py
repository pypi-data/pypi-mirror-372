import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, timezone
import asyncio
import json
import logging
import time
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from jettask.webui.config import RedisConfig, PostgreSQLConfig

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedDataAccess:
    """直接访问数据源，不通过API"""
    
    def __init__(self):
        self.redis_config = None
        self.pg_config = None
        self.redis_prefix = "jettask"
        self.async_engine = None
        self.AsyncSessionLocal = None
        
    async def initialize(self):
        """初始化数据库配置"""
        # 保存配置
        self.redis_config = RedisConfig.from_env()
        self.pg_config = PostgreSQLConfig.from_env()
        
        # 初始化PostgreSQL引擎
        if self.pg_config.dsn:
            dsn = self.pg_config.dsn
            if dsn.startswith('postgresql://'):
                dsn = dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
            
            self.async_engine = create_async_engine(
                dsn,
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,
                echo=False
            )
            
            self.AsyncSessionLocal = sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("Database configuration initialized")
        else:
            logger.warning("PostgreSQL connection not configured")
    
    async def close(self):
        """关闭数据库连接"""
        if self.async_engine:
            await self.async_engine.dispose()
    
    async def _get_redis_client(self):
        """获取Redis客户端"""
        return redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=False
        )
    
    async def get_global_stats(self) -> Dict:
        """获取全局统计信息"""
        redis_client = await self._get_redis_client()
        try:
            # 获取所有队列
            pattern = f"{self.redis_prefix}:QUEUE:*"
            all_queues = set()
            async for key in redis_client.scan_iter(match=pattern, count=100):
                queue_name = key.decode('utf-8').split(":")[-1]
                all_queues.add(queue_name)
            
            # 获取worker信息
            worker_pattern = f"{self.redis_prefix}:CONSUMER:*"
            all_workers = set()
            online_workers = 0
            
            async for key in redis_client.scan_iter(match=worker_pattern, count=100):
                consumer_id = key.decode('utf-8').split(":")[-1]
                all_workers.add(consumer_id)
                
                # 检查是否在线
                last_heartbeat = await redis_client.hget(key, b'last_heartbeat')
                if last_heartbeat:
                    try:
                        last_heartbeat_time = float(last_heartbeat)
                        if time.time() - last_heartbeat_time < 30:
                            online_workers += 1
                    except:
                        pass
            
            # 从PostgreSQL获取任务统计
            task_stats = {
                'pending_tasks': 0,
                'running_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'total_tasks': 0
            }
            
            if self.AsyncSessionLocal:
                async with self.AsyncSessionLocal() as session:
                    query = text("""
                        SELECT 
                            status,
                            COUNT(*) as count
                        FROM tasks
                        GROUP BY status
                    """)
                    result = await session.execute(query)
                    rows = result.mappings().all()
                    
                    for row in rows:
                        status = row['status']
                        count = row['count']
                        if status == 'pending':
                            task_stats['pending_tasks'] = count
                        elif status == 'running':
                            task_stats['running_tasks'] = count
                        elif status in ('success', 'completed'):
                            task_stats['completed_tasks'] = count
                        elif status in ('failed', 'error'):
                            task_stats['failed_tasks'] = count
                        task_stats['total_tasks'] += count
            
            return {
                'total_queues': len(all_queues),
                'active_queues': len(all_queues),  # 简化处理
                'total_workers': len(all_workers),
                'online_workers': online_workers,
                **task_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            return {
                'total_queues': 0,
                'active_queues': 0,
                'total_workers': 0,
                'online_workers': 0,
                'pending_tasks': 0,
                'running_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'total_tasks': 0
            }
        finally:
            await redis_client.close()
    
    async def get_queues(self) -> List[str]:
        """获取所有队列"""
        redis_client = await self._get_redis_client()
        try:
            pattern = f"{self.redis_prefix}:QUEUE:*"
            queues = []
            async for key in redis_client.scan_iter(match=pattern, count=100):
                queue_name = key.decode('utf-8').split(":")[-1]
                queues.append(queue_name)
            return sorted(queues)
        finally:
            await redis_client.close()
    
    async def get_queue_stats(self, queue_name: str) -> Dict:
        """获取队列统计信息"""
        redis_client = await self._get_redis_client()
        try:
            stream_key = f"{self.redis_prefix}:QUEUE:{queue_name}"
            
            try:
                # 获取stream信息
                info = await redis_client.xinfo_stream(stream_key)
                
                # 获取消费者组信息
                groups = await redis_client.xinfo_groups(stream_key)
                consumers = 0
                for group in groups:
                    group_info = await redis_client.xinfo_consumers(stream_key, group[b'name'])
                    consumers += len(group_info)
                
                return {
                    'messages_ready': info[b'length'],
                    'messages_unacknowledged': info.get(b'groups', 0),
                    'consumers': consumers
                }
            except:
                return {
                    'messages_ready': 0,
                    'messages_unacknowledged': 0,
                    'consumers': 0
                }
        finally:
            await redis_client.close()
    
    async def get_queue_timeline(self, queue_names: List[str], start_time: datetime, end_time: datetime) -> Dict:
        """获取队列时间线数据"""
        if not self.AsyncSessionLocal:
            return {"queues": []}
        
        # # 计算时间间隔
        duration = (end_time - start_time).total_seconds()
        if duration <= 300:  # <= 5分钟
            interval_seconds = 1
            interval_type = 'millisecond'
        elif duration <= 900:  # <= 15分钟
            interval_seconds = 1
            interval_type = 'second'
        elif duration <= 1800:  # <= 30分钟
            interval_seconds = 2
            interval_type = 'second'
        elif duration <= 3600:  # <= 1小时
            interval_seconds = 30
            interval_type = 'second'
        elif duration <= 10800:  # <= 3小时
            interval_seconds = 300
            interval_type = 'minute'
        else:
            interval_seconds = 3600
            interval_type = 'hour'
        print(f'{interval_seconds=} {interval_type=}')
        result = []
        
        for queue_name in queue_names[:10]:  # 最多10个队列
            try:
                async with self.AsyncSessionLocal() as session:
                    # 构建SQL查询
                    if interval_type == 'millisecond':
                        query = text(f"""
                        SELECT 
                            DATE_TRUNC('second', created_at) + 
                            INTERVAL '{interval_seconds} seconds' * FLOOR(EXTRACT(EPOCH FROM created_at) * 2) / 2 as time_bucket,
                            COUNT(*) as count
                        FROM tasks
                        WHERE queue_name = :queue_name
                            AND created_at >= :start_dt
                            AND created_at < :end_dt
                        GROUP BY time_bucket
                        ORDER BY time_bucket
                        """)
                    elif interval_type == 'second':
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
                    elif interval_type == 'minute':
                        interval_minutes = int(interval_seconds / 60)
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
                    else:  # hour
                        interval_hours = int(interval_seconds / 3600)
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
                    
                    result_obj = await session.execute(query, {
                        'queue_name': queue_name,
                        'start_dt': start_time,
                        'end_dt': end_time
                    })
                    rows = result_obj.mappings().all()
                    
                    # 构建时间线
                    timeline = []
                    for row in rows:
                        timeline.append({
                            "time": row['time_bucket'].isoformat(),
                            "count": row['count']
                        })
                    
                    # 填充缺失的时间点
                    filled_timeline = self._fill_missing_timepoints(
                        timeline, start_time, end_time, interval_seconds
                    )
                    
                    result.append({
                        "queue": queue_name,
                        "timeline": {"timeline": filled_timeline}
                    })
                    
            except Exception as e:
                logger.error(f"Error getting timeline for queue {queue_name}: {e}")
                
        return {"queues": result}
    
    def _fill_missing_timepoints(self, timeline: List[Dict], start_time: datetime, 
                                 end_time: datetime, interval_seconds: float) -> List[Dict]:
        """填充缺失的时间点"""
        # 创建时间映射
        time_map = {}
        for item in timeline:
            dt = datetime.fromisoformat(item['time'])
            time_map[dt] = item['count']
        
        # 生成完整时间序列
        filled = []
        current = self._align_time(start_time, interval_seconds)
        
        while current < end_time:
            # 查找最近的数据点
            count = 0
            for dt, cnt in time_map.items():
                if abs((dt - current).total_seconds()) < interval_seconds / 2:
                    count = cnt
                    break
            
            filled.append({
                "time": current.isoformat(),
                "count": count
            })
            
            current += timedelta(seconds=interval_seconds)
        
        return filled
    
    def _align_time(self, dt: datetime, interval_seconds: float) -> datetime:
        """对齐时间到间隔"""
        if interval_seconds >= 3600:
            dt = dt.replace(minute=0, second=0, microsecond=0)
            hours = int(interval_seconds / 3600)
            aligned_hour = (dt.hour // hours) * hours
            return dt.replace(hour=aligned_hour)
        elif interval_seconds >= 60:
            dt = dt.replace(second=0, microsecond=0)
            minutes = int(interval_seconds / 60)
            total_minutes = dt.hour * 60 + dt.minute
            aligned_minutes = (total_minutes // minutes) * minutes
            return dt.replace(hour=aligned_minutes // 60, minute=aligned_minutes % 60)
        elif interval_seconds >= 1:
            dt = dt.replace(microsecond=0)
            aligned_second = int(dt.second // interval_seconds) * int(interval_seconds)
            return dt.replace(second=aligned_second)
        else:
            # 毫秒级别
            ms = dt.microsecond / 1000
            interval_ms = interval_seconds * 1000
            aligned_ms = int(ms // interval_ms) * interval_ms
            return dt.replace(microsecond=int(aligned_ms * 1000))


class IntegratedJetTaskMonitor:
    """集成的JetTask监控器"""
    
    def __init__(self):
        self.data_access = IntegratedDataAccess()
        self.queue_data = []
        self.executor = None
        self.loop = None
        self._closed = False
        
    def _run_async(self, coro):
        """在专用线程中运行异步代码"""
        if self._closed:
            raise RuntimeError("Monitor is closed")
            
        # 延迟创建 executor
        if self.executor is None:
            self.executor = ThreadPoolExecutor(max_workers=1)
            
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        
        future = self.executor.submit(run)
        return future.result()
    
    def initialize(self):
        """初始化数据访问"""
        self._run_async(self.data_access.initialize())
    
    def close(self):
        """关闭连接"""
        if self._closed:
            return
            
        self._closed = True
        
        try:
            if self.data_access:
                # 使用新的事件循环来关闭连接
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.data_access.close())
                finally:
                    loop.close()
        except Exception as e:
            logger.error(f"Error closing data access: {e}")
            
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
    
    def fetch_global_stats(self, return_dict: bool = False):
        """获取全局统计数据"""
        stats = self._run_async(self.data_access.get_global_stats())
        
        if return_dict:
            # 返回原始字典数据
            return stats
        
        # 构建显示文本
        stats_text = f"""
        ## 系统概览
        
        ### Workers
        - 在线: {stats.get('online_workers', 0)} / {stats.get('total_workers', 0)}
        - 活跃队列: {stats.get('active_queues', 0)} / {stats.get('total_queues', 0)}
        
        ### 任务统计
        - 待处理: {stats.get('pending_tasks', 0):,}
        - 运行中: {stats.get('running_tasks', 0):,}
        - 已完成: {stats.get('completed_tasks', 0):,}
        - 失败: {stats.get('failed_tasks', 0):,}
        
        ### 实时性能
        - 总任务数: {stats.get('total_tasks', 0):,}
        - 成功率: {self._calculate_success_rate(stats):.1f}%
        """
        return stats_text
    
    def _calculate_success_rate(self, stats: Dict) -> float:
        """计算成功率"""
        completed = stats.get('completed_tasks', 0)
        failed = stats.get('failed_tasks', 0)
        total = completed + failed
        return (completed / total * 100) if total > 0 else 0
    
    def fetch_queues_data(self):
        """获取队列数据"""
        queues = self._run_async(self.data_access.get_queues())
        
        detailed_queues = []
        for queue_name in queues:
            stats = self._run_async(self.data_access.get_queue_stats(queue_name))
            
            queue_info = {
                '队列名称': queue_name,
                '待处理': stats.get('messages_ready', 0),
                '处理中': stats.get('messages_unacknowledged', 0),
                '消费者': stats.get('consumers', 0)
            }
            detailed_queues.append(queue_info)
        
        self.queue_data = detailed_queues
        return pd.DataFrame(detailed_queues) if detailed_queues else pd.DataFrame()
    
    def create_queue_timeline_chart(self, time_range: str = "1h", selected_queues: List[str] = None, 
                                   custom_start: datetime = None, custom_end: datetime = None,
                                   return_with_config: bool = False):
        """创建队列时间线图表"""
        # 计算时间范围
        if custom_start and custom_end:
            # 使用自定义时间范围
            start_time = custom_start
            end_time = custom_end
            time_range = "custom"
        else:
            # 使用预设时间范围
            now = datetime.now(timezone.utc)
            end_time = now
            
            if time_range == "15m":
                start_time = end_time - timedelta(minutes=15)
            elif time_range == "30m":
                start_time = end_time - timedelta(minutes=30)
            elif time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "3h":
                start_time = end_time - timedelta(hours=3)
            elif time_range == "6h":
                start_time = end_time - timedelta(hours=6)
            elif time_range == "12h":
                start_time = end_time - timedelta(hours=12)
            elif time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "today":
                # 今天的开始时间
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = now
            elif time_range == "this_week":
                # 本周的开始时间（周一）
                days_since_monday = now.weekday()
                start_time = now - timedelta(days=days_since_monday)
                start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = now
            elif time_range.endswith("d"):
                # 处理天数
                try:
                    days = int(time_range[:-1])
                    start_time = end_time - timedelta(days=days)
                except:
                    start_time = end_time - timedelta(hours=1)
            elif time_range.endswith("h"):
                # 处理小时数
                try:
                    hours = int(time_range[:-1])
                    start_time = end_time - timedelta(hours=hours)
                except:
                    start_time = end_time - timedelta(hours=1)
            elif time_range.endswith("m"):
                # 处理分钟数
                try:
                    minutes = int(time_range[:-1])
                    start_time = end_time - timedelta(minutes=minutes)
                except:
                    start_time = end_time - timedelta(hours=1)
            elif time_range == "1y":
                start_time = end_time - timedelta(days=365)
            else:
                start_time = end_time - timedelta(hours=1)
        
        # 获取队列列表
        if not selected_queues or len(selected_queues) == 0:
            # 构建标题
            if time_range == "custom":
                time_display = f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}"
            else:
                time_display = time_range
            
            return go.Figure().update_layout(
                title=f"队列处理趋势 - {time_display} (请选择队列)",
                xaxis_title="时间（本地时区）",
                yaxis_title="任务数量",
                template='plotly_dark',
                height=500
            )
        
        # 获取时间线数据
        timeline_data = self._run_async(
            self.data_access.get_queue_timeline(selected_queues, start_time, end_time)
        )
        
        # 创建图表
        fig = go.Figure()
        colors = px.colors.qualitative.Plotly + px.colors.qualitative.D3
        
        for i, queue_data in enumerate(timeline_data.get('queues', [])):
            queue_name = queue_data['queue']
            timeline = queue_data.get('timeline', {}).get('timeline', [])
            
            if timeline:
                # 转换为本地时间
                local_times = []
                for item in timeline:
                    utc_time = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                    local_time = utc_time.replace(tzinfo=timezone.utc).astimezone()
                    local_times.append(local_time)
                
                counts = [item['count'] for item in timeline]
                hover_times = [t.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] for t in local_times]
                
                fig.add_trace(go.Scatter(
                    x=local_times,
                    y=counts,
                    name=queue_name,
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=5),
                    customdata=hover_times,
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                  '时间: %{customdata}<br>' +
                                  '任务数: %{y}<br>' +
                                  '<extra></extra>'
                ))
        
        # 构建标题
        if time_range == "custom":
            time_display = f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}"
        else:
            time_display = time_range
        
        fig.update_layout(
            title=f"队列处理趋势 - {time_display}",
            xaxis_title="时间（本地时区）",
            yaxis_title="任务数量",
            hovermode='x unified',
            template='plotly_dark',
            height=500,
            xaxis=dict(
                tickformat='%Y-%m-%d<br>%H:%M:%S.%L',
                tickangle=-45,
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.2)',
                tickformatstops=[
                    dict(dtickrange=[None, 1000], value="%H:%M:%S.%L"),
                    dict(dtickrange=[1000, 60000], value="%H:%M:%S"),
                    dict(dtickrange=[60000, 3600000], value="%H:%M"),
                    dict(dtickrange=[3600000, None], value="%Y-%m-%d<br>%H:%M")
                ]
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.2)',
                fixedrange=True  # 固定Y轴，不允许缩放
            ),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            ),
            margin=dict(r=150),
            dragmode='zoom',  # 使用缩放模式
            selectdirection='h'  # 只允许水平选择
        )
        
        # 配置轴以支持正确的选择行为
        fig.update_xaxes(
            fixedrange=False,  # 允许X轴交互
            showspikes=True,  # 显示垂直线
            spikemode='across',
            spikesnap='cursor',
            spikecolor='gray',
            spikethickness=1
        )
        
        fig.update_yaxes(
            fixedrange=True  # 保持Y轴固定
        )
        
        # 添加自定义数据属性以便跟踪时间范围
        fig.add_annotation(
            x=0, y=0,
            text="",
            showarrow=False,
            visible=False,
            # 存储时间信息
            name="time_info"
        )
        
        # 配置图表以支持缩放事件
        fig.update_layout(
            # 允许在x轴上进行框选缩放
            dragmode='zoom',
            selectdirection='h',
            # 显示缩放和重置按钮
            showlegend=True,
            hovermode='x unified',
            # 保存缩放状态
            uirevision='constant',
            # 添加范围选择器和范围滑块
            xaxis=dict(
                rangeslider=dict(visible=True),
                rangeselector=dict(
                    buttons=list([
                        dict(count=15, label="15分钟", step="minute", stepmode="backward"),
                        dict(count=1, label="1小时", step="hour", stepmode="backward"),
                        dict(count=6, label="6小时", step="hour", stepmode="backward"),
                        dict(count=1, label="1天", step="day", stepmode="backward"),
                        dict(step="all", label="全部")
                    ])
                )
            )
        )
        
        if return_with_config:
            return fig, start_time, end_time
        return fig


# 创建全局监控实例
monitor = None

def get_or_create_monitor():
    """获取或创建监控器实例"""
    global monitor
    if monitor is None or monitor._closed:
        monitor = IntegratedJetTaskMonitor()
        monitor.initialize()
    return monitor


def create_integrated_interface():
    """创建集成的Gradio界面"""
    # 使用全局监控器
    global monitor
    monitor = get_or_create_monitor()
    
    # 自定义CSS样式 - 极简版
    custom_css = """
    /* 让下拉框更紧凑 */
    .gr-dropdown {
        min-width: 150px;
    }
    """
    
    with gr.Blocks(title="JetTask Monitor", theme=gr.themes.Soft(), css=custom_css) as app:
        gr.Markdown("# JetTask Monitor - 任务队列监控平台（集成版）")
        gr.Markdown("""
        **提示**: 为避免打断您的工作，系统不会自动刷新数据。
        - 点击 **刷新数据** 手动更新统计信息
        - 选择时间范围或队列时，只有图表会更新
        - 在图表上拖动缩放后，点击按钮应用为自定义时间
        """)
        
        with gr.Tab("概览"):
            # 队列处理趋势放在最上方
            with gr.Row():
                with gr.Column(scale=2):
                    queue_selector_for_timeline = gr.CheckboxGroup(
                        choices=[],
                        value=[],
                        label="选择队列（最多10个）",
                        interactive=True
                    )
                with gr.Column(scale=3):
                    # 紧凑的时间选择器
                    with gr.Row():
                        with gr.Column(scale=1):
                            time_range_dropdown = gr.Dropdown(
                                choices=[
                                    ("最近15分钟", "15m"),
                                    ("最近30分钟", "30m"),
                                    ("最近1小时", "1h"),
                                    ("最近3小时", "3h"),
                                    ("最近6小时", "6h"),
                                    ("最近12小时", "12h"),
                                    ("最近24小时", "24h"),
                                    ("最近7天", "7d"),
                                    ("最近30天", "30d"),
                                    ("今天", "today"),
                                    ("本周", "this_week")
                                ],
                                value="15m",
                                label="时间范围",
                                interactive=True
                            )
                        with gr.Column(scale=1):
                            refresh_chart_btn = gr.Button(
                                "🔄 刷新图表", 
                                variant="primary",
                                size="sm"
                            )
                    
                    # 隐藏的状态存储
                    time_range = gr.State("15m")
                    actual_start_time = gr.State("")
                    actual_end_time = gr.State("")
                    custom_start_time = gr.State("")
                    custom_end_time = gr.State("")
            
            # 队列趋势图表 - 启用交互模式
            with gr.Row():
                with gr.Column():
                    queue_timeline_chart = gr.Plot(label="队列处理趋势")
                    
                    # 添加自定义HTML和JavaScript来监听Plotly事件
                    gr.HTML("""
                    <script>
                    // 监听Plotly图表的缩放事件
                    function setupPlotlyZoomListener() {
                        const plots = document.querySelectorAll('.js-plotly-plot');
                        plots.forEach(plot => {
                            if (plot && plot._fullLayout && !plot._zoomListenerAdded) {
                                plot._zoomListenerAdded = true;
                                
                                // 存储原始范围
                                let originalRange = null;
                                if (plot._fullLayout.xaxis && plot._fullLayout.xaxis.range) {
                                    originalRange = [...plot._fullLayout.xaxis.range];
                                }
                                
                                plot.on('plotly_relayout', (eventData) => {
                                    // 检查是否有x轴范围变化
                                    if (eventData['xaxis.range[0]'] && eventData['xaxis.range[1]']) {
                                        const start = eventData['xaxis.range[0]'];
                                        const end = eventData['xaxis.range[1]'];
                                        
                                        // 将数据存储到window对象
                                        window.plotlyZoomRange = {
                                            start: start,
                                            end: end,
                                            timestamp: Date.now()
                                        };
                                        
                                        console.log('缩放事件:', start, '到', end);
                                    } else if (eventData['xaxis.autorange']) {
                                        // 双击重置
                                        window.plotlyZoomRange = null;
                                        console.log('重置缩放');
                                    }
                                });
                            }
                        });
                    }
                    
                    // 定期尝试设置监听器
                    const setupInterval = setInterval(() => {
                        setupPlotlyZoomListener();
                        // 如果找到图表就停止
                        if (document.querySelector('.js-plotly-plot')) {
                            setTimeout(() => clearInterval(setupInterval), 5000);
                        }
                    }, 500);
                    </script>
                    """)
                    
                    # 用于触发Python回调的隐藏组件
                    zoom_trigger = gr.Number(visible=False, value=0)
                    zoom_data = gr.Textbox(visible=False, value="", elem_id="zoom_data")
                    
                    # 添加定时器检查缩放状态
                    gr.HTML("""
                    <script>
                    // 定期检查缩放状态并触发更新
                    let lastProcessedTimestamp = 0;
                    
                    setInterval(() => {
                        if (window.plotlyZoomRange && 
                            window.plotlyZoomRange.timestamp > lastProcessedTimestamp) {
                            
                            lastProcessedTimestamp = window.plotlyZoomRange.timestamp;
                            
                            // 更新zoom_data组件的值
                            const zoomDataInput = document.querySelector('#zoom_data textarea');
                            if (zoomDataInput) {
                                const zoomInfo = JSON.stringify(window.plotlyZoomRange);
                                zoomDataInput.value = zoomInfo;
                                zoomDataInput.dispatchEvent(new Event('input', { bubbles: true }));
                                
                                console.log('触发数据更新:', zoomInfo);
                            }
                        }
                    }, 1000); // 每秒检查一次
                    </script>
                    """, elem_id="zoom_checker")
                    
                    gr.Markdown("""
                    **💡 提示**: 
                    - 使用鼠标框选时间范围，系统会自动获取该时段的详细数据
                    - 双击图表可以重置到原始视图
                    """)
            
            # 统计信息和刷新按钮
            with gr.Row():
                with gr.Column(scale=4):
                    stats_display = gr.Markdown(monitor.fetch_global_stats())
                with gr.Column(scale=1):
                    refresh_btn = gr.Button("刷新数据", variant="secondary")
            
            # 队列表格
            with gr.Row():
                queue_table = gr.DataFrame(
                    monitor.fetch_queues_data(),
                    label="队列状态",
                    interactive=False
                )
        
        # 定义更新函数
        def update_stats_only():
            """仅更新统计信息和队列表格"""
            current_monitor = get_or_create_monitor()
            stats = current_monitor.fetch_global_stats()
            queues_df = current_monitor.fetch_queues_data()
            return stats, queues_df
        
        def update_overview():
            """更新概览页面（包括队列选择器）"""
            current_monitor = get_or_create_monitor()
            stats = current_monitor.fetch_global_stats()
            queues_df = current_monitor.fetch_queues_data()
            
            # 更新队列选择器
            timeline_queue_choices = [q['队列名称'] for q in current_monitor.queue_data]
            
            return (
                stats,
                queues_df,
                gr.update(choices=timeline_queue_choices, value=timeline_queue_choices[:3] if timeline_queue_choices else [])
            )
        
        def update_timeline_chart(time_range, selected_queues, custom_start=None, custom_end=None):
            """更新时间线图表"""
            current_monitor = get_or_create_monitor()
            
            # 如果提供了自定义时间，使用它
            if custom_start and custom_end:
                try:
                    start_dt = datetime.fromisoformat(custom_start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(custom_end.replace('Z', '+00:00'))
                    fig, actual_start, actual_end = current_monitor.create_queue_timeline_chart(
                        "custom", selected_queues, start_dt, end_dt, return_with_config=True
                    )
                except:
                    # 如果解析失败，使用默认时间范围
                    fig, actual_start, actual_end = current_monitor.create_queue_timeline_chart(
                        time_range, selected_queues, return_with_config=True
                    )
            else:
                fig, actual_start, actual_end = current_monitor.create_queue_timeline_chart(
                    time_range, selected_queues, return_with_config=True
                )
            
            return fig, actual_start.isoformat(), actual_end.isoformat()
        
        def handle_time_range_change(time_value):
            """处理时间范围变化"""
            return time_value
        
        def init_timeline_chart():
            """初始化时间线图表"""
            current_monitor = get_or_create_monitor()
            current_monitor.fetch_queues_data()  # 获取队列数据
            initial_queues = [q['队列名称'] for q in current_monitor.queue_data][:3]
            
            if initial_queues:
                fig, start_time, end_time = current_monitor.create_queue_timeline_chart("15m", initial_queues, return_with_config=True)
            else:
                fig, start_time, end_time = current_monitor.create_queue_timeline_chart("15m", [], return_with_config=True)
            
            return fig, start_time.isoformat(), end_time.isoformat()
        
        def handle_zoom_change(zoom_data_json, selected_queues):
            """处理缩放变化，自动获取新数据"""
            if not zoom_data_json:
                return gr.update(), gr.update(), gr.update(), gr.update()
            
            try:
                import json
                zoom_data = json.loads(zoom_data_json)
                
                # 解析时间
                start_str = zoom_data['start']
                end_str = zoom_data['end']
                
                # Plotly返回的时间格式可能是 "2024-01-01 12:00:00" 或 ISO格式
                try:
                    start_dt = datetime.fromisoformat(start_str.replace(' ', 'T').replace('Z', '+00:00'))
                except:
                    start_dt = datetime.strptime(start_str.split('.')[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                
                try:
                    end_dt = datetime.fromisoformat(end_str.replace(' ', 'T').replace('Z', '+00:00'))
                except:
                    end_dt = datetime.strptime(end_str.split('.')[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                
                print(f"检测到缩放: {start_dt} 到 {end_dt}")
                
                # 调用后端接口获取新数据
                current_monitor = get_or_create_monitor()
                fig, actual_start, actual_end = current_monitor.create_queue_timeline_chart(
                    "custom", selected_queues, start_dt, end_dt, return_with_config=True
                )
                
                # 计算时间间隔以显示数据粒度
                duration = (end_dt - start_dt).total_seconds()
                if duration <= 900:  # <= 15分钟
                    granularity = "毫秒级"
                elif duration <= 3600:  # <= 1小时
                    granularity = "秒级"
                elif duration <= 10800:  # <= 3小时
                    granularity = "30秒间隔"
                elif duration <= 86400:  # <= 1天
                    granularity = "5分钟间隔"
                else:
                    granularity = "1小时间隔"
                
                print(f"自动重新获取数据，粒度: {granularity}")
                
                return fig, actual_start.isoformat(), actual_end.isoformat(), "custom"
            except Exception as e:
                print(f"处理缩放事件出错: {e}")
                return gr.update(), gr.update(), gr.update(), gr.update()
        
        # 事件绑定
        # 手动刷新按钮 - 只更新统计和表格，不改变用户的选择
        refresh_btn.click(
            update_stats_only,
            outputs=[stats_display, queue_table]
        )
        
        # 刷新图表按钮
        refresh_chart_btn.click(
            update_timeline_chart,
            inputs=[time_range, queue_selector_for_timeline],
            outputs=[queue_timeline_chart, actual_start_time, actual_end_time]
        )
        
        # 同时刷新图表（使用当前选择的参数）
        refresh_btn.click(
            update_timeline_chart,
            inputs=[time_range, queue_selector_for_timeline],
            outputs=[queue_timeline_chart, actual_start_time, actual_end_time]
        )
        
        # 时间范围下拉框变化
        time_range_dropdown.change(
            handle_time_range_change,
            inputs=[time_range_dropdown],
            outputs=[time_range]
        ).then(
            update_timeline_chart,
            inputs=[time_range, queue_selector_for_timeline],
            outputs=[queue_timeline_chart, actual_start_time, actual_end_time]
        )
        
        # 队列选择变化时更新图表
        queue_selector_for_timeline.change(
            update_timeline_chart,
            inputs=[time_range, queue_selector_for_timeline],
            outputs=[queue_timeline_chart, actual_start_time, actual_end_time]
        )
        
        # 监听缩放数据变化，自动更新图表
        zoom_data.change(
            handle_zoom_change,
            inputs=[zoom_data, queue_selector_for_timeline],
            outputs=[queue_timeline_chart, actual_start_time, actual_end_time, time_range]
        )
        
        # 页面加载时初始化
        app.load(
            update_overview,
            outputs=[stats_display, queue_table, queue_selector_for_timeline]
        )
        
        app.load(
            init_timeline_chart,
            outputs=[queue_timeline_chart, actual_start_time, actual_end_time]
        )
        
        # 应用关闭时清理资源
        def cleanup():
            global monitor
            if monitor and not monitor._closed:
                monitor.close()
                monitor = None
        
        app.unload(cleanup)
    
    return app


if __name__ == "__main__":
    app = create_integrated_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        inbrowser=False
    )