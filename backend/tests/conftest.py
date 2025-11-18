"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def test_session_id():
    """Test session ID fixture"""
    return "test-session-123"

