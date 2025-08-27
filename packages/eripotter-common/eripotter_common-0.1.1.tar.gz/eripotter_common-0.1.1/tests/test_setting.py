"""Test setting module."""

import os
import pytest
from pydantic import Field

from eripotter_common.setting import BaseSettings, load_env, get_env

def test_load_env(tmp_path):
    """Test loading environment variables from file."""
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_VAR=test_value")
    
    load_env(str(env_file))
    assert os.getenv("TEST_VAR") == "test_value"

def test_get_env():
    """Test getting environment variables."""
    os.environ["TEST_VAR"] = "test_value"
    
    assert get_env("TEST_VAR") == "test_value"
    assert get_env("NON_EXISTENT", default="default") == "default"
    
    with pytest.raises(ValueError):
        get_env("NON_EXISTENT", required=True)

def test_base_settings():
    """Test base settings class."""
    class TestSettings(BaseSettings):
        """Test settings class."""
        database_url: str = Field(..., env="DATABASE_URL")
        api_key: str = Field(None, env="API_KEY")
        debug: bool = Field(False, env="DEBUG")
    
    # Set environment variables
    os.environ["DATABASE_URL"] = "postgresql://localhost/test"
    os.environ["API_KEY"] = "secret"
    os.environ["DEBUG"] = "true"
    
    settings = TestSettings()
    
    assert settings.database_url == "postgresql://localhost/test"
    assert settings.api_key == "secret"
    assert settings.debug is True
    
    # Test dictionary conversion
    settings_dict = settings.dict()
    assert settings_dict["database_url"] == "postgresql://localhost/test"
    assert settings_dict["api_key"] == "secret"
    assert settings_dict["debug"] is True
