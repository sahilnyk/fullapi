"""Middleware configuration."""

from typing import List, Dict, Any
import os


class MiddlewareConfig:
    """Middleware configuration settings."""
    
    def __init__(self):
        self.cors_origins: List[str] = self._get_cors_origins()
        self.cors_allow_credentials: bool = self._get_bool_env("CORS_ALLOW_CREDENTIALS", False)
        self.cors_allow_methods: List[str] = self._get_list_env("CORS_ALLOW_METHODS", ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        self.cors_allow_headers: List[str] = self._get_list_env("CORS_ALLOW_HEADERS", ["*"])
        self.cors_expose_headers: List[str] = self._get_list_env("CORS_EXPOSE_HEADERS", [])
        
        self.rate_limit_enabled: bool = self._get_bool_env("RATE_LIMIT_ENABLED", False)
        self.rate_limit_requests: int = self._get_int_env("RATE_LIMIT_REQUESTS", 100)
        self.rate_limit_window: int = self._get_int_env("RATE_LIMIT_WINDOW", 60)  # seconds
        
        self.security_headers_enabled: bool = self._get_bool_env("SECURITY_HEADERS_ENABLED", True)
        self.security_headers: Dict[str, str] = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'"
        }
        
        self.trusted_proxy_headers: List[str] = self._get_list_env("TRUSTED_PROXY_HEADERS", ["X-Forwarded-For", "X-Forwarded-Proto"])
        
        self.gzip_enabled: bool = self._get_bool_env("GZIP_ENABLED", True)
        self.gzip_minimum_size: int = self._get_int_env("GZIP_MINIMUM_SIZE", 1000)
        
        self.request_logging_enabled: bool = self._get_bool_env("REQUEST_LOGGING_ENABLED", False)
        self.request_logging_format: str = os.getenv("REQUEST_LOGGING_FORMAT", "%(asctime)s - %(levelname)s - %(message)s")
        self.request_logging_exclude_paths: List[str] = self._get_list_env("REQUEST_LOGGING_EXCLUDE_PATHS", ["/health", "/metrics"])
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable."""
        return os.getenv(key, str(default)).lower() == "true"
    
    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer environment variable."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def _get_list_env(self, key: str, default: List[str]) -> List[str]:
        """Get list environment variable."""
        value = os.getenv(key, "")
        if value:
            return [item.strip() for item in value.split(",")]
        return default
    
    def _get_cors_origins(self) -> List[str]:
        """Get CORS origins from environment."""
        origins = os.getenv("CORS_ORIGINS", "")
        if origins:
            return [origin.strip() for origin in origins.split(",")]
        return ["http://localhost:3000", "http://localhost:8000"]
