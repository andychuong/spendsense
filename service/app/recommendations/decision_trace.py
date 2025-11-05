"""Decision trace generation service for storing complete decision-making traces."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DecisionTraceGenerator:
    """Service for generating comprehensive decision traces for recommendations."""

    def __init__(self):
        """Initialize decision trace generator."""
        pass

    def create_decision_trace(
        self,
        user_id: uuid.UUID,
        recommendation_id: uuid.UUID,
        recommendation_type: str,
        persona_id: int,
        persona_name: str,
        persona_assignment_info: Dict[str, Any],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        guardrails: Dict[str, Any],
        generation_time_ms: Optional[float] = None,
        recommendation_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a comprehensive decision trace for a recommendation.

        Args:
            user_id: User ID
            recommendation_id: Recommendation ID
            recommendation_type: Type of recommendation ("education" or "partner_offer")
            persona_id: Assigned persona ID
            persona_name: Assigned persona name
            persona_assignment_info: Persona assignment details (criteria_met, priority, rationale)
            signals_30d: Detected behavioral signals for 30-day window
            signals_180d: Detected behavioral signals for 180-day window
            guardrails: Guardrails checks performed (consent, eligibility, tone, disclaimer)
            generation_time_ms: Time taken to generate recommendation in milliseconds
            recommendation_metadata: Additional metadata about the recommendation

        Returns:
            Complete decision trace dictionary
        """
        timestamp = datetime.utcnow().isoformat() + "Z"

        trace = {
            "recommendation_id": str(recommendation_id),
            "user_id": str(user_id),
            "timestamp": timestamp,
            "detected_signals": {
                "subscriptions": {
                    "30d": signals_30d.get("subscriptions", {}),
                    "180d": signals_180d.get("subscriptions", {}),
                },
                "savings": {
                    "30d": signals_30d.get("savings", {}),
                    "180d": signals_180d.get("savings", {}),
                },
                "credit": {
                    "30d": signals_30d.get("credit", {}),
                    "180d": signals_180d.get("credit", {}),
                },
                "income": {
                    "30d": signals_30d.get("income", {}),
                    "180d": signals_180d.get("income", {}),
                },
            },
            "persona_assignment": {
                "persona_id": persona_id,
                "persona_name": persona_name,
                "criteria_met": persona_assignment_info.get("criteria_met", []),
                "priority": persona_assignment_info.get("priority", None),
                "rationale": persona_assignment_info.get("rationale", ""),
                "persona_changed": persona_assignment_info.get("persona_changed", False),
            },
            "recommendation": {
                "recommendation_id": str(recommendation_id),
                "type": recommendation_type,
                "title": recommendation_metadata.get("title", "") if recommendation_metadata else "",
                "content_preview": recommendation_metadata.get("content_preview", "") if recommendation_metadata else "",
                "rationale_preview": recommendation_metadata.get("rationale_preview", "") if recommendation_metadata else "",
                "guardrails": guardrails,
            },
            "generation_time_ms": generation_time_ms,
        }

        return trace

    def create_persona_assignment_info(
        self,
        persona_id: int,
        persona_name: str,
        criteria_met: List[str],
        priority: int,
        rationale: str,
        persona_changed: bool = False,
    ) -> Dict[str, Any]:
        """
        Create persona assignment information for decision trace.

        Args:
            persona_id: Persona ID
            persona_name: Persona name
            criteria_met: List of criteria that were met
            priority: Persona priority (1-5)
            rationale: Rationale for persona assignment
            persona_changed: Whether persona changed from previous assignment

        Returns:
            Persona assignment info dictionary
        """
        return {
            "persona_id": persona_id,
            "persona_name": persona_name,
            "criteria_met": criteria_met,
            "priority": priority,
            "rationale": rationale,
            "persona_changed": persona_changed,
        }

    def create_guardrails_info(
        self,
        consent_status: bool,
        consent_check_timestamp: Optional[str] = None,
        eligibility_status: Optional[bool] = None,
        eligibility_explanation: Optional[str] = None,
        eligibility_details: Optional[Dict[str, Any]] = None,
        tone_valid: Optional[bool] = None,
        tone_score: Optional[float] = None,
        tone_explanation: Optional[str] = None,
        disclaimer_present: bool = True,
        disclaimer_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create guardrails information for decision trace.

        Args:
            consent_status: Whether consent was granted
            consent_check_timestamp: Timestamp of consent check
            eligibility_status: Whether recommendation is eligible
            eligibility_explanation: Explanation of eligibility check
            eligibility_details: Detailed eligibility information (income, credit score, etc.)
            tone_valid: Whether tone validation passed
            tone_score: Tone score (0-10, where 10 is most empowering)
            tone_explanation: Explanation of tone validation
            disclaimer_present: Whether regulatory disclaimer is present
            disclaimer_text: Text of regulatory disclaimer

        Returns:
            Guardrails info dictionary
        """
        guardrails = {
            "consent": {
                "status": consent_status,
                "checked_at": consent_check_timestamp or datetime.utcnow().isoformat() + "Z",
            },
            "disclaimer": {
                "present": disclaimer_present,
                "text": disclaimer_text,
            },
        }

        if eligibility_status is not None:
            guardrails["eligibility"] = {
                "status": eligibility_status,
                "explanation": eligibility_explanation or "",
                "details": eligibility_details or {},
            }

        if tone_valid is not None:
            guardrails["tone"] = {
                "valid": tone_valid,
                "score": tone_score,
                "explanation": tone_explanation or "",
            }

        return guardrails

    def generate_human_readable_trace(
        self,
        trace: Dict[str, Any],
        format: str = "markdown",
    ) -> str:
        """
        Generate human-readable decision trace.

        Args:
            trace: Decision trace dictionary
            format: Output format ("markdown" or "html")

        Returns:
            Human-readable decision trace string
        """
        if format == "markdown":
            return self._generate_markdown_trace(trace)
        elif format == "html":
            return self._generate_html_trace(trace)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_trace(self, trace: Dict[str, Any]) -> str:
        """Generate Markdown-formatted decision trace."""
        lines = []

        # Header
        lines.append("# Decision Trace")
        lines.append("")
        lines.append(f"**Recommendation ID**: `{trace['recommendation_id']}`")
        lines.append(f"**User ID**: `{trace['user_id']}`")
        lines.append(f"**Timestamp**: {trace['timestamp']}")
        lines.append("")

        # Persona Assignment
        lines.append("## Persona Assignment")
        persona = trace["persona_assignment"]
        lines.append(f"- **Persona**: {persona['persona_name']} (ID: {persona['persona_id']})")
        lines.append(f"- **Priority**: {persona.get('priority', 'N/A')}")
        lines.append(f"- **Rationale**: {persona.get('rationale', 'N/A')}")
        if persona.get("persona_changed"):
            lines.append("- **Status**: Persona changed from previous assignment")
        else:
            lines.append("- **Status**: Persona unchanged")

        criteria_met = persona.get("criteria_met", [])
        if criteria_met:
            lines.append("- **Criteria Met**:")
            for criterion in criteria_met:
                lines.append(f"  - {criterion}")
        lines.append("")

        # Detected Signals
        lines.append("## Detected Behavioral Signals")
        signals = trace["detected_signals"]

        for signal_type in ["subscriptions", "savings", "credit", "income"]:
            signal_30d = signals[signal_type].get("30d", {})
            signal_180d = signals[signal_type].get("180d", {})

            if signal_30d or signal_180d:
                lines.append(f"### {signal_type.title()}")

                if signal_30d:
                    lines.append("**30-Day Window:**")
                    lines.append(self._format_signal_summary(signal_30d, signal_type))

                if signal_180d:
                    lines.append("**180-Day Window:**")
                    lines.append(self._format_signal_summary(signal_180d, signal_type))

                lines.append("")

        # Guardrails
        lines.append("## Guardrails Checks")
        guardrails = trace["recommendation"]["guardrails"]

        # Consent
        consent = guardrails.get("consent", {})
        consent_status = "✓ Granted" if consent.get("status") else "✗ Not Granted"
        lines.append(f"- **Consent**: {consent_status}")
        lines.append(f"  - Checked at: {consent.get('checked_at', 'N/A')}")

        # Eligibility
        if "eligibility" in guardrails:
            eligibility = guardrails["eligibility"]
            eligibility_status = "✓ Eligible" if eligibility.get("status") else "✗ Not Eligible"
            lines.append(f"- **Eligibility**: {eligibility_status}")
            lines.append(f"  - Explanation: {eligibility.get('explanation', 'N/A')}")

            details = eligibility.get("details", {})
            if details:
                lines.append("  - Details:")
                for key, value in details.items():
                    lines.append(f"    - {key}: {value}")

        # Tone
        if "tone" in guardrails:
            tone = guardrails["tone"]
            tone_status = "✓ Valid" if tone.get("valid") else "✗ Invalid"
            lines.append(f"- **Tone Validation**: {tone_status}")
            lines.append(f"  - Score: {tone.get('score', 'N/A')}/10")
            lines.append(f"  - Explanation: {tone.get('explanation', 'N/A')}")

        # Disclaimer
        disclaimer = guardrails.get("disclaimer", {})
        disclaimer_status = "✓ Present" if disclaimer.get("present") else "✗ Missing"
        lines.append(f"- **Regulatory Disclaimer**: {disclaimer_status}")
        if disclaimer.get("text"):
            lines.append(f"  - Text: {disclaimer['text'][:100]}...")
        lines.append("")

        # Recommendation Details
        lines.append("## Recommendation Details")
        rec = trace["recommendation"]
        lines.append(f"- **Type**: {rec['type']}")
        lines.append(f"- **Title**: {rec.get('title', 'N/A')}")
        if rec.get("rationale_preview"):
            lines.append(f"- **Rationale Preview**: {rec['rationale_preview'][:200]}...")
        lines.append("")

        # Performance
        if trace.get("generation_time_ms"):
            lines.append("## Performance")
            lines.append(f"- **Generation Time**: {trace['generation_time_ms']:.2f} ms")
            lines.append("")

        return "\n".join(lines)

    def _format_signal_summary(self, signal: Dict[str, Any], signal_type: str) -> str:
        """Format signal summary for display."""
        lines = []

        if signal_type == "subscriptions":
            subscription_count = signal.get("subscription_count", 0)
            total_recurring_spend = signal.get("total_recurring_spend", 0)
            subscription_share = signal.get("subscription_share_percent", 0)

            if subscription_count > 0:
                lines.append(f"  - Recurring subscriptions: {subscription_count}")
                lines.append(f"  - Total recurring spend: ${total_recurring_spend:.2f}/month")
                lines.append(f"  - Subscription share: {subscription_share:.1f}%")

        elif signal_type == "savings":
            savings_growth_rate = signal.get("savings_growth_rate_percent")
            net_inflow = signal.get("net_inflow_monthly")
            emergency_fund_coverage = signal.get("emergency_fund_coverage_months")

            if savings_growth_rate is not None:
                lines.append(f"  - Savings growth rate: {savings_growth_rate:.2f}%")
            if net_inflow is not None:
                lines.append(f"  - Net monthly inflow: ${net_inflow:.2f}")
            if emergency_fund_coverage is not None:
                lines.append(f"  - Emergency fund coverage: {emergency_fund_coverage:.2f} months")

        elif signal_type == "credit":
            high_util_count = len(signal.get("high_utilization_cards", []))
            critical_util_count = len(signal.get("critical_utilization_cards", []))
            severe_util_count = len(signal.get("severe_utilization_cards", []))
            interest_charges = sum([
                card.get("interest_charges", {}).get("total_interest_charges", 0)
                for card in signal.get("cards_with_interest", [])
            ])

            if high_util_count > 0 or critical_util_count > 0 or severe_util_count > 0:
                lines.append(f"  - Cards with high utilization: {high_util_count + critical_util_count + severe_util_count}")
            if interest_charges > 0:
                lines.append(f"  - Total interest charges: ${interest_charges:.2f}")

            min_payment_count = len(signal.get("minimum_payment_only_cards", []))
            overdue_count = len(signal.get("overdue_cards", []))

            if min_payment_count > 0:
                lines.append(f"  - Cards with minimum-payment-only: {min_payment_count}")
            if overdue_count > 0:
                lines.append(f"  - Overdue cards: {overdue_count}")

        elif signal_type == "income":
            income_patterns = signal.get("income_patterns", {})
            payment_frequency = income_patterns.get("payment_frequency")
            median_pay_gap = income_patterns.get("median_pay_gap_days")
            payment_variability = signal.get("payment_variability_percent")
            cash_flow_buffer = signal.get("cash_flow_buffer_months")

            if payment_frequency:
                lines.append(f"  - Payment frequency: {payment_frequency}")
            if median_pay_gap is not None:
                lines.append(f"  - Median pay gap: {median_pay_gap:.0f} days")
            if payment_variability is not None:
                lines.append(f"  - Payment variability: {payment_variability:.1f}%")
            if cash_flow_buffer is not None:
                lines.append(f"  - Cash-flow buffer: {cash_flow_buffer:.2f} months")

        return "\n".join(lines) if lines else "  - No significant signals detected"

    def _generate_html_trace(self, trace: Dict[str, Any]) -> str:
        """Generate HTML-formatted decision trace."""
        # Convert markdown to HTML
        markdown = self._generate_markdown_trace(trace)

        # Simple markdown to HTML conversion
        html = markdown.replace("\n", "<br>\n")
        html = html.replace("# ", "<h1>")
        html = html.replace("## ", "<h2>")
        html = html.replace("### ", "<h3>")
        html = html.replace("**", "<strong>")
        html = html.replace("`", "<code>")

        # Close tags (simplified)
        html = html.replace("<h1>", "<h1>", 1)
        html = html.replace("<h2>", "</h2>\n<h2>", html.count("<h2>") - 1)
        html = html.replace("<h3>", "</h3>\n<h3>", html.count("<h3>") - 1)

        return f"<html><body>{html}</body></html>"



