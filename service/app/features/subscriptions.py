"""Subscription detection service for identifying recurring merchants and subscription patterns."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from collections import defaultdict
from statistics import median

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.common.feature_cache import (
    cache_feature_signals,
    CACHE_PREFIX_SUBSCRIPTIONS,
    get_cached_subscription_signals,
)
from app.common.consent_guardrails import ConsentGuardrails, ConsentError

logger = logging.getLogger(__name__)

# Try to import Transaction model from backend
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


class SubscriptionDetector:
    """Detects recurring subscription patterns from transaction data."""

    def __init__(self, db_session: Session):
        """
        Initialize subscription detector.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.consent_guardrails = ConsentGuardrails(db_session)

    def detect_subscriptions(
        self,
        user_id: uuid.UUID,
        window_days: int = 90,
        min_occurrences: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Detect recurring merchants (subscriptions) for a user.

        Args:
            user_id: User ID
            window_days: Time window in days (default: 90)
            min_occurrences: Minimum number of transactions to consider recurring (default: 3)

        Returns:
            List of detected subscriptions with merchant info, cadence, and spend
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        logger.info(f"Detecting subscriptions for user {user_id} from {start_date} to {end_date}")

        # Query transactions in date range
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,  # Exclude pending transactions
            )
        ).order_by(Transaction.date).all()

        if not transactions:
            logger.info(f"No transactions found for user {user_id} in window {window_days} days")
            return []

        # Group transactions by merchant
        # Note: In Plaid, expenses are negative amounts, so we use absolute value for analysis
        merchant_transactions = defaultdict(list)
        for txn in transactions:
            # Use merchant_entity_id if available, otherwise merchant_name
            merchant_key = txn.merchant_entity_id if txn.merchant_entity_id else txn.merchant_name
            if merchant_key:
                # Use absolute value for amount (Plaid expenses are negative)
                amount = abs(float(txn.amount))
                merchant_transactions[merchant_key].append({
                    "date": txn.date,
                    "amount": amount,
                    "merchant_name": txn.merchant_name,
                    "merchant_entity_id": txn.merchant_entity_id,
                    "transaction_id": txn.transaction_id,
                })

        # Filter merchants with at least min_occurrences transactions
        recurring_merchants = []
        for merchant_key, txns in merchant_transactions.items():
            if len(txns) >= min_occurrences:
                # Calculate cadence and metrics
                subscription_info = self._analyze_merchant_pattern(
                    merchant_key, txns, start_date, end_date
                )
                if subscription_info:
                    recurring_merchants.append(subscription_info)

        logger.info(f"Found {len(recurring_merchants)} recurring merchants for user {user_id}")
        return recurring_merchants

    def _analyze_merchant_pattern(
        self,
        merchant_key: str,
        transactions: List[Dict[str, Any]],
        start_date: date,
        end_date: date,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze merchant transaction pattern to determine subscription details.

        Args:
            merchant_key: Merchant identifier (entity_id or name)
            transactions: List of transaction dictionaries
            start_date: Start date of analysis window
            end_date: End date of analysis window

        Returns:
            Dictionary with subscription details or None if not a valid subscription
        """
        if len(transactions) < 3:
            return None

        # Sort transactions by date
        transactions.sort(key=lambda x: x["date"])

        # Calculate time gaps between transactions
        gaps_days = []
        for i in range(1, len(transactions)):
            gap = (transactions[i]["date"] - transactions[i-1]["date"]).days
            gaps_days.append(gap)

        if not gaps_days:
            return None

        # Calculate median gap to determine cadence
        median_gap = median(gaps_days)

        # Determine cadence type
        if median_gap <= 10:
            cadence_type = "weekly"
            expected_periods = (end_date - start_date).days // 7
        elif median_gap <= 35:
            cadence_type = "monthly"
            expected_periods = (end_date - start_date).days // 30
        else:
            # Not a regular subscription pattern
            return None

        # Calculate average transaction amount
        amounts = [txn["amount"] for txn in transactions]
        avg_amount = sum(amounts) / len(amounts)

        # Calculate monthly recurring spend
        if cadence_type == "weekly":
            monthly_recurring_spend = avg_amount * 4.33  # ~4.33 weeks per month
        else:  # monthly
            monthly_recurring_spend = avg_amount

        # Get merchant name (use first transaction's merchant_name)
        merchant_name = transactions[0]["merchant_name"] or merchant_key

        return {
            "merchant_key": merchant_key,
            "merchant_name": merchant_name,
            "merchant_entity_id": transactions[0]["merchant_entity_id"],
            "transaction_count": len(transactions),
            "cadence_type": cadence_type,
            "median_gap_days": round(median_gap, 1),
            "average_amount": round(avg_amount, 2),
            "monthly_recurring_spend": round(monthly_recurring_spend, 2),
            "first_transaction_date": transactions[0]["date"].isoformat(),
            "last_transaction_date": transactions[-1]["date"].isoformat(),
            "transaction_ids": [txn["transaction_id"] for txn in transactions],
        }

    def calculate_subscription_signals(
        self,
        user_id: uuid.UUID,
        window_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Calculate subscription signals for a specific time window.

        Args:
            user_id: User ID
            window_days: Time window in days (30 or 180)

        Returns:
            Dictionary with subscription signals including:
            - recurring_merchants: List of detected subscriptions
            - total_recurring_spend: Total monthly recurring spend
            - subscription_count: Number of recurring merchants
            - subscription_share: Percentage of total spend on subscriptions
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)

        logger.info(f"Calculating subscription signals for user {user_id}, {window_days}-day window")

        # Detect subscriptions (using 90-day window for detection, but filter to window_days)
        subscriptions = self.detect_subscriptions(user_id, window_days=90, min_occurrences=3)

        # Filter subscriptions to only include those with transactions in the target window
        filtered_subscriptions = []
        for sub in subscriptions:
            # Check if subscription has transactions in the target window
            first_date = datetime.fromisoformat(sub["first_transaction_date"]).date()
            last_date = datetime.fromisoformat(sub["last_transaction_date"]).date()

            # Include if subscription overlaps with target window
            if last_date >= start_date and first_date <= end_date:
                filtered_subscriptions.append(sub)

        # Calculate total recurring spend (sum of monthly recurring spend)
        total_recurring_spend = sum(
            sub["monthly_recurring_spend"] for sub in filtered_subscriptions
        )

        # Calculate total spend in window
        # In Plaid, expenses are negative amounts, so we sum absolute values
        total_spend_result = self.db.query(
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

        total_spend = float(total_spend_result) if total_spend_result else 0.0

        # Calculate subscription share percentage
        subscription_share = (
            (total_recurring_spend / total_spend * 100) if total_spend > 0 else 0.0
        )

        return {
            "window_days": window_days,
            "window_start": start_date.isoformat(),
            "window_end": end_date.isoformat(),
            "recurring_merchants": filtered_subscriptions,
            "subscription_count": len(filtered_subscriptions),
            "total_recurring_spend": round(total_recurring_spend, 2),
            "total_spend": round(total_spend, 2),
            "subscription_share_percent": round(subscription_share, 2),
        }

    @cache_feature_signals(CACHE_PREFIX_SUBSCRIPTIONS)
    def generate_subscription_signals(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        Generate subscription signals for both 30-day and 180-day windows.

        Args:
            user_id: User ID

        Returns:
            Dictionary with signals for both time windows
        """
        logger.info(f"Generating subscription signals for user {user_id}")

        # Check consent before processing
        try:
            self.consent_guardrails.require_consent(user_id, "feature_detection:subscriptions")
        except ConsentError as e:
            logger.warning(f"Subscription signal generation blocked: {str(e)}")
            raise

        signals_30d = self.calculate_subscription_signals(user_id, window_days=30)
        signals_180d = self.calculate_subscription_signals(user_id, window_days=180)

        return {
            "user_id": str(user_id),
            "generated_at": datetime.utcnow().isoformat(),
            "signals_30d": signals_30d,
            "signals_180d": signals_180d,
        }

