# Event Bus Integration Plan - Complete Implementation Guide

## Overview

This document provides a **step-by-step plan** to integrate the Event Bus into the existing ADK Dev Environment Manager codebase.

Based on the exploration, we have:
- ✅ **Event Bus Infrastructure**: Redis Pub/Sub, EventDispatcher, SSE endpoint
- ✅ **Frontend Components**: AgentTimeline, UI components, useAgentEvents hook
- 🔄 **Agents**: 4 agents (InfrastructureMonitor, CodeReviewer, DeploymentOrchestrator, KnowledgeBase)
- 🔄 **Workflows**: 2 LangGraph workflows (Review, Deployment)
- 🔄 **Tools**: 4 infrastructure monitoring tools
- 🔄 **Sessions**: Session management via Supabase

**Goal**: Make all agent actions visible in real-time via the Event Bus.

---

## Phase 1: Integrate BaseADKAgent (Foundation)

**Priority**: 🔴 CRITICAL - This affects all agents

### **Step 1.1: Update BaseADKAgent Constructor**

**File**: `backend/app/agents/base_agent.py`

**Current**:
```python
class BaseADKAgent:
    def __init__(self, agent_name: str, system_prompt: str, tools: List[FunctionTool]):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools
        # ... Supabase, Langfuse, ADK setup
```

**Update to**:
```python
from app.event_bus import get_event_dispatcher
from uuid import uuid4

class BaseADKAgent:
    def __init__(self, agent_name: str, system_prompt: str, tools: List[FunctionTool]):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools

        # ✅ Add Event Dispatcher
        self.dispatcher = get_event_dispatcher()

        # ... existing Supabase, Langfuse, ADK setup
```

### **Step 1.2: Update BaseADKAgent.execute() Method**

**Current Flow**:
```python
async def execute(self, user_message: str, session_id: Optional[str] = None) -> str:
    # 1. Get/create session
    # 2. Run agent with retries
    # 3. Save to session history
    # 4. Log metrics
    return response_text
```

**Update to**:
```python
async def execute(self, user_message: str, session_id: Optional[str] = None) -> str:
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid4())

    # Generate message ID for tracking
    message_id = f"msg_{uuid4().hex[:8]}"

    try:
        # ✅ 1. Publish session_started event
        await self.dispatcher.session_started(
            session_id=session_id,
            agent=self.agent_name,
            metadata={"user_message_preview": user_message[:100]}
        )

        # ✅ 2. Publish agent_message_start event
        await self.dispatcher.agent_message_start(
            session_id=session_id,
            message_id=message_id,
            agent=self.agent_name
        )

        # Get/create session (existing code)
        session_data = await session_service.get_session(session_id)
        if not session_data:
            await session_service.create_session(
                session_id=session_id,
                user_id="default-user",
                app_name=self.agent_name,
            )

        # ✅ 3. Run agent with event publishing
        response_text = await self._execute_with_events(
            user_message=user_message,
            session_id=session_id,
            message_id=message_id
        )

        # ✅ 4. Publish agent_message_end event
        await self.dispatcher.agent_message_end(
            session_id=session_id,
            message_id=message_id,
            content=response_text
        )

        # Save to session history (existing code)
        await session_service.add_event(
            session_id=session_id,
            event={
                "user_message": user_message,
                "agent_response": response_text,
                "agent_name": self.agent_name,
            }
        )

        return response_text

    except Exception as e:
        # ✅ 5. Publish run_error event
        await self.dispatcher.run_error(
            session_id=session_id,
            error_type=type(e).__name__,
            message=str(e),
            agent=self.agent_name,
            traceback=traceback.format_exc()
        )
        raise
```

### **Step 1.3: Add _execute_with_events() Helper Method**

**Add new method to BaseADKAgent**:

```python
async def _execute_with_events(
    self, user_message: str, session_id: str, message_id: str
) -> str:
    """
    Execute agent with retry logic and event publishing
    """
    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            # Run the agent (existing ADK execution)
            result = await self.llm_agent.run(user_message)
            return result.text

        except Exception as e:
            retry_count += 1

            if retry_count < max_retries:
                # ✅ Publish retry event
                await self.dispatcher.run_retry(
                    session_id=session_id,
                    retry_count=retry_count,
                    max_retries=max_retries,
                    reason=str(e)
                )
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            else:
                raise
```

