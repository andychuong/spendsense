"""Evaluation service for calculating system performance and fairness metrics."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import statistics

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

# Try to import models from backend
try:
    from backend.app.models.user import User
    from backend.app.models.user_profile import UserProfile
    from backend.app.models.user_persona_assignment import UserPersonaAssignment
    from backend.app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.user import User
    from app.models.user_profile import UserProfile
    from app.models.user_persona_assignment import UserPersonaAssignment
    from app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for calculating evaluation metrics for the recommendation system."""

    def __init__(self, db_session: Session):
        """
        Initialize evaluation service.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def calculate_coverage_metrics(self) -> Dict[str, Any]:
        """
        Calculate coverage metrics.

        Returns:
            Dictionary with coverage metrics:
            - users_with_persona_percent: % of users with assigned persona
            - users_with_behaviors_percent: % of users with ≥3 detected behaviors
            - users_with_both_percent: % of users with both persona and ≥3 behaviors
            - total_users: Total number of users
            - users_with_persona_count: Count of users with persona
            - users_with_behaviors_count: Count of users with ≥3 behaviors
            - users_with_both_count: Count of users with both
        """
        logger.info("Calculating coverage metrics")

        # Get total users (excluding operators and admins)
        total_users = self.db.query(User).filter(
            User.role == "user"
        ).count()

        if total_users == 0:
            return {
                "users_with_persona_percent": 0.0,
                "users_with_behaviors_percent": 0.0,
                "users_with_both_percent": 0.0,
                "total_users": 0,
                "users_with_persona_count": 0,
                "users_with_behaviors_count": 0,
                "users_with_both_count": 0,
            }

        # Get users with assigned persona from UserPersonaAssignment
        # Count distinct users who have persona assignments
        from sqlalchemy import distinct
        users_with_persona = self.db.query(
            func.count(distinct(UserPersonaAssignment.user_id))
        ).join(
            User, UserPersonaAssignment.user_id == User.user_id
        ).filter(
            User.role == "user"
        ).scalar() or 0

        # Get users with ≥3 detected behaviors
        users_with_behaviors = 0
        users_with_both = 0

        profiles = self.db.query(UserProfile).join(
            User, UserProfile.user_id == User.user_id
        ).filter(
            User.role == "user"
        ).all()

        for profile in profiles:
            # Count behaviors from signals
            behavior_count = self._count_behaviors(profile.signals_30d or {}, profile.signals_180d or {})

            if behavior_count >= 3:
                users_with_behaviors += 1
                # Check if user also has persona assigned
                has_persona = self.db.query(UserPersonaAssignment).filter(
                    UserPersonaAssignment.user_id == profile.user_id
                ).first() is not None
                if has_persona:
                    users_with_both += 1

        # Calculate percentages
        users_with_persona_percent = (users_with_persona / total_users) * 100 if total_users > 0 else 0.0
        users_with_behaviors_percent = (users_with_behaviors / total_users) * 100 if total_users > 0 else 0.0
        users_with_both_percent = (users_with_both / total_users) * 100 if total_users > 0 else 0.0

        return {
            "users_with_persona_percent": round(users_with_persona_percent, 2),
            "users_with_behaviors_percent": round(users_with_behaviors_percent, 2),
            "users_with_both_percent": round(users_with_both_percent, 2),
            "total_users": total_users,
            "users_with_persona_count": users_with_persona,
            "users_with_behaviors_count": users_with_behaviors,
            "users_with_both_count": users_with_both,
        }

    def _count_behaviors(self, signals_30d: Dict[str, Any], signals_180d: Dict[str, Any]) -> int:
        """
        Count number of detected behaviors from signals.

        Args:
            signals_30d: 30-day signals
            signals_180d: 180-day signals

        Returns:
            Number of behaviors detected (0-4: subscriptions, savings, credit, income)
        """
        behaviors = 0

        # Check subscriptions
        if signals_30d.get("subscriptions", {}).get("subscription_count", 0) > 0 or \
           signals_180d.get("subscriptions", {}).get("subscription_count", 0) > 0:
            behaviors += 1

        # Check savings
        if signals_30d.get("savings", {}).get("net_inflow_monthly") is not None or \
           signals_180d.get("savings", {}).get("net_inflow_monthly") is not None or \
           signals_30d.get("savings", {}).get("savings_growth_rate_percent") is not None or \
           signals_180d.get("savings", {}).get("savings_growth_rate_percent") is not None:
            behaviors += 1

        # Check credit
        if signals_30d.get("credit", {}).get("high_utilization_cards") or \
           signals_180d.get("credit", {}).get("high_utilization_cards") or \
           signals_30d.get("credit", {}).get("critical_utilization_cards") or \
           signals_180d.get("credit", {}).get("critical_utilization_cards") or \
           signals_30d.get("credit", {}).get("cards_with_interest") or \
           signals_180d.get("credit", {}).get("cards_with_interest"):
            behaviors += 1

        # Check income
        if signals_30d.get("income", {}).get("income_patterns", {}).get("payment_frequency") or \
           signals_180d.get("income", {}).get("income_patterns", {}).get("payment_frequency") or \
           signals_30d.get("income", {}).get("cash_flow_buffer_months") is not None or \
           signals_180d.get("income", {}).get("cash_flow_buffer_months") is not None:
            behaviors += 1

        return behaviors

    def calculate_explainability_metrics(self) -> Dict[str, Any]:
        """
        Calculate explainability metrics.

        Returns:
            Dictionary with explainability metrics:
            - recommendations_with_rationales_percent: % of recommendations with plain-language rationales
            - rationales_with_data_points_percent: % of rationales citing specific data points
            - total_recommendations: Total number of recommendations
            - recommendations_with_rationales_count: Count of recommendations with rationales
            - rationales_with_data_points_count: Count of rationales with data points
            - rationale_quality_score: Average rationale quality score (0-10)
        """
        logger.info("Calculating explainability metrics")

        # Get all recommendations
        recommendations = self.db.query(Recommendation).all()
        total_recommendations = len(recommendations)

        if total_recommendations == 0:
            return {
                "recommendations_with_rationales_percent": 0.0,
                "rationales_with_data_points_percent": 0.0,
                "total_recommendations": 0,
                "recommendations_with_rationales_count": 0,
                "rationales_with_data_points_count": 0,
                "rationale_quality_score": 0.0,
            }

        recommendations_with_rationales = 0
        rationales_with_data_points = 0
        quality_scores = []

        for rec in recommendations:
            # Check if rationale exists and is not empty
            if rec.rationale and len(rec.rationale.strip()) > 0:
                recommendations_with_rationales += 1

                # Check if rationale cites specific data points
                if self._rationale_has_data_points(rec.rationale):
                    rationales_with_data_points += 1

                # Calculate rationale quality score
                quality_score = self._calculate_rationale_quality(rec.rationale)
                quality_scores.append(quality_score)

        # Calculate percentages
        recommendations_with_rationales_percent = (
            (recommendations_with_rationales / total_recommendations) * 100
            if total_recommendations > 0 else 0.0
        )
        rationales_with_data_points_percent = (
            (rationales_with_data_points / recommendations_with_rationales) * 100
            if recommendations_with_rationales > 0 else 0.0
        )
        rationale_quality_score = (
            statistics.mean(quality_scores) if quality_scores else 0.0
        )

        return {
            "recommendations_with_rationales_percent": round(recommendations_with_rationales_percent, 2),
            "rationales_with_data_points_percent": round(rationales_with_data_points_percent, 2),
            "total_recommendations": total_recommendations,
            "recommendations_with_rationales_count": recommendations_with_rationales,
            "rationales_with_data_points_count": rationales_with_data_points,
            "rationale_quality_score": round(rationale_quality_score, 2),
        }

    def _rationale_has_data_points(self, rationale: str) -> bool:
        """
        Check if rationale cites specific data points.

        Args:
            rationale: Rationale text

        Returns:
            True if rationale contains data point citations
        """
        if not rationale:
            return False

        rationale_lower = rationale.lower()

        # Check for account citations (ending in, last 4 digits)
        if "ending in" in rationale_lower or "last 4" in rationale_lower or "last four" in rationale_lower:
            return True

        # Check for currency citations ($, amounts)
        if "$" in rationale and any(char.isdigit() for char in rationale):
            return True

        # Check for percentage citations (%)
        if "%" in rationale and any(char.isdigit() for char in rationale):
            return True

        # Check for date citations (month names, dates)
        months = ["january", "february", "march", "april", "may", "june",
                  "july", "august", "september", "october", "november", "december"]
        if any(month in rationale_lower for month in months):
            return True

        # Check for number citations (counts, amounts)
        # Look for patterns like "3 subscriptions", "5 cards", etc.
        import re
        number_patterns = [
            r'\d+\s+(subscriptions?|cards?|merchants?|accounts?)',
            r'\d+\s+(days?|months?|weeks?)',
        ]
        for pattern in number_patterns:
            if re.search(pattern, rationale_lower):
                return True

        return False

    def _calculate_rationale_quality(self, rationale: str) -> float:
        """
        Calculate rationale quality score (0-10).

        Simple automated scoring based on:
        - Length (longer is better, up to a point)
        - Data point citations (presence of $, %, dates, account numbers)
        - Plain language indicators (avoiding jargon)

        Args:
            rationale: Rationale text

        Returns:
            Quality score (0-10)
        """
        if not rationale:
            return 0.0

        score = 0.0

        # Length score (0-3 points)
        length = len(rationale.strip())
        if length >= 100:
            score += 3.0
        elif length >= 50:
            score += 2.0
        elif length >= 20:
            score += 1.0

        # Data point citations (0-4 points)
        if self._rationale_has_data_points(rationale):
            score += 4.0

        # Plain language check (0-3 points)
        # Check for avoiding jargon
        jargon_words = ["leverage", "optimize", "synergize", "utilize", "facilitate", "implementation"]
        rationale_lower = rationale.lower()
        jargon_count = sum(1 for word in jargon_words if word in rationale_lower)

        if jargon_count == 0:
            score += 3.0
        elif jargon_count <= 1:
            score += 2.0
        elif jargon_count <= 2:
            score += 1.0

        # Cap at 10
        return min(score, 10.0)

    def calculate_relevance_metrics(self) -> Dict[str, Any]:
        """
        Calculate relevance metrics.

        Returns:
            Dictionary with relevance metrics:
            - education_persona_fit_percent: % of education items matching persona
            - partner_offer_persona_fit_percent: % of partner offers matching persona
            - total_education_items: Total education recommendations
            - total_partner_offers: Total partner offer recommendations
            - education_items_matching_persona: Count of education items matching persona
            - partner_offers_matching_persona: Count of partner offers matching persona
        """
        logger.info("Calculating relevance metrics")

        # Get all recommendations with their decision traces
        recommendations = self.db.query(Recommendation).join(
            UserProfile, Recommendation.user_id == UserProfile.user_id
        ).all()

        education_items = [r for r in recommendations if r.type == RecommendationType.EDUCATION]
        partner_offers = [r for r in recommendations if r.type == RecommendationType.PARTNER_OFFER]

        total_education_items = len(education_items)
        total_partner_offers = len(partner_offers)

        # Check education-persona fit
        education_items_matching_persona = 0
        for rec in education_items:
            if self._check_education_persona_fit(rec):
                education_items_matching_persona += 1

        # Check partner offer-persona fit
        partner_offers_matching_persona = 0
        for rec in partner_offers:
            if self._check_partner_offer_persona_fit(rec):
                partner_offers_matching_persona += 1

        # Calculate percentages
        education_persona_fit_percent = (
            (education_items_matching_persona / total_education_items) * 100
            if total_education_items > 0 else 0.0
        )
        partner_offer_persona_fit_percent = (
            (partner_offers_matching_persona / total_partner_offers) * 100
            if total_partner_offers > 0 else 0.0
        )

        return {
            "education_persona_fit_percent": round(education_persona_fit_percent, 2),
            "partner_offer_persona_fit_percent": round(partner_offer_persona_fit_percent, 2),
            "total_education_items": total_education_items,
            "total_partner_offers": total_partner_offers,
            "education_items_matching_persona": education_items_matching_persona,
            "partner_offers_matching_persona": partner_offers_matching_persona,
        }

    def _check_education_persona_fit(self, recommendation: Recommendation) -> bool:
        """
        Check if education item matches user's persona.

        Args:
            recommendation: Recommendation object

        Returns:
            True if education item matches persona
        """
        if not recommendation.decision_trace:
            return False

        trace = recommendation.decision_trace
        persona_id = trace.get("persona_assignment", {}).get("persona_id")

        if not persona_id:
            return False

        # Get user's assigned persona from UserPersonaAssignment
        assignment = self.db.query(UserPersonaAssignment).filter(
            UserPersonaAssignment.user_id == recommendation.user_id
        ).order_by(UserPersonaAssignment.assigned_at.asc()).first()

        if not assignment:
            return False

        # Check if recommendation's decision trace persona matches user's assigned persona
        return persona_id == assignment.persona_id

    def _check_partner_offer_persona_fit(self, recommendation: Recommendation) -> bool:
        """
        Check if partner offer matches user's persona.

        Args:
            recommendation: Recommendation object

        Returns:
            True if partner offer matches persona
        """
        # Same logic as education items
        return self._check_education_persona_fit(recommendation)

    def calculate_latency_metrics(self) -> Dict[str, Any]:
        """
        Calculate latency metrics.

        Returns:
            Dictionary with latency metrics:
            - recommendation_generation_latency_p50: p50 latency in ms
            - recommendation_generation_latency_p95: p95 latency in ms
            - recommendation_generation_latency_p99: p99 latency in ms
            - recommendation_generation_latency_mean: Mean latency in ms
            - recommendation_generation_latency_max: Max latency in ms
            - recommendation_generation_latency_min: Min latency in ms
            - recommendations_within_target: Count of recommendations generated within 5 seconds
            - recommendations_within_target_percent: % of recommendations within 5 seconds
            - total_recommendations: Total recommendations with latency data
        """
        logger.info("Calculating latency metrics")

        # Get all recommendations with decision traces
        recommendations = self.db.query(Recommendation).filter(
            Recommendation.decision_trace.isnot(None)
        ).all()

        latencies = []
        target_threshold_ms = 5000  # 5 seconds in milliseconds

        for rec in recommendations:
            if rec.decision_trace:
                latency_ms = rec.decision_trace.get("generation_time_ms")
                if latency_ms is not None:
                    latencies.append(float(latency_ms))

        total_recommendations = len(latencies)

        if total_recommendations == 0:
            return {
                "recommendation_generation_latency_p50": 0.0,
                "recommendation_generation_latency_p95": 0.0,
                "recommendation_generation_latency_p99": 0.0,
                "recommendation_generation_latency_mean": 0.0,
                "recommendation_generation_latency_max": 0.0,
                "recommendation_generation_latency_min": 0.0,
                "recommendations_within_target": 0,
                "recommendations_within_target_percent": 0.0,
                "total_recommendations": 0,
            }

        # Calculate percentiles
        sorted_latencies = sorted(latencies)

        def percentile(data, p):
            """Calculate percentile value."""
            if not data:
                return 0.0
            n = len(data)
            k = (n - 1) * p
            f = int(k)
            c = k - f
            if f + 1 < n:
                return data[f] + c * (data[f + 1] - data[f])
            return data[f]

        p50 = percentile(sorted_latencies, 0.50)
        p95 = percentile(sorted_latencies, 0.95)
        p99 = percentile(sorted_latencies, 0.99)

        mean_latency = statistics.mean(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)

        # Count recommendations within target (5 seconds)
        recommendations_within_target = sum(1 for l in latencies if l <= target_threshold_ms)
        recommendations_within_target_percent = (
            (recommendations_within_target / total_recommendations) * 100
            if total_recommendations > 0 else 0.0
        )

        return {
            "recommendation_generation_latency_p50": round(p50, 2),
            "recommendation_generation_latency_p95": round(p95, 2),
            "recommendation_generation_latency_p99": round(p99, 2),
            "recommendation_generation_latency_mean": round(mean_latency, 2),
            "recommendation_generation_latency_max": round(max_latency, 2),
            "recommendation_generation_latency_min": round(min_latency, 2),
            "recommendations_within_target": recommendations_within_target,
            "recommendations_within_target_percent": round(recommendations_within_target_percent, 2),
            "total_recommendations": total_recommendations,
        }

    def calculate_fairness_metrics(self) -> Dict[str, Any]:
        """
        Calculate fairness metrics.

        Note: This is a simplified implementation. Full demographic parity
        requires demographic data in the user model (e.g., age, gender, race).
        For MVP, we check recommendation distribution across personas.

        Returns:
            Dictionary with fairness metrics:
            - persona_distribution: Distribution of recommendations across personas
            - recommendations_per_persona: Count of recommendations per persona
            - persona_balance_score: Balance score (0-1, 1 = perfectly balanced)
            - signal_detection_by_persona: Signal detection accuracy by persona
        """
        logger.info("Calculating fairness metrics")

        # Get all recommendations with decision traces
        recommendations = self.db.query(Recommendation).filter(
            Recommendation.decision_trace.isnot(None)
        ).all()

        # Count recommendations by persona
        persona_counts = Counter()
        persona_user_counts = Counter()

        for rec in recommendations:
            if rec.decision_trace:
                persona_id = rec.decision_trace.get("persona_assignment", {}).get("persona_id")
                if persona_id:
                    persona_counts[persona_id] += 1

        # Get user distribution by persona from UserPersonaAssignment
        assignments = self.db.query(UserPersonaAssignment).all()
        for assignment in assignments:
            persona_user_counts[assignment.persona_id] += 1

        # Calculate persona distribution percentages
        total_recommendations = sum(persona_counts.values())
        total_users = sum(persona_user_counts.values())

        persona_distribution = {}
        recommendations_per_persona = {}

        for persona_id in range(1, 6):
            count = persona_counts.get(persona_id, 0)
            user_count = persona_user_counts.get(persona_id, 0)

            recommendations_per_persona[persona_id] = count

            rec_percent = (
                (count / total_recommendations) * 100
                if total_recommendations > 0 else 0.0
            )
            user_percent = (
                (user_count / total_users) * 100
                if total_users > 0 else 0.0
            )

            persona_distribution[persona_id] = {
                "recommendations_percent": round(rec_percent, 2),
                "users_percent": round(user_percent, 2),
                "recommendations_count": count,
                "users_count": user_count,
            }

        # Calculate balance score (how evenly distributed)
        # Lower variance = more balanced
        if total_recommendations > 0 and total_users > 0:
            rec_percentages = [v["recommendations_percent"] for v in persona_distribution.values()]
            user_percentages = [v["users_percent"] for v in persona_distribution.values()]

            # Calculate variance from expected distribution
            variances = []
            for rec_pct, user_pct in zip(rec_percentages, user_percentages):
                if user_pct > 0:
                    expected_rec_pct = user_pct
                    variance = abs(rec_pct - expected_rec_pct)
                    variances.append(variance)

            # Balance score: 1 - (normalized variance)
            # Perfect balance = 1.0
            if variances:
                avg_variance = statistics.mean(variances)
                # Normalize: assume max variance is 100 (if all recs go to one persona)
                normalized_variance = avg_variance / 100.0
                balance_score = max(0.0, 1.0 - normalized_variance)
            else:
                balance_score = 1.0
        else:
            balance_score = 0.0

        # Calculate signal detection by persona (simplified)
        signal_detection_by_persona = {}
        for persona_id in range(1, 6):
            # Get users with this persona assignment
            assignments_for_persona = self.db.query(UserPersonaAssignment).filter(
                UserPersonaAssignment.persona_id == persona_id
            ).all()
            
            # Get profiles for these users
            user_ids = [a.user_id for a in assignments_for_persona]
            profiles_for_persona = self.db.query(UserProfile).filter(
                UserProfile.user_id.in_(user_ids)
            ).all() if user_ids else []

            total_behaviors = 0
            total_profiles = len(profiles_for_persona)

            for profile in profiles_for_persona:
                behavior_count = self._count_behaviors(
                    profile.signals_30d or {},
                    profile.signals_180d or {}
                )
                total_behaviors += behavior_count

            avg_behaviors = (
                total_behaviors / total_profiles
                if total_profiles > 0 else 0.0
            )

            signal_detection_by_persona[persona_id] = {
                "avg_behaviors_detected": round(avg_behaviors, 2),
                "profiles_count": total_profiles,
            }

        return {
            "persona_distribution": persona_distribution,
            "recommendations_per_persona": recommendations_per_persona,
            "persona_balance_score": round(balance_score, 3),
            "signal_detection_by_persona": signal_detection_by_persona,
        }

    def calculate_all_metrics(self) -> Dict[str, Any]:
        """
        Calculate all evaluation metrics.

        Returns:
            Dictionary with all metrics:
            - coverage: Coverage metrics
            - explainability: Explainability metrics
            - relevance: Relevance metrics
            - latency: Latency metrics
            - fairness: Fairness metrics
            - calculated_at: Timestamp of calculation
        """
        logger.info("Calculating all evaluation metrics")

        coverage = self.calculate_coverage_metrics()
        explainability = self.calculate_explainability_metrics()
        relevance = self.calculate_relevance_metrics()
        latency = self.calculate_latency_metrics()
        fairness = self.calculate_fairness_metrics()

        return {
            "coverage": coverage,
            "explainability": explainability,
            "relevance": relevance,
            "latency": latency,
            "fairness": fairness,
            "calculated_at": datetime.utcnow().isoformat() + "Z",
        }

