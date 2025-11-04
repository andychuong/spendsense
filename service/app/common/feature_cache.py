"""Feature caching service for Redis-based caching of computed behavioral signals."""

import logging
import json
import uuid
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime, date

logger = logging.getLogger(__name__)

# Try to import Redis client from backend
try:
    from backend.app.core.redis_client import get_redis_client
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    try:
        from app.core.redis_client import get_redis_client
    except ImportError:
        # Fallback: if Redis is not available, return None
        def get_redis_client():
            """Fallback Redis client getter that returns None."""
            logger.warning("Redis client not available - caching disabled")
            return None

# Cache key prefixes for features
CACHE_PREFIX_SUBSCRIPTIONS = "features:subscriptions"
CACHE_PREFIX_SAVINGS = "features:savings"
CACHE_PREFIX_CREDIT = "features:credit"
CACHE_PREFIX_INCOME = "features:income"

# Cache TTLs (in seconds)
FEATURES_TTL = 24 * 60 * 60  # 24 hours


def _serialize_for_json(obj: Any) -> Any:
    """
    Recursively convert UUID objects and dates to strings for JSON serialization.

    Args:
        obj: Object that may contain UUIDs or dates

    Returns:
        Object with UUIDs and dates converted to strings
    """
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_for_json(item) for item in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj


def get_cache_key(prefix: str, user_id: uuid.UUID, window_days: Optional[int] = None) -> str:
    """
    Generate cache key for feature data.

    Args:
        prefix: Cache key prefix (e.g., "features:subscriptions")
        user_id: User ID
        window_days: Optional window size for time-based caching

    Returns:
        Cache key string
    """
    if window_days:
        return f"{prefix}:{user_id}:{window_days}"
    return f"{prefix}:{user_id}"


def cache_feature_signals(prefix: str) -> Callable:
    """
    Decorator to cache feature detection signals.

    Args:
        prefix: Cache key prefix (e.g., "features:subscriptions")

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, user_id: uuid.UUID, *args, **kwargs):
            """
            Wrapper function that implements caching logic.

            Checks cache first, returns cached value if available.
            Otherwise calls function and caches result.
            """
            # Generate cache key
            # Try to get window_days from kwargs or args
            window_days = kwargs.get("window_days")
            if not window_days and args:
                # Check if second positional arg is window_days
                for arg in args:
                    if isinstance(arg, int):
                        window_days = arg
                        break

            # For generate_*_signals methods, we don't use window_days in cache key
            # since they generate both 30d and 180d signals
            cache_key = get_cache_key(prefix, user_id, None)

            # Try to get from cache
            redis_client = get_redis_client()
            if redis_client:
                try:
                    cached_value = redis_client.get(cache_key)
                    if cached_value:
                        logger.debug(f"Cache hit for {cache_key}")
                        return json.loads(cached_value)
                except Exception as e:
                    logger.warning(f"Failed to get cached feature signals: {str(e)}")

            # Call function and cache result
            logger.debug(f"Cache miss for {cache_key}, computing features")
            result = func(self, user_id, *args, **kwargs)

            # Cache result
            if redis_client:
                try:
                    if isinstance(result, dict):
                        result_dict = result
                    else:
                        result_dict = {"data": str(result)}

                    # Serialize UUIDs and dates for JSON
                    serialized_result = _serialize_for_json(result_dict)
                    redis_client.setex(cache_key, FEATURES_TTL, json.dumps(serialized_result))
                    logger.debug(f"Cached feature signals for {cache_key}")
                except Exception as e:
                    logger.warning(f"Failed to cache feature signals: {str(e)}")

            return result

        return wrapper
    return decorator


def get_cached_subscription_signals(
    user_id: uuid.UUID,
    window_days: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get cached subscription signals.

    Args:
        user_id: User ID
        window_days: Optional window size

    Returns:
        Cached subscription signals, or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None

    try:
        cache_key = get_cache_key(CACHE_PREFIX_SUBSCRIPTIONS, user_id, window_days)
        cached_value = redis_client.get(cache_key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached subscription signals: {str(e)}")
        return None


def get_cached_savings_signals(
    user_id: uuid.UUID,
    window_days: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get cached savings signals.

    Args:
        user_id: User ID
        window_days: Optional window size

    Returns:
        Cached savings signals, or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None

    try:
        cache_key = get_cache_key(CACHE_PREFIX_SAVINGS, user_id, window_days)
        cached_value = redis_client.get(cache_key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached savings signals: {str(e)}")
        return None


def get_cached_credit_signals(
    user_id: uuid.UUID,
    window_days: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get cached credit utilization signals.

    Args:
        user_id: User ID
        window_days: Optional window size

    Returns:
        Cached credit signals, or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None

    try:
        cache_key = get_cache_key(CACHE_PREFIX_CREDIT, user_id, window_days)
        cached_value = redis_client.get(cache_key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached credit signals: {str(e)}")
        return None


def get_cached_income_signals(
    user_id: uuid.UUID,
    window_days: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get cached income stability signals.

    Args:
        user_id: User ID
        window_days: Optional window size

    Returns:
        Cached income signals, or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None

    try:
        cache_key = get_cache_key(CACHE_PREFIX_INCOME, user_id, window_days)
        cached_value = redis_client.get(cache_key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached income signals: {str(e)}")
        return None


# ============================================================================
# Cache Invalidation
# ============================================================================

def invalidate_subscription_signals_cache(user_id: uuid.UUID) -> bool:
    """
    Invalidate cached subscription signals for a user.

    Args:
        user_id: User ID

    Returns:
        True if invalidated successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        # Invalidate both 30-day and 180-day caches
        for window_days in [30, 180, None]:
            cache_key = get_cache_key(CACHE_PREFIX_SUBSCRIPTIONS, user_id, window_days)
            redis_client.delete(cache_key)
        logger.info(f"Invalidated subscription signals cache for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate subscription signals cache: {str(e)}")
        return False


