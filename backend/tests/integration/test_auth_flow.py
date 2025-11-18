"""Integration tests for authentication flow"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAuthFlow:
    """Integration tests for authentication"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_unauthenticated_access_to_protected_route(self, client):
        """Test accessing protected route without authentication"""
        response = client.get("/api/agents/")
        assert response.status_code == 401

    def test_authenticated_access_to_protected_route(self, client):
        """Test accessing protected route with authentication"""
        # This test would require a valid JWT token
        # In a real scenario, you'd create a test user and get a token
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/agents/", headers=headers)
        # Should fail with invalid token
        assert response.status_code in [401, 403]

    def test_optional_auth_endpoint(self, client):
        """Test endpoint that works with or without auth"""
        response = client.post(
            "/api/chat/",
            json={"message": "test message"}
        )
        # Should work without auth (returns 200 or 422 for validation)
        assert response.status_code in [200, 422]

    def test_api_key_authentication(self, client, monkeypatch):
        """Test API key authentication for webhooks"""
        test_key = "test-service-key"
        monkeypatch.setattr("app.config.settings.SUPABASE_SERVICE_KEY", test_key)
        
        headers = {"X-API-Key": test_key}
        response = client.post(
            "/api/webhooks/n8n",
            headers=headers,
            json={"event": "test", "data": {}}
        )
        # Should succeed with valid API key
        assert response.status_code == 200

    def test_api_key_authentication_invalid(self, client):
        """Test API key authentication with invalid key"""
        headers = {"X-API-Key": "invalid-key"}
        response = client.post(
            "/api/webhooks/n8n",
            headers=headers,
            json={"event": "test", "data": {}}
        )
        # Should fail with invalid API key
        assert response.status_code == 401

