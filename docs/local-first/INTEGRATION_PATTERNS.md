# Integration Patterns: ADK + Supabase + n8n

Detailed integration patterns for connecting ADK agents with Supabase and n8n.

## Table of Contents
1. [ADK Session Persistence with Supabase](#adk-session-persistence-with-supabase)
2. [Real-time Agent Updates](#real-time-agent-updates)
3. [n8n Workflow Triggers](#n8n-workflow-triggers)
4. [Automated Agent Actions](#automated-agent-actions)
5. [Data Synchronization](#data-synchronization)
6. [Error Handling & Retries](#error-handling--retries)

## ADK Session Persistence with Supabase

### Database Session Service

```python
# backend/app/services/supabase_session_service.py
from google.adk.sessions import DatabaseSessionService
from typing import Optional
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

class SupabaseSessionService(DatabaseSessionService):
    """Enhanced session service with Supabase-specific features."""
    
    def __init__(self, db_url: Optional[str] = None):
        db_url = db_url or os.getenv(
            "SUPABASE_DB_URL",
            "postgresql://postgres:postgres@localhost:54322/postgres"
        )
        
        # Use connection pooling for better performance
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True  # Verify connections before using
        )
        
        super().__init__(db_url=db_url)
        self.engine = engine
    
    async def get_user_sessions(self, user_id: str, limit: int = 10):
        """Get recent sessions for a user."""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT session_id, updated_at, state
                    FROM adk_sessions
                    WHERE user_id = :user_id
                    ORDER BY updated_at DESC
                    LIMIT :limit
                """),
                {"user_id": user_id, "limit": limit}
            )
            return [dict(row) for row in result]
    
    async def cleanup_old_sessions(self, days: int = 30):
        """Remove sessions older than specified days."""
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    DELETE FROM adk_sessions
                    WHERE updated_at < NOW() - INTERVAL ':days days'
                """),
                {"days": days}
            )
            conn.commit()
```

### Usage in FastAPI

```python
# backend/app/main.py
from app.services.supabase_session_service import SupabaseSessionService
from google.adk.runners import Runner
from app.agents.base_agent import root_agent

# Initialize session service
session_service = SupabaseSessionService()

# Create runner
runner = Runner(
    app_name="adk-agent",
    agent=root_agent,
    session_service=session_service
)

@app.get("/api/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """Get user's recent sessions."""
    sessions = await session_service.get_user_sessions(user_id)
    return {"sessions": sessions}
```

## Real-time Agent Updates

### Supabase Real-time Subscriptions

```typescript
// frontend/lib/agent-realtime.ts
import { supabase } from './supabase'
import { RealtimeChannel } from '@supabase/supabase-js'

export class AgentRealtime {
  private channels: Map<string, RealtimeChannel> = new Map()

  subscribeToSession(
    sessionId: string,
    onUpdate: (data: any) => void
  ): RealtimeChannel {
    const channel = supabase
      .channel(`session:${sessionId}`)
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'adk_sessions',
          filter: `session_id=eq.${sessionId}`
        },
        (payload) => {
          onUpdate(payload.new)
        }
      )
      .subscribe()

    this.channels.set(sessionId, channel)
    return channel
  }

  unsubscribeFromSession(sessionId: string): void {
    const channel = this.channels.get(sessionId)
    if (channel) {
      supabase.removeChannel(channel)
      this.channels.delete(sessionId)
    }
  }

  subscribeToAgentEvents(
    userId: string,
    onEvent: (event: any) => void
  ): RealtimeChannel {
    const channel = supabase
      .channel(`agent-events:${userId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'adk_events',
          filter: `user_id=eq.${userId}`
        },
        (payload) => {
          onEvent(payload.new)
        }
      )
      .subscribe()

    return channel
  }
}

export const agentRealtime = new AgentRealtime()
```

### React Hook for Real-time Updates

```typescript
// frontend/hooks/useAgentSession.ts
import { useEffect, useState } from 'react'
import { agentRealtime } from '@/lib/agent-realtime'

export function useAgentSession(sessionId: string | null) {
  const [session, setSession] = useState<any>(null)

  useEffect(() => {
    if (!sessionId) return

    const channel = agentRealtime.subscribeToSession(sessionId, (data) => {
      setSession(data)
    })

    return () => {
      agentRealtime.unsubscribeFromSession(sessionId)
    }
  }, [sessionId])

  return session
}
```

## n8n Workflow Triggers

### Webhook Trigger from FastAPI

```python
# backend/app/api/routes/webhooks.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class AgentEvent(BaseModel):
    session_id: str
    user_id: str
    event_type: str
    data: dict

@router.post("/webhooks/n8n")
async def trigger_n8n_workflow(event: AgentEvent):
    """Trigger n8n workflow when agent event occurs."""
    n8n_webhook_url = os.getenv(
        "N8N_WEBHOOK_URL",
        "http://localhost:5678/webhook/agent-event"
    )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                n8n_webhook_url,
                json=event.dict(),
                timeout=5.0
            )
            response.raise_for_status()
            return {"status": "triggered", "data": response.json()}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger workflow: {str(e)}"
        )
```

### n8n Workflow: Process Agent Events

```json
{
  "name": "Process Agent Events",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "agent-event",
        "responseMode": "responseNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.event_type }}",
              "operation": "equals",
              "value2": "tool_execution"
            }
          ]
        }
      },
      "name": "Check Event Type",
      "type": "n8n-nodes-base.if",
      "position": [450, 300]
    },
    {
      "parameters": {
        "operation": "insert",
        "table": "adk_events",
        "columns": {
          "session_id": "={{ $json.session_id }}",
          "user_id": "={{ $json.user_id }}",
          "event_type": "={{ $json.event_type }}",
          "data": "={{ $json.data }}",
          "created_at": "={{ $now }}"
        }
      },
      "name": "Store Event",
      "type": "n8n-nodes-base.supabase",
      "position": [650, 300]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { \"success\": true } }}"
      },
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "position": [850, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Check Event Type", "type": "main", "index": 0}]]
    },
    "Check Event Type": {
      "main": [[{"node": "Store Event", "type": "main", "index": 0}]]
    },
    "Store Event": {
      "main": [[{"node": "Respond", "type": "main", "index": 0}]]
    }
  }
}
```

## Automated Agent Actions

### n8n Workflow: Scheduled Agent Tasks

```json
{
  "name": "Scheduled Agent Maintenance",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "hour": 3,
          "minute": 0
        }
      },
      "name": "Cron",
      "type": "n8n-nodes-base.cron",
      "position": [250, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT session_id FROM adk_sessions WHERE updated_at < NOW() - INTERVAL '30 days'"
      },
      "name": "Get Old Sessions",
      "type": "n8n-nodes-base.postgres",
      "position": [450, 300]
    },
    {
      "parameters": {
        "method": "DELETE",
        "url": "http://backend:8000/api/sessions/{{ $json.session_id }}"
      },
      "name": "Delete Session",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 300]
    }
  ]
}
```

### Trigger Agent from Database Change

```python
# backend/app/services/database_triggers.py
from supabase import create_client
import os

