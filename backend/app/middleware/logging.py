"""Request logging middleware"""

from fastapi import FastAPI, Request
import logging
import time
from typing import Callable

logger = logging.getLogger(__name__)


def setup_logging(app: FastAPI) -> None:
    """Setup request logging middleware"""

    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):
        """Log all requests"""
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            },
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {response.status_code} ({duration:.3f}s)",
            extra={
                "status_code": response.status_code,
                "duration": duration,
            },
        )

        return response

