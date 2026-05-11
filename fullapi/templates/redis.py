"""Redis caching templates."""

REDIS_CONFIG = '''"""Redis configuration."""

import os
from typing import Optional
import redis
from redis.exceptions import ConnectionError


class RedisConfig:
    """Redis configuration settings."""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        self.redis_ssl = os.getenv("REDIS_SSL", "false").lower() == "true"
        self.redis_decode_responses = os.getenv("REDIS_DECODE_RESPONSES", "true").lower() == "true"
        self.redis_socket_timeout = int(os.getenv("REDIS_SOCKET_TIMEOUT", 5))
        self.redis_socket_connect_timeout = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", 5))
        self.redis_health_check_interval = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", 30))
        self.redis_max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", 10))
    
    def get_redis_url(self) -> str:
        """Get complete Redis URL."""
        if self.redis_url and self.redis_url != "redis://localhost:6379/0":
            return self.redis_url
        
        auth_part = f":{self.redis_password}@" if self.redis_password else ""
        ssl_part = "s" if self.redis_ssl else ""
        return f"redis{ssl_part}://{auth_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"


class RedisClient:
    """Redis client wrapper with connection management."""
    
    def __init__(self, config: Optional[RedisConfig] = None):
        self.config = config or RedisConfig()
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client, creating connection if needed."""
        if not self._connected or self._client is None:
            self._connect()
        return self._client
    
    def _connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._client = redis.Redis(
                from_url=self.config.get_redis_url(),
                decode_responses=self.config.redis_decode_responses,
                socket_timeout=self.config.redis_socket_timeout,
                socket_connect_timeout=self.config.redis_socket_connect_timeout,
                health_check_interval=self.config.redis_health_check_interval,
                max_connections=self.config.redis_max_connections,
            )
            # Test connection
            self._client.ping()
            self._connected = True
        except ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            self._client.close()
        self._connected = False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except ConnectionError:
            return False
    
    def health_check(self) -> dict:
        """Perform Redis health check."""
        try:
            import time
            start_time = time.time()
            info = self.client.info()
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global Redis client instance
redis_client = RedisClient()
'''

REDIS_UTILS = '''"""Redis utility functions."""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import redis
from core.redis_config import redis_client


def cache_key(prefix: str, identifier: str) -> str:
    """Generate cache key with prefix."""
    return f"{prefix}:{identifier}"


def set_cache(
    key: str,
    value: Any,
    expire: Optional[Union[int, timedelta]] = None,
    serialize: bool = True
) -> bool:
    """Set value in Redis cache."""
    try:
        client = redis_client.client
        
        if serialize:
            value = pickle.dumps(value)
        
        if isinstance(expire, timedelta):
            expire = int(expire.total_seconds())
        
        return client.setex(key, expire or 3600, value)  # Default 1 hour
    except Exception:
        return False


def get_cache(
    key: str,
    deserialize: bool = True,
    default: Any = None
) -> Any:
    """Get value from Redis cache."""
    try:
        client = redis_client.client
        value = client.get(key)
        
        if value is None:
            return default
        
        if deserialize:
            return pickle.loads(value)
        
        return value
    except Exception:
        return default


def delete_cache(key: str) -> bool:
    """Delete key from Redis cache."""
    try:
        client = redis_client.client
        return bool(client.delete(key))
    except Exception:
        return False


def clear_cache_pattern(pattern: str) -> int:
    """Clear cache keys matching pattern."""
    try:
        client = redis_client.client
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except Exception:
        return 0


def cache_result(
    key_prefix: str,
    expire: Optional[Union[int, timedelta]] = None,
    serialize: bool = True
):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = get_cache(cache_key, deserialize=serialize)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            set_cache(cache_key, result, expire=expire, serialize=serialize)
            return result
        
        return wrapper
    return decorator


class CacheManager:
    """High-level cache management."""
    
    def __init__(self, prefix: str = "app"):
        self.prefix = prefix
    
    def get(self, identifier: str, default: Any = None) -> Any:
        """Get cached value."""
        key = cache_key(self.prefix, identifier)
        return get_cache(key, default=default)
    
    def set(self, identifier: str, value: Any, expire: Optional[Union[int, timedelta]] = None) -> bool:
        """Set cached value."""
        key = cache_key(self.prefix, identifier)
        return set_cache(key, value, expire=expire)
    
    def delete(self, identifier: str) -> bool:
        """Delete cached value."""
        key = cache_key(self.prefix, identifier)
        return delete_cache(key)
    
    def clear_all(self) -> int:
        """Clear all cache with this prefix."""
        pattern = cache_key(self.prefix, "*")
        return clear_cache_pattern(pattern)
'''

REDIS_ROUTER = '''"""Redis health and management router."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from core.redis_config import redis_client, RedisConfig
from core.redis_utils import CacheManager

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
def redis_health():
    """Check Redis health status."""
    try:
        health_info = redis_client.health_check()
        return health_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis health check failed: {str(e)}"
        )


@router.post("/clear", response_model=Dict[str, Any])
def clear_redis_cache(prefix: str = "app"):
    """Clear Redis cache with given prefix."""
    try:
        cache_manager = CacheManager(prefix)
        deleted_count = cache_manager.clear_all()
        return {
            "message": f"Cleared {deleted_count} cache entries with prefix '{prefix}'",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/info", response_model=Dict[str, Any])
def redis_info():
    """Get Redis server information."""
    try:
        client = redis_client.client
        info = client.info()
        
        # Return relevant information
        return {
            "redis_version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory_human"),
            "uptime_days": info.get("uptime_in_days"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to get Redis info: {str(e)}"
        )


@router.get("/config", response_model=Dict[str, Any])
def redis_config_info():
    """Get current Redis configuration."""
    config = RedisConfig()
    return {
        "redis_url": config.get_redis_url().replace("password", "***") if "password" in config.get_redis_url() else config.get_redis_url(),
        "redis_host": config.redis_host,
        "redis_port": config.redis_port,
        "redis_db": config.redis_db,
        "redis_ssl": config.redis_ssl,
        "redis_decode_responses": config.redis_decode_responses,
        "redis_socket_timeout": config.redis_socket_timeout,
        "redis_max_connections": config.redis_max_connections,
    }
'''

REDIS_DEPS = '''"""Dependencies with Redis support."""

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
'''

REQUIREMENTS_REDIS = """
# Redis caching
redis>=5.0.0
"""

ENV_EXAMPLE_REDIS = """
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false
REDIS_DECODE_RESPONSES=true
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_HEALTH_CHECK_INTERVAL=30
REDIS_MAX_CONNECTIONS=10
"""
