"""Report generation service for evaluation metrics and decision traces."""

import logging
import json
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

# Try to import models from backend
try:
    from backend.app.models.user import User
    from backend.app.models.user_profile import UserProfile
    from backend.app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus
except ImportError:
    import sys
    import os as os_module
    backend_path = os_module.path.join(os_module.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.user import User
    from app.models.user_profile import UserProfile
    from app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus

# Try to import from service layer
try:
    from app.eval.metrics import EvaluationService
    from app.recommendations.decision_trace import DecisionTraceGenerator
except ImportError:
    import sys
    import os as os_module
    service_path = os_module.path.join(os_module.path.dirname(__file__), "../..")
    if service_path not in sys.path:
        sys.path.insert(0, service_path)
    from app.eval.metrics import EvaluationService
    from app.recommendations.decision_trace import DecisionTraceGenerator

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating evaluation reports."""

    def __init__(self, db_session: Session, output_dir: Optional[str] = None):
        """
        Initialize report generator.

        Args:
            db_session: SQLAlchemy database session
            output_dir: Output directory for reports (default: current directory)
        """
        self.db = db_session
        self.eval_service = EvaluationService(db_session)
        self.trace_generator = DecisionTraceGenerator()
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_metrics_json(self, filename: Optional[str] = None) -> str:
        """
        Generate JSON metrics file.

        Args:
            filename: Output filename (default: metrics_{timestamp}.json)

        Returns:
            Path to generated JSON file
        """
        logger.info("Generating JSON metrics file")

        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"

        filepath = self.output_dir / filename

        # Calculate all metrics
        metrics = self.eval_service.calculate_all_metrics()

        # Write JSON file
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)

        logger.info(f"Generated JSON metrics file: {filepath}")
        return str(filepath)

    def generate_metrics_csv(self, filename: Optional[str] = None) -> str:
        """
        Generate CSV metrics file.

        Args:
            filename: Output filename (default: metrics_{timestamp}.csv)

        Returns:
            Path to generated CSV file
        """
        logger.info("Generating CSV metrics file")

        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.csv"

        filepath = self.output_dir / filename

        # Calculate all metrics
        metrics = self.eval_service.calculate_all_metrics()

        # Flatten metrics for CSV
        rows = []

        # Coverage metrics
        coverage = metrics["coverage"]
        rows.append({
            "metric_category": "coverage",
            "metric_name": "users_with_persona_percent",
            "value": coverage["users_with_persona_percent"],
            "count": coverage["users_with_persona_count"],
            "total": coverage["total_users"],
        })
        rows.append({
            "metric_category": "coverage",
            "metric_name": "users_with_behaviors_percent",
            "value": coverage["users_with_behaviors_percent"],
            "count": coverage["users_with_behaviors_count"],
            "total": coverage["total_users"],
        })
        rows.append({
            "metric_category": "coverage",
            "metric_name": "users_with_both_percent",
            "value": coverage["users_with_both_percent"],
            "count": coverage["users_with_both_count"],
            "total": coverage["total_users"],
        })

        # Explainability metrics
        explainability = metrics["explainability"]
        rows.append({
            "metric_category": "explainability",
            "metric_name": "recommendations_with_rationales_percent",
            "value": explainability["recommendations_with_rationales_percent"],
            "count": explainability["recommendations_with_rationales_count"],
            "total": explainability["total_recommendations"],
        })
        rows.append({
            "metric_category": "explainability",
            "metric_name": "rationales_with_data_points_percent",
            "value": explainability["rationales_with_data_points_percent"],
            "count": explainability["rationales_with_data_points_count"],
            "total": explainability["recommendations_with_rationales_count"],
        })
        rows.append({
            "metric_category": "explainability",
            "metric_name": "rationale_quality_score",
            "value": explainability["rationale_quality_score"],
            "count": None,
            "total": None,
        })

        # Relevance metrics
        relevance = metrics["relevance"]
        rows.append({
            "metric_category": "relevance",
            "metric_name": "education_persona_fit_percent",
            "value": relevance["education_persona_fit_percent"],
            "count": relevance["education_items_matching_persona"],
            "total": relevance["total_education_items"],
        })
        rows.append({
            "metric_category": "relevance",
            "metric_name": "partner_offer_persona_fit_percent",
            "value": relevance["partner_offer_persona_fit_percent"],
            "count": relevance["partner_offers_matching_persona"],
            "total": relevance["total_partner_offers"],
        })

        # Latency metrics
        latency = metrics["latency"]
        rows.append({
            "metric_category": "latency",
            "metric_name": "latency_p50_ms",
            "value": latency["recommendation_generation_latency_p50"],
            "count": None,
            "total": latency["total_recommendations"],
        })
        rows.append({
            "metric_category": "latency",
            "metric_name": "latency_p95_ms",
            "value": latency["recommendation_generation_latency_p95"],
            "count": None,
            "total": latency["total_recommendations"],
        })
        rows.append({
            "metric_category": "latency",
            "metric_name": "latency_p99_ms",
            "value": latency["recommendation_generation_latency_p99"],
            "count": None,
            "total": latency["total_recommendations"],
        })
        rows.append({
            "metric_category": "latency",
            "metric_name": "latency_mean_ms",
            "value": latency["recommendation_generation_latency_mean"],
            "count": None,
            "total": latency["total_recommendations"],
        })
        rows.append({
            "metric_category": "latency",
            "metric_name": "recommendations_within_target_percent",
            "value": latency["recommendations_within_target_percent"],
            "count": latency["recommendations_within_target"],
            "total": latency["total_recommendations"],
        })

        # Fairness metrics
        fairness = metrics["fairness"]
        rows.append({
            "metric_category": "fairness",
            "metric_name": "persona_balance_score",
            "value": fairness["persona_balance_score"],
            "count": None,
            "total": None,
        })

        # Persona distribution
        for persona_id, dist in fairness["persona_distribution"].items():
            rows.append({
                "metric_category": "fairness",
                "metric_name": f"persona_{persona_id}_recommendations_percent",
                "value": dist["recommendations_percent"],
                "count": dist["recommendations_count"],
                "total": None,
            })
            rows.append({
                "metric_category": "fairness",
                "metric_name": f"persona_{persona_id}_users_percent",
                "value": dist["users_percent"],
                "count": dist["users_count"],
                "total": None,
            })

        # Write CSV file
        fieldnames = ["metric_category", "metric_name", "value", "count", "total"]
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        logger.info(f"Generated CSV metrics file: {filepath}")
        return str(filepath)

    def generate_summary_report(self, filename: Optional[str] = None) -> str:
        """
        Generate brief summary report (1-2 pages).

        Args:
            filename: Output filename (default: summary_report_{timestamp}.md)

        Returns:
            Path to generated report file
        """
        logger.info("Generating summary report")

        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.md"

        filepath = self.output_dir / filename

        # Calculate all metrics
        metrics = self.eval_service.calculate_all_metrics()

        # Generate report content
        report_lines = []

        # Header
        report_lines.append("# SpendSense Evaluation Report")
        report_lines.append("")
        report_lines.append(f"**Generated**: {metrics['calculated_at']}")
        report_lines.append("")

        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")

        coverage = metrics["coverage"]
        explainability = metrics["explainability"]
        relevance = metrics["relevance"]
        latency = metrics["latency"]
        fairness = metrics["fairness"]

        report_lines.append("### Key Metrics")
        report_lines.append("")
        report_lines.append(f"- **Coverage**: {coverage['users_with_both_percent']:.1f}% of users have assigned persona and ≥3 detected behaviors")
        report_lines.append(f"- **Explainability**: {explainability['recommendations_with_rationales_percent']:.1f}% of recommendations include plain-language rationales")
        report_lines.append(f"- **Relevance**: {relevance['education_persona_fit_percent']:.1f}% education-persona fit, {relevance['partner_offer_persona_fit_percent']:.1f}% partner offer-persona fit")
        report_lines.append(f"- **Latency**: P95 latency of {latency['recommendation_generation_latency_p95']:.0f}ms ({latency['recommendations_within_target_percent']:.1f}% within 5-second target)")
        report_lines.append(f"- **Fairness**: Persona balance score of {fairness['persona_balance_score']:.3f}/1.0")
        report_lines.append("")

        # Coverage Section
        report_lines.append("## Coverage Metrics")
        report_lines.append("")
        report_lines.append(f"- **Total Users**: {coverage['total_users']}")
        report_lines.append(f"- **Users with Persona**: {coverage['users_with_persona_count']} ({coverage['users_with_persona_percent']:.1f}%)")
        report_lines.append(f"- **Users with ≥3 Behaviors**: {coverage['users_with_behaviors_count']} ({coverage['users_with_behaviors_percent']:.1f}%)")
        report_lines.append(f"- **Users with Both**: {coverage['users_with_both_count']} ({coverage['users_with_both_percent']:.1f}%)")
        report_lines.append("")

        # Explainability Section
        report_lines.append("## Explainability Metrics")
        report_lines.append("")
        report_lines.append(f"- **Total Recommendations**: {explainability['total_recommendations']}")
        report_lines.append(f"- **Recommendations with Rationales**: {explainability['recommendations_with_rationales_count']} ({explainability['recommendations_with_rationales_percent']:.1f}%)")
        report_lines.append(f"- **Rationales with Data Points**: {explainability['rationales_with_data_points_count']} ({explainability['rationales_with_data_points_percent']:.1f}%)")
        report_lines.append(f"- **Average Rationale Quality Score**: {explainability['rationale_quality_score']:.1f}/10")
        report_lines.append("")

        # Relevance Section
        report_lines.append("## Relevance Metrics")
        report_lines.append("")
        report_lines.append(f"- **Education Items**: {relevance['total_education_items']} total")
        report_lines.append(f"  - Matching Persona: {relevance['education_items_matching_persona']} ({relevance['education_persona_fit_percent']:.1f}%)")
        report_lines.append(f"- **Partner Offers**: {relevance['total_partner_offers']} total")
        report_lines.append(f"  - Matching Persona: {relevance['partner_offers_matching_persona']} ({relevance['partner_offer_persona_fit_percent']:.1f}%)")
        report_lines.append("")

        # Latency Section
        report_lines.append("## Latency Metrics")
        report_lines.append("")
        report_lines.append(f"- **Total Recommendations with Latency Data**: {latency['total_recommendations']}")
        report_lines.append(f"- **P50 Latency**: {latency['recommendation_generation_latency_p50']:.0f}ms")
        report_lines.append(f"- **P95 Latency**: {latency['recommendation_generation_latency_p95']:.0f}ms")
        report_lines.append(f"- **P99 Latency**: {latency['recommendation_generation_latency_p99']:.0f}ms")
        report_lines.append(f"- **Mean Latency**: {latency['recommendation_generation_latency_mean']:.0f}ms")
        report_lines.append(f"- **Recommendations within 5s**: {latency['recommendations_within_target']} ({latency['recommendations_within_target_percent']:.1f}%)")
        report_lines.append("")

        # Fairness Section
        report_lines.append("## Fairness Metrics")
        report_lines.append("")
        report_lines.append(f"- **Persona Balance Score**: {fairness['persona_balance_score']:.3f}/1.0")
        report_lines.append("")
        report_lines.append("### Persona Distribution")
        report_lines.append("")
        report_lines.append("| Persona | Recommendations | Users | Rec % | Users % |")
        report_lines.append("|---------|----------------|-------|-------|---------|")
        for persona_id in range(1, 6):
            dist = fairness["persona_distribution"][persona_id]
            report_lines.append(
                f"| {persona_id} | {dist['recommendations_count']} | {dist['users_count']} | "
                f"{dist['recommendations_percent']:.1f}% | {dist['users_percent']:.1f}% |"
            )
        report_lines.append("")

        # Signal Detection by Persona
        report_lines.append("### Signal Detection by Persona")
        report_lines.append("")
        report_lines.append("| Persona | Avg Behaviors Detected | Profiles Count |")
        report_lines.append("|---------|----------------------|---------------|")
        for persona_id in range(1, 6):
            detection = fairness["signal_detection_by_persona"][persona_id]
            report_lines.append(
                f"| {persona_id} | {detection['avg_behaviors_detected']:.2f} | {detection['profiles_count']} |"
            )
        report_lines.append("")

        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")

        # Check if metrics meet targets
        recommendations = []
        if coverage['users_with_both_percent'] < 100:
            recommendations.append(f"- Coverage: Currently {coverage['users_with_both_percent']:.1f}%, target is 100%")
        if explainability['recommendations_with_rationales_percent'] < 100:
            recommendations.append(f"- Explainability: Currently {explainability['recommendations_with_rationales_percent']:.1f}%, target is 100%")
        if relevance['education_persona_fit_percent'] < 80:
            recommendations.append(f"- Relevance: Education-persona fit is {relevance['education_persona_fit_percent']:.1f}%, target is ≥80%")
        if latency['recommendations_within_target_percent'] < 100:
            recommendations.append(f"- Latency: {latency['recommendations_within_target_percent']:.1f}% within 5s target, target is 100%")
        if fairness['persona_balance_score'] < 0.8:
            recommendations.append(f"- Fairness: Persona balance score is {fairness['persona_balance_score']:.3f}, target is ≥0.8")

        if recommendations:
            report_lines.append("### Areas for Improvement")
            report_lines.append("")
            for rec in recommendations:
                report_lines.append(rec)
        else:
            report_lines.append("All metrics meet or exceed target thresholds.")

        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append(f"*Report generated at {metrics['calculated_at']}*")

        # Write report file
        report_content = "\n".join(report_lines)
        with open(filepath, 'w') as f:
            f.write(report_content)

        logger.info(f"Generated summary report: {filepath}")
        return str(filepath)

    def generate_user_decision_traces(
        self,
        user_id: Optional[str] = None,
        output_format: str = "json",
        combined: bool = False,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate per-user decision traces.

        Args:
            user_id: Specific user ID to generate traces for (if None, generates for all users)
            output_format: Output format ("json" or "markdown")
            combined: If True, generates one combined file; if False, one file per user
            filename: Output filename (only used if combined=True)

        Returns:
            Path(s) to generated trace file(s)
        """
        logger.info(f"Generating decision traces (format: {output_format}, combined: {combined})")

        # Get recommendations
        query = self.db.query(Recommendation).filter(
            Recommendation.decision_trace.isnot(None)
        )

        if user_id:
            query = query.filter(Recommendation.user_id == user_id)

        recommendations = query.order_by(Recommendation.user_id, Recommendation.created_at).all()

        if not recommendations:
            logger.warning("No recommendations with decision traces found")
            return ""

        if combined:
            # Generate one combined file
            if not filename:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"decision_traces_all_{timestamp}.{output_format}"

            filepath = self.output_dir / filename

            if output_format == "json":
                traces = []
                for rec in recommendations:
                    if rec.decision_trace:
                        traces.append(rec.decision_trace)

                with open(filepath, 'w') as f:
                    json.dump(traces, f, indent=2, default=str)
            else:  # markdown
                content_lines = []
                content_lines.append("# Decision Traces")
                content_lines.append("")
                content_lines.append(f"**Generated**: {datetime.utcnow().isoformat()}Z")
                content_lines.append(f"**Total Recommendations**: {len(recommendations)}")
                content_lines.append("")

                for rec in recommendations:
                    if rec.decision_trace:
                        trace = rec.decision_trace
                        content_lines.append("---")
                        content_lines.append("")
                        content_lines.append(
                            self.trace_generator.generate_human_readable_trace(trace, format="markdown")
                        )
                        content_lines.append("")

                with open(filepath, 'w') as f:
                    f.write("\n".join(content_lines))

            logger.info(f"Generated combined decision traces file: {filepath}")
            return str(filepath)
        else:
            # Generate one file per user
            files_generated = []
            current_user_id = None
            user_traces = []

            for rec in recommendations:
                if rec.user_id != current_user_id:
                    # Save previous user's traces
                    if current_user_id and user_traces:
                        filepath = self._save_user_traces(
                            current_user_id, user_traces, output_format
                        )
                        files_generated.append(filepath)

                    # Start new user
                    current_user_id = rec.user_id
                    user_traces = []

                if rec.decision_trace:
                    user_traces.append(rec.decision_trace)

            # Save last user's traces
            if current_user_id and user_traces:
                filepath = self._save_user_traces(
                    current_user_id, user_traces, output_format
                )
                files_generated.append(filepath)

            logger.info(f"Generated {len(files_generated)} decision trace files")
            return ", ".join(files_generated)

    def _save_user_traces(
        self,
        user_id: str,
        traces: List[Dict[str, Any]],
        output_format: str,
    ) -> str:
        """Save traces for a single user."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"decision_traces_user_{user_id}_{timestamp}.{output_format}"
        filepath = self.output_dir / filename

        if output_format == "json":
            with open(filepath, 'w') as f:
                json.dump(traces, f, indent=2, default=str)
        else:  # markdown
            content_lines = []
            content_lines.append(f"# Decision Traces - User {user_id}")
            content_lines.append("")
            content_lines.append(f"**Generated**: {datetime.utcnow().isoformat()}Z")
            content_lines.append(f"**Total Recommendations**: {len(traces)}")
            content_lines.append("")

            for trace in traces:
                content_lines.append("---")
                content_lines.append("")
                content_lines.append(
                    self.trace_generator.generate_human_readable_trace(trace, format="markdown")
                )
                content_lines.append("")

            with open(filepath, 'w') as f:
                f.write("\n".join(content_lines))

        return str(filepath)

    def generate_all_reports(
        self,
        include_json: bool = True,
        include_csv: bool = True,
        include_summary: bool = True,
        include_traces: bool = True,
        traces_format: str = "json",
        traces_combined: bool = False,
    ) -> Dict[str, str]:
        """
        Generate all reports.

        Args:
            include_json: Include JSON metrics file
            include_csv: Include CSV metrics file
            include_summary: Include summary report
            include_traces: Include decision traces
            traces_format: Format for traces ("json" or "markdown")
            traces_combined: Generate combined traces file or per-user files

        Returns:
            Dictionary mapping report type to file path(s)
        """
        logger.info("Generating all reports")

        reports = {}

        if include_json:
            reports["metrics_json"] = self.generate_metrics_json()

        if include_csv:
            reports["metrics_csv"] = self.generate_metrics_csv()

        if include_summary:
            reports["summary_report"] = self.generate_summary_report()

        if include_traces:
            reports["decision_traces"] = self.generate_user_decision_traces(
                output_format=traces_format,
                combined=traces_combined,
            )

        logger.info(f"Generated {len(reports)} report types")
        return reports

