# Testing Data Guide - How to Get Data for Testing

## Current Situation

**Yes! The synthetic data generator creates files that match exactly what users upload in Step 4.**

## Format Compatibility

### Synthetic Data Generator Output

The generator creates JSON files with this structure:
```json
{
  "user_id": "uuid",
  "accounts": [...],
  "transactions": [...],
  "liabilities": [...]
}
```

### Upload Endpoint Expected Format

The upload endpoint (`POST /api/v1/data/upload`) expects:
- **JSON format**: File with `accounts`, `transactions`, `liabilities` arrays
- **CSV format**: Separate CSV files for accounts, transactions, liabilities

**✅ These formats match perfectly!**

## How to Get Test Data Right Now

### Option 1: Use Existing Synthetic Data Files

You already have synthetic data files in `synthetic_data/` directory:
```bash
# List available files
ls synthetic_data/*.json

# Example: Upload one file via API
curl -X POST http://localhost:8000/api/v1/data/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@synthetic_data/01bee6d9-95e8-477d-a4ec-54d2ae440e89.json"
```

### Option 2: Generate New Synthetic Data

```bash
# Generate fresh synthetic data
python scripts/synthetic_data_generator.py \
  scripts/persona_configs/ \
  docs/support/transactions_100_users_2024.csv \
  --output-dir synthetic_data \
  --format json

# This creates files like:
# synthetic_data/uuid-001.json
# synthetic_data/uuid-002.json
# ... (100 files total, 20 per persona)
```

### Option 3: Use the Seeding Script (Automated)

The seeding script I created can automatically:
1. Create test users
2. Load synthetic data files into database

```bash
# First generate synthetic data (if not already done)
python scripts/synthetic_data_generator.py \
  scripts/persona_configs/ \
  docs/support/transactions_100_users_2024.csv \
  --output-dir synthetic_data \
  --format json

# Then seed database with users + data
python backend/scripts/seed_db.py --users 5 --with-data
```

This will:
- Create 5 test users
- Load synthetic data files for those users
- Store everything in the database automatically

## Complete Testing Workflow

### Step-by-Step for Testing

1. **Generate Synthetic Data** (if not already done):
   ```bash
   python scripts/synthetic_data_generator.py \
     scripts/persona_configs/ \
     docs/support/transactions_100_users_2024.csv \
     --output-dir synthetic_data \
     --format json
   ```

2. **Seed Database** (optional, for automated testing):
   ```bash
   python backend/scripts/seed_db.py --users 5 --with-data
   ```

3. **Or Upload Manually via API**:
   ```bash
   # Login first to get token
   TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"user1@test.com","password":"TestPassword123!"}' \
     | jq -r '.access_token')

   # Upload a file
   curl -X POST http://localhost:8000/api/v1/data/upload \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@synthetic_data/01bee6d9-95e8-477d-a4ec-54d2ae440e89.json"
   ```

4. **Or Use Ingestion Service Directly** (programmatic):
   ```python
   from backend.app.database import SessionLocal
   from service.app.ingestion.service import IngestionService
   import uuid

   db = SessionLocal()
   ingestion_service = IngestionService(db)

   # Use an existing user_id or create one
   user_id = uuid.UUID("...")

   # Load and ingest JSON file
   with open("synthetic_data/01bee6d9-95e8-477d-a4ec-54d2ae440e89.json", "rb") as f:
       result = ingestion_service.ingest(
           file_content=f.read(),
           file_type="json",
           user_id=user_id,
       )
   ```

## File Format Verification

### Generated JSON Structure

Each generated JSON file contains:
```json
{
  "user_id": "01bee6d9-95e8-477d-a4ec-54d2ae440e89",
  "accounts": [
    {
      "account_id": "acct-uuid",
      "name": "Bank Name Checking",
      "type": "depository",
      "subtype": "checking",
      "holder_category": "individual",
      "balances": {
        "available": 1000.00,
        "current": 1000.00,
        "limit": null
      },
      "iso_currency_code": "USD",
      "mask": "1234"
    }
  ],
  "transactions": [
    {
      "transaction_id": "txn-uuid",
      "account_id": "acct-uuid",
      "date": "2024-01-15",
      "amount": -50.00,
      "merchant_name": "Store Name",
      "payment_channel": "online",
      "personal_finance_category": {
        "primary": "GENERAL_MERCHANDISE",
        "detailed": "GENERAL_MERCHANDISE_ONLINE"
      },
      "pending": false,
      "iso_currency_code": "USD"
    }
  ],
  "liabilities": [
    {
      "account_id": "acct-uuid",
      "aprs": [{
        "apr_percentage": 18.5,
        "apr_type": "purchase_apr"
      }],
      "is_overdue": false,
      "minimum_payment_amount": 25.00,
      ...
    }
  ]
}
```

### Parser Expected Format

The parser expects:
- Top-level keys: `accounts`, `transactions`, `liabilities` (optional)
- `accounts`: Array of account objects
- `transactions`: Array of transaction objects
- `liabilities`: Array of liability objects (optional)

**✅ Perfect match!**

## Summary

1. **Yes, synthetic data generator creates upload-ready files**
2. **Format matches exactly what upload endpoint expects**
3. **You have 100+ files ready to use in `synthetic_data/`**
4. **Use seeding script for automated testing**
5. **Or upload manually via API for manual testing**

## Quick Test Command

```bash
# Test with a single file
python backend/scripts/seed_db.py --users 1 --with-data --data-dir synthetic_data
```

This will:
- Create 1 test user
- Load the first synthetic data file
- Process it through the entire pipeline
- Store in database

You can then:
- View persona assignment
- Generate recommendations
- Test the full workflow!


