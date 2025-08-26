import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, timezone
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import aiohttp
from functools import partial

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API 基础URL
API_BASE_URL = "http://localhost:8000"


class JetTaskMonitor:
    """JetTask 监控界面"""
    
    def __init__(self):
        self.current_stats = {}
        self.queue_data = []
        self.worker_data = []
        self.task_data = []
        
    async def fetch_api(self, endpoint: str, params: Dict = None) -> Dict:
        """异步获取API数据"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_BASE_URL}/api/{endpoint}", params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"API请求失败: {endpoint}, 状态码: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"API请求异常: {endpoint}, 错误: {e}")
            return {}
    
    def fetch_global_stats(self):
        """获取全局统计数据"""
        stats = asyncio.run(self.fetch_api("global-stats"))
        self.current_stats = stats
        
        # 构建显示文本
        stats_text = f"""
        ## 📊 系统概览
        
        ### Workers
        - 🟢 在线: {stats.get('online_workers', 0)} / {stats.get('total_workers', 0)}
        - 📦 活跃队列: {stats.get('active_queues', 0)} / {stats.get('total_queues', 0)}
        
        ### 任务统计
        - ⏳ 待处理: {stats.get('pending_tasks', 0):,}
        - 🔄 运行中: {stats.get('running_tasks', 0):,}
        - ✅ 已完成: {stats.get('completed_tasks', 0):,}
        - ❌ 失败: {stats.get('failed_tasks', 0):,}
        
        ### 实时性能
        - 📈 总任务数: {stats.get('total_tasks', 0):,}
        - ⚡ 成功率: {self._calculate_success_rate(stats):.1f}%
        """
        return stats_text
    
    def _calculate_success_rate(self, stats: Dict) -> float:
        """计算成功率"""
        completed = stats.get('completed_tasks', 0)
        failed = stats.get('failed_tasks', 0)
        total = completed + failed
        return (completed / total * 100) if total > 0 else 0
    
    def fetch_queues_data(self):
        """获取队列数据并返回DataFrame"""
        queues_data = asyncio.run(self.fetch_api("queues"))
        queues = queues_data.get('queues', [])
        
        # 获取每个队列的详细信息
        detailed_queues = []
        for queue_name in queues:
            stats = asyncio.run(self.fetch_api(f"queue/{queue_name}/stats"))
            summary = asyncio.run(self.fetch_api(f"queue/{queue_name}/worker-summary"))
            
            queue_info = {
                '队列名称': queue_name,
                '待处理': stats.get('messages_ready', 0),
                '处理中': stats.get('messages_unacknowledged', 0),
                '消费者': stats.get('consumers', 0),
                '成功数': summary.get('summary', {}).get('success_count', 0),
                '失败数': summary.get('summary', {}).get('failed_count', 0),
                '在线Workers': summary.get('summary', {}).get('online_workers', 0),
                '总Workers': summary.get('summary', {}).get('total_workers', 0),
            }
            detailed_queues.append(queue_info)
        
        self.queue_data = detailed_queues
        return pd.DataFrame(detailed_queues) if detailed_queues else pd.DataFrame()
    
    def fetch_workers_data(self, queue_filter: str = "all"):
        """获取Worker数据"""
        if queue_filter == "all":
            # 获取所有队列的workers
            queues_data = asyncio.run(self.fetch_api("queues"))
            queues = queues_data.get('queues', [])
            
            all_workers = []
            for queue_name in queues:
                workers = asyncio.run(self.fetch_api(f"queue/{queue_name}/workers"))
                for worker in workers.get('workers', []):
                    worker_info = {
                        '队列': queue_name,
                        'Worker ID': worker.get('consumer_id', '-'),
                        '主机': worker.get('host', '-'),
                        '进程ID': worker.get('pid', '-'),
                        '状态': '🟢 在线' if worker.get('is_alive') else '🔴 离线',
                        '最后心跳': self._format_heartbeat(worker.get('seconds_ago', 0)),
                        '成功任务': worker.get('success_count', 0),
                        '失败任务': worker.get('failed_count', 0),
                        '运行中': worker.get('running_tasks', 0),
                        '平均处理时间': f"{worker.get('avg_processing_time', 0):.2f}s",
                    }
                    all_workers.append(worker_info)
            
            self.worker_data = all_workers
            return pd.DataFrame(all_workers) if all_workers else pd.DataFrame()
        else:
            # 获取特定队列的workers
            workers = asyncio.run(self.fetch_api(f"queue/{queue_filter}/workers"))
            workers_list = []
            for worker in workers.get('workers', []):
                worker_info = {
                    'Worker ID': worker.get('consumer_id', '-'),
                    '主机': worker.get('host', '-'),
                    '进程ID': worker.get('pid', '-'),
                    '状态': '🟢 在线' if worker.get('is_alive') else '🔴 离线',
                    '最后心跳': self._format_heartbeat(worker.get('seconds_ago', 0)),
                    '成功任务': worker.get('success_count', 0),
                    '失败任务': worker.get('failed_count', 0),
                    '运行中': worker.get('running_tasks', 0),
                    '平均处理时间': f"{worker.get('avg_processing_time', 0):.2f}s",
                }
                workers_list.append(worker_info)
            
            return pd.DataFrame(workers_list) if workers_list else pd.DataFrame()
    
    def _format_heartbeat(self, seconds_ago: int) -> str:
        """格式化心跳时间"""
        if seconds_ago < 60:
            return f"{seconds_ago}秒前"
        elif seconds_ago < 3600:
            return f"{seconds_ago // 60}分钟前"
        else:
            return f"{seconds_ago // 3600}小时前"
    
    def create_queue_timeline_chart(self, time_range: str = "1h", selected_queues: List[str] = None):
        """创建队列时间线图表"""
        # 计算时间范围
        end_time = datetime.now(timezone.utc)
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
        else:
            start_time = end_time - timedelta(hours=1)
        
        # 获取队列列表
        if not selected_queues or len(selected_queues) == 0:
            # 如果没有选择任何队列，返回空图表
            return go.Figure().update_layout(
                title=f"队列处理趋势 - {time_range} (请选择队列)",
                xaxis_title="时间（本地时区）",
                yaxis_title="任务数量",
                template='plotly_dark',
                height=500
            )
        else:
            queues = selected_queues[:10]  # 限制最多10个队列
        
        # 获取时间线数据
        params = {
            'queues': ','.join(queues),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        timeline_data = asyncio.run(self.fetch_api("queues/timeline/pg", params))
        
        # 创建图表
        fig = go.Figure()
        
        # 使用Plotly的默认颜色序列，支持更多队列
        colors = px.colors.qualitative.Plotly + px.colors.qualitative.D3
        
        for i, queue_data in enumerate(timeline_data.get('queues', [])):
            queue_name = queue_data['queue']
            timeline = queue_data.get('timeline', {}).get('timeline', [])
            
            if timeline:
                # 将UTC时间转换为本地时间
                local_times = []
                for item in timeline:
                    # 解析ISO格式的UTC时间
                    utc_time = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                    # 转换为本地时间
                    local_time = utc_time.replace(tzinfo=timezone.utc).astimezone()
                    local_times.append(local_time)
                
                counts = [item['count'] for item in timeline]
                
                # 为hover创建格式化的时间字符串
                hover_times = [t.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] for t in local_times]  # 显示到毫秒
                
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
        
        fig.update_layout(
            title=f"队列处理趋势 - {time_range}",
            xaxis_title="时间（本地时区）",
            yaxis_title="任务数量",
            hovermode='x unified',
            template='plotly_dark',
            height=500,  # 增加高度以便更好地显示多个队列
            xaxis=dict(
                tickformat='%Y-%m-%d<br>%H:%M:%S.%L',  # 显示日期、时间和毫秒
                tickangle=-45,  # 倾斜标签以避免重叠
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.2)',
                tickformatstops=[
                    dict(dtickrange=[None, 1000], value="%H:%M:%S.%L"),  # 小于1秒时显示毫秒
                    dict(dtickrange=[1000, 60000], value="%H:%M:%S"),   # 1秒到1分钟显示秒
                    dict(dtickrange=[60000, 3600000], value="%H:%M"),    # 1分钟到1小时显示分钟
                    dict(dtickrange=[3600000, None], value="%Y-%m-%d<br>%H:%M")  # 大于1小时显示日期和时间
                ]
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.2)',
                fixedrange=True  # 禁用Y轴缩放
            ),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            ),
            margin=dict(r=150),  # 为图例留出空间
            dragmode='zoom',  # 设置为缩放模式，允许框选
            selectdirection='h'  # 只允许水平选择（只能框选X轴）
        )
        
        return fig
    
    def fetch_tasks_data(self, queue_name: str, status_filter: str = "all", limit: int = 100):
        """获取任务数据"""
        params = {
            'queue_name': queue_name,
            'limit': limit
        }
        
        if status_filter != "all":
            params['status'] = status_filter
        
        tasks_data = asyncio.run(self.fetch_api(f"queue/{queue_name}/tasks", params))
        tasks = tasks_data.get('tasks', [])
        
        # 转换为DataFrame格式
        tasks_list = []
        for task in tasks:
            task_info = {
                '任务ID': task.get('message_id', '-')[:20] + '...',
                '任务名称': task.get('task', '-'),
                '状态': self._format_status(task.get('parsed_status', {}).get('status', '未知')),
                '消费者': task.get('consumer', '-'),
                '创建时间': self._format_time(task.get('created_at')),
                '参数': task.get('params_str', '-')[:50] + '...' if len(task.get('params_str', '')) > 50 else task.get('params_str', '-'),
            }
            tasks_list.append(task_info)
        
        return pd.DataFrame(tasks_list) if tasks_list else pd.DataFrame()
    
    def _format_status(self, status: str) -> str:
        """格式化任务状态"""
        status_map = {
            'pending': '⏳ 待处理',
            'running': '🔄 运行中',
            'success': '✅ 成功',
            'failed': '❌ 失败',
            'timeout': '⏱️ 超时',
            'cancelled': '🚫 已取消',
            '未知': '❓ 未知'
        }
        return status_map.get(status, status)
    
    def _format_time(self, time_str: str) -> str:
        """格式化时间显示（转换为本地时区）"""
        if not time_str:
            return '-'
        try:
            # 解析UTC时间
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            # 转换为本地时区
            local_dt = dt.replace(tzinfo=timezone.utc).astimezone()
            # 显示到毫秒（3位小数）
            return local_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        except:
            return time_str
    
    def create_worker_distribution_chart(self):
        """创建Worker分布饼图"""
        # 按队列统计worker数量
        queue_worker_count = {}
        for worker in self.worker_data:
            queue = worker.get('队列', 'Unknown')
            queue_worker_count[queue] = queue_worker_count.get(queue, 0) + 1
        
        if not queue_worker_count:
            return go.Figure()
        
        fig = go.Figure(data=[go.Pie(
            labels=list(queue_worker_count.keys()),
            values=list(queue_worker_count.values()),
            hole=.3
        )])
        
        fig.update_layout(
            title="Worker 分布",
            template='plotly_dark',
            height=400
        )
        
        return fig


# 创建监控实例
monitor = JetTaskMonitor()


def create_interface():
    """创建Gradio界面"""
    
    with gr.Blocks(title="JetTask Monitor", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🚀 JetTask Monitor - 任务队列监控平台")
        
        # 定时刷新组件
        timer = gr.Timer(5.0)  # 每5秒刷新一次
        
        with gr.Tab("📊 概览"):
            with gr.Row():
                stats_display = gr.Markdown(monitor.fetch_global_stats())
            
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Row():
                        time_range = gr.Radio(
                            choices=["15m", "30m", "1h", "3h", "6h", "12h", "24h"],
                            value="1h",
                            label="时间范围",
                            interactive=True
                        )
                        queue_selector_for_timeline = gr.CheckboxGroup(
                            choices=[],  # 将在页面加载时更新
                            value=[],    # 默认选择所有队列
                            label="选择队列（最多10个）",
                            interactive=True
                        )
                    queue_timeline_chart = gr.Plot(
                        label="队列处理趋势"
                    )
                
                with gr.Column(scale=1):
                    worker_dist_chart = gr.Plot()
            
            # 队列表格
            with gr.Row():
                queue_table = gr.DataFrame(
                    monitor.fetch_queues_data(),
                    label="队列状态",
                    interactive=False
                )
        
        with gr.Tab("📦 队列详情"):
            with gr.Row():
                queue_selector = gr.Dropdown(
                    choices=["all"] + [q['队列名称'] for q in monitor.queue_data],
                    value="all",
                    label="选择队列",
                    interactive=True
                )
                refresh_queue_btn = gr.Button("🔄 刷新", variant="secondary")
            
            with gr.Row():
                queue_workers_table = gr.DataFrame(
                    monitor.fetch_workers_data("all"),
                    label="Workers",
                    interactive=False
                )
        
        with gr.Tab("📋 任务列表"):
            with gr.Row():
                task_queue_selector = gr.Dropdown(
                    choices=[q['队列名称'] for q in monitor.queue_data],
                    value=monitor.queue_data[0]['队列名称'] if monitor.queue_data else None,
                    label="选择队列",
                    interactive=True
                )
                task_status_filter = gr.Radio(
                    choices=["all", "pending", "running", "success", "failed"],
                    value="all",
                    label="状态筛选",
                    interactive=True
                )
                task_limit = gr.Slider(
                    minimum=10,
                    maximum=500,
                    value=100,
                    step=10,
                    label="显示数量",
                    interactive=True
                )
            
            tasks_table = gr.DataFrame(
                label="任务列表",
                interactive=False
            )
        
        # 定义更新函数
        def update_overview():
            """更新概览页面"""
            stats = monitor.fetch_global_stats()
            queues_df = monitor.fetch_queues_data()
            workers_df = monitor.fetch_workers_data("all")
            
            # 更新Worker分布图
            worker_chart = monitor.create_worker_distribution_chart()
            
            # 更新队列选择器
            queue_choices = ["all"] + [q['队列名称'] for q in monitor.queue_data]
            task_queue_choices = [q['队列名称'] for q in monitor.queue_data]
            timeline_queue_choices = [q['队列名称'] for q in monitor.queue_data]
            
            return (
                stats,
                queues_df,
                worker_chart,
                gr.update(choices=queue_choices),
                gr.update(choices=task_queue_choices, value=task_queue_choices[0] if task_queue_choices else None),
                gr.update(choices=timeline_queue_choices, value=timeline_queue_choices[:3] if timeline_queue_choices else [])  # 默认选择前3个队列
            )
        
        def update_timeline_chart(time_range, selected_queues):
            """更新时间线图表"""
            return monitor.create_queue_timeline_chart(time_range, selected_queues)
        
        def init_timeline_chart():
            """初始化时间线图表"""
            # 获取队列列表
            queues_data = monitor.fetch_queues_data()
            initial_queues = [q['队列名称'] for q in monitor.queue_data][:3]  # 默认前3个队列
            if initial_queues:
                return monitor.create_queue_timeline_chart("1h", initial_queues)
            else:
                return monitor.create_queue_timeline_chart("1h", [])
        
        def update_queue_workers(queue_name):
            """更新队列Workers"""
            return monitor.fetch_workers_data(queue_name)
        
        def update_tasks(queue_name, status_filter, limit):
            """更新任务列表"""
            if queue_name:
                return monitor.fetch_tasks_data(queue_name, status_filter, int(limit))
            return pd.DataFrame()
        
        # 事件绑定
        timer.tick(
            update_overview,
            outputs=[stats_display, queue_table, worker_dist_chart, queue_selector, task_queue_selector, queue_selector_for_timeline]
        )
        
        time_range.change(
            update_timeline_chart,
            inputs=[time_range, queue_selector_for_timeline],
            outputs=[queue_timeline_chart]
        )
        
        queue_selector_for_timeline.change(
            update_timeline_chart,
            inputs=[time_range, queue_selector_for_timeline],
            outputs=[queue_timeline_chart]
        )
        
        queue_selector.change(
            update_queue_workers,
            inputs=[queue_selector],
            outputs=[queue_workers_table]
        )
        
        refresh_queue_btn.click(
            update_queue_workers,
            inputs=[queue_selector],
            outputs=[queue_workers_table]
        )
        
        # 任务列表更新
        task_queue_selector.change(
            update_tasks,
            inputs=[task_queue_selector, task_status_filter, task_limit],
            outputs=[tasks_table]
        )
        
        task_status_filter.change(
            update_tasks,
            inputs=[task_queue_selector, task_status_filter, task_limit],
            outputs=[tasks_table]
        )
        
        task_limit.change(
            update_tasks,
            inputs=[task_queue_selector, task_status_filter, task_limit],
            outputs=[tasks_table]
        )
        
        # 页面加载时初始化
        app.load(
            update_overview,
            outputs=[stats_display, queue_table, worker_dist_chart, queue_selector, task_queue_selector, queue_selector_for_timeline]
        )
        
        app.load(
            init_timeline_chart,
            outputs=[queue_timeline_chart]
        )
    
    return app


if __name__ == "__main__":
    # 创建并启动应用
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )