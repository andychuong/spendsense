"""Example usage of recommendation generation service."""

import uuid
import logging
from sqlalchemy.orm import Session

from app.recommendations.generator import RecommendationGenerator

logger = logging.getLogger(__name__)


def example_generate_recommendations(db_session: Session, user_id: uuid.UUID):
    """
    Example: Generate recommendations for a user.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Generating recommendations for user {user_id}")

    # Initialize recommendation generator
    # use_openai=True enables OpenAI content generation (with fallback to templates)
    # use_openai=False uses only pre-generated templates
    generator = RecommendationGenerator(db_session, use_openai=True)

    # Generate recommendations
    # This will automatically:
    # 1. Get user's assigned persona
    # 2. Get detected signals from profile
    # 3. Check existing products
    # 4. Select 3-5 education items matching persona
    # 5. Select 1-3 partner offers matching persona and eligibility
    # 6. Generate rationales using detected signals
    # 7. Store recommendations in database with PENDING status
    result = generator.generate_recommendations(user_id)

    logger.info(f"Generated {len(result['recommendations'])} recommendations")
    logger.info(f"Education items: {result['education_count']}")
    logger.info(f"Partner offers: {result['partner_offer_count']}")

    return result


def example_generate_recommendations_with_signals(
    db_session: Session,
    user_id: uuid.UUID,
    signals_30d: dict,
    signals_180d: dict,
):
    """
    Example: Generate recommendations with pre-computed signals.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        signals_30d: Pre-computed 30-day signals
        signals_180d: Pre-computed 180-day signals
    """
    logger.info(f"Generating recommendations for user {user_id} with pre-computed signals")

    # Initialize recommendation generator
    # use_openai=True enables OpenAI content generation (with fallback to templates)
    # use_openai=False uses only pre-generated templates
    generator = RecommendationGenerator(db_session, use_openai=True)

    # Generate recommendations with pre-computed signals
    result = generator.generate_recommendations(
        user_id,
        signals_30d=signals_30d,
        signals_180d=signals_180d,
    )

    logger.info(f"Generated {len(result['recommendations'])} recommendations")

    return result


if __name__ == "__main__":
    # Example usage
    from backend.app.database import SessionLocal

    # Create database session
    db = SessionLocal()

    try:
        # Example user ID (replace with actual user ID)
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        # Generate recommendations
        result = example_generate_recommendations(db, user_id)

        print(f"Generated recommendations for user {user_id}:")
        print(f"  Persona: {result['persona_name']} (ID: {result['persona_id']})")
        print(f"  Education items: {result['education_count']}")
        print(f"  Partner offers: {result['partner_offer_count']}")
        print(f"  Total recommendations: {len(result['recommendations'])}")

        for rec in result['recommendations']:
            print(f"    - {rec['type']}: {rec['title']}")

    finally:
        db.close()

