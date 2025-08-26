"""EriPotter Common Utilities

This package provides common utilities for EriPotter microservices including:
- Configuration management
- Database connections
- Security utilities
- FastAPI extensions
- Logging utilities
"""

__version__ = "0.1.0"

from app.config import settings
from app.db import Base, AsyncDatabase, db
from app.security import hash_password, verify_password
from app.fastapi_ext import create_app, get_session, health_check, lifespan
from app.logging import setup_logging, get_logger

__all__ = [
    # Settings
    "settings",
    
    # Database
    "Base",
    "AsyncDatabase",
    "db",
    
    # Security
    "hash_password",
    "verify_password",
    
    # FastAPI
    "create_app",
    "get_session",
    "health_check",
    "lifespan",
    
    # Logging
    "setup_logging",
    "get_logger",
]