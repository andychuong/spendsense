"""Example usage of partner offer service."""

import uuid
import logging
from sqlalchemy.orm import Session

from app.recommendations.partner_offer_service import PartnerOfferService
from app.recommendations.catalog import PARTNER_OFFER_CATALOG

logger = logging.getLogger(__name__)


def example_select_eligible_offers(db_session: Session, user_id: uuid.UUID):
    """
    Example: Select eligible partner offers for a user.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Selecting eligible partner offers for user {user_id}")

    # Initialize partner offer service
    service = PartnerOfferService(db_session)

    # Get user profile to determine persona
    # In real usage, you would get this from UserProfile
    persona_id = 1  # Example: High Utilization persona

    # Select eligible offers
    # This will automatically:
    # 1. Check existing products (credit cards, savings accounts)
    # 2. Calculate income from payroll deposits
    # 3. Estimate credit score from utilization and payment behavior
    # 4. Filter harmful products (payday loans, etc.)
    # 5. Check eligibility requirements (credit score, income, existing products)
    # 6. Generate eligibility explanations
    eligible_offers = service.select_eligible_offers(
        persona_id=persona_id,
        user_id=user_id,
        count=3,
    )

    logger.info(f"Selected {len(eligible_offers)} eligible partner offers")

    for offer in eligible_offers:
        print(f"\nOffer: {offer['title']}")
        print(f"  ID: {offer['id']}")
        print(f"  Eligibility Status: {offer.get('eligibility_status', 'unknown')}")
        print(f"  Eligibility Explanation: {offer.get('eligibility_explanation', 'N/A')}")
        if offer.get('estimated_income'):
            print(f"  Estimated Income: ${offer['estimated_income']:,.2f}/month")
        if offer.get('estimated_credit_score'):
            print(f"  Estimated Credit Score: {offer['estimated_credit_score']}")

    return eligible_offers


def example_check_specific_offer_eligibility(
    db_session: Session,
    user_id: uuid.UUID,
    offer_id: str,
):
    """
    Example: Check eligibility for a specific partner offer.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        offer_id: Partner offer ID
    """
    logger.info(f"Checking eligibility for offer {offer_id} for user {user_id}")

    # Find the offer
    offer = next((o for o in PARTNER_OFFER_CATALOG if o["id"] == offer_id), None)
    if not offer:
        logger.error(f"Offer {offer_id} not found")
        return None

    # Initialize partner offer service
    service = PartnerOfferService(db_session)

    # Get existing products
    existing_products = service.check_existing_products(user_id)

    # Calculate income
    estimated_income = service.calculate_income_from_transactions(user_id)

    # Estimate credit score
    estimated_credit_score = service.estimate_credit_score(user_id)

    # Check eligibility
    is_eligible, explanation = service.check_eligibility(
        offer,
        user_id,
        existing_products,
        estimated_income,
        estimated_credit_score,
    )

    print(f"\nOffer: {offer['title']}")
    print(f"  Eligible: {is_eligible}")
    print(f"  Explanation: {explanation}")
    print(f"  Existing Products: {existing_products}")
    if estimated_income:
        print(f"  Estimated Income: ${estimated_income:,.2f}/month")
    if estimated_credit_score:
        print(f"  Estimated Credit Score: {estimated_credit_score}")

    return {
        "offer": offer,
        "is_eligible": is_eligible,
        "explanation": explanation,
        "existing_products": existing_products,
        "estimated_income": estimated_income,
        "estimated_credit_score": estimated_credit_score,
    }


def example_check_harmful_products(db_session: Session):
    """
    Example: Check for harmful products in catalog.

    Args:
        db_session: SQLAlchemy database session
    """
    logger.info("Checking for harmful products in catalog")

    service = PartnerOfferService(db_session)

    harmful_offers = []
    for offer in PARTNER_OFFER_CATALOG:
        if service.is_harmful_product(offer):
            harmful_offers.append(offer)

    if harmful_offers:
        print(f"\nFound {len(harmful_offers)} harmful products:")
        for offer in harmful_offers:
            print(f"  - {offer['id']}: {offer['title']}")
    else:
        print("\nNo harmful products found in catalog (all clear!)")

    return harmful_offers


if __name__ == "__main__":
    # Example usage
    from backend.app.database import SessionLocal

    # Create database session
    db = SessionLocal()

    try:
        # Example user ID (replace with actual user ID)
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        # Example 1: Select eligible offers
        print("=" * 60)
        print("Example 1: Select Eligible Partner Offers")
        print("=" * 60)
        eligible_offers = example_select_eligible_offers(db, user_id)

        # Example 2: Check specific offer eligibility
        if PARTNER_OFFER_CATALOG:
            print("\n" + "=" * 60)
            print("Example 2: Check Specific Offer Eligibility")
            print("=" * 60)
            first_offer_id = PARTNER_OFFER_CATALOG[0]["id"]
            example_check_specific_offer_eligibility(db, user_id, first_offer_id)

        # Example 3: Check for harmful products
        print("\n" + "=" * 60)
        print("Example 3: Check for Harmful Products")
        print("=" * 60)
        harmful_offers = example_check_harmful_products(db)

    finally:
        db.close()

