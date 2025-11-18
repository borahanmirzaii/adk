"""Unit tests for cache service"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.cache_service import CacheService


class TestCacheService:
    """Tests for CacheService"""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        redis_mock = AsyncMock()
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock(return_value=True)
        redis_mock.delete = AsyncMock(return_value=1)
        redis_mock.exists = AsyncMock(return_value=False)
        return redis_mock

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create CacheService with mocked Redis"""
        with patch('app.services.cache_service.get_redis_client', return_value=mock_redis):
            return CacheService()

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, cache_service, mock_redis):
        """Test getting a value that doesn't exist"""
        mock_redis.get.return_value = None
        
        result = await cache_service.get("test-key")
        assert result is None
        mock_redis.get.assert_called_once_with("test-key")

    @pytest.mark.asyncio
    async def test_get_cache_hit(self, cache_service, mock_redis):
        """Test getting a cached value"""
        mock_redis.get.return_value = '{"test": "value"}'
        
        result = await cache_service.get("test-key")
        assert result == {"test": "value"}
        mock_redis.get.assert_called_once_with("test-key")

    @pytest.mark.asyncio
    async def test_set_cache(self, cache_service, mock_redis):
        """Test setting a cache value"""
        await cache_service.set("test-key", {"test": "value"}, ttl=3600)
        
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == "test-key"
        assert "test" in call_args[0][1]
        assert call_args[1]["ex"] == 3600

    @pytest.mark.asyncio
    async def test_delete_cache(self, cache_service, mock_redis):
        """Test deleting a cache value"""
        await cache_service.delete("test-key")
        
        mock_redis.delete.assert_called_once_with("test-key")

    @pytest.mark.asyncio
    async def test_exists(self, cache_service, mock_redis):
        """Test checking if a key exists"""
        mock_redis.exists.return_value = True
        
        result = await cache_service.exists("test-key")
        assert result is True
        mock_redis.exists.assert_called_once_with("test-key")

    @pytest.mark.asyncio
    async def test_clear_pattern(self, cache_service, mock_redis):
        """Test clearing cache by pattern"""
        mock_redis.keys = AsyncMock(return_value=["key1", "key2"])
        mock_redis.delete = AsyncMock(return_value=2)
        
        result = await cache_service.clear_pattern("test:*")
        assert result == 2
        mock_redis.keys.assert_called_once_with("test:*")

