"""OpenAI client utilities for content generation with retry logic, rate limiting, and caching."""

import logging
import os
import json
import hashlib
import time
from typing import Optional, Dict, Any, List
from functools import wraps

# Try to import OpenAI SDK
try:
    from openai import OpenAI
    from openai import RateLimitError, APIError, APIConnectionError, APITimeoutError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("OpenAI SDK not available - OpenAI features will be disabled")

# Try to import Redis client from backend
try:
    from backend.app.core.redis_client import get_redis_client
except ImportError:
    import sys
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    try:
        from app.core.redis_client import get_redis_client
    except ImportError:
        def get_redis_client():
            """Fallback Redis client getter that returns None."""
            return None

logger = logging.getLogger(__name__)

# Cache configuration
OPENAI_CACHE_TTL = 7 * 24 * 60 * 60  # 7 days in seconds
CACHE_PREFIX = "openai:content"

# Rate limiting configuration
RATE_LIMIT_REQUESTS_PER_MINUTE = 100
RATE_LIMIT_WINDOW = 60  # seconds

# Track rate limiting
_request_timestamps: List[float] = []


class OpenAIClient:
    """OpenAI client with retry logic, rate limiting, and caching."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo-preview",
        fallback_model: str = "gpt-3.5-turbo",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Primary model to use (default: gpt-4-turbo-preview)
            fallback_model: Fallback model if primary fails (default: gpt-3.5-turbo)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries (default: 3)
        """
        if not OPENAI_AVAILABLE:
            self.client = None
            logger.warning("OpenAI SDK not available - OpenAI features disabled")
            return

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.fallback_model = fallback_model
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.api_key:
            logger.warning("OpenAI API key not provided - OpenAI features disabled")
            self.client = None
            return

        try:
            self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)
            logger.info(f"OpenAI client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.client = None

    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.

        Returns:
            True if within limits, False if rate limited
        """
        global _request_timestamps

        # Clean old timestamps (older than 1 minute)
        current_time = time.time()
        _request_timestamps = [
            ts for ts in _request_timestamps
            if current_time - ts < RATE_LIMIT_WINDOW
        ]

        # Check if we're at the limit
        if len(_request_timestamps) >= RATE_LIMIT_REQUESTS_PER_MINUTE:
            logger.warning(f"Rate limit reached: {len(_request_timestamps)} requests in last minute")
            return False

        # Add current request timestamp
        _request_timestamps.append(current_time)
        return True

    def _exponential_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.

        Args:
            attempt: Current retry attempt (1-indexed)

        Returns:
            Delay in seconds
        """
        return min(2 ** attempt, 60)  # Max 60 seconds

    def _get_cache_key(self, persona_id: int, signal_hash: str) -> str:
        """
        Generate cache key for OpenAI content.

        Args:
            persona_id: Persona ID
            signal_hash: Hash of behavioral signals

        Returns:
            Cache key string
        """
        return f"{CACHE_PREFIX}:{persona_id}:{signal_hash}"

    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """
        Get content from cache.

        Args:
            cache_key: Cache key

        Returns:
            Cached content or None
        """
        redis_client = get_redis_client()
        if not redis_client:
            return None

        try:
            cached_value = redis_client.get(cache_key)
            if cached_value:
                logger.debug(f"Cache hit for OpenAI content: {cache_key}")
                return cached_value
            return None
        except Exception as e:
            logger.warning(f"Failed to get cached OpenAI content: {str(e)}")
            return None

    def _save_to_cache(self, cache_key: str, content: str) -> bool:
        """
        Save content to cache.

        Args:
            cache_key: Cache key
            content: Content to cache

        Returns:
            True if saved successfully, False otherwise
        """
        redis_client = get_redis_client()
        if not redis_client:
            return False

        try:
            redis_client.setex(cache_key, OPENAI_CACHE_TTL, content)
            logger.debug(f"Cached OpenAI content: {cache_key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache OpenAI content: {str(e)}")
            return False

    def _hash_signals(self, signals: Dict[str, Any]) -> str:
        """
        Generate hash of behavioral signals for cache key.

        Args:
            signals: Behavioral signals dictionary

        Returns:
            Hash string
        """
        # Create a stable hash from signals
        signals_str = json.dumps(signals, sort_keys=True)
        return hashlib.md5(signals_str.encode()).hexdigest()

    def generate_content(
        self,
        prompt: str,
        persona_id: int,
        signals: Dict[str, Any],
        use_cache: bool = True,
    ) -> Optional[str]:
        """
        Generate content using OpenAI API with caching and retry logic.

        Args:
            prompt: Prompt for content generation
            persona_id: Persona ID (for cache key)
            signals: Behavioral signals (for cache key)
            use_cache: Whether to use cache (default: True)

        Returns:
            Generated content or None if generation fails
        """
        if not self.client:
            logger.warning("OpenAI client not available - skipping content generation")
            return None

        # Check rate limit
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded - skipping OpenAI request")
            return None

        # Generate cache key
        signal_hash = self._hash_signals(signals)
        cache_key = self._get_cache_key(persona_id, signal_hash)

        # Try cache first
        if use_cache:
            cached_content = self._get_from_cache(cache_key)
            if cached_content:
                return cached_content

        # Generate content with retry logic
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Generating content with OpenAI (attempt {attempt}/{self.max_retries})")

                # Try primary model first
                model_to_use = self.model if attempt == 1 else self.fallback_model

                response = self.client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": "You are a helpful financial advisor assistant. Provide clear, educational, and empowering financial advice."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )

                content = response.choices[0].message.content.strip()

                # Cache the result
                if use_cache:
                    self._save_to_cache(cache_key, content)

                logger.info(f"Successfully generated content using {model_to_use}")
                return content

            except RateLimitError as e:
                logger.warning(f"Rate limit error (attempt {attempt}): {str(e)}")
                last_error = e
                if attempt < self.max_retries:
                    delay = self._exponential_backoff(attempt)
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                else:
                    logger.error("Rate limit exceeded after all retries")

            except (APIConnectionError, APITimeoutError) as e:
                logger.warning(f"Connection/timeout error (attempt {attempt}): {str(e)}")
                last_error = e
                if attempt < self.max_retries:
                    delay = self._exponential_backoff(attempt)
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                else:
                    logger.error("Connection/timeout error after all retries")

            except APIError as e:
                logger.error(f"OpenAI API error (attempt {attempt}): {str(e)}")
                last_error = e
                # Don't retry on API errors (e.g., invalid request, authentication)
                break

            except Exception as e:
                logger.error(f"Unexpected error generating content (attempt {attempt}): {str(e)}")
                last_error = e
                if attempt < self.max_retries:
                    delay = self._exponential_backoff(attempt)
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                else:
                    logger.error("Unexpected error after all retries")

        logger.error(f"Failed to generate content after {self.max_retries} attempts: {last_error}")
        return None

    def validate_tone(self, text: str) -> Optional[float]:
        """
        Validate tone of text using OpenAI (optional).

        Args:
            text: Text to validate

        Returns:
            Tone score (0-10, where 10 is empowering) or None if validation fails
        """
        if not self.client:
            return None

        prompt = (
            "Analyze this financial recommendation text for tone. "
            "Look for shaming language, judgmental phrases, or negative language. "
            "Rate the tone on a scale of 0-10, where:\n"
            "- 0-3: Shaming, judgmental, negative\n"
            "- 4-6: Neutral but could be improved\n"
            "- 7-10: Empowering, educational, supportive\n\n"
            f"Text: {text}\n\n"
            "Respond with only the score (0-10) as a number."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.fallback_model,  # Use cheaper model for tone validation
                messages=[
                    {"role": "system", "content": "You are a tone analyzer for financial content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10,
            )

            score_str = response.choices[0].message.content.strip()
            score = float(score_str)

            # Clamp score to 0-10 range
            score = max(0, min(10, score))

            logger.info(f"Tone validation score: {score}/10")
            return score

        except Exception as e:
            logger.warning(f"Failed to validate tone: {str(e)}")
            return None


# Global OpenAI client instance
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> Optional[OpenAIClient]:
    """
    Get global OpenAI client instance.

    Returns:
        OpenAI client instance or None if not available
    """
    global _openai_client

    if _openai_client is not None:
        return _openai_client

    # Try to get API key and model from environment or config
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    fallback_model = os.getenv("OPENAI_FALLBACK_MODEL", "gpt-3.5-turbo")

    _openai_client = OpenAIClient(
        api_key=api_key,
        model=model,
        fallback_model=fallback_model,
    )

    return _openai_client


