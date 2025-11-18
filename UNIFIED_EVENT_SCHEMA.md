# Unified Agent Event Schema (AG-UI Compatible)

## 🎯 Overview

This is the **complete message contract** for the entire ADK Dev Environment Manager system. All events flow through the Unified Event Bus and follow this schema.

**Compatible With**:
- FastAPI (SSE/WebSocket)
- Google ADK
- LangGraph
- Supabase
- n8n
- CopilotKit
- Next.js
- AG-UI Protocol

---

## 📋 Root Event Structure

Every event has this root structure:

```json
{
  "event_id": "uuid",
  "session_id": "string",
  "timestamp": "2024-01-01T12:00:00Z",
  "type": "string",
  "payload": {}
}
```

---

## 📚 Event Categories

### **1. Session Events**

#### `session_started`
```json
{
  "type": "session_started",
  "payload": {
    "session_id": "abc",
    "agent": "infrastructure_monitor",
    "metadata": {
      "user_id": "123",
      "workflow": "infra_monitoring"
    }
  }
}
```

#### `session_ended`
```json
{
  "type": "session_ended",
  "payload": {
    "session_id": "abc",
    "reason": "completed",
    "summary": "Infrastructure monitor finished health scan."
  }
}
```

---

### **2. Agent Message Events**

#### `agent_message_start`
```json
{
  "type": "agent_message_start",
  "payload": {
    "agent": "code_reviewer",
    "message_id": "m1"
  }
}
```

#### `agent_message_delta`
```json
{
  "type": "agent_message_delta",
  "payload": {
    "message_id": "m1",
    "delta": "Analyzing code..."
  }
}
```

#### `agent_message_end`
```json
{
  "type": "agent_message_end",
  "payload": {
    "message_id": "m1",
    "content": "Code review completed."
  }
}
```

---

### **3. Tool Execution Events**

#### `tool_call_started`
```json
{
  "type": "tool_call_started",
  "payload": {
    "tool_call_id": "tc_001",
    "tool_name": "docker_list_containers",
    "agent": "infrastructure_monitor",
    "args": { "status": "running" }
  }
}
```

#### `tool_call_delta`
```json
{
  "type": "tool_call_delta",
  "payload": {
    "tool_call_id": "tc_001",
    "delta": "checking Docker..."
  }
}
```

#### `tool_call_result`
```json
{
  "type": "tool_call_result",
  "payload": {
    "tool_call_id": "tc_001",
    "tool_name": "docker_list_containers",
    "result": [
      { "name": "supabase-db", "status": "running" }
    ]
  }
}
```

---

### **4. Workflow Events (LangGraph)**

#### `workflow_started`
```json
{
  "type": "workflow_started",
  "payload": {
    "workflow": "review_workflow",
    "run_id": "run_001"
  }
}
```

#### `workflow_step_started`
```json
{
  "type": "workflow_step_started",
  "payload": {
    "run_id": "run_001",
    "step_id": "step_static_analysis",
    "description": "Running static analysis..."
  }
}
```

#### `workflow_step_completed`
```json
{
  "type": "workflow_step_completed",
  "payload": {
    "run_id": "run_001",
    "step_id": "step_static_analysis",
    "output": { "score": 82 }
  }
}
```

#### `workflow_transition`
```json
{
  "type": "workflow_transition",
  "payload": {
    "run_id": "run_001",
    "from_step": "static_analysis",
    "to_step": "security_scan",
    "reason": "static_analysis_complete"
  }
}
```

#### `workflow_completed`
```json
{
  "type": "workflow_completed",
  "payload": {
    "run_id": "run_001",
    "result": {
      "summary": "Code review finished successfully."
    }
  }
}
```

---

### **5. Agent Thinking / Reasoning**

#### `agent_thought`
```json
{
  "type": "agent_thought",
  "payload": {
    "agent": "code_reviewer",
    "content": "Evaluating code smell patterns...",
    "debug": true
  }
}
```

---

### **6. Error, Retry & Interrupt Events**

#### `run_error`
```json
{
  "type": "run_error",
  "payload": {
    "error_type": "ToolError",
    "message": "Docker daemon unreachable.",
    "agent": "infrastructure_monitor",
    "step": "docker_check"
  }
}
```

