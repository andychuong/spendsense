"""Redis connection and client management."""

from typing import Optional
import redis
from redis import Redis
import ssl

from app.config import settings


# Global Redis client instance
_redis_client: Optional[Redis] = None


def get_redis_client() -> Optional[Redis]:
    """
    Get Redis client instance.

    Returns:
        Redis client instance or None if Redis is not available
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        # Parse Redis URL
        redis_url = settings.redis_url

        # Create SSL context if SSL is enabled
        ssl_context = None
        if settings.redis_ssl:
            ssl_context = ssl.create_default_context()
            if settings.redis_ssl_cert_reqs:
                # Map string to ssl.CERT_REQUIRED, ssl.CERT_OPTIONAL, etc.
                cert_reqs_map = {
                    "required": ssl.CERT_REQUIRED,
                    "optional": ssl.CERT_OPTIONAL,
                    "none": ssl.CERT_NONE,
                }
                ssl_context.check_hostname = settings.redis_ssl_cert_reqs != "none"
                ssl_context.verify_mode = cert_reqs_map.get(
                    settings.redis_ssl_cert_reqs.lower(), ssl.CERT_REQUIRED
                )

        # Create Redis client
        _redis_client = redis.from_url(
            redis_url,
            ssl=ssl_context,
            decode_responses=True,  # Automatically decode responses to strings
            socket_connect_timeout=5,
            socket_timeout=5,
        )

        # Test connection
        _redis_client.ping()

        return _redis_client
    except Exception as e:
        # Redis not available, log but don't fail
        print(f"WARNING: Redis connection failed: {e}. Redis features will be disabled.")
        return None


def close_redis_client() -> None:
    """
    Close Redis client connection.
    """
    global _redis_client

    if _redis_client is not None:
        try:
            _redis_client.close()
        except Exception:
            pass
        finally:
            _redis_client = None

