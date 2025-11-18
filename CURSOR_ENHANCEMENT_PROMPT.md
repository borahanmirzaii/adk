# Cursor Implementation Plan - Enhancement & Refinement Prompt

## Analysis of Current Plan

### ✅ Strengths
1. **Comprehensive Sprint Structure** - Clear 6-sprint methodology with acceptance criteria
2. **Complete Architecture** - All major components covered (ADK, Supabase, n8n, LangGraph, CopilotKit)
3. **Quality Standards** - Emphasis on testing (>80% coverage), error handling, observability
4. **Professional Methodology** - Gateway checks, user stories, deliverables
5. **Production Focus** - CI/CD, monitoring, security considerations

### ⚠️ Weaknesses & Gaps

#### 1. Infrastructure Setup Missing Practical Details
- No mention of using **official Docker images** (Supabase, n8n)
- Missing **Supabase CLI** installation and usage
- No **pnpm** configuration for frontend
- Missing **Justfile** for modern task running
- Overly complex "from-scratch" approach instead of leveraging official tooling

#### 2. Use Case Not Compelling Enough
- "DevOps Assistant" is too generic and enterprise-focused
- Doesn't show immediate value for individual developers
- Missing clear demo scenario that excites users
- Four agents feel disconnected rather than synergistic

#### 3. Practical Implementation Gaps
- No actual code snippets for critical integrations
- Missing specific ADK patterns and best practices
- No guidance on LangGraph state machine design
- Vague on CopilotKit AG-UI protocol implementation

#### 4. Developer Experience Issues
- 20-day timeline too long for initial prototype
- No "quick win" milestone to maintain momentum
- Missing local development workflow details
- No troubleshooting guide for common issues

#### 5. Real-World Considerations
- No data persistence strategy during development
- Missing environment switching (dev/staging/prod)
- No cost estimation for API usage (Gemini calls)
- Unclear on offline/local-first capabilities

---

## 🚀 Enhanced Implementation Prompt for Cursor

Copy this COMPLETE enhanced prompt to Cursor after reviewing the initial plan:

---

# ENHANCED Implementation Plan: ADK DevOps Assistant

## Critical Enhancements to Original Plan

I've reviewed the initial implementation plan. Before proceeding, incorporate these critical enhancements to make the implementation more practical, efficient, and developer-friendly.

---

## 1. Use Official Docker Images & Tools (HIGHEST PRIORITY)

### Infrastructure Setup Changes

**Instead of manual configuration, use official images and CLI tools:**

#### Supabase Setup
```bash
# Install Supabase CLI (add to preflight check)
brew install supabase/tap/supabase

# Initialize Supabase in project
cd infrastructure/supabase
supabase init

# Start Supabase locally (auto-configures all services)
supabase start

# This gives you:
# - PostgreSQL with pgvector
# - PostgREST API
# - Auth (GoTrue)
# - Storage
# - Realtime subscriptions
# - Studio UI (http://localhost:54323)
```

**Benefits**:
- ✅ Zero manual configuration
- ✅ Automatic port management
- ✅ Built-in migrations system
- ✅ Local Studio UI for debugging
- ✅ Production-parity guaranteed

**Update docker-compose.yml**:
```yaml
# Remove manual Supabase services
# Just use: supabase start

services:
  n8n:
    image: n8nio/n8n:latest  # ← Use official image
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
    volumes:
      - ./infrastructure/n8n:/home/node/.n8n

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3001:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
      - NEXTAUTH_SECRET=your_secret_here
      - NEXTAUTH_URL=http://localhost:3001

volumes:
  redis_data:
```

#### n8n Setup
```bash
# Use official n8n Docker image with volume mounting
# Workflows persist in ./infrastructure/n8n/

# Access n8n at: http://localhost:5678
# Credentials: admin/admin (change in .env)
```

**Benefits**:
- ✅ Official maintained image
- ✅ Automatic updates
- ✅ Workflow import/export ready
- ✅ Pre-built integrations with Supabase

