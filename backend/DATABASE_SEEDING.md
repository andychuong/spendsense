# Database Seeding Guide

## Current Status

**The database is NOT automatically seeded** - it starts empty after migrations.

## When Database Gets Seeded

### 1. **Schema Creation** (Automatic)
```bash
alembic upgrade head
```
- Creates all tables (users, sessions, accounts, transactions, etc.)
- **Does NOT insert any data**
- Tables are empty after migrations

### 2. **Manual Seeding** (Manual - You need to do this)

#### Option A: Use the Seeding Script (Recommended for Development)

```bash
# From backend directory
cd backend
python scripts/seed_db.py --users 5
```

This creates:
- 5 regular test users (`user1@test.com` through `user5@test.com`)
- 1 operator user (`operator@test.com`)
- 1 admin user (`admin@test.com`)
- Password for all: `TestPassword123!`

**With synthetic data:**
```bash
# First generate synthetic data (if not already done)
python scripts/synthetic_data_generator.py scripts/persona_configs/ docs/support/transactions_100_users_2024.csv --output-dir synthetic_data --format json

# Then seed database with users + data
python backend/scripts/seed_db.py --users 5 --with-data
```

#### Option B: Manual User Registration

Use the API:
```bash
# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "consent": true
  }'
```

#### Option C: Data Upload

After registering/login, upload data:
```bash
# Upload Plaid data
curl -X POST http://localhost:8000/api/v1/data/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@path/to/data.json"
```

## Database Setup Flow

```
1. Create database + user (manual, one-time)
   ↓
2. Run migrations: alembic upgrade head
   ↓
3. [Database schema created, but EMPTY]
   ↓
4. Seed database (optional): python backend/scripts/seed_db.py
   ↓
5. [Database now has test users]
   ↓
6. Upload data or use API to add more users/data
```

## What Gets Seeded

### Users Table
- Test users with email/password
- Operator user for testing operator endpoints
- Admin user for testing admin endpoints

### Optional: Transaction Data
- Accounts (checking, savings, credit cards)
- Transactions (payroll, purchases, subscriptions)
- Liabilities (credit card balances, loans)

## Testing Recommendation Generation

After seeding:

1. **Users exist** → Can login
2. **Data uploaded** → Can generate signals
3. **Persona assigned** → Can generate recommendations

```python
# Example workflow after seeding
from backend.app.database import SessionLocal
from app.features.persona_assignment import PersonaAssignmentService
from app.recommendations.generator import RecommendationGenerator

db = SessionLocal()

# 1. Assign persona (if not already assigned)
persona_service = PersonaAssignmentService(db)
persona_service.assign_persona(user_id)

# 2. Generate recommendations
recommendation_service = RecommendationGenerator(db)
recommendation_service.generate_recommendations(user_id)
```

## Files Created

- `backend/scripts/seed_db.py` - Database seeding script

## Notes

- **Production**: Database should NOT be seeded with test data
- **Development**: Use seeding script for local testing
- **CI/CD**: Use fixtures in `conftest.py` for automated tests
- **Migration**: Seeding happens AFTER migrations, not during

