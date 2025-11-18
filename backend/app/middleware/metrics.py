"""Prometheus metrics middleware"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import REGISTRY

logger = logging.getLogger(__name__)

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions'
)

agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_name', 'status']
)

agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration in seconds',
    ['agent_name'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics"""
        start_time = time.time()
        
        # Get endpoint path (remove query params)
        endpoint = request.url.path
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            logger.error(f"Request failed: {e}")
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
        
        return response


def get_metrics():
    """Get Prometheus metrics in text format"""
    return generate_latest(REGISTRY)


def record_agent_execution(agent_name: str, duration: float, status: str = "success"):
    """Record agent execution metrics"""
    agent_executions_total.labels(
        agent_name=agent_name,
        status=status
    ).inc()
    
    agent_execution_duration_seconds.labels(
        agent_name=agent_name
    ).observe(duration)


def update_active_sessions(count: int):
    """Update active sessions gauge"""
    active_sessions.set(count)

