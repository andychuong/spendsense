"""Consent guardrails service for enforcing consent before data processing."""

import logging
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

# Try to import User model from backend
try:
    from backend.app.models.user import User
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.user import User

logger = logging.getLogger(__name__)


class ConsentError(Exception):
    """Exception raised when consent check fails."""
    pass


class ConsentGuardrails:
    """Service for enforcing consent guardrails before data processing."""

    def __init__(self, db_session: Session):
        """
        Initialize consent guardrails service.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def get_user_consent_status(self, user_id: uuid.UUID) -> Optional[bool]:
        """
        Get user consent status from database.

        Args:
            user_id: User ID

        Returns:
            True if consent granted, False if not granted, None if user not found
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        return user.consent_status

    def check_consent(
        self,
        user_id: uuid.UUID,
        operation: str,
        raise_on_failure: bool = True,
    ) -> bool:
        """
        Check if user has granted consent for data processing.

        This method logs the consent check and optionally raises an exception
        if consent is not granted.

        Args:
            user_id: User ID
            operation: Description of the operation being performed
                (e.g., "feature_detection", "recommendation_generation")
            raise_on_failure: If True, raise ConsentError if consent not granted

        Returns:
            True if consent granted, False otherwise

        Raises:
            ConsentError: If raise_on_failure=True and consent not granted
        """
        consent_status = self.get_user_consent_status(user_id)

        if consent_status is None:
            logger.warning(
                f"Consent check failed: User {user_id} not found for operation '{operation}'"
            )
            if raise_on_failure:
                raise ConsentError(f"User {user_id} not found")
            return False

        if consent_status:
            logger.info(
                f"Consent check passed: User {user_id} has granted consent for '{operation}'"
            )
            return True
        else:
            logger.warning(
                f"Consent check failed: User {user_id} has not granted consent for '{operation}'"
            )
            if raise_on_failure:
                raise ConsentError(
                    f"User {user_id} has not granted consent for data processing. "
                    f"Operation '{operation}' blocked."
                )
            return False

    def require_consent(
        self,
        user_id: uuid.UUID,
        operation: str,
    ) -> None:
        """
        Require consent for data processing operation.

        Raises ConsentError if consent is not granted.

        Args:
            user_id: User ID
            operation: Description of the operation being performed

        Raises:
            ConsentError: If consent not granted
        """
        self.check_consent(user_id, operation, raise_on_failure=True)

    def log_consent_check(
        self,
        user_id: uuid.UUID,
        operation: str,
        consent_granted: bool,
        details: Optional[str] = None,
    ) -> None:
        """
        Log a consent check event.

        Args:
            user_id: User ID
            operation: Description of the operation
            consent_granted: Whether consent was granted
            details: Optional additional details about the check
        """
        log_message = (
            f"Consent check logged: User {user_id}, Operation '{operation}', "
            f"Consent Granted: {consent_granted}"
        )
        if details:
            log_message += f", Details: {details}"

        if consent_granted:
            logger.info(log_message)
        else:
            logger.warning(log_message)


def check_consent_decorator(operation: str):
    """
    Decorator to check consent before executing a function.

    Usage:
        @check_consent_decorator("feature_detection")
        def generate_signals(self, user_id: uuid.UUID, ...):
            # Function will only execute if consent is granted
            ...

    Args:
        operation: Description of the operation (for logging)

    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(self, user_id: uuid.UUID, *args, **kwargs):
            # Get db_session from self (assuming service classes have db_session attribute)
            db_session = getattr(self, 'db', None) or getattr(self, 'db_session', None)

            if db_session is None:
                logger.error(
                    f"Consent check decorator failed: {type(self).__name__} "
                    f"does not have db or db_session attribute"
                )
                raise ConsentError("Database session not available for consent check")

            guardrails = ConsentGuardrails(db_session)
            guardrails.require_consent(user_id, operation)

            return func(self, user_id, *args, **kwargs)
        return wrapper
    return decorator


