#!/usr/bin/env python
"""
Jettask WebUI Runner

Usage:
    python -m jettask.webui.run [--host HOST] [--port PORT] [--redis REDIS_URL]
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jettask.webui.api import app, monitor
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="Jettask Monitor WebUI")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--redis", default="redis://localhost:6379", help="Redis URL (default: redis://localhost:6379)")
    parser.add_argument("--prefix", default="jettask", help="Redis key prefix (default: jettask)")
    
    args = parser.parse_args()
    
    # 更新Redis连接
    monitor.redis_url = args.redis
    monitor.redis_prefix = args.prefix
    
    print(f"Starting Jettask Monitor WebUI...")
    print(f"Redis URL: {args.redis}")
    print(f"Redis Prefix: {args.prefix}")
    print(f"Server: http://{args.host}:{args.port}")
    print(f"Visit http://localhost:{args.port} in your browser")
    
    # 运行服务器
    uvicorn.run(
        "jettask.webui.api:app",
        host=args.host,
        port=args.port,
        log_level="info",
        reload=True
    )

if __name__ == "__main__":
    main()