#!/usr/bin/env python3
"""Script to assign personas to users who have data but no persona assigned.

This script:
1. Finds all users with transaction data but no UserProfile
2. Assigns personas using PersonaAssignmentService
3. Uses OpenAI integration for enhanced rationales if available

Usage:
    # Activate virtual environment first:
    source backend/venv/bin/activate  # or: . backend/venv/bin/activate

    # Then run:
    python backend/scripts/assign_personas.py [--dry-run]

    # Or from backend directory:
    cd backend
    source venv/bin/activate
    python scripts/assign_personas.py [--dry-run]

Options:
    --dry-run    Show what would be done without making changes
"""

import sys
import os
import argparse
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
from app.models.transaction import Transaction

# Check if sqlalchemy is available
try:
    from sqlalchemy.orm import Session
except ImportError:
    print("=" * 60)
    print("ERROR: Missing dependencies")
    print("=" * 60)
    print("Please activate the virtual environment first:")
    print("  source backend/venv/bin/activate")
    print("  # or")
    print("  . backend/venv/bin/activate")
    print("")
    print("Then run the script again.")
    sys.exit(1)

# Try to import PersonaAssignmentService
try:
    from app.features.persona_assignment import PersonaAssignmentService
    PERSONA_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Failed to import PersonaAssignmentService: {e}")
    PERSONA_SERVICE_AVAILABLE = False


def find_users_without_personas(db: Session) -> list:
    """
    Find users who have transaction data but no UserProfile.

    Args:
        db: Database session

    Returns:
        List of User objects
    """
    # Get all users
    all_users = db.query(User).all()

    users_needing_personas = []

    for user in all_users:
        # Check if user has a profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()

        if profile:
            continue  # User already has a profile

        # Check if user has transaction data
        transaction_count = db.query(Transaction).filter(
            Transaction.user_id == user.user_id
        ).count()

        if transaction_count > 0:
            users_needing_personas.append(user)

    return users_needing_personas


def assign_personas_to_users(db: Session, users: list, dry_run: bool = False) -> dict:
    """
    Assign personas to users.

    Args:
        db: Database session
        users: List of User objects
        dry_run: If True, don't make changes

    Returns:
        Dictionary with results
    """
    if not PERSONA_SERVICE_AVAILABLE:
        return {
            "success": False,
            "error": "PersonaAssignmentService not available",
            "assigned": 0,
            "failed": 0,
        }

    persona_service = PersonaAssignmentService(db_session=db)

    results = {
        "assigned": 0,
        "failed": 0,
        "errors": [],
    }

    for user in users:
        if dry_run:
            print(f"  [DRY RUN] Would assign persona to user {user.user_id} ({user.email or 'no email'})")
            continue

        try:
            print(f"  Assigning persona to user {user.user_id} ({user.email or 'no email'})...")
            result = persona_service.assign_persona(user.user_id)

            persona_name = result.get("persona_name", "Unknown")
            persona_id = result.get("persona_id", "Unknown")

            print(f"    ✓ Assigned: {persona_name} (ID: {persona_id})")
            if result.get("persona_changed"):
                print(f"    ✓ Persona changed: {result.get('persona_changed')}")

            results["assigned"] += 1

        except Exception as e:
            error_msg = f"Failed to assign persona to user {user.user_id}: {str(e)}"
            print(f"    ✗ {error_msg}")
            results["failed"] += 1
            results["errors"].append(error_msg)
            # Rollback the transaction on error
            db.rollback()

    results["success"] = True
    return results


def main():
    parser = argparse.ArgumentParser(description="Assign personas to users with data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")

    args = parser.parse_args()

    print("=" * 60)
    print("PERSONA ASSIGNMENT SCRIPT")
    print("=" * 60)

    if args.dry_run:
        print("\n⚠ DRY RUN MODE - No changes will be made\n")

    if not PERSONA_SERVICE_AVAILABLE:
        print("✗ PersonaAssignmentService not available. Cannot assign personas.")
        print("  Make sure the service layer is properly installed and configured.")
        sys.exit(1)

    db = SessionLocal()

    try:
        # Find users without personas
        print("Finding users with data but no persona...")
        users_needing_personas = find_users_without_personas(db)

        if not users_needing_personas:
            print("✓ All users with data already have personas assigned.")
            return

        print(f"Found {len(users_needing_personas)} users needing personas:")
        for user in users_needing_personas:
            transaction_count = db.query(Transaction).filter(
                Transaction.user_id == user.user_id
            ).count()
            print(f"  - {user.email or 'no email'} (ID: {user.user_id}, {transaction_count} transactions)")

        print(f"\n{'[DRY RUN] Would assign' if args.dry_run else 'Assigning'} personas...")
        results = assign_personas_to_users(db, users_needing_personas, dry_run=args.dry_run)

        if not args.dry_run:
            print("\n" + "=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(f"  Assigned: {results['assigned']}")
            print(f"  Failed: {results['failed']}")

            if results["errors"]:
                print("\nErrors:")
                for error in results["errors"]:
                    print(f"  - {error}")

        print("\n" + "=" * 60)
        print("✅ Persona assignment complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()

