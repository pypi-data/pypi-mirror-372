#!/usr/bin/env python
"""
JetTask CLI - 命令行接口
"""
import click
import sys
import os
import importlib
import importlib.util
import json
from pathlib import Path

# 处理相对导入和直接运行的情况
try:
    from .app_importer import import_app, AppImporter
except ImportError:
    # 如果相对导入失败，添加父目录到路径并尝试绝对导入
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from jettask.core.app_importer import import_app, AppImporter

@click.group()
@click.version_option(version='0.1.0', prog_name='JetTask')
def cli():
    """JetTask - 高性能分布式任务队列系统"""
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='服务器监听地址')
@click.option('--port', default=8001, type=int, help='服务器监听端口')
def webui(host, port):
    """启动 Web UI 监控界面"""
    from jettask.webui.backend.main import run_server
    click.echo(f"Starting JetTask Web UI on {host}:{port}")
    
    # 修改端口设置
    import uvicorn
    uvicorn.run(
        "jettask.webui.backend.main:app",
        host=host,
        port=port,
        log_level="info"
    )

def load_module_from_path(module_path: str):
    """从文件路径加载 Python 模块"""
    path = Path(module_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")
    
    # 获取模块名
    module_name = path.stem
    
    # 加载模块
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Cannot load module from {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return module

def find_jettask_app(module):
    """在模块中查找 Jettask 实例"""
    from jettask import Jettask
    
    # 查找模块中的 Jettask 实例
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, Jettask):
            return obj
    
    # 如果没有找到，尝试查找名为 'app' 的变量
    if hasattr(module, 'app'):
        obj = getattr(module, 'app')
        if isinstance(obj, Jettask):
            return obj
    
    return None

@cli.command()
@click.argument('app_str', required=False, default=None)
@click.option('--queues', '-q', help='队列名称（逗号分隔，如: queue1,queue2）')
@click.option('--executor', '-e', 
              type=click.Choice(['asyncio', 'multi_asyncio']),
              default='asyncio',
              help='执行器类型')
@click.option('--concurrency', '-c', type=int, default=4, help='并发数')
@click.option('--prefetch', '-p', type=int, default=100, help='预取倍数')
@click.option('--reload', '-r', is_flag=True, help='自动重载')
@click.option('--config', help='配置文件 (JSON格式)')
def worker(app_str, queues, executor, concurrency, prefetch, reload, config):
    """启动任务处理 Worker
    
    示例:
    \b
      # 显式指定 app
      jettask worker main:app --queues async_queue
      jettask worker tasks.py:app --queues queue1,queue2
      jettask worker myapp.tasks --queues high,normal,low
      
      # 自动发现 app（从当前目录的 app.py 或 main.py）
      jettask worker --queues async_queue
      
      # 使用环境变量
      export JETTASK_APP=myapp:app
      jettask worker --queues async_queue
    """
    
    # 如果提供了配置文件，从中加载配置
    if config:
        click.echo(f"Loading configuration from {config}")
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        # 从配置文件读取参数（命令行参数优先）
        queues = queues or ','.join(config_data.get('queues', [])) if config_data.get('queues') else None
        executor = executor or config_data.get('executor', 'asyncio')
        concurrency = concurrency if concurrency != 4 else config_data.get('concurrency', 4)
        prefetch = prefetch if prefetch != 100 else config_data.get('prefetch', 100)
        reload = reload or config_data.get('reload', False)
    
    # 加载应用
    try:
        if app_str:
            click.echo(f"Loading app from: {app_str}")
            app = import_app(app_str)
        else:
            click.echo("Auto-discovering Jettask app...")
            click.echo("Searching in: app.py, main.py, server.py, worker.py")
            app = import_app()  # 自动发现
        
        # 显示应用信息
        app_info = AppImporter.get_app_info(app)
        click.echo(f"\nFound Jettask app:")
        click.echo(f"  Tasks: {app_info['tasks']} registered")
        if app_info.get('task_names') and app_info['tasks'] > 0:
            task_preview = app_info['task_names'][:3]
            click.echo(f"  Names: {', '.join(task_preview)}" + 
                      (f" (+{app_info['tasks'] - 3} more)" if app_info['tasks'] > 3 else ""))
    except ImportError as e:
        import traceback
        click.echo(f"Error: Failed to import app: {e}", err=True)
        
        # 始终显示完整的堆栈跟踪，帮助用户定位问题
        click.echo("\n" + "=" * 60, err=True)
        click.echo("Full traceback:", err=True)
        click.echo("=" * 60, err=True)
        traceback.print_exc()
        click.echo("=" * 60, err=True)
        
        click.echo("\nTips:", err=True)
        click.echo("  - Check if there are syntax errors in your code", err=True)
        click.echo("  - Verify all imports in your module are available", err=True)
        click.echo("  - Specify app location: jettask worker myapp:app", err=True)
        click.echo("  - Or set environment variable: export JETTASK_APP=myapp:app", err=True)
        click.echo("  - Or ensure app.py or main.py exists in current directory", err=True)
        sys.exit(1)
    except Exception as e:
        import traceback
        click.echo(f"Error loading app: {e}", err=True)
        
        # 对于所有异常都显示堆栈信息
        click.echo("\n" + "=" * 60, err=True)
        click.echo("Full traceback:", err=True)
        click.echo("=" * 60, err=True)
        traceback.print_exc()
        click.echo("=" * 60, err=True)
        
        click.echo("\nThis might be a bug in JetTask or your application.", err=True)
        click.echo("Please check the traceback above for details.", err=True)
        sys.exit(1)
    
    # 处理队列参数
    if queues:
        # 解析队列列表（支持逗号分隔）
        queue_list = [q.strip() for q in queues.split(',') if q.strip()]
    else:
        # 如果没有指定队列，尝试从 app 获取
        if hasattr(app, 'ep') and hasattr(app.ep, 'queues'):
            queue_list = list(app.ep.queues)
            if queue_list:
                click.echo(f"Using queues from app: {', '.join(queue_list)}")
        else:
            queue_list = []
    
    if not queue_list:
        click.echo("Error: No queues specified", err=True)
        click.echo("  Use --queues to specify queues, e.g.: --queues queue1,queue2", err=True)
        click.echo("  Or define queues in your app configuration", err=True)
        sys.exit(1)
    
    # 从 app 实例中获取实际配置
    redis_url = app.redis_url if hasattr(app, 'redis_url') else 'Not configured'
    redis_prefix = app.redis_prefix if hasattr(app, 'redis_prefix') else 'jettask'
    consumer_strategy = app.consumer_strategy if hasattr(app, 'consumer_strategy') else 'heartbeat'
    
    # 显示配置信息
    click.echo("=" * 60)
    click.echo("JetTask Worker Configuration")
    click.echo("=" * 60)
    click.echo(f"App:          {app_str}")
    click.echo(f"Redis URL:    {redis_url}")
    click.echo(f"Redis Prefix: {redis_prefix}")
    click.echo(f"Strategy:     {consumer_strategy}")
    click.echo(f"Queues:       {', '.join(queue_list)}")
    click.echo(f"Executor:     {executor}")
    click.echo(f"Concurrency:  {concurrency}")
    click.echo(f"Prefetch:     {prefetch}")
    click.echo(f"Auto-reload:  {reload}")
    click.echo("=" * 60)
    
    # 启动 Worker
    try:
        click.echo(f"Starting {executor} worker...")
        app.start(
            execute_type=executor,
            queues=queue_list,
            concurrency=concurrency,
            prefetch_multiplier=prefetch,
            reload=reload
        )
    except KeyboardInterrupt:
        click.echo("\nShutting down worker...")
    except Exception as e:
        click.echo(f"Error starting worker: {e}", err=True)
        sys.exit(1)

@cli.command('webui-consumer')
@click.option('--pg-url', help='PostgreSQL URL (optional, will use env var if not provided)')
def webui_consumer(pg_url):
    """启动 Web UI 数据消费者（同步 Redis 数据到 PostgreSQL）"""
    click.echo("Starting WebUI Consumer...")
    
    import os
    if pg_url:
        os.environ['JETTASK_PG_URL'] = pg_url
    
    # 启动 pg_consumer (它会从环境变量读取 Redis 配置)
    from jettask.webui.pg_consumer import main as consumer_main
    consumer_main()

@cli.command()
def monitor():
    """启动系统监控器"""
    click.echo("Starting JetTask Monitor")
    from jettask.webui.run_monitor import main as monitor_main
    monitor_main()

@cli.command()
def init():
    """初始化数据库和配置"""
    click.echo("Initializing JetTask...")
    
    # 初始化数据库
    from jettask.webui.db_init import init_database
    click.echo("Initializing database...")
    init_database()
    
    click.echo("JetTask initialized successfully!")

@cli.command()
def status():
    """显示系统状态"""
    click.echo("JetTask System Status")
    click.echo("=" * 50)
    
    # 检查 Redis 连接
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        click.echo("✓ Redis: Connected")
    except:
        click.echo("✗ Redis: Not connected")
    
    # 检查 PostgreSQL 连接
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.getenv('JETTASK_PG_DB', 'jettask'),
            user=os.getenv('JETTASK_PG_USER', 'jettask'),
            password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
            host=os.getenv('JETTASK_PG_HOST', 'localhost'),
            port=os.getenv('JETTASK_PG_PORT', '5432')
        )
        conn.close()
        click.echo("✓ PostgreSQL: Connected")
    except:
        click.echo("✗ PostgreSQL: Not connected")
    
    click.echo("=" * 50)

