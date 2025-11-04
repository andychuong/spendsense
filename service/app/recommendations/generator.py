"""Recommendation generation service."""

import logging
import uuid
import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.recommendations.catalog import (
    EDUCATION_CATALOG,
    PARTNER_OFFER_CATALOG,
    REGULATORY_DISCLAIMER,
)
from app.recommendations.rationale import RationaleGenerator
from app.recommendations.content_generator import ContentGenerator
from app.recommendations.partner_offer_service import PartnerOfferService
from app.recommendations.decision_trace import DecisionTraceGenerator
from app.common.consent_guardrails import ConsentGuardrails, ConsentError
from app.common.eligibility_guardrails import EligibilityGuardrails, EligibilityError
from app.common.tone_validation_guardrails import ToneValidationGuardrails, ToneError

# Try to import models from backend
try:
    from backend.app.models.user_profile import UserProfile, PersonaId
    from backend.app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus
    from backend.app.models.account import Account as AccountModel
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.user_profile import UserProfile, PersonaId
    from app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus
    from app.models.account import Account as AccountModel

logger = logging.getLogger(__name__)


class RecommendationGenerator:
    """Service for generating personalized recommendations based on persona and signals."""

    def __init__(self, db_session: Session, use_openai: bool = True):
        """
        Initialize recommendation generator.

        Args:
            db_session: SQLAlchemy database session
            use_openai: Whether to use OpenAI for content generation (default: True)
        """
        self.db = db_session
        self.rationale_generator = RationaleGenerator(db_session)
        self.content_generator = ContentGenerator()
        self.partner_offer_service = PartnerOfferService(db_session)
        self.consent_guardrails = ConsentGuardrails(db_session)
        self.eligibility_guardrails = EligibilityGuardrails(db_session)
        self.tone_validation_guardrails = ToneValidationGuardrails(db_session, use_openai=use_openai)
        self.decision_trace_generator = DecisionTraceGenerator()
        self.use_openai = use_openai

    def get_user_profile(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Get user profile with persona assignment."""
        return self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

    def get_user_accounts(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get user accounts to check for existing products."""
        accounts = self.db.query(AccountModel).filter(
            AccountModel.user_id == user_id
        ).all()

        return [
            {
                "account_id": str(acc.account_id),
                "type": acc.type,
                "subtype": acc.subtype,
                "name": acc.name,
            }
            for acc in accounts
        ]

    def check_existing_products(self, user_id: uuid.UUID) -> Dict[str, bool]:
        """
        Check what products user already has.

        Returns:
            Dictionary with product flags
        """
        accounts = self.get_user_accounts(user_id)

        has_credit_card = any(
            acc["type"] == "credit" or acc["subtype"] in ["credit card", "paypal"]
            for acc in accounts
        )

        has_savings = any(
            acc["type"] == "depository" and acc["subtype"] in ["savings", "money market", "hsa"]
            for acc in accounts
        )

        has_high_yield_savings = any(
            acc["type"] == "depository" and acc["subtype"] == "savings"
            for acc in accounts
        )  # Simplified check - in real system, would check APY

        return {
            "credit_card": has_credit_card,
            "savings": has_savings,
            "high_yield_savings": has_high_yield_savings,
        }

    def select_education_items(
        self,
        persona_id: int,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Select education items matching persona.

        Args:
            persona_id: Persona ID (1-5)
            count: Number of items to select (default 5, will be capped at 3-5)

        Returns:
            List of education item dictionaries
        """
        # Filter education items for this persona
        matching_items = [
            item for item in EDUCATION_CATALOG
            if persona_id in item["persona_ids"]
        ]

        # If not enough items for this persona, include general items (Persona 5)
        if len(matching_items) < count:
            general_items = [
                item for item in EDUCATION_CATALOG
                if 5 in item["persona_ids"] and item not in matching_items
            ]
            matching_items.extend(general_items[:count - len(matching_items)])

        # Select random items (or all if fewer than count)
        selected = random.sample(
            matching_items,
            min(count, len(matching_items))
        ) if matching_items else []

        # Ensure we return 3-5 items
        if len(selected) < 3:
            # Add more general items if needed
            general_items = [
                item for item in EDUCATION_CATALOG
                if 5 in item["persona_ids"] and item not in selected
            ]
            selected.extend(general_items[:3 - len(selected)])

        # Cap at 5 items
        selected = selected[:5]

        return selected

    def select_partner_offers(
        self,
        persona_id: int,
        user_id: uuid.UUID,
        signals_30d: Optional[Dict[str, Any]] = None,
        signals_180d: Optional[Dict[str, Any]] = None,
        count: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Select partner offers matching persona and eligibility.

        Args:
            persona_id: Persona ID (1-5)
            user_id: User ID
            signals_30d: Optional 30-day signals
            signals_180d: Optional 180-day signals
            count: Number of offers to select (default 3, will be capped at 1-3)

        Returns:
            List of partner offer dictionaries with eligibility information
        """
        # Use PartnerOfferService to select eligible offers
        return self.partner_offer_service.select_eligible_offers(
            persona_id,
            user_id,
            signals_30d,
            signals_180d,
            count,
        )

    def generate_recommendations(
        self,
        user_id: uuid.UUID,
        signals_30d: Optional[Dict[str, Any]] = None,
        signals_180d: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate recommendations for a user.

        Args:
            user_id: User ID
            signals_30d: Optional pre-computed signals for 30-day window
            signals_180d: Optional pre-computed signals for 180-day window

        Returns:
            Dictionary with recommendation generation results
        """
        logger.info(f"Generating recommendations for user {user_id}")

        # Track generation start time
        generation_start_time = time.time()

        # Check consent before processing
        consent_check_time = datetime.utcnow().isoformat() + "Z"
        try:
            consent_status = self.consent_guardrails.check_consent(
                user_id,
                "recommendation_generation",
                raise_on_failure=True,
            )
        except ConsentError as e:
            logger.warning(f"Recommendation generation blocked: {str(e)}")
            return {
                "user_id": str(user_id),
                "recommendations": [],
                "error": "Consent is required for recommendation generation. Please grant consent first.",
                "consent_required": True,
            }

        # Get user profile
        profile = self.get_user_profile(user_id)
        if not profile:
            logger.warning(f"No profile found for user {user_id}")
            return {
                "user_id": str(user_id),
                "recommendations": [],
                "error": "No profile found. Please run persona assignment first.",
            }

        persona_id = profile.persona_id
        persona_name = profile.persona_name

        # Get signals from profile if not provided
        if signals_30d is None:
            signals_30d = profile.signals_30d or {}
        if signals_180d is None:
            signals_180d = profile.signals_180d or {}

        # Extract persona assignment info (criteria_met from signals)
        persona_assignment_info = self._extract_persona_assignment_info(
            persona_id,
            persona_name,
            signals_30d,
            signals_180d,
        )

        # Select education items (3-5)
        education_items = self.select_education_items(persona_id, count=5)

        # Select partner offers (1-3) with eligibility checking
        partner_offers = self.select_partner_offers(
            persona_id,
            user_id,
            signals_30d,
            signals_180d,
            count=3,
        )

        # Get existing products for decision trace
        existing_products = self.check_existing_products(user_id)

        # Filter education items and partner offers through eligibility guardrails
        eligible_education_items = []
        for item in education_items:
            try:
                is_eligible, explanation = self.eligibility_guardrails.check_eligibility(
                    item,
                    user_id,
                    signals_30d,
                    signals_180d,
                    raise_on_failure=False,
                )
                if is_eligible:
                    eligible_education_items.append(item)
                else:
                    logger.info(f"Education item {item.get('id')} filtered by eligibility: {explanation}")
            except Exception as e:
                logger.warning(f"Error checking eligibility for education item {item.get('id')}: {e}")
                # Include item if eligibility check fails (graceful degradation)
                eligible_education_items.append(item)

        # Partner offers are already filtered by PartnerOfferService, but we'll double-check
        eligible_partner_offers = []
        for offer in partner_offers:
            try:
                is_eligible, explanation = self.eligibility_guardrails.check_eligibility(
                    offer,
                    user_id,
                    signals_30d,
                    signals_180d,
                    raise_on_failure=False,
                )
                if is_eligible:
                    eligible_partner_offers.append(offer)
                else:
                    logger.info(f"Partner offer {offer.get('id')} filtered by eligibility: {explanation}")
            except Exception as e:
                logger.warning(f"Error checking eligibility for partner offer {offer.get('id')}: {e}")
                # Include offer if eligibility check fails (graceful degradation)
                eligible_partner_offers.append(offer)

        # Generate recommendations
        recommendations = []

        # Generate education recommendations
        for item in eligible_education_items:
            item_start_time = time.time()
            rationale = self.rationale_generator.generate_rationale(
                item,
                signals_30d,
                signals_180d,
                persona_id,
                user_id,
            )

            # Add regulatory disclaimer
            rationale += f"\n\n{REGULATORY_DISCLAIMER}"

            # Generate content using OpenAI (with fallback to template)
            content = self.content_generator.generate_education_content(
                item,
                persona_id,
                signals_30d,
                use_openai=self.use_openai,
            )

            # Validate tone for content and rationale
            combined_text = f"{content}\n\n{rationale}"
            tone_valid, tone_explanation, tone_score = self.tone_validation_guardrails.validate_tone(
                combined_text,
                user_id,
                item.get("id"),
                raise_on_failure=False,
            )

            if not tone_valid:
                logger.warning(
                    f"Education item {item.get('id')} failed tone validation: {tone_explanation}. "
                    f"Still generating recommendation but tone needs improvement."
                )

            # Check eligibility for education item
            is_eligible, eligibility_explanation = self.eligibility_guardrails.check_eligibility(
                item,
                user_id,
                signals_30d,
                signals_180d,
                raise_on_failure=False,
            )

            # Get eligibility details
            eligibility_details = {}
            if not is_eligible:
                eligibility_details = {
                    "explanation": eligibility_explanation,
                }

            # Create guardrails info
            guardrails_info = self.decision_trace_generator.create_guardrails_info(
                consent_status=True,  # Already checked above
                consent_check_timestamp=consent_check_time,
                eligibility_status=is_eligible,
                eligibility_explanation=eligibility_explanation if not is_eligible else None,
                eligibility_details=eligibility_details if not is_eligible else None,
                tone_valid=tone_valid,
                tone_score=tone_score,
                tone_explanation=tone_explanation,
                disclaimer_present=True,
                disclaimer_text=REGULATORY_DISCLAIMER,
            )

            # Calculate generation time for this recommendation
            item_generation_time_ms = (time.time() - item_start_time) * 1000

            # Create recommendation
            recommendation = Recommendation(
                user_id=user_id,
                type=RecommendationType.EDUCATION,
                title=item["title"],
                content=content,
                rationale=rationale,
                status=RecommendationStatus.PENDING,
            )
            self.db.add(recommendation)
            self.db.flush()  # Flush to get recommendation_id

            # Create comprehensive decision trace
            decision_trace = self.decision_trace_generator.create_decision_trace(
                user_id=user_id,
                recommendation_id=recommendation.recommendation_id,
                recommendation_type="education",
                persona_id=persona_id,
                persona_name=persona_name,
                persona_assignment_info=persona_assignment_info,
                signals_30d=signals_30d,
                signals_180d=signals_180d,
                guardrails=guardrails_info,
                generation_time_ms=item_generation_time_ms,
                recommendation_metadata={
                    "title": item["title"],
                    "content_preview": content[:200] + "..." if len(content) > 200 else content,
                    "rationale_preview": rationale[:200] + "..." if len(rationale) > 200 else rationale,
                },
            )

            # Update recommendation with decision trace
            recommendation.decision_trace = decision_trace

            recommendations.append({
                "recommendation_id": str(recommendation.recommendation_id),
                "type": "education",
                "title": item["title"],
            })

        # Generate partner offer recommendations
        for offer in eligible_partner_offers:
            offer_start_time = time.time()
            rationale = self.rationale_generator.generate_rationale(
                offer,
                signals_30d,
                signals_180d,
                persona_id,
                user_id,
            )

            # Add regulatory disclaimer
            rationale += f"\n\n{REGULATORY_DISCLAIMER}"

            # Generate content using OpenAI (with fallback to template)
            content = self.content_generator.generate_partner_offer_content(
                offer,
                persona_id,
                signals_30d,
                use_openai=self.use_openai,
            )

            # Validate tone for content and rationale
            combined_text = f"{content}\n\n{rationale}"
            tone_valid, tone_explanation, tone_score = self.tone_validation_guardrails.validate_tone(
                combined_text,
                user_id,
                offer.get("id"),
                raise_on_failure=False,
            )

            if not tone_valid:
                logger.warning(
                    f"Partner offer {offer.get('id')} failed tone validation: {tone_explanation}. "
                    f"Still generating recommendation but tone needs improvement."
                )

            # Get eligibility information from offer
            eligibility_status = offer.get("eligibility_status", "eligible") == "eligible"
            eligibility_explanation = offer.get("eligibility_explanation", "")
            eligibility_details = {
                "estimated_income": offer.get("estimated_income"),
                "estimated_credit_score": offer.get("estimated_credit_score"),
                "eligibility_requirements": offer.get("eligibility_requirements", {}),
                "existing_products": existing_products,
            }

            # Create guardrails info
            guardrails_info = self.decision_trace_generator.create_guardrails_info(
                consent_status=True,  # Already checked above
                consent_check_timestamp=consent_check_time,
                eligibility_status=eligibility_status,
                eligibility_explanation=eligibility_explanation if not eligibility_status else None,
                eligibility_details=eligibility_details,
                tone_valid=tone_valid,
                tone_score=tone_score,
                tone_explanation=tone_explanation,
                disclaimer_present=True,
                disclaimer_text=REGULATORY_DISCLAIMER,
            )

            # Calculate generation time for this recommendation
            offer_generation_time_ms = (time.time() - offer_start_time) * 1000

            # Create recommendation
            recommendation = Recommendation(
                user_id=user_id,
                type=RecommendationType.PARTNER_OFFER,
                title=offer["title"],
                content=content,
                rationale=rationale,
                status=RecommendationStatus.PENDING,
            )
            self.db.add(recommendation)
            self.db.flush()  # Flush to get recommendation_id

            # Create comprehensive decision trace
            decision_trace = self.decision_trace_generator.create_decision_trace(
                user_id=user_id,
                recommendation_id=recommendation.recommendation_id,
                recommendation_type="partner_offer",
                persona_id=persona_id,
                persona_name=persona_name,
                persona_assignment_info=persona_assignment_info,
                signals_30d=signals_30d,
                signals_180d=signals_180d,
                guardrails=guardrails_info,
                generation_time_ms=offer_generation_time_ms,
                recommendation_metadata={
                    "title": offer["title"],
                    "content_preview": content[:200] + "..." if len(content) > 200 else content,
                    "rationale_preview": rationale[:200] + "..." if len(rationale) > 200 else rationale,
                },
            )

            # Update recommendation with decision trace
            recommendation.decision_trace = decision_trace

            recommendations.append({
                "recommendation_id": str(recommendation.recommendation_id),
                "type": "partner_offer",
                "title": offer["title"],
            })

        # Commit recommendations
        self.db.commit()

        # Calculate total generation time
        total_generation_time_ms = (time.time() - generation_start_time) * 1000

        logger.info(
            f"Generated {len(recommendations)} recommendations for user {user_id}: "
            f"{len(eligible_education_items)} education (from {len(education_items)} selected), "
            f"{len(eligible_partner_offers)} partner offers (from {len(partner_offers)} selected) "
            f"in {total_generation_time_ms:.2f}ms"
        )

        return {
            "user_id": str(user_id),
            "persona_id": persona_id,
            "persona_name": persona_name,
            "recommendations": recommendations,
            "education_count": len(eligible_education_items),
            "partner_offer_count": len(eligible_partner_offers),
            "education_selected": len(education_items),
            "partner_offers_selected": len(partner_offers),
            "generated_at": datetime.utcnow().isoformat(),
            "generation_time_ms": total_generation_time_ms,
        }

    def _extract_persona_assignment_info(
        self,
        persona_id: int,
        persona_name: str,
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract persona assignment information for decision trace.

        Args:
            persona_id: Persona ID
            persona_name: Persona name
            signals_30d: Signals for 30-day window
            signals_180d: Signals for 180-day window

        Returns:
            Persona assignment info dictionary
        """
        criteria_met = []

        # Persona priority mapping
        persona_priority = {
            1: 1,  # High Utilization
            2: 2,  # Variable Income Budgeter
            3: 3,  # Subscription-Heavy
            4: 4,  # Savings Builder
            5: 5,  # Custom Persona
        }

        # Extract criteria met based on persona
        if persona_id == 1:  # High Utilization
            credit_signals = signals_30d.get("credit", {}) or signals_180d.get("credit", {})
            if credit_signals.get("critical_utilization_cards") or credit_signals.get("severe_utilization_cards"):
                criteria_met.append("Credit card utilization ≥50%")
            if credit_signals.get("cards_with_interest"):
                criteria_met.append("Interest charges detected")
            if credit_signals.get("minimum_payment_only_cards"):
                criteria_met.append("Minimum-payment-only behavior")
            if credit_signals.get("overdue_cards"):
                criteria_met.append("Overdue accounts")

        elif persona_id == 2:  # Variable Income Budgeter
            income_signals = signals_180d.get("income", {}) or signals_30d.get("income", {})
            income_patterns = income_signals.get("income_patterns", {})
            median_pay_gap = income_patterns.get("median_pay_gap_days")
            cash_flow_buffer = income_signals.get("cash_flow_buffer_months")

            if median_pay_gap and median_pay_gap > 45:
                criteria_met.append(f"Median pay gap > 45 days ({median_pay_gap:.0f} days)")
            if cash_flow_buffer is not None and cash_flow_buffer < 1.0:
                criteria_met.append(f"Cash-flow buffer < 1 month ({cash_flow_buffer:.2f} months)")

        elif persona_id == 3:  # Subscription-Heavy
            subscription_signals = signals_30d.get("subscriptions", {}) or signals_180d.get("subscriptions", {})
            subscription_count = subscription_signals.get("subscription_count", 0)
            total_recurring_spend = subscription_signals.get("total_recurring_spend", 0)
            subscription_share = subscription_signals.get("subscription_share_percent", 0)

            if subscription_count >= 3:
                criteria_met.append(f"Recurring merchants ≥3 ({subscription_count})")
            if total_recurring_spend >= 50:
                criteria_met.append(f"Monthly recurring spend ≥$50 (${total_recurring_spend:.2f})")
            if subscription_share >= 10:
                criteria_met.append(f"Subscription share ≥10% ({subscription_share:.1f}%)")

        elif persona_id == 4:  # Savings Builder
            savings_signals = signals_180d.get("savings", {}) or signals_30d.get("savings", {})
            credit_signals = signals_180d.get("credit", {}) or signals_30d.get("credit", {})

            savings_growth_rate = savings_signals.get("savings_growth_rate_percent")
            net_inflow = savings_signals.get("net_inflow_monthly")

            if savings_growth_rate and savings_growth_rate >= 2.0:
                criteria_met.append(f"Savings growth rate ≥2% ({savings_growth_rate:.2f}%)")
            if net_inflow and net_inflow >= 200:
                criteria_met.append(f"Net savings inflow ≥$200/month (${net_inflow:.2f})")

            # Check all utilizations < 30%
            high_util_cards = credit_signals.get("high_utilization_cards", [])
            critical_cards = credit_signals.get("critical_utilization_cards", [])
            severe_cards = credit_signals.get("severe_utilization_cards", [])
            if not (high_util_cards or critical_cards or severe_cards):
                criteria_met.append("All card utilizations < 30%")

        else:  # Persona 5: Custom Persona
            criteria_met.append("User does not match specific persona criteria")

        return {
            "persona_id": persona_id,
            "persona_name": persona_name,
            "criteria_met": criteria_met,
            "priority": persona_priority.get(persona_id, 5),
            "rationale": f"Assigned to {persona_name} persona based on detected behavioral signals.",
            "persona_changed": False,  # Could be determined from profile history if needed
        }

