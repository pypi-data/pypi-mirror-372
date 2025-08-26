"""Configuration management for EriPotter services."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    """Database connection settings."""
    url: str = Field(..., description="Database connection URL")
    echo: bool = Field(False, description="Enable SQL query logging")
    pool_size: int = Field(5, description="Connection pool size")
    max_overflow: int = Field(10, description="Maximum number of connections that can be created beyond pool_size")
    pool_timeout: int = Field(30, description="Number of seconds to wait before giving up on getting a connection from the pool")

class LogSettings(BaseModel):
    """Logging settings."""
    level: str = Field("INFO", description="Logging level")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    json_format: bool = Field(False, description="Use JSON format for logging")

class Settings(BaseSettings):
    """Global settings for EriPotter services."""
    app_name: str = Field(..., description="Application name")
    environment: str = Field("development", description="Deployment environment")
    debug: bool = Field(False, description="Debug mode")
    
    # Database settings
    database: DatabaseSettings
    
    # Logging settings
    logging: LogSettings = Field(default_factory=LogSettings)
    
    # Custom settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom settings")

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

def get_settings() -> Settings:
    """Get application settings from environment variables."""
    return Settings()
