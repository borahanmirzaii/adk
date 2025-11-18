"""Chat endpoints for agent interactions"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.services.session_service import session_service
from app.services.task_service import task_service
from app.agents.infrastructure_monitor import InfrastructureMonitorAgent
from app.middleware.auth import require_auth, get_optional_user, UserContext, Role
from app.config import settings
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
async def chat(
    request: ChatRequest,
    user: Optional[UserContext] = Depends(get_optional_user)
) -> ChatResponse:
    """Chat with an agent"""
    # Get user ID from auth or use default
    user_id = user.user_id if user else "anonymous"
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = await session_service.get_session(session_id)

    if not session:
        # Create new session
        tenant_id = user.tenant_id if user else None
        await session_service.create_session(
            session_id=session_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )

    # Route to appropriate agent
    agent_name = request.agent_name or "infrastructure_monitor"
    
    if agent_name == "infrastructure_monitor":
        agent = InfrastructureMonitorAgent()
        response_text = await agent.execute(request.message, session_id=session_id, user_id=user_id)
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


@router.post("/async")
async def chat_async(
    request: ChatRequest,
    user: Optional[UserContext] = Depends(get_optional_user)
) -> Dict[str, Any]:
    """Chat with an agent asynchronously (returns task ID)"""
    # Get user ID from auth or use default
    user_id = user.user_id if user else "anonymous"
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = await session_service.get_session(session_id)

    if not session:
        # Create new session
        tenant_id = user.tenant_id if user else None
        await session_service.create_session(
            session_id=session_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )

    # Enqueue task
    agent_name = request.agent_name or "infrastructure_monitor"
    task_id = task_service.enqueue_task(
        "execute_agent_task",
        agent_name=agent_name,
        message=request.message,
        session_id=session_id,
        user_id=user_id
    )
    
    if not task_id:
        raise HTTPException(
            status_code=503,
            detail="Task queue unavailable"
        )
    
    return {
        "task_id": task_id,
        "session_id": session_id,
        "status": "queued",
        "message": "Task queued for processing"
    }


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    user: UserContext = Depends(require_auth)
) -> Dict[str, Any]:
    """Get status of an async task (requires authentication)"""
    status_info = task_service.get_task_status(task_id)
    
    if not status_info:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    return status_info


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    user: UserContext = Depends(require_auth)
) -> Dict[str, str]:
    """Cancel an async task (requires authentication)"""
    cancelled = task_service.cancel_task(task_id)
    
    if not cancelled:
        raise HTTPException(
            status_code=404,
            detail="Task not found or cannot be cancelled"
        )
    
    return {"status": "cancelled", "task_id": task_id}


@router.get("/sessions/{session_id}")
async def get_session_history(
    session_id: str,
    user: UserContext = Depends(require_auth)
) -> Dict[str, Any]:
    """Get chat history for a session (requires authentication)"""
    # Verify user owns this session
    session = await session_service.get_session(session_id)
    if session and session.get("user_id") != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this session"
        )
    
    history = await session_service.get_session_history(session_id)
    return {
        "session_id": session_id,
        "messages": history,
    }

