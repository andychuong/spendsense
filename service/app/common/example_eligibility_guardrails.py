"""Example usage of eligibility guardrails service."""

import uuid
import logging
from sqlalchemy.orm import Session

from app.common.eligibility_guardrails import EligibilityGuardrails, EligibilityError
from app.recommendations.catalog import EDUCATION_CATALOG, PARTNER_OFFER_CATALOG
from app.recommendations.generator import RecommendationGenerator

logger = logging.getLogger(__name__)


def example_check_eligibility_for_education_item(
    db_session: Session,
    user_id: uuid.UUID,
    item_id: str,
    signals_30d: dict = None,
    signals_180d: dict = None,
):
    """
    Example: Check eligibility for an education item.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        item_id: Education item ID
        signals_30d: Optional 30-day signals
        signals_180d: Optional 180-day signals
    """
    logger.info(f"Checking eligibility for education item {item_id} for user {user_id}")

    guardrails = EligibilityGuardrails(db_session)

    # Find education item
    item = next((item for item in EDUCATION_CATALOG if item["id"] == item_id), None)
    if not item:
        logger.warning(f"Education item {item_id} not found")
        return None

    # Check eligibility
    is_eligible, explanation = guardrails.check_eligibility(
        item,
        user_id,
        signals_30d,
        signals_180d,
        raise_on_failure=False,
    )

    if is_eligible:
        logger.info(f"Education item {item_id} is eligible: {explanation}")
    else:
        logger.warning(f"Education item {item_id} is not eligible: {explanation}")

    return is_eligible, explanation


def example_check_eligibility_for_partner_offer(
    db_session: Session,
    user_id: uuid.UUID,
    offer_id: str,
    signals_30d: dict = None,
    signals_180d: dict = None,
):
    """
    Example: Check eligibility for a partner offer.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        offer_id: Partner offer ID
        signals_30d: Optional 30-day signals
        signals_180d: Optional 180-day signals
    """
    logger.info(f"Checking eligibility for partner offer {offer_id} for user {user_id}")

    guardrails = EligibilityGuardrails(db_session)

    # Find partner offer
    offer = next((offer for offer in PARTNER_OFFER_CATALOG if offer["id"] == offer_id), None)
    if not offer:
        logger.warning(f"Partner offer {offer_id} not found")
        return None

    # Check eligibility
    is_eligible, explanation = guardrails.check_eligibility(
        offer,
        user_id,
        signals_30d,
        signals_180d,
        raise_on_failure=False,
    )

    if is_eligible:
        logger.info(f"Partner offer {offer_id} is eligible: {explanation}")
    else:
        logger.warning(f"Partner offer {offer_id} is not eligible: {explanation}")

    return is_eligible, explanation


def example_check_harmful_product(db_session: Session, user_id: uuid.UUID):
    """
    Example: Check if a recommendation is a harmful product.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Checking for harmful products for user {user_id}")

    guardrails = EligibilityGuardrails(db_session)

    # Create a test recommendation with harmful keywords
    harmful_offer = {
        "id": "harmful_001",
        "title": "Payday Loan - Fast Cash",
        "content": "Get cash advance with easy approval",
        "eligibility_requirements": {},
    }

    is_harmful = guardrails.is_harmful_product(harmful_offer)

    if is_harmful:
        logger.warning(f"Detected harmful product: {harmful_offer['title']}")
    else:
        logger.info(f"Product is not harmful: {harmful_offer['title']}")

    return is_harmful


def example_check_existing_products(db_session: Session, user_id: uuid.UUID):
    """
    Example: Check what products user already has.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Checking existing products for user {user_id}")

    guardrails = EligibilityGuardrails(db_session)

    existing_products = guardrails.check_existing_products(user_id)

    logger.info(f"User {user_id} existing products: {existing_products}")

    return existing_products


def example_calculate_income_and_credit_score(
    db_session: Session,
    user_id: uuid.UUID,
    signals_30d: dict = None,
    signals_180d: dict = None,
):
    """
    Example: Calculate income and credit score for eligibility checks.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        signals_30d: Optional 30-day signals
        signals_180d: Optional 180-day signals
    """
    logger.info(f"Calculating income and credit score for user {user_id}")

    guardrails = EligibilityGuardrails(db_session)

    # Calculate income
    estimated_income = guardrails.calculate_income_from_transactions(user_id)
    logger.info(f"Estimated monthly income: ${estimated_income:.2f}" if estimated_income else "Income not available")

    # Estimate credit score
    estimated_credit_score = guardrails.estimate_credit_score(
        user_id,
        signals_30d,
        signals_180d,
    )
    logger.info(f"Estimated credit score: {estimated_credit_score}" if estimated_credit_score else "Credit score not available")

    return estimated_income, estimated_credit_score


