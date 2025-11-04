"""Example usage of tone validation guardrails service."""

import uuid
import logging
from sqlalchemy.orm import Session

from app.common.tone_validation_guardrails import ToneValidationGuardrails, ToneError
from app.recommendations.catalog import EDUCATION_CATALOG, PARTNER_OFFER_CATALOG

logger = logging.getLogger(__name__)


def example_check_tone_for_text(
    db_session: Session,
    text: str,
    user_id: uuid.UUID = None,
    recommendation_id: str = None,
):
    """
    Example: Check tone for a piece of text.

    Args:
        db_session: SQLAlchemy database session
        text: Text to validate
        user_id: Optional user ID for logging
        recommendation_id: Optional recommendation ID for logging
    """
    logger.info(f"Checking tone for text: {text[:50]}...")

    guardrails = ToneValidationGuardrails(db_session, use_openai=True)

    # Check tone
    is_valid, explanation, score = guardrails.validate_tone(
        text,
        user_id,
        recommendation_id,
        raise_on_failure=False,
    )

    if is_valid:
        logger.info(f"Tone is valid: {explanation}")
        if score is not None:
            logger.info(f"Tone score: {score}/10")
    else:
        logger.warning(f"Tone is invalid: {explanation}")
        if score is not None:
            logger.warning(f"Tone score: {score}/10")

    return is_valid, explanation, score


def example_check_shaming_keywords(db_session: Session):
    """
    Example: Check for shaming keywords in text.

    Args:
        db_session: SQLAlchemy database session
    """
    logger.info("Checking for shaming keywords")

    guardrails = ToneValidationGuardrails(db_session, use_openai=False)

    # Test text with shaming language
    bad_text = "You're overspending and being irresponsible with your money. This is terrible!"

    has_shaming, keywords = guardrails.check_shaming_keywords(bad_text)

    if has_shaming:
        logger.warning(f"Found shaming keywords: {', '.join(keywords)}")
    else:
        logger.info("No shaming keywords found")

    # Test text with empowering language
    good_text = "You have an opportunity to improve your financial situation. Here are some strategies to help you succeed."

    has_shaming, keywords = guardrails.check_shaming_keywords(good_text)

    if has_shaming:
        logger.warning(f"Found shaming keywords: {', '.join(keywords)}")
    else:
        logger.info("No shaming keywords found")

    return has_shaming


def example_check_empowering_keywords(db_session: Session):
    """
    Example: Check for empowering keywords in text.

    Args:
        db_session: SQLAlchemy database session
    """
    logger.info("Checking for empowering keywords")

    guardrails = ToneValidationGuardrails(db_session, use_openai=False)

    # Test text with empowering language
    good_text = "You have an opportunity to improve your financial situation. Here are some strategies to help you succeed and build wealth."

    has_empowering, keywords = guardrails.check_empowering_keywords(good_text)

    if has_empowering:
        logger.info(f"Found empowering keywords: {', '.join(keywords)}")
    else:
        logger.warning("No empowering keywords found")

    # Test neutral text
    neutral_text = "Your credit card balance is $5,000. The interest rate is 18%."

    has_empowering, keywords = guardrails.check_empowering_keywords(neutral_text)

    if has_empowering:
        logger.info(f"Found empowering keywords: {', '.join(keywords)}")
    else:
        logger.info("No empowering keywords found (neutral text)")

    return has_empowering


def example_keyword_based_validation(db_session: Session):
    """
    Example: Validate tone using keyword-based approach.

    Args:
        db_session: SQLAlchemy database session
    """
    logger.info("Testing keyword-based tone validation")

    guardrails = ToneValidationGuardrails(db_session, use_openai=False)

    # Test bad text
    bad_text = "You're overspending and being irresponsible with your money."
    is_valid, explanation = guardrails.validate_tone_keyword_based(bad_text)

    logger.info(f"Bad text validation: Valid={is_valid}, Explanation={explanation}")

    # Test good text
    good_text = "You have an opportunity to improve your financial situation. Here are some strategies to help you succeed."
    is_valid, explanation = guardrails.validate_tone_keyword_based(good_text)

    logger.info(f"Good text validation: Valid={is_valid}, Explanation={explanation}")

    # Test neutral text
    neutral_text = "Your credit card balance is $5,000. The interest rate is 18%."
    is_valid, explanation = guardrails.validate_tone_keyword_based(neutral_text)

    logger.info(f"Neutral text validation: Valid={is_valid}, Explanation={explanation}")

    return {"bad": (is_valid, explanation), "good": (is_valid, explanation), "neutral": (is_valid, explanation)}


