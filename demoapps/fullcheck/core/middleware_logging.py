"""Request logging middleware."""

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
