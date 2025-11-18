# Troubleshooting Guide

Common issues and solutions for ADK Dev Environment Manager.

## Port Conflicts

### Issue: Port already in use

**Symptoms:**
- Error: "Address already in use"
- Service won't start

**Solutions:**

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or stop all infrastructure
just infra-stop

# Check all ports
just check
```

## Supabase Issues

### Issue: Supabase won't start

**Symptoms:**
- `supabase start` fails
- Database connection errors

**Solutions:**

```bash
# Reset Supabase
just db-reset

# Or manually
cd infrastructure/supabase
supabase stop
supabase db reset
supabase start

# Check Supabase status
supabase status
```

### Issue: Database migrations fail

**Solutions:**

```bash
# Reset database
just db-reset

# Push migrations manually
cd infrastructure/supabase
supabase db push

# Check migration status
supabase migration list
```

## Docker Issues

### Issue: Docker out of memory

**Symptoms:**
- Containers crash
- Slow performance

**Solutions:**

```bash
# Check Docker resources
docker system df

# Clean up
just clean-all
docker system prune -a

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory
```

### Issue: Docker containers won't start

**Solutions:**

```bash
# Check container logs
docker-compose logs

# Restart containers
docker-compose restart

# Rebuild containers
docker-compose up -d --build

# Check Docker status
docker ps -a
```

## Frontend Issues

### Issue: Frontend build fails

**Symptoms:**
- `pnpm install` errors
- Build errors
- Module not found

**Solutions:**

```bash
# Clean and reinstall
just clean
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Clear pnpm cache
pnpm store prune

# Check Node version
node --version  # Should be 18+
```

### Issue: Frontend won't connect to backend

**Solutions:**

```bash
# Check backend is running
curl http://localhost:8000/api/health/

# Check CORS settings in backend/app/main.py
# Verify NEXT_PUBLIC_API_URL in .env.local
```

## Backend Issues

### Issue: Import errors

**Symptoms:**
- ModuleNotFoundError
- Import errors

**Solutions:**

```bash
# Reinstall dependencies
cd backend
uv sync

# Check Python version
python --version  # Should be 3.11+

# Verify virtual environment
which python
```

### Issue: Database connection errors

**Solutions:**

```bash
# Check Supabase is running
just infra-status

# Verify DATABASE_URL in .env.local
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: Redis connection errors

**Solutions:**

```bash
# Check Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli ping

# Restart Redis
docker-compose restart redis
```

## Agent Issues

### Issue: Agents won't start

**Symptoms:**
- Agent status shows "error"
- No agent responses

**Solutions:**

```bash
# Check agent logs
just logs-backend

# Verify GOOGLE_API_KEY is set
echo $GOOGLE_API_KEY

# Test agent manually
just agent-monitor
```

### Issue: Langfuse tracing not working

**Solutions:**

```bash
# Check Langfuse is running
curl http://localhost:3001/api/public/health

# Verify LANGFUSE keys in .env.local
# Check Langfuse logs
docker-compose logs langfuse
```

## n8n Issues

### Issue: n8n workflows not triggering

**Solutions:**

```bash
# Check n8n is running
curl http://localhost:5678/healthz

# Verify webhook URL
# Check n8n logs
docker-compose logs n8n

# Access n8n UI
open http://localhost:5678
```

## Environment Variables

### Issue: Missing environment variables

**Symptoms:**
- Configuration errors
- API key errors

**Solutions:**

```bash
# Check .env.local exists
ls -la .env.local

# Copy from template
cp .env.example .env.local

# Verify required variables
cat .env.local | grep GOOGLE_API_KEY

# Reload environment
source .env.local
```

## Performance Issues

### Issue: Slow responses

**Solutions:**

```bash
# Check system resources
just info

# Check service health
curl http://localhost:8000/api/health/detailed

# Check Redis cache
redis-cli INFO stats

# Check database performance
# Use Supabase Studio: http://localhost:54323
```

## Getting Help

If issues persist:

1. Check logs:
   ```bash
   just logs
   just logs-backend
   ```

2. Run diagnostics:
   ```bash
   just check
   just infra-status
   ```

3. Review documentation:
   - [Setup Guide](SETUP.md)
   - [API Documentation](API.md)
   - [Architecture](ARCHITECTURE.md)

4. Check GitHub Issues
5. Contact support