---

## 2. Use pnpm for Frontend (Not npm/yarn)

### Frontend Package Manager

**Update all frontend commands to use pnpm**:

```bash
# Install pnpm (add to preflight check)
curl -fsSL https://get.pnpm.io/install.sh | sh -

# Initialize frontend
cd frontend
pnpm create next-app@latest . --typescript --tailwind --app

# Install dependencies
pnpm add @copilotkit/react-core @copilotkit/react-ui
pnpm add @supabase/supabase-js
pnpm add -D @playwright/test

# Update package.json scripts
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "playwright test",
    "test:e2e": "pnpm test"
  }
}
```

**Benefits**:
- ✅ Faster than npm (3x speed improvement)
- ✅ Disk space efficient (content-addressable storage)
- ✅ Strict dependency resolution
- ✅ Better monorepo support

---

## 3. Use Justfile for Task Running (Not Makefile)

### Modern Task Runner with Better DX

**Install just**:
```bash
# macOS
brew install just

# Verify installation
just --version
```

**Create `justfile` in project root**:

```just
# justfile - Modern task runner for ADK DevOps Assistant

# Load environment variables
set dotenv-load := true

# Default recipe (runs when you type 'just')
default:
    @just --list

# Show all available recipes
help:
    @just --list

# === SETUP COMMANDS ===

# Initial setup (run once)
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "🚀 Setting up development environment..."

    # Run preflight checks
    ./scripts/preflight_check.sh

    # Install Supabase CLI
    if ! command -v supabase &> /dev/null; then
        echo "📦 Installing Supabase CLI..."
        brew install supabase/tap/supabase
    fi

    # Install pnpm
    if ! command -v pnpm &> /dev/null; then
        echo "📦 Installing pnpm..."
        curl -fsSL https://get.pnpm.io/install.sh | sh -
    fi

    # Install Python dependencies
    cd backend && uv sync

    # Install frontend dependencies
    cd ../frontend && pnpm install

    # Initialize Supabase
    cd ../infrastructure/supabase
    if [ ! -f "config.toml" ]; then
        supabase init
    fi

    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Update .env.local with your API keys"
    echo "  2. Run: just start"

# Check system prerequisites
check:
    #!/usr/bin/env bash
    echo "🔍 Running preflight checks..."
    ./scripts/preflight_check.sh

# === INFRASTRUCTURE COMMANDS ===

# Start all infrastructure services
infra-start:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "🏗️  Starting infrastructure..."

    # Start Supabase
    cd infrastructure/supabase
    supabase start

    # Start other services
    cd ../..
    docker-compose up -d

    echo ""
    echo "✅ Infrastructure running!"
    echo ""
    echo "📍 Service URLs:"
    echo "   Supabase Studio: http://localhost:54323"
    echo "   n8n:             http://localhost:5678"
    echo "   Langfuse:        http://localhost:3001"
    echo "   Redis:           localhost:6379"

# Stop all infrastructure services
infra-stop:
    #!/usr/bin/env bash
    echo "🛑 Stopping infrastructure..."

    # Stop Supabase
    cd infrastructure/supabase && supabase stop

    # Stop Docker services
    cd ../.. && docker-compose down

    echo "✅ Infrastructure stopped"

# Restart all infrastructure services
infra-restart:
    just infra-stop
    just infra-start

# Show infrastructure status
infra-status:
    #!/usr/bin/env bash
    echo "📊 Infrastructure Status"
    echo ""

    # Supabase status
    cd infrastructure/supabase
    supabase status || echo "⚠️  Supabase not running"

    # Docker status
    cd ../..
    echo ""
    docker-compose ps

# === DATABASE COMMANDS ===

# Run database migrations
db-migrate:
    #!/usr/bin/env bash
    cd infrastructure/supabase
    supabase db push

# Reset database (WARNING: deletes all data)
db-reset:
    #!/usr/bin/env bash
    echo "⚠️  WARNING: This will delete all data!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd infrastructure/supabase
        supabase db reset
        echo "✅ Database reset complete"
    fi

# Open Supabase Studio
db-studio:
    open http://localhost:54323

# Seed database with sample data
db-seed:
    #!/usr/bin/env bash
    cd backend
    uv run python scripts/seed_data.py

# === DEVELOPMENT COMMANDS ===

# Start backend dev server
dev-backend:
    #!/usr/bin/env bash
    cd backend
    uv run fastapi dev app/main.py --reload

# Start frontend dev server
dev-frontend:
    #!/usr/bin/env bash
    cd frontend
    pnpm dev

# Start both backend and frontend (requires tmux)
dev:
    #!/usr/bin/env bash
    if ! command -v tmux &> /dev/null; then
        echo "❌ tmux not found. Install with: brew install tmux"
        exit 1
    fi

    # Kill existing session if it exists
    tmux kill-session -t adk-dev 2>/dev/null || true

    # Create new session
    tmux new-session -d -s adk-dev -n "backend"
    tmux send-keys -t adk-dev "just dev-backend" C-m

    # Split window for frontend
    tmux split-window -t adk-dev -h
    tmux send-keys -t adk-dev "just dev-frontend" C-m

    # Attach to session
    tmux attach -t adk-dev

# Start everything (infrastructure + dev servers)
start:
    just infra-start
    @echo ""
    @echo "⏳ Waiting 5 seconds for services to initialize..."
    sleep 5
    just dev

# Stop everything
stop:
    @echo "🛑 Stopping all services..."
    -tmux kill-session -t adk-dev 2>/dev/null || true
    just infra-stop
    @echo "✅ All services stopped"

# === TESTING COMMANDS ===

# Run all tests
test:
    just test-backend
    just test-frontend

# Run backend tests
test-backend:
    #!/usr/bin/env bash
    cd backend
    uv run pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run frontend tests
test-frontend:
    #!/usr/bin/env bash
    cd frontend
    pnpm test

# Run e2e tests
test-e2e:
    #!/usr/bin/env bash
    cd frontend
    pnpm exec playwright test

# Run tests in watch mode
test-watch:
    #!/usr/bin/env bash
    cd backend
    uv run pytest-watch tests/

# Open test coverage report
test-coverage:
    #!/usr/bin/env bash
    cd backend
    open htmlcov/index.html

# === CODE QUALITY COMMANDS ===

# Lint all code
lint:
    just lint-backend
    just lint-frontend

# Lint backend code
lint-backend:
    #!/usr/bin/env bash
    cd backend
    uv run ruff check app/
    uv run mypy app/

# Lint frontend code
lint-frontend:
    #!/usr/bin/env bash
    cd frontend
    pnpm lint

# Format all code
format:
    just format-backend
    just format-frontend

# Format backend code
format-backend:
    #!/usr/bin/env bash
    cd backend
    uv run ruff format app/

# Format frontend code
format-frontend:
    #!/usr/bin/env bash
    cd frontend
    pnpm format

# Run type checking
typecheck:
    just typecheck-backend
    just typecheck-frontend

# Type check backend
typecheck-backend:
    #!/usr/bin/env bash
    cd backend
    uv run mypy app/

# Type check frontend
typecheck-frontend:
    #!/usr/bin/env bash
    cd frontend
    pnpm typecheck

# === AGENT COMMANDS ===

# Run infrastructure monitor agent (CLI mode)
agent-monitor:
    #!/usr/bin/env bash
    cd backend
    uv run python -m app.agents.infrastructure_monitor.agent

# Run code reviewer agent (CLI mode)
agent-reviewer:
    #!/usr/bin/env bash
    cd backend
    uv run python -m app.agents.code_reviewer.agent

# Run all agents in monitoring mode
agents-start:
    #!/usr/bin/env bash
    echo "🤖 Starting all agents..."
    cd backend
    uv run python scripts/start_agents.py

# === CLEANUP COMMANDS ===

# Clean all build artifacts
clean:
    #!/usr/bin/env bash
    echo "🧹 Cleaning build artifacts..."

    # Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    # Frontend
    cd frontend
    rm -rf .next node_modules

    # Backend
    cd ../backend
    rm -rf .venv htmlcov .coverage

    echo "✅ Cleanup complete"

# Deep clean (includes Docker volumes)
clean-all: clean
    #!/usr/bin/env bash
    echo "🧹 Deep cleaning (including Docker volumes)..."

    # Stop everything first
    just infra-stop

    # Remove Docker volumes
    docker-compose down -v

    # Remove Supabase data
    cd infrastructure/supabase
    rm -rf .branches .temp

    echo "✅ Deep cleanup complete"

# === LOGS & MONITORING ===

# Show logs from all services
logs:
    docker-compose logs -f

# Show logs from specific service
logs-service service:
    docker-compose logs -f {{service}}

# Show backend logs
logs-backend:
    tail -f backend/logs/app.log

# Show Langfuse traces
traces:
    open http://localhost:3001

# Show n8n workflows
workflows:
    open http://localhost:5678

# === DEPLOYMENT COMMANDS ===

# Build for production
build:
    just build-backend
    just build-frontend

# Build backend
build-backend:
    #!/usr/bin/env bash
    cd backend
    docker build -t adk-backend:latest .

# Build frontend
build-frontend:
    #!/usr/bin/env bash
    cd frontend
    docker build -t adk-frontend:latest .

# Run production containers locally
prod-local:
    docker-compose -f docker-compose.prod.yml up -d

# === UTILITY COMMANDS ===

# Generate API documentation
docs-api:
    #!/usr/bin/env bash
    cd backend
    uv run python scripts/generate_api_docs.py
    open http://localhost:8000/docs

# Create new agent from template
new-agent name:
    #!/usr/bin/env bash
    echo "🤖 Creating new agent: {{name}}"
    cd backend
    uv run python scripts/create_agent.py {{name}}

# Create new workflow from template
new-workflow name:
    #!/usr/bin/env bash
    echo "📊 Creating new workflow: {{name}}"
    cd backend
    uv run python scripts/create_workflow.py {{name}}

# Show system info
info:
    #!/usr/bin/env bash
    echo "🔍 System Information"
    echo ""
    echo "📦 Installed Tools:"
    echo "  Docker:    $(docker --version 2>/dev/null || echo 'not installed')"
    echo "  Supabase:  $(supabase --version 2>/dev/null || echo 'not installed')"
    echo "  pnpm:      $(pnpm --version 2>/dev/null || echo 'not installed')"
    echo "  uv:        $(uv --version 2>/dev/null || echo 'not installed')"
    echo "  Python:    $(python --version 2>/dev/null || echo 'not installed')"
    echo "  Node:      $(node --version 2>/dev/null || echo 'not installed')"
    echo "  just:      $(just --version 2>/dev/null || echo 'not installed')"
    echo ""
    echo "📍 Project Structure:"
    echo "  Root:      $(pwd)"
    echo "  Backend:   $(pwd)/backend"
    echo "  Frontend:  $(pwd)/frontend"
    echo ""
    echo "🌐 Service URLs (when running):"
    echo "  Backend API:      http://localhost:8000"
    echo "  Frontend:         http://localhost:3000"
    echo "  Supabase Studio:  http://localhost:54323"
    echo "  n8n:              http://localhost:5678"
    echo "  Langfuse:         http://localhost:3001"

# === QUICK RECIPES ===

# Quick start (setup + start everything)
quickstart:
    just setup
    just start

# Full reset (clean + setup + start)
reset: clean-all setup start

# CI pipeline (what runs in GitHub Actions)
ci: lint typecheck test

# Pre-commit checks
pre-commit: format lint typecheck test-backend
    @echo "✅ All pre-commit checks passed!"
```

