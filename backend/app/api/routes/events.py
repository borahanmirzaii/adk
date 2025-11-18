"""SSE endpoint for streaming agent events to clients"""

import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from starlette.requests import Request

from app.dependencies import get_redis_client
from app.event_bus import get_event_bus
from app.event_bus.schema import Event

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/events/{session_id}")
async def stream_events(session_id: str, request: Request):
    """
    Server-Sent Events (SSE) endpoint for streaming agent events
    
    This endpoint establishes a persistent SSE connection and streams events
    from the Redis Pub/Sub event bus for the specified session.
    
    Args:
        session_id: The session ID to stream events for
        request: FastAPI request object (used to detect client disconnect)
    
    Returns:
        StreamingResponse with text/event-stream content type
    
    Example:
        Connect via EventSource:
        ```javascript
        const es = new EventSource('/api/events/abc123');
        es.onmessage = (event) => console.log(JSON.parse(event.data));
        ```
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    
    # Get event bus instance
    try:
        event_bus = get_event_bus()
    except Exception as e:
        logger.error(f"Failed to get event bus: {e}")
        raise HTTPException(
            status_code=503,
            detail="Event bus unavailable"
        )
    
    # Create stop event to signal when client disconnects
    stop_event = asyncio.Event()
    
    async def event_generator():
        """Generator function that yields SSE-formatted events"""
        try:
            # Stream events from the event bus
            async for event in event_bus.stream_session_events(session_id, stop_event):
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info(f"Client disconnected for session {session_id}")
                    stop_event.set()
                    break
                
                # Yield SSE-formatted event
                yield event.to_sse()
                
        except asyncio.CancelledError:
            logger.info(f"Event stream cancelled for session {session_id}")
            stop_event.set()
        except Exception as e:
            logger.error(f"Error streaming events for session {session_id}: {e}")
            # Send error event before closing
            error_event = Event(
                session_id=session_id,
                type="run_error",
                payload={
                    "error_type": "stream_error",
                    "message": str(e),
                    "agent": "system",
                }
            )
            yield error_event.to_sse()
        finally:
            # Ensure stop event is set
            stop_event.set()
            logger.info(f"Event stream closed for session {session_id}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
