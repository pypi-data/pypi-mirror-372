"""
데이터베이스 연결 및 엔진 생성 유틸리티
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings

logger = logging.getLogger("db")

class Base(DeclarativeBase):
    """Base class for all models."""
    pass

def get_database_url() -> str:
    """데이터베이스 URL 반환"""
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    
    url = settings.DATABASE_URL
    
    # SQLite URL을 비동기 형식으로 변환
    if url.startswith("sqlite"):
        url = url.replace("sqlite:", "sqlite+aiosqlite:")
    # PostgreSQL URL을 비동기 형식으로 변환
    elif url.startswith("postgresql"):
        url = url.replace("postgresql:", "postgresql+asyncpg:")
    
    return url

class AsyncDatabase:
    """비동기 데이터베이스 연결 관리자"""
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.async_session: async_sessionmaker[AsyncSession] | None = None

    async def initialize(self) -> None:
        """데이터베이스 엔진 및 세션 초기화"""
        if self.engine is not None:
            return

        url = get_database_url()
        parsed = urlparse(url)
        logger.info(f"DB → {parsed.scheme}://{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}")
        
        connect_args = {}
        # Railway Postgres일 때 sslmode=require 자동 부여
        if "sslmode=" not in url and (
            (parsed.hostname or "").endswith("proxy.rlwy.net")
            or (parsed.hostname or "").endswith("railway.app")
        ):
            connect_args["sslmode"] = "require"
        
        self.engine = create_async_engine(
            url,
            pool_pre_ping=True,
            connect_args=connect_args,
            echo=settings.SQL_ECHO,
        )
        
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """데이터베이스 세션 컨텍스트 매니저"""
        if self.async_session is None:
            await self.initialize()
        
        async with self.async_session() as session:  # type: ignore
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.async_session = None

# 전역 데이터베이스 인스턴스
db = AsyncDatabase()