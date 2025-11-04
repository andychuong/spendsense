"""Feature engineering module for behavioral signal detection."""

from app.features.subscriptions import SubscriptionDetector
from app.features.savings import SavingsDetector
from app.features.credit import CreditUtilizationDetector
from app.features.income import IncomeStabilityDetector
from app.features.persona_assignment import PersonaAssignmentService

__all__ = [
    "SubscriptionDetector",
    "SavingsDetector",
    "CreditUtilizationDetector",
    "IncomeStabilityDetector",
    "PersonaAssignmentService",
]
