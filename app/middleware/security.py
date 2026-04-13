from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import time


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting - 10 requests per minute per IP"""

    def __init__(self, app):
        super().__init__(app)
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Keep only last 60 seconds requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if current_time - t < 60
        ]

        if len(self.requests[client_ip]) >= 10:
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests. Try again later."}
            )

        self.requests[client_ip].append(current_time)

        return await call_next(request)