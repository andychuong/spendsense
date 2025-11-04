"""Example usage of savings pattern detection service."""

import uuid
from sqlalchemy.orm import Session

from app.features.savings import SavingsDetector

# Example: Generate savings signals for a user
def example_generate_savings_signals(db_session: Session, user_id: uuid.UUID):
    """
    Example usage of savings pattern detection.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to analyze
    """
    # Initialize detector
    detector = SavingsDetector(db_session)

    # Generate savings signals for both 30-day and 180-day windows
    signals = detector.generate_savings_signals(user_id)

    print(f"Savings Signals for User {user_id}:")
    print(f"Generated at: {signals['generated_at']}")

    # 30-day window signals
    signals_30d = signals['signals_30d']
    print(f"\n30-Day Window:")
    print(f"  Net Inflow: ${signals_30d['net_inflow']['net_inflow']:.2f}")
    print(f"  Growth Rate: {signals_30d['growth_rate']['growth_rate_percent']:.2f}%")
    print(f"  Emergency Fund Coverage: {signals_30d['emergency_fund_coverage']['coverage_months']:.2f} months")
    print(f"  Savings Balance: ${signals_30d['savings_balance']:.2f}")

    if signals_30d['net_inflow']['account_details']:
        print(f"\n  Net Inflow Details:")
        for acc_detail in signals_30d['net_inflow']['account_details']:
            print(f"    - {acc_detail['account_name']}: ${acc_detail['net_inflow']:.2f}")

    # 180-day window signals
    signals_180d = signals['signals_180d']
    print(f"\n180-Day Window:")
    print(f"  Net Inflow: ${signals_180d['net_inflow']['net_inflow']:.2f}")
    print(f"  Growth Rate: {signals_180d['growth_rate']['growth_rate_percent']:.2f}%")
    print(f"  Emergency Fund Coverage: {signals_180d['emergency_fund_coverage']['coverage_months']:.2f} months")
    print(f"  Savings Balance: ${signals_180d['savings_balance']:.2f}")

    return signals


# Example: Calculate emergency fund coverage
def example_emergency_fund_coverage(db_session: Session, user_id: uuid.UUID):
    """
    Example with emergency fund coverage calculation.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to analyze
    """
    detector = SavingsDetector(db_session)

    # Calculate emergency fund coverage (default uses 90-day window for expenses)
    emergency_fund = detector.calculate_emergency_fund_coverage(user_id, window_days=90)

    print(f"Emergency Fund Analysis for User {user_id}:")
    print(f"  Total Savings Balance: ${emergency_fund['savings_balance']:.2f}")
    print(f"  Average Monthly Expenses: ${emergency_fund['average_monthly_expenses']:.2f}")
    print(f"  Coverage: {emergency_fund['coverage_months']:.2f} months")

    if emergency_fund['account_details']:
        print(f"\n  Savings Accounts:")
        for acc_detail in emergency_fund['account_details']:
            print(f"    - {acc_detail['account_name']} ({acc_detail['subtype']}): ${acc_detail['balance']:.2f}")

    return emergency_fund

