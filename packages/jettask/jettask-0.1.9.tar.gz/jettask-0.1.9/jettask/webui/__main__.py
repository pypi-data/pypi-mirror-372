#!/usr/bin/env python3
"""WebUI启动入口"""

import sys
import os
import logging
import argparse
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import uvicorn
from jettask.webui.api import app
from jettask.webui.config import PostgreSQLConfig, WebUIConfig, RedisConfig
from jettask.webui.db_init import init_database
from jettask.webui.pg_consumer import PostgreSQLConsumer

def parse_pg_config(args):
    """解析PostgreSQL配置"""
    if args.pg_url:
        pg_config = PostgreSQLConfig.from_url(args.pg_url)
    else:
        pg_config = PostgreSQLConfig.from_env()
        # 命令行参数覆盖环境变量
        if hasattr(args, 'pg_host') and args.pg_host:
            pg_config.host = args.pg_host
        if hasattr(args, 'pg_port') and args.pg_port:
            pg_config.port = args.pg_port
        if hasattr(args, 'pg_database') and args.pg_database:
            pg_config.database = args.pg_database
        if hasattr(args, 'pg_user') and args.pg_user:
            pg_config.user = args.pg_user
        if hasattr(args, 'pg_password') and args.pg_password:
            pg_config.password = args.pg_password
    return pg_config


def add_pg_arguments(parser):
    """添加PostgreSQL相关参数"""
    parser.add_argument('--pg-host', type=str, help='PostgreSQL host (env: JETTASK_PG_HOST)')
    parser.add_argument('--pg-port', type=int, help='PostgreSQL port (env: JETTASK_PG_PORT)')
    parser.add_argument('--pg-database', type=str, help='PostgreSQL database (env: JETTASK_PG_DATABASE)')
    parser.add_argument('--pg-user', type=str, help='PostgreSQL user (env: JETTASK_PG_USER)')
    parser.add_argument('--pg-password', type=str, help='PostgreSQL password (env: JETTASK_PG_PASSWORD)')
    parser.add_argument('--pg-url', type=str, help='PostgreSQL URL (postgresql://user:pass@host:port/db)')


if __name__ == "__main__":
    # 创建主解析器
    parser = argparse.ArgumentParser(description='Jettask WebUI')
    subparsers = parser.add_subparsers(dest='command', help='可用命令', required=True)
    
    # 创建 run 子命令
    run_parser = subparsers.add_parser('run', help='运行WebUI服务器')
    run_parser.add_argument('--port', type=int, default=8080, help='服务器端口')
    run_parser.add_argument('--host', type=str, default='0.0.0.0', help='服务器地址')
    run_parser.add_argument('--with-consumer', action='store_true', help='启动内置的PostgreSQL消费者（默认不启动）')
    add_pg_arguments(run_parser)
    
    # 创建 init 子命令
    init_parser = subparsers.add_parser('init', help='初始化PostgreSQL数据库')
    add_pg_arguments(init_parser)
    
    # 创建 consumer 子命令
    consumer_parser = subparsers.add_parser('consumer', help='运行PostgreSQL消费者')
    add_pg_arguments(consumer_parser)
    consumer_parser.add_argument('--redis-host', type=str, default='localhost', help='Redis主机地址')
    consumer_parser.add_argument('--redis-port', type=int, default=6379, help='Redis端口')
    consumer_parser.add_argument('--redis-db', type=int, default=0, help='Redis数据库')
    consumer_parser.add_argument('--redis-password', type=str, help='Redis密码')
    consumer_parser.add_argument('--node-id', type=str, help='节点ID（用于分布式部署）')
    consumer_parser.add_argument('--prefix', type=str, default='jettask', help='Redis键前缀')
    
    # 解析参数
    args = parser.parse_args()
    
    # 执行相应的命令
    if args.command == 'init':
        # 初始化数据库
        pg_config = parse_pg_config(args)
        asyncio.run(init_database(pg_config))
        
    elif args.command == 'run':
        # 运行服务器
        pg_config = parse_pg_config(args)
        
        # 设置应用配置
        app.state.pg_config = pg_config
        app.state.enable_consumer = args.with_consumer  # 默认不启动，需要显式指定
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        uvicorn.run(app, host=args.host, port=args.port)
        
    elif args.command == 'consumer':
        # 运行独立的PostgreSQL消费者
        pg_config = parse_pg_config(args)
        
        # 解析Redis配置
        redis_config = RedisConfig(
            host=args.redis_host,
            port=args.redis_port,
            db=args.redis_db,
            password=args.redis_password
        )
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 运行消费者
        async def run_consumer():
            consumer = PostgreSQLConsumer(
                pg_config=pg_config,
                redis_config=redis_config,
                prefix=args.prefix,
                node_id=args.node_id
            )
            
            try:
                await consumer.start()
                logging.info(f"PostgreSQL consumer started on node: {consumer.node_id}")
                
                # 保持运行
                while True:
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                logging.info("Received interrupt signal")
            finally:
                await consumer.stop()
                
        asyncio.run(run_consumer())