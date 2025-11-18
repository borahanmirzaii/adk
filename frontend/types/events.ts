/**
 * Unified Agent Event Schema - TypeScript Type Definitions
 * AG-UI Protocol Compatible
 *
 * This file contains all event types used throughout the application.
 * Events flow from backend → Event Bus → frontend via SSE/WebSocket.
 */

// ============================================================================
// Base Event Structure
// ============================================================================

export interface BaseEvent {
  event_id: string;
  session_id: string;
  timestamp: string; // ISO 8601 format
  type: EventType;
  payload: EventPayload;
}

export type EventType =
  // Session
  | "session_started"
  | "session_ended"
  // Agent Messages
  | "agent_message_start"
  | "agent_message_delta"
  | "agent_message_end"
  // Tools
  | "tool_call_started"
  | "tool_call_delta"
  | "tool_call_result"
  // Workflows
  | "workflow_started"
  | "workflow_step_started"
  | "workflow_step_completed"
  | "workflow_transition"
  | "workflow_completed"
  // Reasoning
  | "agent_thought"
  // Errors
  | "run_error"
  | "run_retry"
  | "run_interrupted"
  // RAG
  | "retrieval_started"
  | "retrieval_result"
  // n8n
  | "automation_triggered"
  | "automation_completed"
  // Infrastructure
  | "metrics_update";

export type EventPayload =
  | SessionStartedPayload
  | SessionEndedPayload
  | AgentMessageStartPayload
  | AgentMessageDeltaPayload
  | AgentMessageEndPayload
  | ToolCallStartedPayload
  | ToolCallDeltaPayload
  | ToolCallResultPayload
  | WorkflowStartedPayload
  | WorkflowStepStartedPayload
  | WorkflowStepCompletedPayload
  | WorkflowTransitionPayload
  | WorkflowCompletedPayload
  | AgentThoughtPayload
  | RunErrorPayload
  | RunRetryPayload
  | RunInterruptedPayload
  | RetrievalStartedPayload
  | RetrievalResultPayload
  | AutomationTriggeredPayload
  | AutomationCompletedPayload
  | MetricsUpdatePayload;

// ============================================================================
// 1. Session Events
// ============================================================================

export interface SessionStartedPayload {
  session_id: string;
  agent: string;
  metadata?: {
    user_id?: string;
    workflow?: string;
    [key: string]: any;
  };
}

export interface SessionEndedPayload {
  session_id: string;
  reason: "completed" | "error" | "interrupted" | "timeout";
  summary?: string;
}

// ============================================================================
// 2. Agent Message Events
// ============================================================================

export interface AgentMessageStartPayload {
  agent: string;
  message_id: string;
}

export interface AgentMessageDeltaPayload {
  message_id: string;
  delta: string;
}

export interface AgentMessageEndPayload {
  message_id: string;
  content: string;
}

// ============================================================================
// 3. Tool Execution Events
// ============================================================================

export interface ToolCallStartedPayload {
  tool_call_id: string;
  tool_name: string;
  agent: string;
  args: Record<string, any>;
}

export interface ToolCallDeltaPayload {
  tool_call_id: string;
  delta: string;
}

export interface ToolCallResultPayload {
  tool_call_id: string;
  tool_name: string;
  result: any;
  error?: string;
}

// ============================================================================
// 4. Workflow Events (LangGraph)
// ============================================================================

export interface WorkflowStartedPayload {
  workflow: string;
  run_id: string;
}

export interface WorkflowStepStartedPayload {
  run_id: string;
  step_id: string;
  description: string;
}

export interface WorkflowStepCompletedPayload {
  run_id: string;
  step_id: string;
  output: any;
}

export interface WorkflowTransitionPayload {
  run_id: string;
  from_step: string;
  to_step: string;
  reason: string;
}

export interface WorkflowCompletedPayload {
  run_id: string;
  result: {
    summary: string;
    [key: string]: any;
  };
}

// ============================================================================
// 5. Agent Thinking / Reasoning
// ============================================================================

export interface AgentThoughtPayload {
  agent: string;
  content: string;
  debug: boolean;
}

// ============================================================================
// 6. Error, Retry & Interrupt Events
// ============================================================================

export interface RunErrorPayload {
  error_type: string;
  message: string;
  agent: string;
  step?: string;
  traceback?: string;
}

export interface RunRetryPayload {
  retry_count: number;
  max_retries: number;
  reason: string;
}

export interface RunInterruptedPayload {
  reason: "user_stop" | "timeout" | "system_error";
  step?: string;
}

// ============================================================================
// 7. Knowledge Base / RAG Events
// ============================================================================

export interface RetrievalStartedPayload {
  query: string;
  agent: string;
}

export interface RetrievalResultPayload {
  documents: Array<{
    id: string;
    score: number;
    content: string;
    metadata?: Record<string, any>;
  }>;
}

// ============================================================================
// 8. n8n Automation Events
// ============================================================================

export interface AutomationTriggeredPayload {
  workflow: string;
  trigger: string;
}

export interface AutomationCompletedPayload {
  workflow: string;
  result: string;
}

// ============================================================================
// 9. System Metrics / Infrastructure Monitor
// ============================================================================

