import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class PostgreSQLConfig:
    """PostgreSQL数据库配置"""
    host: str = "localhost"
    port: int = 5432
    database: str = "jettask"
    user: str = "jettask"
    password: str = "123456"
    
    @classmethod
    def from_env(cls) -> "PostgreSQLConfig":
        """从环境变量中读取配置"""
        return cls(
            host=os.getenv("JETTASK_PG_HOST", "localhost"),
            port=int(os.getenv("JETTASK_PG_PORT", "5432")),
            database=os.getenv("JETTASK_PG_DATABASE", "jettask"),
            user=os.getenv("JETTASK_PG_USER", "jettask"),
            password=os.getenv("JETTASK_PG_PASSWORD", "123456")
        )
    
    @classmethod
    def from_url(cls, url: str) -> "PostgreSQLConfig":
        """从数据库URL中解析配置
        格式: postgresql://user:password@host:port/database
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        return cls(
            host=parsed.hostname or "localhost",
            port=parsed.port or 5432,
            database=parsed.path.lstrip("/") if parsed.path else "jettask",
            user=parsed.username or "jettask",
            password=parsed.password or "123456"
        )
    
    @property
    def dsn(self) -> str:
        """返回asyncpg连接字符串"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def psycopg_dsn(self) -> str:
        """返回psycopg连接字符串"""
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"


@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "RedisConfig":
        """从环境变量中读取配置"""
        return cls(
            host=os.getenv("JETTASK_REDIS_HOST", "localhost"),
            port=int(os.getenv("JETTASK_REDIS_PORT", "6379")),
            db=int(os.getenv("JETTASK_REDIS_DB", "0")),
            password=os.getenv("JETTASK_REDIS_PASSWORD")
        )


@dataclass
class WebUIConfig:
    """WebUI配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    postgres: PostgreSQLConfig = None
    redis: RedisConfig = None
    
    def __post_init__(self):
        if self.postgres is None:
            self.postgres = PostgreSQLConfig.from_env()
        if self.redis is None:
            self.redis = RedisConfig.from_env()