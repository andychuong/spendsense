# SpendSense Memory Bank
## Project Knowledge Base & Progress Tracker

**Last Updated**: 2025-11-04  
**Version**: 1.18  
**Status**: Phase 2 - Task 4.3 Complete (Synthetic Data Generator)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Completed Tasks](#completed-tasks)
4. [Architecture & Design Decisions](#architecture--design-decisions)
5. [Database Schema](#database-schema)
6. [Authentication & Authorization](#authentication--authorization)
7. [API Endpoints](#api-endpoints)
8. [Frontend Components](#frontend-components)
9. [Infrastructure](#infrastructure)
10. [Configuration & Environment](#configuration--environment)
11. [Key Files & Locations](#key-files--locations)
12. [Next Steps](#next-steps)

---

## Project Overview

**SpendSense** is a financial wellness platform that analyzes user transaction data to provide personalized financial recommendations. The platform uses behavioral signals (subscriptions, savings patterns, credit utilization, income stability) to assign personas and generate tailored recommendations.

### Project Structure
```
SpendSense/
├── backend/          # FastAPI backend service
├── frontend/         # React TypeScript frontend
├── service/          # Data processing service layer
│   └── app/
│       ├── ingestion/  # Data ingestion services (Task 4.1)
│       └── common/     # Shared utilities (validator moved here)
├── infrastructure/   # Terraform AWS infrastructure
├── docs/            # Documentation
├── scripts/         # Utility scripts
│   ├── synthetic_data_generator.py  # Synthetic data generator (Task 4.3)
│   └── persona_configs/             # Persona YAML configurations
└── synthetic_data/  # Generated synthetic user profiles (100 JSON files)
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.11.7
- **Database**: PostgreSQL 16.10 (AWS RDS) / 15.6+ (local)
- **ORM**: SQLAlchemy 2.0.23
- **Cache**: Redis 7.1 (AWS ElastiCache) / 7.2.4+ (local)
- **Migrations**: Alembic 1.13.0
- **Authentication**: JWT (RS256), bcrypt (cost factor 12)
- **SMS**: AWS SNS
- **OAuth**: Google, GitHub, Facebook, Apple (configured)

### Service Layer
- **Language**: Python 3.11.7
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.3
- **Storage**: PyArrow 15.0.0 (Parquet support)
- **Database**: PostgreSQL 16.10 (via SQLAlchemy models)
- **File Storage**: AWS S3 (Parquet files)

### Frontend
- **Framework**: React 18.2.0
- **Language**: TypeScript 5.3.3
- **Build Tool**: Vite 5.0.11
- **Routing**: React Router 6.21.1 (with v7 future flags)
- **State Management**: 
  - Zustand 4.4.7 (client state)
  - React Query 5.17.0 (server state)
- **HTTP Client**: Axios 1.6.5
- **Styling**: Tailwind CSS 4.0+ with @tailwindcss/postcss
- **Icons**: React Icons 5.0+

### Infrastructure
- **Cloud Provider**: AWS
- **IaC**: Terraform
- **Region**: us-west-1
- **Services**: RDS PostgreSQL, ElastiCache Redis, S3, VPC, IAM

---

## Completed Tasks

### Phase 1: Foundation & Backend Core

#### ✅ Task 1.1: Project Setup
- Initialized project repository
- Set up project structure (backend, frontend, service, infrastructure)
- Configured development environment
- Set up version control and branch strategy

#### ✅ Task 1.2: Database Design & Setup
- Designed PostgreSQL schema with all required tables
- Created Alembic migrations:
  - `001_initial_schema.py` - Initial database schema
  - `0b436e74aaff_increase_refresh_token_length.py` - Increased refresh token length to 1000 chars
  - `9a34438a9f36_description.py` - Added description field
- Set up local PostgreSQL database
- Created SQLAlchemy models:
  - `User` - User accounts with roles (user, operator, admin)
  - `Session` - Refresh token sessions
  - `UserProfile` - User profile data
  - `DataUpload` - Transaction data uploads
  - `Recommendation` - Generated recommendations
  - `PersonaHistory` - Persona assignment history
  - `Account` - Plaid account data (checking, savings, credit cards, etc.)
  - `Transaction` - Plaid transaction data
  - `Liability` - Plaid liability data (credit cards, mortgages, student loans)

#### ✅ Task 1.3: AWS Infrastructure Setup (Development)
- Set up AWS account and IAM roles
- Created VPC and networking (dev environment)
- Set up RDS PostgreSQL 16.10 instance (dev)
- Set up ElastiCache Redis 7.1 (dev)
- Set up S3 buckets (dev)
- Terraform modules created:
  - VPC module
  - RDS module
  - Redis module
  - S3 module
  - IAM module
- Includes `owner_id` support for shared AWS accounts

### Phase 2: Authentication & Authorization

#### ✅ Task 2.1: Authentication Foundation
- Implemented JWT token generation/validation using RS256
- Set up password hashing with bcrypt (cost factor 12)
- Created authentication middleware (`get_current_active_user`)
- Implemented token refresh mechanism
- Created RSA key generation utilities (`scripts/generate_rsa_keys.py`)
- Authentication dependencies in `app/core/dependencies.py`

**Key Files**:
- `backend/app/core/security.py` - JWT and password hashing
- `backend/app/core/dependencies.py` - FastAPI dependencies

#### ✅ Task 2.2: Email/Password Authentication
- Implemented user registration endpoint (`POST /api/v1/auth/register`)
- Implemented user login endpoint (`POST /api/v1/auth/login`)
- Created user management endpoints:
  - `GET /api/v1/users/me` - Get current user
  - `PUT /api/v1/users/me` - Update current user
- Added input validation:
  - Email format validation
  - Password strength (12+ chars, uppercase, lowercase, digit, special char)
- Token refresh endpoint (`POST /api/v1/auth/refresh`)
- Logout endpoint (`POST /api/v1/auth/logout`)
- Fixed enum role storage in database
- Refresh token length: 1000 characters
- Session management with database tracking

**Key Files**:
- `backend/app/api/v1/endpoints/auth.py` - Authentication endpoints
- `backend/app/api/v1/schemas/auth.py` - Request/response schemas

#### ✅ Task 2.3: Phone/SMS Authentication
- Integrated AWS SNS for SMS sending
- Implemented phone verification code generation (6-digit, cryptographically secure)
- Created Redis connection utility for code storage (10-minute TTL)
- Added rate limiting:
  - 5 SMS per hour per phone
  - 10 SMS per day per phone
- Implemented phone validation using `phonenumbers` library (E.164 format)
- Created endpoints:
  - `POST /api/v1/auth/phone/request` - Request verification code
  - `POST /api/v1/auth/phone/verify` - Verify code and login/register
- Automatic user registration/login on verification

**Key Files**:
- `backend/app/core/sms_service.py` - SMS service
- `backend/app/core/redis_client.py` - Redis client
- `backend/SMS_TESTING.md` - SMS testing documentation

#### ✅ Task 2.5: Account Linking
- Implemented account linking endpoints:
  - `POST /api/v1/auth/oauth/link` - Link OAuth provider
  - `POST /api/v1/auth/phone/link` - Link phone number
- Implemented account unlinking endpoints:
  - `DELETE /api/v1/auth/oauth/unlink/{provider}` - Unlink OAuth provider
  - `DELETE /api/v1/auth/phone/unlink` - Unlink phone number
- Created account merging logic:
  - Merges user data from duplicate accounts
  - Merges: DataUpload, Recommendation, UserProfile, PersonaHistory
  - Preserves primary authentication method
  - Ensures at least one authentication method remains after unlinking
- Proper validation, error handling
- CSRF protection via OAuth state verification

**Key Files**:
- `backend/app/core/oauth_service.py` - OAuth service
- `backend/OAUTH_SETUP.md` - OAuth configuration guide

#### ✅ Task 3.1: User Management API
- Implemented user profile endpoints:
  - `GET /api/v1/users/me` - Get current user profile
  - `PUT /api/v1/users/me` - Update current user profile
  - `GET /api/v1/users/{user_id}` - Get user profile by ID (with authorization)
  - `DELETE /api/v1/users/me` - Delete user account and all related data
- Created consent management API:
  - `POST /api/v1/consent` - Grant consent
  - `GET /api/v1/consent` - Get consent status
  - `DELETE /api/v1/consent` - Revoke consent (with optional data deletion)
- Added user data deletion endpoint that:
  - Deletes all user-related data (sessions, data uploads, recommendations, profiles, persona history)
  - Deletes the user record itself
  - Logs account deletion events
- Added logging for profile updates
- Unit tests created (20/64 passing, work in progress):
  - Test files created: `test_user_endpoints.py`, `test_consent_endpoints.py`
  - Using mocked database (no real DB needed)
  - Mock authentication dependencies
  - UUID to string conversion handled via field validator

**Key Files**:
- `backend/app/api/v1/endpoints/user.py` - User management endpoints
- `backend/app/api/v1/endpoints/consent.py` - Consent management endpoints
- `backend/app/api/v1/schemas/user.py` - User schemas (with UUID validator)
- `backend/tests/test_user_endpoints.py` - User endpoint tests
- `backend/tests/test_consent_endpoints.py` - Consent endpoint tests
- `backend/tests/conftest.py` - Test fixtures with mocked database

#### ✅ Task 3.2: Data Upload API
- Created file upload endpoint (`POST /api/v1/data/upload`):
  - Supports JSON and CSV file formats
  - Validates file type (extension and MIME type)
  - Validates file size (max 10MB)
  - Uploads files to S3 bucket (`spendsense-data`)
  - Stores upload metadata in PostgreSQL
  - Returns upload ID and status
- Created upload status endpoint (`GET /api/v1/data/upload/{upload_id}`):
  - Returns upload status (pending, processing, completed, failed)
  - Authorization: Users can only view their own uploads
  - Operators and admins can view any user's uploads
- Implemented S3 service (`app/core/s3_service.py`):
  - File validation (type, size)
  - S3 upload/download/delete functions
  - Proper error handling and logging
- Created data upload schemas:
  - `DataUploadResponse` - Upload response schema
  - `DataUploadStatusResponse` - Status response schema
- Unit tests created (12 tests, all passing):
  - Test file: `test_data_upload_endpoints.py`
  - Tests cover: successful uploads, validation, authorization, error handling

**Key Files**:
- `backend/app/api/v1/endpoints/data_upload.py` - Data upload endpoints
- `backend/app/core/s3_service.py` - S3 file storage service
- `backend/app/api/v1/schemas/data_upload.py` - Data upload schemas
- `backend/tests/test_data_upload_endpoints.py` - Data upload endpoint tests

#### ✅ Task 3.3: Caching Infrastructure
- Created comprehensive caching service (`app/core/cache_service.py`):
  - Session storage in Redis (store, get, update, delete)
  - API response caching decorators (profile, recommendations, signals)
  - Cache invalidation functions
  - TTL management per cache type
- Implemented session storage in Redis:
  - Sessions stored with 30-day TTL
  - Key format: `session:{session_id}`
  - Value: JSON with user_id, role, last_used_at
  - Integrated into all authentication endpoints:
    - Registration, login, token refresh, phone verification, OAuth callbacks
- Created API response caching:
  - Profile cache: 5-minute TTL
  - Recommendations cache: 1-hour TTL
  - Signals cache: 24-hour TTL
  - Decorators: `@cache_profile_response`, `@cache_recommendations_response`, `@cache_signals_response`
- Implemented cache invalidation strategy:
  - Automatic invalidation on user profile updates
  - Automatic invalidation on user deletion
  - Automatic invalidation on consent revocation
  - Functions for targeted invalidation (profile, recommendations, signals, all)
  - Pattern-based invalidation support
- Unit tests created (21 tests, all passing):
  - Test file: `test_cache_service.py`
  - Tests cover: session storage, API caching, cache invalidation, error handling

**Key Files**:
- `backend/app/core/cache_service.py` - Caching service
- `backend/app/core/redis_client.py` - Redis client (already existed)
- `backend/tests/test_cache_service.py` - Cache service tests
- Updated endpoints: `auth.py`, `user.py`, `consent.py` (integrated caching)

#### ✅ Task 4.1: Data Ingestion Service
- Created database models for Plaid data:
  - `Account` model (`backend/app/models/account.py`):
    - Stores account information (account_id, type, subtype, balances, holder_category)
    - Supports depository accounts (checking, savings, money market, HSA)
    - Supports credit accounts (credit cards)
    - Supports loan accounts (mortgages, student loans)
    - Excludes business accounts (only individual accounts)
    - Foreign keys to users and data_uploads
  - `Transaction` model (`backend/app/models/transaction.py`):
    - Stores transaction data (transaction_id, date, amount, merchant_name, payment_channel)
    - Stores personal finance category (primary/detailed)
    - Tracks pending status
    - Foreign keys to accounts, users, and data_uploads
  - `Liability` model (`backend/app/models/liability.py`):
    - Stores credit card liabilities (APRs, minimum payment, last payment, overdue status)
    - Stores mortgage/student loan liabilities (interest rate, next payment due date)
    - Foreign keys to accounts, users, and data_uploads
- Created Alembic migration:
  - `002_add_accounts_transactions_liabilities.py` - Creates accounts, transactions, and liabilities tables with indexes and foreign keys
- Created Plaid data parser (`service/app/ingestion/parser.py`):
  - `PlaidParser` class with JSON and CSV parsing support
  - `parse_json()` - Parses Plaid JSON format with accounts, transactions, liabilities
  - `parse_csv()` - Parses Plaid CSV format (separate sections for accounts, transactions, liabilities)
  - Handles nested structures (balances, personal_finance_category)
  - Proper error handling and validation
- Created data validator (`service/app/ingestion/validator.py`):
  - `PlaidValidator` class with comprehensive schema validation
  - Validates account structure (type, subtype, holder_category, balances)
  - Validates transaction structure (date format, amount, payment_channel, category)
  - Validates liability structure (APRs, dates, amounts, interest rates)
  - Cross-references transactions/liabilities with accounts
  - Returns validation errors and warnings with severity levels
  - Validates account types: checking, savings, credit cards, money market, HSA
  - Excludes business accounts (holder_category must be "individual")
- Created storage module (`service/app/ingestion/storage.py`):
  - `DataStorage` class for PostgreSQL and S3 Parquet storage
  - PostgreSQL storage methods:
    - `store_accounts_postgresql()` - Stores/updates accounts in PostgreSQL
    - `store_transactions_postgresql()` - Stores/updates transactions in PostgreSQL
    - `store_liabilities_postgresql()` - Stores/updates liabilities in PostgreSQL
    - Handles account_id mapping (Plaid account_id → database account.id)
    - Supports upsert logic (update existing, insert new)
  - S3 Parquet storage methods:
    - `store_parquet_s3()` - Stores data as Parquet files in S3
    - Creates pandas DataFrames for accounts, transactions, liabilities
    - Converts DataFrames to Parquet format using PyArrow
    - Uploads to S3 bucket (`spendsense-analytics`)
    - S3 key format: `{data_type}/user_id={user_id}/ingestion_date={date}/{data_type}.parquet`
- Created main ingestion service (`service/app/ingestion/service.py`):
  - `IngestionService` class orchestrates the full ingestion pipeline
  - `ingest()` method:
    - Parses file (JSON or CSV)
    - Validates data structure
    - Stores in PostgreSQL (accounts, transactions, liabilities)
    - Stores in S3 as Parquet files
    - Returns comprehensive ingestion report with:
      - Summary (accounts/transactions/liabilities processed, valid, invalid)
      - Errors and warnings
      - Storage information (PostgreSQL counts, S3 keys)
      - Status (pending, processing, completed, failed)
- Service layer structure created:
  - `service/app/ingestion/` - Data ingestion module
  - `service/app/ingestion/__init__.py` - Exports parser, validator, storage, service
  - All modules follow existing patterns and pass linting

**Key Files**:
- `backend/app/models/account.py` - Account model
- `backend/app/models/transaction.py` - Transaction model
- `backend/app/models/liability.py` - Liability model
- `backend/alembic/versions/002_add_accounts_transactions_liabilities.py` - Migration
- `service/app/ingestion/parser.py` - Plaid data parser
- `service/app/ingestion/validator.py` - Data validator
- `service/app/ingestion/storage.py` - PostgreSQL and S3 storage
- `service/app/ingestion/service.py` - Main ingestion service

#### ✅ Task 4.2: Data Validation Service
- Enhanced existing `PlaidValidator` class (`service/app/ingestion/validator.py`):
  - Validates account structure (required fields, types, subtypes)
  - Validates transaction structure (required fields, date formats, amounts)
  - Validates liability structure (APRs, payment amounts, dates)
  - Detects duplicate accounts/transactions
  - Validates data ranges (dates, amounts)
  - Returns validation errors with clear messages and severity levels
  - Logs validation errors
  - Cross-references transactions/liabilities with accounts
- Created validation error reporting:
  - `ValidationError` class with type, field, value, message, severity
  - Error severity levels: "error" (blocks processing) and "warning" (allows processing)
  - Comprehensive error reporting with context
  - Error aggregation and summary reporting

**Key Files**:
- `service/app/ingestion/validator.py` - Enhanced data validator
- `service/app/ingestion/validation_results.py` - Validation error classes

#### ✅ Task 4.3: Synthetic Data Generator
- Created synthetic Plaid data generator (`scripts/synthetic_data_generator.py`)
- Generates 100 diverse user profiles (20 per persona)
- Uses YAML-based persona configurations located in `scripts/persona_configs/`:
  - `1_high_utilization.yaml` - Users with high credit card utilization (≥50%, ≥80%)
  - `2_variable_income.yaml` - Users with irregular income streams (freelancers, gig workers)
  - `3_subscription_heavy.yaml` - Users with many recurring subscriptions
  - `4_savings_builder.yaml` - Users consistently building savings
  - `5_custom.yaml` - General/mixed profiles
- Uses real merchant data from CSV file (`docs/support/transactions_100_users_2024.csv`) for realistic transaction generation
- Validates all generated data against `PlaidValidator` from `service/app/common/validator.py`
- Supports export to JSON format (single file per user: `{user_id}.json` containing accounts, transactions, and liabilities)
- Supports export to CSV format (separate files: `{user_id}_accounts.csv`, `{user_id}_transactions.csv`, `{user_id}_liabilities.csv`)
- Supports export to both formats (`--format both`)
- Configuration-driven generation with comprehensive logging
- All generated data passes validation (0 errors, 0 warnings)
- Suitable for testing feature engineering, persona assignment, and recommendation generation
- Command-line interface with arguments:
  - `config_dir` (required): Directory containing persona YAML configuration files
  - `transactions_csv` (required): Path to CSV file with sample transactions
  - `--output-dir` (optional): Directory to save generated data (default: `synthetic_data`)
  - `--format` (optional): Output format - `json`, `csv`, or `both` (default: `json`)

**Key Files**:
- `scripts/synthetic_data_generator.py` - Main synthetic data generator script
- `scripts/persona_configs/` - YAML configuration files for each persona (5 files)
- `scripts/README.md` - Documentation for synthetic data generator
- `docs/support/transactions_100_users_2024.csv` - Sample transaction data for merchant pool

### Phase 4: Frontend Development

#### ✅ Task 3.4: API Documentation
- Enhanced FastAPI app with comprehensive OpenAPI metadata:
  - Added API description with features overview
  - Added authentication guide with JWT token usage
  - Added rate limiting information
  - Added response caching information
  - Configured tag descriptions for all endpoint groups
- Added request/response examples to all Pydantic schemas:
  - Authentication schemas (register, login, token refresh, phone verification, OAuth)
  - User management schemas (profile, profile update)
  - Consent management schemas (grant, status, revoke)
  - Data upload schemas (upload response, status response)
- Enhanced all endpoint documentation:
  - Added `summary` field to all endpoints
  - Added `description` field with detailed information
  - Added `responses` parameter with status codes and descriptions
  - Applied to all endpoint groups:
    - Authentication endpoints (register, login, refresh, logout, phone, OAuth)
    - User management endpoints (get profile, update profile, delete account)
    - Consent management endpoints (grant, get status, revoke)
    - Data upload endpoints (upload file, get status)
    - Operator endpoints (review queue, analytics, user management)
- Documentation available at:
  - `/docs` - Swagger UI (interactive API documentation)
  - `/redoc` - ReDoc (alternative documentation view)
  - `/openapi.json` - OpenAPI JSON schema

**Key Files**:
- `backend/app/main.py` - Enhanced with OpenAPI metadata
- `backend/app/api/v1/schemas/auth.py` - Added examples to all auth schemas
- `backend/app/api/v1/schemas/user.py` - Added examples to user schemas
- `backend/app/api/v1/schemas/consent.py` - Added examples to consent schemas
- `backend/app/api/v1/schemas/data_upload.py` - Added examples to data upload schemas
- `backend/app/api/v1/endpoints/auth.py` - Enhanced with summaries and responses
- `backend/app/api/v1/endpoints/user.py` - Enhanced with summaries and responses
- `backend/app/api/v1/endpoints/consent.py` - Enhanced with summaries and responses
- `backend/app/api/v1/endpoints/data_upload.py` - Enhanced with summaries and responses
- `backend/app/api/v1/endpoints/operator.py` - Enhanced with summaries and responses

#### ✅ Task 2.6: Authorization (RBAC)
- Implemented role-based access control:
  - User roles: `user`, `operator`, `admin`
  - Role hierarchy: admin > operator > user
- Created authorization dependencies:
  - `require_role(role)` - Require specific role
  - `require_operator` - Require operator or admin
  - `require_admin` - Require admin role
- Added resource-level authorization helpers:
  - `check_resource_access` - Check if user can access resource
  - `check_user_access` - Check if user can access another user's data
  - `require_owner_or_operator_factory` - Factory for owner/operator checks
  - `require_owner_or_admin_factory` - Factory for owner/admin checks
  - `require_owner_only_factory` - Factory for owner-only checks
- Added endpoint-level authorization:
  - Operator endpoints (GET /api/v1/operator/review, GET /api/v1/operator/analytics, etc.)
  - Admin endpoints (GET /api/v1/operator/admin/users, PUT /api/v1/operator/admin/users/{user_id}/role)
- Added resource-level authorization example:
  - User endpoints (GET /api/v1/users/{user_id})
- Implemented authorization logging for audit trail
- All authorization failures logged with user ID, role, and resource details

**Key Files**:
- `backend/app/core/dependencies.py` - Authorization dependencies
- `backend/app/api/v1/endpoints/user.py` - User endpoints with authorization

### Phase 4: Frontend Development

#### ✅ Task 10.1: Frontend Project Setup
- Initialized React 18.2.0 project with TypeScript 5.3.3
- Configured Vite 5.0.11 build tool
- Set up React Router 6.21.1 with all routes:
  - Public: `/login`, `/register`
  - Protected: `/`, `/profile`, `/recommendations`, `/recommendations/:id`, `/settings`, `/upload`
  - Operator: `/operator`, `/operator/review/:id`, `/operator/analytics`
- Implemented Zustand 4.4.7 for client state management:
  - Auth store with persistence (`src/store/authStore.ts`)
- Configured React Query 5.17.0 for server state
- Set up Axios 1.6.5 with interceptors:
  - Request interceptor: Adds JWT token to Authorization header
  - Response interceptor: Handles 401 errors and token refresh
- Implemented automatic token refresh mechanism
- Created protected route components (`ProtectedRoute`, `OperatorRoute`)
- Configured environment variables (`.env.local`)
- Created complete project structure with placeholder pages

**Key Files**:
- `frontend/src/services/api.ts` - Axios instance with interceptors
- `frontend/src/store/authStore.ts` - Authentication state store
- `frontend/src/App.tsx` - Main app with routing
- `frontend/vite.config.ts` - Vite configuration

#### ✅ Task 10.2: Authentication UI
- Created login page with:
  - Email/password authentication
  - Phone/SMS authentication
  - Tab switching between methods
  - Form validation
  - Error handling
  - Loading states
  - OAuth buttons
- Created registration page with:
  - Email/password registration with password confirmation
  - Phone/SMS registration
  - Tab switching between methods
  - Form validation
  - Error handling
  - Loading states
  - OAuth buttons
- Implemented phone verification component:
  - 6-digit code input
  - 10-minute countdown timer
  - Resend code functionality (rate-limited)
  - Error handling
  - Loading states
- Added OAuth buttons component:
  - Google, GitHub, Facebook, Apple buttons
  - React Icons (FaGoogle, FaGithub, FaFacebook, FaApple)
  - Proper styling with brand colors
  - Loading states
  - Error handling
- Implemented comprehensive form validation:
  - Email format validation
  - Password strength (matches backend: 12+ chars, uppercase, lowercase, digit, special char)
  - Phone E.164 format validation
  - Verification code validation (6 digits)
- Integrated Tailwind CSS 4.0+ with @tailwindcss/postcss
- Created authService with API integration for all auth methods
- Implemented validation utilities (`src/utils/validation.ts`)
- Added React Router v7 future flags:
  - `v7_startTransition: true`
  - `v7_relativeSplatPath: true`
- All pages feature Tailwind styling with:
  - Proper spacing, colors, hover states
  - Focus states for accessibility
  - Responsive design
  - Modern UI/UX

**Key Files**:
- `frontend/src/pages/Login.tsx` - Login page
- `frontend/src/pages/Register.tsx` - Registration page
- `frontend/src/components/PhoneVerification.tsx` - Phone verification component
- `frontend/src/components/OAuthButtons.tsx` - OAuth buttons component
- `frontend/src/services/authService.ts` - Authentication service
- `frontend/src/utils/validation.ts` - Validation utilities

#### ✅ Task 10.3: Token Management (Completed in 10.1)
- Implemented token storage in localStorage
- Created token refresh mechanism (automatic on 401)
- Implemented logout functionality
- Added token expiration handling
- Integrated into API client and auth store

#### ✅ Task 10.4: Account Linking UI
- Updated backend `UserProfileResponse` schema to include `oauth_providers` field
- Created `userService` for fetching user profile with linked accounts
- Added account linking API methods to `authService`:
  - `linkOAuthProvider` - Link OAuth provider to account
  - `linkPhoneNumber` - Link phone number to account
  - `unlinkOAuthProvider` - Unlink OAuth provider from account
  - `unlinkPhoneNumber` - Unlink phone number from account
- Created `AccountLinking` component with:
  - Display linked accounts (email, phone, OAuth providers)
  - Link OAuth providers (Google, GitHub, Facebook, Apple) via OAuth flow
  - Link phone number via SMS verification
  - Unlink accounts with confirmation dialogs
  - Validation to ensure at least one authentication method remains
  - Visual indicators for linked/unlinked accounts
  - Error handling and success messages
  - OAuth callback handling with state verification
- Created Settings page with AccountLinking component
- Implemented OAuth callback handling for account linking:
  - Detects OAuth callback in URL parameters
  - Verifies OAuth state for CSRF protection
  - Calls link endpoint with code and state
  - Handles account merging notifications
- All code compiles successfully (TypeScript and Python)

**Key Files**:
- `frontend/src/components/AccountLinking.tsx` - Account linking component
- `frontend/src/pages/Settings.tsx` - Settings page with account linking
- `frontend/src/services/userService.ts` - User profile service
- `frontend/src/services/authService.ts` - Updated with account linking methods
- `backend/app/api/v1/schemas/user.py` - Updated UserProfileResponse schema

#### ✅ Task 11.1: Dashboard Page
- Created personalized dashboard layout with sections for:
  - Assigned persona display
  - Key behavioral signals (30-day)
  - Recommendations list (approved)
  - Consent status badge
- Created `dashboardService` for fetching dashboard data:
  - Fetches user profile, behavioral profile, and recommendations
  - Gracefully handles missing endpoints (404s)
  - Returns structured dashboard data
- Implemented `PersonaBadge` component:
  - Color-coded persona indicators (5 personas: High Utilization, Variable Income, Subscription-Heavy, Savings Builder, Custom)
  - Shows persona name and description
  - Visual indicators with distinct color schemes
- Implemented `BehavioralSignals` component:
  - Displays 30-day behavioral signals in organized cards
  - Shows subscriptions metrics (recurring merchants, monthly spend, share)
  - Shows savings metrics (net inflow, growth rate, emergency fund coverage)
  - Shows credit metrics (utilization, high utilization cards, interest charges, overdue accounts)
  - Shows income metrics (payment frequency, cash flow buffer, variable income)
  - Formatted currency and percentages
  - Empty state when no signals available
- Implemented `RecommendationsList` component:
  - Displays approved recommendations with type badges (education/partner offer)
  - Shows recommendation title, content, and rationale
  - Links to detailed recommendation view
  - Empty state for new users
- Implemented `ConsentStatusBadge` component:
  - Shows consent status with color-coded badge (green/yellow)
  - Links to settings for consent management
  - Clear messaging about consent impact
- Main Dashboard page features:
  - Loading skeletons while fetching data
  - Error states with retry functionality
  - Empty states for new users with helpful guidance and quick actions
  - Quick actions section (Upload Data, View Profile, All Recommendations)
  - Mobile-responsive design
  - All components properly typed with TypeScript
- Dashboard service handles missing backend endpoints gracefully
- When behavioral profiling and recommendations endpoints are implemented, dashboard will automatically display that data

**Key Files**:
- `frontend/src/pages/Dashboard.tsx` - Main dashboard page
- `frontend/src/services/dashboardService.ts` - Dashboard data service
- `frontend/src/components/PersonaBadge.tsx` - Persona display component
- `frontend/src/components/BehavioralSignals.tsx` - Behavioral signals display component
- `frontend/src/components/RecommendationsList.tsx` - Recommendations list component
- `frontend/src/components/ConsentStatusBadge.tsx` - Consent status badge component

#### ✅ Task 11.2: Profile View
- Created comprehensive profile page layout with sections for:
  - Current persona display
  - Behavioral signals (30-day and 180-day)
  - Signal trends visualization
  - Persona history timeline
- Created `profileService` for fetching profile data:
  - Fetches behavioral profile and persona history
  - Gracefully handles missing endpoints (404s)
  - Returns structured profile data
- Implemented `TimePeriodSelector` component:
  - Toggle between 30-day and 180-day analysis
  - Tab-style selector with active state
  - Updates signals display based on selected period
- Implemented `ProfileBehavioralSignals` component:
  - Displays behavioral signals with expandable sections
  - Shows subscriptions, savings, credit, and income metrics
  - Expandable/collapsible sections for detailed views
  - Formatted currency and percentages
  - Empty state when no signals available
- Implemented `SignalTrends` component:
  - Simple progress bar visualizations
  - Shows trends between 30-day and 180-day periods
  - Trend indicators (increasing/decreasing/stable)
  - Color-coded trends (green for increasing, red for decreasing)
  - Displays both 30d and 180d values for comparison
- Implemented `PersonaHistoryTimeline` component:
  - Timeline visualization of persona assignments
  - Shows persona changes over time
  - Displays assigned_at timestamps
  - Uses PersonaBadge component for consistency
  - Sorted by date (most recent first)
  - Empty state for new users
- Main Profile page features:
  - Current persona display
  - Time period selector
  - Behavioral signals with expandable sections
  - Signal trends visualization
  - Persona history timeline
  - Export functionality placeholder (PDF/CSV buttons)
  - Loading skeletons while fetching data
  - Error states with retry functionality
  - Empty states for new users
  - Mobile-responsive design
  - All components properly typed with TypeScript
- Profile service handles missing backend endpoints gracefully
- When behavioral profiling and persona history endpoints are implemented, profile will automatically display that data

**Key Files**:
- `frontend/src/pages/Profile.tsx` - Main profile page
- `frontend/src/services/profileService.ts` - Profile data service
- `frontend/src/components/TimePeriodSelector.tsx` - Time period selector component
- `frontend/src/components/ProfileBehavioralSignals.tsx` - Profile behavioral signals component
- `frontend/src/components/SignalTrends.tsx` - Signal trends visualization component
- `frontend/src/components/PersonaHistoryTimeline.tsx` - Persona history timeline component

---

## Architecture & Design Decisions

### Authentication Flow
1. User registers/logs in → Receives access token + refresh token
2. Access token stored in localStorage + Zustand store
3. Access token added to all API requests via interceptor
4. On 401 error → Automatically refresh token using refresh token
5. If refresh fails → Redirect to login

### Token Management
- **Access Token**: Short-lived, used for API authentication
- **Refresh Token**: Long-lived, stored in database Session table
- **Storage**: localStorage for frontend, database for backend validation
- **Refresh**: Automatic via Axios interceptor

### State Management Strategy
- **Client State**: Zustand (auth, UI state, form state)
- **Server State**: React Query (API data, caching, refetching)
- **URL State**: React Router (query params, path params)

### Security Decisions
- **Password Hashing**: bcrypt with cost factor 12
- **JWT Algorithm**: RS256 (asymmetric keys)
- **Token Storage**: localStorage (frontend), database (backend)
- **Rate Limiting**: Redis-based for SMS (5/hour, 10/day)
- **CSRF Protection**: OAuth state parameter
- **Input Validation**: Pydantic on backend, custom validators on frontend

### Database Design
- **UUID Primary Keys**: All tables use UUID for user IDs
- **Timestamps**: `created_at`, `updated_at` on all tables
- **Soft Deletes**: Not implemented (future consideration)
- **Foreign Keys**: Proper relationships with cascade options
- **Indexes**: On frequently queried fields (email, user_id, etc.)

---

## Database Schema

### Tables

#### `users`
- `id` (UUID, PK)
- `email` (String, unique, nullable)
- `phone` (String, unique, nullable)
- `password_hash` (String, nullable)
- `role` (Enum: user, operator, admin)
- `is_active` (Boolean)
- `created_at`, `updated_at` (DateTime)

#### `sessions`
- `session_id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `refresh_token_hash` (String)
- `expires_at` (DateTime)
- `created_at` (DateTime)

#### `user_profiles`
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id, unique)
- `consent_granted` (Boolean)
- `consent_version` (String)
- `description` (Text, nullable)
- `created_at`, `updated_at` (DateTime)

#### `data_uploads`
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `file_path` (String)
- `file_format` (Enum: json, csv)
- `status` (Enum: pending, processing, completed, failed)
- `error_message` (Text, nullable)
- `created_at`, `updated_at` (DateTime)

#### `recommendations`
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `type` (Enum: education, partner_offer)
- `title` (String)
- `content` (Text)
- `rationale` (Text)
- `status` (Enum: pending, approved, rejected)
- `created_at`, `updated_at` (DateTime)

#### `persona_history`
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `persona` (Enum: high_utilization, variable_income, subscription_heavy, savings_builder, custom)
- `rationale` (Text)
- `created_at` (DateTime)

#### `accounts`
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.user_id)
- `account_id` (String, Plaid account_id)
- `name` (String)
- `type` (String: depository, credit, loan)
- `subtype` (String: checking, savings, credit card, money market, HSA, mortgage, student)
- `holder_category` (String: individual, business)
- `balance_available` (Numeric, nullable)
- `balance_current` (Numeric)
- `balance_limit` (Numeric, nullable)
- `iso_currency_code` (String, default: USD)
- `mask` (String, nullable)
- `upload_id` (UUID, FK → data_uploads.upload_id, nullable)
- `created_at`, `updated_at` (DateTime)

#### `transactions`
- `id` (UUID, PK)
- `account_id` (UUID, FK → accounts.id)
- `user_id` (UUID, FK → users.user_id)
- `transaction_id` (String, Plaid transaction_id)
- `date` (Date)
- `amount` (Numeric)
- `merchant_name` (String, nullable)
- `merchant_entity_id` (String, nullable)
- `payment_channel` (String: online, in_store, other)
- `category_primary` (String)
- `category_detailed` (String, nullable)
- `pending` (Boolean, default: false)
- `iso_currency_code` (String, default: USD)
- `upload_id` (UUID, FK → data_uploads.upload_id, nullable)
- `created_at` (DateTime)

#### `liabilities`
- `id` (UUID, PK)
- `account_id` (UUID, FK → accounts.id)
- `user_id` (UUID, FK → users.user_id)
- `apr_percentage` (Numeric, nullable, for credit cards)
- `apr_type` (String, nullable: purchase, cash, balance_transfer)
- `minimum_payment_amount` (Numeric, nullable)
- `last_payment_amount` (Numeric, nullable)
- `last_payment_date` (Date, nullable)
- `last_statement_balance` (Numeric, nullable)
- `is_overdue` (Boolean, nullable)
- `next_payment_due_date` (Date, nullable, indexed)
- `interest_rate` (Numeric, nullable, for mortgages/student loans)
- `upload_id` (UUID, FK → data_uploads.upload_id, nullable)
- `created_at`, `updated_at` (DateTime)

---

## Authentication & Authorization

### Authentication Methods
1. **Email/Password**: Traditional email + password registration/login
2. **Phone/SMS**: Phone number + SMS verification code
3. **OAuth**: Google, GitHub, Facebook, Apple (configured)

### Authorization Levels
1. **User**: Can access own data
2. **Operator**: Can access own data + review recommendations
3. **Admin**: Can access all data + manage users

### Role Hierarchy
```
Admin > Operator > User
```

### Protected Routes
- **Public**: `/login`, `/register`
- **User**: All authenticated routes
- **Operator**: `/operator/*` routes
- **Admin**: `/operator/admin/*` routes

---

## API Endpoints

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register with email/password
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout (revoke refresh token)
- `POST /api/v1/auth/phone/request` - Request SMS verification code
- `POST /api/v1/auth/phone/verify` - Verify SMS code and login/register
- `GET /api/v1/auth/oauth/{provider}/authorize` - Get OAuth authorization URL
- `GET|POST /api/v1/auth/oauth/{provider}/callback` - OAuth callback handler
- `POST /api/v1/auth/oauth/link` - Link OAuth provider to account
- `POST /api/v1/auth/phone/link` - Link phone number to account
- `DELETE /api/v1/auth/oauth/unlink/{provider}` - Unlink OAuth provider
- `DELETE /api/v1/auth/phone/unlink` - Unlink phone number

### User Endpoints
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/{user_id}` - Get user by ID (with authorization)
- `DELETE /api/v1/users/me` - Delete user account and all related data

### Consent Endpoints
- `POST /api/v1/consent` - Grant consent for data processing
- `GET /api/v1/consent` - Get consent status
- `DELETE /api/v1/consent` - Revoke consent (with optional data deletion)

### Data Upload Endpoints
- `POST /api/v1/data/upload` - Upload transaction data file (JSON/CSV, max 10MB)
- `GET /api/v1/data/upload/{upload_id}` - Get upload status

### Operator Endpoints (Future)
- `GET /api/v1/operator/review` - Get review queue
- `GET /api/v1/operator/analytics` - Get analytics
- `GET /api/v1/operator/admin/users` - Get all users (admin only)
- `PUT /api/v1/operator/admin/users/{user_id}/role` - Update user role (admin only)

---

## Frontend Components

### Pages
- `Login.tsx` - Login page with email/phone/OAuth
- `Register.tsx` - Registration page with email/phone/OAuth
- `Dashboard.tsx` - User dashboard with persona, signals, recommendations, and consent status
- `Profile.tsx` - User profile page with behavioral signals, trends, and persona history
- `Recommendations.tsx` - Recommendations list (placeholder)
- `RecommendationDetail.tsx` - Recommendation detail (placeholder)
- `Settings.tsx` - Settings page with Account Linking component
- `Upload.tsx` - Data upload page (placeholder)
- `OperatorDashboard.tsx` - Operator dashboard (placeholder)
- `OperatorReview.tsx` - Operator review page (placeholder)
- `OperatorAnalytics.tsx` - Operator analytics (placeholder)

### Components
- `OAuthButtons.tsx` - OAuth provider buttons with icons
- `PhoneVerification.tsx` - Phone verification with countdown timer
- `AccountLinking.tsx` - Account linking component for managing linked authentication methods
- `PersonaBadge.tsx` - Persona display component with color-coded indicators
- `BehavioralSignals.tsx` - Behavioral signals display component (subscriptions, savings, credit, income)
- `RecommendationsList.tsx` - Recommendations list component with type badges and rationales
- `ConsentStatusBadge.tsx` - Consent status badge component with settings link
- `TimePeriodSelector.tsx` - Time period selector component (30-day vs 180-day)
- `ProfileBehavioralSignals.tsx` - Profile behavioral signals component with expandable sections
- `SignalTrends.tsx` - Signal trends visualization component with progress bars
- `PersonaHistoryTimeline.tsx` - Persona history timeline component

### Services
- `api.ts` - Axios instance with interceptors
- `authService.ts` - Authentication service functions (including account linking)
- `userService.ts` - User profile service for fetching user data
- `dashboardService.ts` - Dashboard data service for fetching persona, signals, and recommendations
- `profileService.ts` - Profile data service for fetching behavioral profile and persona history

### State Management
- `authStore.ts` - Zustand store for authentication state
- `queryClient.ts` - React Query client configuration

### Utilities
- `validation.ts` - Form validation utilities
- `queryClient.ts` - React Query configuration

---

## Infrastructure

### AWS Resources (Dev Environment)
- **VPC**: Custom VPC with public/private subnets
- **RDS PostgreSQL**: 16.10 instance in private subnet
- **ElastiCache Redis**: 7.1 cluster in private subnet
- **S3 Buckets**: For file storage
- **IAM Roles**: For service access
- **Security Groups**: Properly configured for access control

### Terraform Modules
- `modules/vpc/` - VPC and networking
- `modules/rds/` - RDS PostgreSQL
- `modules/redis/` - ElastiCache Redis
- `modules/s3/` - S3 buckets
- `modules/iam/` - IAM roles and policies

### Environment
- **Region**: us-west-1
- **Environment**: dev
- **Owner ID Support**: For shared AWS accounts

---

## Configuration & Environment

### Backend Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_PUBLIC_KEY` - RSA public key for JWT verification
- `JWT_PRIVATE_KEY` - RSA private key for JWT signing
- `JWT_ALGORITHM` - RS256
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiration
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiration
- `AWS_REGION` - AWS region
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `SNS_PHONE_NUMBER` - AWS SNS phone number (optional)
- OAuth credentials (Google, GitHub, Facebook, Apple)

### Frontend Environment Variables
- `VITE_API_BASE_URL` - Backend API base URL (default: http://localhost:8000)
- `VITE_ENV` - Environment (development/production)

### Configuration Files
- `backend/env.example` - Backend environment template
- `frontend/.env.local` - Frontend environment (gitignored)
- `backend/app/config.py` - Backend configuration
- `frontend/vite.config.ts` - Vite configuration
- `frontend/tailwind.config.js` - Tailwind CSS configuration
- `frontend/postcss.config.js` - PostCSS configuration

---

## Key Files & Locations

### Backend
- `backend/app/main.py` - FastAPI application entry point (with OpenAPI metadata)
- `backend/app/config.py` - Configuration settings
- `backend/app/database.py` - Database connection
- `backend/app/core/security.py` - JWT and password hashing
- `backend/app/core/dependencies.py` - FastAPI dependencies
- `backend/app/core/sms_service.py` - SMS service
- `backend/app/core/redis_client.py` - Redis client
- `backend/app/core/oauth_service.py` - OAuth service
- `backend/app/core/cache_service.py` - Caching service (session storage, API caching, invalidation)
- `backend/app/core/s3_service.py` - S3 file storage service
- `backend/app/api/v1/endpoints/auth.py` - Authentication endpoints
- `backend/app/api/v1/endpoints/user.py` - User endpoints
- `backend/app/api/v1/endpoints/consent.py` - Consent management endpoints
- `backend/app/api/v1/endpoints/data_upload.py` - Data upload endpoints
- `backend/app/models/` - SQLAlchemy models
  - `account.py` - Account model
  - `transaction.py` - Transaction model
  - `liability.py` - Liability model
- `backend/app/api/v1/schemas/auth.py` - Authentication schemas (with examples)
- `backend/app/api/v1/schemas/user.py` - User management schemas (with examples)
- `backend/app/api/v1/schemas/consent.py` - Consent management schemas (with examples)
- `backend/app/api/v1/schemas/data_upload.py` - Data upload schemas (with examples)
- `backend/alembic/versions/` - Database migrations
  - `002_add_accounts_transactions_liabilities.py` - Accounts, transactions, liabilities tables
- `backend/tests/test_data_upload_endpoints.py` - Data upload endpoint tests
- `backend/tests/test_cache_service.py` - Cache service tests

### Frontend
- `frontend/src/main.tsx` - React entry point
- `frontend/src/App.tsx` - Main app component with routing
- `frontend/src/pages/` - Page components
- `frontend/src/components/` - Reusable components (OAuthButtons, PhoneVerification, AccountLinking, PersonaBadge, BehavioralSignals, RecommendationsList, ConsentStatusBadge, TimePeriodSelector, ProfileBehavioralSignals, SignalTrends, PersonaHistoryTimeline)
- `frontend/src/services/api.ts` - API client
- `frontend/src/services/authService.ts` - Auth service (including account linking)
- `frontend/src/services/userService.ts` - User profile service
- `frontend/src/services/dashboardService.ts` - Dashboard data service
- `frontend/src/services/profileService.ts` - Profile data service
- `frontend/src/store/authStore.ts` - Auth state store
- `frontend/src/utils/validation.ts` - Validation utilities
- `frontend/src/styles/index.css` - Global styles with Tailwind

### Service Layer
- `service/app/ingestion/` - Data ingestion services
  - `parser.py` - Plaid data parser (JSON/CSV)
  - `storage.py` - PostgreSQL and S3 Parquet storage
  - `service.py` - Main ingestion service
  - `__init__.py` - Module exports
- `service/app/common/` - Shared utilities
  - `validator.py` - Plaid schema validator (moved from ingestion/)
- `service/setup.py` - Service package setup file (makes service installable)
- `scripts/synthetic_data_generator.py` - Synthetic data generator script
- `scripts/persona_configs/` - Persona YAML configuration files
  - `1_high_utilization.yaml` - High utilization persona config
  - `2_variable_income.yaml` - Variable income persona config
  - `3_subscription_heavy.yaml` - Subscription-heavy persona config
  - `4_savings_builder.yaml` - Savings builder persona config
  - `5_custom.yaml` - Custom persona config
- `scripts/requirements.txt` - Generator dependencies (Faker, PyYAML)
- `synthetic_data/` - Generated synthetic user profiles (100 JSON files)

### Infrastructure
- `infrastructure/terraform/environments/dev/` - Dev environment Terraform
- `infrastructure/terraform/modules/` - Terraform modules

### Documentation
- `docs/PROJECT-PLAN.md` - Project plan with task list
- `docs/architecture.md` - System architecture
- `docs/backend/` - Backend PRD documents
- `docs/frontend/` - Frontend PRD documents
- `docs/service/` - Service layer PRD documents
- `backend/SMS_TESTING.md` - SMS testing guide
- `backend/OAUTH_SETUP.md` - OAuth setup guide
- `backend/DATABASE_SETUP.md` - Database setup guide
- `scripts/README.md` - Scripts documentation including synthetic data generator

---

## Next Steps

### Immediate (Phase 2 - Week 4)
- **Task 4.1**: Data Ingestion Service ✅ (Completed)
- **Task 4.2**: Data Validation Service ✅ (Completed)
- **Task 4.3**: Synthetic Data Generator ✅ (Completed)
- **Task 5.1**: Subscription Detection (Next)
- **Task 5.2**: Savings Pattern Detection
- **Task 5.3**: Credit Utilization Detection
- **Task 5.4**: Income Stability Detection

### Immediate (Phase 4)
- **Task 11.3**: Recommendations View
- **Task 11.4**: Recommendation Detail View
- **Task 12.1**: Data Upload UI (backend API ready)
- **Task 12.2**: Consent Management UI
- **Task 12.3**: Mobile Responsiveness
- **Task 12.4**: UI Polish & Accessibility

### Future (Phase 2 & 3)
- **Task 4.1**: Data Ingestion Service ✅ (Completed)
- **Task 4.2**: Data Validation Service ✅ (Completed)
- **Task 4.3**: Synthetic Data Generator ✅ (Completed)
- **Task 5.1-5.4**: Feature Engineering (Subscription Detection, Savings Patterns, Credit Utilization, Income Stability)
- **Task 6.1-6.3**: Persona Assignment
- **Task 7.1-7.4**: Recommendation Generation
- **Task 8.1-8.4**: Guardrails Implementation
- **Task 9.1-9.3**: Decision Traces & Evaluation

### Infrastructure (Phase 6)
- **Task 15.1-15.3**: Containerization & ECS Setup
- **Task 16.1-16.4**: CI/CD Pipeline

---

## Notes & Considerations

### Known Issues
- OAuth providers require backend configuration to be fully functional
- Browser extension CSP errors (not related to SpendSense) can be ignored

### Best Practices Implemented
- ✅ Environment variables for configuration
- ✅ Proper error handling and logging
- ✅ Input validation on both frontend and backend
- ✅ Security best practices (bcrypt, JWT RS256, rate limiting)
- ✅ TypeScript for type safety
- ✅ React Query for server state management
- ✅ Zustand for client state management
- ✅ Tailwind CSS for consistent styling
- ✅ Responsive design considerations

### Testing Considerations
- SMS testing documented in `backend/SMS_TESTING.md`
- OAuth testing documented in `backend/OAUTH_SETUP.md`
- Unit tests structure in place (`backend/tests/`, `frontend/tests/`)
- Integration tests needed (future)
- **Test Infrastructure**: Using mocked database (no real DB needed)
  - Tests use `mock_db_session` fixture with `MagicMock`
  - Authentication dependencies mocked (`get_current_user`, `get_current_active_user`)
  - UUID to string conversion handled via field validator in schemas
- **Test Status** (as of latest run):
  - **Total Tests**: 64 tests created
  - **Passing**: 20 tests (31%)
  - **Failing**: 43 tests (67%)
  - **Errors**: 1 test (2%)
  - **Test Files Created**:
    - `test_user_endpoints.py` - User Management API tests (17 tests)
    - `test_consent_endpoints.py` - Consent Management tests (12 tests)
    - `test_auth_email_password.py` - Email/Password Auth tests (19 tests)
    - `test_auth_phone_sms.py` - Phone/SMS Auth tests (12 tests)
  - **Common Issues**: Mock setup, database operation expectations, function signature mismatches

### Performance Considerations
- Redis caching implemented for:
  - SMS rate limiting (5/hour, 10/day per phone)
  - Session storage (30-day TTL)
  - API response caching (profile: 5min, recommendations: 1hr, signals: 24hr)
  - OAuth state storage (10-minute TTL)
  - Token blacklisting
- React Query caching for API responses (frontend)
- Token refresh mechanism to minimize re-authentication
- Cache invalidation on data updates to ensure consistency

---

**End of Memory Bank**

