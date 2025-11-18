"""
Application Dependencies

This module provides singleton instances of shared resources like Redis clients.
Dependencies are cached using lru_cache to ensure single instances across the application.
"""

import logging
from functools import lru_cache

import redis.asyncio as redis

from .config import settings

logger = logging.getLogger(__name__)


@lru_cache
def get_redis_client() -> redis.Redis:
    """
    Get or create the singleton Redis client instance

    Returns:
        Async Redis client configured from settings

    Example:
        >>> redis_client = get_redis_client()
        >>> await redis_client.ping()
    """
    client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        db=settings.REDIS_DB,
    )
    logger.info(f"Redis client initialized: {settings.REDIS_URL}")
    return client


async def close_redis_client():
    """
    Close the Redis client connection

    Call this during application shutdown to gracefully close connections.

    Example:
        >>> await close_redis_client()
    """
    client = get_redis_client()
    await client.close()
    logger.info("Redis client closed")
