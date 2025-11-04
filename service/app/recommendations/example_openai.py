"""Example usage of OpenAI content generation."""

import os
import logging
from typing import Dict, Any

from app.common.openai_client import get_openai_client
from app.recommendations.content_generator import ContentGenerator
from app.recommendations.catalog import EDUCATION_CATALOG, PARTNER_OFFER_CATALOG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_openai_education_content():
    """Example: Generate education content using OpenAI."""
    logger.info("Example: Generating education content with OpenAI")

    # Initialize content generator
    generator = ContentGenerator()

    # Example persona and signals
    persona_id = 1  # High Utilization
    signals = {
        "credit": {
            "high_utilization_cards_30d": [
                {"account_name": "Visa ending in 4523", "utilization": 0.68}
            ],
            "interest_charges_30d": [{"amount": 87.50, "account_name": "Visa ending in 4523"}],
        },
        "subscriptions": {
            "recurring_merchant_count": 5,
            "monthly_recurring_spend_30d": 125.50,
        },
    }

    # Get an education item from catalog
    template_item = EDUCATION_CATALOG[0]  # First education item

    # Generate content using OpenAI (with fallback to template)
    content = generator.generate_education_content(
        template_item,
        persona_id,
        signals,
        use_openai=True,  # Set to False to use template only
    )

    logger.info(f"Generated content:\n{content}")
    return content


def example_openai_partner_offer_content():
    """Example: Generate partner offer content using OpenAI."""
    logger.info("Example: Generating partner offer content with OpenAI")

    # Initialize content generator
    generator = ContentGenerator()

    # Example persona and signals
    persona_id = 4  # Savings Builder
    signals = {
        "savings": {
            "net_inflow_30d": 250.00,
            "emergency_fund_coverage_30d": 2.5,
            "savings_growth_rate_30d": 5.2,
        },
    }

    # Get a partner offer from catalog
    template_offer = PARTNER_OFFER_CATALOG[3]  # High-yield savings offer

    # Generate content using OpenAI (with fallback to template)
    content = generator.generate_partner_offer_content(
        template_offer,
        persona_id,
        signals,
        use_openai=True,  # Set to False to use template only
    )

    logger.info(f"Generated content:\n{content}")
    return content


def example_openai_client_direct():
    """Example: Direct usage of OpenAI client."""
    logger.info("Example: Direct OpenAI client usage")

    # Get OpenAI client
    client = get_openai_client()

    if not client:
        logger.warning("OpenAI client not available. Set OPENAI_API_KEY environment variable.")
        return None

    # Example prompt
    prompt = """Generate a brief educational tip about credit card utilization.

    Requirements:
    - Write in plain language
    - Keep it empowering (not judgmental)
    - Length: 2-3 sentences

    Generate the tip:"""

    # Generate content
    persona_id = 1
    signals = {
        "credit": {
            "high_utilization_cards_30d": [
                {"account_name": "Visa ending in 4523", "utilization": 0.68}
            ],
        },
    }

    content = client.generate_content(
        prompt=prompt,
        persona_id=persona_id,
        signals=signals,
        use_cache=True,
    )

    if content:
        logger.info(f"Generated content:\n{content}")
    else:
        logger.warning("Failed to generate content (may fall back to templates)")

    return content


def example_tone_validation():
    """Example: Validate tone of recommendation text."""
    logger.info("Example: Tone validation")

    # Get OpenAI client
    client = get_openai_client()

    if not client:
        logger.warning("OpenAI client not available. Set OPENAI_API_KEY environment variable.")
        return None

    # Example text (should be empowering)
    good_text = (
        "We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). "
        "Bringing this below 30% could improve your credit score and reduce interest charges of $87/month."
    )

    # Example text (should be flagged as judgmental)
    bad_text = (
        "You're overspending on credit cards! Your utilization is way too high and you're wasting money on interest. "
        "You need to be more responsible with your spending."
    )

    # Validate tone
    good_score = client.validate_tone(good_text)
    bad_score = client.validate_tone(bad_text)

    logger.info(f"Tone scores:")
    logger.info(f"  Good text (empowering): {good_score}/10")
    logger.info(f"  Bad text (judgmental): {bad_score}/10")

    return {"good_score": good_score, "bad_score": bad_score}


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("OpenAI features will be disabled - templates will be used instead.")
        print()

    # Run examples
    print("=" * 60)
    print("Example 1: Generate education content with OpenAI")
    print("=" * 60)
    example_openai_education_content()

    print("\n" + "=" * 60)
    print("Example 2: Generate partner offer content with OpenAI")
    print("=" * 60)
    example_openai_partner_offer_content()

    print("\n" + "=" * 60)
    print("Example 3: Direct OpenAI client usage")
    print("=" * 60)
    example_openai_client_direct()

    print("\n" + "=" * 60)
    print("Example 4: Tone validation")
    print("=" * 60)
    example_tone_validation()


