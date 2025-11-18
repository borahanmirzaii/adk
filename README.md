# ADK Dev Environment Manager

A production-ready local-first AI agent development platform that serves as your **personal AI assistant for managing development environments**.

## 🎯 Use Case: AI-Powered Dev Environment Manager

**The Story**: As a developer working on multiple projects, you have an AI assistant that:

1. **Watches your development environment in real-time** - Monitors Docker containers, databases, services
2. **Reviews your code as you write it** - Real-time code quality feedback, security detection
3. **Manages deployments intelligently** - Analyzes git history, runs pre-deployment checks
4. **Serves as your personal knowledge base** - Remembers project decisions, answers codebase questions

### Demo Scenario: "The Monday Morning Scenario"

You open your laptop Monday morning. The AI assistant:

1. ✅ Checks all services (Supabase, Redis, n8n, Langfuse)
2. ✅ Reports: "PostgreSQL disk usage increased 40% over weekend"
3. ✅ Suggests: "Run cleanup script? I found 10,000 old session records"

You start coding a new feature:

4. ✅ Real-time code review: "This function has O(n²) complexity"
5. ✅ Security scan: "Detected SQL injection vulnerability on line 42"
6. ✅ Suggests: "Similar pattern exists in auth.py - want me to refactor both?"

You're ready to deploy:

7. ✅ Pre-flight check: "Found 3 failing tests in deployment pipeline"
8. ✅ Deploys after fixes: "All services green. Deployment took 2m 34s"
9. ✅ Monitors: "Deployment successful. No errors in last 5 minutes"

You ask a question:

10. ✅ "How did we implement caching in the user service?"
11. ✅ Returns: Relevant code snippet + explanation + link to file

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Local Development Environment (OrbStack)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Supabase │◄─┤   n8n    │◄─┤ FastAPI  │◄─┤ Langfuse │  │
│  │ (CLI)    │  │(Official)│  │ (ADK)    │  │(Self-host)│  │
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
│            │  (pnpm)      │                                 │
│            └──────────────┘                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- macOS (for OrbStack) or Docker Desktop
- Python 3.11+
- Node.js 18+
- `just` task runner: `brew install just`
- `uv` package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `pnpm`: `curl -fsSL https://get.pnpm.io/install.sh | sh -`

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd adk-devops-assistant
   ```

2. **Run setup**
   ```bash
   just setup
   ```

3. **Configure environment**
   ```bash
   # Copy environment template
   cp .env.example .env.local
   
   # Update .env.local with your API keys:
   # - GOOGLE_API_KEY (required)
   # - LANGFUSE_PUBLIC_KEY (optional)
   # - LANGFUSE_SECRET_KEY (optional)
   ```

4. **Start all services**
   ```bash
   just start
   ```

5. **Access services**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - Supabase Studio: http://localhost:54323
   - n8n: http://localhost:5678
   - Langfuse: http://localhost:3001

## 📋 Available Commands

Use `just` to run commands:

```bash
# Setup
just setup          # Initial setup
just check          # Run preflight checks

# Infrastructure
just infra-start    # Start all infrastructure
just infra-stop     # Stop all infrastructure
just infra-status   # Show infrastructure status

# Development
just dev            # Start backend + frontend
just dev-backend    # Start backend only
just dev-frontend   # Start frontend only
just start          # Start everything (infra + dev)

# Database
just db-migrate     # Run migrations
just db-reset       # Reset database
just db-studio      # Open Supabase Studio
just db-seed        # Seed sample data

# Testing
just test           # Run all tests
just test-backend   # Backend tests
just test-frontend  # Frontend tests
just test-e2e       # E2E tests

# Code Quality
just lint           # Lint all code
just format         # Format all code
just typecheck      # Type checking

# Agents
just agent-monitor  # Run infrastructure monitor
just agent-reviewer # Run code reviewer

# Utilities
just info           # Show system info
just logs           # Show service logs
just traces         # Open Langfuse traces
just workflows      # Open n8n workflows

# Quick Recipes
just quickstart     # Setup + start everything
just reset          # Full reset (clean + setup + start)
just ci             # CI pipeline checks
```

See all commands: `just` or `just help`

## 🏛️ Project Structure

```
adk-devops-assistant/
├── justfile                    # Modern task runner
├── docker-compose.yml         # n8n, Redis, Langfuse
├── scripts/
│   └── preflight_check.sh     # Preflight validation
├── infrastructure/
│   ├── supabase/             # Managed by Supabase CLI
│   ├── n8n/                  # n8n workflows
│   └── langfuse/             # Langfuse config
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── agents/           # ADK agents
│   │   ├── workflows/        # LangGraph workflows
│   │   ├── api/              # API routes
│   │   ├── services/         # Business logic
│   │   └── models/           # Pydantic models
│   └── tests/                # Backend tests
├── frontend/                   # Next.js frontend (pnpm)
│   ├── app/                  # Next.js App Router
│   ├── components/          # React components
│   └── lib/                 # Utilities
└── docs/                      # Documentation
```

## 🧪 Testing

```bash
# Run all tests
just test

# Backend tests with coverage
just test-backend

# Frontend tests
just test-frontend

# E2E tests
just test-e2e

# Open coverage report
just test-coverage
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.11+, uv package manager
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, **pnpm**
- **Database**: PostgreSQL (Supabase CLI), Redis
- **AI Framework**: Google ADK (Python)
- **Orchestration**: LangGraph
- **Observability**: Langfuse (self-hosted)
- **UI Framework**: CopilotKit (React)
- **Automation**: n8n (official Docker image)
- **Task Runner**: **Justfile** (modern alternative to Makefile)
- **Container Runtime**: OrbStack (macOS) / Docker

## 📚 Documentation

- [Setup Guide](docs/SETUP.md)
- [API Documentation](docs/API.md)
- [Agent Documentation](docs/AGENTS.md)
- [Workflows](docs/WORKFLOWS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🐛 Troubleshooting

### Port conflicts
```bash
just infra-stop
# Or manually: lsof -i :8000 && kill -9 <PID>
```

### Supabase won't start
```bash
just db-reset
# Or: cd infrastructure/supabase && supabase db reset
```

### Docker out of memory
```bash
just clean-all
docker system prune -a
```

### Frontend build fails
```bash
just clean
cd frontend && pnpm install
```

### Just command not found
```bash
brew install just
```

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `just ci` to ensure all checks pass
5. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- Google ADK for the agent framework
- Supabase for the database and real-time features
- Langfuse for observability
- CopilotKit for the UI framework
- n8n for workflow automation

