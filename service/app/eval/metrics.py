"""Metrics collection and evaluation for RAG recommendations."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class RecommendationMetrics:
    """
    Collect and analyze metrics for recommendation quality.
    
    Tracks:
    - Generation performance (speed, success rate)
    - Content quality (citation rate, personalization)
    - User engagement (views, clicks, dismissals)
    - User feedback (ratings, helpful votes)
    - Operator decisions (approvals, rejections, edits)
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.generations = []
        self.user_interactions = []
        self.operator_decisions = []
    
    def track_generation(
        self,
        user_id: str,
        method: str,  # "rag" or "catalog"
        generation_result: Dict[str, Any],
    ):
        """
        Track recommendation generation.
        
        Args:
            user_id: User ID
            method: Generation method ("rag" or "catalog")
            generation_result: Result from generation
        """
        metrics = {
            "user_id": user_id,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
            "success": generation_result.get("success", False),
            "generation_time_ms": generation_result.get("generation_time_ms", 0),
            "recommendation_count": generation_result.get("total_recommendations", 0),
            "education_count": len(generation_result.get("education_recommendations", [])),
            "partner_offer_count": len(generation_result.get("partner_offers", [])),
        }
        
        # RAG-specific metrics
        if method == "rag":
            context_used = generation_result.get("context_used", {})
            metrics.update({
                "documents_retrieved": context_used.get("documents_retrieved", 0),
                "similar_scenarios": context_used.get("similar_scenarios_found", 0),
            })
            
            # Analyze citation rate
            citations = 0
            recommendations = (
                generation_result.get("education_recommendations", []) +
                generation_result.get("partner_offers", [])
            )
            
            for rec in recommendations:
                rationale = rec.get("rationale", "")
                if any(char.isdigit() for char in rationale):
                    citations += 1
            
            metrics["citation_rate"] = citations / len(recommendations) if recommendations else 0
        
        self.generations.append(metrics)
        logger.debug(f"Tracked generation: {method} for user {user_id}")
    
    def track_user_interaction(
        self,
        user_id: str,
        recommendation_id: str,
        action: str,  # "view", "click", "dismiss", "rate", "helpful"
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Track user interaction with recommendation.
        
        Args:
            user_id: User ID
            recommendation_id: Recommendation ID
            action: Action type
            metadata: Additional metadata (rating, click target, etc.)
        """
        interaction = {
            "user_id": user_id,
            "recommendation_id": recommendation_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        
        self.user_interactions.append(interaction)
        logger.debug(f"Tracked interaction: {action} on {recommendation_id}")
    
    def track_operator_decision(
        self,
        operator_id: str,
        recommendation_id: str,
        decision: str,  # "approve", "reject", "edit"
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Track operator decision on recommendation.
        
        Args:
            operator_id: Operator ID
            recommendation_id: Recommendation ID
            decision: Decision type
            metadata: Additional metadata (edit changes, rejection reason, etc.)
        """
        decision_record = {
            "operator_id": operator_id,
            "recommendation_id": recommendation_id,
            "decision": decision,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        
        self.operator_decisions.append(decision_record)
        logger.debug(f"Tracked operator decision: {decision} on {recommendation_id}")
    
    def get_generation_metrics(self, method: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregated generation metrics.
        
        Args:
            method: Filter by method ("rag" or "catalog"), or None for all
        
        Returns:
            Aggregated metrics
        """
        generations = self.generations
        if method:
            generations = [g for g in generations if g["method"] == method]
        
        if not generations:
            return {
                "sample_size": 0,
                "success_rate": 0,
                "avg_generation_time_ms": 0,
                "avg_recommendation_count": 0,
            }
        
        successful = [g for g in generations if g["success"]]
        
        metrics = {
            "sample_size": len(generations),
            "successful_generations": len(successful),
            "success_rate": len(successful) / len(generations),
            "avg_generation_time_ms": sum(g["generation_time_ms"] for g in successful) / len(successful) if successful else 0,
            "avg_recommendation_count": sum(g["recommendation_count"] for g in successful) / len(successful) if successful else 0,
            "avg_education_count": sum(g["education_count"] for g in successful) / len(successful) if successful else 0,
            "avg_partner_offer_count": sum(g["partner_offer_count"] for g in successful) / len(successful) if successful else 0,
        }
        
        # RAG-specific metrics
        if method == "rag":
            rag_gens = [g for g in successful if g["method"] == "rag"]
            if rag_gens:
                metrics.update({
                    "avg_documents_retrieved": sum(g.get("documents_retrieved", 0) for g in rag_gens) / len(rag_gens),
                    "avg_similar_scenarios": sum(g.get("similar_scenarios", 0) for g in rag_gens) / len(rag_gens),
                    "avg_citation_rate": sum(g.get("citation_rate", 0) for g in rag_gens) / len(rag_gens),
                })
        
        return metrics
    
    def get_interaction_metrics(self, recommendation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregated interaction metrics.
        
        Args:
            recommendation_id: Filter by recommendation ID, or None for all
        
        Returns:
            Aggregated metrics
        """
        interactions = self.user_interactions
        if recommendation_id:
            interactions = [i for i in interactions if i["recommendation_id"] == recommendation_id]
        
        if not interactions:
            return {
                "total_interactions": 0,
                "views": 0,
                "clicks": 0,
                "dismissals": 0,
                "ratings": 0,
                "helpful_votes": 0,
            }
        
        # Count by action type
        action_counts = defaultdict(int)
        for interaction in interactions:
            action_counts[interaction["action"]] += 1
        
        # Calculate rates
        views = action_counts.get("view", 0)
        clicks = action_counts.get("click", 0)
        dismissals = action_counts.get("dismiss", 0)
        
        metrics = {
            "total_interactions": len(interactions),
            "views": views,
            "clicks": clicks,
            "dismissals": dismissals,
            "ratings": action_counts.get("rate", 0),
            "helpful_votes": action_counts.get("helpful", 0),
            "click_through_rate": clicks / views if views > 0 else 0,
            "dismissal_rate": dismissals / views if views > 0 else 0,
        }
        
        # Average rating
        ratings = [i["metadata"].get("rating", 0) for i in interactions if i["action"] == "rate"]
        if ratings:
            metrics["avg_rating"] = sum(ratings) / len(ratings)
            metrics["rating_distribution"] = {
                "5_stars": sum(1 for r in ratings if r == 5),
                "4_stars": sum(1 for r in ratings if r == 4),
                "3_stars": sum(1 for r in ratings if r == 3),
                "2_stars": sum(1 for r in ratings if r == 2),
                "1_star": sum(1 for r in ratings if r == 1),
            }
        
        return metrics
    
    def get_operator_metrics(self, operator_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregated operator decision metrics.
        
        Args:
            operator_id: Filter by operator ID, or None for all
        
        Returns:
            Aggregated metrics
        """
        decisions = self.operator_decisions
        if operator_id:
            decisions = [d for d in decisions if d["operator_id"] == operator_id]
        
        if not decisions:
            return {
                "total_decisions": 0,
                "approvals": 0,
                "rejections": 0,
                "edits": 0,
                "approval_rate": 0,
            }
        
        # Count by decision type
        approvals = sum(1 for d in decisions if d["decision"] == "approve")
        rejections = sum(1 for d in decisions if d["decision"] == "reject")
        edits = sum(1 for d in decisions if d["decision"] == "edit")
        
        metrics = {
            "total_decisions": len(decisions),
            "approvals": approvals,
            "rejections": rejections,
            "edits": edits,
            "approval_rate": approvals / len(decisions),
            "rejection_rate": rejections / len(decisions),
            "edit_rate": edits / len(decisions),
        }
        
        # Common rejection reasons
        rejection_reasons = [
            d["metadata"].get("reason", "unknown")
            for d in decisions if d["decision"] == "reject"
        ]
        if rejection_reasons:
            reason_counts = defaultdict(int)
            for reason in rejection_reasons:
                reason_counts[reason] += 1
            metrics["rejection_reasons"] = dict(reason_counts)
        
        return metrics
    
    def compare_methods(self) -> Dict[str, Any]:
        """
        Compare RAG vs Catalog generation methods.
        
        Returns:
            Comparison metrics
        """
        rag_metrics = self.get_generation_metrics(method="rag")
        catalog_metrics = self.get_generation_metrics(method="catalog")
        
        if rag_metrics["sample_size"] == 0 or catalog_metrics["sample_size"] == 0:
            return {
                "error": "Need data from both RAG and catalog to compare",
                "rag_sample_size": rag_metrics["sample_size"],
                "catalog_sample_size": catalog_metrics["sample_size"],
            }
        
        comparison = {
            "rag": rag_metrics,
            "catalog": catalog_metrics,
            "improvements": {
                "success_rate": rag_metrics["success_rate"] - catalog_metrics["success_rate"],
                "generation_time_ms": rag_metrics["avg_generation_time_ms"] - catalog_metrics["avg_generation_time_ms"],
                "recommendation_count": rag_metrics["avg_recommendation_count"] - catalog_metrics["avg_recommendation_count"],
            },
            "winner": self._determine_winner(rag_metrics, catalog_metrics),
        }
        
        return comparison
    
    def _determine_winner(self, rag_metrics: Dict[str, Any], catalog_metrics: Dict[str, Any]) -> str:
        """
        Determine which method is better.
        
        Args:
            rag_metrics: RAG metrics
            catalog_metrics: Catalog metrics
        
        Returns:
            "rag", "catalog", or "tie"
        """
        # Weight different factors
        rag_score = 0
        catalog_score = 0
        
        # Success rate (30% weight)
        if rag_metrics["success_rate"] > catalog_metrics["success_rate"]:
            rag_score += 30
        elif catalog_metrics["success_rate"] > rag_metrics["success_rate"]:
            catalog_score += 30
        
        # Generation time (20% weight) - faster is better
        if rag_metrics["avg_generation_time_ms"] < catalog_metrics["avg_generation_time_ms"]:
            rag_score += 20
        elif catalog_metrics["avg_generation_time_ms"] < rag_metrics["avg_generation_time_ms"]:
            catalog_score += 20
        
        # Citation rate (50% weight) - only RAG has this
        if "avg_citation_rate" in rag_metrics:
            if rag_metrics["avg_citation_rate"] > 0.5:  # Good citation rate
                rag_score += 50
        
        if abs(rag_score - catalog_score) < 10:
            return "tie"
        elif rag_score > catalog_score:
            return "rag"
        else:
            return "catalog"
    
    def get_summary(self) -> str:
        """
        Get human-readable summary of all metrics.
        
        Returns:
            Summary string
        """
        lines = [
            "=" * 80,
            "Recommendation Metrics Summary",
            "=" * 80,
        ]
        
        # Generation metrics
        lines.append("\nGENERATION METRICS:")
        for method in ["rag", "catalog"]:
            metrics = self.get_generation_metrics(method=method)
            if metrics["sample_size"] > 0:
                lines.extend([
                    f"\n  {method.upper()}:",
                    f"    Sample Size: {metrics['sample_size']}",
                    f"    Success Rate: {metrics['success_rate']:.1%}",
                    f"    Avg Generation Time: {metrics['avg_generation_time_ms']:.0f}ms",
                    f"    Avg Recommendations: {metrics['avg_recommendation_count']:.1f}",
                ])
                
                if method == "rag" and "avg_citation_rate" in metrics:
                    lines.append(f"    Avg Citation Rate: {metrics['avg_citation_rate']:.1%}")
        
        # Interaction metrics
        interaction_metrics = self.get_interaction_metrics()
        if interaction_metrics["total_interactions"] > 0:
            lines.extend([
                "\nUSER INTERACTION METRICS:",
                f"  Total Interactions: {interaction_metrics['total_interactions']}",
                f"  Views: {interaction_metrics['views']}",
                f"  Clicks: {interaction_metrics['clicks']}",
                f"  Click-Through Rate: {interaction_metrics['click_through_rate']:.1%}",
                f"  Dismissal Rate: {interaction_metrics['dismissal_rate']:.1%}",
            ])
            
            if "avg_rating" in interaction_metrics:
                lines.append(f"  Avg Rating: {interaction_metrics['avg_rating']:.2f}/5.0")
        
        # Operator metrics
        operator_metrics = self.get_operator_metrics()
        if operator_metrics["total_decisions"] > 0:
            lines.extend([
                "\nOPERATOR DECISION METRICS:",
                f"  Total Decisions: {operator_metrics['total_decisions']}",
                f"  Approval Rate: {operator_metrics['approval_rate']:.1%}",
                f"  Rejection Rate: {operator_metrics['rejection_rate']:.1%}",
                f"  Edit Rate: {operator_metrics['edit_rate']:.1%}",
            ])
        
        # Comparison
        comparison = self.compare_methods()
        if "error" not in comparison:
            lines.extend([
                "\nCOMPARISON (RAG vs CATALOG):",
                f"  Winner: {comparison['winner'].upper()}",
                f"  Success Rate Improvement: {comparison['improvements']['success_rate']:+.1%}",
                f"  Generation Time Difference: {comparison['improvements']['generation_time_ms']:+.0f}ms",
            ])
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset all collected metrics."""
        self.generations = []
        self.user_interactions = []
        self.operator_decisions = []
        logger.info("Metrics reset")


# Singleton instance for global metrics collection
_global_metrics = RecommendationMetrics()


def get_metrics_collector() -> RecommendationMetrics:
    """Get global metrics collector instance."""
    return _global_metrics
