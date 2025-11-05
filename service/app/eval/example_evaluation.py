"""Example usage of evaluation service."""

import logging
from sqlalchemy.orm import Session

from app.eval.metrics import EvaluationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_evaluation(db_session: Session):
    """Example of calculating evaluation metrics."""

    # Initialize evaluation service
    eval_service = EvaluationService(db_session)

    # Calculate all metrics
    logger.info("Calculating all evaluation metrics...")
    all_metrics = eval_service.calculate_all_metrics()

    print("=" * 80)
    print("EVALUATION METRICS")
    print("=" * 80)

    # Coverage Metrics
    print("\n## Coverage Metrics")
    coverage = all_metrics["coverage"]
    print(f"Total Users: {coverage['total_users']}")
    print(f"Users with Persona: {coverage['users_with_persona_count']} ({coverage['users_with_persona_percent']}%)")
    print(f"Users with ≥3 Behaviors: {coverage['users_with_behaviors_count']} ({coverage['users_with_behaviors_percent']}%)")
    print(f"Users with Both: {coverage['users_with_both_count']} ({coverage['users_with_both_percent']}%)")

    # Explainability Metrics
    print("\n## Explainability Metrics")
    explainability = all_metrics["explainability"]
    print(f"Total Recommendations: {explainability['total_recommendations']}")
    print(f"Recommendations with Rationales: {explainability['recommendations_with_rationales_count']} ({explainability['recommendations_with_rationales_percent']}%)")
    print(f"Rationales with Data Points: {explainability['rationales_with_data_points_count']} ({explainability['rationales_with_data_points_percent']}%)")
    print(f"Average Rationale Quality Score: {explainability['rationale_quality_score']}/10")

    # Relevance Metrics
    print("\n## Relevance Metrics")
    relevance = all_metrics["relevance"]
    print(f"Education Items: {relevance['total_education_items']}")
    print(f"Education Items Matching Persona: {relevance['education_items_matching_persona']} ({relevance['education_persona_fit_percent']}%)")
    print(f"Partner Offers: {relevance['total_partner_offers']}")
    print(f"Partner Offers Matching Persona: {relevance['partner_offers_matching_persona']} ({relevance['partner_offer_persona_fit_percent']}%)")

    # Latency Metrics
    print("\n## Latency Metrics")
    latency = all_metrics["latency"]
    print(f"Total Recommendations with Latency Data: {latency['total_recommendations']}")
    print(f"P50 Latency: {latency['recommendation_generation_latency_p50']} ms")
    print(f"P95 Latency: {latency['recommendation_generation_latency_p95']} ms")
    print(f"P99 Latency: {latency['recommendation_generation_latency_p99']} ms")
    print(f"Mean Latency: {latency['recommendation_generation_latency_mean']} ms")
    print(f"Min Latency: {latency['recommendation_generation_latency_min']} ms")
    print(f"Max Latency: {latency['recommendation_generation_latency_max']} ms")
    print(f"Recommendations within 5s: {latency['recommendations_within_target']} ({latency['recommendations_within_target_percent']}%)")

    # Fairness Metrics
    print("\n## Fairness Metrics")
    fairness = all_metrics["fairness"]
    print(f"Persona Balance Score: {fairness['persona_balance_score']}/1.0")
    print("\nPersona Distribution:")
    for persona_id, dist in fairness['persona_distribution'].items():
        print(f"  Persona {persona_id}:")
        print(f"    Recommendations: {dist['recommendations_count']} ({dist['recommendations_percent']}%)")
        print(f"    Users: {dist['users_count']} ({dist['users_percent']}%)")

    print("\nSignal Detection by Persona:")
    for persona_id, detection in fairness['signal_detection_by_persona'].items():
        print(f"  Persona {persona_id}:")
        print(f"    Avg Behaviors Detected: {detection['avg_behaviors_detected']}")
        print(f"    Profiles Count: {detection['profiles_count']}")

    print(f"\nCalculated at: {all_metrics['calculated_at']}")

    # Calculate individual metrics
    print("\n" + "=" * 80)
    print("INDIVIDUAL METRIC CALCULATIONS")
    print("=" * 80)

    # Coverage only
    print("\n### Coverage Metrics Only")
    coverage_only = eval_service.calculate_coverage_metrics()
    print(f"Users with Persona: {coverage_only['users_with_persona_percent']}%")

    # Explainability only
    print("\n### Explainability Metrics Only")
    explainability_only = eval_service.calculate_explainability_metrics()
    print(f"Recommendations with Rationales: {explainability_only['recommendations_with_rationales_percent']}%")

    # Relevance only
    print("\n### Relevance Metrics Only")
    relevance_only = eval_service.calculate_relevance_metrics()
    print(f"Education-Persona Fit: {relevance_only['education_persona_fit_percent']}%")

    # Latency only
    print("\n### Latency Metrics Only")
    latency_only = eval_service.calculate_latency_metrics()
    print(f"P95 Latency: {latency_only['recommendation_generation_latency_p95']} ms")

    # Fairness only
    print("\n### Fairness Metrics Only")
    fairness_only = eval_service.calculate_fairness_metrics()
    print(f"Persona Balance Score: {fairness_only['persona_balance_score']}")

    return all_metrics


if __name__ == "__main__":
    # This would typically be called with a database session
    # from app.database import get_db_session
    # db_session = get_db_session()
    # example_evaluation(db_session)
    print("Example evaluation service usage. Provide a database session to run.")
    print("\nUsage:")
    print("  from app.eval.metrics import EvaluationService")
    print("  eval_service = EvaluationService(db_session)")
    print("  metrics = eval_service.calculate_all_metrics()")