def example_require_appropriate_tone(db_session: Session):
    """
    Example: Require appropriate tone (raises exception if invalid).

    Args:
        db_session: SQLAlchemy database session
    """
    logger.info("Testing require_appropriate_tone")

    guardrails = ToneValidationGuardrails(db_session, use_openai=False)

    # Test good text (should pass)
    good_text = "You have an opportunity to improve your financial situation. Here are some strategies to help you succeed."

    try:
        guardrails.require_appropriate_tone(good_text)
        logger.info("Good text passed tone validation")
    except ToneError as e:
        logger.warning(f"Good text failed tone validation: {e}")

    # Test bad text (should raise exception)
    bad_text = "You're overspending and being irresponsible with your money. This is terrible!"

    try:
        guardrails.require_appropriate_tone(bad_text)
        logger.warning("Bad text passed tone validation (unexpected)")
    except ToneError as e:
        logger.info(f"Bad text correctly failed tone validation: {e}")

    return True


def example_tone_validation_integration(
    db_session: Session,
    user_id: uuid.UUID,
    use_openai: bool = True,
):
    """
    Example: Complete workflow showing tone validation integration.

    This demonstrates how tone validation filters recommendations
    based on shaming language, judgmental phrases, and empowering tone.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
        use_openai: Whether to use OpenAI for tone validation
    """
    logger.info(f"Running tone validation integration for user {user_id}")

    guardrails = ToneValidationGuardrails(db_session, use_openai=use_openai)

    # Test texts with different tones
    test_texts = [
        {
            "text": "You're overspending and being irresponsible with your money. This is terrible!",
            "description": "Shaming language",
        },
        {
            "text": "Your credit card balance is $5,000. The interest rate is 18%.",
            "description": "Neutral text",
        },
        {
            "text": "You have an opportunity to improve your financial situation. Here are some strategies to help you succeed.",
            "description": "Empowering language",
        },
        {
            "text": "We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could improve your credit score and reduce interest charges of $87/month.",
            "description": "Educational with empowering tone",
        },
    ]

    results = []

    for test_case in test_texts:
        is_valid, explanation, score = guardrails.validate_tone(
            test_case["text"],
            user_id,
            f"test_{test_case['description']}",
            raise_on_failure=False,
        )

        result = {
            "description": test_case["description"],
            "is_valid": is_valid,
            "explanation": explanation,
            "score": score,
        }
        results.append(result)

        logger.info(
            f"Text '{test_case['description']}': "
            f"Valid={is_valid}, Score={score if score else 'N/A'}, "
            f"Explanation={explanation[:100]}..."
        )

    return results


def example_validate_catalog_items(db_session: Session, user_id: uuid.UUID):
    """
    Example: Validate tone for catalog items.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    """
    logger.info(f"Validating tone for catalog items for user {user_id}")

    guardrails = ToneValidationGuardrails(db_session, use_openai=False)

    # Validate education items
    education_results = []
    for item in EDUCATION_CATALOG[:3]:  # Check first 3 items
        combined_text = f"{item['title']}\n\n{item['content']}"
        is_valid, explanation, score = guardrails.validate_tone(
            combined_text,
            user_id,
            item["id"],
            raise_on_failure=False,
        )

        education_results.append({
            "id": item["id"],
            "title": item["title"],
            "is_valid": is_valid,
            "explanation": explanation,
            "score": score,
        })

        logger.info(
            f"Education item {item['id']} ({item['title']}): "
            f"Valid={is_valid}, Score={score if score else 'N/A'}"
        )

    # Validate partner offers
    partner_results = []
    for offer in PARTNER_OFFER_CATALOG[:3]:  # Check first 3 offers
        combined_text = f"{offer['title']}\n\n{offer['content']}"
        is_valid, explanation, score = guardrails.validate_tone(
            combined_text,
            user_id,
            offer["id"],
            raise_on_failure=False,
        )

        partner_results.append({
            "id": offer["id"],
            "title": offer["title"],
            "is_valid": is_valid,
            "explanation": explanation,
            "score": score,
        })

        logger.info(
            f"Partner offer {offer['id']} ({offer['title']}): "
            f"Valid={is_valid}, Score={score if score else 'N/A'}"
        )

    return {
        "education_items": education_results,
        "partner_offers": partner_results,
    }


if __name__ == "__main__":
    # Example usage (requires database session)
    # from backend.app.database import SessionLocal
    # db = SessionLocal()
    # user_id = uuid.UUID("...")
    #
    # # Check tone for text
    # example_check_tone_for_text(db, "You're overspending!", user_id, "test_001")
    #
    # # Check shaming keywords
    # example_check_shaming_keywords(db)
    #
    # # Check empowering keywords
    # example_check_empowering_keywords(db)
    #
    # # Keyword-based validation
    # example_keyword_based_validation(db)
    #
    # # Require appropriate tone
    # example_require_appropriate_tone(db)
    #
    # # Complete workflow
    # example_tone_validation_integration(db, user_id)
    #
    # # Validate catalog items
    # example_validate_catalog_items(db, user_id)
    pass


