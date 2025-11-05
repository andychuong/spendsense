"""Example usage of rationale generation service."""

import uuid
import logging
from sqlalchemy.orm import Session

from app.recommendations.rationale import RationaleGenerator
from app.recommendations.catalog import EDUCATION_CATALOG, PARTNER_OFFER_CATALOG

logger = logging.getLogger(__name__)


def example_generate_rationale_standalone(db_session: Session, user_id: uuid.UUID):
    """
    Example: Generate rationale for a recommendation using RationaleGenerator.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Generating rationale for user {user_id}")

    # Initialize rationale generator
    rationale_generator = RationaleGenerator(db_session)

    # Example signals (normally from user profile)
    signals_30d = {
        "credit": {
            "critical_utilization_cards": [
                {
                    "account_id": "acct-123",
                    "account_name": "Visa Credit Card",
                    "utilization_percent": 68.5,
                    "current_balance": 3400.00,
                    "credit_limit": 5000.00,
                }
            ],
            "cards_with_interest": [
                {
                    "account_id": "acct-123",
                    "account_name": "Visa Credit Card",
                    "interest_charges": {
                        "total_interest_charges": 87.50,
                    }
                }
            ],
        }
    }

    signals_180d = {}

    # Test with Persona 1 (High Utilization)
    test_item = EDUCATION_CATALOG[0]
    rationale = rationale_generator.generate_rationale(
        test_item,
        signals_30d,
        signals_180d,
        persona_id=1,
        user_id=user_id,
    )

    logger.info(f"Generated rationale: {rationale[:200]}...")
    return rationale


def example_generate_rationale_with_account_details(
    db_session: Session,
    user_id: uuid.UUID,
    signals_30d: dict,
    signals_180d: dict,
):
    """
    Example: Generate rationale with account details from database.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        signals_30d: 30-day signals
        signals_180d: 180-day signals
    """
    logger.info(f"Generating rationale with account details for user {user_id}")

    # Initialize rationale generator
    rationale_generator = RationaleGenerator(db_session)

    # Example education item
    test_item = EDUCATION_CATALOG[0]

    # Generate rationale for Persona 1
    rationale = rationale_generator.generate_rationale(
        test_item,
        signals_30d,
        signals_180d,
        persona_id=1,
        user_id=user_id,
    )

    logger.info(f"Generated rationale: {rationale}")
    return rationale


def example_format_helpers():
    """Example: Using formatting helper methods."""
    from sqlalchemy.orm import Session

    # This would normally use a real database session
    # For demonstration, showing the formatting methods

    class MockAccount:
        def __init__(self):
            self.name = "Visa Credit Card"
            self.mask = "4523"
            self.account_id = "acct-123456789"

    class MockSession:
        pass

    db = MockSession()
    generator = RationaleGenerator(db)

    # Format account number
    account = MockAccount()
    formatted = generator.format_account_number(account)
    print(f"Formatted account: {formatted}")
    # Output: "Visa Credit Card ending in 4523"

    # Format currency
    amount = 1234.56
    formatted = generator.format_currency(amount)
    print(f"Formatted currency: {formatted}")
    # Output: "$1,234.56"

    # Format percentage
    percent = 68.5
    formatted = generator.format_percent(percent)
    print(f"Formatted percent: {formatted}")
    # Output: "68.5%"

    # Format date
    from datetime import date
    date_value = date(2024, 1, 15)
    formatted = generator.format_date(date_value)
    print(f"Formatted date: {formatted}")
    # Output: "January 15, 2024"



