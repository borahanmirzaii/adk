"""Agent-related tasks for RQ worker"""

import asyncio
import logging
from typing import Dict, Any, Optional
from app.agents.infrastructure_monitor import InfrastructureMonitorAgent

logger = logging.getLogger(__name__)


def execute_agent_task(
    agent_name: str,
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute an agent task asynchronously (RQ worker function)
    
    Note: RQ tasks must be synchronous, but we run async agent code
    
    Args:
        agent_name: Name of the agent to execute
        message: User message
        session_id: Optional session ID
        user_id: Optional user ID
    
    Returns:
        Dictionary with agent response
    """
    try:
        logger.info(f"Executing agent task: {agent_name} for session {session_id}")
        
        # Route to appropriate agent
        if agent_name == "infrastructure_monitor":
            agent = InfrastructureMonitorAgent()
            # Run async execute in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    agent.execute(message, session_id=session_id, user_id=user_id)
                )
            finally:
                loop.close()
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        return {
            "status": "completed",
            "agent": agent_name,
            "response": response,
            "session_id": session_id,
        }
    except Exception as e:
        logger.error(f"Agent task failed: {e}", exc_info=True)
        raise


def process_long_running_agent_task(
    agent_name: str,
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Process a long-running agent task with progress updates
    
    Args:
        agent_name: Name of the agent to execute
        message: User message
        session_id: Optional session ID
        user_id: Optional user ID
        **kwargs: Additional parameters
    
    Returns:
        Dictionary with task results
    """
    try:
        logger.info(f"Processing long-running agent task: {agent_name}")
        
        # This is a placeholder for long-running tasks
        # In production, you would update job metadata with progress
        # from rq import get_current_job
        # job = get_current_job()
        # job.meta['progress'] = 50
        # job.save_meta()
        
        if agent_name == "infrastructure_monitor":
            agent = InfrastructureMonitorAgent()
            # Run async execute in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    agent.execute(message, session_id=session_id, user_id=user_id)
                )
            finally:
                loop.close()
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        return {
            "status": "completed",
            "agent": agent_name,
            "response": response,
            "session_id": session_id,
        }
    except Exception as e:
        logger.error(f"Long-running agent task failed: {e}", exc_info=True)
        raise

