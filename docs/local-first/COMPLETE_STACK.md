# Complete Stack: Local-First with Langfuse, LangGraph, and CopilotKit

Complete integration guide for local-first development with all components: OrbStack, Supabase, n8n, ADK, Langfuse, LangGraph, and CopilotKit.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Langfuse Local Setup](#langfuse-local-setup)
3. [LangGraph Integration](#langgraph-integration)
4. [CopilotKit (Agent UI SDK) Setup](#copilotkit-agent-ui-sdk-setup)
5. [Complete Docker Compose](#complete-docker-compose)
6. [Integration Patterns](#integration-patterns)
7. [Development Workflow](#development-workflow)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│           Local Development Environment (OrbStack)          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Supabase │◄─┤   n8n    │◄─┤ FastAPI  │◄─┤ Langfuse │  │
│  │ (Postgres)│  │(Automation)│ │ (ADK)    │  │(Observability)│
│  │          │  │          │  │          │  │          │  │
│  │ - DB     │  │ - Webhooks│  │ - Agents │  │ - Traces │  │
│  │ - Auth   │  │ - Workflows│ │ - LangGraph│ │ - Analytics│
│  │ - Real-time│ │ - Triggers│ │ - Tools  │  │ - Metrics│
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │              │             │         │
│       └─────────────┴──────────────┴─────────────┘         │
│                    │                                        │
│                    ▼                                        │
│            ┌──────────────┐                                 │
│            │   Next.js    │                                 │
│            │ (CopilotKit) │                                 │
│            │  (Agent UI)  │                                 │
│            └──────────────┘                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Langfuse Local Setup

### Self-Hosted Langfuse with Docker

```yaml
# docker-compose.langfuse.yml
version: '3.8'

services:
  langfuse-db:
    image: postgres:15
    container_name: langfuse_db
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse
      POSTGRES_DB: langfuse
    volumes:
      - langfuse_db_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - adk-network

  langfuse:
    image: langfuse/langfuse:latest
    container_name: langfuse
    ports:
      - "3001:3000"
    environment:
      DATABASE_URL: postgresql://langfuse:langfuse@langfuse-db:5432/langfuse
      NEXTAUTH_SECRET: your-secret-key-here
      NEXTAUTH_URL: http://localhost:3001
      SALT: your-salt-here
      LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES: "true"
    depends_on:
      - langfuse-db
    networks:
      - adk-network

volumes:
  langfuse_db_data:

networks:
  adk-network:
    external: true
```

### Start Langfuse

```bash
# Create network if not exists
docker network create adk-network

# Start Langfuse
docker-compose -f docker-compose.langfuse.yml up -d

# Access Langfuse
# http://localhost:3001
# Default credentials: admin@langfuse.com / langfuse
```

### ADK Integration with Langfuse

```python
# backend/app/services/langfuse_setup.py
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from langfuse.opentelemetry import LangfuseSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import os

def setup_langfuse():
    """Setup Langfuse observability for ADK."""
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_host = os.getenv("LANGFUSE_HOST", "http://localhost:3001")
    
    if not langfuse_public_key or not langfuse_secret_key:
        print("Langfuse not configured, skipping observability setup")
        return
    
    try:
        # Setup OpenTelemetry
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()
        
        # Instrument ADK
        GoogleADKInstrumentor().instrument()
        
        # Add Langfuse span processor
        langfuse_processor = LangfuseSpanProcessor(
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key,
            host=langfuse_host
        )
        
        tracer_provider.add_span_processor(
            BatchSpanProcessor(langfuse_processor)
        )
        
        print(f"Langfuse observability enabled at {langfuse_host}")
    except Exception as e:
        print(f"Failed to setup Langfuse: {e}")
```

### Environment Variables

```bash
# backend/.env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3001
```

## LangGraph Integration

### Install Dependencies

```bash
cd backend
uv add langgraph langchain-google-genai
```

### Create LangGraph Workflow with ADK

```python
# backend/app/agents/langgraph_workflow.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from google import adk
from app.config import settings

class AgentState(TypedDict):
    query: str
    research: str
    analysis: str
    response: str

# Create ADK agents for each step
researcher = adk.LlmAgent(
    model=adk.models.Gemini(
        model_name=settings.GEMINI_MODEL,
        api_key=settings.GEMINI_API_KEY
    ),
    instructions="You are a research assistant. Research topics thoroughly."
)

analyzer = adk.LlmAgent(
    model=adk.models.Gemini(
        model_name=settings.GEMINI_MODEL,
        api_key=settings.GEMINI_API_KEY
    ),
    instructions="You analyze research and provide insights."
)

responder = adk.LlmAgent(
    model=adk.models.Gemini(
        model_name=settings.GEMINI_MODEL,
        api_key=settings.GEMINI_API_KEY
    ),
    instructions="You provide clear, concise responses based on analysis."
)

# Define nodes
def research_node(state: AgentState) -> AgentState:
    """Research the query."""
    result = researcher.run(state["query"])
    return {"research": result.content}

def analyze_node(state: AgentState) -> AgentState:
    """Analyze the research."""
    result = analyzer.run(f"Analyze: {state['research']}")
    return {"analysis": result.content}

def respond_node(state: AgentState) -> AgentState:
    """Generate final response."""
    result = responder.run(
        f"Based on this analysis: {state['analysis']}, "
        f"respond to: {state['query']}"
    )
    return {"response": result.content}

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("research", research_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("respond", respond_node)

# Define edges
workflow.set_entry_point("research")
workflow.add_edge("research", "analyze")
workflow.add_edge("analyze", "respond")
workflow.add_edge("respond", END)

# Compile workflow
agent_workflow = workflow.compile()
```

### FastAPI Integration

```python
# backend/app/api/routes/langgraph.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.langgraph_workflow import agent_workflow

router = APIRouter()

class LangGraphRequest(BaseModel):
    query: str

class LangGraphResponse(BaseModel):
    response: str
    steps: list

@router.post("/langgraph", response_model=LangGraphResponse)
async def langgraph_chat(request: LangGraphRequest):
    """Process query through LangGraph workflow."""
    result = agent_workflow.invoke({"query": request.query})
    
    return LangGraphResponse(
        response=result["response"],
        steps=[
            {"step": "research", "result": result["research"]},
            {"step": "analysis", "result": result["analysis"]},
            {"step": "response", "result": result["response"]}
        ]
    )
```

## CopilotKit (Agent UI SDK) Setup

### Backend Integration

```python
# backend/app/api/routes/copilotkit.py
from fastapi import APIRouter
from copilotkit.integrations.fastapi import add_copilotkit_endpoint
from app.agents.langgraph_workflow import agent_workflow

router = APIRouter()

# Add CopilotKit endpoint for AG-UI protocol
add_copilotkit_endpoint(
    router,
    agent=agent_workflow,
    path="/copilotkit"
)
```

### Frontend Integration

```typescript
// frontend/app/layout.tsx
'use client'

import { CopilotKit } from '@copilotkit/react-core'
import { CopilotSidebar } from '@copilotkit/react-ui'
import '@copilotkit/react-ui/styles.css'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <CopilotKit
          runtimeUrl={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/copilotkit`}
        >
          <CopilotSidebar>
            {children}
          </CopilotSidebar>
        </CopilotKit>
      </body>
    </html>
  )
}
```

### Install Frontend Dependencies

```bash
cd frontend
npm install @copilotkit/react-core @copilotkit/react-ui
```

## Complete Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Supabase (managed by Supabase CLI)
  supabase_db:
    image: supabase/postgres:15.1.0.147
    container_name: supabase_db
    ports:
      - "54322:5432"
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    volumes:
      - supabase_db_data:/var/lib/postgresql/data
    networks:
      - adk-network

  # Langfuse
  langfuse-db:
    image: postgres:15
    container_name: langfuse_db
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse
      POSTGRES_DB: langfuse
    volumes:
      - langfuse_db_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - adk-network

  langfuse:
    image: langfuse/langfuse:latest
    container_name: langfuse
    ports:
      - "3001:3000"
    environment:
      DATABASE_URL: postgresql://langfuse:langfuse@langfuse-db:5432/langfuse
      NEXTAUTH_SECRET: your-secret-key
      NEXTAUTH_URL: http://localhost:3001
      SALT: your-salt
    depends_on:
      - langfuse-db
    networks:
      - adk-network

  # n8n
  n8n:
    image: n8nio/n8n
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=supabase_db
      - DB_POSTGRESDB_DATABASE=postgres
      - DB_POSTGRESDB_USER=postgres
      - DB_POSTGRESDB_PASSWORD=postgres
      - DB_POSTGRESDB_PORT=5432
    volumes:
      - ~/.n8n:/home/node/.n8n
    networks:
      - adk-network
    depends_on:
      - supabase_db

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: adk-backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=http://supabase_kong:8000
      - SUPABASE_DB_URL=postgresql://postgres:postgres@supabase_db:5432/postgres
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_HOST=http://langfuse:3000
    volumes:
      - ./backend:/app
    networks:
      - adk-network
    depends_on:
      - supabase_db
      - langfuse

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: adk-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - adk-network
    depends_on:
      - backend

networks:
  adk-network:
    driver: bridge

volumes:
  supabase_db_data:
  langfuse_db_data:
```

## Integration Patterns

### LangGraph + ADK + Langfuse

```python
# backend/app/agents/integrated_agent.py
from langgraph.graph import StateGraph, END
from google import adk
from app.services.langfuse_setup import setup_langfuse

# Setup Langfuse first
setup_langfuse()

# Create ADK agents
adk_agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You are a helpful assistant."
)

# Wrap ADK agent in LangGraph node
def adk_node(state):
    result = adk_agent.run(state["query"])
    return {"response": result.content}

# Build LangGraph workflow
workflow = StateGraph(dict)
workflow.add_node("adk_agent", adk_node)
workflow.set_entry_point("adk_agent")
workflow.add_edge("adk_agent", END)

agent = workflow.compile()
```

### CopilotKit + LangGraph + ADK

```python
# backend/app/api/routes/copilotkit_langgraph.py
from fastapi import APIRouter
from copilotkit.integrations.fastapi import add_copilotkit_endpoint
from app.agents.integrated_agent import agent

router = APIRouter()

# Expose LangGraph agent via CopilotKit
add_copilotkit_endpoint(
    router,
    agent=agent,
    path="/copilotkit"
)
```

### n8n Workflow: Monitor Langfuse Traces

```json
{
  "name": "Monitor Agent Performance",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "hour": 1,
          "minute": 0
        }
      },
      "name": "Cron",
      "type": "n8n-nodes-base.cron"
    },
    {
      "parameters": {
        "method": "GET",
        "url": "http://langfuse:3000/api/public/traces",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth"
      },
      "name": "Get Traces",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "parameters": {
        "operation": "insert",
        "table": "agent_metrics",
        "columns": {
          "date": "={{ $now }}",
          "trace_count": "={{ $json.length }}",
          "data": "={{ $json }}"
        }
      },
      "name": "Store Metrics",
      "type": "n8n-nodes-base.supabase"
    }
  ]
}
```

## Development Workflow

### Start All Services

```bash
# Start Supabase
supabase start

# Start all Docker services
docker-compose up -d

# Verify services
curl http://localhost:3001  # Langfuse
curl http://localhost:5678  # n8n
curl http://localhost:8000/docs  # FastAPI
curl http://localhost:3000  # Next.js
```

### Makefile

```makefile
.PHONY: dev stop clean logs

dev:
	supabase start
	docker-compose up -d
	@echo "Services running:"
	@echo "  Supabase Studio: http://localhost:54323"
	@echo "  Langfuse: http://localhost:3001"
	@echo "  n8n: http://localhost:5678"
	@echo "  FastAPI: http://localhost:8000/docs"
	@echo "  Next.js: http://localhost:3000"

stop:
	supabase stop
	docker-compose down

clean:
	docker-compose down -v
	supabase stop --no-backup

logs:
	docker-compose logs -f

logs-langfuse:
	docker-compose logs -f langfuse

logs-backend:
	docker-compose logs -f backend
```

## Environment Variables

```bash
# .env
# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_DB_URL=postgresql://postgres:postgres@localhost:54322/postgres
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3001

# ADK
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.0-flash-exp

# n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook
```

## Testing the Integration

### Test Langfuse

```python
# backend/test_langfuse.py
from app.services.langfuse_setup import setup_langfuse
from google import adk

setup_langfuse()

agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Test agent"
)

result = agent.run("Hello!")
print(result.content)
# Check Langfuse dashboard at http://localhost:3001
```

### Test LangGraph

```python
# backend/test_langgraph.py
from app.agents.langgraph_workflow import agent_workflow

result = agent_workflow.invoke({"query": "What is AI?"})
print(result["response"])
```

### Test CopilotKit

```bash
# Start frontend and backend
# Open http://localhost:3000
# Use CopilotKit chat interface
```

## Best Practices

1. **Observability First**: Setup Langfuse before building agents
2. **Workflow Design**: Use LangGraph for complex multi-step workflows
3. **UI Integration**: Use CopilotKit for consistent agent UI
4. **Local Development**: Run everything locally for fast iteration
5. **Monitoring**: Use n8n to monitor and automate based on Langfuse metrics

## References

- **Langfuse Self-Hosted**: https://langfuse.com/docs/deployment/self-host
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **CopilotKit Docs**: https://docs.copilotkit.ai/
- **ADK Integration**: `../integrations/COPILOTKIT_LANGGRAPH_LANGFUSE.md`

