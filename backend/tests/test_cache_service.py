"""Unit tests for caching service."""

import pytest
import uuid
import json
from datetime import datetime
from unittest.mock import MagicMock, patch, Mock
from app.core.cache_service import (
    store_session,
    get_session,
    update_session_last_used,
    delete_session,
    get_cached_profile,
    get_cached_recommendations,
    get_cached_signals,
    invalidate_user_profile_cache,
    invalidate_recommendations_cache,
    invalidate_signals_cache,
    invalidate_all_user_caches,
    invalidate_cache_pattern,
)


class TestSessionStorage:
    """Tests for session storage in Redis."""

    @patch("app.core.cache_service.get_redis_client")
    def test_store_session_success(self, mock_get_redis_client):
        """Test successfully storing a session."""
        mock_redis = MagicMock()
        mock_get_redis_client.return_value = mock_redis

        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        role = "user"

        result = store_session(session_id, user_id, role)

        assert result is True
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"session:{session_id}"
        assert call_args[0][1] == 30 * 24 * 60 * 60  # 30 days TTL
        stored_value = json.loads(call_args[0][2])
        assert stored_value["user_id"] == str(user_id)
        assert stored_value["role"] == role
        assert "last_used_at" in stored_value

    @patch("app.core.cache_service.get_redis_client")
    def test_store_session_redis_unavailable(self, mock_get_redis_client):
        """Test storing session when Redis is unavailable."""
        mock_get_redis_client.return_value = None

        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        role = "user"

        result = store_session(session_id, user_id, role)

        assert result is False

    @patch("app.core.cache_service.get_redis_client")
    def test_store_session_redis_error(self, mock_get_redis_client):
        """Test storing session when Redis raises an error."""
        mock_redis = MagicMock()
        mock_redis.setex.side_effect = Exception("Redis error")
        mock_get_redis_client.return_value = mock_redis

        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        role = "user"

        result = store_session(session_id, user_id, role)

        assert result is False

    @patch("app.core.cache_service.get_redis_client")
    def test_get_session_success(self, mock_get_redis_client):
        """Test successfully getting a session."""
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        role = "user"
        last_used_at = datetime.utcnow().isoformat()

        session_data = {
            "user_id": str(user_id),
            "role": role,
            "last_used_at": last_used_at,
        }

        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(session_data)
        mock_get_redis_client.return_value = mock_redis

        result = get_session(session_id)

        assert result is not None
        assert result["user_id"] == str(user_id)
        assert result["role"] == role
        assert result["last_used_at"] == last_used_at
        mock_redis.get.assert_called_once_with(f"session:{session_id}")

    @patch("app.core.cache_service.get_redis_client")
    def test_get_session_not_found(self, mock_get_redis_client):
        """Test getting a session that doesn't exist."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_get_redis_client.return_value = mock_redis

        session_id = uuid.uuid4()
        result = get_session(session_id)

        assert result is None

    @patch("app.core.cache_service.get_redis_client")
    def test_get_session_redis_unavailable(self, mock_get_redis_client):
        """Test getting session when Redis is unavailable."""
        mock_get_redis_client.return_value = None

        session_id = uuid.uuid4()
        result = get_session(session_id)

        assert result is None

    @patch("app.core.cache_service.get_session")
    @patch("app.core.cache_service.store_session")
    def test_update_session_last_used_success(
        self, mock_store_session, mock_get_session
    ):
        """Test successfully updating session last_used_at."""
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        role = "user"

        session_data = {
            "user_id": str(user_id),
            "role": role,
            "last_used_at": datetime.utcnow().isoformat(),
        }
        mock_get_session.return_value = session_data
        mock_store_session.return_value = True

        result = update_session_last_used(session_id)

        assert result is True
        mock_get_session.assert_called_once_with(session_id)
        mock_store_session.assert_called_once()
        call_args = mock_store_session.call_args
        assert call_args[0][0] == session_id
        assert call_args[0][1] == uuid.UUID(str(user_id))
        assert call_args[0][2] == role

    @patch("app.core.cache_service.get_session")
    def test_update_session_last_used_not_found(self, mock_get_session):
        """Test updating session last_used_at when session doesn't exist."""
        mock_get_session.return_value = None

        session_id = uuid.uuid4()
        result = update_session_last_used(session_id)

        assert result is False

    @patch("app.core.cache_service.get_redis_client")
    def test_delete_session_success(self, mock_get_redis_client):
        """Test successfully deleting a session."""
        mock_redis = MagicMock()
        mock_get_redis_client.return_value = mock_redis

        session_id = uuid.uuid4()
        result = delete_session(session_id)

        assert result is True
        mock_redis.delete.assert_called_once_with(f"session:{session_id}")

    @patch("app.core.cache_service.get_redis_client")
    def test_delete_session_redis_unavailable(self, mock_get_redis_client):
        """Test deleting session when Redis is unavailable."""
        mock_get_redis_client.return_value = None

        session_id = uuid.uuid4()
        result = delete_session(session_id)

        assert result is False