@cli.command()
@click.argument('app_str', required=False, default=None)
@click.option('--interval', '-i', type=float, default=None, 
              help='检查间隔（秒），默认使用app配置')
@click.option('--batch-size', '-b', type=int, default=None,
              help='每批处理的最大任务数，默认使用app配置')
@click.option('--pg-url', '-p', envvar='JETTASK_PG_URL',
              help='PostgreSQL 连接 URL（或设置 JETTASK_PG_URL 环境变量）')
@click.option('--redis-url', '-r', envvar='REDIS_URL',
              help='Redis 连接 URL（或设置 REDIS_URL 环境变量）')
@click.option('--debug', is_flag=True, help='启用调试模式')
def scheduler(app_str, interval, batch_size, pg_url, redis_url, debug):
    """启动定时任务调度器
    
    示例:
    \b
      # 显式指定 app
      jettask scheduler main:app
      jettask scheduler tasks.py:app --interval 30
      
      # 自动发现 app
      jettask scheduler
      
      # 使用环境变量
      export JETTASK_APP=myapp:app
      export JETTASK_PG_URL=postgresql://user:pass@localhost/db
      jettask scheduler
    """
    import asyncio
    
    # 处理相对导入
    try:
        from ..scheduler.scheduler import TaskScheduler
        from ..scheduler.manager import ScheduledTaskManager
    except ImportError:
        # 直接运行时使用绝对导入
        from jettask.scheduler.scheduler import TaskScheduler
        from jettask.scheduler.manager import ScheduledTaskManager
    
    # 设置日志级别
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # 加载应用
    try:
        if app_str:
            click.echo(f"Loading app from: {app_str}")
            app = import_app(app_str)
        else:
            click.echo("Auto-discovering Jettask app...")
            click.echo("Searching in: app.py, main.py, server.py, worker.py")
            app = import_app()  # 自动发现
        
        # 显示应用信息
        app_info = AppImporter.get_app_info(app)
        click.echo(f"\nFound Jettask app:")
        click.echo(f"  Tasks: {app_info['tasks']} registered")
        if app_info.get('task_names') and app_info['tasks'] > 0:
            task_preview = app_info['task_names'][:3]
            click.echo(f"  Names: {', '.join(task_preview)}" + 
                      (f" (+{app_info['tasks'] - 3} more)" if app_info['tasks'] > 3 else ""))
    except ImportError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nTips:", err=True)
        click.echo("  - Specify app location: jettask scheduler myapp:app", err=True)
        click.echo("  - Or set environment variable: export JETTASK_APP=myapp:app", err=True)
        click.echo("  - Or ensure app.py or main.py exists in current directory", err=True)
        sys.exit(1)
    except Exception as e:
        import traceback
        click.echo(f"Error loading app: {e}", err=True)
        if debug:
            traceback.print_exc()
        sys.exit(1)
    
    # 获取配置
    # 优先级：命令行参数 > 环境变量 > app 配置
    redis_url = redis_url or getattr(app, 'redis_url', 'redis://localhost:6379/0')
    pg_url = pg_url or getattr(app, 'pg_url', None)
    
    # 从app的scheduler_config获取默认值
    scheduler_config = getattr(app, 'scheduler_config', {})
    if interval is None:
        interval = scheduler_config.get('scan_interval', 0.1)
    if batch_size is None:
        batch_size = scheduler_config.get('batch_size', 100)
    
    # 显示配置信息
    click.echo("\n" + "=" * 60)
    click.echo("JetTask Scheduler Configuration")
    click.echo("=" * 60)
    click.echo(f"App:          {app_str or 'auto-discovered'}")
    click.echo(f"Redis URL:    {redis_url}")
    click.echo(f"PostgreSQL:   {pg_url or 'Not configured'}")
    if pg_url and not (pg_url.startswith('postgresql://') or pg_url.startswith('postgres://')):
        click.echo(f"  Source:     From app configuration")
    click.echo(f"Interval:     {interval} seconds (from {'CLI' if '--interval' in sys.argv else 'app config'})")
    click.echo(f"Batch Size:   {batch_size} (from {'CLI' if '--batch-size' in sys.argv else 'app config'})")
    click.echo(f"Debug:        {'Enabled' if debug else 'Disabled'}")
    click.echo("=" * 60)
    
    # 检查 PostgreSQL 配置
    if not pg_url:
        click.echo("\n" + "=" * 60)
        click.echo("ERROR: PostgreSQL configuration is required for scheduler")
        click.echo("=" * 60)
        click.echo("\nThe scheduler requires PostgreSQL to:")
        click.echo("  • Store scheduled task definitions")
        click.echo("  • Track task execution history")
        click.echo("  • Manage cron schedules")
        click.echo("\nPlease configure PostgreSQL using one of these methods:")
        click.echo("\n1. Command line option:")
        click.echo("   jettask scheduler --pg-url postgresql://user:pass@localhost/db")
        click.echo("\n2. Environment variable:")
        click.echo("   export JETTASK_PG_URL=postgresql://user:pass@localhost/db")
        click.echo("   jettask scheduler")
        click.echo("\n3. Example with local PostgreSQL:")
        click.echo("   jettask scheduler --pg-url postgresql://jettask:123456@localhost/jettask")
        click.echo("=" * 60)
        sys.exit(1)
    
    # 创建调度器实例
    click.echo("\nUsing PostgreSQL for scheduled task management")
    manager = ScheduledTaskManager(pg_url)
    scheduler_instance = TaskScheduler(
        app=app,
        redis_url=redis_url,
        db_manager=manager,
        scan_interval=interval,
        batch_size=batch_size
    )
    
    # 运行调度器
    async def run_scheduler():
        """运行调度器的异步函数"""
        try:
            click.echo("\nStarting scheduler...")
            # 先连接
            await scheduler_instance.connect()
            # 然后运行
            await scheduler_instance.run()
        except KeyboardInterrupt:
            click.echo("\nReceived shutdown signal, stopping scheduler...")
        except Exception as e:
            click.echo(f"\nScheduler error: {e}", err=True)
            if debug:
                import traceback
                traceback.print_exc()
        finally:
            # 停止调度器
            scheduler_instance.stop()
            
            # 强制清理leader锁
            if scheduler_instance.is_leader and scheduler_instance.redis:
                try:
                    leader_key = f"{scheduler_instance.redis_prefix}:leader"
                    await scheduler_instance.redis.delete(leader_key)
                    click.echo("Leader lock cleaned up")
                except Exception as e:
                    click.echo(f"Failed to cleanup leader lock: {e}", err=True)
            
            # 确保断开连接
            await scheduler_instance.disconnect()
            click.echo("Scheduler stopped")
    
    # 启动事件循环
    try:
        asyncio.run(run_scheduler())
    except KeyboardInterrupt:
        click.echo("\nScheduler shutdown complete")
    except Exception as e:
        click.echo(f"Fatal error: {e}", err=True)
        sys.exit(1)

def main():
    """主入口函数"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()