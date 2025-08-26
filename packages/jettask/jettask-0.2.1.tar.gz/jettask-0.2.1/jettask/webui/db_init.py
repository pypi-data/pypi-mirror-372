"""数据库初始化工具"""

import asyncio
import logging
import sys
from pathlib import Path

import asyncpg
from asyncpg.exceptions import PostgresError

from jettask.webui.config import PostgreSQLConfig

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self, pg_config: PostgreSQLConfig):
        self.pg_config = pg_config
        self.schema_path = Path(__file__).parent / "schema.sql"
        
    async def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            logger.info(f"正在测试数据库连接: {self.pg_config.host}:{self.pg_config.port}/{self.pg_config.database}")
            
            conn = await asyncpg.connect(self.pg_config.dsn)
            await conn.close()
            
            logger.info("✓ 数据库连接成功")
            return True
            
        except Exception as e:
            logger.error(f"✗ 数据库连接失败: {e}")
            return False
            
    async def create_database(self) -> bool:
        """创建数据库（如果不存在）"""
        try:
            # 连接到默认的postgres数据库
            admin_dsn = f"postgresql://{self.pg_config.user}:{self.pg_config.password}@{self.pg_config.host}:{self.pg_config.port}/postgres"
            conn = await asyncpg.connect(admin_dsn)
            
            # 检查数据库是否存在
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)",
                self.pg_config.database
            )
            
            if not exists:
                logger.info(f"正在创建数据库: {self.pg_config.database}")
                await conn.execute(f'CREATE DATABASE "{self.pg_config.database}"')
                logger.info("✓ 数据库创建成功")
            else:
                logger.info(f"✓ 数据库已存在: {self.pg_config.database}")
                
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"✗ 创建数据库失败: {e}")
            logger.info("请确保您有创建数据库的权限，或手动创建数据库")
            return False
            
    async def init_schema(self) -> bool:
        """初始化数据库架构"""
        try:
            if not self.schema_path.exists():
                logger.error(f"✗ Schema文件不存在: {self.schema_path}")
                return False
                
            logger.info("正在读取schema文件...")
            schema_sql = self.schema_path.read_text()
            
            logger.info("正在初始化数据库表结构...")
            conn = await asyncpg.connect(self.pg_config.dsn)
            
            # 执行schema
            await conn.execute(schema_sql)
            
            # 验证表是否创建成功
            tables = await conn.fetch("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN ('tasks', 'queue_stats', 'workers')
                ORDER BY tablename
            """)
            
            created_tables = [row['tablename'] for row in tables]
            logger.info(f"✓ 成功创建表: {', '.join(created_tables)}")
            
            # 显示表结构信息
            for table in created_tables:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                logger.info(f"  - {table}: {count} 条记录")
                
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"✗ 初始化schema失败: {e}")
            return False
            
    async def check_permissions(self) -> bool:
        """检查用户权限"""
        try:
            conn = await asyncpg.connect(self.pg_config.dsn)
            
            # 检查基本权限
            permissions = await conn.fetch("""
                SELECT has_table_privilege($1, 'tasks', 'SELECT') as can_select,
                       has_table_privilege($1, 'tasks', 'INSERT') as can_insert,
                       has_table_privilege($1, 'tasks', 'UPDATE') as can_update,
                       has_table_privilege($1, 'tasks', 'DELETE') as can_delete
            """, self.pg_config.user)
            
            if permissions:
                perm = permissions[0]
                logger.info(f"✓ 用户权限检查:")
                logger.info(f"  - SELECT: {'✓' if perm['can_select'] else '✗'}")
                logger.info(f"  - INSERT: {'✓' if perm['can_insert'] else '✗'}")
                logger.info(f"  - UPDATE: {'✓' if perm['can_update'] else '✗'}")
                logger.info(f"  - DELETE: {'✓' if perm['can_delete'] else '✗'}")
                
            await conn.close()
            return True
            
        except Exception as e:
            logger.warning(f"权限检查失败: {e}")
            return True  # 不阻止继续
            
    async def run(self) -> bool:
        """运行完整的初始化流程"""
        logger.info("=" * 50)
        logger.info("开始初始化PostgreSQL数据库")
        logger.info("=" * 50)
        
        # 1. 创建数据库（如果需要）
        if not await self.create_database():
            return False
            
        # 2. 测试连接
        if not await self.test_connection():
            return False
            
        # 3. 初始化schema
        if not await self.init_schema():
            return False
            
        # 4. 检查权限
        await self.check_permissions()
        
        logger.info("=" * 50)
        logger.info("✓ 数据库初始化完成！")
        logger.info("=" * 50)
        logger.info("")
        logger.info("您现在可以启动WebUI:")
        logger.info(f"  python -m jettask.webui --pg-url {self.pg_config.dsn}")
        logger.info("")
        
        return True


async def init_database_async(pg_config: PostgreSQLConfig):
    """初始化数据库的异步入口函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    initializer = DatabaseInitializer(pg_config)
    success = await initializer.run()
    
    if not success:
        sys.exit(1)

def init_database():
    """初始化数据库的同步入口函数（供 CLI 使用）"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # 从环境变量读取配置
    pg_config = PostgreSQLConfig(
        host=os.getenv('JETTASK_PG_HOST', 'localhost'),
        port=int(os.getenv('JETTASK_PG_PORT', '5432')),
        database=os.getenv('JETTASK_PG_DB', 'jettask'),
        user=os.getenv('JETTASK_PG_USER', 'jettask'),
        password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
    )
    
    asyncio.run(init_database_async(pg_config))