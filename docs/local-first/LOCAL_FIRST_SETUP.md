# Local-First Development: OrbStack + Supabase + n8n + ADK

Comprehensive guide for setting up a local-first development environment with OrbStack, Supabase, n8n, and ADK agents.

## Table of Contents
1. [Overview](#overview)
2. [Local-First Architecture](#local-first-architecture)
3. [OrbStack Setup](#orbstack-setup)
4. [Supabase Local Development](#supabase-local-development)
5. [n8n Integration](#n8n-integration)
6. [ADK Integration with Supabase](#adk-integration-with-supabase)
7. [Complete Docker Compose Setup](#complete-docker-compose-setup)
8. [Development Workflow](#development-workflow)
9. [Best Practices](#best-practices)

## Overview

### What is Local-First Development?

Local-first development emphasizes:
- **Offline Capability**: Work without internet connection
- **Data Sovereignty**: Your data stays on your machine
- **Fast Iteration**: No network latency
- **Cost Efficiency**: No cloud costs during development
- **Privacy**: Sensitive data never leaves your machine

### Technology Stack

- **OrbStack**: Lightweight Docker alternative for macOS
- **Supabase**: Local PostgreSQL database with real-time capabilities
- **n8n**: Workflow automation for backend processes
- **ADK**: Agent Development Kit for AI agents
- **Langfuse**: LLM observability and tracing (self-hosted)
- **LangGraph**: Workflow orchestration for complex agent behaviors
- **CopilotKit**: Agent UI SDK for building agent interfaces
- **FastAPI**: Python backend API
- **Next.js**: React frontend

## Local-First Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Local Development Environment               │
│                    (OrbStack/Docker)                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Supabase   │  │     n8n     │  │   FastAPI    │  │
│  │  (Postgres)  │◄─┤  (Automation)│◄─┤  (ADK API)   │  │
│  │              │  │              │  │              │  │
│  │ - Database   │  │ - Webhooks   │  │ - Agents     │  │
│  │ - Auth       │  │ - Workflows  │  │ - Sessions   │  │
│  │ - Storage    │  │ - Triggers   │  │ - Tools      │  │
│  │ - Real-time  │  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │           │
│         └─────────────────┴──────────────────┘           │
│                          │                               │
│                          ▼                               │
│                  ┌──────────────┐                       │
│                  │   Next.js    │                       │
│                  │  (Frontend)  │                       │
│                  │              │                       │
│                  │ - CopilotKit │                       │
│                  │ - UI         │                       │
│                  └──────────────┘                       │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## OrbStack Setup

### Installation

1. **Download OrbStack**:
   ```bash
   # Visit https://orbstack.dev/ or use Homebrew
   brew install orbstack
   ```

2. **Verify Installation**:
   ```bash
   docker --version
   docker ps
   ```

3. **OrbStack Benefits**:
   - Faster than Docker Desktop
   - Lower resource usage
   - Native macOS integration
   - Docker API compatible

### Configuration

Create `~/.orbstack/config.yaml`:

```yaml
# OrbStack configuration
resources:
  cpus: 4
  memory: 8GB
  disk: 50GB

networking:
  host_network: true
  dns:
    - 8.8.8.8
    - 8.8.4.4
```

## Supabase Local Development

### Installation

```bash
# Install Supabase CLI
npm install -g supabase

# Or using Homebrew
brew install supabase/tap/supabase
```

### Project Setup

```bash
# Initialize Supabase project
cd your-project
supabase init

# Start Supabase locally (uses OrbStack/Docker)
supabase start
```

### Supabase Services

After `supabase start`, you get:

- **PostgreSQL**: `postgresql://postgres:postgres@localhost:54322/postgres`
- **API URL**: `http://localhost:54321`
- **Studio**: `http://localhost:54323`
- **Auth**: `http://localhost:54324`
- **Storage**: `http://localhost:54325`

### Database Schema for ADK

```sql
-- Create sessions table for ADK
CREATE TABLE adk_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT UNIQUE NOT NULL,
  user_id TEXT NOT NULL,
  app_name TEXT NOT NULL,
  state JSONB DEFAULT '{}',
  events JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast lookups
CREATE INDEX idx_adk_sessions_user_id ON adk_sessions(user_id);
CREATE INDEX idx_adk_sessions_session_id ON adk_sessions(session_id);

-- Create memory table for long-term storage
CREATE TABLE adk_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,
  app_name TEXT,
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  embedding VECTOR(1536), -- For semantic search
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for vector search
CREATE INDEX idx_adk_memory_embedding ON adk_memory 
USING ivfflat (embedding vector_cosine_ops);

-- Create artifacts table for binary data
CREATE TABLE adk_artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT,
  name TEXT NOT NULL,
  mime_type TEXT,
  data BYTEA,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Real-time Subscriptions

```typescript
// frontend/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:54321'
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'your-anon-key'

export const supabase = createClient(supabaseUrl, supabaseKey)

// Subscribe to session updates
export function subscribeToSession(sessionId: string, callback: (data: any) => void) {
  return supabase
    .channel(`session:${sessionId}`)
    .on('postgres_changes', {
      event: 'UPDATE',
      schema: 'public',
      table: 'adk_sessions',
      filter: `session_id=eq.${sessionId}`
    }, callback)
    .subscribe()
}
```

## n8n Integration

### Docker Setup

```yaml
# docker-compose.n8n.yml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=supabase_db
      - DB_POSTGRESDB_DATABASE=postgres
      - DB_POSTGRESDB_USER=postgres
      - DB_POSTGRESDB_PASSWORD=postgres
      - DB_POSTGRESDB_PORT=5432
    volumes:
      - ~/.n8n:/home/node/.n8n
      - ./n8n/workflows:/data/workflows
    networks:
      - adk-network
    depends_on:
      - supabase_db
```

### n8n Workflows for ADK

#### 1. Session Cleanup Workflow

```json
{
  "name": "Cleanup Old Sessions",
  "nodes": [
    {
      "name": "Cron Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "hour": 2,
          "minute": 0
        }
      }
    },
    {
      "name": "Delete Old Sessions",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "DELETE FROM adk_sessions WHERE updated_at < NOW() - INTERVAL '30 days'"
      }
    }
  ]
}
```

#### 2. Agent Event Webhook

```json
{
  "name": "Process Agent Events",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "agent-event",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Store in Supabase",
      "type": "n8n-nodes-base.supabase",
      "parameters": {
        "operation": "insert",
        "table": "adk_events",
        "columns": {
          "session_id": "={{ $json.session_id }}",
          "event_type": "={{ $json.event_type }}",
          "data": "={{ $json.data }}"
        }
      }
    }
  ]
}
```

## ADK Integration with Supabase

### Database Session Service

```python
# backend/app/services/supabase_session.py
from google.adk.sessions import DatabaseSessionService
from app.config import settings
import os

# Get Supabase database URL
supabase_db_url = os.getenv(
    "SUPABASE_DB_URL",
    "postgresql://postgres:postgres@localhost:54322/postgres"
)

# Create database session service
session_service = DatabaseSessionService(db_url=supabase_db_url)
```

### Supabase Memory Service

```python
# backend/app/services/supabase_memory.py
from google.adk.memory import BaseMemoryService
from supabase import create_client, Client
import os

class SupabaseMemoryService(BaseMemoryService):
    """Memory service using Supabase for storage."""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL", "http://localhost:54321")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "your-service-key")
        self.client: Client = create_client(supabase_url, supabase_key)
    
    async def add_session_to_memory(
        self,
        session_id: str,
        user_id: str,
        app_name: str,
        content: str,
        metadata: dict = None
    ):
        """Add session content to memory."""
        self.client.table("adk_memory").insert({
            "session_id": session_id,
            "user_id": user_id,
            "app_name": app_name,
            "content": content,
            "metadata": metadata or {}
        }).execute()
    
    async def search_memory(
        self,
        query: str,
        user_id: str = None,
        app_name: str = None,
        limit: int = 10
    ):
        """Search memory using vector similarity."""
        # Use Supabase vector search
        response = self.client.rpc(
            "search_memory",
            {
                "query_embedding": self._get_embedding(query),
                "user_id": user_id,
                "app_name": app_name,
                "match_threshold": 0.7,
                "match_count": limit
            }
        ).execute()
        
        return response.data
```

### FastAPI Integration

```python
# backend/app/main.py
from fastapi import FastAPI
from app.services.supabase_session import session_service
from app.services.supabase_memory import SupabaseMemoryService
from app.agents.base_agent import root_agent
from google.adk.runners import Runner

app = FastAPI()

# Setup memory service
memory_service = SupabaseMemoryService()

# Create runner with Supabase session service
runner = Runner(
    app_name="adk-agent",
    agent=root_agent,
    session_service=session_service,
    memory_service=memory_service
)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    result = await runner.run_async(
        request.message,
        session_id=request.session_id,
        user_id=request.user_id
    )
    return {"response": result.content, "session_id": result.session_id}
```

## Complete Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Supabase (managed by Supabase CLI, but we can reference it)
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
    volumes:
      - ./backend:/app
    networks:
      - adk-network
    depends_on:
      - supabase_db

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
```

## Development Workflow

### 1. Start All Services

```bash
# Start Supabase
supabase start

# Start other services
docker-compose up -d

# Or use make
make dev
```

### 2. Development Scripts

```makefile
# Makefile
.PHONY: dev stop clean reset

dev:
	supabase start
	docker-compose up -d
	@echo "Services running:"
	@echo "  Supabase Studio: http://localhost:54323"
	@echo "  n8n: http://localhost:5678"
	@echo "  FastAPI: http://localhost:8000"
	@echo "  Next.js: http://localhost:3000"

stop:
	supabase stop
	docker-compose down

clean:
	docker-compose down -v
	supabase stop --no-backup

reset:
	make clean
	make dev
```

### 3. Database Migrations

```bash
# Create migration
supabase migration new create_adk_tables

# Apply migration
supabase db reset

# Or apply specific migration
supabase migration up
```

## Best Practices

### 1. Environment Variables

```bash
# .env.local
# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_DB_URL=postgresql://postgres:postgres@localhost:54322/postgres
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# ADK
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.0-flash-exp

# n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook
```

### 2. Data Persistence

- Use Docker volumes for data persistence
- Regular backups of Supabase database
- Version control for n8n workflows

### 3. Security

- Never commit `.env` files
- Use service role keys only in backend
- Use anon keys in frontend
- Secure n8n with authentication

### 4. Performance

- Use connection pooling for database
- Cache frequently accessed data
- Optimize n8n workflows
- Monitor resource usage

## Next Steps

1. **Setup**: Follow this guide to set up your local environment
2. **Schema**: Create database schema for your use case
3. **Workflows**: Build n8n workflows for automation
4. **Integration**: Connect ADK agents to Supabase
5. **Testing**: Test all integrations locally
6. **Deploy**: Use same setup for production

## References

- **OrbStack**: https://orbstack.dev/
- **Supabase Local Dev**: https://supabase.com/docs/guides/local-development
- **n8n Docs**: https://docs.n8n.io/
- **ADK Sessions**: `../insp/adk-docs/docs/sessions/`

