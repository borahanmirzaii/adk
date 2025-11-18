"""
Unified Agent Event Schema - Python Pydantic Models
AG-UI Protocol Compatible

This module contains all event types used throughout the backend.
Events are published to the Event Bus and streamed to the frontend.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ============================================================================
# Event Type Enum
# ============================================================================

class EventType(str, Enum):
    """All possible event types in the system"""

    # Session
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"

    # Agent Messages
    AGENT_MESSAGE_START = "agent_message_start"
    AGENT_MESSAGE_DELTA = "agent_message_delta"
    AGENT_MESSAGE_END = "agent_message_end"

    # Tools
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_DELTA = "tool_call_delta"
    TOOL_CALL_RESULT = "tool_call_result"

    # Workflows
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_STEP_STARTED = "workflow_step_started"
    WORKFLOW_STEP_COMPLETED = "workflow_step_completed"
    WORKFLOW_TRANSITION = "workflow_transition"
    WORKFLOW_COMPLETED = "workflow_completed"

    # Reasoning
    AGENT_THOUGHT = "agent_thought"

    # Errors
    RUN_ERROR = "run_error"
    RUN_RETRY = "run_retry"
    RUN_INTERRUPTED = "run_interrupted"

    # RAG
    RETRIEVAL_STARTED = "retrieval_started"
    RETRIEVAL_RESULT = "retrieval_result"

    # n8n
    AUTOMATION_TRIGGERED = "automation_triggered"
    AUTOMATION_COMPLETED = "automation_completed"

    # Infrastructure
    METRICS_UPDATE = "metrics_update"


# ============================================================================
# Base Event Model
# ============================================================================

class BaseEvent(BaseModel):
    """Base event structure for all events"""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: EventType
    payload: Dict[str, Any]

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


# ============================================================================
# 1. Session Event Payloads
# ============================================================================

class SessionStartedPayload(BaseModel):
    """Payload for session_started event"""

    session_id: str
    agent: str
    metadata: Optional[Dict[str, Any]] = None


class SessionEndedPayload(BaseModel):
    """Payload for session_ended event"""

    session_id: str
    reason: Literal["completed", "error", "interrupted", "timeout"]
    summary: Optional[str] = None


# ============================================================================
# 2. Agent Message Event Payloads
# ============================================================================

class AgentMessageStartPayload(BaseModel):
    """Payload for agent_message_start event"""

    agent: str
    message_id: str


class AgentMessageDeltaPayload(BaseModel):
    """Payload for agent_message_delta event"""

    message_id: str
    delta: str


class AgentMessageEndPayload(BaseModel):
    """Payload for agent_message_end event"""

    message_id: str
    content: str


# ============================================================================
# 3. Tool Execution Event Payloads
# ============================================================================

class ToolCallStartedPayload(BaseModel):
    """Payload for tool_call_started event"""

    tool_call_id: str
    tool_name: str
    agent: str
    args: Dict[str, Any]


class ToolCallDeltaPayload(BaseModel):
    """Payload for tool_call_delta event"""

    tool_call_id: str
    delta: str


class ToolCallResultPayload(BaseModel):
    """Payload for tool_call_result event"""

    tool_call_id: str
    tool_name: str
    result: Any
    error: Optional[str] = None


# ============================================================================
# 4. Workflow Event Payloads (LangGraph)
# ============================================================================

class WorkflowStartedPayload(BaseModel):
    """Payload for workflow_started event"""

    workflow: str
    run_id: str


class WorkflowStepStartedPayload(BaseModel):
    """Payload for workflow_step_started event"""

    run_id: str
    step_id: str
    description: str


class WorkflowStepCompletedPayload(BaseModel):
    """Payload for workflow_step_completed event"""

    run_id: str
    step_id: str
    output: Any


class WorkflowTransitionPayload(BaseModel):
    """Payload for workflow_transition event"""

    run_id: str
    from_step: str
    to_step: str
    reason: str


class WorkflowCompletedPayload(BaseModel):
    """Payload for workflow_completed event"""

    run_id: str
    result: Dict[str, Any]


# ============================================================================
# 5. Agent Thinking / Reasoning Payloads
# ============================================================================

class AgentThoughtPayload(BaseModel):
    """Payload for agent_thought event"""

    agent: str
    content: str
    debug: bool = True


# ============================================================================
# 6. Error, Retry & Interrupt Event Payloads
# ============================================================================

class RunErrorPayload(BaseModel):
    """Payload for run_error event"""

    error_type: str
    message: str
    agent: str
    step: Optional[str] = None
    traceback: Optional[str] = None


class RunRetryPayload(BaseModel):
    """Payload for run_retry event"""

    retry_count: int
    max_retries: int
    reason: str


class RunInterruptedPayload(BaseModel):
    """Payload for run_interrupted event"""

    reason: Literal["user_stop", "timeout", "system_error"]
    step: Optional[str] = None


# ============================================================================
# 7. Knowledge Base / RAG Event Payloads
# ============================================================================

class RetrievalDocument(BaseModel):
    """A single retrieved document"""

    id: str
    score: float
    content: str
    metadata: Optional[Dict[str, Any]] = None


class RetrievalStartedPayload(BaseModel):
    """Payload for retrieval_started event"""

    query: str
    agent: str


class RetrievalResultPayload(BaseModel):
    """Payload for retrieval_result event"""

    documents: List[RetrievalDocument]


# ============================================================================
# 8. n8n Automation Event Payloads
# ============================================================================

class AutomationTriggeredPayload(BaseModel):
    """Payload for automation_triggered event"""

    workflow: str
    trigger: str


class AutomationCompletedPayload(BaseModel):
    """Payload for automation_completed event"""

    workflow: str
    result: str


# ============================================================================
# 9. System Metrics / Infrastructure Monitor Payloads
# ============================================================================

class MetricsUpdatePayload(BaseModel):
    """Payload for metrics_update event"""

    cpu: float  # percentage
    memory_used: str
    disk_free: str
    containers_running: int
    extra: Optional[Dict[str, Any]] = None


# ============================================================================
# Typed Event Models (for type safety)
# ============================================================================

class SessionStartedEvent(BaseEvent):
    """Typed event for session_started"""

    type: Literal[EventType.SESSION_STARTED] = EventType.SESSION_STARTED
    payload: SessionStartedPayload


class SessionEndedEvent(BaseEvent):
    """Typed event for session_ended"""

    type: Literal[EventType.SESSION_ENDED] = EventType.SESSION_ENDED
    payload: SessionEndedPayload


class AgentMessageStartEvent(BaseEvent):
    """Typed event for agent_message_start"""

    type: Literal[EventType.AGENT_MESSAGE_START] = EventType.AGENT_MESSAGE_START
    payload: AgentMessageStartPayload


class AgentMessageDeltaEvent(BaseEvent):
    """Typed event for agent_message_delta"""

    type: Literal[EventType.AGENT_MESSAGE_DELTA] = EventType.AGENT_MESSAGE_DELTA
    payload: AgentMessageDeltaPayload


class AgentMessageEndEvent(BaseEvent):
    """Typed event for agent_message_end"""

    type: Literal[EventType.AGENT_MESSAGE_END] = EventType.AGENT_MESSAGE_END
    payload: AgentMessageEndPayload


class ToolCallStartedEvent(BaseEvent):
    """Typed event for tool_call_started"""

    type: Literal[EventType.TOOL_CALL_STARTED] = EventType.TOOL_CALL_STARTED
    payload: ToolCallStartedPayload


class ToolCallDeltaEvent(BaseEvent):
    """Typed event for tool_call_delta"""

    type: Literal[EventType.TOOL_CALL_DELTA] = EventType.TOOL_CALL_DELTA
    payload: ToolCallDeltaPayload


class ToolCallResultEvent(BaseEvent):
    """Typed event for tool_call_result"""

    type: Literal[EventType.TOOL_CALL_RESULT] = EventType.TOOL_CALL_RESULT
    payload: ToolCallResultPayload


class WorkflowStartedEvent(BaseEvent):
    """Typed event for workflow_started"""

    type: Literal[EventType.WORKFLOW_STARTED] = EventType.WORKFLOW_STARTED
    payload: WorkflowStartedPayload


class WorkflowStepStartedEvent(BaseEvent):
    """Typed event for workflow_step_started"""

    type: Literal[EventType.WORKFLOW_STEP_STARTED] = EventType.WORKFLOW_STEP_STARTED
    payload: WorkflowStepStartedPayload


class WorkflowStepCompletedEvent(BaseEvent):
    """Typed event for workflow_step_completed"""

    type: Literal[EventType.WORKFLOW_STEP_COMPLETED] = EventType.WORKFLOW_STEP_COMPLETED
    payload: WorkflowStepCompletedPayload


class WorkflowTransitionEvent(BaseEvent):
    """Typed event for workflow_transition"""

    type: Literal[EventType.WORKFLOW_TRANSITION] = EventType.WORKFLOW_TRANSITION
    payload: WorkflowTransitionPayload


class WorkflowCompletedEvent(BaseEvent):
    """Typed event for workflow_completed"""

    type: Literal[EventType.WORKFLOW_COMPLETED] = EventType.WORKFLOW_COMPLETED
    payload: WorkflowCompletedPayload


class AgentThoughtEvent(BaseEvent):
    """Typed event for agent_thought"""

    type: Literal[EventType.AGENT_THOUGHT] = EventType.AGENT_THOUGHT
    payload: AgentThoughtPayload


class RunErrorEvent(BaseEvent):
    """Typed event for run_error"""

    type: Literal[EventType.RUN_ERROR] = EventType.RUN_ERROR
    payload: RunErrorPayload


class RunRetryEvent(BaseEvent):
    """Typed event for run_retry"""

    type: Literal[EventType.RUN_RETRY] = EventType.RUN_RETRY
    payload: RunRetryPayload


class RunInterruptedEvent(BaseEvent):
    """Typed event for run_interrupted"""

    type: Literal[EventType.RUN_INTERRUPTED] = EventType.RUN_INTERRUPTED
    payload: RunInterruptedPayload


class RetrievalStartedEvent(BaseEvent):
    """Typed event for retrieval_started"""

    type: Literal[EventType.RETRIEVAL_STARTED] = EventType.RETRIEVAL_STARTED
    payload: RetrievalStartedPayload


class RetrievalResultEvent(BaseEvent):
    """Typed event for retrieval_result"""

    type: Literal[EventType.RETRIEVAL_RESULT] = EventType.RETRIEVAL_RESULT
    payload: RetrievalResultPayload


class AutomationTriggeredEvent(BaseEvent):
    """Typed event for automation_triggered"""

    type: Literal[EventType.AUTOMATION_TRIGGERED] = EventType.AUTOMATION_TRIGGERED
    payload: AutomationTriggeredPayload


class AutomationCompletedEvent(BaseEvent):
    """Typed event for automation_completed"""

    type: Literal[EventType.AUTOMATION_COMPLETED] = EventType.AUTOMATION_COMPLETED
    payload: AutomationCompletedPayload


class MetricsUpdateEvent(BaseEvent):
    """Typed event for metrics_update"""

    type: Literal[EventType.METRICS_UPDATE] = EventType.METRICS_UPDATE
    payload: MetricsUpdatePayload


# ============================================================================
# Union Type for All Events
# ============================================================================

AgentEvent = Union[
    SessionStartedEvent,
    SessionEndedEvent,
    AgentMessageStartEvent,
    AgentMessageDeltaEvent,
    AgentMessageEndEvent,
    ToolCallStartedEvent,
    ToolCallDeltaEvent,
    ToolCallResultEvent,
    WorkflowStartedEvent,
    WorkflowStepStartedEvent,
    WorkflowStepCompletedEvent,
    WorkflowTransitionEvent,
    WorkflowCompletedEvent,
    AgentThoughtEvent,
    RunErrorEvent,
    RunRetryEvent,
    RunInterruptedEvent,
    RetrievalStartedEvent,
    RetrievalResultEvent,
    AutomationTriggeredEvent,
    AutomationCompletedEvent,
    MetricsUpdateEvent,
]


# ============================================================================
# Helper Functions
# ============================================================================

def create_session_started_event(
    session_id: str,
    agent: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> SessionStartedEvent:
    """Helper to create a session_started event"""
    return SessionStartedEvent(
        session_id=session_id,
        payload=SessionStartedPayload(
            session_id=session_id,
            agent=agent,
            metadata=metadata or {},
        ),
    )


def create_tool_call_started_event(
    session_id: str,
    tool_call_id: str,
    tool_name: str,
    agent: str,
    args: Dict[str, Any],
) -> ToolCallStartedEvent:
    """Helper to create a tool_call_started event"""
    return ToolCallStartedEvent(
        session_id=session_id,
        payload=ToolCallStartedPayload(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            agent=agent,
            args=args,
        ),
    )


def create_tool_call_result_event(
    session_id: str,
    tool_call_id: str,
    tool_name: str,
    result: Any,
    error: Optional[str] = None,
) -> ToolCallResultEvent:
    """Helper to create a tool_call_result event"""
    return ToolCallResultEvent(
        session_id=session_id,
        payload=ToolCallResultPayload(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            result=result,
            error=error,
        ),
    )


def create_run_error_event(
    session_id: str,
    error_type: str,
    message: str,
    agent: str,
    step: Optional[str] = None,
    traceback: Optional[str] = None,
) -> RunErrorEvent:
    """Helper to create a run_error event"""
    return RunErrorEvent(
        session_id=session_id,
        payload=RunErrorPayload(
            error_type=error_type,
            message=message,
            agent=agent,
            step=step,
            traceback=traceback,
        ),
    )


def create_metrics_update_event(
    session_id: str,
    cpu: float,
    memory_used: str,
    disk_free: str,
    containers_running: int,
    extra: Optional[Dict[str, Any]] = None,
) -> MetricsUpdateEvent:
    """Helper to create a metrics_update event"""
    return MetricsUpdateEvent(
        session_id=session_id,
        payload=MetricsUpdatePayload(
            cpu=cpu,
            memory_used=memory_used,
            disk_free=disk_free,
            containers_running=containers_running,
            extra=extra,
        ),
    )
