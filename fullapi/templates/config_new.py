"""Config template with enhanced settings."""

CONFIG = '''"""Application configuration settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal
import secrets
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "${project_name}"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "FastAPI application"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = True
    
    # Gzip Compression
    GZIP_ENABLED: bool = True
    GZIP_MINIMUM_SIZE: int = 1000
    
    # Request ID
    REQUEST_ID_ENABLED: bool = True
    REQUEST_ID_HEADER: str = "X-Request-ID"
    
    # Request Logging
    REQUEST_LOGGING_ENABLED: bool = False
    REQUEST_LOGGING_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    REQUEST_LOGGING_EXCLUDE_PATHS: list[str] = ["/health", "/metrics"]
    
    # Trusted Proxy
    TRUSTED_PROXY_HEADERS: list[str] = ["X-Forwarded-For", "X-Forwarded-Proto"]
    
    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate random SECRET_KEY if not set (development only)
        if not self.SECRET_KEY:
            if self.DEBUG or self.ENVIRONMENT == "development":
                self.SECRET_KEY = secrets.token_urlsafe(32)
                print("⚠️  WARNING: Using auto-generated SECRET_KEY. Set SECRET_KEY in .env for production!")
            else:
                raise ValueError("SECRET_KEY must be set in .env file for production!")


@lru_cache()
def get_settings():
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
'''

CONFIG_BASIC = '''"""Application configuration settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "${project_name}"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "FastAPI application"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings():
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
'''
