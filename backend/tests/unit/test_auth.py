"""Unit tests for authentication middleware"""

import pytest
from fastapi import HTTPException
from app.middleware.auth import (
    UserContext,
    Role,
    get_current_user,
    require_auth,
    require_role,
    verify_api_key,
    require_api_key,
)
from app.config import settings


class TestUserContext:
    """Tests for UserContext class"""

    def test_user_context_creation(self):
        """Test creating a UserContext"""
        user = UserContext(
            user_id="test-user-123",
            email="test@example.com",
            role=Role.USER,
            metadata={"name": "Test User"}
        )
        assert user.user_id == "test-user-123"
        assert user.email == "test@example.com"
        assert user.role == Role.USER
        assert user.metadata == {"name": "Test User"}

    def test_has_role_user(self):
        """Test role checking for USER role"""
        user = UserContext("user-1", "user@example.com", Role.USER)
        assert user.has_role(Role.USER) is True
        assert user.has_role(Role.ADMIN) is False
        assert user.has_role(Role.AGENT) is False

    def test_has_role_agent(self):
        """Test role checking for AGENT role"""
        user = UserContext("agent-1", "agent@example.com", Role.AGENT)
        assert user.has_role(Role.USER) is True
        assert user.has_role(Role.AGENT) is True
        assert user.has_role(Role.ADMIN) is False

    def test_has_role_admin(self):
        """Test role checking for ADMIN role"""
        user = UserContext("admin-1", "admin@example.com", Role.ADMIN)
        assert user.has_role(Role.USER) is True
        assert user.has_role(Role.AGENT) is True
        assert user.has_role(Role.ADMIN) is True


class TestRequireRole:
    """Tests for require_role dependency factory"""

    @pytest.mark.asyncio
    async def test_require_role_success(self):
        """Test require_role with sufficient permissions"""
        user = UserContext("user-1", "user@example.com", Role.ADMIN)
        role_checker = require_role(Role.USER)
        result = await role_checker(user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_require_role_insufficient(self):
        """Test require_role with insufficient permissions"""
        user = UserContext("user-1", "user@example.com", Role.USER)
        role_checker = require_role(Role.ADMIN)
        
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(user=user)
        
        assert exc_info.value.status_code == 403


class TestVerifyAPIKey:
    """Tests for API key verification"""

    @pytest.mark.asyncio
    async def test_verify_api_key_valid(self, monkeypatch):
        """Test verifying a valid API key"""
        test_key = "test-service-key"
        monkeypatch.setattr(settings, "SUPABASE_SERVICE_KEY", test_key)
        
        from fastapi import Request
        from unittest.mock import Mock
        
        request = Mock(spec=Request)
        request.headers = {"X-API-Key": test_key}
        
        result = await verify_api_key(request)
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_api_key_invalid(self):
        """Test verifying an invalid API key"""
        from fastapi import Request
        from unittest.mock import Mock
        
        request = Mock(spec=Request)
        request.headers = {"X-API-Key": "invalid-key"}
        
        result = await verify_api_key(request)
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_api_key_missing(self):
        """Test verifying when API key is missing"""
        from fastapi import Request
        from unittest.mock import Mock
        
        request = Mock(spec=Request)
        request.headers = {}
        
        result = await verify_api_key(request)
        assert result is False