### **Step 1.4: Add Streaming Support (Optional - Advanced)**

If Google ADK supports streaming:

```python
async def execute_streaming(
    self, user_message: str, session_id: str
) -> AsyncIterator[str]:
    """
    Stream agent responses with delta events
    """
    message_id = f"msg_{uuid4().hex[:8]}"

    await self.dispatcher.agent_message_start(
        session_id=session_id,
        message_id=message_id,
        agent=self.agent_name
    )

    full_response = ""
    async for chunk in self.llm_agent.stream(user_message):
        # ✅ Publish delta event for each chunk
        await self.dispatcher.agent_message_delta(
            session_id=session_id,
            message_id=message_id,
            delta=chunk.text
        )
        full_response += chunk.text
        yield chunk.text

    await self.dispatcher.agent_message_end(
        session_id=session_id,
        message_id=message_id,
        content=full_response
    )
```

### **Verification**

```bash
# 1. Start Redis
docker-compose up redis -d

# 2. Start backend
just dev-backend

# 3. In terminal 1: Listen to events
curl http://localhost:8000/api/events/test-session

# 4. In terminal 2: Trigger agent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Check Docker containers", "session_id": "test-session", "agent_name": "infrastructure_monitor"}'

# 5. Verify events appear in terminal 1:
# - session_started
# - agent_message_start
# - agent_message_end
```

**Expected Output** (Terminal 1):
```
event: session_started
data: {"event_id":"...","session_id":"test-session","type":"session_started",...}

event: agent_message_start
data: {"event_id":"...","session_id":"test-session","type":"agent_message_start",...}

event: agent_message_end
data: {"event_id":"...","session_id":"test-session","type":"agent_message_end",...}
```

---

## Phase 2: Integrate Tool Events

**Priority**: 🟠 HIGH - Provides visibility into tool execution

### **Step 2.1: Wrap Tool Functions with Event Publishing**

**Current Pattern** (in `backend/app/agents/infrastructure_monitor/tools.py`):

```python
def check_docker_containers() -> Dict[str, Any]:
    client = docker.from_env()
    containers = client.containers.list(all=True)
    return {
        "total": len(containers),
        "running": len([c for c in containers if c.status == "running"]),
        "containers": [...],
    }
```

**Problem**: Tools don't have access to `session_id` or `dispatcher`.

**Solution 1: Tool Decorator Pattern**

Create a tool wrapper that injects event publishing:

**File**: `backend/app/agents/tool_wrapper.py` (NEW)

```python
from functools import wraps
from typing import Any, Callable, Dict
from uuid import uuid4
from app.event_bus import get_event_dispatcher
import asyncio

class ToolContext:
    """Thread-local storage for tool execution context"""
    session_id: str = None
    agent_name: str = None

tool_context = ToolContext()

def with_events(tool_name: str):
    """
    Decorator that wraps a tool function with event publishing

    Usage:
        @with_events("check_docker_containers")
        def check_docker_containers() -> Dict[str, Any]:
            # ... tool logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            dispatcher = get_event_dispatcher()
            tool_call_id = f"tc_{uuid4().hex[:8]}"
            session_id = tool_context.session_id or "unknown"
            agent_name = tool_context.agent_name or "unknown"

            # ✅ Publish tool_call_started
            await dispatcher.tool_call_started(
                session_id=session_id,
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                args={"args": args, "kwargs": kwargs},
                agent=agent_name
            )

            try:
                # Execute the tool
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # ✅ Publish tool_call_result (success)
                await dispatcher.tool_call_result(
                    session_id=session_id,
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    result=result
                )

                return result

            except Exception as e:
                # ✅ Publish tool_call_result (error)
                await dispatcher.tool_call_result(
                    session_id=session_id,
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    result=None,
                    error=str(e)
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # For synchronous tools, run in event loop
            return asyncio.run(async_wrapper(*args, **kwargs))

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
```

### **Step 2.2: Update Tool Definitions**

**File**: `backend/app/agents/infrastructure_monitor/tools.py`

**Before**:
```python
def check_docker_containers() -> Dict[str, Any]:
    client = docker.from_env()
    # ... tool logic
```

