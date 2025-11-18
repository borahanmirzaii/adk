"""Agent management endpoints"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.agents.infrastructure_monitor import InfrastructureMonitorAgent

router = APIRouter()


class AgentStatus(BaseModel):
    """Agent status model"""
    name: str
    status: str
    last_heartbeat: str
    metrics: Dict[str, Any]


@router.get("/")
async def list_agents() -> List[Dict[str, str]]:
    """List all available agents"""
    return [
        {"name": "infrastructure_monitor", "status": "available"},
        {"name": "code_reviewer", "status": "available"},
        {"name": "deployment_orchestrator", "status": "available"},
        {"name": "knowledge_base", "status": "available"},
    ]


@router.get("/{agent_name}")
async def get_agent_status(agent_name: str) -> AgentStatus:
    """Get status of a specific agent"""
    # TODO: Implement actual agent status retrieval from database
    return AgentStatus(
        name=agent_name,
        status="running",
        last_heartbeat="2024-01-01T00:00:00Z",
        metrics={},
    )


@router.post("/{agent_name}/execute")
async def execute_agent(agent_name: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an agent with a message"""
    user_message = message.get("message", "")
    session_id = message.get("session_id")

    # Route to appropriate agent
    if agent_name == "infrastructure_monitor":
        agent = InfrastructureMonitorAgent()
        response = await agent.execute(user_message, session_id=session_id)
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

