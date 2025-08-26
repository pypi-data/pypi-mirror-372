"""
Configuration management for EriPotter services.
"""
import os
from typing import List
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

# Railway가 아니면 .env 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv(find_dotenv())

class DatabaseSettings(BaseModel):
    """데이터베이스 설정"""
    url: str = ""
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30

class Settings(BaseSettings):
    """Global settings for EriPotter services."""
    # Database settings
    DATABASE_URL: str = ""
    SQL_ECHO: bool = False
    
    # CORS settings
    ALLOW_ORIGINS: List[str] = [
        "https://eripotter.com",
        "https://www.eripotter.com",
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # Service settings
    SERVICE_NAME: str = "eripotter-service"
    PORT: int = 8001
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    @property
    def database(self) -> DatabaseSettings:
        """데이터베이스 설정 반환"""
        return DatabaseSettings(
            url=self.DATABASE_URL,
            echo=self.SQL_ECHO
        )

settings = Settings()