**After**:
```python
from app.agents.tool_wrapper import with_events

@with_events("check_docker_containers")
def check_docker_containers() -> Dict[str, Any]:
    """Check status of all Docker containers"""
    client = docker.from_env()
    # ... existing tool logic (no changes)
```

**Apply to all tools**:
```python
@with_events("check_disk_space")
def check_disk_space() -> Dict[str, Any]:
    # ... existing logic

@with_events("check_memory_usage")
def check_memory_usage() -> Dict[str, Any]:
    # ... existing logic

@with_events("check_database_connection")
def check_database_connection() -> Dict[str, Any]:
    # ... existing logic
```

### **Step 2.3: Update BaseADKAgent to Set Tool Context**

**File**: `backend/app/agents/base_agent.py`

```python
from app.agents.tool_wrapper import tool_context

async def execute(self, user_message: str, session_id: Optional[str] = None) -> str:
    # ... existing code ...

    # ✅ Set tool context before agent execution
    tool_context.session_id = session_id
    tool_context.agent_name = self.agent_name

    # Run agent (tools will now publish events)
    result = await self.llm_agent.run(user_message)

    # ✅ Clear tool context
    tool_context.session_id = None
    tool_context.agent_name = None

    return result.text
```

### **Solution 2: Custom Tool Base Class (Alternative)**

If you prefer a class-based approach:

**File**: `backend/app/agents/base_tool.py` (NEW)

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import uuid4
from app.event_bus import get_event_dispatcher

