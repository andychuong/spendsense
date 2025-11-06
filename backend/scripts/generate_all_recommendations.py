#!/usr/bin/env python3
"""Script to generate recommendations for all users with profiles."""

import sys
import os
import uuid

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
from app.models.user_persona_assignment import UserPersonaAssignment

# Try to import services
try:
    from app.features.persona_assignment import PersonaAssignmentService
    PERSONA_SERVICE_AVAILABLE = True
except ImportError:
    PERSONA_SERVICE_AVAILABLE = False
    print("⚠ PersonaAssignmentService not available")

try:
    from app.recommendations.rag_integration import create_enhanced_generator
    RECOMMENDATION_SERVICE_AVAILABLE = True
except ImportError:
    try:
        from app.recommendations.generator import RecommendationGenerator as create_enhanced_generator
        RECOMMENDATION_SERVICE_AVAILABLE = True
        print("⚠ Using legacy RecommendationGenerator (RAG integration not available)")
    except ImportError:
        RECOMMENDATION_SERVICE_AVAILABLE = False
        print("⚠ RecommendationGenerator not available")


def generate_recommendations_for_all_users():
    """Generate recommendations for all users who have profiles and personas."""
    db = SessionLocal()
    
    try:
        # Get all users with profiles
        users_with_profiles = db.query(User).join(
            UserProfile, User.user_id == UserProfile.user_id
        ).filter(
            User.role == "user"
        ).all()
        
        print(f"Found {len(users_with_profiles)} users with profiles")
        
        if not users_with_profiles:
            print("No users with profiles found. Users need to have data uploaded first.")
            return
        
        if not RECOMMENDATION_SERVICE_AVAILABLE:
            print("RecommendationGenerator not available. Cannot generate recommendations.")
            return
        
        # Create enhanced generator with RAG support (or fallback to legacy)
        try:
            generator = create_enhanced_generator(db_session=db)
            print("✓ Using EnhancedRecommendationGenerator with RAG support")
        except Exception as e:
            print(f"⚠ Failed to create enhanced generator: {e}")
            print("  Falling back to legacy RecommendationGenerator")
            from app.recommendations.generator import RecommendationGenerator
            generator = RecommendationGenerator(db_session=db, use_openai=True)
        
        success_count = 0
        error_count = 0
        
        for user in users_with_profiles:
            try:
                # Check if user has persona assigned
                persona_assignment = db.query(UserPersonaAssignment).filter(
                    UserPersonaAssignment.user_id == user.user_id
                ).first()
                
                if not persona_assignment:
                    print(f"  ⚠ Skipping {user.email} - no persona assigned")
                    continue
                
                print(f"  Generating recommendations for {user.email} (Persona {persona_assignment.persona_id})...")
                
                result = generator.generate_recommendations(user.user_id)
                
                if result.get("error"):
                    print(f"    ✗ Error: {result.get('error')}")
                    error_count += 1
                else:
                    rec_count = len(result.get("recommendations", []))
                    edu_count = result.get("education_count", 0)
                    offer_count = result.get("partner_offer_count", 0)
                    print(f"    ✓ Generated {rec_count} recommendations ({edu_count} education, {offer_count} partner offers)")
                    success_count += 1
                    
            except Exception as e:
                print(f"    ✗ Error generating recommendations for {user.email}: {e}")
                error_count += 1
        
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Success: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Total: {len(users_with_profiles)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("GENERATING RECOMMENDATIONS FOR ALL USERS")
    print("=" * 60)
    generate_recommendations_for_all_users()


