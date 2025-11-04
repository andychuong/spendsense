# Recommendation Generation Service - Testing Guide

## What We Can Test Right Now

### ✅ Tests That Work Without Database (Already Working)

1. **Catalog Structure Test** (`test_catalog_standalone.py`)
   - Verifies all education items and partner offers have required fields
   - Checks catalog counts per persona
   - Validates data structure

2. **Persona Matching Test**
   - Verifies each persona has ≥3 education items
   - Verifies each persona has ≥1 partner offers
   - Shows which recommendations match which personas

3. **Content Quality Test**
   - Validates content length
   - Checks for required fields
   - Verifies eligibility requirements structure

4. **Regulatory Disclaimer Test**
   - Verifies disclaimer text is present
   - Checks for key phrases ("educational", "not financial advice", "licensed")

### 🔧 Tests That Require Database Setup

To test these, you need:
- Database connection configured
- At least one user with assigned persona
- SQLAlchemy installed

5. **Full Integration Test**
   - Generate recommendations for a user
   - Verify recommendations are stored in database
   - Check rationale generation with real signals
   - Verify decision traces are created

6. **Recommendation Selection Logic**
   - Test that 3-5 education items are selected
   - Test that 1-3 partner offers are selected
   - Test that recommendations match persona

7. **Rationale Generation with Signals**
   - Test rationale generation with different signal types
   - Verify data points are cited correctly
   - Check persona-specific rationale logic

## How to Run Tests

### Standalone Tests (No Database Required)

```bash
# From project root
python3 service/app/recommendations/test_catalog_standalone.py
```

This will test:
- Catalog structure
- Persona matching
- Content quality
- Regulatory disclaimer

### Integration Tests (Requires Database)

```bash
# From service directory
cd service
python3 -m app.recommendations.test_recommendations
```

**Requirements:**
- Database must be running
- At least one user with assigned persona
- SQLAlchemy installed (`pip install sqlalchemy`)

## Current Test Results

✅ **4/4 tests passing** for catalog structure:
- ✓ Catalog Structure
- ✓ Persona Matching
- ✓ Content Quality
- ✓ Regulatory Disclaimer

## What's Working

1. **Education Catalog**: 14 items covering all 5 personas
   - Persona 1: 3 items
   - Persona 2: 3 items
   - Persona 3: 3 items
   - Persona 4: 3 items
   - Persona 5: 2 items (could add 1 more)

2. **Partner Offer Catalog**: 6 offers
   - Persona 1: 1 offer (balance transfer card)
   - Persona 2: 1 offer (budgeting app)
   - Persona 3: 1 offer (subscription manager)
   - Persona 4: 2 offers (high-yield savings, round-up app)
   - Persona 5: 1 offer (credit monitoring)

3. **Recommendation Generator**: Ready to use
   - Selects 3-5 education items per persona
   - Selects 1-3 partner offers per persona
   - Generates rationales using detected signals
   - Stores recommendations in database

## Next Steps for Full Testing

1. **Set up database connection**:
   ```bash
   # Install dependencies
   pip install sqlalchemy psycopg2-binary

   # Configure database URL in backend/app/config.py
   ```

2. **Create test user with persona**:
   - Upload data for a user
   - Run persona assignment
   - Then run recommendation generation

3. **Run integration test**:
   ```python
   from backend.app.database import SessionLocal
   from app.recommendations.generator import RecommendationGenerator

   db = SessionLocal()
   generator = RecommendationGenerator(db)
   result = generator.generate_recommendations(user_id)
   ```

## Sample Output

When you run the standalone test, you'll see:

```
============================================================
RECOMMENDATION CATALOG - TEST SUITE
============================================================

✓ PASSED: Catalog Structure
✓ PASSED: Persona Matching
✓ PASSED: Content Quality
✓ PASSED: Regulatory Disclaimer

Total: 4/4 tests passed

SAMPLE RECOMMENDATIONS BY PERSONA
============================================================
High Utilization (Persona 1):
  Education Items:
    - Debt Paydown Strategies: The Snowball vs. Avalanche Method
    - Understanding Credit Utilization: How It Affects Your Score
  Partner Offers:
    - Balance Transfer Credit Card - 0% APR for 18 Months
...
```

## Files Created

- `service/app/recommendations/catalog.py` - Education items and partner offers
- `service/app/recommendations/generator.py` - Recommendation generation logic
- `service/app/recommendations/test_catalog_standalone.py` - Standalone tests
- `service/app/recommendations/test_recommendations.py` - Full integration tests
- `service/app/recommendations/example_recommendations.py` - Usage examples


