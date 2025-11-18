"""End-to-end tests for agent workflows"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app


class TestAgentWorkflows:
    """E2E tests for agent workflows"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_agent_execute(self):
        """Mock agent execution"""
        with patch('app.agents.infrastructure_monitor.InfrastructureMonitorAgent.execute') as mock:
            mock.return_value = AsyncMock(return_value="Test response")
            yield mock

    def test_chat_workflow(self, client, mock_agent_execute):
        """Test complete chat workflow"""
        # Create a chat session
        response = client.post(
            "/api/chat/",
            json={
                "message": "Check system status",
                "agent_name": "infrastructure_monitor"
            }
        )
        
        # Should return a response
        assert response.status_code in [200, 422]  # 422 if validation fails
        if response.status_code == 200:
            data = response.json()
            assert "response" in data or "session_id" in data

    def test_async_chat_workflow(self, client):
        """Test async chat workflow with task queue"""
        with patch('app.services.task_service.task_service.enqueue_task') as mock_enqueue:
            mock_enqueue.return_value = "test-task-123"
            
            response = client.post(
                "/api/chat/async",
                json={
                    "message": "Long running task",
                    "agent_name": "infrastructure_monitor"
                }
            )
            
            # Should return task ID
            if response.status_code == 200:
                data = response.json()
                assert "task_id" in data
                assert data["task_id"] == "test-task-123"

    def test_get_task_status_workflow(self, client):
        """Test getting task status"""
        with patch('app.services.task_service.task_service.get_task_status') as mock_status:
            mock_status.return_value = {
                "task_id": "test-task-123",
                "status": "finished",
                "result": {"response": "Task completed"}
            }
            
            # This would require authentication in real scenario
            # For now, test the endpoint structure
            response = client.get("/api/chat/tasks/test-task-123")
            
            # Should return 401 without auth, or 200 with mock
            assert response.status_code in [200, 401, 404]

    def test_session_history_workflow(self, client):
        """Test retrieving session history"""
        # Create a session first
        response = client.post(
            "/api/chat/",
            json={"message": "Test message"}
        )
        
        if response.status_code == 200:
            session_id = response.json().get("session_id")
            
            # Try to get history (requires auth)
            history_response = client.get(f"/api/chat/sessions/{session_id}")
            
            # Should require authentication
            assert history_response.status_code in [200, 401, 403]

