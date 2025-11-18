"""Integration tests for agent endpoints"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_agents():
    """Test listing all agents"""
    response = client.get("/api/agents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_agent_status():
    """Test getting agent status"""
    response = client.get("/api/agents/infrastructure_monitor")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "infrastructure_monitor"
    assert "status" in data

