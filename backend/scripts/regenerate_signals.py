#!/usr/bin/env python3
"""Script to regenerate signals for all users with profiles."""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add service to path
_project_root = os.path.dirname(backend_path)
_service_dir = os.path.join(_project_root, "service")
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.user_profile import UserProfile

# Import cache invalidation functions
from app.common.feature_cache import (
    invalidate_income_signals_cache,
    invalidate_subscription_signals_cache,
    invalidate_savings_signals_cache,
    invalidate_credit_signals_cache,
)
from app.core.cache_service import invalidate_user_profile_cache

# Import services
try:
    from app.features.persona_assignment import PersonaAssignmentService
    PERSONA_SERVICE_AVAILABLE = True
except ImportError:
    PERSONA_SERVICE_AVAILABLE = False
    print("⚠ PersonaAssignmentService not available")


def _serialize_for_json(obj):
    """Recursively convert UUID objects and dates to strings for JSON serialization."""
    import uuid
    from datetime import datetime, date
    
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_for_json(item) for item in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj


def regenerate_signals_for_user(db: Session, user_id: str):
    """Regenerate signals for a single user."""
    import uuid
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        print(f"  ✗ Invalid user ID: {user_id}")
        return False
    
    try:
        # Generate signals explicitly
        from app.features.subscriptions import SubscriptionDetector
        from app.features.savings import SavingsDetector
        from app.features.credit import CreditUtilizationDetector
        from app.features.income import IncomeStabilityDetector
        
        # Clear all caches before regenerating to ensure fresh data
        print(f"  Clearing all caches...")
        invalidate_income_signals_cache(user_uuid)
        invalidate_subscription_signals_cache(user_uuid)
        invalidate_savings_signals_cache(user_uuid)
        invalidate_credit_signals_cache(user_uuid)
        # Clear the profile API response cache too
        invalidate_user_profile_cache(user_uuid)
        
        subscription_detector = SubscriptionDetector(db_session=db)
        savings_detector = SavingsDetector(db_session=db)
        credit_detector = CreditUtilizationDetector(db_session=db)
        income_detector = IncomeStabilityDetector(db_session=db)
        
        # Generate income signals directly by calling calculate_income_signals for both windows
        # This bypasses the cache decorator on generate_income_signals
        income_signals_30d = income_detector.calculate_income_signals(user_uuid, window_days=30)
        income_signals_180d = income_detector.calculate_income_signals(user_uuid, window_days=180)
        
        # Format as generate_income_signals would return
        from datetime import datetime
        income_signals = {
            "user_id": str(user_uuid),
            "generated_at": datetime.utcnow().isoformat(),
            "signals_30d": income_signals_30d,
            "signals_180d": income_signals_180d,
        }
        
        # Debug: Check what income_signals contains
        print(f"  Debug - Income signals keys: {list(income_signals.keys())}")
        print(f"  Debug - signals_30d keys: {list(income_signals.get('signals_30d', {}).keys())}")
        print(f"  Debug - signals_180d keys: {list(income_signals.get('signals_180d', {}).keys())}")
        
        income_30d_raw = income_signals.get("signals_30d", {})
        income_180d_raw = income_signals.get("signals_180d", {})
        
        print(f"  Debug - 30d payroll deposits: {len(income_30d_raw.get('payroll_deposits', []))}")
        print(f"  Debug - 180d payroll deposits: {len(income_180d_raw.get('payroll_deposits', []))}")
        
        if income_30d_raw.get('payroll_deposits'):
            print(f"  Debug - Sample 30d deposit: {income_30d_raw['payroll_deposits'][0]}")
        
        subscription_signals = subscription_detector.generate_subscription_signals(user_uuid)
        savings_signals = savings_detector.generate_savings_signals(user_uuid)
        credit_signals = credit_detector.generate_credit_signals(user_uuid)
        
        signals_30d = {
            "subscriptions": subscription_signals.get("signals_30d", {}),
            "savings": savings_signals.get("signals_30d", {}),
            "credit": credit_signals.get("signals_30d", {}),
            "income": income_signals.get("signals_30d", {}),
        }
        
        signals_180d = {
            "subscriptions": subscription_signals.get("signals_180d", {}),
            "savings": savings_signals.get("signals_180d", {}),
            "credit": credit_signals.get("signals_180d", {}),
            "income": income_signals.get("signals_180d", {}),
        }
        
        # Serialize signals (convert UUIDs to strings)
        signals_30d_serialized = _serialize_for_json(signals_30d)
        signals_180d_serialized = _serialize_for_json(signals_180d)
        
        # Save signals to profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_uuid).first()
        if not profile:
            profile = UserProfile(
                user_id=user_uuid,
                signals_30d=signals_30d_serialized,
                signals_180d=signals_180d_serialized,
            )
            db.add(profile)
        else:
            profile.signals_30d = signals_30d_serialized
            profile.signals_180d = signals_180d_serialized
        db.commit()
        
        # Clear the profile cache again after updating database
        # This ensures the next API call gets fresh data
        invalidate_user_profile_cache(user_uuid)
        print(f"  ✓ Profile cache cleared after database update")
        
        # Check if income signals were generated
        income_30d = signals_30d.get('income', {})
        income_180d = signals_180d.get('income', {})
        
        payroll_count_30d = len(income_30d.get('payroll_deposits', []))
        payroll_count_180d = len(income_180d.get('payroll_deposits', []))
        
        mean_amount_30d = income_30d.get('payment_variability', {}).get('mean_amount')
        mean_amount_180d = income_180d.get('payment_variability', {}).get('mean_amount')
        
        if payroll_count_30d >= 2 or payroll_count_180d >= 2:
            print(f"  ✓ Signals regenerated - 30d: {payroll_count_30d} deposits, 180d: {payroll_count_180d} deposits")
            if mean_amount_30d:
                print(f"    Mean amount (30d): ${mean_amount_30d:.2f}")
            if mean_amount_180d:
                print(f"    Mean amount (180d): ${mean_amount_180d:.2f}")
            return True
        else:
            print(f"  ⚠ Signals regenerated but still insufficient data - 30d: {payroll_count_30d} deposits, 180d: {payroll_count_180d} deposits")
            return False
            
    except Exception as e:
        import traceback
        print(f"  ✗ Error: {str(e)}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False


def main():
    if not PERSONA_SERVICE_AVAILABLE:
        print("❌ PersonaAssignmentService not available. Cannot regenerate signals.")
        return
    
    db = SessionLocal()
    
    try:
        # Get all users with profiles
        users_with_profiles = db.query(User).join(UserProfile).filter(
            User.role == "user"
        ).all()
        
        print(f"🔄 Regenerating signals for {len(users_with_profiles)} users...\n")
        
        success_count = 0
        error_count = 0
        
        for i, user in enumerate(users_with_profiles, 1):
            print(f"[{i}/{len(users_with_profiles)}] Processing {user.email}...")
            if regenerate_signals_for_user(db, str(user.user_id)):
                success_count += 1
            else:
                error_count += 1
        
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Success: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Total: {len(users_with_profiles)}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