def example_require_eligibility_for_recommendation(
    db_session: Session,
    user_id: uuid.UUID,
    recommendation: dict,
    signals_30d: dict = None,
    signals_180d: dict = None,
):
    """
    Example: Require eligibility for a recommendation (raises exception if not eligible).

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        recommendation: Recommendation dictionary
        signals_30d: Optional 30-day signals
        signals_180d: Optional 180-day signals
    """
    logger.info(f"Requiring eligibility for recommendation {recommendation.get('id')} for user {user_id}")

    guardrails = EligibilityGuardrails(db_session)

    try:
        guardrails.require_eligibility(
            recommendation,
            user_id,
            signals_30d,
            signals_180d,
        )
        logger.info(f"Recommendation {recommendation.get('id')} is eligible")
        return True
    except EligibilityError as e:
        logger.warning(f"Recommendation {recommendation.get('id')} is not eligible: {e}")
        return False


def example_eligibility_guardrails_integration(
    db_session: Session,
    user_id: uuid.UUID,
    signals_30d: dict = None,
    signals_180d: dict = None,
):
    """
    Example: Complete workflow showing eligibility guardrails integration.

    This demonstrates how eligibility guardrails filter recommendations
    based on income, credit score, existing products, and harmful product checks.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        signals_30d: Optional 30-day signals
        signals_180d: Optional 180-day signals
    """
    logger.info(f"Running eligibility guardrails integration for user {user_id}")

    guardrails = EligibilityGuardrails(db_session)

    try:
        # Step 1: Check existing products
        existing_products = guardrails.check_existing_products(user_id)
        logger.info(f"User {user_id} existing products: {existing_products}")

        # Step 2: Calculate income and credit score
        estimated_income = guardrails.calculate_income_from_transactions(user_id)
        estimated_credit_score = guardrails.estimate_credit_score(
            user_id,
            signals_30d,
            signals_180d,
        )
        logger.info(f"Income: ${estimated_income:.2f}" if estimated_income else "Income: Not available")
        logger.info(f"Credit Score: {estimated_credit_score}" if estimated_credit_score else "Credit Score: Not available")

        # Step 3: Check eligibility for partner offers
        eligible_offers = []
        for offer in PARTNER_OFFER_CATALOG[:3]:  # Check first 3 offers
            is_eligible, explanation = guardrails.check_eligibility(
                offer,
                user_id,
                signals_30d,
                signals_180d,
                raise_on_failure=False,
            )

            if is_eligible:
                logger.info(f"Offer {offer['id']} ({offer['title']}) is eligible: {explanation}")
                eligible_offers.append(offer)
            else:
                logger.warning(f"Offer {offer['id']} ({offer['title']}) is not eligible: {explanation}")

        # Step 4: Generate recommendations with eligibility filtering
        recommendation_generator = RecommendationGenerator(db_session, use_openai=False)
        recommendations = recommendation_generator.generate_recommendations(
            user_id,
            signals_30d,
            signals_180d,
        )

        logger.info(
            f"Generated {len(recommendations.get('recommendations', []))} recommendations "
            f"({recommendations.get('education_count', 0)} education, "
            f"{recommendations.get('partner_offer_count', 0)} partner offers)"
        )

        return {
            "existing_products": existing_products,
            "estimated_income": estimated_income,
            "estimated_credit_score": estimated_credit_score,
            "eligible_offers": eligible_offers,
            "recommendations": recommendations,
        }

    except EligibilityError as e:
        logger.error(f"Workflow blocked: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage (requires database session)
    # from backend.app.database import SessionLocal
    # db = SessionLocal()
    # user_id = uuid.UUID("...")
    #
    # # Check eligibility for education item
    # example_check_eligibility_for_education_item(db, user_id, "edu_001")
    #
    # # Check eligibility for partner offer
    # example_check_eligibility_for_partner_offer(db, user_id, "offer_001")
    #
    # # Check for harmful products
    # example_check_harmful_product(db, user_id)
    #
    # # Check existing products
    # example_check_existing_products(db, user_id)
    #
    # # Calculate income and credit score
    # example_calculate_income_and_credit_score(db, user_id)
    #
    # # Complete workflow
    # example_eligibility_guardrails_integration(db, user_id)
    pass



