"""Example usage of consent guardrails service."""

import uuid
import logging
from sqlalchemy.orm import Session

from app.common.consent_guardrails import ConsentGuardrails, ConsentError
from app.features.subscriptions import SubscriptionDetector
from app.features.savings import SavingsDetector
from app.features.credit import CreditUtilizationDetector
from app.features.income import IncomeStabilityDetector
from app.features.persona_assignment import PersonaAssignmentService
from app.recommendations.generator import RecommendationGenerator

logger = logging.getLogger(__name__)


def example_check_consent(db_session: Session, user_id: uuid.UUID):
    """
    Example: Check user consent status.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Checking consent for user {user_id}")

    guardrails = ConsentGuardrails(db_session)

    # Check consent status
    consent_status = guardrails.get_user_consent_status(user_id)

    if consent_status is None:
        logger.warning(f"User {user_id} not found")
    elif consent_status:
        logger.info(f"User {user_id} has granted consent")
    else:
        logger.warning(f"User {user_id} has not granted consent")

    return consent_status


def example_require_consent_for_feature_detection(
    db_session: Session,
    user_id: uuid.UUID,
):
    """
    Example: Require consent before feature detection.

    This demonstrates how consent guardrails block data processing
    when consent is not granted.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Attempting feature detection for user {user_id}")

    guardrails = ConsentGuardrails(db_session)

    try:
        # Check consent before processing
        guardrails.require_consent(user_id, "feature_detection:subscriptions")

        # If consent granted, proceed with feature detection
        detector = SubscriptionDetector(db_session)
        signals = detector.generate_subscription_signals(user_id)

        logger.info(f"Successfully generated subscription signals for user {user_id}")
        return signals

    except ConsentError as e:
        logger.error(f"Feature detection blocked: {str(e)}")
        return None


def example_require_consent_for_recommendations(
    db_session: Session,
    user_id: uuid.UUID,
):
    """
    Example: Require consent before recommendation generation.

    This demonstrates how consent guardrails block recommendations
    when consent is not granted.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Attempting recommendation generation for user {user_id}")

    try:
        # RecommendationGenerator automatically checks consent
        generator = RecommendationGenerator(db_session, use_openai=False)
        result = generator.generate_recommendations(user_id)

        if result.get("consent_required"):
            logger.warning(f"Recommendation generation blocked: consent required")
            return None

        logger.info(f"Successfully generated recommendations for user {user_id}")
        return result

    except ConsentError as e:
        logger.error(f"Recommendation generation blocked: {str(e)}")
        return None


def example_consent_check_with_logging(
    db_session: Session,
    user_id: uuid.UUID,
    operation: str,
):
    """
    Example: Check consent with explicit logging.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        operation: Operation description
    """
    logger.info(f"Checking consent for operation '{operation}'")

    guardrails = ConsentGuardrails(db_session)

    # Check consent (doesn't raise exception)
    consent_granted = guardrails.check_consent(
        user_id,
        operation,
        raise_on_failure=False,
    )

    # Log the check
    guardrails.log_consent_check(
        user_id,
        operation,
        consent_granted,
        details=f"Operation: {operation}",
    )

    return consent_granted


def example_consent_guardrails_integration(
    db_session: Session,
    user_id: uuid.UUID,
):
    """
    Example: Complete workflow with consent guardrails.

    This demonstrates how consent guardrails are integrated throughout
    the data processing pipeline.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Running complete workflow with consent guardrails for user {user_id}")

    guardrails = ConsentGuardrails(db_session)

    # Step 1: Check consent for feature detection
    try:
        guardrails.require_consent(user_id, "feature_detection")

        # Step 2: Generate all feature signals
        subscription_detector = SubscriptionDetector(db_session)
        subscription_signals = subscription_detector.generate_subscription_signals(user_id)

        savings_detector = SavingsDetector(db_session)
        savings_signals = savings_detector.generate_savings_signals(user_id)

        credit_detector = CreditUtilizationDetector(db_session)
        credit_signals = credit_detector.generate_credit_signals(user_id)

        income_detector = IncomeStabilityDetector(db_session)
        income_signals = income_detector.generate_income_signals(user_id)

        logger.info("All feature signals generated successfully")

        # Step 3: Check consent for persona assignment
        guardrails.require_consent(user_id, "persona_assignment")

        # Step 4: Assign persona
        persona_service = PersonaAssignmentService(db_session)
        persona_result = persona_service.assign_persona(
            user_id,
            signals_30d={
                "subscriptions": subscription_signals.get("signals_30d", {}),
                "savings": savings_signals.get("signals_30d", {}),
                "credit": credit_signals.get("signals_30d", {}),
                "income": income_signals.get("signals_30d", {}),
            },
            signals_180d={
                "subscriptions": subscription_signals.get("signals_180d", {}),
                "savings": savings_signals.get("signals_180d", {}),
                "credit": credit_signals.get("signals_180d", {}),
                "income": income_signals.get("signals_180d", {}),
            },
        )

        logger.info(f"Persona assigned: {persona_result.get('persona_name')}")

        # Step 5: Check consent for recommendation generation
        guardrails.require_consent(user_id, "recommendation_generation")

        # Step 6: Generate recommendations
        recommendation_generator = RecommendationGenerator(db_session, use_openai=False)
        recommendations = recommendation_generator.generate_recommendations(user_id)

        if recommendations.get("consent_required"):
            logger.warning("Recommendation generation blocked: consent required")
            return None

        logger.info(f"Generated {len(recommendations.get('recommendations', []))} recommendations")

        return {
            "subscription_signals": subscription_signals,
            "savings_signals": savings_signals,
            "credit_signals": credit_signals,
            "income_signals": income_signals,
            "persona_assignment": persona_result,
            "recommendations": recommendations,
        }

    except ConsentError as e:
        logger.error(f"Workflow blocked: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage (requires database session)
    # from backend.app.database import SessionLocal
    # db = SessionLocal()
    # user_id = uuid.UUID("...")
    #
    # # Check consent
    # consent_status = example_check_consent(db, user_id)
    #
    # # Try feature detection with consent check
    # signals = example_require_consent_for_feature_detection(db, user_id)
    #
    # # Try recommendation generation with consent check
    # recommendations = example_require_consent_for_recommendations(db, user_id)
    #
    # # Complete workflow
    # result = example_consent_guardrails_integration(db, user_id)
    pass