class TestAPICaching:
    """Tests for API response caching."""

    @patch("app.core.cache_service.get_redis_client")
    def test_get_cached_profile_success(self, mock_get_redis_client):
        """Test successfully getting cached profile."""
        user_id = uuid.uuid4()
        profile_data = {
            "user_id": str(user_id),
            "email": "test@example.com",
            "role": "user",
        }

        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(profile_data)
        mock_get_redis_client.return_value = mock_redis

        result = get_cached_profile(user_id)

        assert result is not None
        assert result["user_id"] == str(user_id)
        assert result["email"] == "test@example.com"
        mock_redis.get.assert_called_once_with(f"profile:{user_id}")

    @patch("app.core.cache_service.get_redis_client")
    def test_get_cached_profile_not_found(self, mock_get_redis_client):
        """Test getting cached profile when not found."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_get_redis_client.return_value = mock_redis

        user_id = uuid.uuid4()
        result = get_cached_profile(user_id)

        assert result is None

    @patch("app.core.cache_service.get_redis_client")
    def test_get_cached_recommendations_success(self, mock_get_redis_client):
        """Test successfully getting cached recommendations."""
        user_id = uuid.uuid4()
        recommendations_data = {
            "recommendations": [
                {"id": "1", "title": "Test Recommendation"},
            ]
        }

        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(recommendations_data)
        mock_get_redis_client.return_value = mock_redis

        result = get_cached_recommendations(user_id)

        assert result is not None
        assert "recommendations" in result
        mock_redis.get.assert_called_once_with(f"recommendations:{user_id}")

    @patch("app.core.cache_service.get_redis_client")
    def test_get_cached_signals_success(self, mock_get_redis_client):
        """Test successfully getting cached signals."""
        user_id = uuid.uuid4()
        signals_data = {
            "signals_30d": {"subscriptions": 5},
            "signals_180d": {"subscriptions": 10},
        }

        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(signals_data)
        mock_get_redis_client.return_value = mock_redis

        result = get_cached_signals(user_id)

        assert result is not None
        assert "signals_30d" in result
        mock_redis.get.assert_called_once_with(f"signals:{user_id}")


class TestCacheInvalidation:
    """Tests for cache invalidation."""

    @patch("app.core.cache_service.get_redis_client")
    def test_invalidate_user_profile_cache_success(self, mock_get_redis_client):
        """Test successfully invalidating user profile cache."""
        mock_redis = MagicMock()
        mock_get_redis_client.return_value = mock_redis

        user_id = uuid.uuid4()
        result = invalidate_user_profile_cache(user_id)

        assert result is True
        mock_redis.delete.assert_called_once_with(f"profile:{user_id}")

    @patch("app.core.cache_service.get_redis_client")
    def test_invalidate_recommendations_cache_success(self, mock_get_redis_client):
        """Test successfully invalidating recommendations cache."""
        mock_redis = MagicMock()
        mock_get_redis_client.return_value = mock_redis

        user_id = uuid.uuid4()
        result = invalidate_recommendations_cache(user_id)

        assert result is True
        mock_redis.delete.assert_called_once_with(f"recommendations:{user_id}")

    @patch("app.core.cache_service.get_redis_client")
    def test_invalidate_signals_cache_success(self, mock_get_redis_client):
        """Test successfully invalidating signals cache."""
        mock_redis = MagicMock()
        mock_get_redis_client.return_value = mock_redis

        user_id = uuid.uuid4()
        result = invalidate_signals_cache(user_id)

        assert result is True
        mock_redis.delete.assert_called_once_with(f"signals:{user_id}")

    @patch("app.core.cache_service.invalidate_signals_cache")
    @patch("app.core.cache_service.invalidate_recommendations_cache")
    @patch("app.core.cache_service.invalidate_user_profile_cache")
    def test_invalidate_all_user_caches_success(
        self,
        mock_invalidate_profile,
        mock_invalidate_recommendations,
        mock_invalidate_signals,
    ):
        """Test successfully invalidating all user caches."""
        mock_invalidate_profile.return_value = True
        mock_invalidate_recommendations.return_value = True
        mock_invalidate_signals.return_value = True

        user_id = uuid.uuid4()
        result = invalidate_all_user_caches(user_id)

        assert result is True
        mock_invalidate_profile.assert_called_once_with(user_id)
        mock_invalidate_recommendations.assert_called_once_with(user_id)
        mock_invalidate_signals.assert_called_once_with(user_id)

    @patch("app.core.cache_service.get_redis_client")
    def test_invalidate_cache_pattern_success(self, mock_get_redis_client):
        """Test successfully invalidating cache pattern."""
        mock_redis = MagicMock()
        mock_redis.keys.return_value = ["profile:user1", "profile:user2"]
        mock_redis.delete.return_value = 2
        mock_get_redis_client.return_value = mock_redis

        result = invalidate_cache_pattern("profile:*")

        assert result == 2
        mock_redis.keys.assert_called_once_with("profile:*")
        mock_redis.delete.assert_called_once_with("profile:user1", "profile:user2")

    @patch("app.core.cache_service.get_redis_client")
    def test_invalidate_cache_pattern_no_keys(self, mock_get_redis_client):
        """Test invalidating cache pattern when no keys match."""
        mock_redis = MagicMock()
        mock_redis.keys.return_value = []
        mock_get_redis_client.return_value = mock_redis

        result = invalidate_cache_pattern("profile:*")

        assert result == 0
        mock_redis.delete.assert_not_called()

    @patch("app.core.cache_service.get_redis_client")
    def test_invalidate_cache_pattern_redis_unavailable(self, mock_get_redis_client):
        """Test invalidating cache pattern when Redis is unavailable."""
        mock_get_redis_client.return_value = None

        result = invalidate_cache_pattern("profile:*")

        assert result == 0


