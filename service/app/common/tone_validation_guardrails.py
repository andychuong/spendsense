"""Tone validation guardrails service for validating recommendation tone."""

import logging
import uuid
import re
from typing import Dict, List, Any, Optional, Tuple

from sqlalchemy.orm import Session

from app.common.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# Shaming/judgmental keywords to flag
SHAMING_KEYWORDS = [
    "you're overspending",
    "irresponsible",
    "wasteful",
    "bad with money",
    "terrible",
    "awful",
    "should be ashamed",
    "you should feel",
    "you're wasting",
    "stupid",
    "dumb",
    "foolish",
    "you're failing",
    "you're failing at",
    "terrible job",
    "poor choices",
    "bad choices",
    "stupid decision",
    "you're wrong",
    "you're doing it wrong",
    "rent-to-own",
]

# Empowering keywords to look for
EMPOWERING_KEYWORDS = [
    "opportunity",
    "improve",
    "potential",
    "you can",
    "help you",
    "support",
    "achieve",
    "reach your goals",
    "build",
    "grow",
    "strengthen",
    "optimize",
    "enhance",
    "progress",
    "advance",
    "success",
    "empower",
    "enable",
    "guide",
    "strategies",
    "tips",
    "steps",
    "you might consider",
    "consider",
    "explore",
]

# Minimum tone score threshold (0-10 scale, where 10 is most empowering)
MIN_TONE_SCORE = 7.0


class ToneError(Exception):
    """Exception raised when tone validation fails."""
    pass


