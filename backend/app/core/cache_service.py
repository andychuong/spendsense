"""Caching service for Redis-based caching operations."""

import logging
import json
import uuid
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from functools import wraps

from app.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)

# Cache key prefixes
CACHE_PREFIX_SESSION = "session"
CACHE_PREFIX_PROFILE = "profile"
CACHE_PREFIX_RECOMMENDATIONS = "recommendations"
CACHE_PREFIX_SIGNALS = "signals"

# Cache TTLs (in seconds)
SESSION_TTL = 30 * 24 * 60 * 60  # 30 days
PROFILE_TTL = 5 * 60  # 5 minutes
RECOMMENDATIONS_TTL = 60 * 60  # 1 hour
SIGNALS_TTL = 24 * 60 * 60  # 24 hours


# ============================================================================
# Session Storage
# ============================================================================

def store_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str,
    last_used_at: Optional[datetime] = None,
) -> bool:
    """
    Store session in Redis.

    Key: session:{session_id}
    TTL: 30 days
    Value: JSON with user_id, role, last_used_at

    Args:
        session_id: Session ID
        user_id: User ID
        role: User role
        last_used_at: Last used timestamp (defaults to now)

    Returns:
        True if stored successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        key = f"{CACHE_PREFIX_SESSION}:{session_id}"
        value = {
            "user_id": str(user_id),
            "role": role,
            "last_used_at": (last_used_at or datetime.utcnow()).isoformat(),
        }
        redis_client.setex(key, SESSION_TTL, json.dumps(value))
        return True
    except Exception as e:
        logger.error(f"Failed to store session in Redis: {str(e)}")
        return False


def get_session(session_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """
    Get session from Redis.

    Args:
        session_id: Session ID

    Returns:
        Session data as dict, or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None

    try:
        key = f"{CACHE_PREFIX_SESSION}:{session_id}"
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Failed to get session from Redis: {str(e)}")
        return None


def update_session_last_used(session_id: uuid.UUID) -> bool:
    """
    Update session last_used_at timestamp.

    Args:
        session_id: Session ID

    Returns:
        True if updated successfully, False otherwise
    """
    session_data = get_session(session_id)
    if not session_data:
        return False

    try:
        user_id = uuid.UUID(session_data["user_id"])
        role = session_data["role"]
        return store_session(session_id, user_id, role, datetime.utcnow())
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to update session last_used_at: {str(e)}")
        return False


def delete_session(session_id: uuid.UUID) -> bool:
    """
    Delete session from Redis.

    Args:
        session_id: Session ID

    Returns:
        True if deleted successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        key = f"{CACHE_PREFIX_SESSION}:{session_id}"
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to delete session from Redis: {str(e)}")
        return False


# ============================================================================
# API Response Caching
# ============================================================================

def cache_profile_response(func: Callable) -> Callable:
    """
    Decorator to cache user profile responses.

    Cache key: profile:{user_id}
    TTL: 5 minutes
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Try to get user_id from kwargs or args
        user_id = kwargs.get("user_id") or kwargs.get("current_user")
        if hasattr(user_id, "user_id"):
            user_id = user_id.user_id
        elif isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        if not user_id:
            # If we can't get user_id, call function without caching
            return await func(*args, **kwargs)

        # Try to get from cache
        cache_key = f"{CACHE_PREFIX_PROFILE}:{user_id}"
        redis_client = get_redis_client()
        if redis_client:
            try:
                cached_value = redis_client.get(cache_key)
                if cached_value:
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Failed to get cached profile: {str(e)}")

        # Call function and cache result
        result = await func(*args, **kwargs)

        if redis_client:
            try:
                # Convert result to JSON-serializable format
                if hasattr(result, "model_dump"):
                    result_dict = result.model_dump()
                elif hasattr(result, "dict"):
                    result_dict = result.dict()
                elif isinstance(result, dict):
                    result_dict = result
                else:
                    result_dict = {"data": str(result)}

                redis_client.setex(cache_key, PROFILE_TTL, json.dumps(result_dict))
            except Exception as e:
                logger.warning(f"Failed to cache profile response: {str(e)}")

        return result

    return wrapper


