# Setup Guide

Complete setup guide for ADK Dev Environment Manager.

## Prerequisites

### Required Tools

1. **Docker** or **OrbStack** (macOS)
   ```bash
   # macOS with OrbStack
   brew install orbstack
   
   # Or Docker Desktop
   # Download from https://www.docker.com/products/docker-desktop
   ```

2. **Supabase CLI**
   ```bash
   brew install supabase/tap/supabase
   ```

3. **pnpm** (Package Manager)
   ```bash
   curl -fsSL https://get.pnpm.io/install.sh | sh -
   ```

4. **uv** (Python Package Manager)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

5. **just** (Task Runner)
   ```bash
   brew install just
   ```

6. **Python 3.11+**
   ```bash
   # Check version
   python --version
   
   # Install if needed (macOS)
   brew install python@3.11
   ```

7. **Node.js 18+**
   ```bash
   # Check version
   node --version
   
   # Install if needed
   brew install node
   ```

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd adk-devops-assistant
```

### 2. Run Preflight Checks

```bash
just check
```

This will verify:
- All required tools are installed
- Ports are available
- System resources are adequate
- Environment variables are configured

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your API keys
# Required:
# - GOOGLE_API_KEY (get from https://makersuite.google.com/app/apikey)
# Optional:
# - LANGFUSE_PUBLIC_KEY
# - LANGFUSE_SECRET_KEY
```

### 4. Run Setup

```bash
just setup
```

This will:
- Install Supabase CLI (if not installed)
- Install pnpm (if not installed)
- Install Python dependencies (via uv)
- Install frontend dependencies (via pnpm)
- Initialize Supabase

### 5. Start Infrastructure

```bash
just infra-start
```

This starts:
- Supabase (via CLI)
- n8n (via Docker)
- Redis (via Docker)
- Langfuse (via Docker)

### 6. Initialize Database

```bash
# Run migrations
just db-migrate

# Seed with sample data
just db-seed
```

### 7. Start Development Servers

```bash
# Start both backend and frontend
just dev

# Or start separately
just dev-backend  # Backend only
just dev-frontend # Frontend only
```

## Access Services

Once everything is running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Supabase Studio**: http://localhost:54323
- **n8n**: http://localhost:5678 (admin/admin)
- **Langfuse**: http://localhost:3001

## Verification

### Check Infrastructure Status

```bash
just infra-status
```

### Run Health Checks

```bash
# Basic health check
curl http://localhost:8000/api/health/

# Detailed health check
curl http://localhost:8000/api/health/detailed
```

### Test Backend

```bash
just test-backend
```

### Test Frontend

```bash
just test-frontend
```

## Troubleshooting

### Port Conflicts

If ports are already in use:

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or stop all infrastructure
just infra-stop
```

### Supabase Won't Start

```bash
# Reset Supabase
just db-reset

# Or manually
cd infrastructure/supabase
supabase stop
supabase db reset
supabase start
```

### Docker Issues

```bash
# Check Docker status
docker ps

# Restart Docker services
docker-compose restart

# Clean up Docker
just clean-all
docker system prune -a
```

### Frontend Build Fails

```bash
# Clean and reinstall
just clean
cd frontend
pnpm install
pnpm dev
```

### Backend Import Errors

```bash
# Reinstall dependencies
cd backend
uv sync
```

## Next Steps

After setup is complete:

1. Read [API Documentation](API.md)
2. Explore [Agent Documentation](AGENTS.md)
3. Review [Workflows](WORKFLOWS.md)
4. Check [Troubleshooting Guide](TROUBLESHOOTING.md)

