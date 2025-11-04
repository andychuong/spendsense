"""Savings pattern detection service for identifying savings behaviors and patterns."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_

from app.common.feature_cache import (
    cache_feature_signals,
    CACHE_PREFIX_SAVINGS,
    get_cached_savings_signals,
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


# Savings-like account subtypes
SAVINGS_ACCOUNT_SUBTYPES = ["savings", "money market", "hsa"]


class SavingsDetector:
    """Detects savings patterns and behaviors from account and transaction data."""

    def __init__(self, db_session: Session):
        """
        Initialize savings detector.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.consent_guardrails = ConsentGuardrails(db_session)

    def get_savings_accounts(
        self,
        user_id: uuid.UUID,
    ) -> List[Account]:
        """
        Get all savings-like accounts for a user.

        Args:
            user_id: User ID

        Returns:
            List of savings-like accounts (savings, money market, HSA)
        """
        accounts = self.db.query(Account).filter(
            and_(
                Account.user_id == user_id,
                Account.type == "depository",
                Account.subtype.in_(SAVINGS_ACCOUNT_SUBTYPES),
                Account.holder_category == "individual",
            )
        ).all()

        logger.info(f"Found {len(accounts)} savings-like accounts for user {user_id}")
        return accounts

    def calculate_net_inflow(
        self,
        user_id: uuid.UUID,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Calculate net inflow to savings accounts.

        Net inflow = sum of deposits (positive amounts) to savings-like accounts.
        In Plaid, deposits are positive amounts, withdrawals are negative.

        Args:
            user_id: User ID
            start_date: Start date of analysis window
            end_date: End date of analysis window

        Returns:
            Dictionary with net inflow details including:
            - net_inflow: Total net inflow amount
            - total_deposits: Total deposits count and amount
            - total_withdrawals: Total withdrawals count and amount
            - account_details: Per-account breakdown
        """
        logger.info(
            f"Calculating net inflow for user {user_id} from {start_date} to {end_date}"
        )

        # Get savings accounts
        savings_accounts = self.get_savings_accounts(user_id)

        if not savings_accounts:
            logger.info(f"No savings accounts found for user {user_id}")
            return {
                "net_inflow": 0.0,
                "total_deposits": {"count": 0, "amount": 0.0},
                "total_withdrawals": {"count": 0, "amount": 0.0},
                "account_details": [],
            }

        savings_account_ids = [acc.id for acc in savings_accounts]

        # Query transactions in date range for savings accounts
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.account_id.in_(savings_account_ids),
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,
            )
        ).order_by(Transaction.date).all()

        # Calculate deposits (positive amounts) and withdrawals (negative amounts)
        total_deposits = Decimal("0.0")
        total_withdrawals = Decimal("0.0")
        deposit_count = 0
        withdrawal_count = 0

        # Per-account breakdown
        account_details = {}
        for acc in savings_accounts:
            account_details[str(acc.id)] = {
                "account_id": acc.account_id,
                "account_name": acc.name,
                "subtype": acc.subtype,
                "deposits": {"count": 0, "amount": Decimal("0.0")},
                "withdrawals": {"count": 0, "amount": Decimal("0.0")},
                "net_inflow": Decimal("0.0"),
            }

        for txn in transactions:
            amount = Decimal(str(txn.amount))
            acc_id = str(txn.account_id)

            if amount > 0:
                # Deposit
                total_deposits += amount
                deposit_count += 1
                account_details[acc_id]["deposits"]["count"] += 1
                account_details[acc_id]["deposits"]["amount"] += amount
            else:
                # Withdrawal
                total_withdrawals += abs(amount)
                withdrawal_count += 1
                account_details[acc_id]["withdrawals"]["count"] += 1
                account_details[acc_id]["withdrawals"]["amount"] += abs(amount)

        # Calculate net inflow per account
        for acc_id, details in account_details.items():
            details["net_inflow"] = (
                details["deposits"]["amount"] - details["withdrawals"]["amount"]
            )

        # Net inflow = total deposits - total withdrawals
        net_inflow = total_deposits - total_withdrawals

        return {
            "net_inflow": float(net_inflow),
            "total_deposits": {
                "count": deposit_count,
                "amount": float(total_deposits),
            },
            "total_withdrawals": {
                "count": withdrawal_count,
                "amount": float(total_withdrawals),
            },
            "account_details": [
                {
                    **details,
                    "deposits": {
                        "count": details["deposits"]["count"],
                        "amount": float(details["deposits"]["amount"]),
                    },
                    "withdrawals": {
                        "count": details["withdrawals"]["count"],
                        "amount": float(details["withdrawals"]["amount"]),
                    },
                    "net_inflow": float(details["net_inflow"]),
                }
                for details in account_details.values()
            ],
        }

    def calculate_savings_growth_rate(
        self,
        user_id: uuid.UUID,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Calculate savings growth rate.

        Growth rate = (current balance - previous balance) / previous balance * 100

        Args:
            user_id: User ID
            start_date: Start date of analysis window
            end_date: End date of analysis window

        Returns:
            Dictionary with growth rate details including:
            - current_balance: Sum of current balances across all savings accounts
            - previous_balance: Sum of balances at start_date
            - growth_amount: Absolute growth amount
            - growth_rate_percent: Percentage growth rate
            - account_details: Per-account breakdown
        """
        logger.info(
            f"Calculating savings growth rate for user {user_id} from {start_date} to {end_date}"
        )

        # Get savings accounts
        savings_accounts = self.get_savings_accounts(user_id)

        if not savings_accounts:
            logger.info(f"No savings accounts found for user {user_id}")
            return {
                "current_balance": 0.0,
                "previous_balance": 0.0,
                "growth_amount": 0.0,
                "growth_rate_percent": 0.0,
                "account_details": [],
            }

        # Get current balances (most recent account balance)
        current_balance = Decimal("0.0")
        previous_balance = Decimal("0.0")

        account_details = []

        for acc in savings_accounts:
            current_bal = Decimal(str(acc.balance_current)) if acc.balance_current else Decimal("0.0")
            current_balance += current_bal

            # Estimate previous balance by working backwards from current balance
            # Previous balance = current balance - net flow during period
            # Net flow = sum of all transactions during the period
            transactions_during_period = self.db.query(
                func.sum(Transaction.amount)
            ).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.account_id == acc.id,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date,
                    Transaction.pending == False,
                )
            ).scalar()

            # Previous balance = current balance - transactions during period
            # This works because: balance_at_end = balance_at_start + transactions_during_period
            transactions_sum = Decimal(str(transactions_during_period)) if transactions_during_period else Decimal("0.0")
            prev_bal_estimate = current_bal - transactions_sum
            previous_balance += prev_bal_estimate

            account_details.append({
                "account_id": acc.account_id,
                "account_name": acc.name,
                "subtype": acc.subtype,
                "current_balance": float(current_bal),
                "previous_balance": float(prev_bal_estimate),
                "growth_amount": float(current_bal - prev_bal_estimate),
                "growth_rate_percent": (
                    float((current_bal - prev_bal_estimate) / prev_bal_estimate * 100)
                    if prev_bal_estimate != 0
                    else 0.0
                ),
            })

        # Calculate overall growth rate
        growth_amount = current_balance - previous_balance
        growth_rate_percent = (
            float((growth_amount / previous_balance * 100))
            if previous_balance != 0
            else 0.0
        )

        return {
            "current_balance": float(current_balance),
            "previous_balance": float(previous_balance),
            "growth_amount": float(growth_amount),
            "growth_rate_percent": round(growth_rate_percent, 2),
            "account_details": account_details,
        }

    def calculate_emergency_fund_coverage(
        self,
        user_id: uuid.UUID,
        window_days: int = 90,
    ) -> Dict[str, Any]:
        """
        Calculate emergency fund coverage.

        Emergency fund coverage = savings balance / average monthly expenses

        Args:
            user_id: User ID
            window_days: Time window in days for calculating average monthly expenses (default: 90)

        Returns:
            Dictionary with emergency fund coverage details including:
            - savings_balance: Total savings balance
            - average_monthly_expenses: Average monthly expenses
            - coverage_months: Emergency fund coverage in months
            - account_details: Per-account breakdown
        """
        logger.info(
            f"Calculating emergency fund coverage for user {user_id} (window: {window_days} days)"
        )

        # Get savings accounts
        savings_accounts = self.get_savings_accounts(user_id)

        if not savings_accounts:
            logger.info(f"No savings accounts found for user {user_id}")
            return {
                "savings_balance": 0.0,
                "average_monthly_expenses": 0.0,
                "coverage_months": 0.0,
                "account_details": [],
            }

        # Calculate total savings balance
        savings_balance = Decimal("0.0")
        account_details = []

        for acc in savings_accounts:
            balance = Decimal(str(acc.balance_current)) if acc.balance_current else Decimal("0.0")
            savings_balance += balance

            account_details.append({
                "account_id": acc.account_id,
                "account_name": acc.name,
                "subtype": acc.subtype,
                "balance": float(balance),
            })

        # Calculate average monthly expenses
        # Look at all transactions (negative amounts are expenses) in the window
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        # Sum all expenses (negative amounts) in the window
        expenses_result = self.db.query(
            func.sum(func.abs(Transaction.amount))
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,
                Transaction.amount < 0,  # Negative amounts are expenses
            )
        ).scalar()

        total_expenses = Decimal(str(expenses_result)) if expenses_result else Decimal("0.0")

        # Calculate average monthly expenses
        # Assuming 30 days per month
        months_in_window = Decimal(str(window_days)) / Decimal("30.0")
        average_monthly_expenses = (
            total_expenses / months_in_window if months_in_window > 0 else Decimal("0.0")
        )

        # Calculate coverage in months
        coverage_months = (
            float(savings_balance / average_monthly_expenses)
            if average_monthly_expenses > 0
            else 0.0
        )

        return {
            "savings_balance": float(savings_balance),
            "average_monthly_expenses": float(average_monthly_expenses),
            "coverage_months": round(coverage_months, 2),
            "account_details": account_details,
        }

    def calculate_savings_signals(
        self,
        user_id: uuid.UUID,
        window_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Calculate savings signals for a specific time window.

        Args:
            user_id: User ID
            window_days: Time window in days (30 or 180)

        Returns:
            Dictionary with savings signals including:
            - net_inflow: Net inflow to savings accounts
            - growth_rate: Savings growth rate
            - emergency_fund_coverage: Emergency fund coverage in months
            - savings_balance: Total savings balance
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        logger.info(f"Calculating savings signals for user {user_id}, {window_days}-day window")

        # Calculate net inflow
        net_inflow_data = self.calculate_net_inflow(user_id, start_date, end_date)

        # Calculate growth rate
        growth_rate_data = self.calculate_savings_growth_rate(user_id, start_date, end_date)

        # Calculate emergency fund coverage (use 90-day window for expense calculation)
        emergency_fund_data = self.calculate_emergency_fund_coverage(user_id, window_days=90)

        return {
            "window_days": window_days,
            "window_start": start_date.isoformat(),
            "window_end": end_date.isoformat(),
            "net_inflow": net_inflow_data,
            "growth_rate": growth_rate_data,
            "emergency_fund_coverage": emergency_fund_data,
            "savings_balance": emergency_fund_data["savings_balance"],
        }

    @cache_feature_signals(CACHE_PREFIX_SAVINGS)
    def generate_savings_signals(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        Generate savings signals for both 30-day and 180-day windows.

        Args:
            user_id: User ID

        Returns:
            Dictionary with signals for both time windows
        """
        logger.info(f"Generating savings signals for user {user_id}")

        # Check consent before processing
        try:
            self.consent_guardrails.require_consent(user_id, "feature_detection:savings")
        except ConsentError as e:
            logger.warning(f"Savings signal generation blocked: {str(e)}")
            raise

        signals_30d = self.calculate_savings_signals(user_id, window_days=30)
        signals_180d = self.calculate_savings_signals(user_id, window_days=180)

        return {
            "user_id": str(user_id),
            "generated_at": datetime.utcnow().isoformat(),
            "signals_30d": signals_30d,
            "signals_180d": signals_180d,
        }