def invalidate_savings_signals_cache(user_id: uuid.UUID) -> bool:
    """
    Invalidate cached savings signals for a user.

    Args:
        user_id: User ID

    Returns:
        True if invalidated successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        # Invalidate both 30-day and 180-day caches
        for window_days in [30, 180, None]:
            cache_key = get_cache_key(CACHE_PREFIX_SAVINGS, user_id, window_days)
            redis_client.delete(cache_key)
        logger.info(f"Invalidated savings signals cache for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate savings signals cache: {str(e)}")
        return False


def invalidate_credit_signals_cache(user_id: uuid.UUID) -> bool:
    """
    Invalidate cached credit utilization signals for a user.

    Args:
        user_id: User ID

    Returns:
        True if invalidated successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        # Invalidate both 30-day and 180-day caches
        for window_days in [30, 180, None]:
            cache_key = get_cache_key(CACHE_PREFIX_CREDIT, user_id, window_days)
            redis_client.delete(cache_key)
        logger.info(f"Invalidated credit signals cache for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate credit signals cache: {str(e)}")
        return False


def invalidate_income_signals_cache(user_id: uuid.UUID) -> bool:
    """
    Invalidate cached income stability signals for a user.

    Args:
        user_id: User ID

    Returns:
        True if invalidated successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False

    try:
        # Invalidate both 30-day and 180-day caches
        for window_days in [30, 180, None]:
            cache_key = get_cache_key(CACHE_PREFIX_INCOME, user_id, window_days)
            redis_client.delete(cache_key)
        logger.info(f"Invalidated income signals cache for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate income signals cache: {str(e)}")
        return False


def invalidate_all_feature_signals_cache(user_id: uuid.UUID) -> bool:
    """
    Invalidate all feature signals cache for a user.

    This includes:
    - Subscription signals
    - Savings signals
    - Credit utilization signals
    - Income stability signals

    Args:
        user_id: User ID

    Returns:
        True if all invalidated successfully, False otherwise
    """
    success = True
    success &= invalidate_subscription_signals_cache(user_id)
    success &= invalidate_savings_signals_cache(user_id)
    success &= invalidate_credit_signals_cache(user_id)
    success &= invalidate_income_signals_cache(user_id)
    return success


def invalidate_feature_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., "features:*", "features:subscriptions:*")

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

