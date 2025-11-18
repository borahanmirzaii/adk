"""Pytest configuration and fixtures"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth import UserContext, Role


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def test_session_id():
    """Test session ID fixture"""
    return "test-session-123"


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.exists = AsyncMock(return_value=False)
    redis_mock.keys = AsyncMock(return_value=[])
    return redis_mock


@pytest.fixture
def test_user():
    """Create a test user context"""
    return UserContext(
        user_id="test-user-123",
        email="test@example.com",
        role=Role.USER,
        metadata={}
    )


@pytest.fixture
def test_admin():
    """Create a test admin user context"""
    return UserContext(
        user_id="test-admin-123",
        email="admin@example.com",
        role=Role.ADMIN,
        metadata={}
    )


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    supabase_mock = Mock()
    supabase_mock.auth.get_user = Mock(return_value=Mock(user=Mock(
        id="test-user-123",
        email="test@example.com",
        user_metadata={"role": "user"}
    )))
    return supabase_mock

