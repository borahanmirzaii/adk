# Complete ADK Agent System Implementation Prompt

Copy and paste this entire prompt into Cursor's Composer (Cmd+I) in plan mode to implement the full local-first AI agent development stack.

---

## Mission: Build Production-Ready Local-First AI Agent Development Platform

I need you to implement a complete, production-ready AI agent development platform using the following stack. This is a comprehensive implementation that integrates all components in an intuitive, robust manner with proper error handling, verification, and best practices.

## Tech Stack

### Core Infrastructure
- **OrbStack**: Local container runtime (Docker alternative for macOS)
- **Supabase**: Self-hosted PostgreSQL with real-time subscriptions, auth, and storage
- **n8n**: Self-hosted workflow automation
- **Redis**: Caching and session management

### AI Agent Framework
- **Google ADK (Agent Development Kit)**: Python framework for building AI agents
- **Langfuse**: LLM observability and tracing
- **LangGraph**: Stateful multi-agent workflows
- **CopilotKit**: React-based agent UI with AG-UI protocol

### Application Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 14+ with TypeScript
- **Database**: PostgreSQL (via Supabase)
- **Message Queue**: Redis + Python RQ for async tasks

## Creative Use Case: "DevOps AI Assistant"

Build an intelligent DevOps assistant that demonstrates ALL system capabilities:

### Agent Capabilities
1. **Infrastructure Monitor Agent**
   - Monitors Docker containers, databases, services
   - Uses Supabase for storing metrics history
   - Sends alerts via n8n workflows
   - Real-time dashboard updates via CopilotKit

2. **Code Review Agent**
   - Reviews code commits and pull requests
   - Uses LangGraph for multi-step review workflow
   - Stores review history in Supabase
   - Provides interactive feedback via chat UI

3. **Deployment Orchestrator Agent**
   - Manages deployment pipelines
   - Coordinates with other agents via LangGraph
   - Tracks deployment state in PostgreSQL
   - Sends notifications via n8n

4. **Knowledge Base Agent**
   - RAG-based documentation assistant
   - Vector search using Supabase pgvector
   - Caches frequent queries in Redis
   - Interactive Q&A via CopilotKit

## Implementation Requirements

### Phase 1: Preflight Checks & Environment Setup

**CRITICAL: Before creating ANY files, perform these checks:**

1. **Port Availability Check**
   ```bash
   # Check if required ports are available
   # Supabase: 54322 (PostgreSQL), 54323 (API), 54324 (Auth), 54325 (Storage)
   # n8n: 5678
   # Redis: 6379
   # FastAPI: 8000
   # Next.js: 3000
   # Langfuse: 3001

   # If ports are occupied, automatically assign alternative ports
   # Store port configuration in .env.local
   ```

2. **Dependency Verification**
   ```bash
   # Verify installed tools
   - OrbStack or Docker Desktop
   - Python 3.11+ with uv
   - Node.js 18+ with pnpm
   - PostgreSQL client tools

   # Create installation guide if missing
   ```

3. **Environment Validation**
   ```bash
   # Check system resources
   - Available RAM (min 8GB recommended)
   - Available disk space (min 10GB)
   - Network connectivity

   # Warn user if resources are insufficient
   ```

4. **API Keys Verification**
   ```bash
   # Check for required API keys
   - GOOGLE_API_KEY (for Gemini)
   - LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY

   # Provide clear instructions for obtaining missing keys
   ```

### Phase 2: Project Structure & Architecture

Create a monorepo with the following structure:

