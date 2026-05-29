"""Redis utility functions."""

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