class BaseTool(ABC):
    """Base class for all tools with built-in event publishing"""

    def __init__(self, name: str):
        self.name = name
        self.dispatcher = get_event_dispatcher()

    async def execute(
        self,
        session_id: str,
        agent_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute tool with event publishing"""
        tool_call_id = f"tc_{uuid4().hex[:8]}"

        # ✅ Publish tool_call_started
        await self.dispatcher.tool_call_started(
            session_id=session_id,
            tool_call_id=tool_call_id,
            tool_name=self.name,
            args=kwargs,
            agent=agent_name
        )

        try:
            # Execute tool logic
            result = await self._execute(**kwargs)

            # ✅ Publish tool_call_result
            await self.dispatcher.tool_call_result(
                session_id=session_id,
                tool_call_id=tool_call_id,
                tool_name=self.name,
                result=result
            )

            return result

        except Exception as e:
            # ✅ Publish error
            await self.dispatcher.tool_call_result(
                session_id=session_id,
                tool_call_id=tool_call_id,
                tool_name=self.name,
                result=None,
                error=str(e)
            )
            raise

    @abstractmethod
    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Implement tool logic here"""
        pass
```

**Usage**:
```python
class CheckDockerContainersTool(BaseTool):
    def __init__(self):
        super().__init__("check_docker_containers")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        client = docker.from_env()
        # ... tool logic
```

### **Verification**

```bash
# Trigger agent that uses tools
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Check Docker containers", "session_id": "test-session"}'

# Events should appear:
# - session_started
# - agent_message_start
# - tool_call_started (check_docker_containers)
# - tool_call_result
# - agent_message_end
```

---

## Phase 3: Integrate LangGraph Workflows

**Priority**: 🟡 MEDIUM - Provides workflow visibility

### **Step 3.1: Add Workflow Event Publishing to Review Workflow**

**File**: `backend/app/workflows/review_workflow.py`

**Current**:
```python
from langgraph.graph import StateGraph

workflow = StateGraph(ReviewState)
workflow.add_node("static_analysis", static_analysis_node)
workflow.add_node("security_scan", security_scan_node)
workflow.add_node("best_practices", best_practices_node)
workflow.add_node("generate_report", generate_report_node)
# ... edges ...
review_workflow = workflow.compile()
```

**Update State to Include Context**:
```python
class ReviewState(TypedDict):
    # Existing fields
    code: str
    static_analysis_result: Annotated[List[Dict], operator.add]
    security_scan_result: Annotated[List[Dict], operator.add]
    best_practices_result: Annotated[List[Dict], operator.add]
    final_report: str
    errors: List[str]

    # ✅ Add event context
    session_id: str
    run_id: str
```

**Update Node Functions**:
```python
from app.event_bus import get_event_dispatcher

async def static_analysis_node(state: ReviewState) -> ReviewState:
    """Perform static analysis on code"""
    dispatcher = get_event_dispatcher()

    # ✅ Publish workflow_step_started
    await dispatcher.workflow_step_started(
        session_id=state["session_id"],
        run_id=state["run_id"],
        step_id="static_analysis",
        description="Analyzing code for syntax and style issues"
    )

    try:
        # Existing analysis logic
        issues = [
            {"type": "style", "line": 42, "message": "Line too long"},
            # ... more issues
        ]

        # ✅ Publish workflow_step_completed
        await dispatcher.workflow_step_completed(
            session_id=state["session_id"],
            run_id=state["run_id"],
            step_id="static_analysis",
            output={"issues_found": len(issues)}
        )

        return {
            **state,
            "static_analysis_result": issues,
        }

    except Exception as e:
        # ✅ Publish error
        await dispatcher.run_error(
            session_id=state["session_id"],
            error_type=type(e).__name__,
            message=str(e),
            agent="code_reviewer",
            step="static_analysis"
        )
        return {
            **state,
            "errors": state["errors"] + [str(e)],
        }

# Repeat for other nodes:
async def security_scan_node(state: ReviewState) -> ReviewState:
    dispatcher = get_event_dispatcher()

    # ✅ Publish transition
    await dispatcher.workflow_transition(
        session_id=state["session_id"],
        run_id=state["run_id"],
        from_step="static_analysis",
        to_step="security_scan",
        reason="Static analysis completed successfully"
    )

    await dispatcher.workflow_step_started(
        session_id=state["session_id"],
        run_id=state["run_id"],
        step_id="security_scan",
        description="Scanning for security vulnerabilities"
    )

    # ... existing logic ...

    await dispatcher.workflow_step_completed(
        session_id=state["session_id"],
        run_id=state["run_id"],
        step_id="security_scan",
        output={"vulnerabilities_found": len(vulnerabilities)}
    )

    return state

# best_practices_node: similar pattern
# generate_report_node: similar pattern
```

### **Step 3.2: Update CodeReviewerAgent to Pass Context**

**File**: `backend/app/agents/code_reviewer/agent.py`

**Current**:
```python
async def review_code(self, code: str, session_id: Optional[str] = None) -> str:
    result = await review_workflow.ainvoke({
        "code": code,
        "static_analysis_result": [],
        # ...
    })
    return result["final_report"]
```

**Update to**:
```python
from uuid import uuid4
from app.event_bus import get_event_dispatcher

async def review_code(self, code: str, session_id: Optional[str] = None) -> str:
    if not session_id:
        session_id = str(uuid4())

    run_id = f"run_{uuid4().hex[:8]}"
    dispatcher = get_event_dispatcher()

    # ✅ Publish workflow_started
    await dispatcher.workflow_started(
        session_id=session_id,
        workflow="code_review",
        run_id=run_id
    )

    try:
        # Run workflow with context
        result = await review_workflow.ainvoke({
            "code": code,
            "static_analysis_result": [],
            "security_scan_result": [],
            "best_practices_result": [],
            "final_report": "",
            "errors": [],
            # ✅ Pass context
            "session_id": session_id,
            "run_id": run_id,
        })

        # ✅ Publish workflow_completed
        await dispatcher.workflow_completed(
            session_id=session_id,
            run_id=run_id,
            result={
                "summary": result["final_report"][:200],
                "total_issues": (
                    len(result["static_analysis_result"]) +
                    len(result["security_scan_result"]) +
                    len(result["best_practices_result"])
                ),
            }
        )

        return result["final_report"]

    except Exception as e:
        # ✅ Publish error
        await dispatcher.run_error(
            session_id=session_id,
            error_type=type(e).__name__,
            message=str(e),
            agent="code_reviewer",
            step="workflow_execution"
        )
        raise
```

### **Step 3.3: Apply Same Pattern to Deployment Workflow**

**File**: `backend/app/workflows/deployment_workflow.py`

Apply the same pattern:
1. Add `session_id` and `run_id` to `DeploymentState`
2. Update each node to publish workflow events
3. Update `DeploymentOrchestratorAgent` to pass context

### **Verification**

```bash
# Trigger code review
curl -X POST http://localhost:8000/api/agents/code_reviewer/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "def foo():\n  pass", "session_id": "test-session"}'

# Events should appear:
# - workflow_started
# - workflow_step_started (static_analysis)
# - workflow_step_completed (static_analysis)
# - workflow_transition (static_analysis → security_scan)
# - workflow_step_started (security_scan)
# - workflow_step_completed (security_scan)
# - workflow_transition (security_scan → best_practices)
# - workflow_step_started (best_practices)
# - workflow_step_completed (best_practices)
# - workflow_transition (best_practices → generate_report)
# - workflow_step_started (generate_report)
# - workflow_step_completed (generate_report)
# - workflow_completed
```

---

## Phase 4: Add Metrics Publishing to InfrastructureMonitorAgent

**Priority**: 🟢 LOW - Nice-to-have for real-time monitoring

### **Step 4.1: Update monitor_services() Method**

**File**: `backend/app/agents/infrastructure_monitor/agent.py`

**Current**:
```python
async def monitor_services(self) -> Dict[str, Any]:
    # Check Docker
    docker_status = check_docker_containers()
    # Check disk
    disk_status = check_disk_space()
    # Check memory
    memory_status = check_memory_usage()
    # Store in Supabase
    # Send n8n alert if critical
```

**Update to**:
```python
from app.event_bus import get_event_dispatcher

async def monitor_services(self, session_id: Optional[str] = None) -> Dict[str, Any]:
    if not session_id:
        session_id = f"monitor_{uuid4().hex[:8]}"

    dispatcher = get_event_dispatcher()

    # Check services (existing logic)
    docker_status = check_docker_containers()
    disk_status = check_disk_space()
    memory_status = check_memory_usage()

    # ✅ Publish metrics_update event
    await dispatcher.metrics_update(
        session_id=session_id,
        cpu=memory_status["percent_used"],  # Approximation
        memory_used=f"{memory_status['used_gb']:.1f}GB",
        disk_free=f"{disk_status['free_gb']:.1f}GB",
        containers_running=docker_status["running"],
        extra={
            "total_containers": docker_status["total"],
            "disk_percent_used": disk_status["percent_used"],
        }
    )

    # Existing Supabase storage and n8n logic
    # ...

    return {
        "docker": docker_status,
        "disk": disk_status,
        "memory": memory_status,
    }
```

### **Step 4.2: Create Periodic Monitoring Task (Optional)**

**File**: `backend/app/tasks/monitoring.py` (NEW)

```python
import asyncio
from app.agents.infrastructure_monitor.agent import InfrastructureMonitorAgent

async def periodic_monitoring(interval_seconds: int = 60):
    """
    Run infrastructure monitoring periodically and publish metrics
    """
    agent = InfrastructureMonitorAgent()
    session_id = f"periodic_monitor_{uuid4().hex[:8]}"

    while True:
        try:
            await agent.monitor_services(session_id=session_id)
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")

        await asyncio.sleep(interval_seconds)

# Start in background when app starts
# In main.py:
# @app.on_event("startup")
# async def startup():
#     asyncio.create_task(periodic_monitoring(interval_seconds=60))
```

---

## Phase 5: Frontend Integration

**Priority**: 🔴 CRITICAL - Make events visible to users

### **Step 5.1: Create Agent Session Page**

**File**: `frontend/app/agents/[sessionId]/page.tsx` (NEW)

```typescript
import { AgentRunView } from "@/components/agents/AgentRunView";

export default function AgentSessionPage({
  params,
}: {
  params: { sessionId: string };
}) {
  return (
    <div className="h-screen">
      <AgentRunView sessionId={params.sessionId} />
    </div>
  );
}
```

### **Step 5.2: Update Chat API Route to Support SSE**

**File**: `frontend/app/api/chat/route.ts`

```typescript
export async function POST(request: Request) {
  const { message, session_id, agent_name } = await request.json();

  // Call backend
  const response = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id, agent_name }),
  });

  const data = await response.json();

  return Response.json({
    ...data,
    // Return session_id so frontend can connect to SSE
    session_id: data.session_id,
  });
}
```

### **Step 5.3: Create Chat Interface with Timeline**

**File**: `frontend/app/chat/page.tsx`

```typescript
"use client";

