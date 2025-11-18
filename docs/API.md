# API Documentation

API endpoints for ADK Dev Environment Manager.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, authentication is not required. Future versions will use Supabase Auth.

## Endpoints

### Health Checks

#### GET `/api/health/`

Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "adk-devops-assistant"
}
```

#### GET `/api/health/detailed`

Detailed health check for all services.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "redis": {"status": "healthy"},
    "supabase": {"status": "healthy"},
    "langfuse": {"status": "healthy"},
    "n8n": {"status": "healthy"}
  }
}
```

### Agents

#### GET `/api/agents/`

List all available agents.

**Response:**
```json
[
  {"name": "infrastructure_monitor", "status": "available"},
  {"name": "code_reviewer", "status": "available"},
  {"name": "deployment_orchestrator", "status": "available"},
  {"name": "knowledge_base", "status": "available"}
]
```

#### GET `/api/agents/{agent_name}`

Get status of a specific agent.

**Response:**
```json
{
  "name": "infrastructure_monitor",
  "status": "running",
  "last_heartbeat": "2024-01-01T00:00:00Z",
  "metrics": {}
}
```

#### POST `/api/agents/{agent_name}/execute`

Execute an agent with a message.

**Request:**
```json
{
  "message": "Check service status",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "agent": "infrastructure_monitor",
  "response": "All services are healthy",
  "status": "completed"
}
```

### Chat

#### POST `/api/chat/`

Chat with an agent.

**Request:**
```json
{
  "message": "What services are running?",
  "session_id": "optional-session-id",
  "agent_name": "infrastructure_monitor"
}
```

**Response:**
```json
{
  "response": "Currently running services: Supabase, Redis, n8n, Langfuse",
  "session_id": "session-123",
  "agent_name": "infrastructure_monitor"
}
```

#### GET `/api/chat/sessions/{session_id}`

Get chat history for a session.

**Response:**
```json
{
  "session_id": "session-123",
  "messages": [
    {
      "user_message": "What services are running?",
      "agent_response": "All services are healthy",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Webhooks

#### POST `/api/webhooks/n8n`

Receive webhooks from n8n.

**Request:** (JSON payload from n8n)

**Response:**
```json
{
  "status": "received",
  "message": "Webhook processed"
}
```

#### POST `/api/webhooks/alerts`

Receive alert webhooks.

**Request:**
```json
{
  "event": "service_down",
  "data": {
    "service": "redis",
    "status": "critical"
  }
}
```

**Response:**
```json
{
  "status": "received",
  "message": "Alert processed"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "Validation error",
  "details": [...],
  "path": "/api/chat/"
}
```

### 404 Not Found

```json
{
  "error": "Not found",
  "status_code": 404,
  "path": "/api/agents/invalid"
}
```

### 429 Too Many Requests

```json
{
  "error": "Rate limit exceeded. Please try again later.",
  "status_code": 429
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "An error occurred",
  "path": "/api/chat/"
}
```

## Rate Limiting

Rate limiting is enforced per IP address:
- **Limit**: 60 requests per minute
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

## Examples

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health/

# List agents
curl http://localhost:8000/api/agents/

# Chat with agent
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What services are running?",
    "agent_name": "infrastructure_monitor"
  }'
```

### Using Python

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/chat/",
        json={
            "message": "What services are running?",
            "agent_name": "infrastructure_monitor"
        }
    )
    print(response.json())
```

