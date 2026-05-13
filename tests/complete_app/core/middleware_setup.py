"""Middleware setup and configuration."""

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