```
adk-devops-assistant/
├── .env.example                      # All environment variables template
├── .env.local                        # Auto-generated based on preflight
├── docker-compose.yml               # All services orchestration
├── Makefile                         # Common commands
├── README.md                        # Complete setup guide
├── ARCHITECTURE.md                  # System architecture documentation
│
├── infrastructure/                  # Infrastructure as code
│   ├── supabase/
│   │   ├── config.toml
│   │   ├── seed.sql                # Initial database schema
│   │   └── migrations/
│   ├── n8n/
│   │   ├── workflows/              # Workflow definitions
│   │   └── credentials/
│   └── langfuse/
│       └── config/
│
├── backend/                         # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Configuration management
│   │   ├── dependencies.py         # Dependency injection
│   │   │
│   │   ├── agents/                 # ADK agents
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py      # Base agent class
│   │   │   ├── infrastructure_monitor/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── tools.py
│   │   │   │   └── prompts.py
│   │   │   ├── code_reviewer/
│   │   │   ├── deployment_orchestrator/
│   │   │   └── knowledge_base/
│   │   │
│   │   ├── workflows/              # LangGraph workflows
│   │   │   ├── __init__.py
│   │   │   ├── review_workflow.py
│   │   │   └── deployment_workflow.py
│   │   │
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── agents.py      # Agent endpoints
│   │   │   │   ├── chat.py        # Chat endpoints
│   │   │   │   ├── health.py      # Health checks
│   │   │   │   └── webhooks.py    # n8n webhooks
│   │   │   └── websocket.py       # WebSocket for streaming
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── session_service.py # Supabase session management
│   │   │   ├── cache_service.py   # Redis caching
│   │   │   ├── task_service.py    # RQ task queue
│   │   │   ├── observability.py   # Langfuse integration
│   │   │   └── n8n_service.py     # n8n workflow triggers
│   │   │
│   │   ├── models/                 # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── session.py
│   │   │   └── deployment.py
│   │   │
│   │   ├── middleware/             # Custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Supabase auth
│   │   │   ├── rate_limit.py      # Rate limiting
│   │   │   ├── error_handler.py   # Global error handling
│   │   │   └── logging.py         # Request logging
│   │   │
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       └── helpers.py
│   │
│   ├── tests/                      # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py            # Pytest fixtures
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── scripts/                    # Utility scripts
│   │   ├── preflight_check.py     # Pre-startup validation
│   │   ├── setup_database.py      # Database initialization
│   │   └── seed_data.py           # Sample data seeding
│   │
│   ├── pyproject.toml             # Python dependencies
│   ├── requirements.txt            # Pinned dependencies
│   └── .python-version            # Python version
│
├── frontend/                       # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx             # Root layout with CopilotKit
│   │   ├── page.tsx               # Main dashboard
│   │   ├── agents/
│   │   │   └── page.tsx           # Agent management
│   │   ├── deployments/
│   │   │   └── page.tsx           # Deployment tracking
│   │   └── api/                   # Next.js API routes
│   │
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx  # CopilotKit chat UI
│   │   │   ├── MessageList.tsx
│   │   │   └── AgentSelector.tsx
│   │   ├── dashboard/
│   │   │   ├── MetricsCard.tsx
│   │   │   ├── ServiceStatus.tsx
│   │   │   └── RecentActivity.tsx
│   │   └── shared/
│   │       ├── ErrorBoundary.tsx
│   │       └── LoadingSpinner.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                 # API client
│   │   ├── supabase.ts            # Supabase client
│   │   ├── websocket.ts           # WebSocket client
│   │   └── utils.ts
│   │
│   ├── hooks/
│   │   ├── useAgent.ts
│   │   ├── useRealtimeUpdates.ts  # Supabase real-time
│   │   └── useAuth.ts             # Supabase auth
│   │
│   ├── types/
│   │   └── index.ts               # TypeScript types
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
│
├── shared/                         # Shared code
│   └── types/                     # Shared TypeScript types
│
└── docs/                          # Documentation
    ├── SETUP.md                   # Detailed setup guide
    ├── API.md                     # API documentation
    ├── AGENTS.md                  # Agent documentation
    ├── WORKFLOWS.md               # LangGraph workflows
    └── TROUBLESHOOTING.md         # Common issues
```

### Phase 3: Development Methodology

Follow this sprint-based development process:

#### Sprint 0: Foundation (Days 1-2)
**Goal**: Setup infrastructure and core services

**User Stories**:
- As a developer, I need a working local environment so I can start building
- As a developer, I need all services running so I can test integrations

