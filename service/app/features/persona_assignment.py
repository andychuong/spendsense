"""Persona assignment service for assigning users to behavioral personas based on detected signals."""

import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from app.features.subscriptions import SubscriptionDetector
from app.features.savings import SavingsDetector
from app.features.credit import CreditUtilizationDetector
from app.features.income import IncomeStabilityDetector
from app.common.consent_guardrails import ConsentGuardrails, ConsentError

# Try to import OpenAI client
try:
    from app.common.openai_client import get_openai_client
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI client not available - persona rationales will use rule-based generation only")

logger = logging.getLogger(__name__)


def _serialize_signals_for_json(signals: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively convert UUID objects to strings in signals dictionary for JSON serialization.

    Args:
        signals: Signals dictionary that may contain UUID objects

    Returns:
        Dictionary with UUIDs converted to strings
    """
    if isinstance(signals, dict):
        return {k: _serialize_signals_for_json(v) for k, v in signals.items()}
    elif isinstance(signals, list):
        return [_serialize_signals_for_json(item) for item in signals]
    elif isinstance(signals, uuid.UUID):
        return str(signals)
    elif isinstance(signals, datetime):
        return signals.isoformat()
    else:
        return signals

# Try to import models from backend
try:
    from backend.app.models.user_profile import UserProfile, PersonaId
    from backend.app.models.persona_history import PersonaHistory
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.user_profile import UserProfile, PersonaId
    from app.models.persona_history import PersonaHistory


# Persona definitions
PERSONA_DEFINITIONS = {
    1: {
        "name": "High Utilization",
        "priority": 1,
    },
    2: {
        "name": "Variable Income Budgeter",
        "priority": 2,
    },
    3: {
        "name": "Subscription-Heavy",
        "priority": 3,
    },
    4: {
        "name": "Savings Builder",
        "priority": 4,
    },
    5: {
        "name": "Custom Persona",
        "priority": 5,
    },
}


class PersonaAssignmentService:
    """Service for assigning users to behavioral personas based on detected signals."""

    def __init__(self, db_session: Session):
        """
        Initialize persona assignment service.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.subscription_detector = SubscriptionDetector(db_session)
        self.savings_detector = SavingsDetector(db_session)
        self.credit_detector = CreditUtilizationDetector(db_session)
        self.income_detector = IncomeStabilityDetector(db_session)
        self.consent_guardrails = ConsentGuardrails(db_session)

        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE:
            try:
                self.openai_client = get_openai_client()
                if self.openai_client and self.openai_client.client:
                    logger.info("OpenAI client initialized for persona assignment")
                else:
                    logger.info("OpenAI client not available (no API key or client not initialized)")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client for persona assignment: {str(e)}")
                self.openai_client = None

    def check_persona_1_high_utilization(
        self,
        credit_signals_30d: Dict[str, Any],
        credit_signals_180d: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Check if user matches Persona 1: High Utilization.

        Criteria:
        - Any card utilization ≥50% OR
        - Interest charges > 0 OR
        - Minimum-payment-only OR
        - is_overdue = true

        Args:
            credit_signals_30d: Credit signals for 30-day window
            credit_signals_180d: Credit signals for 180-day window

        Returns:
            Tuple of (matches, rationale)
        """
        # Use 30-day window for primary check, fallback to 180-day if needed
        signals = credit_signals_30d if credit_signals_30d else credit_signals_180d

        if not signals:
            return False, ""

        reasons = []

        # Check for utilization ≥50%
        critical_cards = signals.get("critical_utilization_cards", [])
        severe_cards = signals.get("severe_utilization_cards", [])
        if critical_cards or severe_cards:
            all_high_util = critical_cards + severe_cards
            card_names = [card.get("account_name", "Unknown") for card in all_high_util]
            max_util = max([card.get("utilization_percent", 0) for card in all_high_util], default=0)
            reasons.append(f"Credit card utilization at {max_util:.1f}% (cards: {', '.join(card_names)})")

        # Check for interest charges
        cards_with_interest = signals.get("cards_with_interest", [])
        if cards_with_interest:
            total_interest = sum([card.get("interest_charges", {}).get("total_interest_charges", 0)
                                 for card in cards_with_interest])
            card_names = [card.get("account_name", "Unknown") for card in cards_with_interest]
            reasons.append(f"Interest charges totaling ${total_interest:.2f} on {', '.join(card_names)}")

        # Check for minimum-payment-only behavior
        min_payment_cards = signals.get("minimum_payment_only_cards", [])
        if min_payment_cards:
            card_names = [card.get("account_name", "Unknown") for card in min_payment_cards]
            reasons.append(f"Making minimum payments only on {', '.join(card_names)}")

        # Check for overdue accounts
        overdue_cards = signals.get("overdue_cards", [])
        if overdue_cards:
            card_names = [card.get("account_name", "Unknown") for card in overdue_cards]
            reasons.append(f"Overdue accounts: {', '.join(card_names)}")

        if reasons:
            rationale = "High credit card utilization detected. " + " ".join(reasons)
            return True, rationale

        return False, ""

    def check_persona_2_variable_income(
        self,
        income_signals_30d: Dict[str, Any],
        income_signals_180d: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Check if user matches Persona 2: Variable Income Budgeter.

        Criteria:
        - Median pay gap > 45 days AND
        - Cash-flow buffer < 1 month

        Args:
            income_signals_30d: Income signals for 30-day window
            income_signals_180d: Income signals for 180-day window

        Returns:
            Tuple of (matches, rationale)
        """
        # Use 180-day window for income stability (more reliable)
        signals = income_signals_180d if income_signals_180d else income_signals_30d

        if not signals:
            return False, ""

        # Check median pay gap > 45 days
        income_patterns = signals.get("income_patterns", {})
        median_pay_gap = income_patterns.get("median_pay_gap_days", None)

        if median_pay_gap is None or median_pay_gap <= 45:
            return False, ""

        # Check cash-flow buffer < 1 month
        cash_flow_buffer = signals.get("cash_flow_buffer_months", None)

        if cash_flow_buffer is None or cash_flow_buffer >= 1.0:
            return False, ""

        # Build rationale
        rationale = (
            f"Variable income pattern detected: median pay gap of {median_pay_gap:.0f} days "
            f"and cash-flow buffer of {cash_flow_buffer:.2f} months."
        )

        return True, rationale

    def check_persona_3_subscription_heavy(
        self,
        subscription_signals_30d: Dict[str, Any],
        subscription_signals_180d: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Check if user matches Persona 3: Subscription-Heavy.

        Criteria:
        - Recurring merchants ≥3 AND
        - (Monthly recurring spend ≥$50 in 30d OR subscription spend share ≥10%)

        Args:
            subscription_signals_30d: Subscription signals for 30-day window
            subscription_signals_180d: Subscription signals for 180-day window

        Returns:
            Tuple of (matches, rationale)
        """
        # Use 30-day window for subscription detection
        signals = subscription_signals_30d if subscription_signals_30d else subscription_signals_180d

        if not signals:
            return False, ""

        # Check recurring merchants ≥3
        subscription_count = signals.get("subscription_count", 0)

        if subscription_count < 3:
            return False, ""

        # Check monthly recurring spend ≥$50 OR subscription share ≥10%
        total_recurring_spend = signals.get("total_recurring_spend", 0)
        subscription_share = signals.get("subscription_share_percent", 0)

        if total_recurring_spend < 50 and subscription_share < 10:
            return False, ""

        # Build rationale
        recurring_merchants = signals.get("recurring_merchants", [])
        merchant_names = [m.get("merchant_name", "Unknown") for m in recurring_merchants[:5]]

        rationale = (
            f"Subscription-heavy pattern detected: {subscription_count} recurring subscriptions "
            f"with ${total_recurring_spend:.2f}/month recurring spend ({subscription_share:.1f}% of total). "
            f"Top subscriptions: {', '.join(merchant_names)}."
        )

        return True, rationale

    def check_persona_4_savings_builder(
        self,
        savings_signals_30d: Dict[str, Any],
        savings_signals_180d: Dict[str, Any],
        credit_signals_30d: Dict[str, Any],
        credit_signals_180d: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Check if user matches Persona 4: Savings Builder.

        Criteria:
        - (Savings growth rate ≥2% over window OR net savings inflow ≥$200/month) AND
        - All card utilizations < 30%

        Args:
            savings_signals_30d: Savings signals for 30-day window
            savings_signals_180d: Savings signals for 180-day window
            credit_signals_30d: Credit signals for 30-day window
            credit_signals_180d: Credit signals for 180-day window

        Returns:
            Tuple of (matches, rationale)
        """
        # Use 180-day window for savings growth (more reliable)
        savings_signals = savings_signals_180d if savings_signals_180d else savings_signals_30d
        credit_signals = credit_signals_180d if credit_signals_180d else credit_signals_30d

        if not savings_signals:
            return False, ""

        # Check savings growth rate ≥2% OR net savings inflow ≥$200/month
        savings_growth_rate = savings_signals.get("savings_growth_rate_percent", None)
        net_inflow = savings_signals.get("net_inflow_monthly", None)

        has_savings_activity = False
        savings_reason = ""

        if savings_growth_rate is not None and savings_growth_rate >= 2.0:
            has_savings_activity = True
            savings_reason = f"savings growth rate of {savings_growth_rate:.2f}%"
        elif net_inflow is not None and net_inflow >= 200:
            has_savings_activity = True
            savings_reason = f"monthly savings inflow of ${net_inflow:.2f}"

        if not has_savings_activity:
            return False, ""

        # Check all card utilizations < 30%
        if credit_signals:
            high_util_cards = credit_signals.get("high_utilization_cards", [])
            critical_cards = credit_signals.get("critical_utilization_cards", [])
            severe_cards = credit_signals.get("severe_utilization_cards", [])

            # If any card has utilization ≥30%, don't match
            if high_util_cards or critical_cards or severe_cards:
                return False, ""

        # Build rationale
        rationale = (
            f"Savings builder pattern detected: {savings_reason}. "
            f"All credit card utilizations are below 30%."
        )

        return True, rationale

    def assign_persona(
        self,
        user_id: uuid.UUID,
        signals_30d: Optional[Dict[str, Any]] = None,
        signals_180d: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Assign persona to user based on detected signals.

        Priority logic:
        1. Check Persona 1 (High Utilization) → Assign if criteria met
        2. If not Persona 1, check Persona 2 (Variable Income Budgeter)
        3. If not Persona 2, check Persona 3 (Subscription-Heavy)
        4. If not Persona 3, check Persona 4 (Savings Builder)
        5. If not Persona 4, assign Persona 5 (Custom Persona)

        Args:
            user_id: User ID
            signals_30d: Optional pre-computed signals for 30-day window
            signals_180d: Optional pre-computed signals for 180-day window

        Returns:
            Dictionary with persona assignment details
        """
        logger.info(f"Assigning persona for user {user_id}")

        # Check consent before processing
        try:
            self.consent_guardrails.require_consent(user_id, "persona_assignment")
        except ConsentError as e:
            logger.warning(f"Persona assignment blocked: {str(e)}")
            raise

        # Generate signals if not provided
        if signals_30d is None or signals_180d is None:
            subscription_signals = self.subscription_detector.generate_subscription_signals(user_id)
            savings_signals = self.savings_detector.generate_savings_signals(user_id)
            credit_signals = self.credit_detector.generate_credit_signals(user_id)
            income_signals = self.income_detector.generate_income_signals(user_id)

            signals_30d = {
                "subscriptions": subscription_signals.get("signals_30d", {}),
                "savings": savings_signals.get("signals_30d", {}),
                "credit": credit_signals.get("signals_30d", {}),
                "income": income_signals.get("signals_30d", {}),
            }

            signals_180d = {
                "subscriptions": subscription_signals.get("signals_180d", {}),
                "savings": savings_signals.get("signals_180d", {}),
                "credit": credit_signals.get("signals_180d", {}),
                "income": income_signals.get("signals_180d", {}),
            }
        else:
            # Extract signals from provided dictionaries
            signals_30d = {
                "subscriptions": signals_30d.get("subscriptions", {}),
                "savings": signals_30d.get("savings", {}),
                "credit": signals_30d.get("credit", {}),
                "income": signals_30d.get("income", {}),
            }

            signals_180d = {
                "subscriptions": signals_180d.get("subscriptions", {}),
                "savings": signals_180d.get("savings", {}),
                "credit": signals_180d.get("credit", {}),
                "income": signals_180d.get("income", {}),
            }

        # Apply priority logic
        persona_id = None
        persona_name = None
        rationale = ""

        # Check Persona 1: High Utilization
        matches, rationale = self.check_persona_1_high_utilization(
            signals_30d.get("credit", {}),
            signals_180d.get("credit", {}),
        )
        if matches:
            persona_id = PersonaId.HIGH_UTILIZATION
            persona_name = PERSONA_DEFINITIONS[1]["name"]

        # Check Persona 2: Variable Income Budgeter
        if not persona_id:
            matches, rationale = self.check_persona_2_variable_income(
                signals_30d.get("income", {}),
                signals_180d.get("income", {}),
            )
            if matches:
                persona_id = PersonaId.VARIABLE_INCOME_BUDGETER
                persona_name = PERSONA_DEFINITIONS[2]["name"]

        # Check Persona 3: Subscription-Heavy
        if not persona_id:
            matches, rationale = self.check_persona_3_subscription_heavy(
                signals_30d.get("subscriptions", {}),
                signals_180d.get("subscriptions", {}),
            )
            if matches:
                persona_id = PersonaId.SUBSCRIPTION_HEAVY
                persona_name = PERSONA_DEFINITIONS[3]["name"]

        # Check Persona 4: Savings Builder
        if not persona_id:
            matches, rationale = self.check_persona_4_savings_builder(
                signals_30d.get("savings", {}),
                signals_180d.get("savings", {}),
                signals_30d.get("credit", {}),
                signals_180d.get("credit", {}),
            )
            if matches:
                persona_id = PersonaId.SAVINGS_BUILDER
                persona_name = PERSONA_DEFINITIONS[4]["name"]

        # Default to Persona 5: Custom Persona
        if not persona_id:
            persona_id = PersonaId.CUSTOM
            persona_name = PERSONA_DEFINITIONS[5]["name"]
            rationale = "User does not match specific persona criteria. Assigned to custom persona."

        # Enhance rationale with OpenAI if available
        if self.openai_client and self.openai_client.client:
            try:
                enhanced_rationale = self._generate_openai_rationale(
                    persona_id=persona_id,
                    persona_name=persona_name,
                    base_rationale=rationale,
                    signals_30d=signals_30d,
                    signals_180d=signals_180d,
                )
                if enhanced_rationale:
                    rationale = enhanced_rationale
                    logger.info(f"Enhanced persona rationale using OpenAI for user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to generate OpenAI rationale for persona assignment: {str(e)}")
                # Continue with rule-based rationale

        # Store persona assignment
        user_profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

        # Check if persona changed
        persona_changed = False
        if user_profile:
            if user_profile.persona_id != persona_id:
                persona_changed = True
            # Update existing profile
            user_profile.persona_id = persona_id
            user_profile.persona_name = persona_name
            # Serialize signals to ensure UUIDs are converted to strings for JSON storage
            user_profile.signals_30d = _serialize_signals_for_json(signals_30d)
            user_profile.signals_180d = _serialize_signals_for_json(signals_180d)
        else:
            # Create new profile
            # Serialize signals to ensure UUIDs are converted to strings for JSON storage
            user_profile = UserProfile(
                user_id=user_id,
                persona_id=persona_id,
                persona_name=persona_name,
                signals_30d=_serialize_signals_for_json(signals_30d),
                signals_180d=_serialize_signals_for_json(signals_180d),
            )
            persona_changed = True
            self.db.add(user_profile)

        # Track persona history if changed
        if persona_changed:
            # Serialize signals to ensure UUIDs are converted to strings for JSON storage
            serialized_signals = {
                "signals_30d": _serialize_signals_for_json(signals_30d),
                "signals_180d": _serialize_signals_for_json(signals_180d),
            }
            persona_history = PersonaHistory(
                user_id=user_id,
                persona_id=persona_id,
                persona_name=persona_name,
                signals=serialized_signals,
            )
            self.db.add(persona_history)
            logger.info(f"Persona changed for user {user_id}: {persona_name} (ID: {persona_id})")

        # Commit changes
        self.db.commit()

        return {
            "user_id": str(user_id),
            "persona_id": persona_id,
            "persona_name": persona_name,
            "rationale": rationale,
            "persona_changed": persona_changed,
            "assigned_at": datetime.utcnow().isoformat(),
        }

    def _generate_openai_rationale(
        self,
        persona_id: int,
        persona_name: str,
        base_rationale: str,
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
    ) -> Optional[str]:
        """
        Generate enhanced persona rationale using OpenAI.

        Args:
            persona_id: Persona ID (1-5)
            persona_name: Persona name
            base_rationale: Base rationale from rule-based logic
            signals_30d: 30-day behavioral signals
            signals_180d: 180-day behavioral signals

        Returns:
            Enhanced rationale string or None if generation fails
        """
        if not self.openai_client or not self.openai_client.client:
            return None

        # Build context from signals
        context_parts = [
            f"Assigned Persona: {persona_name} (ID: {persona_id})",
            f"Base Rationale: {base_rationale}",
        ]

        # Add key signal summaries
        if signals_180d:
            if signals_180d.get("credit"):
                credit = signals_180d["credit"]
                if credit.get("high_utilization_cards"):
                    context_parts.append(f"High utilization cards: {len(credit['high_utilization_cards'])}")
                if credit.get("total_interest_charges"):
                    context_parts.append(f"Interest charges: ${credit['total_interest_charges']:.2f}")

            if signals_180d.get("income"):
                income = signals_180d["income"]
                if income.get("payment_variability"):
                    var = income["payment_variability"]
                    if var.get("variability_level"):
                        context_parts.append(f"Income variability: {var['variability_level']}")

            if signals_180d.get("subscriptions"):
                subs = signals_180d["subscriptions"]
                if subs.get("recurring_merchants"):
                    context_parts.append(f"Recurring subscriptions: {len(subs['recurring_merchants'])}")

            if signals_180d.get("savings"):
                savings = signals_180d["savings"]
                if savings.get("net_inflow"):
                    context_parts.append(f"Savings net inflow: ${savings['net_inflow']:.2f}")

        context = "\n".join(context_parts)

        prompt = f"""Generate a personalized, empathetic rationale explaining why this user was assigned the "{persona_name}" persona.

Context:
{context}

Requirements:
- Write in plain, empathetic language (avoid judgmental tone)
- Cite specific data points from the signals (amounts, percentages, counts)
- Keep it empowering and educational
- Length: 2-4 sentences
- Explain what this persona means for their financial situation
- Focus on actionable insights

Generate a personalized persona rationale:"""

        try:
            enhanced_rationale = self.openai_client.generate_content(
                prompt=prompt,
                persona_id=persona_id,
                signals={"signals_180d": signals_180d},
                use_cache=True,
            )
            return enhanced_rationale
        except Exception as e:
            logger.warning(f"OpenAI rationale generation failed: {str(e)}")
            return None

