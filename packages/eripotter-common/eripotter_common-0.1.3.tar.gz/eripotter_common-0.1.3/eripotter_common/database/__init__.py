"""Database utilities for EriPotter microservices."""

from .base import (
    Base,
    engine,
    async_engine,
    get_database_url,
    get_db_engine,
    get_async_db_engine,
)
from .session import (
    Session,
    AsyncSession,
    get_session,
    get_async_session,
)
from .config import (
    DATABASE_URL,
    ASYNC_DATABASE_URL,
    POOL_SIZE,
    MAX_OVERFLOW,
    ECHO_SQL,
    POOL_PRE_PING,
    is_railway_db,
    get_connect_args,
)

__all__ = [
    # Base classes and engines
    "Base",
    "engine",
    "async_engine",
    
    # Database functions
    "get_database_url",
    "get_db_engine",
    "get_async_db_engine",
    
    # Session management
    "Session",
    "AsyncSession",
    "get_session",
    "get_async_session",
    
    # Configuration
    "DATABASE_URL",
    "ASYNC_DATABASE_URL",
    "POOL_SIZE",
    "MAX_OVERFLOW",
    "ECHO_SQL",
    "POOL_PRE_PING",
    "is_railway_db",
    "get_connect_args",
]