**Tasks**:
1. Create docker-compose.yml with all services
2. Implement preflight check script
3. Setup Supabase with initial schema
4. Configure n8n with sample workflows
5. Setup Redis for caching
6. Setup Langfuse for observability
7. Create .env.example with all required variables
8. Write comprehensive README.md

**Acceptance Criteria**:
- [ ] All services start without errors
- [ ] Preflight check passes all validations
- [ ] Health check endpoints return 200
- [ ] Database migrations apply successfully
- [ ] Ports are automatically configured if conflicts exist

**Gateway**: All services must be green in health dashboard

---

#### Sprint 1: Backend Core (Days 3-5)
**Goal**: FastAPI backend with auth, error handling, and basic API

**User Stories**:
- As a user, I can authenticate securely
- As a developer, I have proper error handling
- As a system, I can monitor API health

**Tasks**:
1. FastAPI app setup with middleware
2. Supabase authentication integration
3. Rate limiting middleware
4. Global error handler
5. Request logging with Langfuse
6. Health check endpoints
7. Database session service
8. Redis cache service
9. API documentation with OpenAPI
10. Unit tests for core services

**Acceptance Criteria**:
- [ ] Auth flow works end-to-end
- [ ] Rate limiting blocks excessive requests
- [ ] Errors return proper HTTP codes and messages
- [ ] All requests logged to Langfuse
- [ ] Cache hit rate > 80% for repeated queries
- [ ] API docs accessible at /docs
- [ ] Test coverage > 80%

**Gateway**: All integration tests pass

---

#### Sprint 2: Infrastructure Monitor Agent (Days 6-8)
**Goal**: First working agent with tools and observability

**User Stories**:
- As a DevOps engineer, I can monitor service health
- As a system, I can alert on issues
- As a user, I can see real-time metrics

**Tasks**:
1. Base agent class with ADK
2. Infrastructure monitoring tools:
   - Check Docker container status
   - Check database connections
   - Check disk space
   - Check memory usage
3. Supabase integration for metrics storage
4. n8n workflow for alerts
5. Langfuse tracing integration
6. Real-time updates via Supabase subscriptions
7. Agent evaluation suite
8. Integration tests

**Acceptance Criteria**:
- [ ] Agent detects all services correctly
- [ ] Metrics stored in Supabase every 30 seconds
- [ ] Alerts trigger via n8n for critical issues
- [ ] All agent actions traced in Langfuse
- [ ] Real-time dashboard updates in < 1 second
- [ ] Agent evaluation score > 0.9
- [ ] Error recovery works (retry logic)

**Gateway**: Agent runs for 1 hour without failures

---

#### Sprint 3: Code Review Agent with LangGraph (Days 9-11)
**Goal**: Multi-step workflow agent with state management

**User Stories**:
- As a developer, I can get automated code reviews
- As a system, I can coordinate multiple agents
- As a user, I can track review progress

**Tasks**:
1. Code review agent with ADK
2. LangGraph workflow:
   - Fetch code changes
   - Static analysis
   - Security scan
   - Best practices check
   - Generate review report
3. State persistence in Supabase
4. Integration with Infrastructure Monitor
5. Caching for similar code patterns
6. Webhook integration with n8n
7. Progress tracking UI
8. Comprehensive tests

**Acceptance Criteria**:
- [ ] Complete review flow executes successfully
- [ ] State persists across workflow steps
- [ ] Multi-agent coordination works
- [ ] Similar reviews use cache (< 2s response)
- [ ] Review quality score > 0.85
- [ ] Workflow visualizable in LangGraph
- [ ] All workflow steps traced

**Gateway**: Successfully review 10 different code samples

---

#### Sprint 4: Frontend with CopilotKit (Days 12-14)
**Goal**: Interactive UI with real-time agent communication

**User Stories**:
- As a user, I can chat with agents
- As a user, I see real-time updates
- As a user, I have an intuitive dashboard

**Tasks**:
1. Next.js app setup with TypeScript
2. CopilotKit integration:
   - Chat interface
   - AG-UI protocol implementation
   - Agent state synchronization
3. Supabase auth on frontend
4. Real-time subscriptions for updates
5. Dashboard with metrics visualization
6. Agent management UI
7. Error boundaries and loading states
8. E2E tests with Playwright

