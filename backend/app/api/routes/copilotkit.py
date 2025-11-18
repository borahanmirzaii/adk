"""CopilotKit endpoint for AG-UI protocol"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from app.agents.infrastructure_monitor import InfrastructureMonitorAgent
from app.middleware.auth import get_optional_user, UserContext
import json

router = APIRouter()


@router.post("/copilotkit")
async def copilotkit_endpoint(
    request: Request,
    user: UserContext = Depends(get_optional_user)
):
    """Handle CopilotKit requests"""
    body = await request.json()
    
    # Extract message from CopilotKit format
    message = body.get("message", "")
    session_id = body.get("session_id")
    
    # Execute agent
    agent = InfrastructureMonitorAgent()
    user_id = user.user_id if user else "anonymous"
    response = await agent.execute(message, session_id=session_id, user_id=user_id)
    
    # Return in CopilotKit format
    return {
        "response": response,
        "session_id": session_id,
    }

