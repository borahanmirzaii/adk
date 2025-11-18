# Event Bus Integration - Complete Checklist

Quick reference for all files that need updates.

---

## 📁 Files to Update

### ✅ **Already Complete** (No changes needed)

```
✅ backend/app/event_bus/           # Event Bus infrastructure
✅ backend/app/models/events.py     # Event models
✅ backend/app/api/routes/events.py # SSE endpoint
✅ backend/app/config.py            # Redis config
✅ backend/app/dependencies.py      # Redis client
✅ backend/app/main.py              # Events router registered

✅ frontend/types/events.ts         # TypeScript types
✅ frontend/hooks/useAgentEvents.ts # SSE hook
✅ frontend/components/agents/      # All UI components
```

---

## 🔄 **Phase 1: BaseADKAgent** (1 file)

### `backend/app/agents/base_agent.py`

**Line ~10**: Add import
```python
from app.event_bus import get_event_dispatcher
from uuid import uuid4
```

**Line ~20**: Add to `__init__`
```python
self.dispatcher = get_event_dispatcher()
```

**Line ~50**: Update `execute()` method
```python
async def execute(self, user_message: str, session_id: Optional[str] = None) -> str:
    if not session_id:
        session_id = str(uuid4())
    
    message_id = f"msg_{uuid4().hex[:8]}"
    
    # Publish session_started
    await self.dispatcher.session_started(
        session_id=session_id,
        agent=self.agent_name,
        metadata={}
    )
    
    # Publish agent_message_start
    await self.dispatcher.agent_message_start(
        session_id=session_id,
        message_id=message_id,
        agent=self.agent_name
    )
    
    # ... existing execution ...
    
    # Publish agent_message_end
    await self.dispatcher.agent_message_end(
        session_id=session_id,
        message_id=message_id,
        content=response_text
    )
    
    return response_text
```

**✅ Test**: Run backend, trigger agent, verify events via curl

---

## 🔄 **Phase 2: Tool Events** (2 files)

### `backend/app/agents/tool_wrapper.py` ⭐ NEW FILE

Create this file with the decorator pattern from `EVENT_BUS_INTEGRATION_PLAN.md` Phase 2.

### `backend/app/agents/infrastructure_monitor/tools.py`

**Line ~1**: Add import
```python
from app.agents.tool_wrapper import with_events
```

**Line ~10**: Add decorator to each tool
```python
@with_events("check_docker_containers")
def check_docker_containers() -> Dict[str, Any]:
    # ... existing code unchanged ...

@with_events("check_disk_space")
def check_disk_space() -> Dict[str, Any]:
    # ... existing code unchanged ...

@with_events("check_memory_usage")
def check_memory_usage() -> Dict[str, Any]:
    # ... existing code unchanged ...

@with_events("check_database_connection")
def check_database_connection() -> Dict[str, Any]:
    # ... existing code unchanged ...
```

**✅ Test**: Trigger agent with tools, verify tool_call events

---

## 🔄 **Phase 3: Workflow Events** (4 files)

### `backend/app/workflows/review_workflow.py`

**Line ~15**: Update ReviewState
```python
class ReviewState(TypedDict):
    # ... existing fields ...
    session_id: str  # ⭐ NEW
    run_id: str      # ⭐ NEW
```

**Line ~30+**: Update each node function
```python
from app.event_bus import get_event_dispatcher

async def static_analysis_node(state: ReviewState) -> ReviewState:
    dispatcher = get_event_dispatcher()
    
    # Publish step_started
    await dispatcher.workflow_step_started(
        session_id=state["session_id"],
        run_id=state["run_id"],
        step_id="static_analysis",
        description="Analyzing code for syntax and style issues"
    )
    
    # ... existing analysis logic ...
    
    # Publish step_completed
    await dispatcher.workflow_step_completed(
        session_id=state["session_id"],
        run_id=state["run_id"],
        step_id="static_analysis",
        output={"issues_found": len(issues)}
    )
    
    return {**state, "static_analysis_result": issues}

# Repeat for security_scan_node, best_practices_node, generate_report_node
```

### `backend/app/agents/code_reviewer/agent.py`

**Line ~20**: Update review_code method
```python
from app.event_bus import get_event_dispatcher
from uuid import uuid4

async def review_code(self, code: str, session_id: Optional[str] = None) -> str:
    if not session_id:
        session_id = str(uuid4())
    
    run_id = f"run_{uuid4().hex[:8]}"
    dispatcher = get_event_dispatcher()
    
    # Publish workflow_started
    await dispatcher.workflow_started(
        session_id=session_id,
        workflow="code_review",
        run_id=run_id
    )
    
    # Run workflow with context
    result = await review_workflow.ainvoke({
        "code": code,
        # ... existing fields ...
        "session_id": session_id,  # ⭐ NEW
        "run_id": run_id,          # ⭐ NEW
    })
    
    # Publish workflow_completed
    await dispatcher.workflow_completed(
        session_id=session_id,
        run_id=run_id,
        result={"summary": result["final_report"][:200]}
    )
    
    return result["final_report"]
```

### `backend/app/workflows/deployment_workflow.py`

Same pattern as review_workflow.py

### `backend/app/agents/deployment_orchestrator/agent.py`

Same pattern as code_reviewer/agent.py