**Acceptance Criteria**:
- [ ] Chat interface responds in < 500ms
- [ ] Real-time updates appear instantly
- [ ] Auth flow seamless (SSO preferred)
- [ ] Dashboard shows all agents status
- [ ] Error states handled gracefully
- [ ] Mobile responsive design
- [ ] E2E tests cover critical paths
- [ ] Lighthouse score > 90

**Gateway**: Complete user journey without errors

---

#### Sprint 5: Deployment & Knowledge Base (Days 15-17)
**Goal**: Complete all agents and add async processing

**User Stories**:
- As a DevOps engineer, I can manage deployments
- As a user, I can search documentation
- As a system, I handle long-running tasks

**Tasks**:
1. Deployment Orchestrator Agent
2. Knowledge Base Agent with RAG:
   - Supabase pgvector setup
   - Document embedding
   - Semantic search
   - Context-aware responses
3. RQ task queue for async operations
4. n8n workflows for deployment pipelines
5. Vector caching in Redis
6. Multi-agent coordination via LangGraph
7. Performance optimization
8. Load testing

**Acceptance Criteria**:
- [ ] Deployment workflow completes successfully
- [ ] Knowledge base returns relevant results
- [ ] Vector search response < 200ms
- [ ] Async tasks don't block API
- [ ] Can handle 100 concurrent users
- [ ] All agents coordinate without conflicts
- [ ] Cache hit rate > 70% for queries
- [ ] Zero data loss during failures

**Gateway**: System handles production-like load

---

#### Sprint 6: Production Readiness (Days 18-20)
**Goal**: Monitoring, testing, deployment automation

**User Stories**:
- As an operator, I can monitor system health
- As a developer, I have comprehensive tests
- As a team, we can deploy with confidence

**Tasks**:
1. Comprehensive monitoring dashboard
2. Alerting system via n8n
3. Automated backup scripts
4. CI/CD pipeline (GitHub Actions):
   - Linting and formatting
   - Unit tests
   - Integration tests
   - E2E tests
   - Agent evaluation
5. Docker production images
6. Kubernetes manifests (optional)
7. Security audit
8. Performance benchmarks
9. Documentation completion
10. Demo video/tutorial

**Acceptance Criteria**:
- [ ] All tests pass in CI/CD
- [ ] Code coverage > 85%
- [ ] Security scan shows no critical issues
- [ ] Backup/restore tested successfully
- [ ] Production deployment documented
- [ ] All APIs have >99% uptime in 7-day test
- [ ] Documentation covers all features
- [ ] Performance benchmarks documented

**Gateway**: Production deployment succeeds

---

### Phase 4: Code Quality Standards

**Enforce these standards throughout:**

1. **Type Safety**
   - Python: Full type hints, mypy strict mode
   - TypeScript: Strict mode enabled
   - Pydantic models for all data structures

2. **Error Handling**
   - Try-catch blocks for all external calls
   - Custom exception classes
   - Proper HTTP status codes
   - User-friendly error messages
   - Automatic retry with exponential backoff
   - Circuit breaker for failing services

3. **Testing**
   - Unit tests for all business logic
   - Integration tests for API endpoints
   - E2E tests for critical user flows
   - Agent evaluation tests
   - Load testing for performance
   - Minimum 80% code coverage

4. **Logging & Observability**
   - Structured logging (JSON format)
   - All agent actions traced in Langfuse
   - Performance metrics tracked
   - Error tracking with context
   - Request/response logging

5. **Security**
   - Authentication on all endpoints
   - Authorization checks (RBAC)
   - Input validation on all endpoints
   - SQL injection prevention
   - XSS prevention
   - CSRF protection
   - Rate limiting
   - Secret management (never commit secrets)

6. **Code Organization**
   - Single Responsibility Principle
   - Dependency Injection
   - Factory patterns for agents
   - Service layer separation
   - Clear module boundaries
   - Comprehensive docstrings

7. **Performance**
   - Database query optimization (indexes)
   - N+1 query prevention
   - Caching strategy (Redis)
   - Connection pooling
   - Async operations where appropriate
   - Lazy loading