class ToneValidationGuardrails:
    """Service for enforcing tone validation guardrails on recommendations."""

    def __init__(self, db_session: Session, use_openai: bool = True):
        """
        Initialize tone validation guardrails service.

        Args:
            db_session: SQLAlchemy database session
            use_openai: Whether to use OpenAI for tone validation (default: True)
        """
        self.db = db_session
        self.use_openai = use_openai
        self.openai_client = get_openai_client() if use_openai else None

    def check_shaming_keywords(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check text for shaming/judgmental keywords.

        Args:
            text: Text to check

        Returns:
            Tuple of (has_shaming_keywords, list_of_found_keywords)
        """
        text_lower = text.lower()
        found_keywords = []

        for keyword in SHAMING_KEYWORDS:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_keywords.append(keyword)

        return len(found_keywords) > 0, found_keywords

    def check_empowering_keywords(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check text for empowering keywords.

        Args:
            text: Text to check

        Returns:
            Tuple of (has_empowering_keywords, list_of_found_keywords)
        """
        text_lower = text.lower()
        found_keywords = []

        for keyword in EMPOWERING_KEYWORDS:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_keywords.append(keyword)

        return len(found_keywords) > 0, found_keywords

    def validate_tone_keyword_based(self, text: str) -> Tuple[bool, str]:
        """
        Validate tone using keyword-based approach.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, explanation)
        """
        has_shaming, shaming_keywords = self.check_shaming_keywords(text)
        has_empowering, empowering_keywords = self.check_empowering_keywords(text)

        if has_shaming:
            explanation = (
                f"Text contains shaming/judgmental language: {', '.join(shaming_keywords[:3])}. "
                f"Please use neutral, supportive language instead."
            )
            return False, explanation

        if has_empowering:
            explanation = (
                f"Text uses empowering language: {', '.join(empowering_keywords[:3])}. "
                f"Tone is appropriate."
            )
            return True, explanation

        # Neutral text - not shaming but could be more empowering
        explanation = (
            "Text uses neutral tone. Consider adding more empowering language "
            "to better support users."
        )
        return True, explanation  # Neutral is acceptable, but not ideal

    def validate_tone_openai(self, text: str) -> Optional[float]:
        """
        Validate tone using OpenAI API (optional).

        Args:
            text: Text to validate

        Returns:
            Tone score (0-10, where 10 is empowering) or None if validation fails
        """
        if not self.openai_client:
            return None

        try:
            score = self.openai_client.validate_tone(text)
            return score
        except Exception as e:
            logger.warning(f"OpenAI tone validation failed: {str(e)}")
            return None

    def validate_tone(
        self,
        text: str,
        user_id: Optional[uuid.UUID] = None,
        recommendation_id: Optional[str] = None,
        raise_on_failure: bool = False,
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Validate tone of recommendation text.

        This method performs comprehensive tone validation:
        - Keyword-based checks for shaming/judgmental language
        - Keyword-based checks for empowering language
        - Optional OpenAI-based tone scoring

        Args:
            text: Recommendation text to validate
            user_id: Optional user ID for logging
            recommendation_id: Optional recommendation ID for logging
            raise_on_failure: If True, raise ToneError if tone is invalid

        Returns:
            Tuple of (is_valid, explanation, tone_score)
            - is_valid: True if tone is acceptable (score >= 7 or no shaming keywords)
            - explanation: Human-readable explanation of validation result
            - tone_score: OpenAI tone score (0-10) if available, None otherwise

        Raises:
            ToneError: If raise_on_failure=True and tone is invalid
        """
        # First, check for shaming keywords (immediate failure)
        has_shaming, shaming_keywords = self.check_shaming_keywords(text)

        if has_shaming:
            explanation = (
                f"Text contains shaming/judgmental language: {', '.join(shaming_keywords[:3])}. "
                f"Please use neutral, supportive language instead."
            )
            self.log_tone_validation(
                user_id,
                recommendation_id,
                False,
                explanation,
                None,
            )
            if raise_on_failure:
                raise ToneError(explanation)
            return False, explanation, None

        # Try OpenAI validation if available
        openai_score = None
        if self.use_openai:
            openai_score = self.validate_tone_openai(text)

        # Determine validity based on OpenAI score if available
        if openai_score is not None:
            is_valid = openai_score >= MIN_TONE_SCORE

            if is_valid:
                explanation = (
                    f"Tone is appropriate (score: {openai_score:.1f}/10). "
                    f"Text uses empowering, educational language."
                )
            else:
                explanation = (
                    f"Tone needs improvement (score: {openai_score:.1f}/10). "
                    f"Text should be more empowering and supportive (target: {MIN_TONE_SCORE}+)."
                )

            self.log_tone_validation(
                user_id,
                recommendation_id,
                is_valid,
                explanation,
                openai_score,
            )

            if not is_valid and raise_on_failure:
                raise ToneError(explanation)

            return is_valid, explanation, openai_score

        # Fallback to keyword-based validation if OpenAI not available
        is_valid, explanation = self.validate_tone_keyword_based(text)

        # Adjust explanation based on keyword check
        if not is_valid:
            # Shouldn't happen since we already checked shaming keywords, but handle it
            pass
        else:
            # Check if we have empowering keywords
            has_empowering, empowering_keywords = self.check_empowering_keywords(text)
            if has_empowering:
                explanation = (
                    f"Tone is appropriate (keyword-based check). "
                    f"Text uses empowering language: {', '.join(empowering_keywords[:3])}."
                )
            else:
                explanation = (
                    f"Tone is neutral (keyword-based check). "
                    f"Consider adding more empowering language to better support users."
                )

        self.log_tone_validation(
            user_id,
            recommendation_id,
            is_valid,
            explanation,
            None,
        )

        if not is_valid and raise_on_failure:
            raise ToneError(explanation)

        return is_valid, explanation, None

    def require_appropriate_tone(
        self,
        text: str,
        user_id: Optional[uuid.UUID] = None,
        recommendation_id: Optional[str] = None,
    ) -> None:
        """
        Require appropriate tone for recommendation text.

        Raises ToneError if tone is invalid.

        Args:
            text: Recommendation text to validate
            user_id: Optional user ID for logging
            recommendation_id: Optional recommendation ID for logging

        Raises:
            ToneError: If tone is invalid
        """
        self.validate_tone(
            text,
            user_id,
            recommendation_id,
            raise_on_failure=True,
        )

    def log_tone_validation(
        self,
        user_id: Optional[uuid.UUID],
        recommendation_id: Optional[str],
        is_valid: bool,
        explanation: str,
        tone_score: Optional[float],
        details: Optional[str] = None,
    ) -> None:
        """
        Log a tone validation event.

        Args:
            user_id: Optional user ID
            recommendation_id: Optional recommendation ID
            is_valid: Whether tone is valid
            explanation: Validation explanation
            tone_score: Optional tone score (0-10)
            details: Optional additional details about the check
        """
        log_message = (
            f"Tone validation logged: "
            f"User: {user_id or 'unknown'}, "
            f"Recommendation: {recommendation_id or 'unknown'}, "
            f"Valid: {is_valid}, "
            f"Score: {tone_score if tone_score is not None else 'N/A'}, "
            f"Explanation: {explanation}"
        )
        if details:
            log_message += f", Details: {details}"

        if is_valid:
            logger.info(log_message)
        else:
            logger.warning(log_message)



