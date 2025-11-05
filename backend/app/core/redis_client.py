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

        # For SSL connections, use rediss:// URL scheme
        # If SSL is enabled but URL doesn't use rediss://, update it
        if settings.redis_ssl and not redis_url.startswith("rediss://"):
            # Replace redis:// with rediss://
            redis_url = redis_url.replace("redis://", "rediss://", 1)

        # Build connection kwargs
        connection_kwargs = {
            "decode_responses": True,  # Automatically decode responses to strings
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }

        # Add SSL configuration if SSL is enabled
        if settings.redis_ssl:
            # Create SSL context if SSL is enabled
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
            
            # Use ssl_cert_reqs instead of ssl parameter
            connection_kwargs["ssl_cert_reqs"] = ssl_context.verify_mode
            connection_kwargs["ssl_check_hostname"] = ssl_context.check_hostname

        # Create Redis client
        _redis_client = redis.from_url(
            redis_url,
            **connection_kwargs
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

