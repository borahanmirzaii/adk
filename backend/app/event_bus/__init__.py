"""
Event Bus Package - AG-UI Protocol Implementation

This package implements a real-time event streaming system using Redis Pub/Sub and SSE.
Events follow the AG-UI Protocol specification for compatibility with industry-standard tools.
"""

from .bus import EventBus, get_event_bus
from .dispatcher import EventDispatcher, get_event_dispatcher
from .schema import Event

__all__ = [
    "Event",
    "EventBus",
    "get_event_bus",
    "EventDispatcher",
    "get_event_dispatcher",
]