### Phase 5: Verification Checkpoints

**At each gateway, verify:**

1. **Functionality**
   - All features work as specified
   - Edge cases handled
   - Error scenarios tested

2. **Performance**
   - Response times within SLA
   - No memory leaks
   - Efficient database queries

3. **Security**
   - No exposed secrets
   - Auth/authz working
   - Input validation complete

4. **Quality**
   - Tests passing
   - Code coverage met
   - Linting clean
   - Type checking passes

5. **Documentation**
   - README updated
   - API docs current
   - Code comments clear
   - Architecture diagrams updated

### Phase 6: Error Recovery Patterns

**Implement robust error handling:**

```python
# Retry pattern for external services
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)

# Circuit breaker for failing services
@circuit_breaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=ServiceUnavailableError
)

# Graceful degradation
try:
    result = await premium_feature()
except ServiceUnavailableError:
    result = fallback_feature()
    logger.warning("Using fallback due to service unavailability")

# Health check with auto-recovery
async def health_check():
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "langfuse": check_langfuse(),
    }

    failed = [k for k, v in checks.items() if not v]

    if failed:
        logger.error(f"Health check failed: {failed}")
        await trigger_recovery(failed)

    return all(checks.values())
```

### Phase 7: Preflight Check Implementation

**Create comprehensive preflight script:**

```python
# backend/scripts/preflight_check.py

import sys
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class PreflightChecker:
    """Comprehensive preflight checks before starting services"""

    REQUIRED_PORTS = {
        "postgres": 54322,
        "supabase_api": 54323,
        "supabase_auth": 54324,
        "supabase_storage": 54325,
        "n8n": 5678,
        "redis": 6379,
        "fastapi": 8000,
        "nextjs": 3000,
        "langfuse": 3001,
    }

    REQUIRED_ENV_VARS = [
        "GOOGLE_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "DATABASE_URL",
    ]

    def check_port_available(self, port: int) -> bool:
        """Check if port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def find_alternative_port(self, start_port: int) -> int:
        """Find next available port"""
        port = start_port
        while port < start_port + 100:
            if self.check_port_available(port):
                return port
            port += 1
        raise RuntimeError(f"No available ports found after {start_port}")

    def check_all_ports(self) -> Dict[str, int]:
        """Check all required ports and find alternatives if needed"""
        port_mapping = {}
        conflicts = []

        for service, port in self.REQUIRED_PORTS.items():
            if self.check_port_available(port):
                port_mapping[service] = port
            else:
                alternative = self.find_alternative_port(port + 1)
                port_mapping[service] = alternative
                conflicts.append(f"{service}: {port} -> {alternative}")

        if conflicts:
            print(f"⚠️  Port conflicts resolved:")
            for conflict in conflicts:
                print(f"   {conflict}")

        return port_mapping

    def check_dependencies(self) -> List[str]:
        """Check required system dependencies"""
        missing = []

        deps = {
            "docker": ["docker", "--version"],
            "python": ["python", "--version"],
            "node": ["node", "--version"],
            "pnpm": ["pnpm", "--version"],
        }

        for name, cmd in deps.items():
            try:
                subprocess.run(cmd, capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing.append(name)

        return missing

    def check_resources(self) -> Dict[str, bool]:
        """Check system resources"""
        import psutil

        checks = {
            "memory": psutil.virtual_memory().available > 8 * 1024**3,  # 8GB
            "disk": psutil.disk_usage('/').free > 10 * 1024**3,  # 10GB
        }

        return checks

    def generate_env_file(self, port_mapping: Dict[str, int]):
        """Generate .env.local with port configuration"""
        env_content = f"""# Auto-generated by preflight check
# Generated at: {datetime.now().isoformat()}

# Service Ports
POSTGRES_PORT={port_mapping['postgres']}
SUPABASE_API_PORT={port_mapping['supabase_api']}
SUPABASE_AUTH_PORT={port_mapping['supabase_auth']}
SUPABASE_STORAGE_PORT={port_mapping['supabase_storage']}
N8N_PORT={port_mapping['n8n']}
REDIS_PORT={port_mapping['redis']}
FASTAPI_PORT={port_mapping['fastapi']}
NEXTJS_PORT={port_mapping['nextjs']}
LANGFUSE_PORT={port_mapping['langfuse']}

# Service URLs (auto-configured)
SUPABASE_URL=http://localhost:{port_mapping['supabase_api']}
REDIS_URL=redis://localhost:{port_mapping['redis']}
API_URL=http://localhost:{port_mapping['fastapi']}

# TODO: Add your API keys
GOOGLE_API_KEY=your_google_api_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
"""

        Path(".env.local").write_text(env_content)
        print(f"✅ Generated .env.local with port configuration")

    def run_all_checks(self) -> bool:
        """Run all preflight checks"""
        print("🚀 Running preflight checks...\n")

        # Check dependencies
        missing_deps = self.check_dependencies()
        if missing_deps:
            print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
            return False
        print("✅ All dependencies installed")

        # Check resources
        resources = self.check_resources()
        if not all(resources.values()):
            print(f"⚠️  Resource warnings:")
            if not resources['memory']:
                print("   - Low memory (< 8GB available)")
            if not resources['disk']:
                print("   - Low disk space (< 10GB available)")
        else:
            print("✅ System resources adequate")

        # Check ports
        port_mapping = self.check_all_ports()
        print("✅ Port configuration complete")

        # Generate env file
        self.generate_env_file(port_mapping)

        print("\n✅ All preflight checks passed!")
        print("\nNext steps:")
        print("1. Update .env.local with your API keys")
        print("2. Run: make start")

        return True

if __name__ == "__main__":
    checker = PreflightChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
```

