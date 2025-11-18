# Quick Implementation Guides

Fast implementation guides for high-priority architecture enhancements.

## Table of Contents
1. [Redis Caching (15 min)](#redis-caching-15-min)
2. [Rate Limiting (10 min)](#rate-limiting-10-min)
3. [Basic Auth (20 min)](#basic-auth-20-min)
4. [Celery Setup (30 min)](#celery-setup-30-min)
5. [Database Backups (15 min)](#database-backups-15-min)

## Redis Caching (15 min)

### 1. Add Redis to Docker Compose

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - adk-network

volumes:
  redis_data:
```

### 2. Install Dependencies

```bash
cd backend
uv add redis aioredis
```

### 3. Create Cache Service

```python
# backend/app/services/cache.py
import redis.asyncio as redis
import json
import os

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True
        )
    
    async def get(self, key: str):
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: dict, ttl: int = 3600):
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        await self.redis.delete(key)

cache = CacheService()
```

### 4. Use in FastAPI

```python
# backend/app/api/routes/chat.py
from app.services.cache import cache

@router.post("/api/chat")
async def chat(request: ChatRequest):
    # Check cache
    cache_key = f"chat:{request.session_id}:{hash(request.message)}"
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # Process
    result = await runner.run_async(request.message, session_id=request.session_id)
    
    # Cache result
    await cache.set(cache_key, {"response": result.content}, ttl=3600)
    
    return {"response": result.content, "session_id": result.session_id}
```

## Rate Limiting (10 min)

### 1. Install slowapi

```bash
cd backend
uv add slowapi
```

### 2. Setup Limiter

```python
# backend/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379/1")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 3. Apply to Routes

```python
# backend/app/api/routes/chat.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

@router.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    # Your logic
    pass
```

## Basic Auth (20 min)

### 1. Install Supabase Auth

```bash
cd backend
uv add supabase
```

### 2. Create Auth Middleware

```python
# backend/app/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from supabase import create_client
import os

security = HTTPBearer()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

async def verify_token(credentials = Depends(security)):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 3. Protect Routes

```python
# backend/app/api/routes/chat.py
from app.middleware.auth import verify_token

@router.post("/api/chat")
async def chat(request: ChatRequest, user = Depends(verify_token)):
    result = await runner.run_async(
        request.message,
        session_id=request.session_id,
        user_id=user.id
    )
    return {"response": result.content}
```

## Celery Setup (30 min)

### 1. Add Celery to Docker Compose

```yaml
# docker-compose.yml
services:
  celery_worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - adk-network
```

### 2. Install Celery

```bash
cd backend
uv add celery redis
```

### 3. Create Celery App

```python
# backend/app/celery_app.py
from celery import Celery
import os

celery_app = Celery(
    "adk_agent",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

@celery_app.task
def process_agent_task(session_id: str, message: str):
    from app.agents.base_agent import root_agent
    from google.adk.runners import Runner
    
    runner = Runner(app_name="adk-agent", agent=root_agent)
    result = runner.run(message, session_id=session_id)
    return result.content
```

### 4. Use in FastAPI

```python
# backend/app/api/routes/async_chat.py
from app.celery_app import process_agent_task

@router.post("/api/chat/async")
async def async_chat(request: ChatRequest):
    task = process_agent_task.delay(request.session_id, request.message)
    return {"task_id": task.id, "status": "queued"}

@router.get("/api/chat/status/{task_id}")
async def task_status(task_id: str):
    from app.celery_app import celery_app
    task = celery_app.AsyncResult(task_id)
    return {"status": task.state, "result": task.result if task.ready() else None}
```

## Database Backups (15 min)

### 1. Create Backup Script

```bash
# scripts/backup_db.sh
#!/bin/bash
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

pg_dump -h localhost -p 54322 -U postgres -d postgres > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### 2. Make Executable

```bash
chmod +x scripts/backup_db.sh
```

### 3. Schedule with n8n

Create n8n workflow:
- Cron trigger (daily at 2 AM)
- Execute command node: `./scripts/backup_db.sh`
- Store in Supabase Storage or S3

### 4. Or Use Cron

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_db.sh
```

## Environment Variables

Add to `.env`:

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Supabase Auth
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_KEY=your-service-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Testing

### Test Redis

```python
# backend/test_redis.py
from app.services.cache import cache

async def test_cache():
    await cache.set("test", {"data": "value"})
    result = await cache.get("test")
    assert result["data"] == "value"
    print("Redis cache working!")
```

### Test Rate Limiting

```bash
# Make 11 requests quickly
for i in {1..11}; do
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "test"}'
done
# 11th should be rate limited
```

## Next Steps

1. Implement Redis caching
2. Add rate limiting
3. Set up basic auth
4. Configure Celery for async tasks
5. Automate database backups

See `ARCHITECTURE_ENHANCEMENTS.md` for detailed implementations.

