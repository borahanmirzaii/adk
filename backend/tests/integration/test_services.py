"""Integration tests for services"""

import pytest
from app.services.cache_service import cache_service
from app.services.session_service import session_service


@pytest.mark.asyncio
async def test_cache_service():
    """Test cache service"""
    # Test set and get
    cache_service.set("test_key", {"test": "value"}, ttl=60)
    value = cache_service.get("test_key")
    assert value == {"test": "value"}

    # Test exists
    assert cache_service.exists("test_key") is True

    # Test delete
    cache_service.delete("test_key")
    assert cache_service.exists("test_key") is False


@pytest.mark.asyncio
async def test_session_service():
    """Test session service"""
    session_id = "test-session-123"
    user_id = "test-user"

    # Create session
    session = await session_service.create_session(
        session_id=session_id,
        user_id=user_id,
    )
    assert session["session_id"] == session_id

    # Get session
    retrieved = await session_service.get_session(session_id)
    assert retrieved is not None
    assert retrieved["session_id"] == session_id

    # Add event
    success = await session_service.add_event(
        session_id=session_id,
        event={
            "user_message": "Hello",
            "agent_response": "Hi there!",
            "agent_name": "test_agent",
            "metadata": {},
        },
    )
    assert success is True

    # Get history
    history = await session_service.get_session_history(session_id)
    assert len(history) > 0

