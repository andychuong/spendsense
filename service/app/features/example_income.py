"""Example usage of income stability detection service."""

import uuid
from sqlalchemy.orm import Session

from app.features.income import IncomeStabilityDetector

# Example: Generate income stability signals for a user
def example_generate_income_signals(db_session: Session, user_id: uuid.UUID):
    """
    Example usage of income stability detection.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to analyze
    """
    # Initialize detector
    detector = IncomeStabilityDetector(db_session)

    # Generate income stability signals for both 30-day and 180-day windows
    signals = detector.generate_income_signals(user_id)

    print(f"Income Stability Signals for User {user_id}:")
    print(f"Generated at: {signals['generated_at']}")

    # 30-day window signals
    signals_30d = signals['signals_30d']
    print(f"\n30-Day Window:")
    print(f"  Payroll Deposits: {len(signals_30d['payroll_deposits'])} deposits")

    if signals_30d['payroll_deposits']:
        total_income = sum(dep['amount'] for dep in signals_30d['payroll_deposits'])
        print(f"  Total Income: ${total_income:.2f}")

    freq = signals_30d['payment_frequency']
    if freq.get('median_gap_days'):
        print(f"  Payment Frequency: {freq['frequency_type']} (median gap: {freq['median_gap_days']} days)")
    else:
        print(f"  Payment Frequency: {freq.get('frequency_type', 'insufficient_data')}")

    var = signals_30d['payment_variability']
    if var.get('coefficient_of_variation') is not None:
        print(f"  Payment Variability: {var['variability_level']} (CV: {var['coefficient_of_variation']:.2f}%)")
        print(f"    Mean Amount: ${var['mean_amount']:.2f}")
        print(f"    Range: ${var['min_amount']:.2f} - ${var['max_amount']:.2f}")
    else:
        print(f"  Payment Variability: {var.get('variability_level', 'insufficient_data')}")

    buffer = signals_30d['cash_flow_buffer']
    print(f"  Cash-Flow Buffer: {buffer['cash_flow_buffer_months']:.2f} months")
    print(f"    Current Balance: ${buffer['current_balance']:.2f}")
    print(f"    Minimum Balance: ${buffer['minimum_balance']:.2f}")
    print(f"    Avg Monthly Expenses: ${buffer['average_monthly_expenses']:.2f}")

    variable = signals_30d['variable_income_pattern']
    if variable['is_variable_income']:
        print(f"  ⚠️  Variable Income Pattern Detected ({variable['confidence']} confidence)")
        for reason in variable['reasons']:
            print(f"    - {reason}")
    else:
        print(f"  Income Pattern: Stable")

    # 180-day window signals
    signals_180d = signals['signals_180d']
    print(f"\n180-Day Window:")
    print(f"  Payroll Deposits: {len(signals_180d['payroll_deposits'])} deposits")

    if signals_180d['payroll_deposits']:
        total_income = sum(dep['amount'] for dep in signals_180d['payroll_deposits'])
        print(f"  Total Income: ${total_income:.2f}")

    freq = signals_180d['payment_frequency']
    if freq.get('median_gap_days'):
        print(f"  Payment Frequency: {freq['frequency_type']} (median gap: {freq['median_gap_days']} days)")

    var = signals_180d['payment_variability']
    if var.get('coefficient_of_variation') is not None:
        print(f"  Payment Variability: {var['variability_level']} (CV: {var['coefficient_of_variation']:.2f}%)")

    buffer = signals_180d['cash_flow_buffer']
    print(f"  Cash-Flow Buffer: {buffer['cash_flow_buffer_months']:.2f} months")

    variable = signals_180d['variable_income_pattern']
    if variable['is_variable_income']:
        print(f"  ⚠️  Variable Income Pattern Detected ({variable['confidence']} confidence)")
    else:
        print(f"  Income Pattern: Stable")

    return signals


# Example: Detect payroll deposits only
def example_detect_payroll_deposits(db_session: Session, user_id: uuid.UUID):
    """
    Example with payroll deposit detection only.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to analyze
    """
    from datetime import date, timedelta

    detector = IncomeStabilityDetector(db_session)

    # Detect payroll deposits in last 90 days
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    payroll_deposits = detector.detect_payroll_deposits(user_id, start_date, end_date)

    print(f"Payroll Deposits for User {user_id} (last 90 days):")
    print(f"  Found {len(payroll_deposits)} deposits")

    if payroll_deposits:
        total_amount = sum(dep['amount'] for dep in payroll_deposits)
        print(f"  Total Amount: ${total_amount:.2f}")
        print(f"\n  Deposits:")
        for dep in payroll_deposits[:10]:  # Show first 10
            print(f"    - {dep['date']}: ${dep['amount']:.2f}")

    return payroll_deposits



