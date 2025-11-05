#!/usr/bin/env python3
"""Database seeding script for development and testing.

This script seeds the database with test users and data for local development.

Usage:
    python backend/scripts/seed_db.py [--users N] [--users-per-persona N] [--with-data] [--clean] [--password PASSWORD]

Options:
    --users N              Total number of test users to create (default: 50, ignored if --users-per-persona is used)
    --users-per-persona N   Number of users per persona (personas 1-5). Default: 10 per persona = 50 total users.
                           This ensures balanced distribution across all personas.
    --with-data            Also seed with synthetic transaction data (requires synthetic_data directory)
    --clean                Clean up all existing user data before seeding
    --password             Password for all users (default: TestPassword123!)

Examples:
    # Create 50 users (10 per persona) with data
    python backend/scripts/seed_db.py --users-per-persona 10 --with-data
    
    # Create 100 users (20 per persona) with data
    python backend/scripts/seed_db.py --users-per-persona 20 --with-data
    
    # Create 50 users total, distributed evenly
    python backend/scripts/seed_db.py --users 50 --with-data
"""

import sys
import os
import argparse
import uuid
import random
from pathlib import Path
from faker import Faker

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add service to path for persona assignment
_project_root = os.path.dirname(backend_path)
_service_dir = os.path.join(_project_root, "service")
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.recommendation import Recommendation
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.liability import Liability
from app.models.data_upload import DataUpload
from app.models.user_profile import UserProfile
from app.models.persona_history import PersonaHistory
from app.models.session import Session as SessionModel
from app.models.persona import Persona
from app.core.security import get_password_hash

# Initialize Faker for generating names
faker = Faker()

# Try to import ingestion service for data seeding
try:
    from app.ingestion.service import IngestionService
    INGESTION_AVAILABLE = True
except ImportError:
    INGESTION_AVAILABLE = False
    print("⚠ Ingestion service not available. Data seeding will be skipped.")

# Try to import persona assignment service
try:
    from app.features.persona_assignment import PersonaAssignmentService
    PERSONA_SERVICE_AVAILABLE = True
except ImportError:
    PERSONA_SERVICE_AVAILABLE = False
    print("⚠ PersonaAssignmentService not available. Personas will not be assigned automatically.")


def cleanup_all_users(db: Session):
    """Clean up all user-related data from the database."""
    print("Cleaning up all existing user data...")
    
    # Count records before deletion
    users_count = db.query(User).count()
    recommendations_count = db.query(Recommendation).count()
    accounts_count = db.query(Account).count()
    transactions_count = db.query(Transaction).count()
    liabilities_count = db.query(Liability).count()
    data_uploads_count = db.query(DataUpload).count()
    user_profiles_count = db.query(UserProfile).count()
    persona_history_count = db.query(PersonaHistory).count()
    sessions_count = db.query(SessionModel).count()
    
    print(f"  Found {users_count} users, {recommendations_count} recommendations, {accounts_count} accounts, "
          f"{transactions_count} transactions, {liabilities_count} liabilities, "
          f"{data_uploads_count} data uploads, {user_profiles_count} user profiles, "
          f"{persona_history_count} persona history entries, {sessions_count} sessions")
    
    if users_count == 0:
        print("  No users found. Nothing to clean up.")
        return
    
    # Delete in order respecting foreign key constraints
    print("  Deleting recommendations...")
    db.execute(text("DELETE FROM recommendations"))
    
    print("  Deleting user persona assignments...")
    db.execute(text("DELETE FROM user_persona_assignments"))
    
    print("  Deleting liabilities...")
    db.execute(text("DELETE FROM liabilities"))
    
    print("  Deleting transactions...")
    db.execute(text("DELETE FROM transactions"))
    
    print("  Deleting accounts...")
    db.execute(text("DELETE FROM accounts"))
    
    print("  Deleting data uploads...")
    db.execute(text("DELETE FROM data_uploads"))
    
    print("  Deleting persona history...")
    db.execute(text("DELETE FROM persona_history"))
    
    print("  Deleting user profiles...")
    db.execute(text("DELETE FROM user_profiles"))
    
    print("  Deleting sessions...")
    db.execute(text("DELETE FROM sessions"))
    
    print("  Deleting users...")
    db.execute(text("DELETE FROM users"))
    
    db.commit()
    print("  ✓ All user data cleaned up successfully")


