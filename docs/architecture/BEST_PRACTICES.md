# Best Practices: FastAPI + Next.js + ADK Architecture

This document outlines best practices for building a production-ready application with FastAPI backend, Next.js frontend, and ADK agents, integrated with CopilotKit and Langfuse.

## Table of Contents
1. [Project Structure](#project-structure)
2. [Backend Architecture (FastAPI)](#backend-architecture-fastapi)
3. [Frontend Architecture (Next.js)](#frontend-architecture-nextjs)
4. [Integration Patterns](#integration-patterns)
5. [Security Best Practices](#security-best-practices)
6. [Development Workflow](#development-workflow)
7. [Deployment Strategy](#deployment-strategy)

## Project Structure

### Recommended Monorepo Structure

```
adk-agent-app/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py           # Configuration management
│   │   ├── agents/             # ADK agents
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py   # Base agent setup
│   │   │   └── tools/           # Custom tools
│   │   ├── api/                # API routes
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── chat.py     # Chat endpoints
│   │   │   │   ├── agent.py    # Agent management
│   │   │   │   └── health.py   # Health checks
│   │   │   └── websocket.py    # WebSocket endpoints
│   │   ├── services/           # Business logic
│   │   │   ├── session.py      # Session management
│   │   │   └── observability.py # Langfuse integration
│   │   └── middleware/        # Custom middleware
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml         # Project config (uv)
│   └── .env.example           # Environment template
├── frontend/                  # Next.js frontend
│   ├── app/                   # Next.js app directory
│   │   ├── layout.tsx         # Root layout with CopilotKit
│   │   ├── page.tsx           # Main page
│   │   └── api/               # API routes (if needed)
│   ├── components/           # React components
│   │   ├── chat/              # Chat components
│   │   └── ui/                # UI components
│   ├── lib/                   # Utilities
│   │   ├── api.ts             # API client
│   │   └── copilotkit.ts      # CopilotKit config
│   ├── public/                # Static assets
│   ├── package.json
│   └── .env.local.example
├── shared/                    # Shared types/schemas
│   ├── types/                 # TypeScript types
│   └── schemas/               # Pydantic/Zod schemas
├── docker/                    # Docker configs
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── .github/                   # CI/CD
│   └── workflows/
├── README.md
└── .gitignore
```

## Backend Architecture (FastAPI)

### 1. Application Setup

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.config import settings
from app.api.routes import chat, agent, health
from app.services.observability import setup_langfuse

app = FastAPI(
    title="ADK Agent API",
    description="FastAPI backend for ADK agents",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup observability
setup_langfuse()

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### 2. Configuration Management

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # ADK
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    PROJECT_ID: str | None = None
    LOCATION: str = "us-central1"
    
    # Langfuse
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    # Session
    SESSION_STORAGE: str = "memory"  # memory, redis, postgres
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 3. Agent Setup with ADK

```python
# backend/app/agents/base_agent.py
from google import adk
from google.adk.sessions import InMemorySessionService
from app.config import settings
from app.services.observability import instrument_adk

# Setup session service
session_service = InMemorySessionService()

# Create base agent
base_agent = adk.LlmAgent(
    model=adk.models.Gemini(
        model_name=settings.GEMINI_MODEL,
        api_key=settings.GEMINI_API_KEY
    ),
    instructions="You are a helpful AI assistant."
)

# Instrument with Langfuse
instrument_adk()

# Export configured agent
root_agent = base_agent
```

### 4. API Routes

```python
# backend/app/api/routes/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.adk.runners import Runner
from app.agents.base_agent import root_agent, session_service

router = APIRouter()
runner = Runner(
    app_name="adk-agent",
    agent=root_agent,
    session_service=session_service
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await runner.run_async(
            request.message,
            session_id=request.session_id,
            user_id=request.user_id
        )
        return ChatResponse(
            response=result.content,
            session_id=result.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 5. WebSocket Support

```python
# backend/app/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from app.agents.base_agent import root_agent, session_service

runner = Runner(
    app_name="adk-agent",
    agent=root_agent,
    session_service=session_service
)

@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str):
    await websocket.accept()
    
    try:
        config = RunConfig(
            streaming_mode=StreamingMode.STREAMING,
            session_id=session_id,
            user_id=user_id
        )
        
        async for event in runner.stream_async("", config=config):
            await websocket.send_json(event.model_dump())
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
```

### 6. Langfuse Integration

```python
# backend/app/services/observability.py
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from langfuse.opentelemetry import LangfuseSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from app.config import settings

def setup_langfuse():
    if not settings.LANGFUSE_PUBLIC_KEY:
        return
    
    # Setup OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    
    # Instrument ADK
    GoogleADKInstrumentor().instrument()
    
    # Add Langfuse
    tracer_provider.add_span_processor(
        BatchSpanProcessor(LangfuseSpanProcessor())
    )
```

## Frontend Architecture (Next.js)

### 1. CopilotKit Setup

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
        <CopilotKit runtimeUrl="http://localhost:8000/api/copilotkit">
          <CopilotSidebar>
            {children}
          </CopilotSidebar>
        </CopilotKit>
      </body>
    </html>
  )
}
```

### 2. API Client

```typescript
// frontend/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatRequest {
  message: string
  session_id?: string
  user_id?: string
}

export interface ChatResponse {
  response: string
  session_id: string
}

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    throw new Error('Failed to send message')
  }
  
  return response.json()
}
```

### 3. Chat Component

```typescript
// frontend/components/chat/ChatInterface.tsx
'use client'
import { useState } from 'react'
import { sendMessage } from '@/lib/api'

export function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  
  const handleSend = async () => {
    const response = await sendMessage({
      message: input,
      session_id: sessionId || undefined,
    })
    
    setMessages([...messages, { role: 'user', content: input }])
    setMessages([...messages, { role: 'assistant', content: response.response }])
    setSessionId(response.session_id)
    setInput('')
  }
  
  return (
    <div className="chat-container">
      {/* Chat UI */}
    </div>
  )
}
```

## Integration Patterns

### 1. AG-UI Protocol with CopilotKit

```python
# backend/app/api/routes/copilotkit.py
from fastapi import APIRouter
from copilotkit.integrations.fastapi import add_copilotkit_endpoint
from app.agents.base_agent import root_agent

router = APIRouter()

# Add CopilotKit endpoint
add_copilotkit_endpoint(
    router,
    agent=root_agent,
    path="/copilotkit"
)
```

### 2. Type Safety with Pydantic + Zod

```python
# shared/schemas/chat.py (Pydantic)
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
```

```typescript
// shared/schemas/chat.ts (Zod)
import { z } from 'zod'

export const ChatRequestSchema = z.object({
  message: z.string(),
  session_id: z.string().optional(),
})
```

## Security Best Practices

### 1. Authentication

```python
# backend/app/middleware/auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

async def verify_token(token: str = Security(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 2. Input Validation

```python
# Always validate inputs
from pydantic import BaseModel, validator

class ChatRequest(BaseModel):
    message: str
    
    @validator('message')
    def validate_message(cls, v):
        if len(v) > 10000:
            raise ValueError('Message too long')
        return v.strip()
```

### 3. Environment Variables

```bash
# backend/.env
GEMINI_API_KEY=your-key-here
LANGFUSE_PUBLIC_KEY=your-key
LANGFUSE_SECRET_KEY=your-secret
CORS_ORIGINS=["http://localhost:3000"]
```

## Development Workflow

### 1. Concurrent Development

```json
// package.json (root)
{
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && uvicorn app.main:app --reload",
    "dev:frontend": "cd frontend && next dev"
  }
}
```

### 2. Type Generation

```bash
# Generate TypeScript types from Pydantic models
datamodel-codegen --input backend/app/schemas --output frontend/lib/types
```

## Deployment Strategy

### 1. Docker Setup

```dockerfile
# docker/Dockerfile.backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
# docker/docker-compose.yml
version: '3.8'
services:
  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
  
  frontend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## Key Takeaways

1. **Separation of Concerns**: Clear separation between frontend and backend
2. **Type Safety**: Use Pydantic and Zod for shared schemas
3. **Observability**: Integrate Langfuse from the start
4. **Security**: Always validate inputs and use proper authentication
5. **Development**: Use concurrent tools for smooth development
6. **Deployment**: Containerize for consistency

## References

- FastAPI Best Practices: https://fastapi.tiangolo.com/
- Next.js Documentation: https://nextjs.org/docs
- CopilotKit Integration: `../integrations/COPILOTKIT_LANGGRAPH_LANGFUSE.md`
- ADK Documentation: `../insp/adk-docs/docs/`

