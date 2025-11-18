# Project Setup Guide: FastAPI + Next.js + ADK

Step-by-step guide to set up a complete FastAPI + Next.js + ADK application with CopilotKit and Langfuse.

## Prerequisites

- Python 3.11+
- Node.js 18+
- `uv` package manager
- `npm` or `pnpm`
- Google Cloud account (for Gemini API)
- Langfuse account (optional, for observability)

## Step 1: Initialize Project Structure

```bash
# Create project directory
mkdir adk-agent-app
cd adk-agent-app

# Initialize git
git init
```

## Step 2: Backend Setup (FastAPI)

```bash
# Create backend directory
mkdir -p backend/app/{agents,api/routes,services,middleware}
cd backend

# Initialize with uv
uv init --name adk-backend --package

# Install dependencies
uv add fastapi uvicorn[standard] python-dotenv pydantic-settings
uv add google-adk
uv add langfuse openinference-instrumentation-google-adk
uv add copilotkit-python  # If using CopilotKit backend integration
```

### Create Backend Files

```bash
# backend/app/__init__.py (empty)
touch app/__init__.py

# backend/app/main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import chat, health

app = FastAPI(title="ADK Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/health")
app.include_router(chat.router, prefix="/api/chat")
EOF

# backend/app/config.py
cat > app/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF
```

## Step 3: Frontend Setup (Next.js)

```bash
# Go to project root
cd ..

# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

cd frontend

# Install CopilotKit
npm install @copilotkit/react-core @copilotkit/react-ui
```

### Create Frontend Files

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

## Step 4: Environment Configuration

```bash
# backend/.env
cat > backend/.env << 'EOF'
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
CORS_ORIGINS=["http://localhost:3000"]
EOF

# frontend/.env.local
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

## Step 5: Create Basic Agent

```python
# backend/app/agents/base_agent.py
from google import adk
from app.config import settings

agent = adk.LlmAgent(
    model=adk.models.Gemini(
        model_name=settings.GEMINI_MODEL,
        api_key=settings.GEMINI_API_KEY
    ),
    instructions="You are a helpful AI assistant."
)

root_agent = agent
```

## Step 6: Create API Routes

```python
# backend/app/api/routes/__init__.py
# backend/app/api/routes/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "healthy"}

# backend/app/api/routes/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.agents.base_agent import root_agent

router = APIRouter()
session_service = InMemorySessionService()
runner = Runner(
    app_name="adk-agent",
    agent=root_agent,
    session_service=session_service
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await runner.run_async(
            request.message,
            session_id=request.session_id
        )
        return ChatResponse(
            response=result.content,
            session_id=result.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Step 7: Setup Langfuse (Optional)

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
    
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    GoogleADKInstrumentor().instrument()
    tracer_provider.add_span_processor(
        BatchSpanProcessor(LangfuseSpanProcessor())
    )

# Call in main.py
# from app.services.observability import setup_langfuse
# setup_langfuse()
```

## Step 8: Development Scripts

```json
// package.json (root)
{
  "name": "adk-agent-app",
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && uv run uvicorn app.main:app --reload",
    "dev:frontend": "cd frontend && npm run dev",
    "install:all": "cd backend && uv sync && cd ../frontend && npm install"
  },
  "devDependencies": {
    "concurrently": "^8.2.2"
  }
}
```

## Step 9: Run the Application

```bash
# Install all dependencies
npm run install:all

# Run both servers
npm run dev
```

Backend: http://localhost:8000
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs

## Step 10: Test the Setup

```bash
# Test backend
curl http://localhost:8000/api/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Next Steps

1. **Add More Features**: See `BEST_PRACTICES.md` for advanced patterns
2. **Add Authentication**: Implement JWT or OAuth
3. **Add Database**: For session persistence
4. **Add Tests**: Unit and integration tests
5. **Deploy**: Use Docker and deploy to cloud

## Troubleshooting

### CORS Issues
- Ensure CORS_ORIGINS includes your frontend URL
- Check that credentials are allowed

### ADK Issues
- Verify GEMINI_API_KEY is set correctly
- Check model name is valid

### Langfuse Issues
- Ensure keys are set in .env
- Check network connectivity to Langfuse

## References

- FastAPI Docs: https://fastapi.tiangolo.com/
- Next.js Docs: https://nextjs.org/docs
- ADK Docs: `../insp/adk-docs/docs/`
- CopilotKit: `../integrations/COPILOTKIT_LANGGRAPH_LANGFUSE.md`

