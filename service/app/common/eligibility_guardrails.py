"""Eligibility guardrails service for validating recommendation eligibility."""

import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

# Try to import models from backend
try:
    from backend.app.models.transaction import Transaction
    from backend.app.models.account import Account as AccountModel
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.transaction import Transaction
    from app.models.account import Account as AccountModel

logger = logging.getLogger(__name__)

# Harmful product keywords to filter out
HARMFUL_PRODUCT_KEYWORDS = [
    "payday loan",
    "payday",
    "predatory loan",
    "title loan",
    "cash advance",
    "check cashing",
    "pawn shop",
    "rent-to-own",
]


class EligibilityError(Exception):
    """Exception raised when eligibility check fails."""
    pass


class EligibilityGuardrails:
    """Service for enforcing eligibility guardrails before recommendation generation."""

    def __init__(self, db_session: Session):
        """
        Initialize eligibility guardrails service.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def get_user_accounts(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Get user accounts to check for existing products.

        Args:
            user_id: User ID

        Returns:
            List of account dictionaries
        """
        accounts = self.db.query(AccountModel).filter(
            AccountModel.user_id == user_id
        ).all()

        return [
            {
                "account_id": str(acc.account_id),
                "type": acc.type,
                "subtype": acc.subtype,
                "name": acc.name,
                "mask": acc.mask,
            }
            for acc in accounts
        ]

    def check_existing_products(self, user_id: uuid.UUID) -> Dict[str, bool]:
        """
        Check what products user already has.

        Args:
            user_id: User ID

        Returns:
            Dictionary with product flags:
            - credit_card: Has credit card
            - savings: Has savings account
            - high_yield_savings: Has high-yield savings account
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

        # Check for high-yield savings (simplified - in real system would check APY)
        # For now, check if they have a savings account with a bank name that typically offers high yield
        high_yield_banks = ["ally", "marcus", "discover", "capital one", "american express"]
        has_high_yield_savings = any(
            acc["type"] == "depository" and acc["subtype"] == "savings"
            and any(bank in acc.get("name", "").lower() for bank in high_yield_banks)
            for acc in accounts
        )

        return {
            "credit_card": has_credit_card,
            "savings": has_savings,
            "high_yield_savings": has_high_yield_savings,
        }

    def calculate_income_from_transactions(
        self,
        user_id: uuid.UUID,
        months: int = 6,
    ) -> Optional[float]:
        """
        Calculate estimated monthly income from payroll deposits.

        Args:
            user_id: User ID
            months: Number of months to look back (default 6)

        Returns:
            Estimated monthly income (average) or None if no payroll deposits found
        """
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=months * 30)

        # Get checking accounts
        checking_accounts = self.db.query(AccountModel).filter(
            and_(
                AccountModel.user_id == user_id,
                AccountModel.type == "depository",
                AccountModel.subtype == "checking",
            )
        ).all()

        if not checking_accounts:
            logger.warning(f"No checking accounts found for user {user_id}")
            return None

        account_ids = [acc.account_id for acc in checking_accounts]

        # Get payroll deposits
        payroll_deposits = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.account_id.in_(account_ids),
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.amount > 0,  # Deposits are positive
                Transaction.personal_finance_category == "PAYROLL",
            )
        ).all()

        if not payroll_deposits:
            logger.warning(f"No payroll deposits found for user {user_id} in last {months} months")
            return None

        # Calculate total deposits and average monthly income
        total_deposits = sum(float(dep.amount) for dep in payroll_deposits)
        days_diff = (end_date - start_date).days
        months_covered = days_diff / 30.0

        if months_covered > 0:
            monthly_income = total_deposits / months_covered
            logger.info(f"Calculated monthly income for user {user_id}: ${monthly_income:.2f} (from {len(payroll_deposits)} deposits)")
            return monthly_income

        return None

    def estimate_credit_score(
        self,
        user_id: uuid.UUID,
        signals_30d: Optional[Dict[str, Any]] = None,
        signals_180d: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """
        Estimate credit score based on credit utilization and payment behavior.

        Note: This is a rough estimate and not a replacement for actual credit score.
        In production, you would integrate with a credit bureau API.

        Args:
            user_id: User ID
            signals_30d: Optional 30-day signals
            signals_180d: Optional 180-day signals

        Returns:
            Estimated credit score (300-850) or None if cannot estimate
        """
        # Use 30-day signals if available, otherwise 180-day
        signals = signals_30d or signals_180d or {}
        credit_signals = signals.get("credit", {})

        if not credit_signals:
            logger.warning(f"No credit signals available for user {user_id}")
            return None

        # Base score starts at 650 (average)
        estimated_score = 650

        # Adjust based on utilization
        high_util_cards = credit_signals.get("high_utilization_cards_30d", [])
        critical_cards = credit_signals.get("critical_utilization_cards", [])
        severe_cards = credit_signals.get("severe_utilization_cards", [])

        if severe_cards:
            # Severe utilization (≥80%) - reduce score significantly
            estimated_score -= 80
        elif critical_cards:
            # Critical utilization (≥50%) - reduce score moderately
            estimated_score -= 50
        elif high_util_cards:
            # High utilization (≥30%) - reduce score slightly
            estimated_score -= 20

        # Check for interest charges (indicates carrying balance)
        interest_charges = credit_signals.get("interest_charges_30d", [])
        if interest_charges:
            estimated_score -= 30

        # Check for minimum payment only behavior
        min_payment_only = credit_signals.get("minimum_payment_only_30d", [])
        if min_payment_only:
            estimated_score -= 20

        # Check for overdue accounts
        overdue_accounts = credit_signals.get("overdue_accounts_30d", [])
        if overdue_accounts:
            estimated_score -= 100  # Significant negative impact

        # Clamp score to valid range (300-850)
        estimated_score = max(300, min(850, estimated_score))

        logger.info(f"Estimated credit score for user {user_id}: {estimated_score}")
        return estimated_score

    def is_harmful_product(self, recommendation: Dict[str, Any]) -> bool:
        """
        Check if a recommendation is a harmful product (payday loans, etc.).

        Args:
            recommendation: Recommendation dictionary (can be education item or partner offer)

        Returns:
            True if recommendation is harmful, False otherwise
        """
        # Check title and content for harmful keywords
        title_lower = recommendation.get("title", "").lower()
        content_lower = recommendation.get("content", "").lower()

        for keyword in HARMFUL_PRODUCT_KEYWORDS:
            if keyword in title_lower or keyword in content_lower:
                logger.warning(f"Detected harmful product: {recommendation.get('id')} - {recommendation.get('title')}")
                return True

        return False

    def check_eligibility(
        self,
        recommendation: Dict[str, Any],
        user_id: uuid.UUID,
        signals_30d: Optional[Dict[str, Any]] = None,
        signals_180d: Optional[Dict[str, Any]] = None,
        raise_on_failure: bool = False,
    ) -> Tuple[bool, str]:
        """
        Check if user is eligible for a recommendation.

        This method performs comprehensive eligibility checks:
        - Harmful product filtering
        - Existing products filtering
        - Minimum income requirements
        - Minimum credit score requirements

        Args:
            recommendation: Recommendation dictionary (education item or partner offer)
            user_id: User ID
            signals_30d: Optional 30-day signals
            signals_180d: Optional 180-day signals
            raise_on_failure: If True, raise EligibilityError if not eligible

        Returns:
            Tuple of (is_eligible, explanation)

        Raises:
            EligibilityError: If raise_on_failure=True and recommendation not eligible
        """
        eligibility_reqs = recommendation.get("eligibility_requirements", {})

        # Check for harmful products
        if self.is_harmful_product(recommendation):
            explanation = "This product is not recommended due to predatory lending practices."
            self.log_eligibility_check(
                user_id,
                recommendation.get("id", "unknown"),
                False,
                explanation,
            )
            if raise_on_failure:
                raise EligibilityError(explanation)
            return False, explanation

        # Get existing products
        existing_products = self.check_existing_products(user_id)

        # Check blocked conditions (don't offer if user already has specific products)
        blocked_if = eligibility_reqs.get("blocked_if", [])
        for blocked_product in blocked_if:
            if existing_products.get(blocked_product, False):
                explanation = f"You already have a {blocked_product.replace('_', ' ')}. This offer is not applicable."
                self.log_eligibility_check(
                    user_id,
                    recommendation.get("id", "unknown"),
                    False,
                    explanation,
                )
                if raise_on_failure:
                    raise EligibilityError(explanation)
                return False, explanation

        # Calculate income and credit score if needed
        estimated_income = None
        estimated_credit_score = None

        min_income = eligibility_reqs.get("min_income")
        min_credit_score = eligibility_reqs.get("min_credit_score")

        if min_income is not None or min_credit_score is not None:
            # Calculate income if needed
            if min_income is not None:
                estimated_income = self.calculate_income_from_transactions(user_id)

            # Estimate credit score if needed
            if min_credit_score is not None:
                estimated_credit_score = self.estimate_credit_score(
                    user_id,
                    signals_30d,
                    signals_180d,
                )

        # Check minimum credit score
        if min_credit_score is not None:
            if estimated_credit_score is None:
                explanation = "Credit score information is not available. Please check your credit score to determine eligibility."
                self.log_eligibility_check(
                    user_id,
                    recommendation.get("id", "unknown"),
                    False,
                    explanation,
                )
                if raise_on_failure:
                    raise EligibilityError(explanation)
                return False, explanation

            if estimated_credit_score < min_credit_score:
                explanation = f"This offer requires a credit score of {min_credit_score}+. Your estimated credit score is {estimated_credit_score}."
                self.log_eligibility_check(
                    user_id,
                    recommendation.get("id", "unknown"),
                    False,
                    explanation,
                )
                if raise_on_failure:
                    raise EligibilityError(explanation)
                return False, explanation

        # Check minimum income
        if min_income is not None:
            if estimated_income is None:
                explanation = "Income information is not available. Please verify your income to determine eligibility."
                self.log_eligibility_check(
                    user_id,
                    recommendation.get("id", "unknown"),
                    False,
                    explanation,
                )
                if raise_on_failure:
                    raise EligibilityError(explanation)
                return False, explanation

            if estimated_income < min_income:
                explanation = f"This offer requires a minimum monthly income of ${min_income:,.2f}. Your estimated monthly income is ${estimated_income:,.2f}."
                self.log_eligibility_check(
                    user_id,
                    recommendation.get("id", "unknown"),
                    False,
                    explanation,
                )
                if raise_on_failure:
                    raise EligibilityError(explanation)
                return False, explanation

        # Build eligibility explanation
        explanation_parts = []

        if min_credit_score is not None:
            if estimated_credit_score is None:
                explanation_parts.append(f"Credit score check: Information not available")
            elif estimated_credit_score >= min_credit_score:
                explanation_parts.append(f"Credit score check: ✓ ({estimated_credit_score} ≥ {min_credit_score})")
            else:
                explanation_parts.append(f"Credit score check: ✗ ({estimated_credit_score} < {min_credit_score})")

        if min_income is not None:
            if estimated_income is None:
                explanation_parts.append(f"Income check: Information not available")
            elif estimated_income >= min_income:
                explanation_parts.append(f"Income check: ✓ (${estimated_income:,.2f} ≥ ${min_income:,.2f})")
            else:
                explanation_parts.append(f"Income check: ✗ (${estimated_income:,.2f} < ${min_income:,.2f})")

        # Check required products
        required_products = eligibility_reqs.get("existing_products", [])
        if required_products:
            has_required = any(
                existing_products.get(product, False)
                for product in required_products
            )
            if has_required:
                explanation_parts.append(f"Product requirement: ✓ (You have required products)")
            else:
                explanation_parts.append(f"Product requirement: Note - This offer may require existing products")

        if not explanation_parts:
            explanation_parts.append("No specific eligibility requirements.")

        explanation = " | ".join(explanation_parts)

        # Log successful eligibility check
        self.log_eligibility_check(
            user_id,
            recommendation.get("id", "unknown"),
            True,
            explanation,
        )

        return True, explanation

    def require_eligibility(
        self,
        recommendation: Dict[str, Any],
        user_id: uuid.UUID,
        signals_30d: Optional[Dict[str, Any]] = None,
        signals_180d: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Require eligibility for a recommendation.

        Raises EligibilityError if recommendation is not eligible.

        Args:
            recommendation: Recommendation dictionary
            user_id: User ID
            signals_30d: Optional 30-day signals
            signals_180d: Optional 180-day signals

        Raises:
            EligibilityError: If recommendation not eligible
        """
        self.check_eligibility(
            recommendation,
            user_id,
            signals_30d,
            signals_180d,
            raise_on_failure=True,
        )

    def log_eligibility_check(
        self,
        user_id: uuid.UUID,
        recommendation_id: str,
        is_eligible: bool,
        explanation: str,
        details: Optional[str] = None,
    ) -> None:
        """
        Log an eligibility check event.

        Args:
            user_id: User ID
            recommendation_id: Recommendation ID
            is_eligible: Whether recommendation is eligible
            explanation: Eligibility explanation
            details: Optional additional details about the check
        """
        log_message = (
            f"Eligibility check logged: User {user_id}, Recommendation '{recommendation_id}', "
            f"Eligible: {is_eligible}, Explanation: {explanation}"
        )
        if details:
            log_message += f", Details: {details}"

        if is_eligible:
            logger.info(log_message)
        else:
            logger.warning(log_message)


