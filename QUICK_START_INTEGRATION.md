# Quick Start: Event Bus Integration

**TL;DR**: 3 simple steps to get events flowing in your existing codebase.

---

## 🚀 Quick Start (30 minutes)

### **Step 1: Update BaseADKAgent (10 min)**

**File**: `backend/app/agents/base_agent.py`

Add these 3 changes:

```python
# 1. Import dispatcher
from app.event_bus import get_event_dispatcher
from uuid import uuid4

class BaseADKAgent:
    def __init__(self, agent_name: str, system_prompt: str, tools: List[FunctionTool]):
        # ... existing code ...

        # 2. Add dispatcher
        self.dispatcher = get_event_dispatcher()

    async def execute(self, user_message: str, session_id: Optional[str] = None) -> str:
        if not session_id:
            session_id = str(uuid4())

        message_id = f"msg_{uuid4().hex[:8]}"

        # 3. Publish events
        await self.dispatcher.session_started(
            session_id=session_id,
            agent=self.agent_name,
            metadata={}
        )

        await self.dispatcher.agent_message_start(
            session_id=session_id,
            message_id=message_id,
            agent=self.agent_name
        )

        # ... existing agent execution ...
        result = await self.llm_agent.run(user_message)

        await self.dispatcher.agent_message_end(
            session_id=session_id,
            message_id=message_id,
            content=result.text
        )

        return result.text
```

### **Step 2: Test It (5 min)**

```bash
# Terminal 1: Start Redis
docker-compose up redis -d

# Terminal 2: Start backend
just dev-backend

# Terminal 3: Listen to events
curl http://localhost:8000/api/events/test-session

# Terminal 4: Trigger agent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test-session"}'
```

**You should see**:
```
event: session_started
data: {...}

event: agent_message_start
data: {...}

event: agent_message_end
data: {...}
```

✅ **If you see these events, it works!**

### **Step 3: Add Frontend Page (15 min)**

**File**: `frontend/app/test-events/page.tsx` (NEW)

```typescript
"use client";

import { useState } from "react";
import { AgentTimeline } from "@/components/agents/AgentTimeline";

export default function TestEventsPage() {
  const [sessionId] = useState("test-session-" + Date.now());
  const [message, setMessage] = useState("");

  const sendMessage = async () => {
    await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        agent_name: "infrastructure_monitor",
      }),
    });
    setMessage("");
  };

  return (
    <div className="p-8 grid grid-cols-2 gap-8 h-screen">
      <div>
        <h1 className="text-2xl font-bold mb-4">Send Message</h1>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          className="w-full border rounded p-2 mb-2"
          placeholder="Type a message..."
        />
        <button
          onClick={sendMessage}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Send
        </button>
        <p className="mt-4 text-sm text-gray-500">
          Session: <code>{sessionId}</code>
        </p>
      </div>

      <div>
        <h1 className="text-2xl font-bold mb-4">Live Events</h1>
        <div className="border rounded h-[calc(100%-3rem)] overflow-auto">
          <AgentTimeline sessionId={sessionId} />
        </div>
      </div>
    </div>
  );
}
```

Visit: `http://localhost:3000/test-events`

Type a message → Press Enter → Watch events appear in real-time! 🎉

---

## ✅ That's It!

You now have:
- ✅ Real-time event streaming from agents
- ✅ Visual timeline of all agent actions
- ✅ Foundation for adding more events

---

## Next: Add More Events

### **Tool Events** (15 min)

**File**: `backend/app/agents/tool_wrapper.py` (NEW)

Copy this file from `EVENT_BUS_INTEGRATION_PLAN.md` Phase 2.

Then update your tools:

```python
from app.agents.tool_wrapper import with_events

@with_events("check_docker_containers")
def check_docker_containers() -> Dict[str, Any]:
    # ... existing code ...
```

Done! Tool events now appear automatically.

### **Workflow Events** (30 min)

See `EVENT_BUS_INTEGRATION_PLAN.md` Phase 3 for complete guide.

---

## 📚 Full Documentation

- **Complete Integration Plan**: `EVENT_BUS_INTEGRATION_PLAN.md`
- **Implementation Details**: `EVENT_BUS_COMPLETE_IMPLEMENTATION.md`
- **Event Schema**: `UNIFIED_EVENT_SCHEMA.md`

---

## 🐛 Troubleshooting

**No events appearing?**
1. Check Redis: `docker ps | grep redis`
2. Check backend logs
3. Verify session_id matches in curl and agent

**Frontend not updating?**
1. Check browser console for errors
2. Test SSE with curl first
3. Verify CORS headers

**Tool events missing?**
1. Ensure decorator is applied
2. Check tool_context is set in BaseADKAgent

---

## 💡 Pro Tips

1. **Use curl for debugging**: Always test SSE with curl before trying frontend
2. **Check session_id**: Most issues are session_id mismatches
3. **Start simple**: Get basic events working first, then add tools/workflows
4. **Read logs**: Backend logs show all event publishing

---

Happy event streaming! 🚀
