"""Security headers middleware."""

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
