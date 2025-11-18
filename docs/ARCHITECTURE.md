# Architecture Documentation

System architecture for ADK Dev Environment Manager.

## Overview

ADK Dev Environment Manager is a local-first AI agent development platform built with modern tools and best practices.

## System Architecture

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

## Components

### Backend (FastAPI)

- **Framework**: FastAPI with Python 3.11+
- **Package Manager**: uv
- **Structure**:
  - `app/agents/` - ADK agents
  - `app/workflows/` - LangGraph workflows
  - `app/api/` - API routes
  - `app/services/` - Business logic
  - `app/models/` - Pydantic models
  - `app/middleware/` - Custom middleware

### Frontend (Next.js)

- **Framework**: Next.js 14+ with App Router
- **Package Manager**: pnpm
- **UI Framework**: CopilotKit (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS

### Database (Supabase)

- **PostgreSQL** with pgvector extension
- **Managed via**: Supabase CLI
- **Features**:
  - Real-time subscriptions
  - Row Level Security (RLS)
  - Automatic migrations
  - Studio UI

### Caching (Redis)

- **Purpose**: Session management, rate limiting, caching
- **Deployment**: Docker container
- **Usage**: Backend services, agent state

### Observability (Langfuse)

- **Purpose**: LLM tracing and analytics
- **Deployment**: Docker container
- **Integration**: OpenTelemetry with ADK

### Automation (n8n)

- **Purpose**: Workflow automation, webhooks
- **Deployment**: Official Docker image
- **Features**: Workflow import/export, Supabase integration

## Data Flow

### Agent Execution Flow

```
User Request
    ↓
FastAPI Endpoint
    ↓
Agent Service
    ↓
ADK Agent (with Langfuse tracing)
    ↓
Tools Execution
    ↓
Supabase (Session Storage)
    ↓
Response to User
```

### Real-time Updates Flow

```
Agent Action
    ↓
Supabase Insert/Update
    ↓
Supabase Realtime Trigger
    ↓
Frontend Subscription
    ↓
UI Update
```

## Security

- **Authentication**: Supabase Auth (future)
- **Authorization**: Row Level Security (RLS)
- **Rate Limiting**: Redis-based middleware
- **Input Validation**: Pydantic models
- **Error Handling**: Global error handlers

## Scalability

- **Horizontal Scaling**: Stateless backend design
- **Caching**: Redis for frequently accessed data
- **Database**: Connection pooling, indexes
- **Async Processing**: RQ task queue (future)

## Monitoring

- **Health Checks**: `/api/health/detailed`
- **Logging**: Structured JSON logging
- **Tracing**: Langfuse for agent actions
- **Metrics**: Infrastructure metrics table

## Development Workflow

1. **Local Development**: All services run locally
2. **Testing**: Unit, integration, E2E tests
3. **Code Quality**: Ruff, mypy, ESLint
4. **CI/CD**: GitHub Actions (future)

## Deployment

- **Local**: `just start`
- **Production**: Docker containers, Kubernetes (future)

## Technology Decisions

### Why Supabase CLI?

- Zero manual configuration
- Automatic port management
- Built-in migrations
- Production parity

### Why pnpm?

- 3x faster than npm
- Disk space efficient
- Better monorepo support

### Why Justfile?

- Modern syntax
- Better error handling
- Cross-platform support
- No tab/space issues

### Why CopilotKit?

- Standardized AG-UI protocol
- Pre-built React components
- Real-time state sync
- Human-in-the-loop support

## Future Enhancements

- [ ] Authentication with Supabase Auth
- [ ] WebSocket support for streaming
- [ ] RQ task queue for async operations
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline
- [ ] Performance monitoring dashboard

