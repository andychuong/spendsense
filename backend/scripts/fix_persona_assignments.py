#!/usr/bin/env python3
"""Script to fix persona assignments by excluding essential bills from subscriptions."""

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
from app.models.user_persona_assignment import UserPersonaAssignment
from app.features.persona_assignment import PersonaAssignmentService
from app.features.subscriptions import SubscriptionDetector
from app.common.feature_cache import invalidate_all_feature_signals_cache

def main():
    db = SessionLocal()
    
    try:
        # Find specific users mentioned
        david = db.query(User).filter(User.email == 'user47@test.com').first()
        joseph = db.query(User).filter(User.email == 'user3@test.com').first()
        
        if david:
            print(f"\n=== Checking David Murphy (user47@test.com) ===")
            # Clear cache first
            invalidate_all_feature_signals_cache(david.user_id)
            subscription_detector = SubscriptionDetector(db)
            signals_30d = subscription_detector.calculate_subscription_signals(david.user_id, 30)
            print(f"Subscription count: {signals_30d.get('subscription_count', 0)}")
            recurring = signals_30d.get("recurring_merchants", [])
            if recurring:
                print("Detected subscriptions:")
                for sub in recurring:
                    print(f"  - {sub.get('merchant_name', 'Unknown')}: ${sub.get('monthly_recurring_spend', 0):.2f}/month")
            else:
                print("No subscriptions detected!")
        
        if joseph:
            print(f"\n=== Checking Joseph Stewart (user3@test.com) ===")
            # Clear cache first
            invalidate_all_feature_signals_cache(joseph.user_id)
            subscription_detector = SubscriptionDetector(db)
            signals_30d = subscription_detector.calculate_subscription_signals(joseph.user_id, 30)
            print(f"Subscription count: {signals_30d.get('subscription_count', 0)}")
            recurring = signals_30d.get("recurring_merchants", [])
            if recurring:
                print("Detected subscriptions:")
                for sub in recurring:
                    print(f"  - {sub.get('merchant_name', 'Unknown')}: ${sub.get('monthly_recurring_spend', 0):.2f}/month")
            else:
                print("No subscriptions detected!")
        
        # Find all users
        users = db.query(User).filter(User.email.like('user%@test.com')).all()
        
        print(f"\n\nReassigning personas for {len(users)} users...")
        
        persona_service = PersonaAssignmentService(db_session=db)
        
        for user in users:
            # Clear cache for this user to force fresh signal calculation
            invalidate_all_feature_signals_cache(user.user_id)
            
            # Delete existing assignment
            db.query(UserPersonaAssignment).filter(UserPersonaAssignment.user_id == user.user_id).delete()
            
            # Reassign persona
            try:
                result = persona_service.assign_persona(user.user_id)
                
                # Check assigned persona
                assignment = db.query(UserPersonaAssignment).filter(
                    UserPersonaAssignment.user_id == user.user_id
                ).first()
                
                if assignment:
                    if user.email in ['user47@test.com', 'user3@test.com']:
                        print(f"  ✓ {user.email}: {assignment.persona_id} - {assignment.rationale}")
                    else:
                        print(f"  ✓ {user.email}: {assignment.persona_id}")
                else:
                    print(f"  ✗ {user.email}: No persona assigned")
            except Exception as e:
                print(f"  ✗ {user.email}: Error - {e}")
                db.rollback()
                continue
        
        db.commit()
        print("\n✅ Persona reassignment complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

