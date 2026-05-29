"""Trusted proxy middleware."""

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