def create_test_user(db: Session, email: str, password: str = "TestPassword123!", role: UserRole = UserRole.USER, consent: bool = True, name: str = None, monthly_income: float = None) -> User:
    """Create a test user."""
    # Generate name if not provided
    if name is None:
        name = faker.name()

    user = User(
        user_id=uuid.uuid4(),
        name=name,
        email=email,
        password_hash=get_password_hash(password),
        role=role.value,
        consent_status=consent,
        consent_version="1.0",
        monthly_income=monthly_income,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_users(db: Session, count: int = 50, password: str = "TestPassword123!", users_per_persona: int = None):
    """Seed database with test users.
    
    Args:
        count: Total number of regular users to create. If users_per_persona is specified, this will be overridden.
        password: Password for all users
        users_per_persona: Number of users per persona (1-5). If specified, creates users_per_persona * 5 users.
    """
    # If users_per_persona is specified, calculate total count
    if users_per_persona is not None:
        count = users_per_persona * 5
    
    print(f"Creating {count} regular users plus 1 operator and 1 admin...")
    if users_per_persona:
        print(f"  ({users_per_persona} users per persona for personas 1-5)")

    users = []
    
    # Income ranges for different personas (monthly)
    income_ranges = {
        1: (3000, 5000),   # High Utilization - lower income
        2: (2000, 6000),   # Variable Income - wide range
        3: (4000, 6000),   # Subscription-Heavy - moderate to high
        4: (5000, 8000),   # Savings Builder - higher income
        5: (3500, 7000),   # Custom - wide range
    }

    # Create regular users with varied personas
    # Ensure balanced distribution: create users_per_persona for each persona
    persona_assignments = []
    user_counter = 0
    
    # If users_per_persona is specified, create balanced groups
    if users_per_persona:
        for persona_id in range(1, 6):  # Personas 1-5
            for j in range(users_per_persona):
                # Generate varied income based on persona
                income_min, income_max = income_ranges[persona_id]
                monthly_income = round(random.uniform(income_min, income_max), 2)
                
                email = f"user{user_counter+1}@test.com"
                user = create_test_user(db, email, password=password, consent=True, monthly_income=monthly_income)
                print(f"  ✓ Created user {user_counter+1}: {user.name} ({email}) - Target Persona {persona_id}, Income: ${monthly_income:,.2f}/month")
                users.append((user, persona_id))
                persona_assignments.append(persona_id)
                user_counter += 1
    else:
        # Fallback to round-robin distribution
        for i in range(count):
            persona_id = (i % 5) + 1
            persona_assignments.append(persona_id)
            
            # Generate varied income based on persona
            income_min, income_max = income_ranges[persona_id]
            monthly_income = round(random.uniform(income_min, income_max), 2)
            
            email = f"user{i+1}@test.com"
            user = create_test_user(db, email, password=password, consent=True, monthly_income=monthly_income)
            print(f"  ✓ Created user {i+1}: {user.name} ({email}) - Target Persona {persona_id}, Income: ${monthly_income:,.2f}/month")
            users.append((user, persona_id))
    
    # Print distribution summary
    from collections import Counter
    persona_dist = Counter(persona_assignments)
    print(f"\n  Target persona distribution:")
    for persona_id in sorted(persona_dist.keys()):
        print(f"    Persona {persona_id}: {persona_dist[persona_id]} users")

    # Create an operator user
    operator = create_test_user(db, "operator@test.com", password=password, role=UserRole.OPERATOR, consent=True)
    print(f"  ✓ Created operator: {operator.name} (operator@test.com)")

    # Create an admin user
    admin = create_test_user(db, "admin@test.com", password=password, role=UserRole.ADMIN, consent=True)
    print(f"  ✓ Created admin: {admin.name} (admin@test.com)")

    return users, operator, admin


def seed_data_from_files(db: Session, users_with_personas: list, synthetic_data_dir: str = "synthetic_data"):
    """Seed database with synthetic data files, matching personas."""
    if not INGESTION_AVAILABLE:
        print("⚠ Ingestion service not available. Skipping data seeding.")
        return []

    synthetic_path = Path(synthetic_data_dir)
    # If relative path doesn't exist, try from project root
    if not synthetic_path.exists():
        project_root = Path(__file__).parent.parent.parent
        synthetic_path = project_root / synthetic_data_dir

    if not synthetic_path.exists():
        print(f"⚠ Synthetic data directory '{synthetic_data_dir}' not found.")
        print(f"  Tried: {Path(synthetic_data_dir).absolute()}")
        print(f"  Tried: {(Path(__file__).parent.parent.parent / synthetic_data_dir).absolute()}")
        print("  Generate synthetic data first:")
        print("  python scripts/synthetic_data_generator.py scripts/persona_configs/ docs/support/transactions_100_users_2024.csv --output-dir synthetic_data --format json")
        return []

    print(f"Loading synthetic data from {synthetic_path.absolute()}...")

    ingestion_service = IngestionService(db)
    
    # Group JSON files by persona (assuming files are named with persona info or we can match them)
    json_files = list(synthetic_path.glob("*.json"))
    
    if not json_files:
        print(f"  ⚠ No JSON files found in {synthetic_data_dir}")
        return []

    print(f"  Found {len(json_files)} JSON files")
    
    # Shuffle files to get variety
    random.shuffle(json_files)
    
    # Load data for users, cycling through available files
    loaded_users = []
    loaded_count = 0
    
    for i, (user, persona_id) in enumerate(users_with_personas):
        json_file = json_files[i % len(json_files)]
        
        try:
            with open(json_file, 'rb') as f:
                file_content = f.read()

            result = ingestion_service.ingest(
                file_content=file_content,
                file_type="json",
                user_id=user.user_id,
            )

            if result.get("status") == "completed":
                print(f"  ✓ Loaded data for {user.email} (Persona {persona_id}) from {json_file.name}")
                loaded_users.append(user)
                loaded_count += 1
            else:
                print(f"  ✗ Failed to load data for {user.email}: {result.get('status')}")

        except Exception as e:
            print(f"  ✗ Error loading {json_file.name} for {user.email}: {e}")
            import traceback
            traceback.print_exc()

    print(f"  Loaded data for {loaded_count} users")
    return loaded_users


def assign_personas_to_users(db: Session, users: list):
    """Assign personas to users who have data."""
    if not PERSONA_SERVICE_AVAILABLE:
        print("⚠ PersonaAssignmentService not available. Skipping persona assignment.")
        return
    
    print("Assigning personas to users...")
    persona_service = PersonaAssignmentService(db_session=db)
    
    assigned_count = 0
    persona_summary = {}  # Track persona assignments
    
    for user in users:
        try:
            result = persona_service.assign_persona(user.user_id)
            # Handle both single persona and multiple personas format
            assigned_personas = result.get("assigned_personas", [])
            if not assigned_personas:
                # Fallback to old format
                persona_id = result.get("persona_id", "Unknown")
                assigned_personas = [persona_id] if persona_id != "Unknown" else []
            
            # Get persona names for display
            from app.models.persona import Persona
            persona_names = []
            for pid in assigned_personas:
                persona = db.query(Persona).filter(Persona.persona_id == pid).first()
                persona_names.append(persona.name if persona else f"Persona {pid}")
            persona_name = ", ".join(persona_names) if persona_names else "Unknown"
            
            # Track assignments (assigned_personas is a list of persona IDs)
            for pid in assigned_personas:
                persona_summary[pid] = persona_summary.get(pid, 0) + 1
            
            print(f"  ✓ Assigned {persona_name} to {user.email}")
            assigned_count += 1
        except Exception as e:
            print(f"  ✗ Failed to assign persona to {user.email}: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
    
    print(f"\n  Assigned personas to {assigned_count} users")
    print(f"\n  Final persona distribution:")
    from collections import Counter
    from app.models.persona import Persona
    
    # Get persona names for display
    persona_dist = Counter(persona_summary)
    for persona_id in sorted(persona_dist.keys()):
        persona = db.query(Persona).filter(Persona.persona_id == persona_id).first()
        persona_name = persona.name if persona else f"Persona {persona_id}"
        print(f"    {persona_name} (ID: {persona_id}): {persona_dist[persona_id]} users")


def seed_personas(db: Session):
    """Seed the personas table with predefined personas."""
    print("Seeding personas table...")
    
    personas = [
        {"persona_id": 1, "name": "High Utilization", "description": "Users with high credit utilization, carrying significant balances relative to their credit limits."},
        {"persona_id": 2, "name": "Variable Income Budgeter", "description": "Users with irregular or unpredictable income streams, such as freelancers or gig economy workers."},
        {"persona_id": 3, "name": "Subscription-Heavy", "description": "Users with a high number of recurring subscriptions, spending a significant amount on these services."},
        {"persona_id": 4, "name": "Savings Builder", "description": "Users who are consistently growing their savings and maintaining low credit utilization."},
        {"persona_id": 5, "name": "Balanced Spender", "description": "Users who do not fit a specific persona, exhibiting balanced and varied financial behaviors."},
        {"persona_id": 6, "name": "Debt Consolidator", "description": "Users with multiple credit cards/loans carrying balances who could benefit from consolidation strategies."},
        {"persona_id": 7, "name": "Emergency Fund Seeker", "description": "Users with low savings relative to expenses who need emergency fund guidance."},
        {"persona_id": 8, "name": "Foodie", "description": "Users who spend a significant portion of their income on dining out and food-related expenses."},
        {"persona_id": 9, "name": "Frequent Traveler", "description": "Users with significant spending on airlines, hotels, and other travel-related expenses."},
        {"persona_id": 10, "name": "Home Improver", "description": "Users who frequently shop at home improvement stores, furniture stores, or spend on home services."}
    ]
    
    for persona_data in personas:
        persona = db.query(Persona).filter(Persona.persona_id == persona_data["persona_id"]).first()
        if not persona:
            persona = Persona(**persona_data)
            db.add(persona)
            print(f"  ✓ Added persona: {persona.name}")
        else:
            persona.name = persona_data["name"]
            persona.description = persona_data["description"]
            print(f"  ✓ Updated persona: {persona.name}")
    
    db.commit()
    print("  ✓ Personas seeding complete")


def main():
    parser = argparse.ArgumentParser(description="Seed database with test data")
    parser.add_argument("--users", type=int, default=50, help="Number of regular test users to create (default: 50, total will be 52 with admin+operator)")
    parser.add_argument("--users-per-persona", type=int, default=None, help="Number of users per persona (personas 1-5). If specified, overrides --users. Example: --users-per-persona 10 creates 50 users (10 per persona)")
    parser.add_argument("--with-data", action="store_true", help="Also seed with synthetic transaction data")
    parser.add_argument("--data-dir", default="synthetic_data", help="Directory containing synthetic data files (default: synthetic_data)")
    parser.add_argument("--clean", action="store_true", help="Clean up all existing user data before seeding")
    parser.add_argument("--password", default="TestPassword123!", help="Password for all users (default: TestPassword123!)")

    args = parser.parse_args()
    
    # Use users_per_persona if specified, otherwise default to 10 per persona
    # This ensures balanced distribution across personas
    users_per_persona = args.users_per_persona if args.users_per_persona is not None else 10

    print("=" * 60)
    print("DATABASE SEEDING")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Clean up existing data if requested
        if args.clean:
            cleanup_all_users(db)
            print()

        # Seed personas
        seed_personas(db)
        print()

        # Seed users
        users_with_personas, operator, admin = seed_users(db, count=args.users, password=args.password, users_per_persona=users_per_persona)

        # Seed data if requested
        users_with_data = []
        if args.with_data:
            print()
            users_with_data = seed_data_from_files(db, users_with_personas, synthetic_data_dir=args.data_dir)
            
            # Assign personas to users who have data
            if users_with_data and PERSONA_SERVICE_AVAILABLE:
                print()
                assign_personas_to_users(db, users_with_data)

        print("\n" + "=" * 60)
        print("SEEDING COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()

