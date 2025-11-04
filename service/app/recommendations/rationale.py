"""Rationale generation service for creating plain-language, data-driven rationales."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.orm import Session

# Try to import models from backend
try:
    from backend.app.models.account import Account as AccountModel
    from backend.app.models.transaction import Transaction as TransactionModel
    from backend.app.models.liability import Liability as LiabilityModel
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.account import Account as AccountModel
    from app.models.transaction import Transaction as TransactionModel
    from app.models.liability import Liability as LiabilityModel

logger = logging.getLogger(__name__)


class RationaleGenerator:
    """Service for generating plain-language rationales with specific data point citations."""

    def __init__(self, db_session: Session):
        """
        Initialize rationale generator.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def format_account_number(self, account: AccountModel) -> str:
        """
        Format account number for display (last 4 digits).

        Args:
            account: Account model instance

        Returns:
            Formatted account string (e.g., "Visa ending in 4523")
        """
        # Try to use mask if available
        if account.mask:
            return f"{account.name} ending in {account.mask}"

        # Fallback: extract last 4 digits from account_id if mask not available
        account_id_str = str(account.account_id)
        if len(account_id_str) >= 4:
            last_four = account_id_str[-4:]
            return f"{account.name} ending in {last_four}"

        return account.name

    def format_currency(self, amount: float, show_cents: bool = True) -> str:
        """
        Format amount as currency.

        Args:
            amount: Amount to format
            show_cents: Whether to show cents (default: True)

        Returns:
            Formatted currency string (e.g., "$1,234.56" or "$1,235")
        """
        if amount is None:
            return "$0"

        # Convert to float if Decimal
        if isinstance(amount, Decimal):
            amount = float(amount)

        if show_cents:
            return f"${amount:,.2f}"
        else:
            return f"${amount:,.0f}"

    def format_date(self, date_value: date) -> str:
        """
        Format date in readable format.

        Args:
            date_value: Date to format

        Returns:
            Formatted date string (e.g., "January 15, 2024")
        """
        if date_value is None:
            return "recently"

        return date_value.strftime("%B %d, %Y")

    def format_percent(self, value: float, decimals: int = 1) -> str:
        """
        Format percentage.

        Args:
            value: Percentage value (e.g., 68.5 for 68.5%)
            decimals: Number of decimal places

        Returns:
            Formatted percentage string (e.g., "68.5%")
        """
        if value is None:
            return "0%"

        return f"{value:.{decimals}f}%"

    def get_account_details(self, user_id: uuid.UUID, account_id: Optional[str] = None) -> Optional[AccountModel]:
        """
        Get account details from database.

        Args:
            user_id: User ID
            account_id: Optional Plaid account_id

        Returns:
            Account model instance or None
        """
        query = self.db.query(AccountModel).filter(AccountModel.user_id == user_id)

        if account_id:
            query = query.filter(AccountModel.account_id == account_id)

        return query.first()

    def get_recent_transactions(self, user_id: uuid.UUID, account_id: Optional[str] = None, limit: int = 5) -> List[TransactionModel]:
        """
        Get recent transactions for data point citations.

        Args:
            user_id: User ID
            account_id: Optional account ID to filter
            limit: Maximum number of transactions to return

        Returns:
            List of transaction model instances
        """
        query = self.db.query(TransactionModel).filter(
            TransactionModel.user_id == user_id
        ).order_by(TransactionModel.date.desc())

        if account_id:
            # Get database account ID from Plaid account_id
            account = self.db.query(AccountModel).filter(
                AccountModel.user_id == user_id,
                AccountModel.account_id == account_id
            ).first()
            if account:
                query = query.filter(TransactionModel.account_id == account.id)

        return query.limit(limit).all()

    def generate_rationale_for_persona_1(
        self,
        recommendation: Dict[str, Any],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        user_id: uuid.UUID,
    ) -> str:
        """
        Generate rationale for Persona 1: High Utilization.

        Args:
            recommendation: Recommendation dictionary
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            user_id: User ID for fetching account details

        Returns:
            Plain-language rationale string
        """
        credit_signals = signals_30d.get("credit", {}) or signals_180d.get("credit", {})
        if not credit_signals:
            return self._generate_generic_rationale(recommendation)

        rationale_parts = []

        # Get account details for citations
        critical_cards = credit_signals.get("critical_utilization_cards", [])
        severe_cards = credit_signals.get("severe_utilization_cards", [])

        if critical_cards or severe_cards:
            card_signal = (critical_cards + severe_cards)[0]
            account_id = card_signal.get("account_id")

            # Try to get account from database for better formatting
            account = None
            if account_id:
                account = self.get_account_details(user_id, account_id)

            if account:
                account_display = self.format_account_number(account)
            else:
                account_display = card_signal.get("account_name", "your credit card")

            utilization = card_signal.get("utilization_percent", 0)
            balance = card_signal.get("current_balance", 0)
            limit = card_signal.get("credit_limit", 0)

            rationale_parts.append(
                f"We noticed {account_display} is at {utilization:.0f}% utilization "
                f"({self.format_currency(balance)} of {self.format_currency(limit)} limit)."
            )

        # Interest charges
        interest_cards = credit_signals.get("cards_with_interest", [])
        if interest_cards:
            total_interest = sum([
                card.get("interest_charges", {}).get("total_interest_charges", 0)
                for card in interest_cards
            ])
            if total_interest > 0:
                rationale_parts.append(
                    f"You're paying {self.format_currency(total_interest)} per month in interest charges."
                )

        # Minimum payment behavior
        min_payment_cards = credit_signals.get("minimum_payment_only_cards", [])
        if min_payment_cards:
            card_signal = min_payment_cards[0]
            account_id = card_signal.get("account_id")
            account = None
            if account_id:
                account = self.get_account_details(user_id, account_id)

            if account:
                account_display = self.format_account_number(account)
            else:
                account_display = card_signal.get("account_name", "your credit card")

            rationale_parts.append(
                f"You're making minimum payments on {account_display}, which can keep you in debt for years."
            )

        # Overdue accounts
        overdue_cards = credit_signals.get("overdue_cards", [])
        if overdue_cards:
            card_signal = overdue_cards[0]
            account_id = card_signal.get("account_id")
            account = None
            if account_id:
                account = self.get_account_details(user_id, account_id)

            if account:
                account_display = self.format_account_number(account)
            else:
                account_display = card_signal.get("account_name", "your credit card")

            rationale_parts.append(
                f"{account_display} is overdue, which can hurt your credit score."
            )

        if rationale_parts:
            return " ".join(rationale_parts)

        return self._generate_generic_rationale(recommendation)

    def generate_rationale_for_persona_2(
        self,
        recommendation: Dict[str, Any],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        user_id: uuid.UUID,
    ) -> str:
        """
        Generate rationale for Persona 2: Variable Income Budgeter.

        Args:
            recommendation: Recommendation dictionary
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            user_id: User ID for fetching account details

        Returns:
            Plain-language rationale string
        """
        income_signals = signals_180d.get("income", {}) or signals_30d.get("income", {})
        if not income_signals:
            return self._generate_generic_rationale(recommendation)

        rationale_parts = []

        # Income pattern
        income_patterns = income_signals.get("income_patterns", {})
        median_gap = income_patterns.get("median_pay_gap_days", None)

        if median_gap and median_gap > 45:
            # Get recent payroll deposits for date citation
            recent_transactions = self.get_recent_transactions(user_id, limit=10)
            payroll_deposits = [
                t for t in recent_transactions
                if t.category_primary == "PAYROLL" and t.amount > 0  # Positive for deposits
            ]

            if payroll_deposits:
                latest_payroll = payroll_deposits[0]
                pay_date = self.format_date(latest_payroll.date)
                rationale_parts.append(
                    f"Your income arrives irregularly (last payment was on {pay_date}, "
                    f"with a median gap of {median_gap:.0f} days between payments)."
                )
            else:
                rationale_parts.append(
                    f"Your income arrives irregularly (median gap of {median_gap:.0f} days between payments)."
                )

        # Cash flow buffer
        cash_buffer = income_signals.get("cash_flow_buffer_months", None)
        if cash_buffer is not None and cash_buffer < 1:
            rationale_parts.append(
                f"Your cash flow buffer is {cash_buffer:.2f} months, below the recommended 1-2 months "
                f"needed to handle irregular income."
            )

        if rationale_parts:
            return " ".join(rationale_parts)

        return self._generate_generic_rationale(recommendation)

    def generate_rationale_for_persona_3(
        self,
        recommendation: Dict[str, Any],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        user_id: uuid.UUID,
    ) -> str:
        """
        Generate rationale for Persona 3: Subscription-Heavy.

        Args:
            recommendation: Recommendation dictionary
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            user_id: User ID for fetching account details

        Returns:
            Plain-language rationale string
        """
        sub_signals = signals_30d.get("subscriptions", {}) or signals_180d.get("subscriptions", {})
        if not sub_signals:
            return self._generate_generic_rationale(recommendation)

        rationale_parts = []

        sub_count = sub_signals.get("subscription_count", 0)
        total_recurring = sub_signals.get("total_recurring_spend", 0)
        sub_share = sub_signals.get("subscription_share_percent", 0)

        if sub_count >= 3:
            # Get merchant names for citations
            recurring_merchants = sub_signals.get("recurring_merchants", [])
            merchant_names = [m.get("merchant_name", "Unknown") for m in recurring_merchants[:3]]

            if merchant_names:
                merchants_str = ", ".join(merchant_names)
                if len(recurring_merchants) > 3:
                    merchants_str += f", and {len(recurring_merchants) - 3} more"

                rationale_parts.append(
                    f"You have {sub_count} recurring subscriptions including {merchants_str}, "
                    f"totaling {self.format_currency(total_recurring)} per month."
                )
            else:
                rationale_parts.append(
                    f"You have {sub_count} recurring subscriptions totaling "
                    f"{self.format_currency(total_recurring)} per month."
                )

            if sub_share >= 10:
                rationale_parts.append(
                    f"This represents {self.format_percent(sub_share)} of your total spending."
                )

        if rationale_parts:
            return " ".join(rationale_parts)

        return self._generate_generic_rationale(recommendation)

    def generate_rationale_for_persona_4(
        self,
        recommendation: Dict[str, Any],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        user_id: uuid.UUID,
    ) -> str:
        """
        Generate rationale for Persona 4: Savings Builder.

        Args:
            recommendation: Recommendation dictionary
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            user_id: User ID for fetching account details

        Returns:
            Plain-language rationale string
        """
        savings_signals = signals_180d.get("savings", {}) or signals_30d.get("savings", {})
        if not savings_signals:
            return self._generate_generic_rationale(recommendation)

        rationale_parts = []

        # Get savings account details
        savings_accounts = self.db.query(AccountModel).filter(
            AccountModel.user_id == user_id,
            AccountModel.type == "depository",
            AccountModel.subtype.in_(["savings", "money market", "hsa"])
        ).all()

        growth_rate = savings_signals.get("savings_growth_rate_percent", None)
        net_inflow = savings_signals.get("net_inflow_monthly", None)

        if savings_accounts:
            account = savings_accounts[0]
            account_display = self.format_account_number(account)
            balance = float(account.balance_current) if account.balance_current else 0

            if growth_rate and growth_rate >= 2:
                rationale_parts.append(
                    f"Your {account_display} is growing at {self.format_percent(growth_rate)} "
                    f"and currently has a balance of {self.format_currency(balance)}."
                )
            elif net_inflow and net_inflow >= 200:
                rationale_parts.append(
                    f"You're saving {self.format_currency(net_inflow)} per month in your {account_display}, "
                    f"which currently has a balance of {self.format_currency(balance)}."
                )
        else:
            if growth_rate and growth_rate >= 2:
                rationale_parts.append(
                    f"Your savings are growing at {self.format_percent(growth_rate)}."
                )
            elif net_inflow and net_inflow >= 200:
                rationale_parts.append(
                    f"You're saving {self.format_currency(net_inflow)} per month."
                )

        # Emergency fund coverage
        emergency_fund_coverage = savings_signals.get("emergency_fund_coverage_months", None)
        if emergency_fund_coverage is not None:
            rationale_parts.append(
                f"Your emergency fund covers {emergency_fund_coverage:.1f} months of expenses."
            )

        if rationale_parts:
            return " ".join(rationale_parts)

        return self._generate_generic_rationale(recommendation)

    def generate_rationale_for_persona_5(
        self,
        recommendation: Dict[str, Any],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        user_id: uuid.UUID,
    ) -> str:
        """
        Generate rationale for Persona 5: Custom Persona.

        Args:
            recommendation: Recommendation dictionary
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            user_id: User ID for fetching account details

        Returns:
            Plain-language rationale string
        """
        # For custom persona, use generic rationale but try to include any available signals
        rationale_parts = []

        # Try to find any notable signals
        all_signals = {**signals_30d, **signals_180d}

        # Check for any credit signals
        if all_signals.get("credit"):
            credit = all_signals["credit"]
            if credit.get("high_utilization_cards"):
                card = credit["high_utilization_cards"][0]
                account_display = card.get("account_name", "your credit card")
                utilization = card.get("utilization_percent", 0)
                rationale_parts.append(
                    f"Your {account_display} is at {utilization:.0f}% utilization."
                )

        # Check for subscription signals
        if all_signals.get("subscriptions"):
            subs = all_signals["subscriptions"]
            sub_count = subs.get("subscription_count", 0)
            if sub_count >= 3:
                rationale_parts.append(
                    f"You have {sub_count} recurring subscriptions."
                )

        # Check for savings signals
        if all_signals.get("savings"):
            savings = all_signals["savings"]
            net_inflow = savings.get("net_inflow_monthly", 0)
            if net_inflow and net_inflow > 0:
                rationale_parts.append(
                    f"You're saving {self.format_currency(net_inflow)} per month."
                )

        if rationale_parts:
            return " ".join(rationale_parts)

        return self._generate_generic_rationale(recommendation)

    def _generate_generic_rationale(self, recommendation: Dict[str, Any]) -> str:
        """
        Generate generic rationale when no specific signals are available.

        Args:
            recommendation: Recommendation dictionary

        Returns:
            Generic rationale string
        """
        rec_type = recommendation.get("id", "").split("_")[0]

        if rec_type == "edu":
            return "This educational content matches your financial profile and can help you improve your financial health."
        elif rec_type == "offer":
            return "This offer may help you achieve your financial goals based on your current financial situation."
        else:
            return "This recommendation is tailored to your financial profile."

    def generate_rationale(
        self,
        recommendation: Dict[str, Any],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        persona_id: int,
        user_id: uuid.UUID,
    ) -> str:
        """
        Generate rationale for a recommendation based on persona and signals.

        Args:
            recommendation: Recommendation dictionary (education item or partner offer)
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            persona_id: Persona ID (1-5)
            user_id: User ID for fetching account details

        Returns:
            Plain-language rationale string with data point citations
        """
        # Route to persona-specific rationale generator
        if persona_id == 1:
            rationale = self.generate_rationale_for_persona_1(
                recommendation, signals_30d, signals_180d, user_id
            )
        elif persona_id == 2:
            rationale = self.generate_rationale_for_persona_2(
                recommendation, signals_30d, signals_180d, user_id
            )
        elif persona_id == 3:
            rationale = self.generate_rationale_for_persona_3(
                recommendation, signals_30d, signals_180d, user_id
            )
        elif persona_id == 4:
            rationale = self.generate_rationale_for_persona_4(
                recommendation, signals_30d, signals_180d, user_id
            )
        else:  # Persona 5 or unknown
            rationale = self.generate_rationale_for_persona_5(
                recommendation, signals_30d, signals_180d, user_id
            )

        return rationale

