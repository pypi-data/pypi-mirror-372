"""Session management utilities."""

from contextlib import contextmanager
from typing import Generator, AsyncGenerator

from sqlalchemy.orm import Session as SQLAlchemySession, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from .base import engine, async_engine

# Create session factories
Session = sessionmaker(bind=engine)
AsyncSession = sessionmaker(bind=async_engine, class_=AsyncSession)

@contextmanager
def get_session() -> Generator[SQLAlchemySession, None, None]:
    """Get a database session.
    
    Yields:
        SQLAlchemy Session instance
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.
    
    Yields:
        SQLAlchemy AsyncSession instance
    """
    session = AsyncSession()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()