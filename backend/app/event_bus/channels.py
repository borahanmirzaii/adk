"""
Channel Naming Utilities for Redis Pub/Sub

This module provides helper functions for generating consistent channel names
for the Redis Pub/Sub event bus.
"""


def session_channel(session_id: str) -> str:
    """
    Generate channel name for a specific session

    Args:
        session_id: The session identifier

    Returns:
        Redis channel name (e.g., "session:abc123")

    Example:
        >>> session_channel("abc123")
        "session:abc123"
    """
    return f"session:{session_id}"


def broadcast_channel() -> str:
    """
    Generate the broadcast channel name

    This channel receives all events across all sessions.
    Useful for system monitoring and logging.

    Returns:
        Redis channel name for broadcasts

    Example:
        >>> broadcast_channel()
        "broadcast:all"
    """
    return "broadcast:all"


def agent_channel(agent_name: str) -> str:
    """
    Generate channel name for a specific agent

    Args:
        agent_name: The agent identifier

    Returns:
        Redis channel name (e.g., "agent:infrastructure_monitor")

    Example:
        >>> agent_channel("infrastructure_monitor")
        "agent:infrastructure_monitor"
    """
    return f"agent:{agent_name}"
