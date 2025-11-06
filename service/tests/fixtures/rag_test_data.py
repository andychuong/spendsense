"""Test fixtures and sample data for RAG testing."""

import uuid
from typing import Dict, Any, List


# Sample user profiles for testing
SAMPLE_USERS = [
    {
        "id": uuid.uuid4(),
        "name": "High Utilization User",
        "personas": ["HIGH_UTILIZATION"],
        "signals_30d": {
            "credit": {
                "avg_utilization": 0.68,
                "total_credit_balance": 5200.00,
                "total_credit_limit": 7650.00,
                "cards_with_interest": ["card_1"],
                "high_utilization_cards": ["card_1"],
                "interest_charges_30d": 87.00,
                "min_payments_30d": 156.00,
            }
        },
        "signals_180d": {
            "credit": {
                "utilization_trend": "increasing",
                "balance_trend": "increasing",
            }
        },
        "expected_recommendations": [
            "debt_reduction",
            "balance_transfer",
            "credit_counseling",
        ],
    },
    {
        "id": uuid.uuid4(),
        "name": "Variable Income User",
        "personas": ["VARIABLE_INCOME_BUDGETER"],
        "signals_30d": {
            "income": {
                "payment_frequency": "irregular",
                "median_pay_gap_days": 52,
                "cash_flow_buffer_months": 0.6,
                "variable_income_detected": True,
            }
        },
        "signals_180d": {
            "income": {
                "income_volatility": "high",
            }
        },
        "expected_recommendations": [
            "emergency_fund",
            "income_smoothing",
            "budgeting_tools",
        ],
    },
    {
        "id": uuid.uuid4(),
        "name": "Subscription Heavy User",
        "personas": ["SUBSCRIPTION_HEAVY"],
        "signals_30d": {
            "subscriptions": {
                "subscription_count": 8,
                "total_recurring_spend": 127.00,
                "subscription_share_percent": 15.0,
                "inactive_subscriptions": 2,
            }
        },
        "signals_180d": {},
        "expected_recommendations": [
            "subscription_audit",
            "subscription_management",
            "spending_reduction",
        ],
    },
    {
        "id": uuid.uuid4(),
        "name": "Savings Builder User",
        "personas": ["SAVINGS_BUILDER"],
        "signals_30d": {
            "savings": {
                "net_inflow_monthly": 250.00,
                "savings_growth_rate_percent": 3.5,
                "emergency_fund_coverage_months": 2.1,
                "consistent_savings": True,
            },
            "credit": {
                "avg_utilization": 0.15,
            }
        },
        "signals_180d": {
            "savings": {
                "savings_trend": "growing",
            }
        },
        "expected_recommendations": [
            "high_yield_savings",
            "investment_education",
            "savings_optimization",
        ],
    },
    {
        "id": uuid.uuid4(),
        "name": "Balanced Budget User",
        "personas": ["BALANCED_BUDGET"],
        "signals_30d": {
            "credit": {
                "avg_utilization": 0.28,
            },
            "savings": {
                "net_inflow_monthly": 150.00,
            }
        },
        "signals_180d": {},
        "expected_recommendations": [
            "financial_optimization",
            "goal_setting",
        ],
    },
]


# Sample test scenarios for retrieval testing
SAMPLE_SCENARIOS = [
    {
        "id": "scenario_1",
        "content": "User reduced credit utilization from 85% to 30% in 6 months by using balance transfer and debt avalanche method",
        "type": "user_scenario",
        "persona": "HIGH_UTILIZATION",
        "outcome": "success",
        "metadata": {
            "starting_utilization": 0.85,
            "ending_utilization": 0.30,
            "timeframe_months": 6,
            "strategy": "balance_transfer_and_avalanche",
        }
    },
    {
        "id": "scenario_2",
        "content": "Variable income user built 3-month emergency fund by saving 30% of large payments",
        "type": "user_scenario",
        "persona": "VARIABLE_INCOME_BUDGETER",
        "outcome": "success",
        "metadata": {
            "starting_buffer_months": 0.5,
            "ending_buffer_months": 3.0,
            "savings_rate": 0.30,
        }
    },
    {
        "id": "scenario_3",
        "content": "User canceled 4 unused subscriptions, saving $68/month",
        "type": "user_scenario",
        "persona": "SUBSCRIPTION_HEAVY",
        "outcome": "success",
        "metadata": {
            "subscriptions_canceled": 4,
            "monthly_savings": 68.00,
        }
    },
]


# Sample education content for testing
SAMPLE_EDUCATION = [
    {
        "id": "edu_credit_util",
        "title": "Understanding Credit Utilization",
        "content": "Credit utilization is the ratio of your credit card balances to your credit limits. Keeping utilization below 30% helps maintain good credit scores.",
        "category": "credit",
        "personas": ["HIGH_UTILIZATION"],
    },
    {
        "id": "edu_emergency_fund",
        "title": "Building an Emergency Fund",
        "content": "An emergency fund provides financial stability during income gaps or unexpected expenses. Aim for 3-6 months of essential expenses.",
        "category": "savings",
        "personas": ["VARIABLE_INCOME_BUDGETER", "SAVINGS_BUILDER"],
    },
    {
        "id": "edu_subscription_audit",
        "title": "Auditing Your Subscriptions",
        "content": "Review subscriptions quarterly to identify unused services. The average person has 2-3 forgotten subscriptions costing $50-100/month.",
        "category": "subscriptions",
        "personas": ["SUBSCRIPTION_HEAVY"],
    },
]


# Expected retrieval results for test queries
TEST_QUERIES = [
    {
        "query": "high credit card debt strategies",
        "expected_doc_types": ["education", "strategy"],
        "expected_categories": ["debt", "credit"],
        "min_relevance_score": 0.5,
    },
    {
        "query": "emergency fund for variable income",
        "expected_doc_types": ["education", "strategy"],
        "expected_categories": ["savings", "income"],
        "min_relevance_score": 0.5,
    },
    {
        "query": "reducing subscription spending",
        "expected_doc_types": ["education", "strategy"],
        "expected_categories": ["subscriptions", "budgeting"],
        "min_relevance_score": 0.5,
    },
]


def get_sample_user_by_persona(persona: str) -> Dict[str, Any]:
    """Get sample user with specific persona."""
    for user in SAMPLE_USERS:
        if persona in user["personas"]:
            return user
    return None


def get_sample_users_for_testing() -> List[Dict[str, Any]]:
    """Get all sample users for testing."""
    return SAMPLE_USERS.copy()


def get_test_scenario_by_persona(persona: str) -> Dict[str, Any]:
    """Get test scenario for specific persona."""
    for scenario in SAMPLE_SCENARIOS:
        if scenario["persona"] == persona:
            return scenario
    return None

