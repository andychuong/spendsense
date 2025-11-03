# Database Setup Guide

This guide explains how to set up the PostgreSQL database for local development.

## Prerequisites

- PostgreSQL 15.6+ installed (local development) - Note: AWS RDS uses PostgreSQL 16.10 (adjusted for us-west-1 availability)
- Python 3.11.7 or later
- Virtual environment activated

## Setup Steps

### 1. Install PostgreSQL

If you haven't already, install PostgreSQL:

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Note:** After installing PostgreSQL via Homebrew, you may need to add it to your PATH. Add this to your `~/.zshrc` (or `~/.bash_profile` for bash):
```bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

Then reload your shell:
```bash
source ~/.zshrc
```

Alternatively, you can use the full path:
```bash
/opt/homebrew/opt/postgresql@15/bin/psql postgres
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql-15
sudo systemctl start postgresql
```

**Windows:**
Download and install from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

### 2. Create Database and User

Connect to PostgreSQL:
```bash
psql postgres
```

Create database and user:
```sql
-- Create database
CREATE DATABASE spendsense_db;

-- Create user
CREATE USER spendsense_user WITH PASSWORD 'spendsense_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE spendsense_db TO spendsense_user;

-- Connect to the database
\c spendsense_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO spendsense_user;
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` and set your database URL:
```bash
DATABASE_URL=postgresql://spendsense_user:spendsense_password@localhost:5432/spendsense_db
```

### 5. Run Database Migrations

```bash
# Initialize Alembic (already done)
# alembic init alembic

# Create initial migration (already done)
# alembic revision --autogenerate -m "Initial database schema"

# Apply migrations
alembic upgrade head
```

### 6. Verify Database Setup

You can verify the tables were created:
```bash
psql -U spendsense_user -d spendsense_db -c "\dt"
```

You should see the following tables:
- users
- sessions
- data_uploads
- recommendations
- user_profiles
- persona_history

## Common Commands

### Create a new migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

### Check current migration version
```bash
alembic current
```

## Troubleshooting

### Connection refused
- Ensure PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
- Check that the database URL in `.env` is correct
- Verify PostgreSQL is listening on the correct port (default: 5432)

### Migration errors
- Ensure you're using the correct database URL
- Check that all dependencies are installed
- Verify the database user has proper permissions

### Enum type errors
If you encounter enum type errors when running migrations, you may need to manually drop and recreate enum types:
```sql
DROP TYPE IF EXISTS userrole CASCADE;
DROP TYPE IF EXISTS filetype CASCADE;
DROP TYPE IF EXISTS uploadstatus CASCADE;
DROP TYPE IF EXISTS recommendationtype CASCADE;
DROP TYPE IF EXISTS recommendationstatus CASCADE;
```

Then re-run migrations.

