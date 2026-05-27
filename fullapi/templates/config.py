"""Config template."""

CONFIG = '''from pydantic_settings import BaseSettings
from functools import lru_cache
import secrets
import os


class Settings(BaseSettings):
    APP_NAME: str = "${project_name}"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # JWT - SECURITY: Never use default SECRET_KEY in production!
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate random SECRET_KEY if not set (development only)
        if not self.SECRET_KEY:
            if self.DEBUG:
                self.SECRET_KEY = secrets.token_urlsafe(32)
                print("WARNING: Using auto-generated SECRET_KEY. Set SECRET_KEY in .env for production!")
            else:
                raise ValueError("SECRET_KEY must be set in .env file for production!")


@lru_cache()
def get_settings():
    return Settings()
'''

CONFIG_BASIC = '''from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "${project_name}"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
'''
