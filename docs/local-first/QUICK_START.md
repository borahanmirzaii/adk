# Quick Start: Local-First Development Setup

Get up and running with OrbStack, Supabase, n8n, and ADK in 10 minutes.

## Prerequisites

- macOS (for OrbStack)
- Node.js 18+
- Python 3.11+
- `uv` package manager

## Step 1: Install OrbStack

```bash
# Using Homebrew
brew install orbstack

# Or download from https://orbstack.dev/
```

Verify:
```bash
docker --version
```

## Step 2: Install Supabase CLI

```bash
npm install -g supabase
```

## Step 3: Initialize Project

```bash
# Create project directory
mkdir adk-local-dev && cd adk-local-dev

# Initialize Supabase
supabase init

# Start Supabase
supabase start
```

Note the output - you'll need:
- API URL: `http://localhost:54321`
- DB URL: `postgresql://postgres:postgres@localhost:54322/postgres`
- Studio: `http://localhost:54323`

## Step 4: Setup Langfuse (Self-Hosted)

```bash
# Create langfuse docker-compose
cat > docker-compose.langfuse.yml << 'EOF'
version: '3.8'

services:
  langfuse-db:
    image: postgres:15
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse
      POSTGRES_DB: langfuse
    volumes:
      - langfuse_db_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3001:3000"
    environment:
      DATABASE_URL: postgresql://langfuse:langfuse@langfuse-db:5432/langfuse
      NEXTAUTH_SECRET: change-this-secret
      NEXTAUTH_URL: http://localhost:3001
      SALT: change-this-salt
    depends_on:
      - langfuse-db

volumes:
  langfuse_db_data:
EOF

# Start Langfuse
docker-compose -f docker-compose.langfuse.yml up -d
```

Access Langfuse at: `http://localhost:3001` (default: admin@langfuse.com / langfuse)

## Step 5: Setup n8n

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
    volumes:
      - ~/.n8n:/home/node/.n8n
EOF

# Start n8n
docker-compose up -d
```

Access n8n at: `http://localhost:5678`

## Step 6: Setup Backend

```bash
# Create backend directory
mkdir -p backend/app/{agents,api/routes,services}

# Initialize with uv
cd backend
uv init --name adk-backend --package

# Install dependencies
uv add fastapi uvicorn[standard] python-dotenv pydantic-settings
uv add google-adk supabase
```

## Step 7: Create Database Schema

```bash
# Create migration
supabase migration new create_adk_tables
```

Edit the migration file:

```sql
-- supabase/migrations/YYYYMMDDHHMMSS_create_adk_tables.sql
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

CREATE INDEX idx_adk_sessions_user_id ON adk_sessions(user_id);
CREATE INDEX idx_adk_sessions_session_id ON adk_sessions(session_id);
```

Apply migration:
```bash
supabase db reset
```

## Step 8: Create Backend Code

### Add Langfuse Integration

```python
# backend/app/services/langfuse_setup.py
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from langfuse.opentelemetry import LangfuseSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import os

def setup_langfuse():
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_host = os.getenv("LANGFUSE_HOST", "http://localhost:3001")
    
    if not langfuse_public_key:
        return
    
    trace.set_tracer_provider(TracerProvider())
    GoogleADKInstrumentor().instrument()
    tracer_provider = trace.get_tracer_provider()
    tracer_provider.add_span_processor(
        BatchSpanProcessor(LangfuseSpanProcessor(
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key,
            host=langfuse_host
        ))
    )
```

### Add LangGraph (Optional)

```bash
cd backend
uv add langgraph langchain-google-genai
```

## Step 9: Create Backend Code

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = "http://localhost:54321"
    SUPABASE_DB_URL: str = "postgresql://postgres:postgres@localhost:54322/postgres"
    GEMINI_API_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

```python
# backend/app/services/supabase_session.py
from google.adk.sessions import DatabaseSessionService
from app.config import settings

session_service = DatabaseSessionService(db_url=settings.SUPABASE_DB_URL)
```

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.supabase_session import session_service
from app.services.langfuse_setup import setup_langfuse
from app.agents.base_agent import root_agent
from google.adk.runners import Runner

# Setup Langfuse observability
setup_langfuse()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runner = Runner(
    app_name="adk-agent",
    agent=root_agent,
    session_service=session_service
)

@app.post("/api/chat")
async def chat(request: dict):
    result = await runner.run_async(
        request["message"],
        session_id=request.get("session_id"),
        user_id=request.get("user_id", "default")
    )
    return {
        "response": result.content,
        "session_id": result.session_id
    }
```

## Step 10: Create .env File

```bash
# backend/.env
GEMINI_API_KEY=your-gemini-api-key
SUPABASE_URL=http://localhost:54321
SUPABASE_DB_URL=postgresql://postgres:postgres@localhost:54322/postgres
LANGFUSE_PUBLIC_KEY=pk-lf-...  # Get from Langfuse dashboard
LANGFUSE_SECRET_KEY=sk-lf-...   # Get from Langfuse dashboard
LANGFUSE_HOST=http://localhost:3001
```

## Step 11: Run Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

## Step 12: Test Setup

```bash
# Test health
curl http://localhost:8000/docs

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Step 13: Setup Frontend with CopilotKit

```bash
# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app

cd frontend
npm install @copilotkit/react-core @copilotkit/react-ui @supabase/supabase-js
```

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

```bash
# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app

cd frontend
npm install @supabase/supabase-js
```

```typescript
// frontend/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  'http://localhost:54321',
  'your-anon-key' // Get from Supabase Studio
)
```

## Step 14: Verify Everything Works

1. **Supabase Studio**: http://localhost:54323
2. **Langfuse**: http://localhost:3001
3. **n8n**: http://localhost:5678
4. **FastAPI Docs**: http://localhost:8000/docs
5. **Next.js**: http://localhost:3000

## Common Issues

### Port Already in Use
```bash
# Find and kill process
lsof -ti:54321 | xargs kill
lsof -ti:5678 | xargs kill
lsof -ti:8000 | xargs kill
```

### Supabase Won't Start
```bash
# Reset Supabase
supabase stop
supabase start
```

### Docker Issues
```bash
# Restart OrbStack
# Or restart Docker containers
docker-compose restart
```

## Next Steps

1. Read `LOCAL_FIRST_SETUP.md` for detailed setup
2. Check `COMPLETE_STACK.md` for Langfuse, LangGraph, and CopilotKit integration
3. Review `INTEGRATION_PATTERNS.md` for advanced patterns
4. Build your first agent workflow
5. Set up n8n automations
6. Monitor agents in Langfuse dashboard

## Resources

- **OrbStack**: https://orbstack.dev/
- **Supabase Docs**: https://supabase.com/docs
- **n8n Docs**: https://docs.n8n.io/
- **ADK Docs**: `../insp/adk-docs/docs/`

