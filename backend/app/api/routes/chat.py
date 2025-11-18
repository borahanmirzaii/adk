"""Chat endpoints for agent interactions"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.services.session_service import session_service
from app.agents.infrastructure_monitor import InfrastructureMonitorAgent
import uuid

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: Optional[str] = None
    agent_name: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str
    agent_name: str


@router.post("/")
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat with an agent"""
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = await session_service.get_session(session_id)

    if not session:
        # Create new session
        await session_service.create_session(
            session_id=session_id,
            user_id="default-user",  # TODO: Get from auth
        )

    # Route to appropriate agent
    agent_name = request.agent_name or "infrastructure_monitor"
    
    if agent_name == "infrastructure_monitor":
        agent = InfrastructureMonitorAgent()
        response_text = await agent.execute(request.message, session_id=session_id)
    else:
        # Default echo for unknown agents
        response_text = f"Echo: {request.message}"

    # Save to session history
    await session_service.add_event(
        session_id=session_id,
        event={
            "user_message": request.message,
            "agent_response": response_text,
            "agent_name": request.agent_name or "default",
            "metadata": {},
        },
    )

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        agent_name=request.agent_name or "default",
    )


@router.get("/sessions/{session_id}")
async def get_session_history(session_id: str) -> Dict[str, Any]:
    """Get chat history for a session"""
    history = await session_service.get_session_history(session_id)
    return {
        "session_id": session_id,
        "messages": history,
    }