class DatabaseTriggerService:
    """Service to handle database triggers and notify agents."""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL", "http://localhost:54321")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.client = create_client(supabase_url, supabase_key)
    
    async def notify_agent_on_data_change(
        self,
        table: str,
        record_id: str,
        action: str
    ):
        """Notify agent when data changes."""
        # Store event in database
        self.client.table("adk_events").insert({
            "event_type": f"data_{action}",
            "data": {
                "table": table,
                "record_id": record_id,
                "action": action
            }
        }).execute()
        
        # Trigger n8n webhook if configured
        n8n_webhook = os.getenv("N8N_WEBHOOK_URL")
        if n8n_webhook:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(n8n_webhook, json={
                    "table": table,
                    "record_id": record_id,
                    "action": action
                })
```

## Data Synchronization

### Sync Agent State to Supabase

```python
# backend/app/services/state_sync.py
from google.adk.sessions import Session
from supabase import create_client
import os

class StateSyncService:
    """Sync agent state to Supabase in real-time."""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL", "http://localhost:54321")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.client = create_client(supabase_url, supabase_key)
    
    async def sync_session_state(self, session: Session):
        """Update session state in Supabase."""
        self.client.table("adk_sessions").update({
            "state": session.state,
            "events": [event.model_dump() for event in session.events],
            "updated_at": "now()"
        }).eq("session_id", session.id).execute()
    
    async def sync_to_memory(self, session: Session, content: str):
        """Add session content to long-term memory."""
        # Generate embedding (simplified - use actual embedding service)
        embedding = await self._generate_embedding(content)
        
        self.client.table("adk_memory").insert({
            "session_id": session.id,
            "user_id": session.user_id,
            "app_name": session.app_name,
            "content": content,
            "embedding": embedding,
            "metadata": {
                "created_at": session.last_update_time.isoformat()
            }
        }).execute()
    
    async def _generate_embedding(self, text: str):
        """Generate embedding for text (simplified)."""
        # Use actual embedding service (e.g., OpenAI, Vertex AI)
        # This is a placeholder
        return [0.0] * 1536
