"""Rate limiting middleware."""

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
