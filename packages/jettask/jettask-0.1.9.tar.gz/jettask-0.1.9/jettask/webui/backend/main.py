"""
JetTask Monitor 独立后端API服务
完全脱离gradio和integrated_gradio_app依赖
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

import sys
import os
# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_access import JetTaskDataAccess

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据访问实例
data_access = JetTaskDataAccess()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    try:
        await data_access.initialize()
        logger.info("JetTask Monitor API 启动成功")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise
    
    yield
    
    # 关闭时清理资源
    try:
        await data_access.close()
        logger.info("JetTask Monitor API 关闭完成")
    except Exception as e:
        logger.error(f"关闭时出错: {e}")


app = FastAPI(
    title="JetTask Monitor API", 
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TimeRangeQuery(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    time_range: Optional[str] = "15m"  # 默认15分钟
    queues: Optional[List[str]] = None


class QueueTimelineResponse(BaseModel):
    data: List[Dict]
    granularity: str


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "JetTask Monitor API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/queues")
async def get_queues():
    """获取所有队列列表"""
    try:
        queues_data = await data_access.fetch_queues_data()
        return {
            "success": True,
            "data": [q['队列名称'] for q in queues_data]
        }
    except Exception as e:
        logger.error(f"获取队列列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/queue-timeline")
async def get_queue_timeline(query: TimeRangeQuery):
    """获取队列处理趋势数据"""
    try:
        logger.info(f"获取队列时间线数据: {query}")
        
        # 确定时间范围
        if query.start_time and query.end_time:
            start_time = query.start_time
            end_time = query.end_time
            time_range = "custom"
        else:
            # 使用预设时间范围
            end_time = datetime.now(timezone.utc)
            time_range = query.time_range
            
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
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(minutes=15)
        
        # 如果没有指定队列，获取前3个队列
        if not query.queues:
            queues_data = await data_access.fetch_queues_data()
            query.queues = [q['队列名称'] for q in queues_data][:10]
        # logger.info(f'{start_time=} {end_time=} {query.queues=}')
        # 获取时间线数据
        timeline_data = await data_access.fetch_queue_timeline_data(
            query.queues, start_time, end_time
        )
        # logger.info(f"获取到时间线数据: {timeline_data} 条记录")
        # 计算数据粒度 - 与 data_access 中的逻辑保持一致
        duration = (end_time - start_time).total_seconds()
        ideal_interval_seconds = duration / 200  # 目标200个点
        
        # 判断时间跨度和粒度
        is_cross_day = start_time.date() != end_time.date()
        
        if ideal_interval_seconds <= 1:
            granularity = "second"  # 秒级
        elif ideal_interval_seconds <= 60:
            granularity = "minute"  # 分钟级以下
        elif ideal_interval_seconds <= 3600:
            granularity = "hour"  # 小时级
        elif is_cross_day:
            granularity = "day"  # 跨天
        else:
            granularity = "hour"  # 默认小时级
        
        return QueueTimelineResponse(
            data=timeline_data,
            granularity=granularity
        )
        
    except Exception as e:
        logger.error(f"获取队列时间线数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_global_stats():
    """获取全局统计信息"""
    try:
        stats_data = await data_access.fetch_global_stats()
        return {
            "success": True,
            "data": stats_data
        }
    except Exception as e:
        logger.error(f"获取全局统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queues/detail")
async def get_queues_detail():
    """获取队列详细信息"""
    try:
        queues_data = await data_access.fetch_queues_data()
        return {
            "success": True,
            "data": queues_data
        }
    except Exception as e:
        logger.error(f"获取队列详细信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def run_server():
    """运行 Web UI 服务器"""
    import uvicorn
    uvicorn.run(
        "jettask.webui.backend.main:app", 
        host="0.0.0.0", 
        port=8001,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    run_server()