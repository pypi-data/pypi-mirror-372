"""Base module for database operations."""

import logging
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase

from .config import (
    DATABASE_URL,
    ASYNC_DATABASE_URL,
    POOL_SIZE,
    MAX_OVERFLOW,
    ECHO_SQL,
    POOL_PRE_PING,
    get_connect_args,
)

logger = logging.getLogger("eripotter.database")

class Base(DeclarativeBase):
    """Base class for all models."""
    pass

def get_database_url() -> str:
    """데이터베이스 URL 반환"""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    return DATABASE_URL

def get_db_engine(url: str = None) -> Engine:
    """데이터베이스 엔진 생성
    
    Args:
        url: Optional database URL. If not provided, uses default DATABASE_URL
    
    Returns:
        SQLAlchemy Engine instance
    """
    url = url or get_database_url()
    parsed = urlparse(url)
    logger.info(
        f"DB → {parsed.scheme}://{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
    )
    
    return create_engine(
        url,
        echo=ECHO_SQL,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_pre_ping=POOL_PRE_PING,
        connect_args=get_connect_args(url),
    )

def get_async_db_engine(url: str = None) -> AsyncEngine:
    """비동기 데이터베이스 엔진 생성
    
    Args:
        url: Optional database URL. If not provided, uses default ASYNC_DATABASE_URL
    
    Returns:
        SQLAlchemy AsyncEngine instance
    """
    url = url or ASYNC_DATABASE_URL
    parsed = urlparse(url)
    logger.info(
        f"AsyncDB → {parsed.scheme}://{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
    )
    
    return create_async_engine(
        url,
        echo=ECHO_SQL,
        pool_pre_ping=POOL_PRE_PING,
        connect_args=get_connect_args(url),
    )

# Default engines
engine = get_db_engine()
async_engine = get_async_db_engine()