**Benefits of Justfile over Makefile**:
- ✅ Better error handling (bash strict mode)
- ✅ Modern syntax (easier to read/write)
- ✅ Cross-platform support
- ✅ Better variable interpolation
- ✅ Supports shebang recipes (multi-line bash)
- ✅ Environment variable loading built-in
- ✅ No tab vs space issues
- ✅ Better dependency management between recipes

**Example Usage**:
```bash
# Show all commands
just

# Quick start
just quickstart

# Development
just start
just dev
just test

# Database management
just db-migrate
just db-studio

# Code quality
just format
just lint
just test

# Cleanup
just clean
```

---

## 4. STRONGER Use Case: "AI-Powered Dev Environment Manager"

### Replace Generic "DevOps Assistant" with Compelling Real-World Scenario

**New Use Case**: Personal AI assistant that manages YOUR development environment

#### The Story
```
As a developer working on multiple projects, I want an AI assistant that:

1. **Watches my development environment in real-time**
   - Monitors Docker containers, databases, services
   - Detects issues before they become problems
   - Suggests optimizations based on resource usage

2. **Reviews my code as I write it**
   - Real-time code quality feedback
   - Security vulnerability detection
   - Suggests best practices and refactoring

3. **Manages my deployments intelligently**
   - Analyzes git history to suggest deployment strategy
   - Runs pre-deployment checks
   - Coordinates multi-service deployments

4. **Serves as my personal knowledge base**
   - Remembers project decisions and architecture
   - Answers questions about my codebase
   - Suggests solutions based on past work
```

