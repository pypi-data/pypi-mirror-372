"""Database configuration for EriPotter services."""

from urllib.parse import urlparse
from typing import Optional

from ..www.env import (
    DATABASE_URL,
    ASYNC_DATABASE_URL,
)

# Connection pool settings
POOL_SIZE: int = 5
MAX_OVERFLOW: int = 10
POOL_PRE_PING: bool = True

# Debug settings
ECHO_SQL: bool = False

def is_railway_db(url: str) -> bool:
    """Check if the database URL is from Railway.
    
    Args:
        url: Database URL to check
    
    Returns:
        True if the database is hosted on Railway
    """
    parsed = urlparse(url)
    return any(
        (parsed.hostname or "").endswith(domain)
        for domain in ["proxy.rlwy.net", "railway.app"]
    )

def get_connect_args(url: str) -> dict:
    """Get connection arguments based on the database URL.
    
    Args:
        url: Database URL
    
    Returns:
        Dictionary of connection arguments
    """
    if "sslmode=" not in url and is_railway_db(url):
        return {"sslmode": "require"}
    return {}