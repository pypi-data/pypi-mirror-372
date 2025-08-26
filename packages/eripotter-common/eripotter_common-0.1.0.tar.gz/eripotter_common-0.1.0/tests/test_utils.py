"""Test utilities for EriPotter common package."""

import pytest
from app.db import AsyncDatabase, DatabaseConfig, Base
from app.http import AsyncHTTPClient, HTTPClientConfig
from sqlalchemy import Column, Integer, String

# Test database model
class TestUser(Base):
    __tablename__ = "test_users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String)

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection."""
    config = DatabaseConfig(
        url="sqlite+aiosqlite:///:memory:",
        echo=True
    )
    db = AsyncDatabase(config)
    
    async with db.get_session() as session:
        assert session is not None
    
    await db.close()

@pytest.mark.asyncio
async def test_http_client():
    """Test HTTP client."""
    config = HTTPClientConfig(
        base_url="https://httpbin.org",
        timeout=5.0
    )
    client = AsyncHTTPClient(config)
    
    response = await client.get("/get")
    assert response.status_code == 200
    
    await client.close()
