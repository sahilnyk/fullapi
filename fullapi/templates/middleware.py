"""Middleware templates."""

MIDDLEWARE_CONFIG = '''"""Middleware configuration."""

from typing import List, Dict, Any
import os


class MiddlewareConfig:
    """Middleware configuration settings."""
    
    def __init__(self):
        self.cors_origins: List[str] = self._get_cors_origins()
        self.cors_allow_credentials: bool = self._get_bool_env("CORS_ALLOW_CREDENTIALS", False)
        self.cors_allow_methods: List[str] = self._get_list_env("CORS_ALLOW_METHODS", ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        self.cors_allow_headers: List[str] = self._get_list_env("CORS_ALLOW_HEADERS", ["Content-Type", "Authorization", "X-Request-ID"])
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
'''


MIDDLEWARE_CORS = '''"""CORS middleware configuration."""

from fastapi.middleware.cors import CORSMiddleware
from core.middleware_config import MiddlewareConfig


def create_cors_middleware(config: MiddlewareConfig):
    """Create CORS middleware with configuration."""
    return CORSMiddleware(
        allow_origins=config.cors_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=config.cors_allow_methods,
        allow_headers=config.cors_allow_headers,
        expose_headers=config.cors_expose_headers,
    )
'''


MIDDLEWARE_RATE_LIMIT = '''"""Rate limiting middleware."""

from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import asyncio
from collections import defaultdict, deque


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, requests: int = 100, window: int = 60):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.clients = defaultdict(lambda: deque)
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        if not self.rate_limit_enabled:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        now = time.time()
        
        # Clean old requests
        client_requests = self.clients[client_id]
        while client_requests and client_requests[0] <= now - self.window:
            client_requests.popleft()
        
        # Check rate limit
        recent_requests = [req_time for req_time in client_requests if req_time > now - self.window]
        
        if len(recent_requests) >= self.requests:
            error_content = "Rate limit exceeded"
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": error_content,
                    "limit": self.requests,
                    "window": self.window,
                    "retry_after": int(self.window - (now - recent_requests[-1]))
                }
            )
        
        # Add current request
        client_requests.append(now)
        self.clients[client_id] = client_requests
        
        response = await call_next(request)
        
        # Add rate limit headers
        if hasattr(response, 'headers'):
            response.headers["X-RateLimit-Limit"] = str(self.requests)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests - len(recent_requests)))
            response.headers["X-RateLimit-Reset"] = str(int(now + self.window))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try different methods to identify client
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host
'''


MIDDLEWARE_SECURITY = '''"""Security headers middleware."""

from typing import Dict, Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.middleware_config import MiddlewareConfig


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware."""
    
    def __init__(self, app, config: Optional[MiddlewareConfig] = None):
        super().__init__(app)
        self.config = config or MiddlewareConfig()
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        if not self.config.security_headers_enabled:
            return await call_next(request)
        
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.config.security_headers.items():
            response.headers[header] = value

        return response
'''


MIDDLEWARE_GZIP = '''"""Gzip compression middleware."""

from typing import Optional
from starlette.middleware.gzip import GZipMiddleware
from core.middleware_config import MiddlewareConfig


def create_gzip_middleware(config: Optional[MiddlewareConfig] = None):
    """Create Gzip middleware with configuration."""
    middleware_config = config or MiddlewareConfig()

    return GZipMiddleware(
        minimum_size=middleware_config.gzip_minimum_size,
    )
'''


MIDDLEWARE_LOGGING = '''"""Request logging middleware."""

from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import logging
import time
import json
from core.middleware_config import MiddlewareConfig


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware."""
    
    def __init__(self, app, config: Optional[MiddlewareConfig] = None):
        super().__init__(app)
        self.config = config or MiddlewareConfig()
        
        # Configure logger
        self.logger = logging.getLogger("request_logger")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(self.config.request_logging_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def dispatch(self, request: Request, call_next):
        """Log request information."""
        if not self.config.request_logging_enabled:
            return await call_next(request)
        
        # Check if path should be excluded
        for exclude_path in self.config.request_logging_exclude_paths:
            if request.url.path.startswith(exclude_path):
                return await call_next(request)
        
        # Log request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request details
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": round(process_time * 1000, 2),  # milliseconds
            "user_agent": request.headers.get("user-agent", "unknown"),
            "client_ip": request.client.host,
        }
        
        self.logger.info(json.dumps(log_data))

        return response
'''


MIDDLEWARE_TRUSTED_PROXY = '''"""Trusted proxy middleware."""

from typing import List, Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.middleware_config import MiddlewareConfig


class TrustedProxyMiddleware(BaseHTTPMiddleware):
    """Trusted proxy middleware."""
    
    def __init__(self, app, config: Optional[MiddlewareConfig] = None):
        super().__init__(app)
        self.config = config or MiddlewareConfig()
    
    async def dispatch(self, request: Request, call_next):
        """Handle trusted proxy headers."""
        if not self.config.trusted_proxy_headers:
            return await call_next(request)
        
        # Process trusted proxy headers
        for header in self.config.trusted_proxy_headers:
            if header in request.headers:
                # Set the forwarded information
                if header == "X-Forwarded-For":
                    request.state.forwarded_for = request.headers[header]
                elif header == "X-Forwarded-Proto":
                    request.state.forwarded_proto = request.headers[header]
                elif header == "X-Forwarded-Host":
                    request.state.forwarded_host = request.headers[header]

        return await call_next(request)
'''


