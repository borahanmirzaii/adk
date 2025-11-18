"""Rate limiting middleware"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis
from app.config import settings
import time

redis_client = redis.from_url(settings.REDIS_URL)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""

    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request"""
        # Get client identifier
        client_id = request.client.host if request.client else "unknown"

        # Rate limit key
        key = f"rate_limit:{client_id}"

        # Get current count
        current = redis_client.get(key)
        if current and int(current) >= settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
            )

        # Increment counter
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # 1 minute window
        pipe.execute()

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = settings.RATE_LIMIT_PER_MINUTE - (int(current) if current else 0) - 1
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)

        return response

