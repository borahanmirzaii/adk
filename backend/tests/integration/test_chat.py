"""Integration tests for chat endpoints"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_endpoint():
    """Test chat endpoint"""
    response = client.post(
        "/api/chat/",
        json={
            "message": "Hello",
            "agent_name": "infrastructure_monitor",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert "agent_name" in data