import { useState } from "react";
import { AgentTimeline } from "@/components/agents/AgentTimeline";
import { LiveConsole } from "@/components/agents/LiveConsole";

export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  const handleSend = async () => {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        agent_name: "infrastructure_monitor",
      }),
    });

    const data = await response.json();
    setSessionId(data.session_id);
    setMessage("");
  };

  return (
    <div className="h-screen grid grid-cols-2 gap-4 p-4">
      {/* Left: Chat Input */}
      <div>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="w-full h-32 border rounded p-2"
          placeholder="Enter your message..."
        />
        <button
          onClick={handleSend}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
        >
          Send
        </button>
        {sessionId && (
          <p className="mt-2 text-sm text-gray-500">
            Session: <code>{sessionId}</code>
          </p>
        )}
      </div>

      {/* Right: Event Timeline */}
      <div className="border rounded p-4 overflow-hidden">
        {sessionId ? (
          <>
            <AgentTimeline sessionId={sessionId} />
            <LiveConsole sessionId={sessionId} />
          </>
        ) : (
          <p className="text-gray-500">Send a message to start session</p>
        )}
      </div>
    </div>
  );
}
```

### **Step 5.4: Add Navigation**

**File**: `frontend/components/layout/Navigation.tsx`

```typescript
import Link from "next/link";