### Concrete Demo Scenario

**"The Monday Morning Scenario"**

```
You open your laptop Monday morning. The AI assistant:

1. ✅ Checks all services (Supabase, Redis, n8n, Langfuse)
2. ✅ Reports: "PostgreSQL disk usage increased 40% over weekend"
3. ✅ Suggests: "Run cleanup script? I found 10,000 old session records"

You start coding a new feature:

4. ✅ Real-time code review in chat: "This function has O(n²) complexity"
5. ✅ Security scan: "Detected SQL injection vulnerability on line 42"
6. ✅ Suggests: "Similar pattern exists in auth.py - want me to refactor both?"

You're ready to deploy:

7. ✅ Pre-flight check: "Found 3 failing tests in deployment pipeline"
8. ✅ Deploys after fixes: "All services green. Deployment took 2m 34s"
9. ✅ Monitors: "Deployment successful. No errors in last 5 minutes"

You ask a question:

10. ✅ "How did we implement caching in the user service?"
11. ✅ Returns: Relevant code snippet + explanation + link to file
```

**This is immediately valuable and demonstrates ALL system capabilities naturally.**

---

## 5. Practical Implementation Priorities

### Phase 1: Quick Win Prototype (Days 1-3)

**Goal**: Working end-to-end demo in 3 days

