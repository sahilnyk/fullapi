"""CORS middleware configuration."""

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