export function Navigation() {
  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="flex gap-4">
        <Link href="/chat">Chat</Link>
        <Link href="/agents">Agents</Link>
        <Link href="/monitoring">Monitoring</Link>
      </div>
    </nav>
  );
}
```

---

## Phase 6: Testing & Validation

### **End-to-End Test Scenarios**

#### **Test 1: Basic Agent Execution**

```bash
# Terminal 1: Start SSE listener
curl http://localhost:8000/api/events/test-basic

# Terminal 2: Execute agent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test-basic", "agent_name": "infrastructure_monitor"}'

# Verify in Terminal 1:
# ✅ session_started
# ✅ agent_message_start
# ✅ agent_message_end
```

#### **Test 2: Tool Execution**

```bash
# Terminal 1: SSE listener
curl http://localhost:8000/api/events/test-tools

# Terminal 2: Execute agent with tool usage
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Check Docker containers", "session_id": "test-tools"}'

# Verify in Terminal 1:
# ✅ session_started
# ✅ agent_message_start
# ✅ tool_call_started (check_docker_containers)
# ✅ tool_call_result
# ✅ agent_message_end
```

#### **Test 3: Workflow Execution**

```bash
# Terminal 1: SSE listener
curl http://localhost:8000/api/events/test-workflow

# Terminal 2: Execute code review
curl -X POST http://localhost:8000/api/agents/code_reviewer/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "def foo():\n  pass", "session_id": "test-workflow"}'

# Verify in Terminal 1:
# ✅ workflow_started
# ✅ workflow_step_started (static_analysis)
# ✅ workflow_step_completed
# ✅ workflow_transition
# ✅ workflow_step_started (security_scan)
# ✅ ... (all steps)
# ✅ workflow_completed
```

#### **Test 4: Error Handling**

```bash
# Terminal 1: SSE listener
curl http://localhost:8000/api/events/test-error

# Terminal 2: Trigger error (invalid request)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "", "session_id": "test-error"}'

# Verify in Terminal 1:
# ✅ session_started
# ✅ agent_message_start
# ✅ run_error (validation error)
```

#### **Test 5: Frontend Integration**

1. Start frontend: `npm run dev`
2. Navigate to `http://localhost:3000/chat`
3. Send a message
4. Verify AgentTimeline shows real-time events
5. Verify LiveConsole shows logs

---

## Implementation Checklist

### **Phase 1: BaseADKAgent** ⏳
- [ ] Add EventDispatcher to constructor
- [ ] Publish session_started in execute()
- [ ] Publish agent_message_start in execute()
- [ ] Publish agent_message_end in execute()
- [ ] Add _execute_with_events() helper
- [ ] Publish run_retry events
- [ ] Publish run_error events
- [ ] Test with InfrastructureMonitorAgent
- [ ] Verify events appear via SSE