**Sprint 0.5: Minimal Viable Demo**

1. **Day 1: Infrastructure + First Agent**
   ```bash
   # Setup (automated via Justfile)
   just setup        # Installs Supabase CLI, pnpm, checks ports
   just infra-start  # Starts Supabase, n8n, Redis, Langfuse

   # Build first agent: Infrastructure Monitor
   # - Single tool: check Docker containers
   # - Store status in Supabase every 30s
   # - Display in terminal

   # Success criteria: Agent runs for 10 minutes
   ```

2. **Day 2: Add Chat Interface**
   ```bash
   # Setup Next.js with CopilotKit
   cd frontend && pnpm install

   # Integrate with Infrastructure Monitor
   # - Ask: "What services are running?"
   # - Get: Real-time response from agent

   # Success criteria: Chat works locally
   ```

3. **Day 3: Add LangGraph Workflow**
   ```bash
   # Create simple 2-step workflow
   # Step 1: Check service status
   # Step 2: If unhealthy, suggest fix

   # Success criteria: Workflow executes and shows state
   ```

**After Day 3, you have a WORKING demo to build upon.**

---

### Phase 2: Production-Ready Features (Days 4-10)

**Incremental additions** to the Day 3 prototype:

- Day 4-5: Code Review Agent
- Day 6-7: Deployment Orchestrator
- Day 8-9: Knowledge Base (RAG)
- Day 10: Polish + Testing