export interface MetricsUpdatePayload {
  cpu: number; // percentage
  memory_used: string;
  disk_free: string;
  containers_running: number;
  [key: string]: any;
}

// ============================================================================
// Typed Event Interfaces (for type narrowing)
// ============================================================================

export interface SessionStartedEvent extends BaseEvent {
  type: "session_started";
  payload: SessionStartedPayload;
}

export interface SessionEndedEvent extends BaseEvent {
  type: "session_ended";
  payload: SessionEndedPayload;
}

export interface AgentMessageStartEvent extends BaseEvent {
  type: "agent_message_start";
  payload: AgentMessageStartPayload;
}

export interface AgentMessageDeltaEvent extends BaseEvent {
  type: "agent_message_delta";
  payload: AgentMessageDeltaPayload;
}

export interface AgentMessageEndEvent extends BaseEvent {
  type: "agent_message_end";
  payload: AgentMessageEndPayload;
}

export interface ToolCallStartedEvent extends BaseEvent {
  type: "tool_call_started";
  payload: ToolCallStartedPayload;
}

export interface ToolCallDeltaEvent extends BaseEvent {
  type: "tool_call_delta";
  payload: ToolCallDeltaPayload;
}

export interface ToolCallResultEvent extends BaseEvent {
  type: "tool_call_result";
  payload: ToolCallResultPayload;
}

export interface WorkflowStartedEvent extends BaseEvent {
  type: "workflow_started";
  payload: WorkflowStartedPayload;
}

export interface WorkflowStepStartedEvent extends BaseEvent {
  type: "workflow_step_started";
  payload: WorkflowStepStartedPayload;
}

export interface WorkflowStepCompletedEvent extends BaseEvent {
  type: "workflow_step_completed";
  payload: WorkflowStepCompletedPayload;
}

export interface WorkflowTransitionEvent extends BaseEvent {
  type: "workflow_transition";
  payload: WorkflowTransitionPayload;
}

export interface WorkflowCompletedEvent extends BaseEvent {
  type: "workflow_completed";
  payload: WorkflowCompletedPayload;
}

export interface AgentThoughtEvent extends BaseEvent {
  type: "agent_thought";
  payload: AgentThoughtPayload;
}

export interface RunErrorEvent extends BaseEvent {
  type: "run_error";
  payload: RunErrorPayload;
}

export interface RunRetryEvent extends BaseEvent {
  type: "run_retry";
  payload: RunRetryPayload;
}

export interface RunInterruptedEvent extends BaseEvent {
  type: "run_interrupted";
  payload: RunInterruptedPayload;
}

export interface RetrievalStartedEvent extends BaseEvent {
  type: "retrieval_started";
  payload: RetrievalStartedPayload;
}

export interface RetrievalResultEvent extends BaseEvent {
  type: "retrieval_result";
  payload: RetrievalResultPayload;
}

export interface AutomationTriggeredEvent extends BaseEvent {
  type: "automation_triggered";
  payload: AutomationTriggeredPayload;
}

export interface AutomationCompletedEvent extends BaseEvent {
  type: "automation_completed";
  payload: AutomationCompletedPayload;
}

export interface MetricsUpdateEvent extends BaseEvent {
  type: "metrics_update";
  payload: MetricsUpdatePayload;
}

// ============================================================================
// Union Type for All Events (for exhaustive type checking)
// ============================================================================

export type AgentEvent =
  | SessionStartedEvent
  | SessionEndedEvent
  | AgentMessageStartEvent
  | AgentMessageDeltaEvent
  | AgentMessageEndEvent
  | ToolCallStartedEvent
  | ToolCallDeltaEvent
  | ToolCallResultEvent
  | WorkflowStartedEvent
  | WorkflowStepStartedEvent
  | WorkflowStepCompletedEvent
  | WorkflowTransitionEvent
  | WorkflowCompletedEvent
  | AgentThoughtEvent
  | RunErrorEvent
  | RunRetryEvent
  | RunInterruptedEvent
  | RetrievalStartedEvent
  | RetrievalResultEvent
  | AutomationTriggeredEvent
  | AutomationCompletedEvent
  | MetricsUpdateEvent;

// ============================================================================
// Type Guards (for runtime type checking)
// ============================================================================

export function isSessionStartedEvent(event: AgentEvent): event is SessionStartedEvent {
  return event.type === "session_started";
}

export function isToolCallStartedEvent(event: AgentEvent): event is ToolCallStartedEvent {
  return event.type === "tool_call_started";
}

export function isToolCallResultEvent(event: AgentEvent): event is ToolCallResultEvent {
  return event.type === "tool_call_result";
}

export function isWorkflowEvent(event: AgentEvent): boolean {
  return event.type.startsWith("workflow_");
}

export function isErrorEvent(event: AgentEvent): event is RunErrorEvent {
  return event.type === "run_error";
}

export function isMetricsEvent(event: AgentEvent): event is MetricsUpdateEvent {
  return event.type === "metrics_update";
}

// ============================================================================
// Helper Types
// ============================================================================

export interface EventFilter {
  types?: EventType[];
  agents?: string[];
  sessions?: string[];
}

export interface EventStats {
  totalEvents: number;
  byType: Record<EventType, number>;
  byAgent: Record<string, number>;
  errors: number;
  retries: number;
}
