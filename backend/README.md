# SpendSense Backend

FastAPI backend service for the SpendSense platform.

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.11.7
- **Database**: PostgreSQL 16.10 (AWS RDS) / 15.6+ (local development) - SQLAlchemy 2.0.23
- **Cache**: Redis 7.1 (AWS ElastiCache) / 7.2.4+ (local development)
- **Migrations**: Alembic 1.13.0

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   │   ├── v1/
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   ├── users.py     # User management endpoints
│   │   │   └── ...
│   ├── core/                # Core functionality
│   │   ├── security.py      # JWT, password hashing
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── ...
│   └── services/            # Business logic
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup

### Prerequisites

- Python 3.11.7 or later
- PostgreSQL 15.6+ (local development) - Note: AWS RDS uses PostgreSQL 16.10 (adjusted for us-west-1 availability)
- Redis 7.1+ (local development) - Note: AWS ElastiCache uses Redis 7.1 (adjusted for us-west-1 availability)

### Installation Steps

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database:
   - See [DATABASE_SETUP.md](./DATABASE_SETUP.md) for detailed instructions
   - Create database and user:
     ```sql
     CREATE DATABASE spendsense_db;
     CREATE USER spendsense_user WITH PASSWORD 'spendsense_password';
     GRANT ALL PRIVILEGES ON DATABASE spendsense_db TO spendsense_user;
     ```

4. Set up environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```
   
   **Note on JWT Keys for Local Development:**
   - If you don't provide `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY` in your `.env` file, 
     the system will automatically generate RSA keys for development when `ENVIRONMENT=development`.
   - Generated keys are saved to `.dev_keys/` directory (created automatically) for persistence across server restarts.
   - These keys are git-ignored and should never be committed.
   - For production, you must provide keys via environment variables or AWS Secrets Manager.
   - To manually generate keys, run: `python scripts/generate_rsa_keys.py`

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Run development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest
pytest --cov=app tests/  # With coverage
```

### SMS Testing (Local with AWS SNS Sandbox)

To test SMS functionality locally using AWS SNS sandbox mode, see [SMS_TESTING.md](./SMS_TESTING.md) for detailed instructions.

**Quick Start:**
1. Verify your phone number in AWS SNS Console (Text messaging → Sandbox)
2. Configure AWS credentials in `.env` file
3. Start Redis server
4. Request verification code: `POST /api/v1/auth/phone/request`
5. Verify code: `POST /api/v1/auth/phone/verify`

### OAuth Testing

OAuth integration is implemented for Google, GitHub, Facebook, and Apple Sign In. See [OAUTH_SETUP.md](./OAUTH_SETUP.md) for setup instructions and [TEST_OAUTH.md](./TEST_OAUTH.md) for testing guide.

**Quick Start:**
1. Configure OAuth credentials in `.env` file (see `OAUTH_SETUP.md`)
2. Test authorize endpoint: `GET /api/v1/auth/oauth/{provider}/authorize?redirect_uri=http://localhost:3000/callback`
3. Open the `authorize_url` in browser to test full OAuth flow
4. Test callback endpoint: `GET /api/v1/auth/oauth/{provider}/callback?code=...&state=...`

**Account Linking:**
- Link additional OAuth provider: `POST /api/v1/auth/oauth/link`
- Link phone number: `POST /api/v1/auth/phone/link`
- Unlink OAuth provider: `DELETE /api/v1/auth/oauth/unlink/{provider}`
- Unlink phone number: `DELETE /api/v1/auth/phone/unlink`

**Current Status:**
- ✅ Google OAuth: Configured and tested
- ✅ Account Linking: Fully implemented with account merging
- ⚠️ GitHub, Facebook, Apple: Structure ready, credentials needed

## Development Tasks

See [PROJECT-PLAN.md](../docs/PROJECT-PLAN.md) for detailed task breakdown.

- **Task 1.2**: Database Design & Setup ✅ (Complete)
- **Task 2.1**: Authentication Foundation ✅ (Complete)
- **Task 2.2**: Email/Password Authentication ✅ (Complete)
- **Task 2.3**: Phone/SMS Authentication ✅ (Complete)
- **Task 2.4**: OAuth Integration ✅ (Complete)
  - Google OAuth: Configured and tested
  - GitHub, Facebook, Apple: Structure ready, credentials needed
- **Task 2.5**: Account Linking ✅ (Complete)
  - OAuth provider linking and unlinking
  - Phone number linking and unlinking
  - Account merging logic for duplicate accounts
- **Task 3.1**: User Management API
- And more...


