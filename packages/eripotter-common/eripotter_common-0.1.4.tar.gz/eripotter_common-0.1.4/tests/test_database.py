"""Test database module."""

import pytest
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from eripotter_common.database import (
    Base,
    get_db_engine,
    get_async_db_engine,
    get_session,
    get_async_session,
)

class User(Base):
    """Test user model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

def test_get_db_engine():
    """Test database engine creation."""
    engine = get_db_engine("sqlite:///:memory:")
    assert engine is not None

def test_get_async_db_engine():
    """Test async database engine creation."""
    engine = get_async_db_engine("sqlite+aiosqlite:///:memory:")
    assert engine is not None

def test_session():
    """Test session management."""
    engine = get_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    with get_session() as session:
        assert isinstance(session, Session)
        
        # Test CRUD operations
        user = User(name="test")
        session.add(user)
        session.commit()
        
        result = session.query(User).filter_by(name="test").first()
        assert result is not None
        assert result.name == "test"

@pytest.mark.asyncio
async def test_async_session():
    """Test async session management."""
    engine = get_async_db_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async for session in get_async_session():
        assert isinstance(session, AsyncSession)
        
        # Test CRUD operations
        user = User(name="test")
        session.add(user)
        await session.commit()
        
        result = await session.get(User, 1)
        assert result is not None
        assert result.name == "test"