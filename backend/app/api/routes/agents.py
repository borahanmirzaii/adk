"""Agent management endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from app.agents.infrastructure_monitor import InfrastructureMonitorAgent
from app.middleware.auth import require_auth, require_role, UserContext, Role

router = APIRouter()


class AgentStatus(BaseModel):
    """Agent status model"""
    name: str
    status: str
    last_heartbeat: str
    metrics: Dict[str, Any]


@router.get("/")
async def list_agents(
    user: UserContext = Depends(require_auth)
) -> List[Dict[str, str]]:
    """List all available agents (requires authentication)"""
    return [
        {"name": "infrastructure_monitor", "status": "available"},
        {"name": "code_reviewer", "status": "available"},
        {"name": "deployment_orchestrator", "status": "available"},
        {"name": "knowledge_base", "status": "available"},
    ]


@router.get("/{agent_name}")
async def get_agent_status(
    agent_name: str,
    user: UserContext = Depends(require_auth)
) -> AgentStatus:
    """Get status of a specific agent (requires authentication)"""
    # TODO: Implement actual agent status retrieval from database
    return AgentStatus(
        name=agent_name,
        status="running",
        last_heartbeat="2024-01-01T00:00:00Z",
        metrics={},
    )


@router.post("/{agent_name}/execute")
async def execute_agent(
    agent_name: str,
    message: Dict[str, Any],
    user: UserContext = Depends(require_auth)
) -> Dict[str, Any]:
    """Execute an agent with a message (requires authentication)"""
    user_message = message.get("message", "")
    session_id = message.get("session_id")

    # Route to appropriate agent
    if agent_name == "infrastructure_monitor":
        agent = InfrastructureMonitorAgent()
        response = await agent.execute(user_message, session_id=session_id, user_id=user.user_id)
        return {
            "agent": agent_name,
            "response": response,
            "status": "completed",
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_name} not found",
        )


@router.delete("/{agent_name}")
async def delete_agent(
    agent_name: str,
    user: UserContext = Depends(require_role(Role.ADMIN))
) -> Dict[str, str]:
    """Delete an agent (requires admin role)"""
    # TODO: Implement agent deletion
    return {"status": "deleted", "agent": agent_name}

