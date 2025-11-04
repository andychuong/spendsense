"""Example usage of subscription detection service."""

import uuid
from sqlalchemy.orm import Session

from app.features.subscriptions import SubscriptionDetector

# Example: Detect subscriptions for a user
def example_detect_subscriptions(db_session: Session, user_id: uuid.UUID):
    """
    Example usage of subscription detection.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to analyze
    """
    # Initialize detector
    detector = SubscriptionDetector(db_session)

    # Generate subscription signals for both 30-day and 180-day windows
    signals = detector.generate_subscription_signals(user_id)

    print(f"Subscription Signals for User {user_id}:")
    print(f"Generated at: {signals['generated_at']}")

    # 30-day window signals
    signals_30d = signals['signals_30d']
    print(f"\n30-Day Window:")
    print(f"  Subscription Count: {signals_30d['subscription_count']}")
    print(f"  Total Recurring Spend: ${signals_30d['total_recurring_spend']:.2f}/month")
    print(f"  Subscription Share: {signals_30d['subscription_share_percent']:.2f}%")

    if signals_30d['recurring_merchants']:
        print(f"\n  Recurring Merchants:")
        for merchant in signals_30d['recurring_merchants']:
            print(f"    - {merchant['merchant_name']}: ${merchant['monthly_recurring_spend']:.2f}/month ({merchant['cadence_type']})")

    # 180-day window signals
    signals_180d = signals['signals_180d']
    print(f"\n180-Day Window:")
    print(f"  Subscription Count: {signals_180d['subscription_count']}")
    print(f"  Total Recurring Spend: ${signals_180d['total_recurring_spend']:.2f}/month")
    print(f"  Subscription Share: {signals_180d['subscription_share_percent']:.2f}%")

    return signals


# Example: Detect subscriptions with custom parameters
def example_detect_custom(db_session: Session, user_id: uuid.UUID):
    """
    Example with custom detection parameters.

    Args:
        db_session: SQLAlchemy database session
        user_id: User ID to analyze
    """
    detector = SubscriptionDetector(db_session)

    # Detect subscriptions with custom window and minimum occurrences
    subscriptions = detector.detect_subscriptions(
        user_id,
        window_days=180,  # Use 180-day window
        min_occurrences=2  # Require at least 2 transactions
    )

    print(f"Found {len(subscriptions)} recurring merchants:")
    for sub in subscriptions:
        print(f"  - {sub['merchant_name']}: {sub['transaction_count']} transactions, "
              f"${sub['monthly_recurring_spend']:.2f}/month ({sub['cadence_type']})")

    return subscriptions


