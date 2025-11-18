"""
Event Bus Implementation using Redis Pub/Sub

This module provides the core EventBus class that handles publishing events
to Redis and subscribing to event streams for SSE delivery.
"""

import asyncio
import json
import logging
from functools import lru_cache
from typing import AsyncIterator, Optional

import redis.asyncio as redis

from .channels import session_channel, broadcast_channel
from .schema import Event

logger = logging.getLogger(__name__)


class EventBus:
    """
    Redis-backed event bus for real-time event streaming

    The EventBus uses Redis Pub/Sub to distribute events to subscribers.
    Each session has its own channel (session:session_id) and there's a
    broadcast channel for system-wide events.

    Attributes:
        redis_client: Async Redis client instance
    """

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize the Event Bus

        Args:
            redis_client: Async Redis client instance
        """
        self.redis_client = redis_client

    async def publish(
        self, event: Event, broadcast: bool = False
    ) -> None:
        """
        Publish an event to the appropriate Redis channel(s)

        Args:
            event: The event to publish
            broadcast: If True, also publish to broadcast channel

        Example:
            >>> await bus.publish(event)
        """
        try:
            # Publish to session-specific channel
            channel = session_channel(event.session_id)
            await self.redis_client.publish(channel, event.to_json())
            logger.debug(
                f"Published event {event.type} to {channel} (event_id={event.event_id})"
            )

            # Optionally publish to broadcast channel
            if broadcast:
                await self.redis_client.publish(
                    broadcast_channel(), event.to_json()
                )
                logger.debug(
                    f"Broadcast event {event.type} (event_id={event.event_id})"
                )

        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {e}")
            raise

    async def stream_session_events(
        self, session_id: str, stop_event: asyncio.Event
    ) -> AsyncIterator[Event]:
        """
        Subscribe to a session channel and yield events as they arrive

        This is used by the SSE endpoint to stream events to clients.

        Args:
            session_id: The session to subscribe to
            stop_event: Asyncio event to signal when to stop streaming

        Yields:
            Event objects as they are published

        Example:
            >>> stop = asyncio.Event()
            >>> async for event in bus.stream_session_events("abc123", stop):
            ...     print(event.type)
        """
        channel = session_channel(session_id)
        logger.info(f"Starting event stream for session {session_id}")

        # Create a new Redis connection for this subscription
        # (Redis Pub/Sub requires a dedicated connection)
        pubsub_client = self.redis_client.pubsub()

        try:
            # Subscribe to the session channel
            await pubsub_client.subscribe(channel)
            logger.debug(f"Subscribed to channel {channel}")

            # Send initial connection event
            initial_event = Event(
                session_id=session_id,
                type="session_stream_started",
                payload={"message": "SSE connection established"},
            )
            yield initial_event

            # Listen for messages
            while not stop_event.is_set():
                try:
                    # Check for new messages with timeout
                    message = await asyncio.wait_for(
                        pubsub_client.get_message(
                            ignore_subscribe_messages=True, timeout=0.1
                        ),
                        timeout=1.0,
                    )

                    if message and message["type"] == "message":
                        try:
                            event = Event.from_json(message["data"])
                            logger.debug(
                                f"Received event {event.type} on {channel}"
                            )
                            yield event
                        except Exception as e:
                            logger.error(f"Failed to parse event: {e}")

                except asyncio.TimeoutError:
                    # No message received, continue waiting
                    continue

                # Allow other tasks to run
                await asyncio.sleep(0)

        except Exception as e:
            logger.error(f"Error in event stream for {session_id}: {e}")
            raise

        finally:
            # Clean up subscription
            await pubsub_client.unsubscribe(channel)
            await pubsub_client.close()
            logger.info(f"Stopped event stream for session {session_id}")


@lru_cache
def get_event_bus() -> EventBus:
    """
    Get or create the singleton EventBus instance

    This function is cached, so it will return the same instance
    across the application lifecycle.

    Returns:
        EventBus instance

    Example:
        >>> bus = get_event_bus()
        >>> await bus.publish(event)
    """
    from app.dependencies import get_redis_client

    redis_client = get_redis_client()
    return EventBus(redis_client)
