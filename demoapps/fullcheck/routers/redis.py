"""Redis health and management router."""

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
