"""
Event Dispatcher - High-Level API for Publishing Events

This module provides the EventDispatcher class with convenient methods
for publishing different types of events. It handles event normalization
and delegates to the EventBus for actual publishing.
"""

import logging
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, Optional

from .bus import get_event_bus
from .schema import Event

logger = logging.getLogger(__name__)


class EventDispatcher:
    """
    High-level API for publishing events to the Event Bus

    The EventDispatcher provides type-specific methods for each event type,
    handling the conversion from domain events to the unified Event format.

    Example:
        >>> dispatcher = get_event_dispatcher()
        >>> await dispatcher.tool_call_started(
        ...     session_id="abc123",
        ...     tool_call_id="tc_001",
        ...     tool_name="docker_list_containers",
        ...     args={"status": "running"},
        ...     agent="infrastructure_monitor"
        ... )
    """

    def __init__(self):
        """Initialize the EventDispatcher"""
        self.bus = get_event_bus()

    # ========================================================================
    # Session Events
    # ========================================================================

    async def session_started(
        self,
        session_id: str,
        agent: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish a session_started event"""
        event = Event(
            session_id=session_id,
            type="session_started",
            payload={
                "session_id": session_id,
                "agent": agent,
                "metadata": metadata or {},
            },
        )
        await self.bus.publish(event)

    async def session_ended(
        self,
        session_id: str,
        reason: str,
        summary: Optional[str] = None,
    ) -> None:
        """Publish a session_ended event"""
        event = Event(
            session_id=session_id,
            type="session_ended",
            payload={
                "session_id": session_id,
                "reason": reason,
                "summary": summary,
            },
        )
        await self.bus.publish(event)

    # ========================================================================
    # Agent Message Events
    # ========================================================================

    async def agent_message_start(
        self,
        session_id: str,
        message_id: str,
        agent: str,
    ) -> None:
        """Publish an agent_message_start event"""
        event = Event(
            session_id=session_id,
            type="agent_message_start",
            payload={
                "agent": agent,
                "message_id": message_id,
            },
        )
        await self.bus.publish(event)

    async def agent_message_delta(
        self,
        session_id: str,
        message_id: str,
        delta: str,
    ) -> None:
        """Publish an agent_message_delta event"""
        event = Event(
            session_id=session_id,
            type="agent_message_delta",
            payload={
                "message_id": message_id,
                "delta": delta,
            },
        )
        await self.bus.publish(event)

    async def agent_message_end(
        self,
        session_id: str,
        message_id: str,
        content: str,
    ) -> None:
        """Publish an agent_message_end event"""
        event = Event(
            session_id=session_id,
            type="agent_message_end",
            payload={
                "message_id": message_id,
                "content": content,
            },
        )
        await self.bus.publish(event)

    # ========================================================================
    # Tool Execution Events
    # ========================================================================

    async def tool_call_started(
        self,
        session_id: str,
        tool_call_id: str,
        tool_name: str,
        args: Dict[str, Any],
        agent: str,
    ) -> None:
        """Publish a tool_call_started event"""
        event = Event(
            session_id=session_id,
            type="tool_call_started",
            payload={
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "agent": agent,
                "args": args,
            },
        )
        await self.bus.publish(event)

    async def tool_call_delta(
        self,
        session_id: str,
        tool_call_id: str,
        delta: str,
    ) -> None:
        """Publish a tool_call_delta event"""
        event = Event(
            session_id=session_id,
            type="tool_call_delta",
            payload={
                "tool_call_id": tool_call_id,
                "delta": delta,
            },
        )
        await self.bus.publish(event)

    async def tool_call_result(
        self,
        session_id: str,
        tool_call_id: str,
        tool_name: str,
        result: Any,
        error: Optional[str] = None,
    ) -> None:
        """Publish a tool_call_result event"""
        event = Event(
            session_id=session_id,
            type="tool_call_result",
            payload={
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "result": result,
                "error": error,
            },
        )
        await self.bus.publish(event)

    # ========================================================================
    # Workflow Events
    # ========================================================================

    async def workflow_started(
        self,
        session_id: str,
        workflow: str,
        run_id: str,
    ) -> None:
        """Publish a workflow_started event"""
        event = Event(
            session_id=session_id,
            type="workflow_started",
            payload={
                "workflow": workflow,
                "run_id": run_id,
            },
        )
        await self.bus.publish(event)

    async def workflow_step_started(
        self,
        session_id: str,
        run_id: str,
        step_id: str,
        description: str,
    ) -> None:
        """Publish a workflow_step_started event"""
        event = Event(
            session_id=session_id,
            type="workflow_step_started",
            payload={
                "run_id": run_id,
                "step_id": step_id,
                "description": description,
            },
        )
        await self.bus.publish(event)

    async def workflow_step_completed(
        self,
        session_id: str,
        run_id: str,
        step_id: str,
        output: Any,
    ) -> None:
        """Publish a workflow_step_completed event"""
        event = Event(
            session_id=session_id,
            type="workflow_step_completed",
            payload={
                "run_id": run_id,
                "step_id": step_id,
                "output": output,
            },
        )
        await self.bus.publish(event)

    async def workflow_transition(
        self,
        session_id: str,
        run_id: str,
        from_step: str,
        to_step: str,
        reason: str,
    ) -> None:
        """Publish a workflow_transition event"""
        event = Event(
            session_id=session_id,
            type="workflow_transition",
            payload={
                "run_id": run_id,
                "from_step": from_step,
                "to_step": to_step,
                "reason": reason,
            },
        )
        await self.bus.publish(event)

    async def workflow_completed(
        self,
        session_id: str,
        run_id: str,
        result: Dict[str, Any],
    ) -> None:
        """Publish a workflow_completed event"""
        event = Event(
            session_id=session_id,
            type="workflow_completed",
            payload={
                "run_id": run_id,
                "result": result,
            },
        )
        await self.bus.publish(event)

    # ========================================================================
    # Agent Thinking / Reasoning
    # ========================================================================

    async def agent_thought(
        self,
        session_id: str,
        agent: str,
        content: str,
        debug: bool = True,
    ) -> None:
        """Publish an agent_thought event"""
        event = Event(
            session_id=session_id,
            type="agent_thought",
            payload={
                "agent": agent,
                "content": content,
                "debug": debug,
            },
        )
        await self.bus.publish(event)

    # ========================================================================
    # Error, Retry & Interrupt Events
    # ========================================================================

    async def run_error(
        self,
        session_id: str,
        error_type: str,
        message: str,
        agent: str,
        step: Optional[str] = None,
        traceback: Optional[str] = None,
    ) -> None:
        """Publish a run_error event"""
        event = Event(
            session_id=session_id,
            type="run_error",
            payload={
                "error_type": error_type,
                "message": message,
                "agent": agent,
                "step": step,
                "traceback": traceback,
            },
        )
        await self.bus.publish(event)

    async def run_retry(
        self,
        session_id: str,
        retry_count: int,
        max_retries: int,
        reason: str,
    ) -> None:
        """Publish a run_retry event"""
        event = Event(
            session_id=session_id,
            type="run_retry",
            payload={
                "retry_count": retry_count,
                "max_retries": max_retries,
                "reason": reason,
            },
        )
        await self.bus.publish(event)

    async def run_interrupted(
        self,
        session_id: str,
        reason: str,
        step: Optional[str] = None,
    ) -> None:
        """Publish a run_interrupted event"""
        event = Event(
            session_id=session_id,
            type="run_interrupted",
            payload={
                "reason": reason,
                "step": step,
            },
        )
        await self.bus.publish(event)

    # ========================================================================
    # Knowledge Base / RAG Events
    # ========================================================================

    async def retrieval_started(
        self,
        session_id: str,
        query: str,
        agent: str,
    ) -> None:
        """Publish a retrieval_started event"""
        event = Event(
            session_id=session_id,
            type="retrieval_started",
            payload={
                "query": query,
                "agent": agent,
            },
        )
        await self.bus.publish(event)

    async def retrieval_result(
        self,
        session_id: str,
        documents: list,
    ) -> None:
        """Publish a retrieval_result event"""
        event = Event(
            session_id=session_id,
            type="retrieval_result",
            payload={
                "documents": documents,
            },
        )
        await self.bus.publish(event)

    # ========================================================================
    # n8n Automation Events
    # ========================================================================

    async def automation_triggered(
        self,
        session_id: str,
        workflow: str,
        trigger: str,
    ) -> None:
        """Publish an automation_triggered event"""
        event = Event(
            session_id=session_id,
            type="automation_triggered",
            payload={
                "workflow": workflow,
                "trigger": trigger,
            },
        )
        await self.bus.publish(event)

    async def automation_completed(
        self,
        session_id: str,
        workflow: str,
        result: str,
    ) -> None:
        """Publish an automation_completed event"""
        event = Event(
            session_id=session_id,
            type="automation_completed",
            payload={
                "workflow": workflow,
                "result": result,
            },
        )
        await self.bus.publish(event)

    # ========================================================================
    # System Metrics / Infrastructure Monitor
    # ========================================================================

    async def metrics_update(
        self,
        session_id: str,
        cpu: float,
        memory_used: str,
        disk_free: str,
        containers_running: int,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish a metrics_update event"""
        event = Event(
            session_id=session_id,
            type="metrics_update",
            payload={
                "cpu": cpu,
                "memory_used": memory_used,
                "disk_free": disk_free,
                "containers_running": containers_running,
                "extra": extra or {},
            },
        )
        await self.bus.publish(event)


@lru_cache
def get_event_dispatcher() -> EventDispatcher:
    """
    Get or create the singleton EventDispatcher instance

    Returns:
        EventDispatcher instance

    Example:
        >>> dispatcher = get_event_dispatcher()
        >>> await dispatcher.tool_call_started(...)
    """
    return EventDispatcher()
