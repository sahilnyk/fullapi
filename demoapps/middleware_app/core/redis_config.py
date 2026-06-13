"""Redis configuration."""

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
