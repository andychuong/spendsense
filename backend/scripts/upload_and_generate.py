#!/usr/bin/env python3
"""Script to upload test data and generate recommendations for users."""

import sys
import os
import json
import uuid
from pathlib import Path

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
from app.models.data_upload import DataUpload, FileType, UploadStatus
from app.models.user_profile import UserProfile
from app.config import settings

# Try to import services
try:
    from app.ingestion.service import IngestionService
    INGESTION_AVAILABLE = True
except ImportError:
    INGESTION_AVAILABLE = False
    print("⚠ IngestionService not available")

try:
    from app.features.persona_assignment import PersonaAssignmentService
    PERSONA_SERVICE_AVAILABLE = True
except ImportError:
    PERSONA_SERVICE_AVAILABLE = False
    print("⚠ PersonaAssignmentService not available")

try:
    from app.recommendations.generator import RecommendationGenerator
    RECOMMENDATION_SERVICE_AVAILABLE = True
except ImportError:
    RECOMMENDATION_SERVICE_AVAILABLE = False
    print("⚠ RecommendationGenerator not available")


def load_test_data(file_path: str) -> dict:
    """Load test data from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def upload_data_and_generate_recommendations(user_count: int = 5):
    """Upload test data for users and generate recommendations."""
    db = SessionLocal()
    
    try:
        # Get test users
        users = db.query(User).filter(User.role == "user").limit(user_count).all()
        
        if not users:
            print("No users found in database.")
            return
        
        print(f"Processing {len(users)} users...")
        
        # Load test data - try multiple possible locations
        possible_paths = [
            Path(_project_root) / "test_data_upload.json",
            Path(backend_path) / ".." / "test_data_upload.json",
            Path(__file__).parent.parent.parent / "test_data_upload.json",
        ]
        
        test_data_path = None
        for path in possible_paths:
            if path.exists():
                test_data_path = path
                break
        
        if not test_data_path:
            print(f"Test data file not found. Tried:")
            for path in possible_paths:
                print(f"  - {path}")
            return
        
        test_data = load_test_data(str(test_data_path))
        
        if not INGESTION_AVAILABLE:
            print("IngestionService not available. Cannot upload data.")
            return
        
        ingestion_service = IngestionService(
            db_session=db,
            s3_bucket=settings.s3_bucket_analytics
        )
        
        success_count = 0
        error_count = 0
        
        for i, user in enumerate(users, 1):
            try:
                # Update user_id in test data
                test_data_copy = json.loads(json.dumps(test_data))  # Deep copy
                test_data_copy["user_id"] = str(user.user_id)
                
                # Convert to JSON string for ingestion
                data_json = json.dumps(test_data_copy)
                file_content = data_json.encode('utf-8')
                file_size = len(file_content)
                
                print(f"\n[{i}/{len(users)}] Processing {user.email}...")
                
                # Create DataUpload record first (required by ingestion service)
                upload_id = uuid.uuid4()
                file_name = f"test_data_{user.user_id}.json"
                
                data_upload = DataUpload(
                    upload_id=upload_id,
                    user_id=user.user_id,
                    file_name=file_name,
                    file_size=file_size,
                    file_type=FileType.JSON.value.lower(),
                    s3_key=f"test/{user.user_id}/{upload_id}/{file_name}",
                    s3_bucket=settings.s3_bucket_data,
                    status=UploadStatus.PROCESSING.value.lower(),
                )
                db.add(data_upload)
                db.commit()
                db.refresh(data_upload)
                
                print("  Created DataUpload record...")
                
                # Ingest data
                print("  Processing data...")
                report = ingestion_service.ingest(
                    file_content=file_content,
                    file_type="json",
                    user_id=user.user_id,
                    upload_id=upload_id,
                )
                
                if report.get("status") == "completed":
                    # Update upload status
                    data_upload.status = UploadStatus.COMPLETED.value.lower()
                    from datetime import datetime
                    data_upload.processed_at = datetime.utcnow()
                    db.commit()
                    
                    print(f"  ✓ Data processed: {report.get('summary', {}).get('transactions_processed', 0)} transactions processed")
                    
                    # Assign persona and create profile
                    if PERSONA_SERVICE_AVAILABLE:
                        print("  Assigning persona and creating profile...")
                        persona_service = PersonaAssignmentService(db_session=db)
                        
                        # Generate signals first (assign_persona will do this, but we need them for profile)
                        from app.features.subscriptions import SubscriptionDetector
                        from app.features.savings import SavingsDetector
                        from app.features.credit import CreditUtilizationDetector
                        from app.features.income import IncomeStabilityDetector
                        
                        subscription_detector = SubscriptionDetector(db_session=db)
                        savings_detector = SavingsDetector(db_session=db)
                        credit_detector = CreditUtilizationDetector(db_session=db)
                        income_detector = IncomeStabilityDetector(db_session=db)
                        
                        subscription_signals = subscription_detector.generate_subscription_signals(user.user_id)
                        savings_signals = savings_detector.generate_savings_signals(user.user_id)
                        credit_signals = credit_detector.generate_credit_signals(user.user_id)
                        income_signals = income_detector.generate_income_signals(user.user_id)
                        
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
                        
                        # Create or update UserProfile with signals
                        profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()
                        if not profile:
                            profile = UserProfile(
                                user_id=user.user_id,
                                signals_30d=signals_30d,
                                signals_180d=signals_180d,
                            )
                            db.add(profile)
                        else:
                            profile.signals_30d = signals_30d
                            profile.signals_180d = signals_180d
                        db.commit()
                        print("  ✓ Profile created/updated with signals")
                        
                        # Assign persona with pre-computed signals
                        persona_result = persona_service.assign_persona(
                            user.user_id,
                            signals_30d=signals_30d,
                            signals_180d=signals_180d,
                        )
                        
                        assigned_personas = persona_result.get('assigned_personas', [])
                        if assigned_personas:
                            from app.models.persona import PersonaId
                            persona_id = assigned_personas[0]  # Get first assigned persona
                            persona_name = persona_id.name if hasattr(persona_id, 'name') else str(persona_id)
                            print(f"  ✓ Persona assigned: {persona_name} (ID: {persona_id.value if hasattr(persona_id, 'value') else persona_id})")
                        else:
                            print("  ⚠ No persona assigned")
                            error_count += 1
                            continue
                        
                        # Generate recommendations
                        if RECOMMENDATION_SERVICE_AVAILABLE:
                            print("  Generating recommendations...")
                            generator = RecommendationGenerator(db_session=db, use_openai=True)
                            result = generator.generate_recommendations(user.user_id)
                            
                            if result.get("error"):
                                print(f"  ✗ Error: {result.get('error')}")
                                error_count += 1
                            else:
                                rec_count = len(result.get("recommendations", []))
                                edu_count = result.get("education_count", 0)
                                offer_count = result.get("partner_offer_count", 0)
                                print(f"  ✓ Generated {rec_count} recommendations ({edu_count} education, {offer_count} partner offers)")
                                success_count += 1
                        else:
                            print("  ⚠ Cannot generate recommendations - service not available")
                    else:
                        print("  ⚠ Cannot assign persona - service not available")
                else:
                    # Update upload status to failed
                    data_upload.status = UploadStatus.FAILED.value.lower()
                    data_upload.validation_errors = report.get("errors", [])
                    db.commit()
                    print(f"  ✗ Upload failed: {report.get('status')}")
                    error_count += 1
                    
            except Exception as e:
                print(f"  ✗ Error processing {user.email}: {e}")
                import traceback
                traceback.print_exc()
                db.rollback()
                error_count += 1
        
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Success: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Total: {len(users)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Upload test data and generate recommendations")
    parser.add_argument("--users", type=int, default=5, help="Number of users to process (default: 5)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("UPLOADING TEST DATA AND GENERATING RECOMMENDATIONS")
    print("=" * 60)
    upload_data_and_generate_recommendations(user_count=args.users)

