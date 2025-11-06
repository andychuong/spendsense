"""Spending category analysis service for calculating spending breakdowns by category."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.common.feature_cache import cache_feature_signals, CACHE_PREFIX_SUBSCRIPTIONS
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


# Category mapping and grouping
CATEGORY_GROUPS = {
    "Food & Dining": [
        "Food and Drink",
        "Food & Drink",
        "Restaurants",
        "Fast Food",
        "Coffee Shops",
        "Bars",
        "Food Delivery",
        "Dining"
    ],
    "Groceries": [
        "Groceries",
        "Supermarkets and Groceries"
    ],
    "Transportation": [
        "Transportation",
        "Transport",
        "Gas Stations",
        "Parking",
        "Public Transportation",
        "Ride Sharing",
        "Auto & Transport"
    ],
    "Shopping": [
        "Shopping",
        "General Merchandise",
        "Clothing and Apparel",
        "Electronics and Software",
        "Home Improvement",
        "Online Marketplaces",
        "Retail"
    ],
    "Bills & Utilities": [
        "Bills & Utilities",
        "Internet",
        "Mobile Phone",
        "Utilities",
        "Cable"
    ],
    "Entertainment": [
        "Entertainment",
        "Movies & Music",
        "Sports and Recreation",
        "Arts and Entertainment"
    ],
    "Healthcare": [
        "Healthcare",
        "Medical",
        "Pharmacies"
    ],
    "Travel": [
        "Travel",
        "Airlines and Aviation Services",
        "Hotels and Accommodations"
    ],
    "Personal Care": [
        "Personal Care",
        "Gyms and Fitness Centers",
        "Hair Salons and Barbers"
    ],
    "Financial": [
        "Bank Fees",
        "ATM Fees",
        "Wire Transfer",
        "Credit Card",
        "Loan Payment"
    ],
    "Other": []  # Catch-all
}


class SpendingCategoryAnalyzer:
    """Analyzes spending by category."""
    
    def __init__(self, db_session: Session):
        """
        Initialize spending category analyzer.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.consent_guardrails = ConsentGuardrails(db_session)
    
    def get_category_group(self, category_primary: str, merchant_name: str = None) -> str:
        """
        Map a category to its group.
        
        Args:
            category_primary: Primary category from transaction
            merchant_name: Merchant name (optional, for special cases)
        
        Returns:
            Category group name
        """
        if not category_primary:
            return "Other"
        
        # Special merchant overrides
        if merchant_name:
            merchant_lower = merchant_name.lower()
            if 'amazon' in merchant_lower:
                return "Shopping"
            if 'walmart' in merchant_lower or 'target' in merchant_lower:
                return "Shopping"
        
        for group, categories in CATEGORY_GROUPS.items():
            if category_primary in categories:
                return group
        
        # Check partial matches
        category_lower = category_primary.lower()
        for group, categories in CATEGORY_GROUPS.items():
            for cat in categories:
                if cat.lower() in category_lower or category_lower in cat.lower():
                    return group
        
        return "Other"
    
    def calculate_spending_by_category(
        self,
        user_id: uuid.UUID,
        window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate spending breakdown by category.
        
        Args:
            user_id: User ID
            window_days: Time window in days (default: 30)
        
        Returns:
            Dictionary with spending by category
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=window_days)
        
        logger.info(f"Calculating spending by category for user {user_id} from {start_date} to {end_date}")
        
        # Get all expense transactions (negative amounts)
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.pending == False,
                Transaction.amount < 0  # Expenses only
            )
        ).all()
        
        if not transactions:
            logger.info(f"No expense transactions found for user {user_id}")
            return {
                "window_days": window_days,
                "window_start": start_date.isoformat(),
                "window_end": end_date.isoformat(),
                "categories": [],
                "total_spending": 0.0,
                "transaction_count": 0
            }
        
        # Group by category
        category_spending = defaultdict(lambda: {"amount": Decimal("0.0"), "count": 0, "transactions": []})
        total_spending = Decimal("0.0")
        
        for txn in transactions:
            amount = abs(Decimal(str(txn.amount)))  # Absolute value for expenses
            category_group = self.get_category_group(txn.category_primary, txn.merchant_name)
            
            category_spending[category_group]["amount"] += amount
            category_spending[category_group]["count"] += 1
            category_spending[category_group]["transactions"].append({
                "date": txn.date.isoformat(),
                "merchant": txn.merchant_name,
                "amount": float(amount),
                "category_primary": txn.category_primary,
                "category_detailed": txn.category_detailed
            })
            
            total_spending += amount
        
        # Convert to list and calculate percentages
        categories = []
        for category_group, data in category_spending.items():
            amount = float(data["amount"])
            percentage = (amount / float(total_spending) * 100) if total_spending > 0 else 0.0
            
            # Get top merchants in this category
            merchant_spending = defaultdict(float)
            for txn in data["transactions"]:
                if txn["merchant"]:
                    merchant_spending[txn["merchant"]] += txn["amount"]
            
            top_merchants = sorted(
                merchant_spending.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            categories.append({
                "category": category_group,
                "amount": round(amount, 2),
                "percentage": round(percentage, 2),
                "transaction_count": data["count"],
                "top_merchants": [
                    {"merchant": merchant, "amount": round(amt, 2)}
                    for merchant, amt in top_merchants
                ],
                "average_transaction": round(amount / data["count"], 2) if data["count"] > 0 else 0.0
            })
        
        # Sort by amount (highest first)
        categories.sort(key=lambda x: x["amount"], reverse=True)
        
        return {
            "window_days": window_days,
            "window_start": start_date.isoformat(),
            "window_end": end_date.isoformat(),
            "categories": categories,
            "total_spending": round(float(total_spending), 2),
            "transaction_count": len(transactions),
            "top_category": categories[0]["category"] if categories else None,
            "top_category_amount": categories[0]["amount"] if categories else 0.0
        }
    
    def generate_spending_signals(
        self,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Generate spending category signals for 30-day and 180-day windows.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with spending signals for both windows
        """
        # Check consent
        try:
            self.consent_guardrails.require_consent(user_id, "feature_detection:spending_categories")
        except ConsentError as e:
            logger.warning(f"Spending category signal generation blocked: {str(e)}")
            raise
        
        # Calculate for both windows
        signals_30d = self.calculate_spending_by_category(user_id, window_days=30)
        signals_180d = self.calculate_spending_by_category(user_id, window_days=180)
        
        return {
            "user_id": str(user_id),
            "generated_at": datetime.now().isoformat(),
            "signals_30d": signals_30d,
            "signals_180d": signals_180d
        }

