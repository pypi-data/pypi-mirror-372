"""EriPotter Common Library

This library provides common utilities for EriPotter microservices:
- Database management with SQLAlchemy
- Security utilities (password hashing, JWT tokens)
- Web service utilities (API keys, settings)
"""

from . import database
from . import security
from . import www

__version__ = "0.1.0"

__all__ = [
    "database",
    "security",
    "www",
]