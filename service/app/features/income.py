"""Income stability detection service for identifying income patterns and cash flow stability."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from statistics import median
import math

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_

from app.common.feature_cache import (
    cache_feature_signals,
    CACHE_PREFIX_INCOME,
    get_cached_income_signals,
)
from app.common.consent_guardrails import ConsentGuardrails, ConsentError

logger = logging.getLogger(__name__)

# Try to import Transaction and Account models from backend
try:
    from backend.app.models.transaction import Transaction
    from backend.app.models.account import Account
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.transaction import Transaction
    from app.models.account import Account


# Checking account subtypes (for cash-flow buffer calculation)
CHECKING_ACCOUNT_SUBTYPES = ["checking"]


class IncomeStabilityDetector:
    """Detects income stability patterns and cash flow from transaction data."""

    def __init__(self, db_session: Session):
        """
        Initialize income stability detector.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.consent_guardrails = ConsentGuardrails(db_session)

    def get_checking_accounts(
        self,
        user_id: uuid.UUID,
    ) -> List[Account]:
        """
        Get all checking accounts for a user.

        Args:
            user_id: User ID

        Returns:
            List of checking accounts
        """
        accounts = self.db.query(Account).filter(
            and_(
                Account.user_id == user_id,
                Account.type == "depository",
                Account.subtype.in_(CHECKING_ACCOUNT_SUBTYPES),
                Account.holder_category == "individual",
            )
        ).all()

        logger.info(f"Found {len(accounts)} checking accounts for user {user_id}")
        return accounts

    def detect_payroll_deposits(
        self,
        user_id: uuid.UUID,
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Detect payroll ACH deposits.

        Looks for transactions with category "PAYROLL" and payment_channel "ACH".
        In Plaid, deposits are positive amounts.

        Args:
            user_id: User ID
            start_date: Start date of analysis window
            end_date: End date of analysis window

        Returns:
            List of payroll deposit transactions
        """
        logger.info(
            f"Detecting payroll deposits for user {user_id} from {start_date} to {end_date}"
        )

        # Get checking accounts
        checking_accounts = self.get_checking_accounts(user_id)

        if not checking_accounts:
            logger.info(f"No checking accounts found for user {user_id}")
            return []

        account_ids = [acc.id for acc in checking_accounts]

        # Query for payroll ACH deposits
        # Payroll deposits are positive amounts (credits)
        payroll_transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.account_id.in_(account_ids),
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,
                Transaction.amount > 0,  # Deposits are positive
                or_(
                    Transaction.category_primary == "PAYROLL",
                    Transaction.category_primary.like("%PAYROLL%"),
                    Transaction.category_detailed == "PAYROLL",
                    Transaction.category_detailed.like("%PAYROLL%"),
                ),
                Transaction.payment_channel == "ACH",
            )
        ).order_by(Transaction.date).all()

        payroll_deposits = []
        for txn in payroll_transactions:
            payroll_deposits.append({
                "date": txn.date.isoformat(),
                "amount": float(txn.amount),
                "account_id": txn.account_id,
                "transaction_id": txn.transaction_id,
                "merchant_name": txn.merchant_name,
                "category": txn.category_primary,
            })

        logger.info(f"Found {len(payroll_deposits)} payroll deposits")
        return payroll_deposits

    def calculate_payment_frequency(
        self,
        payroll_deposits: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate payment frequency (median time between payroll deposits).

        Args:
            payroll_deposits: List of payroll deposit transactions

        Returns:
            Dictionary with payment frequency details including:
            - median_gap_days: Median time between deposits in days
            - average_gap_days: Average time between deposits in days
            - gap_days: List of gaps between consecutive deposits
            - deposit_count: Number of deposits
        """
        if len(payroll_deposits) < 2:
            return {
                "median_gap_days": None,
                "average_gap_days": None,
                "gap_days": [],
                "deposit_count": len(payroll_deposits),
                "frequency_type": "insufficient_data",
            }

        # Sort deposits by date
        sorted_deposits = sorted(payroll_deposits, key=lambda x: x["date"])

        # Calculate gaps between consecutive deposits
        gap_days = []
        for i in range(1, len(sorted_deposits)):
            current_date = datetime.fromisoformat(sorted_deposits[i]["date"]).date()
            previous_date = datetime.fromisoformat(sorted_deposits[i-1]["date"]).date()
            gap = (current_date - previous_date).days
            gap_days.append(gap)

        if not gap_days:
            return {
                "median_gap_days": None,
                "average_gap_days": None,
                "gap_days": [],
                "deposit_count": len(payroll_deposits),
                "frequency_type": "insufficient_data",
            }

        median_gap = median(gap_days)
        average_gap = sum(gap_days) / len(gap_days)

        # Classify frequency type
        if median_gap <= 7:
            frequency_type = "weekly"
        elif median_gap <= 18:
            frequency_type = "biweekly"
        elif median_gap <= 35:
            frequency_type = "monthly"
        elif median_gap <= 45:
            frequency_type = "irregular"
        else:
            frequency_type = "variable"

        return {
            "median_gap_days": round(median_gap, 1),
            "average_gap_days": round(average_gap, 1),
            "gap_days": gap_days,
            "deposit_count": len(payroll_deposits),
            "frequency_type": frequency_type,
        }

    def calculate_payment_variability(
        self,
        payroll_deposits: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate payment variability (coefficient of variation of payment amounts).

        Coefficient of variation = (standard deviation / mean) × 100

        Args:
            payroll_deposits: List of payroll deposit transactions

        Returns:
            Dictionary with payment variability details including:
            - coefficient_of_variation: CV percentage
            - standard_deviation: Standard deviation of amounts
            - mean_amount: Mean payment amount
            - min_amount: Minimum payment amount
            - max_amount: Maximum payment amount
            - variability_level: Classification (low/medium/high)
        """
        if len(payroll_deposits) < 2:
            return {
                "coefficient_of_variation": None,
                "standard_deviation": None,
                "mean_amount": None,
                "min_amount": None,
                "max_amount": None,
                "variability_level": "insufficient_data",
            }

        amounts = [deposit["amount"] for deposit in payroll_deposits]

        mean_amount = sum(amounts) / len(amounts)

        # Calculate standard deviation
        variance = sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)
        standard_deviation = math.sqrt(variance)

        # Calculate coefficient of variation
        coefficient_of_variation = (
            (standard_deviation / mean_amount) * 100
            if mean_amount > 0
            else 0.0
        )

        # Classify variability level
        if coefficient_of_variation < 5:
            variability_level = "low"
        elif coefficient_of_variation < 15:
            variability_level = "medium"
        else:
            variability_level = "high"

        return {
            "coefficient_of_variation": round(coefficient_of_variation, 2),
            "standard_deviation": round(standard_deviation, 2),
            "mean_amount": round(mean_amount, 2),
            "min_amount": round(min(amounts), 2),
            "max_amount": round(max(amounts), 2),
            "variability_level": variability_level,
        }

    def calculate_cash_flow_buffer(
        self,
        user_id: uuid.UUID,
        window_days: int = 90,
    ) -> Dict[str, Any]:
        """
        Calculate cash-flow buffer in months.

        Cash-flow buffer = (current balance - minimum balance) / average monthly expenses

        Args:
            user_id: User ID
            window_days: Time window in days for calculating average monthly expenses (default: 90)

        Returns:
            Dictionary with cash-flow buffer details including:
            - cash_flow_buffer_months: Buffer in months
            - current_balance: Current total checking balance
            - minimum_balance: Minimum balance in window
            - average_monthly_expenses: Average monthly expenses
            - account_details: Per-account breakdown
        """
        logger.info(
            f"Calculating cash-flow buffer for user {user_id} (window: {window_days} days)"
        )

        # Get checking accounts
        checking_accounts = self.get_checking_accounts(user_id)

        if not checking_accounts:
            logger.info(f"No checking accounts found for user {user_id}")
            return {
                "cash_flow_buffer_months": 0.0,
                "current_balance": 0.0,
                "minimum_balance": 0.0,
                "average_monthly_expenses": 0.0,
                "account_details": [],
            }

        # Calculate current total balance
        current_balance = Decimal("0.0")
        account_details = []

        for acc in checking_accounts:
            balance = Decimal(str(acc.balance_current)) if acc.balance_current else Decimal("0.0")
            current_balance += balance

            account_details.append({
                "account_id": acc.account_id,
                "account_name": acc.name,
                "current_balance": float(balance),
            })

        # Calculate minimum balance in window (by looking at transaction history)
        # This is an approximation - ideally we'd have balance snapshots
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        minimum_balance = current_balance
        account_ids = [acc.id for acc in checking_accounts]

        # Estimate minimum balance by working backwards from current balance
        # Find the minimum balance point by tracking transactions
        # Start with current balance and subtract all expenses to find minimum
        total_expenses = self.db.query(
            func.sum(func.abs(Transaction.amount))
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.account_id.in_(account_ids),
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,
                Transaction.amount < 0,  # Expenses are negative
            )
        ).scalar()

        total_deposits = self.db.query(
            func.sum(Transaction.amount)
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.account_id.in_(account_ids),
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,
                Transaction.amount > 0,  # Deposits are positive
            )
        ).scalar()

        # Estimate minimum balance: current - (deposits - expenses)
        # This approximates the lowest balance during the period
        deposits_sum = Decimal(str(total_deposits)) if total_deposits else Decimal("0.0")
        expenses_sum = Decimal(str(total_expenses)) if total_expenses else Decimal("0.0")

        # Minimum balance estimate: current balance minus net deposits
        # If we had more deposits than expenses, minimum was likely earlier
        net_flow = deposits_sum - expenses_sum
        estimated_minimum = current_balance - net_flow

        # Ensure minimum balance doesn't exceed current balance
        minimum_balance = min(estimated_minimum, current_balance)

        # Calculate average monthly expenses
        months_in_window = Decimal(str(window_days)) / Decimal("30.0")
        average_monthly_expenses = (
            expenses_sum / months_in_window if months_in_window > 0 else Decimal("0.0")
        )

        # Calculate cash-flow buffer in months
        available_buffer = current_balance - minimum_balance
        cash_flow_buffer_months = (
            float(available_buffer / average_monthly_expenses)
            if average_monthly_expenses > 0
            else 0.0
        )

        return {
            "cash_flow_buffer_months": round(cash_flow_buffer_months, 2),
            "current_balance": float(current_balance),
            "minimum_balance": float(minimum_balance),
            "average_monthly_expenses": float(average_monthly_expenses),
            "account_details": account_details,
        }

    def detect_variable_income_patterns(
        self,
        payment_frequency: Dict[str, Any],
        payment_variability: Dict[str, Any],
        cash_flow_buffer: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Identify variable income patterns.

        Variable income is indicated by:
        - High payment variability (CV > 15%)
        - Irregular payment frequency (median gap > 45 days OR frequency_type = "variable")
        - Low cash-flow buffer (< 1 month)

        Args:
            payment_frequency: Payment frequency details
            payment_variability: Payment variability details
            cash_flow_buffer: Cash-flow buffer details

        Returns:
            Dictionary with variable income pattern detection results
        """
        is_variable_income = False
        reasons = []

        # Check payment frequency
        if payment_frequency.get("median_gap_days"):
            median_gap = payment_frequency["median_gap_days"]
            if median_gap > 45 or payment_frequency.get("frequency_type") == "variable":
                is_variable_income = True
                reasons.append(f"Irregular payment frequency (median gap: {median_gap} days)")

        # Check payment variability
        if payment_variability.get("coefficient_of_variation"):
            cv = payment_variability["coefficient_of_variation"]
            if cv >= 15:
                is_variable_income = True
                reasons.append(f"High payment variability (CV: {cv:.2f}%)")

        # Check cash-flow buffer
        if cash_flow_buffer.get("cash_flow_buffer_months") is not None:
            buffer_months = cash_flow_buffer["cash_flow_buffer_months"]
            if buffer_months < 1.0:
                is_variable_income = True
                reasons.append(f"Low cash-flow buffer ({buffer_months:.2f} months)")

        return {
            "is_variable_income": is_variable_income,
            "reasons": reasons,
            "confidence": (
                "high" if len(reasons) >= 2
                else "medium" if len(reasons) == 1
                else "low"
            ),
        }

    def calculate_income_signals(
        self,
        user_id: uuid.UUID,
        window_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Calculate income stability signals for a specific time window.

        Args:
            user_id: User ID
            window_days: Time window in days (30 or 180)

        Returns:
            Dictionary with income stability signals including:
            - payroll_deposits: List of detected payroll deposits
            - payment_frequency: Payment frequency details
            - payment_variability: Payment variability details
            - cash_flow_buffer: Cash-flow buffer details
            - variable_income_pattern: Variable income detection results
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        logger.info(f"Calculating income signals for user {user_id}, {window_days}-day window")

        # Detect payroll deposits
        payroll_deposits = self.detect_payroll_deposits(user_id, start_date, end_date)

        # Calculate payment frequency
        payment_frequency = self.calculate_payment_frequency(payroll_deposits)

        # Calculate payment variability
        payment_variability = self.calculate_payment_variability(payroll_deposits)

        # Calculate cash-flow buffer (use 90-day window for expense calculation)
        cash_flow_buffer = self.calculate_cash_flow_buffer(user_id, window_days=90)

        # Detect variable income patterns
        variable_income_pattern = self.detect_variable_income_patterns(
            payment_frequency,
            payment_variability,
            cash_flow_buffer,
        )

        return {
            "window_days": window_days,
            "window_start": start_date.isoformat(),
            "window_end": end_date.isoformat(),
            "payroll_deposits": payroll_deposits,
            "payment_frequency": payment_frequency,
            "payment_variability": payment_variability,
            "cash_flow_buffer": cash_flow_buffer,
            "variable_income_pattern": variable_income_pattern,
        }

    @cache_feature_signals(CACHE_PREFIX_INCOME)
    def generate_income_signals(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        Generate income stability signals for both 30-day and 180-day windows.

        Args:
            user_id: User ID

        Returns:
            Dictionary with signals for both time windows
        """
        logger.info(f"Generating income stability signals for user {user_id}")

        # Check consent before processing
        try:
            self.consent_guardrails.require_consent(user_id, "feature_detection:income")
        except ConsentError as e:
            logger.warning(f"Income signal generation blocked: {str(e)}")
            raise

        signals_30d = self.calculate_income_signals(user_id, window_days=30)
        signals_180d = self.calculate_income_signals(user_id, window_days=180)

        return {
            "user_id": str(user_id),
            "generated_at": datetime.utcnow().isoformat(),
            "signals_30d": signals_30d,
            "signals_180d": signals_180d,
        }

