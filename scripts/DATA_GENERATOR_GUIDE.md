# Synthetic Data Generator - How It Works

## Current Behavior

**The synthetic data generator does NOT add data to the database** - it only creates files.

## Workflow

```
1. Generate synthetic data (in memory)
   ↓
2. Validate data (using PlaidValidator)
   ↓
3. Export to files (JSON/CSV)
   ↓
4. [Data is in files, NOT in database]
   ↓
5. Upload files via API (to get into database)
```

## Current Usage

```bash
# Step 1: Generate files
python scripts/synthetic_data_generator.py \
  scripts/persona_configs/ \
  docs/support/transactions_100_users_2024.csv \
  --output-dir synthetic_data \
  --format json

# Step 2: Upload files to database (manual)
# Use the data upload API endpoint:
POST /api/v1/data/upload
# Upload each JSON file for each user
```

## Two-Step Process

### Step 1: Generate Files
The generator creates:
- `synthetic_data/user-001.json`
- `synthetic_data/user-002.json`
- ... (100 files total)

### Step 2: Load into Database
You need to upload each file separately via the API or use the ingestion service directly.

## Why This Design?

1. **Separation of Concerns**: Generation vs. Storage
2. **Flexibility**: Can use files for testing without database
3. **Validation**: Files can be validated before committing to DB
4. **Reusability**: Files can be uploaded multiple times

## How to Get Data Into Database

### Option 1: Manual Upload via API (Current)

```python
# After generating files
import requests

for json_file in glob.glob("synthetic_data/*.json"):
    with open(json_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            'http://localhost:8000/api/v1/data/upload',
            headers={'Authorization': f'Bearer {token}'},
            files=files
        )
```

### Option 2: Use Ingestion Service Directly (Recommended)

```python
from backend.app.database import SessionLocal
from service.app.ingestion.service import IngestionService
import json

db = SessionLocal()
ingestion_service = IngestionService(db)

# Load a user first (or create one)
user_id = uuid.UUID("...")

# Load and ingest JSON file
with open("synthetic_data/user-001.json", "rb") as f:
    result = ingestion_service.ingest(
        file_content=f.read(),
        file_type="json",
        user_id=user_id,
    )
```

### Option 3: Use the Seeding Script

The `seed_db.py` script I created can load files automatically:

```bash
python backend/scripts/seed_db.py --users 5 --with-data
```

This will:
1. Create test users
2. Load synthetic data files for those users
3. Store everything in the database

## File Structure

Each generated JSON file contains:
```json
{
  "user_id": "uuid",
  "accounts": [...],
  "transactions": [...],
  "liabilities": [...]
}
```

This matches the Plaid format expected by the ingestion service.

## Summary

- **Generator**: Creates files only (JSON/CSV)
- **Database**: Empty until you upload files
- **Upload**: Use API endpoint or ingestion service
- **Recommended**: Use `seed_db.py` script for easy setup



