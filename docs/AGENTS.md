# Agent Documentation

Documentation for ADK agents in the Dev Environment Manager.

## Overview

The system includes 4 specialized agents:

1. **Infrastructure Monitor** - Monitors development environment
2. **Code Reviewer** - Reviews code quality and security
3. **Deployment Orchestrator** - Manages deployments
4. **Knowledge Base** - RAG-based documentation assistant

## Infrastructure Monitor Agent

### Purpose

Monitors Docker containers, databases, and services in real-time.

### Capabilities

- Check Docker container status
- Monitor database connections
- Check disk space and memory usage
- Store metrics in Supabase
- Trigger alerts via n8n

### Usage

```bash
# Run agent manually
just agent-monitor

# Via API
curl -X POST http://localhost:8000/api/agents/infrastructure_monitor/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "Check all services"}'
```

### Tools

- `check_docker_containers` - List and check Docker containers
- `check_database_connection` - Test database connectivity
- `check_disk_space` - Monitor disk usage
- `check_memory_usage` - Monitor memory usage

## Code Reviewer Agent

### Purpose

Reviews code for quality, security, and best practices.

### Capabilities

- Static analysis
- Security vulnerability detection
- Best practices checking
- Multi-step workflow via LangGraph

### Usage

```bash
# Run agent manually
just agent-reviewer

# Via API
curl -X POST http://localhost:8000/api/agents/code_reviewer/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "Review this code: ..."}'
```

### Workflow

1. Fetch code changes
2. Static analysis
3. Security scan
4. Best practices check
5. Generate review report

## Deployment Orchestrator Agent

### Purpose

Manages deployment pipelines and coordinates multi-service deployments.

### Capabilities

- Analyze git history
- Run pre-deployment checks
- Coordinate multi-service deployments
- Track deployment state

### Usage

```bash
# Via API
curl -X POST http://localhost:8000/api/agents/deployment_orchestrator/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "Deploy service X"}'
```

## Knowledge Base Agent

### Purpose

RAG-based documentation assistant with semantic search.

### Capabilities

- Semantic search using pgvector
- Context-aware responses
- Document embedding
- Vector caching

### Usage

```bash
# Via API
curl -X POST http://localhost:8000/api/agents/knowledge_base/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "How did we implement caching?"}'
```

## Agent Architecture

All agents inherit from `BaseADKAgent` which provides:

- Supabase session management
- Langfuse tracing
- Error handling with retries
- Tool integration

## Agent Status

Check agent status:

```bash
# List all agents
curl http://localhost:8000/api/agents/

# Get specific agent status
curl http://localhost:8000/api/agents/infrastructure_monitor
```

## Creating New Agents

Use the template:

```bash
just new-agent my_agent_name
```

This creates:
- `backend/app/agents/my_agent_name/agent.py`
- `backend/app/agents/my_agent_name/tools.py`
- `backend/app/agents/my_agent_name/prompts.py`

## Best Practices

1. **Use BaseADKAgent** - Inherit from base class
2. **Add Langfuse tracing** - All actions should be traced
3. **Store in Supabase** - Persist agent state
4. **Handle errors** - Use retry logic
5. **Write tests** - Unit and integration tests

