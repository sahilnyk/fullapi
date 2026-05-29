"""Gzip compression middleware."""

from typing import Optional
from starlette.middleware.gzip import GZipMiddleware
from core.middleware_config import MiddlewareConfig


def create_gzip_middleware(config: Optional[MiddlewareConfig] = None):
    """Create Gzip middleware with configuration."""
    middleware_config = config or MiddlewareConfig()

    return GZipMiddleware(
        minimum_size=middleware_config.gzip_minimum_size,
    )
