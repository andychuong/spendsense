"""Credit utilization detection service for identifying credit card utilization patterns and behaviors."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, or_

from app.common.feature_cache import (
    cache_feature_signals,
    CACHE_PREFIX_CREDIT,
    get_cached_credit_signals,
)
from app.common.consent_guardrails import ConsentGuardrails, ConsentError

logger = logging.getLogger(__name__)

# Try to import models from backend
try:
    from backend.app.models.transaction import Transaction
    from backend.app.models.account import Account
    from backend.app.models.liability import Liability
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.liability import Liability


# Utilization thresholds
UTILIZATION_THRESHOLD_HIGH = 30.0  # ≥30%
UTILIZATION_THRESHOLD_CRITICAL = 50.0  # ≥50%
UTILIZATION_THRESHOLD_SEVERE = 80.0  # ≥80%


class CreditUtilizationDetector:
    """Detects credit card utilization patterns and behaviors."""

    def __init__(self, db_session: Session):
        """
        Initialize credit utilization detector.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.consent_guardrails = ConsentGuardrails(db_session)

    def get_credit_card_accounts(
        self,
        user_id: uuid.UUID,
    ) -> List[Account]:
        """
        Get all credit card accounts for a user.

        Args:
            user_id: User ID

        Returns:
            List of credit card accounts
        """
        accounts = self.db.query(Account).filter(
            and_(
                Account.user_id == user_id,
                Account.type == "credit",
                Account.subtype == "credit card",
                Account.holder_category == "individual",
            )
        ).all()

        logger.info(f"Found {len(accounts)} credit card accounts for user {user_id}")
        return accounts

    def calculate_utilization(
        self,
        account: Account,
        liability: Optional[Liability] = None,
    ) -> Dict[str, Any]:
        """
        Calculate utilization for a credit card account.

        Utilization = (current balance / credit limit) × 100

        Args:
            account: Credit card account
            liability: Optional liability record (if available)

        Returns:
            Dictionary with utilization details
        """
        # Get credit limit from account
        credit_limit = Decimal(str(account.balance_limit)) if account.balance_limit else Decimal("0.0")

        # Get current balance (in Plaid, credit card balances are typically positive)
        # balance_current represents the amount owed (positive value)
        current_balance = Decimal(str(account.balance_current)) if account.balance_current else Decimal("0.0")

        # Calculate utilization percentage
        if credit_limit > 0:
            utilization_percent = float((current_balance / credit_limit) * 100)
        else:
            utilization_percent = 0.0

        # Determine utilization level
        utilization_level = "low"
        if utilization_percent >= UTILIZATION_THRESHOLD_SEVERE:
            utilization_level = "severe"
        elif utilization_percent >= UTILIZATION_THRESHOLD_CRITICAL:
            utilization_level = "critical"
        elif utilization_percent >= UTILIZATION_THRESHOLD_HIGH:
            utilization_level = "high"

        # Check if account has utilization flags
        flags = []
        if utilization_percent >= UTILIZATION_THRESHOLD_SEVERE:
            flags.append("utilization_≥80%")
        elif utilization_percent >= UTILIZATION_THRESHOLD_CRITICAL:
            flags.append("utilization_≥50%")
        elif utilization_percent >= UTILIZATION_THRESHOLD_HIGH:
            flags.append("utilization_≥30%")

        return {
            "account_id": account.account_id,
            "account_name": account.name,
            "mask": account.mask,
            "current_balance": float(current_balance),
            "credit_limit": float(credit_limit),
            "utilization_percent": round(utilization_percent, 2),
            "utilization_level": utilization_level,
            "flags": flags,
            "apr_percentage": float(liability.apr_percentage) if liability and liability.apr_percentage else None,
        }

    def detect_minimum_payment_only(
        self,
        account: Account,
        liability: Optional[Liability] = None,
        window_days: int = 90,
    ) -> Dict[str, Any]:
        """
        Detect if user is making minimum-payment-only payments.

        Checks if last 3 payments are approximately equal to minimum payment amount.
        Uses a tolerance of ±10% to account for rounding differences.

        Args:
            account: Credit card account
            liability: Liability record with payment information
            window_days: Time window to look for payments (default: 90 days)

        Returns:
            Dictionary with minimum payment detection details
        """
        if not liability or not liability.minimum_payment_amount:
            return {
                "is_minimum_payment_only": False,
                "reason": "No minimum payment amount available",
                "minimum_payment_amount": None,
                "payment_count": 0,
                "payments": [],
            }

        minimum_payment = Decimal(str(liability.minimum_payment_amount))
        tolerance = minimum_payment * Decimal("0.1")  # 10% tolerance

        # Look for payment transactions (positive amounts to credit card accounts)
        # Payments to credit cards are typically positive amounts (credits)
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        # Query for payment transactions
        # Payments to credit cards are credits (positive amounts)
        # Look for transactions with payment-related categories
        payment_transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == account.user_id,
                Transaction.account_id == account.id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,
                Transaction.amount > 0,  # Payments are positive amounts
                # Payment-related categories
                or_(
                    Transaction.category_primary.like("%PAYMENT%"),
                    Transaction.category_primary.like("%TRANSFER%"),
                    Transaction.merchant_name.like("%PAYMENT%"),
                ),
            )
        ).order_by(Transaction.date.desc()).limit(10).all()

        # Analyze last 3 payments
        payments = []
        minimum_payment_count = 0

        for txn in payment_transactions[:3]:  # Last 3 payments
            payment_amount = Decimal(str(abs(txn.amount)))
            is_minimum = abs(payment_amount - minimum_payment) <= tolerance

            payments.append({
                "date": txn.date.isoformat(),
                "amount": float(payment_amount),
                "is_minimum": is_minimum,
            })

            if is_minimum:
                minimum_payment_count += 1

        # Consider it minimum-payment-only if at least 2 of last 3 payments are minimum
        is_minimum_payment_only = minimum_payment_count >= 2

        return {
            "is_minimum_payment_only": is_minimum_payment_only,
            "reason": (
                f"Last {len(payments)} payments: {minimum_payment_count} were minimum payments"
                if payments
                else "No recent payments found"
            ),
            "minimum_payment_amount": float(minimum_payment),
            "payment_count": len(payments),
            "payments": payments,
        }

    def detect_interest_charges(
        self,
        account: Account,
        window_days: int = 90,
    ) -> Dict[str, Any]:
        """
        Detect interest charges on credit card account.

        Looks for transactions with category "INTEREST_CHARGE" or similar.

        Args:
            account: Credit card account
            window_days: Time window to look for interest charges (default: 90 days)

        Returns:
            Dictionary with interest charge details
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        # Query for interest charge transactions
        # Interest charges are typically negative amounts (debits)
        interest_transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == account.user_id,
                Transaction.account_id == account.id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,
                or_(
                    Transaction.category_primary == "INTEREST_CHARGE",
                    Transaction.category_primary.like("%INTEREST%"),
                    Transaction.category_detailed == "INTEREST_CHARGE",
                    Transaction.category_detailed.like("%INTEREST%"),
                    Transaction.merchant_name.like("%INTEREST%"),
                ),
            )
        ).order_by(Transaction.date.desc()).all()

        total_interest = Decimal("0.0")
        interest_charges = []

        for txn in interest_transactions:
            # Interest charges are negative amounts (expenses)
            interest_amount = abs(Decimal(str(txn.amount)))
            total_interest += interest_amount

            interest_charges.append({
                "date": txn.date.isoformat(),
                "amount": float(interest_amount),
                "category": txn.category_primary,
            })

        return {
            "has_interest_charges": len(interest_charges) > 0,
            "total_interest_charges": float(total_interest),
            "interest_count": len(interest_charges),
            "interest_charges": interest_charges,
        }

    def detect_overdue_accounts(
        self,
        account: Account,
        liability: Optional[Liability] = None,
    ) -> Dict[str, Any]:
        """
        Detect if credit card account is overdue.

        Checks liability.is_overdue flag and next_payment_due_date.

        Args:
            account: Credit card account
            liability: Liability record with overdue information

        Returns:
            Dictionary with overdue account details
        """
        if not liability:
            return {
                "is_overdue": False,
                "reason": "No liability record found",
                "next_payment_due_date": None,
            }

        is_overdue = liability.is_overdue if liability.is_overdue is not None else False

        # Also check if next_payment_due_date is in the past
        if liability.next_payment_due_date:
            days_overdue = (date.today() - liability.next_payment_due_date).days
            if days_overdue > 0 and not is_overdue:
                # Payment is past due but flag not set
                is_overdue = True

        return {
            "is_overdue": is_overdue,
            "reason": (
                f"Account flagged as overdue (next payment due: {liability.next_payment_due_date.isoformat() if liability.next_payment_due_date else 'N/A'})"
                if is_overdue
                else "Account is not overdue"
            ),
            "next_payment_due_date": (
                liability.next_payment_due_date.isoformat()
                if liability.next_payment_due_date
                else None
            ),
            "is_overdue_flag": liability.is_overdue if liability.is_overdue is not None else False,
        }

    def calculate_credit_signals(
        self,
        user_id: uuid.UUID,
        window_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Calculate credit utilization signals for a specific time window.

        Args:
            user_id: User ID
            window_days: Time window in days (30 or 180)

        Returns:
            Dictionary with credit utilization signals including:
            - credit_cards: List of credit cards with utilization details
            - high_utilization_cards: Cards with ≥30% utilization
            - critical_utilization_cards: Cards with ≥50% utilization
            - severe_utilization_cards: Cards with ≥80% utilization
            - minimum_payment_only_cards: Cards with minimum-payment-only behavior
            - cards_with_interest: Cards with interest charges
            - overdue_cards: Cards that are overdue
            - total_utilization: Weighted average utilization across all cards
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        logger.info(f"Calculating credit signals for user {user_id}, {window_days}-day window")

        # Get credit card accounts
        credit_cards = self.get_credit_card_accounts(user_id)

        if not credit_cards:
            logger.info(f"No credit card accounts found for user {user_id}")
            return {
                "window_days": window_days,
                "window_start": start_date.isoformat(),
                "window_end": end_date.isoformat(),
                "credit_cards": [],
                "high_utilization_cards": [],
                "critical_utilization_cards": [],
                "severe_utilization_cards": [],
                "minimum_payment_only_cards": [],
                "cards_with_interest": [],
                "overdue_cards": [],
                "total_utilization": 0.0,
                "total_balance": 0.0,
                "total_limit": 0.0,
            }

        # Get liabilities for credit cards
        account_ids = [acc.id for acc in credit_cards]
        liabilities = self.db.query(Liability).filter(
            Liability.account_id.in_(account_ids)
        ).all()

        # Create liability lookup
        liability_map = {liab.account_id: liab for liab in liabilities}

        # Process each credit card
        credit_card_details = []
        high_utilization = []
        critical_utilization = []
        severe_utilization = []
        minimum_payment_only = []
        cards_with_interest = []
        overdue_cards = []

        total_balance = Decimal("0.0")
        total_limit = Decimal("0.0")

        for account in credit_cards:
            liability = liability_map.get(account.id)

            # Calculate utilization
            utilization_data = self.calculate_utilization(account, liability)

            # Detect minimum payment only
            min_payment_data = self.detect_minimum_payment_only(account, liability, window_days=window_days)

            # Detect interest charges
            interest_data = self.detect_interest_charges(account, window_days=window_days)

            # Detect overdue status
            overdue_data = self.detect_overdue_accounts(account, liability)

            # Accumulate totals
            if utilization_data["credit_limit"] > 0:
                total_balance += Decimal(str(utilization_data["current_balance"]))
                total_limit += Decimal(str(utilization_data["credit_limit"]))

            # Build card details
            card_detail = {
                **utilization_data,
                "minimum_payment_only": min_payment_data,
                "interest_charges": interest_data,
                "overdue": overdue_data,
            }
            credit_card_details.append(card_detail)

            # Categorize cards
            if utilization_data["utilization_percent"] >= UTILIZATION_THRESHOLD_SEVERE:
                severe_utilization.append(card_detail)
            elif utilization_data["utilization_percent"] >= UTILIZATION_THRESHOLD_CRITICAL:
                critical_utilization.append(card_detail)
            elif utilization_data["utilization_percent"] >= UTILIZATION_THRESHOLD_HIGH:
                high_utilization.append(card_detail)

            if min_payment_data["is_minimum_payment_only"]:
                minimum_payment_only.append(card_detail)

            if interest_data["has_interest_charges"]:
                cards_with_interest.append(card_detail)

            if overdue_data["is_overdue"]:
                overdue_cards.append(card_detail)

        # Calculate total utilization (weighted average)
        total_utilization = (
            float((total_balance / total_limit) * 100)
            if total_limit > 0
            else 0.0
        )

        return {
            "window_days": window_days,
            "window_start": start_date.isoformat(),
            "window_end": end_date.isoformat(),
            "credit_cards": credit_card_details,
            "high_utilization_cards": high_utilization,
            "critical_utilization_cards": critical_utilization,
            "severe_utilization_cards": severe_utilization,
            "minimum_payment_only_cards": minimum_payment_only,
            "cards_with_interest": cards_with_interest,
            "overdue_cards": overdue_cards,
            "total_utilization": round(total_utilization, 2),
            "total_balance": float(total_balance),
            "total_limit": float(total_limit),
            "card_count": len(credit_cards),
        }

    @cache_feature_signals(CACHE_PREFIX_CREDIT)
    def generate_credit_signals(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        Generate credit utilization signals for both 30-day and 180-day windows.

        Args:
            user_id: User ID

        Returns:
            Dictionary with signals for both time windows
        """
        logger.info(f"Generating credit utilization signals for user {user_id}")

        # Check consent before processing
        try:
            self.consent_guardrails.require_consent(user_id, "feature_detection:credit")
        except ConsentError as e:
            logger.warning(f"Credit signal generation blocked: {str(e)}")
            raise

        signals_30d = self.calculate_credit_signals(user_id, window_days=30)
        signals_180d = self.calculate_credit_signals(user_id, window_days=180)

        return {
            "user_id": str(user_id),
            "generated_at": datetime.utcnow().isoformat(),
            "signals_30d": signals_30d,
            "signals_180d": signals_180d,
        }