---

## 6. Critical Implementation Details (Code Snippets)

### ADK Agent Pattern (base_agent.py)

```python
"""Base agent class with Supabase session, Langfuse tracing, and error handling"""

from google.adk.llm_agents import LLMAgent
from google.adk.models import GenerativeModel
from google.genai import types
from langfuse import Langfuse
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class BaseADKAgent:
    """Base class for all ADK agents with built-in integrations"""

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        tools: list,
        supabase_url: str,
        supabase_key: str,
        langfuse_public_key: str,
        langfuse_secret_key: str,
    ):
        self.agent_name = agent_name
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.langfuse = Langfuse(
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key,
        )

        # Create ADK agent
        self.agent = LLMAgent(
            name=agent_name,
            model=GenerativeModel("gemini-2.0-flash-exp"),
            system_instruction=system_prompt,
            tools=tools,
        )

        logger.info(f"Initialized {agent_name} with {len(tools)} tools")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def execute(self, user_message: str, session_id: str) -> str:
        """
        Execute agent with tracing and session persistence

        Args:
            user_message: User's input
            session_id: Supabase session ID

        Returns:
            Agent's response
        """
        # Start Langfuse trace
        trace = self.langfuse.trace(
            name=f"{self.agent_name}_execution",
            metadata={"session_id": session_id},
        )

        try:
            # Retrieve session from Supabase
            session_data = await self._get_session(session_id)

            # Execute agent
            span = trace.span(name="agent_execution")
            response = await self.agent.async_run(
                user_message,
                session_id=session_id,
            )
            span.end(output=response)

            # Save to session
            await self._save_to_session(session_id, user_message, response)

            # Log metrics
            trace.event(
                name="execution_complete",
                metadata={
                    "message_length": len(user_message),
                    "response_length": len(response),
                }
            )

            return response

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            trace.event(name="execution_failed", metadata={"error": str(e)})
            raise

        finally:
            trace.update(status="success")

    async def _get_session(self, session_id: str) -> dict:
        """Retrieve session from Supabase"""
        response = self.supabase.table("sessions").select("*").eq("id", session_id).execute()
        return response.data[0] if response.data else {}

    async def _save_to_session(self, session_id: str, user_msg: str, agent_response: str):
        """Save interaction to Supabase session"""
        self.supabase.table("session_history").insert({
            "session_id": session_id,
            "user_message": user_msg,
            "agent_response": agent_response,
            "agent_name": self.agent_name,
            "timestamp": "now()",
        }).execute()
```

### LangGraph Workflow Pattern (review_workflow.py)

