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

# Try to import OpenAI client
try:
    from app.common.openai_client import get_openai_client
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    def get_openai_client():
        return None

logger = logging.getLogger(__name__)


class RationaleGenerator:
    """Service for generating plain-language rationales with specific data point citations."""

    def __init__(self, db_session: Session, use_openai: bool = True):
        """
        Initialize rationale generator.

        Args:
            db_session: SQLAlchemy database session
            use_openai: Whether to use OpenAI for enhanced rationale generation (default: True)
        """
        self.db = db_session
        self.use_openai = use_openai
        self.openai_client = get_openai_client() if use_openai and OPENAI_AVAILABLE else None

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
            interest_paid = credit_signals.get("total_interest_paid_30d", 0)

            rationale = (
                f"We noticed your {account_display} is at {utilization:.0f}% utilization "
                f"(${balance:,.2f} of ${limit:,.2f} limit). "
                f"Bringing this below 30% could significantly improve your credit score."
            )
            if interest_paid > 0:
                rationale += f" It could also help you save on interest charges (you paid ${interest_paid:,.2f} last month)."
            rationale_parts.append(rationale)

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
                    f"We noticed you have {sub_count} subscriptions totaling ${total_recurring:,.2f}/month. "
                    f"Reviewing these regularly is a great way to find opportunities to save."
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
        total_inflows = savings_signals.get("total_savings_inflows_30d", 0)

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
            return "This educational content can help you build stronger financial habits and improve your long-term financial health."
        elif rec_type == "offer":
            return "Based on your financial profile, this offer could help you reach your financial goals faster."
        else:
            return "This recommendation is selected specifically for your financial situation."

    def _build_data_context(
        self,
        user_id: uuid.UUID,
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        persona_id: int,
    ) -> str:
        """
        Build comprehensive data context string with all concrete data points for OpenAI prompt.

        Args:
            user_id: User ID
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            persona_id: Persona ID

        Returns:
            Formatted context string with all concrete data points
        """
        context_parts = []
        
        # Get all accounts for reference
        accounts = self.db.query(AccountModel).filter(
            AccountModel.user_id == user_id
        ).all()
        
        account_map = {}
        for acc in accounts:
            account_map[acc.account_id] = {
                "name": acc.name,
                "mask": acc.mask,
                "type": acc.type,
                "subtype": acc.subtype,
                "balance_current": float(acc.balance_current) if acc.balance_current else 0,
                "balance_limit": float(acc.balance_limit) if acc.balance_limit else 0,
            }
        
        # Persona-specific data extraction
        if persona_id == 1:  # High Utilization
            credit_signals = signals_30d.get("credit", {}) or signals_180d.get("credit", {})
            if credit_signals:
                context_parts.append("CREDIT CARD UTILIZATION:")
                critical_cards = credit_signals.get("critical_utilization_cards", [])
                severe_cards = credit_signals.get("severe_utilization_cards", [])
                high_cards = credit_signals.get("high_utilization_cards", [])
                
                for card_list in [critical_cards, severe_cards, high_cards]:
                    for card in card_list[:3]:  # Limit to top 3
                        account_id = card.get("account_id")
                        account_name = card.get("account_name", "Unknown")
                        utilization = card.get("utilization_percent", 0)
                        balance = card.get("current_balance", 0)
                        limit = card.get("credit_limit", 0)
                        
                        # Try to get account mask if available
                        account_display = account_name
                        if account_id:
                            # Find account in database
                            account = self.db.query(AccountModel).filter(
                                AccountModel.user_id == user_id,
                                AccountModel.account_id == account_id
                            ).first()
                            if account:
                                account_display = self.format_account_number(account)
                        
                        context_parts.append(
                            f"- {account_display}: {utilization:.0f}% utilization "
                            f"(${balance:,.2f} of ${limit:,.2f} limit)"
                        )
                
                # Interest charges
                interest_cards = credit_signals.get("cards_with_interest", [])
                if interest_cards:
                    total_interest = sum([
                        card.get("interest_charges", {}).get("total_interest_charges", 0)
                        for card in interest_cards
                    ])
                    if total_interest > 0:
                        context_parts.append(f"\nMONTHLY INTEREST CHARGES: ${total_interest:,.2f}")
        
        elif persona_id == 2:  # Variable Income Budgeter
            income_signals = signals_180d.get("income", {}) or signals_30d.get("income", {})
            if income_signals:
                context_parts.append("INCOME PATTERNS:")
                income_patterns = income_signals.get("income_patterns", {})
                median_gap = income_patterns.get("median_pay_gap_days")
                if median_gap:
                    context_parts.append(f"- Median gap between payments: {median_gap:.0f} days")
                
                # Get recent payroll deposits
                recent_transactions = self.get_recent_transactions(user_id, limit=10)
                payroll_deposits = [
                    t for t in recent_transactions
                    if t.category_primary == "PAYROLL" and t.amount > 0
                ]
                if payroll_deposits:
                    latest = payroll_deposits[0]
                    context_parts.append(
                        f"- Last payroll deposit: {self.format_date(latest.date)} "
                        f"(${float(latest.amount):,.2f})"
                    )
                
                cash_buffer = income_signals.get("cash_flow_buffer_months")
                if cash_buffer is not None:
                    context_parts.append(f"- Cash flow buffer: {cash_buffer:.2f} months")
        
        elif persona_id == 3:  # Subscription-Heavy
            sub_signals = signals_30d.get("subscriptions", {}) or signals_180d.get("subscriptions", {})
            if sub_signals:
                context_parts.append("SUBSCRIPTIONS:")
                sub_count = sub_signals.get("subscription_count", 0)
                total_recurring = sub_signals.get("total_recurring_spend", 0)
                sub_share = sub_signals.get("subscription_share_percent", 0)
                
                context_parts.append(f"- Total subscriptions: {sub_count}")
                context_parts.append(f"- Monthly recurring spend: ${total_recurring:,.2f}")
                if sub_share > 0:
                    context_parts.append(f"- Subscription share of spending: {sub_share:.1f}%")
                
                recurring_merchants = sub_signals.get("recurring_merchants", [])
                if recurring_merchants:
                    context_parts.append("\nTop recurring merchants:")
                    for merchant in recurring_merchants[:5]:
                        name = merchant.get("merchant_name", "Unknown")
                        amount = merchant.get("monthly_amount", 0)
                        context_parts.append(f"- {name}: ${amount:,.2f}/month")
        
        elif persona_id == 4:  # Savings Builder
            savings_signals = signals_180d.get("savings", {}) or signals_30d.get("savings", {})
            if savings_signals:
                context_parts.append("SAVINGS:")
                savings_accounts = self.db.query(AccountModel).filter(
                    AccountModel.user_id == user_id,
                    AccountModel.type == "depository",
                    AccountModel.subtype.in_(["savings", "money market", "hsa"])
                ).all()
                
                if savings_accounts:
                    for acc in savings_accounts[:3]:
                        account_display = self.format_account_number(acc)
                        balance = float(acc.balance_current) if acc.balance_current else 0
                        context_parts.append(f"- {account_display}: ${balance:,.2f}")
                
                growth_rate = savings_signals.get("savings_growth_rate_percent")
                net_inflow = savings_signals.get("net_inflow_monthly")
                emergency_coverage = savings_signals.get("emergency_fund_coverage_months")
                
                if growth_rate:
                    context_parts.append(f"- Savings growth rate: {growth_rate:.2f}%")
                if net_inflow:
                    context_parts.append(f"- Monthly savings inflow: ${net_inflow:,.2f}")
                if emergency_coverage is not None:
                    context_parts.append(f"- Emergency fund coverage: {emergency_coverage:.1f} months")
        
        return "\n".join(context_parts) if context_parts else "No specific data available."

    def _generate_openai_rationale(
        self,
        recommendation: Dict[str, Any],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
        persona_id: int,
        user_id: uuid.UUID,
    ) -> Optional[str]:
        """
        Generate enhanced rationale using OpenAI with concrete data citations.

        Args:
            recommendation: Recommendation dictionary
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            persona_id: Persona ID
            user_id: User ID

        Returns:
            Generated rationale string or None if generation fails
        """
        if not self.openai_client or not self.openai_client.client:
            return None
        
        # Build comprehensive data context
        data_context = self._build_data_context(user_id, signals_30d, signals_180d, persona_id)
        
        persona_names = {
            1: "High Utilization",
            2: "Variable Income Budgeter",
            3: "Subscription-Heavy",
            4: "Savings Builder",
            5: "Custom Persona",
        }
        persona_name = persona_names.get(persona_id, "Custom Persona")
        
        recommendation_type = "education" if recommendation.get("id", "").startswith("edu_") else "partner offer"
        
        prompt = f"""Generate a personalized "because" rationale for a financial recommendation.

USER CONTEXT:
- Persona: {persona_name} (Persona {persona_id})
- Recommendation Type: {recommendation_type}
- Recommendation Title: {recommendation.get('title', 'N/A')}

CONCRETE USER DATA:
{data_context}

REQUIREMENTS:
- Write in plain, friendly language (NO financial jargon)
- MUST cite specific data points from the user data above (account names with last 4 digits, exact amounts, percentages, dates)
- Format: Start with "We noticed" or "Because" and cite specific data
- Example format: "We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could improve your credit score and reduce interest charges of $87/month."
- Keep it empowering and educational (not judgmental)
- Length: 2-4 sentences
- Include actionable benefit (what they can gain)

Generate the personalized rationale:"""

        try:
            generated_rationale = self.openai_client.generate_content(
                prompt=prompt,
                persona_id=persona_id,
                signals={**signals_30d, **signals_180d},
                use_cache=True,
            )
            
            if generated_rationale:
                logger.info(f"Generated OpenAI-enhanced rationale for recommendation {recommendation.get('id')}")
                return generated_rationale.strip()
        except Exception as e:
            logger.warning(f"OpenAI rationale generation failed: {str(e)}, falling back to rule-based rationale")
        
        return None

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
        Uses OpenAI if available, falls back to rule-based generation.

        Args:
            recommendation: Recommendation dictionary (education item or partner offer)
            signals_30d: 30-day signals
            signals_180d: 180-day signals
            persona_id: Persona ID (1-5)
            user_id: User ID for fetching account details

        Returns:
            Plain-language rationale string with data point citations
        """
        # Try OpenAI-enhanced rationale first if enabled
        if self.use_openai and self.openai_client:
            openai_rationale = self._generate_openai_rationale(
                recommendation, signals_30d, signals_180d, persona_id, user_id
            )
            if openai_rationale:
                return openai_rationale
        
        # Fallback to rule-based rationale generation
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

