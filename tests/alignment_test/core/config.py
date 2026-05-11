from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "tests/alignment_test"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