```python
"""LangGraph workflow for code review with state persistence"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
import operator

class ReviewState(TypedDict):
    """State for code review workflow"""
    code: str
    static_analysis_result: Annotated[list, operator.add]
    security_scan_result: Annotated[list, operator.add]
    best_practices_result: Annotated[list, operator.add]
    final_report: str
    errors: list

async def static_analysis_node(state: ReviewState) -> ReviewState:
    """Run static analysis on code"""
    # Use code_reviewer agent tool
    result = await code_reviewer_agent.run_static_analysis(state["code"])
    state["static_analysis_result"].append(result)
    return state

async def security_scan_node(state: ReviewState) -> ReviewState:
    """Run security scan"""
    result = await code_reviewer_agent.run_security_scan(state["code"])
    state["security_scan_result"].append(result)
    return state

async def best_practices_node(state: ReviewState) -> ReviewState:
    """Check best practices"""
    result = await code_reviewer_agent.check_best_practices(state["code"])
    state["best_practices_result"].append(result)
    return state

async def generate_report_node(state: ReviewState) -> ReviewState:
    """Generate final report"""
    report = await code_reviewer_agent.generate_report(
        static=state["static_analysis_result"],
        security=state["security_scan_result"],
        practices=state["best_practices_result"],
    )
    state["final_report"] = report
    return state

# Build graph
workflow = StateGraph(ReviewState)

workflow.add_node("static_analysis", static_analysis_node)
workflow.add_node("security_scan", security_scan_node)
workflow.add_node("best_practices", best_practices_node)
workflow.add_node("generate_report", generate_report_node)

# Parallel execution of analysis steps
workflow.set_entry_point("static_analysis")
workflow.add_edge("static_analysis", "security_scan")
workflow.add_edge("security_scan", "best_practices")
workflow.add_edge("best_practices", "generate_report")
workflow.add_edge("generate_report", END)

# Compile
review_workflow = workflow.compile()
```

### CopilotKit Integration (ChatInterface.tsx)

```typescript
"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { useSupabaseRealtime } from "@/hooks/useRealtimeUpdates";
import "@copilotkit/react-ui/styles.css";

export default function ChatInterface() {
  const { agentStatus, metrics } = useSupabaseRealtime();

  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="infrastructure_monitor"
    >
      <div className="flex h-screen">
        {/* Sidebar with real-time metrics */}
        <div className="w-64 bg-gray-100 p-4">
          <h2 className="text-lg font-bold mb-4">System Status</h2>
          {agentStatus.map((agent) => (
            <div key={agent.name} className="mb-2">
              <span className={agent.healthy ? "text-green-600" : "text-red-600"}>
                ● {agent.name}
              </span>
            </div>
          ))}
        </div>

        {/* Chat interface */}
        <div className="flex-1">
          <CopilotChat
            labels={{
              title: "Dev Environment Assistant",
              initial: "Hi! I'm monitoring your development environment. Ask me anything!",
            }}
            instructions="You are a helpful AI assistant managing the developer's environment."
          />
        </div>
      </div>
    </CopilotKit>
  );
}
```

---

## 7. Enhanced Preflight Check Script

```bash
#!/bin/bash
# scripts/preflight_check.sh

set -e

echo "🔍 Running preflight checks..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        return 1
    fi
}

# Required tools
MISSING=0
check_command "docker" || MISSING=1
check_command "supabase" || MISSING=1
check_command "pnpm" || MISSING=1
check_command "uv" || MISSING=1
check_command "just" || MISSING=1

if [ $MISSING -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}Missing dependencies. Install with:${NC}"
    echo "  brew install docker supabase/tap/supabase just"
    echo "  curl -fsSL https://get.pnpm.io/install.sh | sh -"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check ports
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠${NC}  Port $1 in use"
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 available"
        return 0
    fi
}

echo ""
echo "Checking ports..."
check_port 54322  # Supabase Postgres
check_port 5678   # n8n
check_port 6379   # Redis
check_port 8000   # FastAPI
check_port 3000   # Next.js
check_port 3001   # Langfuse

# Check API keys
echo ""
echo "Checking environment variables..."
if [ -f .env.local ]; then
    source .env.local
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo -e "${RED}✗${NC} GOOGLE_API_KEY not set in .env.local"
    else
        echo -e "${GREEN}✓${NC} GOOGLE_API_KEY configured"
    fi
else
    echo -e "${YELLOW}⚠${NC}  .env.local not found. Copying from .env.example"
    cp .env.example .env.local
    echo -e "${YELLOW}→${NC} Please update .env.local with your API keys"
fi

echo ""
echo -e "${GREEN}✅ Preflight checks complete!${NC}"
```

---

## 8. Troubleshooting Guide

### Common Issues

**Issue 1: Port conflicts**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>