```

## Error Handling & Retries

### n8n Error Handling Workflow

```json
{
  "name": "Agent Error Handler",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "agent-error"
      },
      "name": "Error Webhook",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "parameters": {
        "operation": "insert",
        "table": "adk_errors",
        "columns": {
          "session_id": "={{ $json.session_id }}",
          "error_type": "={{ $json.error_type }}",
          "error_message": "={{ $json.error_message }}",
          "stack_trace": "={{ $json.stack_trace }}",
          "created_at": "={{ $now }}"
        }
      },
      "name": "Log Error",
      "type": "n8n-nodes-base.supabase"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.error_type }}",
              "operation": "equals",
              "value2": "rate_limit"
            }
          ]
        }
      },
      "name": "Check Error Type",
      "type": "n8n-nodes-base.if"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://backend:8000/api/retry",
        "bodyParameters": {
          "session_id": "={{ $json.session_id }}",
          "retry_after": 60
        }
      },
      "name": "Schedule Retry",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### FastAPI Error Handler

```python
# backend/app/middleware/error_handler.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import logging

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    """Handle errors and notify n8n."""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # Log error
        logger.error(f"Error: {str(e)}", exc_info=True)
        
        # Notify n8n if webhook configured
        n8n_webhook = os.getenv("N8N_ERROR_WEBHOOK_URL")
        if n8n_webhook:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(n8n_webhook, json={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "path": str(request.url),
                        "method": request.method
                    }, timeout=2.0)
            except:
                pass  # Don't fail if webhook fails
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
```

## Complete Integration Example

```python
# backend/app/main.py
from fastapi import FastAPI
from app.services.supabase_session_service import SupabaseSessionService
from app.services.state_sync import StateSyncService
from app.services.database_triggers import DatabaseTriggerService
from app.middleware.error_handler import error_handler_middleware
from google.adk.runners import Runner
from app.agents.base_agent import root_agent

app = FastAPI()

# Setup services
session_service = SupabaseSessionService()
state_sync = StateSyncService()
db_triggers = DatabaseTriggerService()

# Create runner
runner = Runner(
    app_name="adk-agent",
    agent=root_agent,
    session_service=session_service
)

# Add error handler
app.middleware("http")(error_handler_middleware)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with automatic state sync."""
    result = await runner.run_async(
        request.message,
        session_id=request.session_id,
        user_id=request.user_id
    )
    
    # Sync state to Supabase
    session = await session_service.get_session(
        result.session_id,
        result.user_id
    )
    await state_sync.sync_session_state(session)
    
    return {
        "response": result.content,
        "session_id": result.session_id
    }
```

## Best Practices

1. **Connection Pooling**: Always use connection pooling for database
2. **Error Handling**: Implement comprehensive error handling
3. **Retries**: Use exponential backoff for retries
4. **Monitoring**: Log all important events
5. **Security**: Never expose service keys in frontend
6. **Performance**: Cache frequently accessed data
7. **Testing**: Test all integrations locally first

## References

- **Supabase Python Client**: https://github.com/supabase/supabase-py
- **n8n Documentation**: https://docs.n8n.io/
- **ADK Sessions**: `../insp/adk-docs/docs/sessions/`