### **Phase 2: Tool Events** ⏳
- [ ] Create tool_wrapper.py with @with_events decorator
- [ ] Add ToolContext for session tracking
- [ ] Update check_docker_containers with decorator
- [ ] Update check_disk_space with decorator
- [ ] Update check_memory_usage with decorator
- [ ] Update check_database_connection with decorator
- [ ] Update BaseADKAgent to set tool_context
- [ ] Test tool events via SSE
- [ ] Verify tool_call_started and tool_call_result events

### **Phase 3: Workflow Events** ⏳
- [ ] Add session_id and run_id to ReviewState
- [ ] Update static_analysis_node with events
- [ ] Update security_scan_node with events
- [ ] Update best_practices_node with events
- [ ] Update generate_report_node with events
- [ ] Add workflow_transition events between nodes
- [ ] Update CodeReviewerAgent.review_code()
- [ ] Publish workflow_started and workflow_completed
- [ ] Apply same pattern to DeploymentWorkflow
- [ ] Test workflow events via SSE

### **Phase 4: Metrics Publishing** ⏳
- [ ] Update InfrastructureMonitorAgent.monitor_services()
- [ ] Publish metrics_update events
- [ ] Create periodic_monitoring task (optional)
- [ ] Test metrics events via SSE

### **Phase 5: Frontend** ⏳
- [ ] Create app/agents/[sessionId]/page.tsx
- [ ] Create app/chat/page.tsx
- [ ] Add Navigation component
- [ ] Update API routes to return session_id
- [ ] Test frontend → backend → SSE flow
- [ ] Verify AgentTimeline updates in real-time
- [ ] Verify LiveConsole shows logs

### **Phase 6: Testing** ⏳
- [ ] Test 1: Basic agent execution
- [ ] Test 2: Tool execution
- [ ] Test 3: Workflow execution
- [ ] Test 4: Error handling
- [ ] Test 5: Frontend integration
- [ ] Load testing with multiple sessions
- [ ] Test reconnection after disconnect

---

## Estimated Timeline

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1: BaseADKAgent | 2-3 hours | None |
| Phase 2: Tool Events | 2-3 hours | Phase 1 |
| Phase 3: Workflow Events | 3-4 hours | Phase 1 |
| Phase 4: Metrics | 1-2 hours | Phase 1, Phase 2 |
| Phase 5: Frontend | 3-4 hours | Phase 1-4 |
| Phase 6: Testing | 2-3 hours | All phases |
| **Total** | **13-19 hours** | |

---

## Success Criteria

✅ **Complete when**:
1. All agents publish events to Event Bus
2. All tools publish tool_call events
3. All workflows publish step/transition events
4. Frontend displays real-time events
5. All 24 event types are in use
6. No events are lost during execution
7. SSE reconnection works after disconnect
8. Multiple concurrent sessions don't interfere

---

## Troubleshooting Guide

### **Events not appearing in SSE**
- Check Redis is running: `docker ps | grep redis`
- Check backend logs for publishing errors
- Verify session_id matches between publisher and subscriber
- Test with curl first before trying frontend

### **Tool events missing**
- Verify @with_events decorator is applied
- Check tool_context is set in BaseADKAgent.execute()
- Ensure tools are wrapped correctly

### **Workflow events missing**
- Verify session_id and run_id are in state
- Check each node has event publishing
- Ensure dispatcher is imported in workflow file

### **Frontend not updating**
- Check browser console for EventSource errors
- Verify CORS headers in backend
- Test SSE endpoint with curl
- Check useAgentEvents hook connection status

---

## Next Steps After Integration

1. **Add Agent Thoughts**: Publish agent_thought events for reasoning visibility
2. **Add RAG Events**: If implementing vector search, publish retrieval events
3. **Add n8n Events**: Publish automation_triggered/completed when calling n8n
4. **Add Metrics Dashboard**: Create dedicated monitoring page
5. **Add Event Replay**: Store events in Supabase for historical playback
6. **Add Event Filtering**: Allow users to filter events by type
7. **Add Event Search**: Search through event history

---

This plan provides a complete, step-by-step guide to integrating the Event Bus into your existing codebase. Start with Phase 1 (BaseADKAgent) as it's the foundation for all other phases!
