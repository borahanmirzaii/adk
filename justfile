# justfile - Modern task runner for ADK Dev Environment Manager

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