# Or use just recipe
just infra-stop
```

**Issue 2: Supabase won't start**
```bash
# Reset Supabase
just db-reset

# Or manually
cd infrastructure/supabase
supabase stop
supabase db reset
supabase start
```

**Issue 3: Docker out of memory**
```bash
# Check Docker resources
docker system df

# Clean up
just clean-all
docker system prune -a
```

**Issue 4: Frontend build fails**
```bash
# Clear cache
just clean
cd frontend
pnpm install
pnpm dev
```

**Issue 5: Just command not found**
```bash
# Install just
brew install just

# Verify
just --version
```

---

## 9. Updated Success Criteria

### Quick Win (Day 3)
- [ ] Infrastructure starts with `just start`
- [ ] One agent responds in chat interface
- [ ] Real-time updates visible in UI
- [ ] Langfuse traces visible

### MVP (Day 10)
- [ ] All 4 agents functional
- [ ] LangGraph workflow executes
- [ ] CopilotKit chat fully integrated
- [ ] Real-time metrics dashboard
- [ ] Basic tests passing (>70% coverage)

### Production-Ready (Day 20)
- [ ] Test coverage >85%
- [ ] All services containerized
- [ ] CI/CD pipeline functional
- [ ] Documentation complete
- [ ] Demo video created

---

## 10. Implementation Order (Revised)

### Priority 1: Infrastructure (Day 1)
1. Install just (`brew install just`)
2. Create justfile with all recipes
3. Setup Supabase CLI
4. Create docker-compose.yml with official images
5. Run `just setup`
6. Run `just infra-start`
7. Verify health: `just infra-status`

### Priority 2: First Agent (Day 1-2)
1. Create base_agent.py
2. Infrastructure Monitor agent
3. Single tool: check Docker containers
4. Store in Supabase
5. Test via CLI: `just agent-monitor`

### Priority 3: Chat UI (Day 2-3)
1. Setup Next.js with pnpm
2. Install CopilotKit
3. Connect to backend
4. Real-time Supabase subscription
5. Test in browser: `just dev`

### Priority 4: LangGraph (Day 3-5)
1. Create review workflow
2. Add Code Review agent
3. Test workflow execution
4. Visualize state

### Priority 5: Complete Agents (Day 6-8)
1. Deployment Orchestrator
2. Knowledge Base (RAG)
3. Multi-agent coordination

### Priority 6: Production (Day 9-10)
1. Testing suite: `just test`
2. CI/CD
3. Documentation
4. Demo

---

## Key Questions for Cursor

Before implementing, please confirm:

1. **Which sprint should I start with?**
   - Quick Win Prototype (3 days)?
   - Original Sprint 0 (2 days)?

2. **Use official images and tools as specified?**
   - Supabase CLI instead of manual setup? ✅
   - n8n Docker image instead of custom config? ✅
   - pnpm instead of npm? ✅
   - Justfile instead of Makefile? ✅

3. **Focus on "AI Dev Environment Manager" use case?**
   - More practical than generic DevOps Assistant? ✅

4. **Create comprehensive Justfile first?**
   - This makes development much easier ✅

5. **Include code snippets for critical integrations?**
   - Base agent class pattern ✅
   - LangGraph workflow pattern ✅
   - CopilotKit setup ✅

---

## Summary of Enhancements

✅ **Use official tooling** (Supabase CLI, n8n image, pnpm, just)
✅ **Stronger use case** (AI Dev Environment Manager)
✅ **Quick win prototype** (3-day working demo)
✅ **Practical code patterns** (Base agent, LangGraph, CopilotKit)
✅ **Modern task runner** (Justfile with 40+ recipes)
✅ **Better preflight checks** (Port detection, dependency verification)
✅ **Troubleshooting guide** (Common issues + solutions)
✅ **Revised timeline** (10 days to MVP instead of 20)

---

**Please implement these enhancements before proceeding with the original plan. This will result in a more practical, maintainable, and developer-friendly implementation with modern tooling.**
