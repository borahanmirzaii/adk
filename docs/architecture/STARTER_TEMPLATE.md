# Starter Template: Complete FastAPI + Next.js + ADK Setup

A ready-to-use template for getting started quickly.

## Quick Start

```bash
# Clone or copy this structure
mkdir my-adk-app && cd my-adk-app

# Follow the setup steps below
```

## Complete File Structure

```
my-adk-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   └── base_agent.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── chat.py
│   │   │       └── health.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── observability.py
│   ├── pyproject.toml
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── chat/
│   │       └── ChatInterface.tsx
│   ├── lib/
│   │   └── api.ts
│   ├── package.json
│   ├── .env.local.example
│   └── README.md
├── .gitignore
├── README.md
└── package.json
```

## Backend Files

### `backend/pyproject.toml`

```toml
[project]
name = "adk-backend"
version = "0.1.0"
description = "FastAPI backend for ADK agents"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "python-dotenv>=1.0.0",
    "pydantic-settings>=2.0.0",
    "google-adk>=0.1.0",
    "langfuse>=2.0.0",
    "openinference-instrumentation-google-adk>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### `backend/app/main.py`

```python
"""FastAPI application with ADK agent integration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import chat, health
from app.services.observability import setup_langfuse

# Setup observability
setup_langfuse()

# Create FastAPI app
app = FastAPI(
    title="ADK Agent API",
    description="FastAPI backend for ADK agents with CopilotKit support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "ADK Agent API",
        "docs": "/docs",
        "health": "/api/health"
    }
```

### `backend/app/config.py`

```python
"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # ADK Configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    PROJECT_ID: str | None = None
    LOCATION: str = "us-central1"
    
    # Langfuse Configuration (Optional)
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    # Session Configuration
    SESSION_STORAGE: str = "memory"  # memory, redis, postgres
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### `backend/app/agents/base_agent.py`

```python
"""Base ADK agent configuration."""

from google import adk
from app.config import settings

# Create the agent
agent = adk.LlmAgent(
    model=adk.models.Gemini(
        model_name=settings.GEMINI_MODEL,
        api_key=settings.GEMINI_API_KEY
    ),
    instructions="""You are a helpful AI assistant. 
    You provide clear, concise, and accurate responses.
    Always be polite and professional."""
)

# Export as root agent
root_agent = agent
```

### `backend/app/api/routes/health.py`

```python
"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "adk-agent-api"
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check."""
    return {
        "status": "ready",
        "service": "adk-agent-api"
    }
```

### `backend/app/api/routes/chat.py`

```python
"""Chat endpoints for agent interaction."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.agents.base_agent import root_agent

router = APIRouter()

# Setup runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="adk-agent",
    agent=root_agent,
    session_service=session_service
)

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: str | None = None
    user_id: str = "default"

class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the agent and get a response.
    
    Args:
        request: Chat request with message and optional session_id
        
    Returns:
        Chat response with agent's reply and session_id
    """
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
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )
```

### `backend/app/services/observability.py`

```python
"""Observability setup with Langfuse."""

from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from langfuse.opentelemetry import LangfuseSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from app.config import settings

def setup_langfuse():
    """Setup Langfuse observability for ADK."""
    if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
        print("Langfuse not configured, skipping observability setup")
        return
    
    try:
        # Setup OpenTelemetry
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()
        
        # Instrument ADK
        GoogleADKInstrumentor().instrument()
        
        # Add Langfuse span processor
        tracer_provider.add_span_processor(
            BatchSpanProcessor(LangfuseSpanProcessor())
        )
        
        print("Langfuse observability enabled")
    except Exception as e:
        print(f"Failed to setup Langfuse: {e}")
```

### `backend/.env.example`

```bash
# Gemini API
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# Langfuse (Optional)
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com

# CORS
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

## Frontend Files

### `frontend/app/layout.tsx`

```typescript
'use client'

import { CopilotKit } from '@copilotkit/react-core'
import { CopilotSidebar } from '@copilotkit/react-ui'
import '@copilotkit/react-ui/styles.css'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <CopilotKit runtimeUrl={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/copilotkit`}>
          <CopilotSidebar>
            {children}
          </CopilotSidebar>
        </CopilotKit>
      </body>
    </html>
  )
}
```

### `frontend/app/page.tsx`

```typescript
'use client'

import { ChatInterface } from '@/components/chat/ChatInterface'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8">ADK Agent Chat</h1>
        <ChatInterface />
      </div>
    </main>
  )
}
```

### `frontend/components/chat/ChatInterface.tsx`

```typescript
'use client'

import { useState } from 'react'
import { sendMessage } from '@/lib/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = input
    setInput('')
    setLoading(true)

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      const response = await sendMessage({
        message: userMessage,
        session_id: sessionId || undefined,
      })

      // Add assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }])
      setSessionId(response.session_id)
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[600px] border rounded-lg p-4">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-500 text-white ml-auto max-w-[80%]'
                : 'bg-gray-200 text-gray-800 mr-auto max-w-[80%]'
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
          className="flex-1 p-2 border rounded"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  )
}
```

### `frontend/lib/api.ts`

```typescript
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
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Failed to send message')
  }

  return response.json()
}
```

### `frontend/package.json`

```json
{
  "name": "adk-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "14.0.0",
    "@copilotkit/react-core": "^1.0.0",
    "@copilotkit/react-ui": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### `frontend/.env.local.example`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Root Files

### Root `package.json`

```json
{
  "name": "adk-agent-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && uv run uvicorn app.main:app --reload --port 8000",
    "dev:frontend": "cd frontend && npm run dev",
    "install:all": "cd backend && uv sync && cd ../frontend && npm install"
  },
  "devDependencies": {
    "concurrently": "^8.2.2"
  }
}
```

### `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Node
node_modules/
.next/
out/
dist/

# Environment
.env
.env.local
.env*.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

## Setup Instructions

1. **Copy the structure** to your project directory
2. **Backend setup**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your API keys
   uv sync
   ```
3. **Frontend setup**:
   ```bash
   cd frontend
   cp .env.local.example .env.local
   npm install
   ```
4. **Run**:
   ```bash
   # From root
   npm install  # Install concurrently
   npm run dev
   ```

## Testing

- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Health: http://localhost:8000/api/health

## Next Steps

1. Add authentication
2. Add database for session persistence
3. Add WebSocket support for real-time chat
4. Add more agent tools
5. Deploy to production

See `BEST_PRACTICES.md` for advanced patterns.