#### `run_retry`
```json
{
  "type": "run_retry",
  "payload": {
    "retry_count": 1,
    "max_retries": 3,
    "reason": "temporary network issue"
  }
}
```

#### `run_interrupted`
```json
{
  "type": "run_interrupted",
  "payload": {
    "reason": "user_stop",
    "step": "security_scan"
  }
}
```

---

### **7. Knowledge Base / RAG Events**

#### `retrieval_started`
```json
{
  "type": "retrieval_started",
  "payload": {
    "query": "how to fix postgres connection error",
    "agent": "knowledge_base"
  }
}
```

#### `retrieval_result`
```json
{
  "type": "retrieval_result",
  "payload": {
    "documents": [
      {
        "id": "doc1",
        "score": 0.92,
        "content": "Increase max_connections in Postgres..."
      }
    ]
  }
}
```

---

### **8. n8n Automation Events**

#### `automation_triggered`
```json
{
  "type": "automation_triggered",
  "payload": {
    "workflow": "SendSlackAlert",
    "trigger": "disk_space_low"
  }
}
```

#### `automation_completed`
```json
{
  "type": "automation_completed",
  "payload": {
    "workflow": "SendSlackAlert",
    "result": "Notification sent."
  }
}
```

---

### **9. System Metrics / Infrastructure Monitor**

#### `metrics_update`
```json
{
  "type": "metrics_update",
  "payload": {
    "cpu": 42,
    "memory_used": "3.2GB",
    "disk_free": "120GB",
    "containers_running": 5
  }
}
```

---

## 📊 Event Categories Summary

| Category | Events |
|----------|--------|
| **Session** | `session_started`, `session_ended` |
| **Agent Messages** | `agent_message_start`, `agent_message_delta`, `agent_message_end` |
| **Tools** | `tool_call_started`, `tool_call_delta`, `tool_call_result` |
| **Workflows** | `workflow_started`, `workflow_step_started`, `workflow_step_completed`, `workflow_transition`, `workflow_completed` |
| **Reasoning** | `agent_thought` |
| **Errors** | `run_error`, `run_retry`, `run_interrupted` |
| **RAG** | `retrieval_started`, `retrieval_result` |
| **n8n** | `automation_triggered`, `automation_completed` |
| **Infrastructure** | `metrics_update` |

---

## 🎯 Benefits of This Schema

### **1. AG-UI Compatible**
- Works with standard AG-UI Protocol
- Compatible with Replit Agents, Cursor patterns
- Community-proven event structure

### **2. Complete Coverage**
- Covers all agent operations
- Handles errors and retries
- Supports multi-agent workflows
- Includes infrastructure metrics

### **3. Real-Time Streaming**
- Designed for SSE/WebSocket
- Delta events for streaming
- Efficient payload sizes

### **4. Observable**
- Every operation traced
- Debug mode support
- Metric collection built-in

### **5. Type-Safe**
- Clear payload structures
- Easy to validate
- TypeScript-ready
- Python Pydantic-ready

---

## 🚀 Implementation Files

This schema will be implemented in:

**Backend**:
- `backend/app/models/events.py` - Pydantic models
- `backend/app/services/event_bus.py` - Event publishing
- `backend/app/api/routes/events.py` - SSE endpoint

**Frontend**:
- `frontend/types/events.ts` - TypeScript types
- `frontend/hooks/useAgentEvents.ts` - Event consumption
- `frontend/components/agents/*` - Event visualization

---

## 📋 Next Steps

1. **Create Python Pydantic Models** - Type-safe backend events
2. **Create TypeScript Types** - Type-safe frontend events
3. **Implement Event Bus** - SSE/WebSocket streaming
4. **Create Event Hook** - React hook for consuming events
5. **Build UI Components** - Visualize events in real-time

---

See related documents:
- `PYTHON_EVENT_MODELS.md` - Pydantic implementations
- `TYPESCRIPT_EVENT_TYPES.md` - TypeScript type definitions
- `EVENT_BUS_IMPLEMENTATION.md` - FastAPI SSE/WebSocket
- `FRONTEND_EVENT_HOOK.md` - React useAgentEvents hook
