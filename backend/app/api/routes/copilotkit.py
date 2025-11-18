"""CopilotKit endpoint for AG-UI protocol"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.agents.infrastructure_monitor import InfrastructureMonitorAgent
import json

router = APIRouter()


@router.post("/copilotkit")
async def copilotkit_endpoint(request: Request):
    """Handle CopilotKit requests"""
    body = await request.json()
    
    # Extract message from CopilotKit format
    message = body.get("message", "")
    session_id = body.get("session_id")
    
    # Execute agent
    agent = InfrastructureMonitorAgent()
    response = await agent.execute(message, session_id=session_id)
    
    # Return in CopilotKit format
    return {
        "response": response,
        "session_id": session_id,
    }