### Phase 8: Implementation Instructions

**Step-by-step process:**

1. **Start with Infrastructure**
   - Create docker-compose.yml first
   - Setup Supabase schema
   - Configure n8n workflows
   - Verify all services start

2. **Backend Development**
   - FastAPI core first (auth, middleware)
   - One agent at a time
   - Test after each agent
   - Add integration tests

3. **Frontend Development**
   - Basic Next.js setup
   - CopilotKit integration
   - One page at a time
   - E2E tests for each flow

4. **Integration**
   - Connect frontend to backend
   - Test real-time features
   - Performance optimization
   - Security audit

5. **Production Prep**
   - CI/CD setup
   - Monitoring dashboard
   - Documentation
   - Load testing

### Success Criteria

**The implementation is complete when:**

- [ ] All services start with `make start`
- [ ] Preflight check passes on fresh clone
- [ ] All 4 agents working and traced
- [ ] Frontend chat interface functional
- [ ] Real-time updates working
- [ ] All tests passing (>85% coverage)
- [ ] Documentation complete
- [ ] Can handle 100 concurrent users
- [ ] Zero critical security issues
- [ ] Production deployment successful

### Important Guidelines for Cursor

1. **Ask Before Proceeding**: If any requirement is unclear, ask for clarification
2. **One Sprint at a Time**: Complete each sprint before moving to next
3. **Test as You Go**: Write tests alongside implementation
4. **Document Everything**: Update docs as you build
5. **Show Progress**: After each major task, show what was completed
6. **Handle Errors**: Every external call must have error handling
7. **Follow Standards**: Maintain code quality throughout
8. **Gateway Checks**: Verify acceptance criteria before proceeding

### Additional Context

- **Target Users**: DevOps engineers and developers
- **Performance SLA**: API responses < 500ms, real-time updates < 1s
- **Scalability**: Should handle 1000+ concurrent WebSocket connections
- **Availability**: 99.9% uptime in production
- **Security**: SOC 2 compliance ready

### Questions to Ask Before Starting

1. What level of detail do you want for initial implementation?
2. Should I create all files or focus on specific sprint?
3. Do you want me to use specific UI component libraries?
4. Any preference for testing frameworks beyond pytest/Playwright?
5. Should I include observability dashboard templates?

---

**Ready to begin? Let me know which sprint to start with, and I'll implement it with full code, tests, and documentation.**
