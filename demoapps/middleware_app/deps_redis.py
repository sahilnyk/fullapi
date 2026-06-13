"""Dependencies with Redis support."""

from typing import Generator
from sqlalchemy.orm import Session
from db.session import get_db
from core.redis_config import redis_client


def get_redis_client():
    """Get Redis client dependency."""
    try:
        return redis_client.client
    except Exception:
        # Return None if Redis is not available
        return None


def get_cache_manager(prefix: str = "app"):
    """Get cache manager dependency."""
    from core.redis_utils import CacheManager
    return CacheManager(prefix)


# Existing database dependency
def get_db_session() -> Generator[Session, None, None]:
    """Get database session."""
    db = get_db()
    try:
        yield db
    finally:
        db.close()
