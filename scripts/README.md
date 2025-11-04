# SpendSense Scripts

Utility scripts for development, testing, and deployment.

## Scripts

### Development Scripts
- `setup-dev.sh` - Set up development environment
- `run-tests.sh` - Run all tests
- `lint.sh` - Run linters

### Database Scripts
- `migrate-db.sh` - Run database migrations
- `seed-db.sh` - Seed database with test data
- `reset-db.sh` - Reset database (development only)

### Deployment Scripts
- `deploy-staging.sh` - Deploy to staging
- `deploy-prod.sh` - Deploy to production
- `rollback.sh` - Rollback deployment

### Data Scripts

#### Synthetic Data Generator

**Location**: `scripts/synthetic_data_generator.py`

**Purpose**: Generates realistic synthetic Plaid-style financial data for testing and development. Creates diverse user profiles based on 5 predefined personas.

**Usage**:
```bash
# Generate data in JSON format
python scripts/synthetic_data_generator.py scripts/persona_configs/ docs/support/transactions_100_users_2024.csv --output-dir synthetic_data --format json

# Generate data in CSV format
python scripts/synthetic_data_generator.py scripts/persona_configs/ docs/support/transactions_100_users_2024.csv --output-dir synthetic_data --format csv

# Generate data in both formats
python scripts/synthetic_data_generator.py scripts/persona_configs/ docs/support/transactions_100_users_2024.csv --output-dir synthetic_data --format both
```

**Arguments**:
- `config_dir` (required): Directory containing persona YAML configuration files
- `transactions_csv` (required): Path to CSV file with sample transactions for realistic merchant data
- `--output-dir` (optional): Directory to save generated data (default: `synthetic_data`)
- `--format` (optional): Output format - `json`, `csv`, or `both` (default: `json`)

**Persona Configurations**:
Located in `scripts/persona_configs/`:
- `1_high_utilization.yaml` - Users with high credit card utilization (≥50%, ≥80%)
- `2_variable_income.yaml` - Users with irregular income streams (freelancers, gig workers)
- `3_subscription_heavy.yaml` - Users with many recurring subscriptions
- `4_savings_builder.yaml` - Users consistently building savings
- `5_custom.yaml` - General/mixed profiles

**Output**:
- JSON format: One file per user (`{user_id}.json`) containing accounts, transactions, and liabilities
- CSV format: Separate files per user (`{user_id}_accounts.csv`, `{user_id}_transactions.csv`, `{user_id}_liabilities.csv`)

**Features**:
- Configuration-driven generation using YAML files
- Uses real merchant data from provided CSV for realistic transactions
- Validates all generated data against `PlaidValidator`
- Generates 100 diverse user profiles (20 per persona)
- All generated data passes validation (0 errors, 0 warnings)

**Dependencies**:
Install dependencies from `scripts/requirements.txt`:
```bash
pip install -r scripts/requirements.txt
```

**Requirements**:
- Python 3.9+
- Service package installed (`pip install -e service/`)
- Faker library for realistic data generation
- PyYAML for configuration parsing

**Example Output**:
```
synthetic_data/
├── user-001.json
├── user-002.json
├── ...
└── user-100.json
```

**Notes**:
- The generator uses the `PlaidValidator` from `service/app/common/validator.py` to validate all generated data
- Merchant pool is loaded from the provided CSV file to ensure realistic transaction data
- Each persona configuration defines account types, transaction patterns, and payment behaviors
- Generated data is suitable for testing feature engineering, persona assignment, and recommendation generation

- `export-data.py` - Export data for analysis

## Usage

See individual script documentation above for usage instructions.

For detailed task breakdown and project status, see [PROJECT-PLAN.md](../docs/PROJECT-PLAN.md).


