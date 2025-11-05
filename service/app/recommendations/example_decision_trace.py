"""Example usage of decision trace generation service."""

import uuid
from datetime import datetime

from app.recommendations.decision_trace import DecisionTraceGenerator


def example_decision_trace():
    """Example of creating a decision trace."""

    # Initialize decision trace generator
    trace_generator = DecisionTraceGenerator()

    # Example persona assignment info
    persona_assignment_info = trace_generator.create_persona_assignment_info(
        persona_id=1,
        persona_name="High Utilization",
        criteria_met=[
            "Credit card utilization ≥50%",
            "Interest charges detected",
        ],
        priority=1,
        rationale="High credit card utilization detected. Credit card utilization at 68.5% (cards: Visa ending in 4523). Interest charges totaling $87.50 on Visa ending in 4523.",
        persona_changed=False,
    )

    # Example signals
    signals_30d = {
        "subscriptions": {
            "subscription_count": 2,
            "total_recurring_spend": 45.50,
        },
        "savings": {
            "savings_growth_rate_percent": 1.5,
        },
        "credit": {
            "critical_utilization_cards": [
                {
                    "account_name": "Visa ending in 4523",
                    "utilization_percent": 68.5,
                }
            ],
            "cards_with_interest": [
                {
                    "account_name": "Visa ending in 4523",
                    "interest_charges": {
                        "total_interest_charges": 87.50,
                    },
                }
            ],
        },
        "income": {
            "cash_flow_buffer_months": 0.5,
        },
    }

    signals_180d = {
        "subscriptions": {
            "subscription_count": 4,
            "total_recurring_spend": 120.00,
        },
        "savings": {
            "savings_growth_rate_percent": 2.5,
        },
        "credit": {
            "critical_utilization_cards": [
                {
                    "account_name": "Visa ending in 4523",
                    "utilization_percent": 68.5,
                }
            ],
            "cards_with_interest": [
                {
                    "account_name": "Visa ending in 4523",
                    "interest_charges": {
                        "total_interest_charges": 87.50,
                    },
                }
            ],
        },
        "income": {
            "cash_flow_buffer_months": 0.5,
        },
    }

    # Example guardrails info
    guardrails_info = trace_generator.create_guardrails_info(
        consent_status=True,
        consent_check_timestamp=datetime.utcnow().isoformat() + "Z",
        eligibility_status=True,
        eligibility_explanation=None,
        eligibility_details={},
        tone_valid=True,
        tone_score=8.5,
        tone_explanation="Tone validation passed. Empowering language detected.",
        disclaimer_present=True,
        disclaimer_text="This is educational content, not financial advice. Consult a licensed advisor for personalized guidance.",
    )

    # Create decision trace
    decision_trace = trace_generator.create_decision_trace(
        user_id=uuid.uuid4(),
        recommendation_id=uuid.uuid4(),
        recommendation_type="education",
        persona_id=1,
        persona_name="High Utilization",
        persona_assignment_info=persona_assignment_info,
        signals_30d=signals_30d,
        signals_180d=signals_180d,
        guardrails=guardrails_info,
        generation_time_ms=2450.5,
        recommendation_metadata={
            "title": "How to Lower Your Credit Card Utilization",
            "content_preview": "Credit card utilization is a key factor in your credit score...",
            "rationale_preview": "We noticed your Visa ending in 4523 is at 68% utilization...",
        },
    )

    # Generate human-readable trace
    markdown_trace = trace_generator.generate_human_readable_trace(
        decision_trace,
        format="markdown",
    )

    print("=" * 80)
    print("DECISION TRACE (JSON)")
    print("=" * 80)
    import json
    print(json.dumps(decision_trace, indent=2))

    print("\n" + "=" * 80)
    print("DECISION TRACE (MARKDOWN)")
    print("=" * 80)
    print(markdown_trace)

    return decision_trace, markdown_trace


if __name__ == "__main__":
    example_decision_trace()



