"""Example usage of credit utilization detection service."""

import uuid
from sqlalchemy.orm import Session

from app.features.credit import CreditUtilizationDetector

# Example: Generate credit utilization signals for a user
def example_generate_credit_signals(db_session: Session, user_id: uuid.UUID):
    """
    Example usage of credit utilization detection.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to analyze
    """
    # Initialize detector
    detector = CreditUtilizationDetector(db_session)

    # Generate credit utilization signals for both 30-day and 180-day windows
    signals = detector.generate_credit_signals(user_id)

    print(f"Credit Utilization Signals for User {user_id}:")
    print(f"Generated at: {signals['generated_at']}")

    # 30-day window signals
    signals_30d = signals['signals_30d']
    print(f"\n30-Day Window:")
    print(f"  Total Credit Cards: {signals_30d['card_count']}")
    print(f"  Total Utilization: {signals_30d['total_utilization']:.2f}%")
    print(f"  Total Balance: ${signals_30d['total_balance']:.2f}")
    print(f"  Total Limit: ${signals_30d['total_limit']:.2f}")

    if signals_30d['severe_utilization_cards']:
        print(f"\n  Severe Utilization Cards (≥80%): {len(signals_30d['severe_utilization_cards'])}")
        for card in signals_30d['severe_utilization_cards']:
            print(f"    - {card['account_name']}: {card['utilization_percent']:.2f}% "
                  f"(${card['current_balance']:.2f} / ${card['credit_limit']:.2f})")

    if signals_30d['critical_utilization_cards']:
        print(f"\n  Critical Utilization Cards (≥50%): {len(signals_30d['critical_utilization_cards'])}")
        for card in signals_30d['critical_utilization_cards']:
            print(f"    - {card['account_name']}: {card['utilization_percent']:.2f}%")

    if signals_30d['high_utilization_cards']:
        print(f"\n  High Utilization Cards (≥30%): {len(signals_30d['high_utilization_cards'])}")
        for card in signals_30d['high_utilization_cards']:
            print(f"    - {card['account_name']}: {card['utilization_percent']:.2f}%")

    if signals_30d['minimum_payment_only_cards']:
        print(f"\n  Minimum Payment Only Cards: {len(signals_30d['minimum_payment_only_cards'])}")
        for card in signals_30d['minimum_payment_only_cards']:
            min_payment = card['minimum_payment_only']
            print(f"    - {card['account_name']}: {min_payment['reason']}")

    if signals_30d['cards_with_interest']:
        print(f"\n  Cards with Interest Charges: {len(signals_30d['cards_with_interest'])}")
        for card in signals_30d['cards_with_interest']:
            interest = card['interest_charges']
            print(f"    - {card['account_name']}: ${interest['total_interest_charges']:.2f} "
                  f"({interest['interest_count']} charges)")

    if signals_30d['overdue_cards']:
        print(f"\n  Overdue Cards: {len(signals_30d['overdue_cards'])}")
        for card in signals_30d['overdue_cards']:
            overdue = card['overdue']
            print(f"    - {card['account_name']}: {overdue['reason']}")

    # 180-day window signals
    signals_180d = signals['signals_180d']
    print(f"\n180-Day Window:")
    print(f"  Total Credit Cards: {signals_180d['card_count']}")
    print(f"  Total Utilization: {signals_180d['total_utilization']:.2f}%")
    print(f"  Total Balance: ${signals_180d['total_balance']:.2f}")
    print(f"  Total Limit: ${signals_180d['total_limit']:.2f}")

    return signals


# Example: Calculate utilization for a specific account
def example_calculate_account_utilization(db_session: Session, user_id: uuid.UUID):
    """
    Example with account-specific utilization calculation.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to analyze
    """
    detector = CreditUtilizationDetector(db_session)

    # Get credit card accounts
    credit_cards = detector.get_credit_card_accounts(user_id)

    if not credit_cards:
        print(f"No credit card accounts found for user {user_id}")
        return

    print(f"Credit Card Analysis for User {user_id}:")

    for account in credit_cards:
        print(f"\n  Account: {account.name} ({account.account_id})")

        # Get liability for this account
        # Try to import Liability model from backend
        try:
            from backend.app.models.liability import Liability
        except ImportError:
            import sys
            import os
            backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            from app.models.liability import Liability

        liability = db_session.query(Liability).filter(
            Liability.account_id == account.id
        ).first()

        # Calculate utilization
        utilization = detector.calculate_utilization(account, liability)
        print(f"    Utilization: {utilization['utilization_percent']:.2f}% "
              f"({utilization['utilization_level']})")
        print(f"    Balance: ${utilization['current_balance']:.2f} / "
              f"Limit: ${utilization['credit_limit']:.2f}")

        if utilization['flags']:
            print(f"    Flags: {', '.join(utilization['flags'])}")

        # Check minimum payment
        min_payment = detector.detect_minimum_payment_only(account, liability)
        if min_payment['is_minimum_payment_only']:
            print(f"    ⚠️  Minimum Payment Only: {min_payment['reason']}")

        # Check interest charges
        interest = detector.detect_interest_charges(account)
        if interest['has_interest_charges']:
            print(f"    ⚠️  Interest Charges: ${interest['total_interest_charges']:.2f} "
                  f"({interest['interest_count']} charges)")

        # Check overdue
        overdue = detector.detect_overdue_accounts(account, liability)
        if overdue['is_overdue']:
            print(f"    ⚠️  Overdue: {overdue['reason']}")