def cache_recommendations_response(func: Callable) -> Callable:
    """
    Decorator to cache recommendations responses.

    Cache key: recommendations:{user_id}
    TTL: 1 hour
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Try to get user_id from kwargs or args
        user_id = kwargs.get("user_id") or kwargs.get("current_user")
        if hasattr(user_id, "user_id"):
            user_id = user_id.user_id
        elif isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        if not user_id:
            return await func(*args, **kwargs)

        cache_key = f"{CACHE_PREFIX_RECOMMENDATIONS}:{user_id}"
        redis_client = get_redis_client()
        if redis_client:
            try:
                cached_value = redis_client.get(cache_key)
                if cached_value:
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Failed to get cached recommendations: {str(e)}")

        result = await func(*args, **kwargs)

        if redis_client:
            try:
                if hasattr(result, "model_dump"):
                    result_dict = result.model_dump()
                elif hasattr(result, "dict"):
                    result_dict = result.dict()
                elif isinstance(result, (list, dict)):
                    result_dict = result
                else:
                    result_dict = {"data": str(result)}

                redis_client.setex(cache_key, RECOMMENDATIONS_TTL, json.dumps(result_dict))
            except Exception as e:
                logger.warning(f"Failed to cache recommendations response: {str(e)}")

        return result

    return wrapper


def cache_signals_response(func: Callable) -> Callable:
    """
    Decorator to cache behavioral signals responses.

    Cache key: signals:{user_id}
    TTL: 24 hours
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Try to get user_id from kwargs or args
        user_id = kwargs.get("user_id") or kwargs.get("current_user")
        if hasattr(user_id, "user_id"):
            user_id = user_id.user_id
        elif isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        if not user_id:
            return await func(*args, **kwargs)

        cache_key = f"{CACHE_PREFIX_SIGNALS}:{user_id}"
        redis_client = get_redis_client()
        if redis_client:
            try:
                cached_value = redis_client.get(cache_key)
                if cached_value:
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Failed to get cached signals: {str(e)}")

        result = await func(*args, **kwargs)

        if redis_client:
            try:
                if hasattr(result, "model_dump"):
                    result_dict = result.model_dump()
                elif hasattr(result, "dict"):
                    result_dict = result.dict()
                elif isinstance(result, (list, dict)):
                    result_dict = result
                else:
                    result_dict = {"data": str(result)}

                redis_client.setex(cache_key, SIGNALS_TTL, json.dumps(result_dict))
            except Exception as e:
                logger.warning(f"Failed to cache signals response: {str(e)}")

        return result

    return wrapper


def get_cached_profile(user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """
    Get cached user profile.

    Args:
        user_id: User ID

    Returns:
        Cached profile data, or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None

    try:
        cache_key = f"{CACHE_PREFIX_PROFILE}:{user_id}"
        cached_value = redis_client.get(cache_key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached profile: {str(e)}")
        return None


def get_cached_recommendations(user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """
    Get cached recommendations.

    Args:
        user_id: User ID

    Returns:
        Cached recommendations data, or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None

    try:
        cache_key = f"{CACHE_PREFIX_RECOMMENDATIONS}:{user_id}"
        cached_value = redis_client.get(cache_key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached recommendations: {str(e)}")
        return None


def get_cached_signals(user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """
    Get cached behavioral signals.

    Args:
        user_id: User ID

    Returns:
        Cached signals data, or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None

    try:
        cache_key = f"{CACHE_PREFIX_SIGNALS}:{user_id}"
        cached_value = redis_client.get(cache_key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached signals: {str(e)}")
        return None


# ============================================================================
# Cache Invalidation
# ============================================================================

def invalidate_user_profile_cache(user_id: uuid.UUID) -> bool:
    """
    Invalidate user profile cache.

    Args:
        user_id: User ID

    Returns:
        True if invalidated successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        cache_key = f"{CACHE_PREFIX_PROFILE}:{user_id}"
        redis_client.delete(cache_key)
        logger.info(f"Invalidated profile cache for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate profile cache: {str(e)}")
        return False


def invalidate_recommendations_cache(user_id: uuid.UUID) -> bool:
    """
    Invalidate recommendations cache.

    Args:
        user_id: User ID

    Returns:
        True if invalidated successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        cache_key = f"{CACHE_PREFIX_RECOMMENDATIONS}:{user_id}"
        redis_client.delete(cache_key)
        logger.info(f"Invalidated recommendations cache for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate recommendations cache: {str(e)}")
        return False


def invalidate_signals_cache(user_id: uuid.UUID) -> bool:
    """
    Invalidate behavioral signals cache.

    Args:
        user_id: User ID

    Returns:
        True if invalidated successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        cache_key = f"{CACHE_PREFIX_SIGNALS}:{user_id}"
        redis_client.delete(cache_key)
        logger.info(f"Invalidated signals cache for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate signals cache: {str(e)}")
        return False


def invalidate_all_user_caches(user_id: uuid.UUID) -> bool:
    """
    Invalidate all caches for a user.

    This includes:
    - Profile cache
    - Recommendations cache
    - Signals cache

    Args:
        user_id: User ID

    Returns:
        True if all invalidated successfully, False otherwise
    """
    success = True
    success &= invalidate_user_profile_cache(user_id)
    success &= invalidate_recommendations_cache(user_id)
    success &= invalidate_signals_cache(user_id)
    return success


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., "profile:*", "recommendations:*")

    Returns:
        Number of keys deleted
    """
    redis_client = get_redis_client()
    if not redis_client:
        return 0

    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Failed to invalidate cache pattern: {str(e)}")
        return 0


