#!/usr/bin/env python3
"""
JetTask WebUI 启动脚本
支持多种界面模式：
1. FastAPI + HTML (原始模式)
2. Gradio 界面 (新模式)
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from jettask.webui.config import PostgreSQLConfig


def run_fastapi_server(host: str = "0.0.0.0", port: int = 8000, with_consumer: bool = False):
    """运行FastAPI服务器"""
    import uvicorn
    from jettask.webui.api import app
    
    # 如果需要启动消费者
    if with_consumer:
        pg_config = PostgreSQLConfig.from_env()
        if pg_config.dsn:
            app.state.pg_config = pg_config
            app.state.enable_consumer = True
            print("PostgreSQL consumer will be started with the server")
        else:
            print("Warning: PostgreSQL configuration not found, consumer disabled")
    
    print(f"Starting FastAPI server on http://{host}:{port}")
    print("Access the web interface at http://localhost:8000/")
    
    uvicorn.run(
        "jettask.webui.api:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )


def run_gradio_interface(host: str = "0.0.0.0", port: int = 7860, share: bool = False):
    """运行Gradio界面"""
    # 确保FastAPI服务器正在运行
    print("Note: Make sure the FastAPI server is running on port 8000")
    print("You can start it with: python -m jettask.webui.run_webui --mode fastapi")
    print()
    
    from jettask.webui.gradio_app import create_interface
    
    app = create_interface()
    print(f"Starting Gradio interface on http://{host}:{port}")
    
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        inbrowser=True
    )


def run_combined_mode(host: str = "0.0.0.0", api_port: int = 8000, ui_port: int = 7860):
    """同时运行FastAPI和Gradio"""
    import subprocess
    import time
    
    # 启动FastAPI服务器
    print("Starting FastAPI server...")
    api_process = subprocess.Popen([
        sys.executable, "-m", "jettask.webui.api"
    ])
    
    # 等待API服务器启动
    time.sleep(3)
    
    # 启动Gradio界面
    print("\nStarting Gradio interface...")
    try:
        run_gradio_interface(host, ui_port, share=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        api_process.terminate()
        api_process.wait()


def run_integrated_gradio(host: str = "0.0.0.0", port: int = 7860, share: bool = False):
    """运行集成的Gradio界面（直接访问数据源）"""
    from jettask.webui.integrated_gradio_app import create_integrated_interface
    
    print("Starting Integrated Gradio interface (direct data access)...")
    print(f"Access the interface at http://{host}:{port}")
    
    app = create_integrated_interface()
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        inbrowser=True
    )


def main():
    parser = argparse.ArgumentParser(description="JetTask WebUI 启动器")
    parser.add_argument(
        "--mode", 
        choices=["fastapi", "gradio", "combined", "integrated"],
        default="integrated",
        help="界面模式: fastapi(原始HTML), gradio(新界面), combined(同时启动), integrated(集成版,直接访问数据)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址")
    parser.add_argument("--port", type=int, help="服务器端口")
    parser.add_argument("--with-consumer", action="store_true", help="启动PostgreSQL消费者")
    parser.add_argument("--share", action="store_true", help="创建Gradio公共链接")
    
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.mode == "fastapi":
        port = args.port or 8000
        run_fastapi_server(args.host, port, args.with_consumer)
    elif args.mode == "gradio":
        port = args.port or 7860
        run_gradio_interface(args.host, port, args.share)
    elif args.mode == "combined":
        run_combined_mode(args.host)
    elif args.mode == "integrated":
        port = args.port or 7860
        run_integrated_gradio(args.host, port, args.share)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()