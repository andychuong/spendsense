#!/usr/bin/env python3
"""Database seeding script for development and testing.

This script seeds the database with test users and data for local development.

Usage:
    python backend/scripts/seed_db.py [--users N] [--with-data]
    
Options:
    --users N        Number of test users to create (default: 5)
    --with-data      Also seed with synthetic transaction data (requires synthetic_data directory)
"""

import sys
import os
import argparse
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Try to import ingestion service for data seeding
try:
    from app.ingestion.service import IngestionService
    INGESTION_AVAILABLE = True
except ImportError:
    INGESTION_AVAILABLE = False
    print("⚠ Ingestion service not available. Data seeding will be skipped.")


def create_test_user(db: Session, email: str, password: str = "TestPassword123!", role: UserRole = UserRole.USER, consent: bool = True) -> User:
    """Create a test user."""
    user = User(
        user_id=uuid.uuid4(),
        email=email,
        password_hash=get_password_hash(password),
        role=role.value,
        consent_status=consent,
        consent_version="1.0",
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_users(db: Session, count: int = 5):
    """Seed database with test users."""
    print(f"Creating {count} test users...")
    
    users = []
    
    # Create regular users
    for i in range(count):
        email = f"user{i+1}@test.com"
        user = create_test_user(db, email, consent=True)
        users.append(user)
        print(f"  ✓ Created user: {email} (ID: {user.user_id})")
    
    # Create an operator user
    operator = create_test_user(db, "operator@test.com", role=UserRole.OPERATOR, consent=True)
    print(f"  ✓ Created operator: operator@test.com (ID: {operator.user_id})")
    
    # Create an admin user
    admin = create_test_user(db, "admin@test.com", role=UserRole.ADMIN, consent=True)
    print(f"  ✓ Created admin: admin@test.com (ID: {admin.user_id})")
    
    return users


def seed_data_from_files(db: Session, users: list, synthetic_data_dir: str = "synthetic_data"):
    """Seed database with synthetic data files."""
    if not INGESTION_AVAILABLE:
        print("⚠ Ingestion service not available. Skipping data seeding.")
        return
    
    synthetic_path = Path(synthetic_data_dir)
    if not synthetic_path.exists():
        print(f"⚠ Synthetic data directory '{synthetic_data_dir}' not found.")
        print("  Generate synthetic data first:")
        print("  python scripts/synthetic_data_generator.py scripts/persona_configs/ docs/support/transactions_100_users_2024.csv --output-dir synthetic_data --format json")
        return
    
    print(f"Loading synthetic data from {synthetic_data_dir}...")
    
    ingestion_service = IngestionService(db)
    json_files = list(synthetic_path.glob("*.json"))
    
    if not json_files:
        print(f"  ⚠ No JSON files found in {synthetic_data_dir}")
        return
    
    print(f"  Found {len(json_files)} JSON files")
    
    # Load data for first few users
    loaded_count = 0
    for i, user in enumerate(users[:min(5, len(users))]):
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
                print(f"  ✓ Loaded data for {user.email} from {json_file.name}")
                loaded_count += 1
            else:
                print(f"  ✗ Failed to load data for {user.email}: {result.get('status')}")
        
        except Exception as e:
            print(f"  ✗ Error loading {json_file.name} for {user.email}: {e}")
    
    print(f"  Loaded data for {loaded_count} users")


def main():
    parser = argparse.ArgumentParser(description="Seed database with test data")
    parser.add_argument("--users", type=int, default=5, help="Number of test users to create (default: 5)")
    parser.add_argument("--with-data", action="store_true", help="Also seed with synthetic transaction data")
    parser.add_argument("--data-dir", default="synthetic_data", help="Directory containing synthetic data files (default: synthetic_data)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("DATABASE SEEDING")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Seed users
        users = seed_users(db, count=args.users)
        
        # Seed data if requested
        if args.with_data:
            seed_data_from_files(db, users, synthetic_data_dir=args.data_dir)
        
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE")
        print("=" * 60)
        print("\nTest users created:")
        print("  Regular users: user1@test.com through user{N}@test.com")
        print("  Password: TestPassword123!")
        print("  Operator: operator@test.com")
        print("  Admin: admin@test.com")
        print("\nYou can now:")
        print("  1. Login with any test user")
        print("  2. Upload data via /api/v1/data/upload")
        print("  3. Generate recommendations")
        
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