**✅ Test**: Trigger code review, verify workflow events

---

## 🔄 **Phase 4: Metrics** (1 file)

### `backend/app/agents/infrastructure_monitor/agent.py`

**Line ~50**: Update monitor_services method
```python
from app.event_bus import get_event_dispatcher

async def monitor_services(self, session_id: Optional[str] = None) -> Dict[str, Any]:
    if not session_id:
        session_id = f"monitor_{uuid4().hex[:8]}"
    
    dispatcher = get_event_dispatcher()
    
    # ... existing monitoring logic ...
    
    # Publish metrics_update
    await dispatcher.metrics_update(
        session_id=session_id,
        cpu=memory_status["percent_used"],
        memory_used=f"{memory_status['used_gb']:.1f}GB",
        disk_free=f"{disk_status['free_gb']:.1f}GB",
        containers_running=docker_status["running"],
        extra={
            "total_containers": docker_status["total"],
            "disk_percent_used": disk_status["percent_used"],
        }
    )
    
    return {
        "docker": docker_status,
        "disk": disk_status,
        "memory": memory_status,
    }
```

**✅ Test**: Trigger monitoring, verify metrics_update event

---

## 🔄 **Phase 5: Frontend** (4 files)

### `frontend/app/agents/[sessionId]/page.tsx` ⭐ NEW FILE

```typescript
import { AgentRunView } from "@/components/agents/AgentRunView";

export default function AgentSessionPage({
  params,
}: {
  params: { sessionId: string };
}) {
  return <AgentRunView sessionId={params.sessionId} />;
}
```

### `frontend/app/chat/page.tsx` ⭐ NEW FILE

Full implementation in `EVENT_BUS_INTEGRATION_PLAN.md` Phase 5

### `frontend/app/test-events/page.tsx` ⭐ NEW FILE

Copy from `QUICK_START_INTEGRATION.md`

### `frontend/components/layout/Navigation.tsx` ⭐ NEW FILE

```typescript
import Link from "next/link";

export function Navigation() {
  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="flex gap-4">
        <Link href="/chat">Chat</Link>
        <Link href="/test-events">Test Events</Link>
        <Link href="/monitoring">Monitoring</Link>
      </div>
    </nav>
  );
}
```

**✅ Test**: Visit pages, send messages, verify real-time updates

---

## 📊 Summary

| Phase | Files to Update | Files to Create | Total |
|-------|----------------|-----------------|-------|
| Phase 1 | 1 | 0 | 1 |
| Phase 2 | 1 | 1 | 2 |
| Phase 3 | 4 | 0 | 4 |
| Phase 4 | 1 | 0 | 1 |
| Phase 5 | 0 | 4 | 4 |
| **Total** | **7** | **5** | **12** |

---

## ⏱️ Time Estimates

- Phase 1: 2-3 hours ⚡
- Phase 2: 2-3 hours 
- Phase 3: 3-4 hours
- Phase 4: 1-2 hours ⚡
- Phase 5: 3-4 hours
- Testing: 2-3 hours

**Total: 13-19 hours**

---

## 🎯 Completion Criteria

✅ **Phase 1 Complete When**:
- [ ] Events appear in curl output
- [ ] session_started event shows
- [ ] agent_message_start event shows
- [ ] agent_message_end event shows

✅ **Phase 2 Complete When**:
- [ ] tool_call_started events appear
- [ ] tool_call_result events appear
- [ ] Tool args visible in events
- [ ] Tool results visible in events

✅ **Phase 3 Complete When**:
- [ ] workflow_started event appears
- [ ] workflow_step_started for each node
- [ ] workflow_step_completed for each node
- [ ] workflow_transition events appear
- [ ] workflow_completed event appears

✅ **Phase 4 Complete When**:
- [ ] metrics_update events appear
- [ ] CPU/memory/disk/containers in payload

✅ **Phase 5 Complete When**:
- [ ] Frontend pages load
- [ ] AgentTimeline shows events
- [ ] Events update in real-time
- [ ] No errors in browser console

✅ **All Complete When**:
- [ ] All 6 phases done
- [ ] All tests passing
- [ ] No errors in logs
- [ ] Frontend works smoothly
- [ ] Multiple sessions work
- [ ] Reconnection works

---

## 🐛 Common Issues

### Events not appearing?
```bash
# Check Redis
docker ps | grep redis

# Check backend logs
just dev-backend

# Test SSE
curl http://localhost:8000/api/events/test-session
```

### Tool events missing?
- [ ] Decorator applied?
- [ ] tool_context set in BaseADKAgent?
- [ ] Import statement added?

### Workflow events missing?
- [ ] session_id in state?
- [ ] run_id in state?
- [ ] Dispatcher imported?
- [ ] Events published in each node?

### Frontend not updating?
- [ ] Browser console errors?
- [ ] CORS headers correct?
- [ ] SSE endpoint working (test with curl)?
- [ ] session_id matches?

---

## 📚 Reference Documents

- **Quick Start**: `QUICK_START_INTEGRATION.md`
- **Full Plan**: `EVENT_BUS_INTEGRATION_PLAN.md`
- **This Checklist**: `INTEGRATION_CHECKLIST.md`
- **Summary**: `INTEGRATION_SUMMARY.md`

---

Start with **Phase 1** and work your way through! 🚀
