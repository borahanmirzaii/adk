"""
Core Event Model for Event Bus

This module defines the unified Event structure used throughout the system.
All events are normalized to this format before being published to the event bus.
"""

import json
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Event(BaseModel):
    """
    Unified event structure for the Event Bus

    This is the normalized event format that flows through Redis Pub/Sub
    and is streamed to clients via SSE.

    Attributes:
        event_id: Unique identifier for this event
        session_id: Session this event belongs to
        timestamp: When the event occurred (UTC)
        type: Event type (e.g., 'tool_call_started', 'agent_message_delta')
        payload: Event-specific data as a dictionary
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: str
    payload: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

    def to_sse(self) -> str:
        """
        Convert event to Server-Sent Events (SSE) format

        Returns:
            SSE-formatted string ready to send to clients

        Example:
            event: tool_call_started
            data: {"event_id":"123","session_id":"abc",...}

        """
        data = self.model_dump(mode="json")
        return f"event: {self.type}\ndata: {json.dumps(data)}\n\n"

    def to_json(self) -> str:
        """
        Convert event to JSON string

        Returns:
            JSON-serialized event
        """
        return json.dumps(self.model_dump(mode="json"))

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        """
        Create Event from JSON string

        Args:
            json_str: JSON-serialized event

        Returns:
            Event instance
        """
        data = json.loads(json_str)
        return cls(**data)
