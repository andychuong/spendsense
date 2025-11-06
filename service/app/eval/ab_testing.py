"""A/B testing framework for RAG vs Catalog recommendations."""

import hashlib
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ABTestConfig:
    """Configuration for A/B testing."""
    
    def __init__(
        self,
        test_name: str = "rag_vs_catalog",
        variants: Dict[str, str] = None,
        rollout_percentage: float = 0.10,  # 10% default
        enabled: bool = True,
    ):
        """
        Initialize A/B test configuration.
        
        Args:
            test_name: Name of the A/B test
            variants: Dictionary of variant names to generation methods
            rollout_percentage: Percentage of users in test (0.0-1.0)
            enabled: Whether A/B test is enabled
        """
        self.test_name = test_name
        self.variants = variants or {
            "control": "catalog",
            "variant_a": "rag",
        }
        self.rollout_percentage = rollout_percentage
        self.enabled = enabled


class ABTester:
    """
    A/B testing framework for recommendation generation.
    
    Assigns users to test variants and tracks metrics for comparison.
    
    Example:
        ```python
        ab_tester = ABTester(config=ABTestConfig(rollout_percentage=0.10))
        
        # Assign user to variant
        variant = ab_tester.assign_variant(user_id)
        
        # Generate recommendations using assigned variant
        if variant == "control":
            recommendations = generate_catalog(user_id)
        elif variant == "variant_a":
            recommendations = generate_rag(user_id)
        
        # Track metrics
        ab_tester.track_generation(user_id, variant, recommendations)
        
        # Get comparison metrics
        metrics = ab_tester.get_metrics()
        ```
    """
    
    def __init__(
        self,
        db_session: Optional[Session] = None,
        config: Optional[ABTestConfig] = None,
    ):
        """
        Initialize A/B tester.
        
        Args:
            db_session: Optional database session for persisting assignments
            config: A/B test configuration
        """
        self.db = db_session
        self.config = config or ABTestConfig()
        
        # In-memory storage for assignments and metrics (use database in production)
        self._assignments = {}  # user_id -> variant
        self._metrics = {variant: [] for variant in self.config.variants.keys()}
    
    def is_enabled(self) -> bool:
        """Check if A/B testing is enabled."""
        return self.config.enabled
    
    def assign_variant(self, user_id: str) -> str:
        """
        Assign user to a test variant.
        
        Uses consistent hashing to ensure users always get same variant.
        
        Args:
            user_id: User ID
        
        Returns:
            Variant name ("control" or "variant_a")
        """
        if not self.is_enabled():
            return "control"  # Default to control if test disabled
        
        # Check if already assigned
        if user_id in self._assignments:
            return self._assignments[user_id]
        
        # Use hash of user_id for consistent assignment
        hash_value = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
        
        # Determine if user is in test
        user_percentage = (hash_value % 100) / 100.0
        
        if user_percentage >= self.config.rollout_percentage:
            # User not in test, assign to control
            variant = "control"
        else:
            # User in test, assign to variant based on hash
            variant_count = len(self.config.variants)
            variant_index = (hash_value // 100) % variant_count
            variant = list(self.config.variants.keys())[variant_index]
        
        # Store assignment
        self._assignments[user_id] = variant
        
        logger.info(f"Assigned user {user_id} to variant: {variant}")
        return variant
    
    def get_variant(self, user_id: str) -> Optional[str]:
        """
        Get assigned variant for user (if already assigned).
        
        Args:
            user_id: User ID
        
        Returns:
            Variant name or None
        """
        return self._assignments.get(user_id)
    
    def track_generation(
        self,
        user_id: str,
        variant: str,
        generation_result: Dict[str, Any],
    ):
        """
        Track recommendation generation metrics.
        
        Args:
            user_id: User ID
            variant: Variant name
            generation_result: Result from recommendation generation
        """
        if variant not in self._metrics:
            logger.warning(f"Unknown variant: {variant}")
            return
        
        metrics = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "generation_time_ms": generation_result.get("generation_time_ms", 0),
            "recommendation_count": generation_result.get("total_recommendations", 0),
            "success": generation_result.get("success", True),
        }
        
        self._metrics[variant].append(metrics)
        logger.debug(f"Tracked generation for {user_id} in {variant}")
    
    def track_user_feedback(
        self,
        user_id: str,
        recommendation_id: str,
        rating: int,
        helpful: bool,
    ):
        """
        Track user feedback on recommendation.
        
        Args:
            user_id: User ID
            recommendation_id: Recommendation ID
            rating: User rating (1-5)
            helpful: Whether user found it helpful
        """
        variant = self.get_variant(user_id)
        if not variant:
            logger.warning(f"No variant assigned for user {user_id}")
            return
        
        # Find the generation metric to update
        for metric in self._metrics[variant]:
            if metric["user_id"] == user_id:
                if "feedback" not in metric:
                    metric["feedback"] = []
                
                metric["feedback"].append({
                    "recommendation_id": recommendation_id,
                    "rating": rating,
                    "helpful": helpful,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                break
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get comparison metrics for all variants.
        
        Returns:
            Dictionary with metrics for each variant
        """
        results = {}
        
        for variant, metrics_list in self._metrics.items():
            if not metrics_list:
                results[variant] = {
                    "sample_size": 0,
                    "avg_generation_time_ms": 0,
                    "success_rate": 0,
                    "avg_recommendation_count": 0,
                }
                continue
            
            # Calculate aggregates
            successful = [m for m in metrics_list if m.get("success", True)]
            
            avg_time = sum(m["generation_time_ms"] for m in successful) / len(successful) if successful else 0
            success_rate = len(successful) / len(metrics_list) if metrics_list else 0
            avg_count = sum(m["recommendation_count"] for m in successful) / len(successful) if successful else 0
            
            # Feedback metrics
            all_feedback = []
            for m in metrics_list:
                all_feedback.extend(m.get("feedback", []))
            
            avg_rating = sum(f["rating"] for f in all_feedback) / len(all_feedback) if all_feedback else 0
            helpful_rate = sum(1 for f in all_feedback if f["helpful"]) / len(all_feedback) if all_feedback else 0
            
            results[variant] = {
                "sample_size": len(metrics_list),
                "successful_generations": len(successful),
                "success_rate": success_rate,
                "avg_generation_time_ms": avg_time,
                "avg_recommendation_count": avg_count,
                "feedback_count": len(all_feedback),
                "avg_rating": avg_rating,
                "helpful_rate": helpful_rate,
            }
        
        # Calculate comparison
        if "control" in results and "variant_a" in results:
            control = results["control"]
            variant_a = results["variant_a"]
            
            results["comparison"] = {
                "variant_faster": variant_a["avg_generation_time_ms"] < control["avg_generation_time_ms"],
                "speed_improvement": (control["avg_generation_time_ms"] - variant_a["avg_generation_time_ms"]) / control["avg_generation_time_ms"] if control["avg_generation_time_ms"] > 0 else 0,
                "rating_improvement": variant_a.get("avg_rating", 0) - control.get("avg_rating", 0),
                "helpful_rate_improvement": variant_a.get("helpful_rate", 0) - control.get("helpful_rate", 0),
                "statistically_significant": self._check_significance(control, variant_a),
            }
        
        return results
    
    def _check_significance(self, control: Dict[str, Any], variant: Dict[str, Any]) -> bool:
        """
        Check if results are statistically significant.
        
        Simple check - in production, use proper statistical tests (t-test, chi-square, etc.)
        
        Args:
            control: Control metrics
            variant: Variant metrics
        
        Returns:
            True if significant, False otherwise
        """
        # Require minimum sample size
        if control["sample_size"] < 30 or variant["sample_size"] < 30:
            return False
        
        # Require meaningful difference in rating (if available)
        if "avg_rating" in variant and "avg_rating" in control:
            rating_diff = abs(variant["avg_rating"] - control["avg_rating"])
            if rating_diff < 0.3:  # Less than 0.3 points difference
                return False
        
        return True
    
    def get_summary(self) -> str:
        """
        Get human-readable summary of A/B test results.
        
        Returns:
            Summary string
        """
        metrics = self.get_metrics()
        
        lines = [
            "=" * 80,
            f"A/B Test Summary: {self.config.test_name}",
            "=" * 80,
        ]
        
        for variant, stats in metrics.items():
            if variant == "comparison":
                continue
            
            generation_method = self.config.variants.get(variant, variant)
            
            lines.extend([
                f"\n{variant.upper()} ({generation_method}):",
                f"  Sample Size: {stats['sample_size']}",
                f"  Success Rate: {stats['success_rate']:.1%}",
                f"  Avg Generation Time: {stats['avg_generation_time_ms']:.0f}ms",
                f"  Avg Recommendations: {stats['avg_recommendation_count']:.1f}",
                f"  Avg Rating: {stats['avg_rating']:.2f}/5.0",
                f"  Helpful Rate: {stats['helpful_rate']:.1%}",
            ])
        
        if "comparison" in metrics:
            comp = metrics["comparison"]
            lines.extend([
                "\nCOMPARISON:",
                f"  Variant Faster: {'Yes' if comp['variant_faster'] else 'No'}",
                f"  Speed Improvement: {comp['speed_improvement']:+.1%}",
                f"  Rating Improvement: {comp['rating_improvement']:+.2f} points",
                f"  Helpful Rate Improvement: {comp['helpful_rate_improvement']:+.1%}",
                f"  Statistically Significant: {'Yes' if comp['statistically_significant'] else 'No (need more data)'}",
            ])
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_recommendation(self) -> str:
        """
        Get recommendation on whether to rollout variant.
        
        Returns:
            Recommendation string
        """
        metrics = self.get_metrics()
        
        if "comparison" not in metrics:
            return "Need data from both control and variant to make recommendation."
        
        comp = metrics["comparison"]
        
        if not comp["statistically_significant"]:
            return "⏳ Need more data - results not yet statistically significant."
        
        if comp["rating_improvement"] > 0.5 and comp["helpful_rate_improvement"] > 0.1:
            return "✅ RECOMMEND ROLLOUT - Variant shows significant improvement in user satisfaction."
        elif comp["rating_improvement"] > 0:
            return "⚠️  CAUTIOUS ROLLOUT - Variant shows improvement but not dramatic. Consider expanding to 50%."
        else:
            return "❌ DO NOT ROLLOUT - Variant does not show improvement over control."
    
    def reset(self):
        """Reset all assignments and metrics."""
        self._assignments = {}
        self._metrics = {variant: [] for variant in self.config.variants.keys()}
        logger.info("A/B test data reset")


def create_ab_tester(
    db_session: Optional[Session] = None,
    rollout_percentage: float = 0.10,
    enabled: bool = True,
) -> ABTester:
    """
    Factory function to create A/B tester.
    
    Args:
        db_session: Database session
        rollout_percentage: Percentage of users in test (0.0-1.0)
        enabled: Whether A/B test is enabled
    
    Returns:
        ABTester instance
    """
    config = ABTestConfig(
        rollout_percentage=rollout_percentage,
        enabled=enabled,
    )
    
    return ABTester(db_session=db_session, config=config)

