#!/usr/bin/env python3
"""
启动独立的JetTask Monitor后端API服务
"""
import uvicorn
import logging
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """启动服务"""
    logger.info("启动JetTask Monitor独立后端API服务...")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,  # 开发模式，生产环境应设为False
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("服务被用户中断")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()