MIDDLEWARE_SETUP = '''"""Middleware setup and configuration."""

from typing import List
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from core.middleware_config import MiddlewareConfig
from .middleware_cors import create_cors_middleware
from .middleware_rate_limit import RateLimitMiddleware
from .middleware_security import SecurityHeadersMiddleware
from .middleware_gzip import create_gzip_middleware
from .middleware_logging import RequestLoggingMiddleware
from .middleware_trusted_proxy import TrustedProxyMiddleware


def setup_middleware(app: FastAPI, config: Optional[MiddlewareConfig] = None):
    """Setup all middleware for the FastAPI application."""
    middleware_config = config or MiddlewareConfig()
    middleware_list: List[BaseHTTPMiddleware] = []
    
    # Add CORS middleware
    if middleware_config.cors_origins:
        middleware_list.append(create_cors_middleware(middleware_config))
    
    # Add rate limiting middleware
    if middleware_config.rate_limit_enabled:
        middleware_list.append(
            RateLimitMiddleware(
                app, 
                requests=middleware_config.rate_limit_requests,
                window=middleware_config.rate_limit_window
            )
        )
    
    # Add security headers middleware
    if middleware_config.security_headers_enabled:
        middleware_list.append(SecurityHeadersMiddleware(app, middleware_config))
    
    # Add Gzip middleware
    if middleware_config.gzip_enabled:
        middleware_list.append(create_gzip_middleware(middleware_config))
    
    # Add request logging middleware
    if middleware_config.request_logging_enabled:
        middleware_list.append(RequestLoggingMiddleware(app, middleware_config))
    
    # Add trusted proxy middleware
    if middleware_config.trusted_proxy_headers:
        middleware_list.append(TrustedProxyMiddleware(app, middleware_config))
    
    # Add all middleware to app
    for middleware in middleware_list:
        app.add_middleware(middleware)
    
    return middleware_list


def get_middleware_config() -> MiddlewareConfig:
    """Get middleware configuration from environment."""
    return MiddlewareConfig()
'''

MIDDLEWARE_MAIN = '''"""Main application with middleware support."""

from fastapi import FastAPI
from core.middleware_config import get_middleware_config
from core.middleware_setup import setup_middleware
from routers.health import router as health_router
from routers.users import router as users_router


def create_app() -> FastAPI:
    """Create FastAPI application with middleware."""
    app = FastAPI(
        title="FastAPI Project",
        description="FastAPI project with middleware support"
    )
    
    # Setup middleware
    config = get_middleware_config()
    setup_middleware(app, config)
    
    # Include routers
    app.include_router(health_router, tags=["health"])
    app.include_router(users_router, tags=["users"])
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

MIDDLEWARE_EXAMPLES = '''"""Middleware usage examples."""

from fastapi import FastAPI
from core.middleware_config import MiddlewareConfig
from core.middleware_setup import setup_middleware


def create_custom_middleware_app() -> FastAPI:
    """Create app with custom middleware configuration."""
    
    # Custom middleware configuration
    config = MiddlewareConfig()
    config.cors_origins = ["https://example.com", "https://api.example.com"]
    config.rate_limit_enabled = True
    config.rate_limit_requests = 50
    config.security_headers_enabled = True
    config.gzip_enabled = True
    config.request_logging_enabled = True
    
    app = FastAPI(title="Custom Middleware Example")
    setup_middleware(app, config)
    
    return app


def create_minimal_middleware_app() -> FastAPI:
    """Create app with minimal middleware."""
    
    # Minimal middleware configuration
    config = MiddlewareConfig()
    config.cors_origins = ["http://localhost:3000"]
    config.security_headers_enabled = True
    
    app = FastAPI(title="Minimal Middleware Example")
    setup_middleware(app, config)
    
    return app


# Example usage:
# app = create_custom_middleware_app()
# app = create_minimal_middleware_app()
'''

REQUIREMENTS_MIDDLEWARE = """
# Middleware support
fastapi>=0.100.0
starlette>=0.27.0
"""

ENV_EXAMPLE_MIDDLEWARE = """
# Middleware Configuration
# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
CORS_ALLOW_CREDENTIALS=false
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*
CORS_EXPOSE_HEADERS=

# Rate Limiting Configuration
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Security Headers Configuration
SECURITY_HEADERS_ENABLED=true
X-Content-Type-Options=nosniff
X-Frame-Options=DENY
X-XSS-Protection=1; mode=block
Strict-Transport-Security=max-age=31536000; includeSubDomains

# Gzip Configuration
GZIP_ENABLED=true
GZIP_MINIMUM_SIZE=1000

# Request Logging Configuration
REQUEST_LOGGING_ENABLED=true
REQUEST_LOGGING_FORMAT=%(asctime)s - %(levelname)s - %(message)s
REQUEST_LOGGING_EXCLUDE_PATHS=/health,/metrics

# Trusted Proxy Configuration
TRUSTED_PROXY_HEADERS=X-Forwarded-For,X-Forwarded-Proto,X-Forwarded-Host
"""
