# SpendSense Memory Bank
## Project Knowledge Base & Progress Tracker

**Last Updated**: 2025-11-05
**Version**: 1.50
**Status**: Phase 6 - Operator Dashboard & Analytics (Task 18.3 Complete)

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
│       ├── features/   # Feature engineering (Task 5.1+)
│       │   ├── subscriptions.py  # Subscription detection (Task 5.1)
│       │   ├── savings.py        # Savings pattern detection (Task 5.2)
│       │   ├── credit.py         # Credit utilization detection (Task 5.3)
│       │   ├── income.py          # Income stability detection (Task 5.4)
│       │   ├── persona_assignment.py  # Persona assignment service (Task 6.1)
│       │   ├── example_subscriptions.py # Usage examples for subscription detection
│       │   ├── example_savings.py     # Usage examples for savings detection
│       │   ├── example_credit.py      # Usage examples for credit detection
│       │   ├── example_income.py      # Usage examples for income detection
│       │   └── example_persona_assignment.py # Usage examples for persona assignment
│       ├── recommendations/  # Recommendation generation services
│       │   ├── generator.py           # Recommendation generation (Task 7.1)
│       │   ├── rationale.py           # Rationale generation (Task 7.2)
│       │   ├── content_generator.py   # OpenAI content generation (Task 7.3)
│       │   ├── partner_offer_service.py # Partner offer service (Task 7.4)
│       │   ├── decision_trace.py      # Decision trace generation (Task 9.1)
│       │   └── example_*.py           # Usage examples
│       ├── eval/              # Evaluation services (Task 9.2, 9.3)
│       │   ├── metrics.py            # Evaluation service (Task 9.2)
│       │   ├── report.py             # Report generation service (Task 9.3)
│       │   ├── example_evaluation.py  # Usage examples for evaluation service
│       │   └── example_report.py     # Usage examples for report generation
│       └── common/     # Shared utilities
│           ├── consent_guardrails.py  # Consent guardrails service (Task 8.1)
│           ├── feature_cache.py      # Feature caching utility (Task 5.5)
│           ├── openai_client.py      # OpenAI client utilities (Task 7.3)
│           └── validator.py          # Plaid schema validator
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
- **AI/LLM Integration**: OpenAI SDK 1.12.0 (GPT-4-turbo-preview / GPT-3.5-turbo)

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
- **Charts**: Recharts (for analytics dashboard visualization)

### Infrastructure
- **Cloud Provider**: AWS
- **IaC**: Terraform
- **Region**: us-west-1
- **Services**: RDS PostgreSQL, ElastiCache Redis, S3, VPC, IAM

---

## Completed Tasks

> **Note**: Detailed task information is available in [PROJECT-PLAN.md](./PROJECT-PLAN.md). This section provides a high-level summary. Recent tasks (last 3-5) include more detail for quick reference.

### Phase 1: Foundation & Backend Core

- **Task 1.1**: Project Setup ✅ - Repository initialization, project structure (backend/frontend/service/infrastructure), dev environment
- **Task 1.2**: Database Design & Setup ✅ - PostgreSQL schema design, Alembic migrations, SQLAlchemy models (User, Session, UserProfile, Account, Transaction, Liability, etc.)
- **Task 1.3**: AWS Infrastructure Setup ✅ - Terraform modules (VPC, RDS, Redis, S3, IAM), dev environment setup with `owner_id` support

### Phase 2: Authentication & Authorization

- **Task 2.1**: Authentication Foundation ✅ - JWT RS256, bcrypt password hashing, authentication middleware, token refresh
- **Task 2.2**: Email/Password Authentication ✅ - Registration/login endpoints, user management endpoints, password validation (12+ chars), session management
- **Task 2.3**: Phone/SMS Authentication ✅ - AWS SNS integration, 6-digit verification codes, rate limiting (5/hour, 10/day), Redis storage
- **Task 2.4**: OAuth Integration ✅ - Google, GitHub, Facebook, Apple OAuth support with callback handlers
- **Task 2.5**: Account Linking ✅ - OAuth/phone linking/unlinking endpoints, account merging logic, CSRF protection
- **Task 2.6**: Authorization (RBAC) ✅ - Role-based access control (user/operator/admin), authorization dependencies, resource-level checks

### Phase 3: Core API & Data Models

- **Task 3.1**: User Management API ✅ - Profile endpoints (GET/PUT/DELETE), consent management API (grant/status/revoke), user data deletion
- **Task 3.2**: Data Upload API ✅ - File upload endpoint (JSON/CSV, max 10MB), S3 storage, upload status tracking, user ID assigned from authenticated user (not from file), unit tests (12/12 passing)
- **Task 3.3**: Caching Infrastructure ✅ - Redis session storage (30-day TTL), API response caching (profile: 5min, recommendations: 1hr, signals: 24hr), cache invalidation, unit tests (21/21 passing)
- **Task 3.4**: API Documentation ✅ - OpenAPI/Swagger documentation, request/response examples, comprehensive endpoint documentation

### Phase 2: Service Layer - Data Processing

- **Task 4.1**: Data Ingestion Service ✅ - Plaid data parser (JSON/CSV), database models (Account/Transaction/Liability), PostgreSQL + S3 Parquet storage, ingestion service with comprehensive reporting
- **Task 4.2**: Data Validation Service ✅ - Enhanced PlaidValidator with account/transaction/liability validation, duplicate detection, range validation, error reporting with severity levels
- **Task 4.3**: Synthetic Data Generator ✅ - YAML-based persona configurations (5 personas), generates diverse user profiles with accounts/transactions/liabilities, supports JSON/CSV export, validates all generated data. **Security**: Generated files do NOT include `user_id` - assigned by authenticated user during upload

#### ✅ Task 5.1: Subscription Detection
- Implemented subscription detection service (`service/app/features/subscriptions.py`)
- **SubscriptionDetector class** with methods:
  - `detect_subscriptions()` - Core detection logic for recurring merchants
  - `_analyze_merchant_pattern()` - Pattern analysis (cadence, spend)
  - `calculate_subscription_signals()` - Window-specific signal calculation
  - `generate_subscription_signals()` - Combined 30-day and 180-day signals
- **Features**:
  - Detects merchants with ≥3 transactions in 90 days (configurable)
  - Calculates cadence type: `weekly` (≤10 days) or `monthly` (≤35 days) using median gap analysis
  - Computes monthly recurring spend:
    - Weekly subscriptions: `avg_amount × 4.33`
    - Monthly subscriptions: `avg_amount`
  - Calculates subscription share: `(total_recurring_spend / total_spend) × 100`
  - Generates signals for both 30-day and 180-day windows
  - Handles Plaid transaction format (negative amounts for expenses)
  - Groups merchants by `merchant_entity_id` (preferred) or `merchant_name`
  - Filters out pending transactions
  - Uses absolute values for amount calculations
- **Output Structure**:
  - Returns structured data with:
    - Recurring merchants list (merchant name, cadence, monthly spend, transaction count)
    - Total recurring spend
    - Subscription count
    - Subscription share percentage
    - Time window metadata (start/end dates)
- **Example Usage**:
  ```python
  detector = SubscriptionDetector(db_session)
  signals = detector.generate_subscription_signals(user_id)
  # Returns signals for both 30-day and 180-day windows
  ```

**Key Files**:
- `service/app/features/__init__.py` - Feature engineering module
- `service/app/features/subscriptions.py` - Subscription detection service (280 lines)
- `service/app/features/example_subscriptions.py` - Usage examples

#### ✅ Task 5.2: Savings Pattern Detection
- Implemented savings pattern detection service (`service/app/features/savings.py`)
- **SavingsDetector class** with methods:
  - `get_savings_accounts()` - Get all savings-like accounts (savings, money market, HSA)
  - `calculate_net_inflow()` - Calculate net inflow to savings accounts
  - `calculate_savings_growth_rate()` - Compute savings growth rate
  - `calculate_emergency_fund_coverage()` - Calculate emergency fund coverage
  - `calculate_savings_signals()` - Window-specific signal calculation
  - `generate_savings_signals()` - Combined 30-day and 180-day signals
- **Features**:
  - **Net Inflow Calculation**:
    - Calculates deposits (positive amounts) and withdrawals (negative amounts) to savings-like accounts
    - Provides per-account breakdown with deposit/withdrawal counts and amounts
    - Net inflow = total deposits - total withdrawals
    - Handles Plaid transaction format (positive = deposits, negative = withdrawals)
  - **Savings Growth Rate**:
    - Computes growth rate: `(current balance - previous balance) / previous balance × 100`
    - Previous balance estimated from current balance minus transactions during period
    - Works backwards from current balance: `balance_at_start = balance_at_end - transactions_during_period`
    - Returns percentage growth rate and per-account details
  - **Emergency Fund Coverage**:
    - Calculates coverage: `savings balance / average monthly expenses`
    - Uses configurable window (default: 90 days) for expense calculation
    - Average monthly expenses = total expenses in window / (window_days / 30)
    - Returns coverage in months
    - Includes per-account breakdown
  - Generates signals for both 30-day and 180-day windows
  - Filters to only savings-like accounts: `savings`, `money market`, `hsa`
  - Filters out pending transactions
  - Handles individual accounts only (excludes business accounts)
- **Output Structure**:
  - Returns structured data with:
    - Net inflow details (deposits, withdrawals, net inflow per account)
    - Growth rate details (current balance, previous balance, growth amount, growth rate %)
    - Emergency fund coverage (savings balance, average monthly expenses, coverage months)
    - Time window metadata (start/end dates)
    - Per-account breakdowns for all metrics
- **Example Usage**:
  ```python
  detector = SavingsDetector(db_session)
  signals = detector.generate_savings_signals(user_id)
  # Returns signals for both 30-day and 180-day windows
  ```

**Key Files**:
- `service/app/features/savings.py` - Savings pattern detection service (470+ lines)
- `service/app/features/example_savings.py` - Usage examples
- `service/app/features/__init__.py` - Updated to export SavingsDetector

#### ✅ Task 5.3: Credit Utilization Detection
- Implemented credit utilization detection service (`service/app/features/credit.py`)
- **CreditUtilizationDetector class** with methods:
  - `get_credit_card_accounts()` - Get all credit card accounts for user
  - `calculate_utilization()` - Calculate utilization (balance / limit) for each card
  - `detect_minimum_payment_only()` - Detect minimum-payment-only behavior
  - `detect_interest_charges()` - Identify interest charges from transactions
  - `detect_overdue_accounts()` - Flag overdue accounts
  - `calculate_credit_signals()` - Window-specific signal calculation
  - `generate_credit_signals()` - Combined 30-day and 180-day signals
- **Features**:
  - **Utilization Calculation**:
    - Calculates utilization: `(current balance / credit limit) × 100`
    - Flags cards at thresholds: ≥30% (high), ≥50% (critical), ≥80% (severe)
    - Provides utilization level classification (low/high/critical/severe)
    - Includes per-card breakdown with APR information
  - **Minimum Payment Detection**:
    - Analyzes last 3 payments in 90-day window
    - Uses ±10% tolerance to account for rounding differences
    - Flags as minimum-payment-only if ≥2 of last 3 payments are minimum
    - Identifies payment transactions via category patterns (PAYMENT, TRANSFER)
  - **Interest Charge Detection**:
    - Identifies transactions with category "INTEREST_CHARGE" or similar patterns
    - Calculates total interest charges in window
    - Provides per-charge breakdown with dates and amounts
    - Filters to negative amounts (debits/expenses)
  - **Overdue Account Detection**:
    - Checks `liability.is_overdue` flag
    - Verifies `next_payment_due_date` is in the past
    - Provides reason for overdue status
  - Generates signals for both 30-day and 180-day windows
  - Calculates weighted average utilization across all cards
  - Categorizes cards by utilization level and behaviors
  - Filters to individual accounts only (excludes business accounts)
- **Output Structure**:
  - Returns structured data with:
    - Credit card details (utilization, balance, limit, flags)
    - Categorized lists (high/critical/severe utilization cards)
    - Minimum payment only cards
    - Cards with interest charges
    - Overdue cards
    - Total utilization (weighted average)
    - Time window metadata (start/end dates)
- **Example Usage**:
  ```python
  detector = CreditUtilizationDetector(db_session)
  signals = detector.generate_credit_signals(user_id)
  # Returns signals for both 30-day and 180-day windows
  ```

**Key Files**:
- `service/app/features/credit.py` - Credit utilization detection service (450+ lines)
- `service/app/features/example_credit.py` - Usage examples
- `service/app/features/__init__.py` - Updated to export CreditUtilizationDetector

#### ✅ Task 5.4: Income Stability Detection
- Implemented income stability detection service (`service/app/features/income.py`)
- **IncomeStabilityDetector class** with methods:
  - `get_checking_accounts()` - Get all checking accounts for user
  - `detect_payroll_deposits()` - Detect payroll ACH deposits
  - `calculate_payment_frequency()` - Calculate median time between deposits
  - `calculate_payment_variability()` - Calculate coefficient of variation
  - `calculate_cash_flow_buffer()` - Calculate cash-flow buffer in months
  - `detect_variable_income_patterns()` - Identify variable income patterns
  - `calculate_income_signals()` - Window-specific signal calculation
  - `generate_income_signals()` - Combined 30-day and 180-day signals
- **Features**:
  - **Payroll Deposit Detection**:
    - Identifies transactions with category "PAYROLL" and payment_channel "ACH"
    - Filters to positive amounts (deposits)
    - Provides per-deposit breakdown with dates and amounts
  - **Payment Frequency Calculation**:
    - Calculates median time between payroll deposits
    - Calculates average gap between deposits
    - Classifies frequency type: weekly (≤7 days), biweekly (≤18 days), monthly (≤35 days), irregular (≤45 days), variable (>45 days)
    - Provides gap days list for analysis
  - **Payment Variability Calculation**:
    - Calculates coefficient of variation: `(standard deviation / mean) × 100`
    - Classifies variability level: low (CV <5%), medium (CV 5-15%), high (CV ≥15%)
    - Provides statistical summary (mean, std dev, min, max)
  - **Cash-Flow Buffer Calculation**:
    - Calculates buffer: `(current balance - minimum balance) / average monthly expenses`
    - Estimates minimum balance from transaction history
    - Uses 90-day window for expense calculation (configurable)
    - Returns buffer in months
    - Includes per-account breakdown
  - **Variable Income Pattern Detection**:
    - Identifies variable income based on:
      - High payment variability (CV ≥15%)
      - Irregular payment frequency (median gap >45 days OR frequency_type = "variable")
      - Low cash-flow buffer (<1 month)
    - Provides confidence level (high/medium/low) based on number of indicators
    - Lists reasons for variable income classification
  - Generates signals for both 30-day and 180-day windows
  - Filters to checking accounts only (individual accounts)
  - Handles Plaid transaction format correctly
- **Output Structure**:
  - Returns structured data with:
    - Payroll deposits list (dates, amounts, account info)
    - Payment frequency details (median gap, frequency type)
    - Payment variability details (CV, variability level, statistics)
    - Cash-flow buffer details (buffer months, balances, expenses)
    - Variable income pattern detection (is_variable_income, reasons, confidence)
    - Time window metadata (start/end dates)
- **Example Usage**:
  ```python
  detector = IncomeStabilityDetector(db_session)
  signals = detector.generate_income_signals(user_id)
  # Returns signals for both 30-day and 180-day windows
  ```

**Key Files**:
- `service/app/features/income.py` - Income stability detection service (450+ lines)
- `service/app/features/example_income.py` - Usage examples
- `service/app/features/__init__.py` - Updated to export IncomeStabilityDetector

#### ✅ Task 5.5: Feature Caching
- Implemented Redis caching for computed behavioral signals (`service/app/common/feature_cache.py`)
- **Caching Utility**:
  - Created `cache_feature_signals()` decorator for automatic caching
  - Cache keys use pattern: `features:{type}:{user_id}` (e.g., `features:subscriptions:{user_id}`)
  - TTL: 24 hours (86,400 seconds) for all feature signals
  - Gracefully degrades if Redis is unavailable (returns None, continues without caching)
- **Caching Integration**:
  - Integrated caching decorator into all four feature detection services
  - Applied `@cache_feature_signals()` decorator to `generate_*_signals()` methods:
    - `SubscriptionDetector.generate_subscription_signals()`
    - `SavingsDetector.generate_savings_signals()`
    - `CreditUtilizationDetector.generate_credit_signals()`
    - `IncomeStabilityDetector.generate_income_signals()`
  - Caching is transparent - methods check cache first, compute if miss, then cache result
- **Cache Invalidation Functions**:
  - `invalidate_subscription_signals_cache(user_id)` - Invalidate subscription signals
  - `invalidate_savings_signals_cache(user_id)` - Invalidate savings signals
  - `invalidate_credit_signals_cache(user_id)` - Invalidate credit utilization signals
  - `invalidate_income_signals_cache(user_id)` - Invalidate income stability signals
  - `invalidate_all_feature_signals_cache(user_id)` - Invalidate all feature signals
  - `invalidate_feature_cache_pattern(pattern)` - Invalidate by pattern (e.g., "features:*")
- **Cache Helper Functions**:
  - `get_cached_subscription_signals(user_id, window_days)` - Get cached subscription signals
  - `get_cached_savings_signals(user_id, window_days)` - Get cached savings signals
  - `get_cached_credit_signals(user_id, window_days)` - Get cached credit signals
  - `get_cached_income_signals(user_id, window_days)` - Get cached income signals
- **Cache Invalidation Strategy**:
  - Can be called when new transaction/account data is uploaded
  - Should be called when data is updated to ensure fresh signals
  - Invalidates both 30-day and 180-day window caches
  - Uses Redis DELETE for immediate invalidation
- **Performance Benefits**:
  - Avoids recomputing expensive feature calculations
  - Reduces database query load
  - Improves response times for repeated requests
  - Cache hit logs help monitor cache effectiveness

**Key Files**:
- `service/app/common/feature_cache.py` - Feature caching utility (300+ lines)
- `service/app/features/subscriptions.py` - Updated with caching decorator
- `service/app/features/savings.py` - Updated with caching decorator
- `service/app/features/credit.py` - Updated with caching decorator
- `service/app/features/income.py` - Updated with caching decorator

#### ✅ Task 6.1: Persona Assignment Logic
- Implemented persona assignment service (`service/app/features/persona_assignment.py`)
- **PersonaAssignmentService class** with methods:
  - `check_persona_1_high_utilization()` - Checks High Utilization criteria
  - `check_persona_2_variable_income()` - Checks Variable Income Budgeter criteria
  - `check_persona_3_subscription_heavy()` - Checks Subscription-Heavy criteria
  - `check_persona_4_savings_builder()` - Checks Savings Builder criteria
  - `assign_persona()` - Main assignment method with priority logic
- **Priority Logic**:
  - Applies priority-based assignment: Persona 1 > 2 > 3 > 4 > 5
  - Checks personas in order, assigns first matching persona
  - Persona 5 (Custom) is default fallback when no other persona matches
- **Persona Criteria**:
  - **Persona 1: High Utilization**
    - Any card utilization ≥50% OR
    - Interest charges > 0 OR
    - Minimum-payment-only behavior OR
    - is_overdue = true
  - **Persona 2: Variable Income Budgeter**
    - Median pay gap > 45 days AND
    - Cash-flow buffer < 1 month
  - **Persona 3: Subscription-Heavy**
    - Recurring merchants ≥3 AND
    - (Monthly recurring spend ≥$50 in 30d OR subscription spend share ≥10%)
  - **Persona 4: Savings Builder**
    - (Savings growth rate ≥2% over window OR net savings inflow ≥$200/month) AND
    - All card utilizations < 30%
  - **Persona 5: Custom Persona**
    - Default fallback when no other persona matches
- **Features**:
  - Automatically generates signals if not provided (calls all 4 feature detectors)
  - Stores persona assignments in `UserProfile` table:
    - `persona_id` (1-5)
    - `persona_name` (persona name string)
    - `signals_30d` (JSON with all 30-day signals)
    - `signals_180d` (JSON with all 180-day signals)
  - Tracks persona history in `PersonaHistory` table:
    - Creates history entry when persona changes
    - Stores timestamp (`assigned_at`)
    - Stores signals snapshot at assignment time
  - Generates persona rationale explaining why persona was assigned:
    - Cites specific data points (card names, amounts, percentages)
    - Plain language explanations
    - Multiple reasons if applicable
  - Detects persona changes and creates history entries
  - Updates existing profile or creates new profile as needed
- **Signal Integration**:
  - Uses signals from all 4 feature detection services:
    - Subscription signals (from `SubscriptionDetector`)
    - Savings signals (from `SavingsDetector`)
    - Credit signals (from `CreditUtilizationDetector`)
    - Income signals (from `IncomeStabilityDetector`)
  - Works with both 30-day and 180-day window signals
  - Uses appropriate window for each persona check
- **Output Structure**:
  - Returns dictionary with:
    - `user_id` (string UUID)
    - `persona_id` (integer 1-5)
    - `persona_name` (string)
    - `rationale` (string explaining assignment)
    - `persona_changed` (boolean indicating if persona changed)
    - `assigned_at` (ISO timestamp)
- **Example Usage**:
  ```python
  service = PersonaAssignmentService(db_session)
  result = service.assign_persona(user_id)
  # Returns persona assignment with rationale
  ```

**Key Files**:
- `service/app/features/persona_assignment.py` - Persona assignment service (450+ lines)
- `service/app/features/example_persona_assignment.py` - Usage examples
- `service/app/features/__init__.py` - Updated to export PersonaAssignmentService
- `docs/service/ADDITIONAL_PERSONAS.md` - Document with 7 additional persona suggestions

#### ✅ Task 7.1: Recommendation Engine Foundation
- Implemented recommendation generation service (`service/app/recommendations/generator.py`)
- **RecommendationGenerator class** with methods:
  - `get_user_profile()` - Get user profile with persona assignment
  - `get_user_accounts()` - Get user accounts to check for existing products
  - `check_existing_products()` - Check what products user already has (credit cards, savings accounts)
  - `select_education_items()` - Select 3-5 education items matching persona
  - `select_partner_offers()` - Select 1-3 partner offers matching persona and eligibility
  - `generate_recommendations()` - Main method to generate all recommendations
- **Education Item Catalog** (`service/app/recommendations/catalog.py`):
  - 14 pre-defined education items
  - Persona-specific matching (each item has `matching_personas` list)
  - Covers all 5 personas with multiple items per persona
  - Includes titles, content, and categories
- **Partner Offer Catalog** (`service/app/recommendations/catalog.py`):
  - 6 pre-defined partner offers
  - Persona-specific matching
  - Includes eligibility requirements (minimum income, credit score)
  - Types: balance transfer cards, high-yield savings, budgeting apps, subscription management tools
- **Features**:
  - Selects 3-5 education items per user (based on persona)
  - Selects 1-3 partner offers per user (based on persona and eligibility)
  - Checks existing products to avoid duplicate offers
  - Generates basic rationales using detected signals (now uses RationaleGenerator)
  - Stores recommendations in database with `PENDING` status
  - Disclaimer shown once during consent flow (not on every recommendation)
  - Generates decision traces with persona, signals, and selection logic
  - Works with both 30-day and 180-day window signals
- **Recommendation Types**:
  - `education` - Educational content (articles, guides, calculators)
  - `partner_offer` - Partner financial products (credit cards, savings accounts, apps)
- **Recommendation Status**:
  - `pending` - Awaiting operator review
  - `approved` - Ready for user viewing
  - `rejected` - Not approved for user viewing
- **Output Structure**:
  - Returns dictionary with:
    - `user_id` (string UUID)
    - `recommendations` (list of recommendation summaries)
    - `education_count` (number of education items)
    - `partner_offer_count` (number of partner offers)
- **Example Usage**:
  ```python
  generator = RecommendationGenerator(db_session)
  result = generator.generate_recommendations(user_id)
  # Returns recommendations with education and partner offers
  ```

**Key Files**:
- `service/app/recommendations/generator.py` - Recommendation generation service (470+ lines)
- `service/app/recommendations/catalog.py` - Education and partner offer catalogs
- `service/app/recommendations/example_recommendations.py` - Usage examples
- `service/app/recommendations/__init__.py` - Module exports

#### ✅ Task 7.4: Partner Offer Service
- Created comprehensive PartnerOfferService (`service/app/recommendations/partner_offer_service.py`)
- **PartnerOfferService class** with methods:
  - `get_user_accounts()` - Get user accounts to check for existing products
  - `check_existing_products()` - Check what products user already has (credit cards, savings accounts, high-yield savings)
  - `calculate_income_from_transactions()` - Calculate estimated monthly income from payroll deposits
  - `estimate_credit_score()` - Estimate credit score based on utilization and payment behavior
  - `is_harmful_product()` - Check if offer is harmful (payday loans, predatory loans, etc.)
  - `check_eligibility()` - Check if user is eligible for a partner offer
  - `select_eligible_offers()` - Select eligible partner offers for a user
- **Income Calculation**:
  - Analyzes payroll deposits from checking accounts over last 6 months (configurable)
  - Filters transactions with category "PAYROLL" and payment_channel "ACH"
  - Calculates average monthly income: `total_deposits / months_covered`
  - Returns None if no payroll deposits found (graceful degradation)
  - Logs income calculation for debugging
- **Credit Score Estimation**:
  - Estimates credit score (300-850 range) based on credit utilization and payment behavior
  - Base score starts at 650 (average)
  - Adjusts based on:
    - Severe utilization (≥80%): -80 points
    - Critical utilization (≥50%): -50 points
    - High utilization (≥30%): -20 points
    - Interest charges: -30 points
    - Minimum payment only: -20 points
    - Overdue accounts: -100 points (significant negative impact)
  - Clamps score to valid range (300-850)
  - Returns None if no credit signals available (graceful degradation)
  - Note: This is a rough estimate, not a replacement for actual credit score (production would integrate with credit bureau API)
- **Harmful Product Filtering**:
  - Filters out offers containing harmful keywords:
    - "payday loan", "payday"
    - "predatory loan"
    - "title loan"
    - "cash advance"
    - "check cashing"
    - "pawn shop"
    - "rent-to-own"
  - Checks both title and content for harmful keywords
  - Logs warnings when harmful products detected
  - Returns False if offer is harmful
- **Eligibility Checking**:
  - **Credit Score Validation**:
    - Checks minimum credit score requirements
    - Returns False with explanation if score below requirement
    - Handles missing credit score gracefully with explanation
  - **Income Validation**:
    - Checks minimum income requirements
    - Returns False with explanation if income below requirement
    - Handles missing income gracefully with explanation
  - **Existing Product Filtering**:
    - Checks `blocked_if` conditions (blocks offers if user has specific products)
    - Checks `existing_products` requirements (requires user to have specific products)
    - Filters out duplicate offers (e.g., don't offer high-yield savings if user already has one)
  - **Eligibility Explanations**:
    - Generates human-readable explanations for each offer
    - Includes status indicators (✓/✗) for each eligibility check
    - Explains why offer is eligible or not eligible
    - Format: "Credit score check: ✓ (720 ≥ 670) | Income check: ✓ ($4,500.00 ≥ $3,000.00)"
- **Offer Selection**:
  - Filters offers for matching persona (with fallback to Persona 5 general offers)
  - Checks eligibility for each offer
  - Returns only eligible offers (filters out ineligible ones)
  - Selects top N offers (default: 3, configurable)
  - Ensures at least 1 offer if any are available
  - Adds eligibility information to each offer:
    - `eligibility_status` ("eligible")
    - `eligibility_explanation` (human-readable explanation)
    - `estimated_income` (calculated monthly income)
    - `estimated_credit_score` (estimated credit score)
- **Integration**:
  - Updated `RecommendationGenerator` to use `PartnerOfferService`
  - Updated `select_partner_offers()` method to use new service
  - Enhanced decision traces with eligibility information:
    - `eligibility_status` - Whether offer is eligible
    - `eligibility_explanation` - Human-readable explanation
    - `estimated_income` - Estimated monthly income
    - `estimated_credit_score` - Estimated credit score
  - Partner offers now include comprehensive eligibility information
- **Features**:
  - Persona-based matching (filters offers for user's assigned persona)
  - Fallback to general offers (Persona 5) if not enough persona-specific offers
  - Comprehensive eligibility checking (credit score, income, existing products)
  - Harmful product filtering (protects users from predatory products)
  - Graceful degradation (handles missing data with clear explanations)
  - Human-readable eligibility explanations (helps users understand why offers are shown)
  - Logging for debugging and monitoring
- **Example Usage**:
  ```python
  service = PartnerOfferService(db_session)

  # Select eligible offers
  eligible_offers = service.select_eligible_offers(
      persona_id=1,
      user_id=user_id,
      signals_30d=signals_30d,
      signals_180d=signals_180d,
      count=3
  )

  # Check specific offer eligibility
  is_eligible, explanation = service.check_eligibility(
      offer,
      user_id,
      existing_products,
      estimated_income,
      estimated_credit_score
  )
  ```

**Key Files**:
- `service/app/recommendations/partner_offer_service.py` - Partner offer service (500+ lines)
- `service/app/recommendations/example_partner_offers.py` - Usage examples
- `service/app/recommendations/generator.py` - Updated to use PartnerOfferService
- `service/app/recommendations/catalog.py` - Partner offer catalog (already existed)

#### ✅ Task 8.1: Consent Guardrails
- Created comprehensive consent guardrails service (`service/app/common/consent_guardrails.py`)
- **ConsentGuardrails class** with methods:
  - `get_user_consent_status()` - Get user consent status from database (returns True/False/None)
  - `check_consent()` - Check consent with optional exception raising (returns bool)
  - `require_consent()` - Require consent and raise ConsentError if not granted
  - `log_consent_check()` - Log consent check events with user ID, operation, and timestamp
- **Custom Exception**:
  - `ConsentError` - Exception raised when consent check fails (with descriptive error message)
- **Features**:
  - **Consent Checking**: Checks user consent status before any data processing operation
  - **Logging**: All consent checks are logged with user ID, operation description, and timestamp
  - **Flexible API**: Can check consent without raising exception (returns bool) or require consent (raises exception)
  - **Database Integration**: Queries User model directly to get consent status
  - **Error Handling**: Gracefully handles missing users (returns None) and logs warnings
- **Integration Points**:
  - **Feature Detection Services**:
    - `SubscriptionDetector.generate_subscription_signals()` - Checks consent before generating subscription signals
    - `SavingsDetector.generate_savings_signals()` - Checks consent before generating savings signals
    - `CreditUtilizationDetector.generate_credit_signals()` - Checks consent before generating credit signals
    - `IncomeStabilityDetector.generate_income_signals()` - Checks consent before generating income signals
    - All feature detection services raise `ConsentError` if consent not granted
  - **Persona Assignment Service**:
    - `PersonaAssignmentService.assign_persona()` - Checks consent before assigning personas
    - Raises `ConsentError` if consent not granted
  - **Recommendation Generation Service**:
    - `RecommendationGenerator.generate_recommendations()` - Checks consent before generating recommendations
    - Returns error response with `consent_required: True` if consent not granted (doesn't raise exception)
    - Error response includes user-friendly message: "Consent is required for recommendation generation. Please grant consent first."
- **Consent Check Operations**:
  - Operations are logged with descriptive names:
    - `"feature_detection:subscriptions"` - Subscription signal generation
    - `"feature_detection:savings"` - Savings signal generation
    - `"feature_detection:credit"` - Credit signal generation
    - `"feature_detection:income"` - Income signal generation
    - `"persona_assignment"` - Persona assignment
    - `"recommendation_generation"` - Recommendation generation
- **Logging**:
  - Consent checks logged at INFO level when consent granted
  - Consent checks logged at WARNING level when consent not granted
  - All logs include user ID and operation description for audit trail
- **Data Deletion Support**:
  - Data deletion on consent revocation already implemented in backend (Task 3.1)
  - Backend endpoint `DELETE /api/v1/consent` supports optional data deletion
  - When consent is revoked with `delete_data=True`, all user data is deleted:
    - DataUpload records
    - Recommendation records
    - UserProfile records
    - PersonaHistory records
- **Example Usage**:
  ```python
  # Initialize consent guardrails
  guardrails = ConsentGuardrails(db_session)

  # Check consent status
  consent_status = guardrails.get_user_consent_status(user_id)

  # Require consent (raises exception if not granted)
  guardrails.require_consent(user_id, "feature_detection:subscriptions")

  # Check consent without raising exception
  if guardrails.check_consent(user_id, "recommendation_generation", raise_on_failure=False):
      # Process data
      pass
  else:
      # Handle consent not granted
      pass
  ```

**Key Files**:
- `service/app/common/consent_guardrails.py` - Consent guardrails service (200+ lines)
- `service/app/common/example_consent_guardrails.py` - Usage examples demonstrating consent checking workflows
- `service/app/common/__init__.py` - Updated to export ConsentGuardrails and ConsentError
- `service/app/features/subscriptions.py` - Updated with consent checks
- `service/app/features/savings.py` - Updated with consent checks
- `service/app/features/credit.py` - Updated with consent checks
- `service/app/features/income.py` - Updated with consent checks
- `service/app/features/persona_assignment.py` - Updated with consent checks
- `service/app/recommendations/generator.py` - Updated with consent checks

#### ✅ Task 8.2: Eligibility Validation
- Created comprehensive eligibility guardrails service (`service/app/common/eligibility_guardrails.py`)
- **EligibilityGuardrails class** with methods:
  - `check_existing_products()` - Check what products user already has (credit cards, savings, high-yield savings)
  - `calculate_income_from_transactions()` - Calculate estimated monthly income from payroll deposits (last 6 months)
  - `estimate_credit_score()` - Estimate credit score based on utilization, interest charges, payment behavior, and overdue accounts (300-850 range)
  - `is_harmful_product()` - Check for harmful product keywords (payday loans, predatory loans, title loans, cash advances, check cashing, pawn shops, rent-to-own)
  - `check_eligibility()` - Comprehensive eligibility check with income, credit score, existing products, and harmful product filtering
  - `require_eligibility()` - Require eligibility and raise EligibilityError if not eligible
  - `log_eligibility_check()` - Log eligibility check events with user ID, recommendation ID, eligibility status, and explanation
- **Custom Exception**:
  - `EligibilityError` - Exception raised when eligibility check fails (with descriptive error message)
- **Features**:
  - **Income Calculation**: Analyzes payroll deposits from checking accounts over last 6 months (configurable)
  - **Credit Score Estimation**: Estimates credit score based on credit utilization, interest charges, payment behavior, and overdue accounts (base score 650, adjusted based on utilization and payment history)
  - **Product Filtering**: Checks existing products to avoid duplicate offers (e.g., don't offer high-yield savings if user already has one)
  - **Harmful Product Filtering**: Blocks payday loans, predatory loans, title loans, cash advances, check cashing, pawn shops, rent-to-own
  - **Eligibility Explanations**: Generates human-readable explanations for each eligibility check with status indicators (✓/✗)
  - **Graceful Degradation**: Handles missing data (income/credit score) with clear explanations
- **Integration Points**:
  - **RecommendationGenerator**: Integrated eligibility checks to filter both education items and partner offers before generating recommendations
  - All eligibility checks are logged with user ID, recommendation ID, eligibility status, and explanation
  - Recommendations are filtered if not eligible (harmful products, insufficient income/credit score, duplicate products)
- **Eligibility Requirements**:
  - Checks minimum income requirements (from partner offer config)
  - Checks minimum credit score requirements (from partner offer config)
  - Filters offers for products user already has (checks `blocked_if` conditions)
  - Blocks harmful products (checks title and content for harmful keywords)
- **Example Usage**:
  ```python
  # Initialize eligibility guardrails
  guardrails = EligibilityGuardrails(db_session)

  # Check eligibility for a recommendation
  is_eligible, explanation = guardrails.check_eligibility(
      recommendation,
      user_id,
      signals_30d,
      signals_180d,
      raise_on_failure=False,
  )

  # Require eligibility (raises exception if not eligible)
  guardrails.require_eligibility(
      recommendation,
      user_id,
      signals_30d,
      signals_180d,
  )
  ```

**Key Files**:
- `service/app/common/eligibility_guardrails.py` - Eligibility guardrails service (460+ lines)
- `service/app/common/example_eligibility_guardrails.py` - Usage examples demonstrating eligibility checking workflows
- `service/app/common/__init__.py` - Updated to export EligibilityGuardrails and EligibilityError
- `service/app/recommendations/generator.py` - Updated with eligibility checks

#### ✅ Task 8.3: Tone Validation
- Created comprehensive tone validation guardrails service (`service/app/common/tone_validation_guardrails.py`)
- **ToneValidationGuardrails class** with methods:
  - `check_shaming_keywords()` - Check for shaming/judgmental keywords ("overspending", "irresponsible", "wasteful", "bad with money", "terrible", "awful", etc.)
  - `check_empowering_keywords()` - Check for empowering keywords ("opportunity", "improve", "potential", "you can", "help you", "support", "achieve", etc.)
  - `validate_tone_keyword_based()` - Keyword-based tone validation with fallback
  - `validate_tone_openai()` - Uses OpenAI API for tone scoring (0-10 scale, where 10 is empowering)
  - `validate_tone()` - Comprehensive tone validation with keyword checks and optional OpenAI scoring (requires score >= 7.0)
  - `require_appropriate_tone()` - Require appropriate tone and raise ToneError if invalid
  - `log_tone_validation()` - Log tone validation events with user ID, recommendation ID, validation status, explanation, and tone score
- **Custom Exception**:
  - `ToneError` - Exception raised when tone validation fails (with descriptive error message)
- **Features**:
  - **Shaming Language Detection**: Checks for shaming/judgmental keywords using word boundaries for accurate matching
  - **Empowering Language Detection**: Checks for empowering keywords to validate positive tone
  - **OpenAI Integration**: Uses OpenAI API for tone scoring (0-10 scale) when available (optional, with fallback to keyword-based checks)
  - **Minimum Score Threshold**: Requires tone score >= 7.0 for OpenAI-based validation
  - **Immediate Failure**: Blocks recommendations with shaming language immediately (doesn't require OpenAI)
  - **Graceful Degradation**: Falls back to keyword-based validation if OpenAI unavailable
  - **Comprehensive Logging**: All tone validation checks are logged with user ID, recommendation ID, validation status, explanation, and tone score
- **Shaming Keywords**:
  - Includes: "overspending", "irresponsible", "wasteful", "bad with money", "terrible", "awful", "should be ashamed", "you're wasting", "stupid", "dumb", "foolish", "you're failing", "poor choices", "bad choices", "you're wrong", etc.
- **Empowering Keywords**:
  - Includes: "opportunity", "improve", "potential", "you can", "help you", "support", "achieve", "reach your goals", "build", "grow", "strengthen", "optimize", "enhance", "progress", "advance", "success", "empower", "enable", "guide", "strategies", "tips", "steps", etc.
- **Integration Points**:
  - **RecommendationGenerator**: Integrated tone validation to validate both content and rationale for education items and partner offers before storing recommendations
  - Tone validation uses OpenAI if available (with fallback to keyword-based checks)
  - Blocks recommendations with shaming language immediately
  - Enforces empowering tone (score >= 7.0 for OpenAI-based validation)
  - Tone scores are stored in decision traces for both education items and partner offers
  - Warnings are logged when tone validation fails but recommendations are still generated (graceful degradation)
- **Validation Flow**:
  1. First checks for shaming keywords (immediate failure if found)
  2. Tries OpenAI validation if available (scores 0-10, requires >= 7.0)
  3. Falls back to keyword-based validation if OpenAI unavailable
  4. Logs all validation results with explanations
- **Example Usage**:
  ```python
  # Initialize tone validation guardrails
  guardrails = ToneValidationGuardrails(db_session, use_openai=True)

  # Check tone for text
  is_valid, explanation, score = guardrails.validate_tone(
      text,
      user_id,
      recommendation_id,
      raise_on_failure=False,
  )

  # Require appropriate tone (raises exception if invalid)
  guardrails.require_appropriate_tone(
      text,
      user_id,
      recommendation_id,
  )
  ```

**Key Files**:
- `service/app/common/tone_validation_guardrails.py` - Tone validation guardrails service (360+ lines)
- `service/app/common/example_tone_validation_guardrails.py` - Usage examples demonstrating tone validation workflows
- `service/app/common/__init__.py` - Updated to export ToneValidationGuardrails and ToneError
- `service/app/recommendations/generator.py` - Updated with tone validation checks
- `service/app/common/openai_client.py` - OpenAI client with tone validation method

#### ✅ Task 9.1: Decision Trace Generation
- Created comprehensive decision trace generation service (`service/app/recommendations/decision_trace.py`)
- **DecisionTraceGenerator class** with methods:
  - `create_decision_trace()` - Creates comprehensive decision trace with all required fields
  - `create_persona_assignment_info()` - Creates persona assignment information with criteria_met, priority, rationale
  - `create_guardrails_info()` - Creates guardrails information with consent, eligibility, tone, disclaimer checks
  - `generate_human_readable_trace()` - Generates Markdown or HTML formatted decision traces
  - `_generate_markdown_trace()` - Generates Markdown-formatted decision trace
  - `_generate_html_trace()` - Generates HTML-formatted decision trace (basic)
  - `_format_signal_summary()` - Formats signal summaries for display
- **Decision Trace Structure**:
  - **Metadata**: recommendation_id, user_id, timestamp
  - **Detected Signals**: Complete signals for subscriptions, savings, credit, and income for both 30-day and 180-day windows
  - **Persona Assignment**: persona_id, persona_name, criteria_met (list of criteria that were met), priority, rationale, persona_changed flag
  - **Guardrails Checks**:
    - Consent: status and timestamp
    - Eligibility: status, explanation, details (income, credit score, existing products)
    - Tone: validation status, score (0-10), explanation
    - Disclaimer: presence and text
  - **Recommendation Details**: type, title, content_preview, rationale_preview
  - **Performance**: generation_time_ms (time taken to generate recommendation)
- **Integration**:
  - Updated `RecommendationGenerator` to use `DecisionTraceGenerator`
  - Integrated decision trace generation into recommendation creation flow
  - Tracks generation time per recommendation (from start to finish)
  - Extracts persona assignment info with criteria_met from signals using `_extract_persona_assignment_info()` method
  - Creates comprehensive decision traces for all recommendations (education and partner offers)
  - Stores decision traces in database JSON column (`recommendation.decision_trace`)
  - Decision traces are automatically generated and stored when recommendations are created
- **Human-Readable Format**:
  - **Markdown Format**: Comprehensive Markdown-formatted decision traces with sections:
    - Header with recommendation ID, user ID, timestamp
    - Persona Assignment section (persona name, priority, rationale, criteria met)
    - Detected Behavioral Signals section (subscriptions, savings, credit, income for 30d/180d with formatted summaries)
    - Guardrails Checks section (consent, eligibility, tone, disclaimer with status indicators)
    - Recommendation Details section (type, title, rationale preview)
    - Performance section (generation time)
  - **HTML Format**: Basic HTML conversion from Markdown (simplified)
  - Signal summaries formatted with relevant metrics (e.g., subscription count, recurring spend, utilization percentages, cash flow buffer)
- **Persona Assignment Info Extraction**:
  - Extracts criteria_met from signals based on persona:
    - Persona 1 (High Utilization): Credit card utilization ≥50%, interest charges, minimum-payment-only, overdue accounts
    - Persona 2 (Variable Income): Median pay gap > 45 days, cash-flow buffer < 1 month
    - Persona 3 (Subscription-Heavy): Recurring merchants ≥3, monthly recurring spend ≥$50, subscription share ≥10%
    - Persona 4 (Savings Builder): Savings growth rate ≥2%, net savings inflow ≥$200/month, all utilizations < 30%
    - Persona 5 (Custom): Default fallback
  - Maps persona IDs to priorities (1-5)
  - Generates rationale based on detected signals
- **Guardrails Integration**:
  - Consent: Records consent status and check timestamp
  - Eligibility: Records eligibility status, explanation, and details (estimated income, credit score, eligibility requirements, existing products)
  - Tone: Records tone validation status, score (0-10), and explanation
  - Disclaimer: Records disclaimer presence and text
  - All guardrails checks are logged in decision traces for audit purposes
- **Features**:
  - Complete decision trace structure per PRD specifications (TR-SV-009)
  - Stores decision traces for all recommendations automatically
  - Includes detected signals (30d and 180d windows)
  - Includes persona assignment logic with criteria_met
  - Includes all guardrails checks performed
  - Includes generation performance metrics
  - Generates human-readable Markdown traces
  - Supports HTML export format (basic)
  - Example usage file demonstrates decision trace creation
- **Example Usage**:
  ```python
  # Initialize decision trace generator
  trace_generator = DecisionTraceGenerator()

  # Create decision trace
  decision_trace = trace_generator.create_decision_trace(
      user_id=user_id,
      recommendation_id=recommendation_id,
      recommendation_type="education",
      persona_id=persona_id,
      persona_name=persona_name,
      persona_assignment_info=persona_assignment_info,
      signals_30d=signals_30d,
      signals_180d=signals_180d,
      guardrails=guardrails_info,
      generation_time_ms=2450.5,
      recommendation_metadata={"title": "...", "content_preview": "...", "rationale_preview": "..."},
  )

  # Generate human-readable trace
  markdown_trace = trace_generator.generate_human_readable_trace(decision_trace, format="markdown")
  ```

**Key Files**:
- `service/app/recommendations/decision_trace.py` - Decision trace generation service (550+ lines)
- `service/app/recommendations/example_decision_trace.py` - Usage examples
- `service/app/recommendations/generator.py` - Updated to use DecisionTraceGenerator
- `service/app/recommendations/__init__.py` - Updated to export DecisionTraceGenerator

#### ✅ Task 9.2: Evaluation Service
- Created comprehensive evaluation service (`service/app/eval/metrics.py`) for calculating system performance and fairness metrics
- **EvaluationService class** with methods:
  - `calculate_coverage_metrics()` - Calculates coverage metrics (% users with persona, ≥3 behaviors, both)
  - `calculate_explainability_metrics()` - Calculates explainability metrics (% rationales, data points, quality score)
  - `calculate_relevance_metrics()` - Calculates relevance metrics (education-persona fit, partner offer-persona fit)
  - `calculate_latency_metrics()` - Calculates latency metrics (p50/p95/p99, mean/min/max, % within 5s target)
  - `calculate_fairness_metrics()` - Calculates fairness metrics (persona distribution, balance score, signal detection)
  - `calculate_all_metrics()` - Calculates all metrics in one call
  - `_count_behaviors()` - Helper to count behaviors from signals (subscriptions, savings, credit, income)
  - `_rationale_has_data_points()` - Helper to check if rationale cites data points
  - `_calculate_rationale_quality()` - Helper to calculate rationale quality score (0-10)
  - `_check_education_persona_fit()` - Helper to check education-persona fit
  - `_check_partner_offer_persona_fit()` - Helper to check partner offer-persona fit
- **Coverage Metrics**:
  - **Users with Persona**: Counts users with assigned persona (via UserProfile join)
  - **Users with ≥3 Behaviors**: Counts behaviors from signals (subscriptions, savings, credit, income)
  - **Users with Both**: Counts users with both persona and ≥3 behaviors
  - Calculates percentages for all metrics
  - Filters to regular users only (excludes operators and admins)
- **UI Separation**: Operators and admins are displayed separately from regular users:
  - `UsersList.tsx` component filters out operators/admins (shows only role='user')
  - `StaffList.tsx` component displays only operators and admins
  - `StaffManagement.tsx` page provides tabbed interface for managing both groups
  - Navigation hides Profile, Recommendations, and Upload tabs for operators/admins
  - Admins see "Management" link in navigation for staff management
- **Explainability Metrics**:
  - **Recommendations with Rationales**: Checks if rationale exists and is not empty
  - **Rationales with Data Points**: Detects citations of:
    - Account numbers ("ending in", "last 4 digits")
    - Currency amounts ($X,XXX.XX)
    - Percentages (%)
    - Dates (month names)
    - Number patterns (e.g., "3 subscriptions", "5 cards")
  - **Rationale Quality Score** (0-10):
    - Length score (0-3 points): longer is better up to a point
    - Data point citations (0-4 points): presence of citations
    - Plain language check (0-3 points): avoids jargon
- **Relevance Metrics**:
  - **Education-Persona Fit**: Validates persona matching via decision traces
  - **Partner Offer-Persona Fit**: Validates persona matching via decision traces
  - Checks if recommendation's decision trace persona matches user's assigned persona
  - Calculates percentages for both education items and partner offers
- **Latency Metrics**:
  - Extracts latency from `decision_trace.generation_time_ms`
  - Calculates percentiles (p50, p95, p99) with interpolation method
  - Calculates mean, min, max latency
  - Counts recommendations within 5-second target (5000ms)
  - Calculates percentage within target
- **Fairness Metrics**:
  - **Persona Distribution**: Analyzes distribution of recommendations and users across personas
  - **Persona Balance Score** (0-1): Measures distribution evenness (lower variance = more balanced)
  - **Signal Detection by Persona**: Calculates average behaviors detected per persona
  - Calculates recommendations and users percentages per persona
  - Note: Full demographic parity requires demographic data in user model (not in MVP)
- **Features**:
  - Complete metrics calculation per PRD specifications (FR-SV-010, TR-SV-008)
  - All metrics calculated from database queries
  - Handles empty data gracefully (returns 0.0 for percentages when no data)
  - Provides both counts and percentages for all metrics
  - Combined `calculate_all_metrics()` method for convenience
  - Individual metric methods for selective calculation
- **Example Usage**:
  ```python
  # Initialize evaluation service
  eval_service = EvaluationService(db_session)

  # Calculate all metrics
  all_metrics = eval_service.calculate_all_metrics()

  # Or calculate individual metrics
  coverage = eval_service.calculate_coverage_metrics()
  explainability = eval_service.calculate_explainability_metrics()
  relevance = eval_service.calculate_relevance_metrics()
  latency = eval_service.calculate_latency_metrics()
  fairness = eval_service.calculate_fairness_metrics()
  ```

**Key Files**:
- `service/app/eval/metrics.py` - Evaluation service (600+ lines)
- `service/app/eval/__init__.py` - Module exports
- `service/app/eval/example_evaluation.py` - Usage examples

#### ✅ Task 9.3: Report Generation
- Created comprehensive report generation service (`service/app/eval/report.py`) for exporting evaluation metrics and decision traces
- **ReportGenerator class** with methods:
  - `generate_metrics_json()` - Exports all evaluation metrics as JSON with timestamped filename
  - `generate_metrics_csv()` - Exports flattened metrics as CSV with columns: metric_category, metric_name, value, count, total
  - `generate_summary_report()` - Generates 1-2 page Markdown report with executive summary, detailed metrics, tables, and recommendations
  - `generate_user_decision_traces()` - Generates per-user decision traces in JSON or Markdown format
  - `generate_all_reports()` - Generates all reports in one call with configurable options
  - `_save_user_traces()` - Helper method to save traces for a single user
- **JSON Metrics Export**:
  - Includes all metrics from EvaluationService with nested structure
  - Uses timestamped filenames (metrics_{timestamp}.json)
  - Pretty-printed JSON with 2-space indentation
  - Handles UUID serialization and datetime formatting
- **CSV Metrics Export**:
  - Flattens metrics into tabular format suitable for spreadsheet analysis
  - Includes all metric categories (coverage, explainability, relevance, latency, fairness)
  - Includes persona distribution data (recommendations and users per persona)
  - Includes signal detection by persona data
  - Columns: metric_category, metric_name, value, count, total
- **Summary Report**:
  - Markdown format with sections:
    - Executive Summary with key metrics
    - Coverage Metrics (users with persona, ≥3 behaviors, both)
    - Explainability Metrics (rationales, data points, quality score)
    - Relevance Metrics (education-persona fit, partner offer-persona fit)
    - Latency Metrics (p50/p95/p99, mean/min/max, % within 5s target)
    - Fairness Metrics (persona distribution table, signal detection table)
    - Recommendations section highlighting areas for improvement
  - Includes target comparisons (e.g., coverage target 100%, relevance target ≥80%)
  - Automatically identifies areas that don't meet targets
  - Uses tables for persona distribution and signal detection
- **Decision Traces Export**:
  - Supports JSON (structured) and Markdown (human-readable) formats
  - Supports combined file (all users) or per-user files
  - Uses DecisionTraceGenerator for human-readable formatting
  - Filters by user ID option
  - Timestamped filenames (decision_traces_{user_id}_{timestamp}.{format})
  - Markdown format includes all trace sections (persona assignment, signals, guardrails, etc.)
- **Features**:
  - Configurable output directory (default: current directory)
  - Automatic directory creation if it doesn't exist
  - Timestamped filenames to avoid overwrites
  - Integration with EvaluationService for metrics calculation
  - Integration with DecisionTraceGenerator for trace formatting
  - Graceful handling of empty data
  - Comprehensive logging for all operations
- **Example Usage**:
  ```python
  # Initialize report generator
  report_generator = ReportGenerator(db_session, output_dir='./reports')

  # Generate individual reports
  json_file = report_generator.generate_metrics_json()
  csv_file = report_generator.generate_metrics_csv()
  summary_file = report_generator.generate_summary_report()
  traces_file = report_generator.generate_user_decision_traces(combined=True)

  # Or generate all at once
  all_reports = report_generator.generate_all_reports(
      include_json=True,
      include_csv=True,
      include_summary=True,
      include_traces=True,
      traces_format='json',
      traces_combined=True,
  )
  ```

**Key Files**:
- `service/app/eval/report.py` - Report generation service (590+ lines)
- `service/app/eval/__init__.py` - Updated to export ReportGenerator
- `service/app/eval/example_report.py` - Usage examples for report generation

#### ✅ Task 8.4: Regulatory Disclaimers
- Implemented financial advice disclaimer in consent flow instead of on every recommendation
- **Frontend Implementation**:
  - Created `consentService` (`frontend/src/services/consentService.ts`) with API methods:
    - `getConsentStatus()` - Get current user's consent status
    - `grantConsent()` - Grant consent for data processing
    - `revokeConsent()` - Revoke consent (with optional data deletion)
  - Created `ConsentManagement` component (`frontend/src/components/ConsentManagement.tsx`):
    - Prominent disclaimer display (blue highlighted box with info icon)
    - Disclaimer text: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
    - Disclaimer shown prominently when consent is not granted
    - Full consent management UI with grant/revoke functionality
    - Loading states, error handling, and confirmation dialogs
    - Revoke confirmation with optional data deletion
    - Consent status display with color-coded badges
    - Consent version and timestamp display
  - Added ConsentManagement component to Settings page
  - Updated services index to export consentService and types
- **Backend Implementation**:
  - Updated consent endpoint documentation (`backend/app/api/v1/endpoints/consent.py`):
    - Added disclaimer text to endpoint description
    - Added note in docstring about disclaimer acknowledgment
    - Clarified that granting consent acknowledges disclaimer reading
- **Disclaimer Approach**:
  - Disclaimer shown once during consent flow (not on every recommendation)
  - By granting consent, users acknowledge they have read the disclaimer
  - No separate tracking needed - consent status is sufficient
  - Consent granted timestamp serves as disclaimer acceptance timestamp
- **Integration**:
  - ConsentManagement component uses React Query for server state
  - Invalidates dashboard and consent queries on consent changes
  - Graceful error handling with user-friendly messages
  - Mobile-responsive design with proper spacing and touch-friendly buttons
- **User Experience**:
  - Disclaimer displayed in prominent blue box with info icon
  - Clear messaging: "By granting consent below, you acknowledge that you have read and understood this disclaimer."
  - Visual hierarchy emphasizes disclaimer importance
  - Consent status clearly displayed with color coding (green/yellow)
- **Example Usage**:
  ```typescript
  // Get consent status
  const consentStatus = await consentService.getConsentStatus()

  // Grant consent (acknowledges disclaimer)
  const updatedStatus = await consentService.grantConsent({ tos_accepted: true })

  // Revoke consent
  const revokedStatus = await consentService.revokeConsent({ delete_data: false })
  ```

**Key Files**:
- `frontend/src/services/consentService.ts` - Consent API service
- `frontend/src/components/ConsentManagement.tsx` - Consent management component with disclaimer display
- `frontend/src/pages/Settings.tsx` - Updated to include ConsentManagement component
- `frontend/src/services/index.ts` - Updated to export consentService and types
- `backend/app/api/v1/endpoints/consent.py` - Updated endpoint documentation

#### ✅ Task 7.3: OpenAI Integration
- Set up OpenAI SDK (1.12.0) in service requirements
- Created OpenAI client utilities (`service/app/common/openai_client.py`)
- **OpenAIClient class** with methods:
  - `generate_content()` - Generate content with caching and retry logic
  - `validate_tone()` - Optional tone validation (0-10 scale)
  - `_check_rate_limit()` - Rate limiting (100 requests/minute)
  - `_exponential_backoff()` - Retry logic with exponential backoff
  - `_get_from_cache()` / `_save_to_cache()` - Redis caching (7-day TTL)
- **Features**:
  - **Retry Logic**: Exponential backoff with max 3 retries
  - **Rate Limiting**: Tracks requests per minute (100 req/min limit)
  - **Timeout Handling**: 30-second timeout per request
  - **Error Handling**: Handles RateLimitError, APIError, APIConnectionError, APITimeoutError
  - **Model Selection**: GPT-4-turbo-preview (default) or GPT-3.5-turbo (fallback)
  - **Caching**: Redis caching with 7-day TTL, cache key pattern: `openai:content:{persona}:{signal_hash}`
  - **Graceful Degradation**: Returns None if OpenAI unavailable, logs warnings
- Created ContentGenerator service (`service/app/recommendations/content_generator.py`)
- **ContentGenerator class** with methods:
  - `generate_education_content()` - Generate personalized education content
  - `generate_partner_offer_content()` - Generate personalized partner offer content
  - `generate_rationale_content()` - Optional rationale enhancement
  - `_build_persona_context()` - Build context string from persona and signals
  - `_build_education_prompt()` - Build prompt for education content generation
  - `_build_partner_offer_prompt()` - Build prompt for partner offer content generation
- **Content Generation Features**:
  - Uses persona-specific prompt templates with behavioral signals context
  - Generates personalized content based on user's persona and signals
  - Falls back to pre-generated templates when OpenAI fails or unavailable
  - Disclaimer acknowledgment handled during consent grant (not in generated content)
  - Persona-aware prompts that cite specific data points when relevant
- **Integration**:
  - Updated `RecommendationGenerator` to use `ContentGenerator`
  - Added `use_openai` flag (default: True) for optional OpenAI usage
  - Seamless fallback to templates when OpenAI is unavailable
  - Content generation is transparent - automatically uses OpenAI if available, falls back otherwise
- **Tone Validation** (Optional):
  - `validate_tone()` method checks recommendation text tone
  - Returns score 0-10 (10 = empowering, 0 = shaming/judgmental)
  - Uses GPT-3.5-turbo for cost-effective tone validation
  - Can be used to filter out inappropriate recommendations
- **Example Usage**:
  ```python
  # Initialize recommendation generator with OpenAI
  generator = RecommendationGenerator(db_session, use_openai=True)

  # Generate recommendations (will use OpenAI if available)
  result = generator.generate_recommendations(user_id)

  # Or use ContentGenerator directly
  content_gen = ContentGenerator()
  content = content_gen.generate_education_content(
      template_item,
      persona_id,
      signals,
      use_openai=True
  )
  ```

**Key Files**:
- `service/app/common/openai_client.py` - OpenAI client utilities (400+ lines)
- `service/app/recommendations/content_generator.py` - Content generation service (350+ lines)
- `service/app/recommendations/generator.py` - Updated to use ContentGenerator
- `service/app/recommendations/example_openai.py` - Usage examples for OpenAI integration
- `service/requirements.txt` - Added OpenAI SDK dependency

#### ✅ Task 7.2: Rationale Generation
- Created dedicated rationale generation service (`service/app/recommendations/rationale.py`)
- **RationaleGenerator class** with methods:
  - `format_account_number()` - Format account with last 4 digits from mask (e.g., "Visa ending in 4523")
  - `format_currency()` - Format amounts as currency (e.g., "$1,234.56")
  - `format_date()` - Format dates in readable format (e.g., "January 15, 2024")
  - `format_percent()` - Format percentages (e.g., "68.5%")
  - `get_account_details()` - Get account details from database for citations
  - `get_recent_transactions()` - Get recent transactions for data point citations
  - `generate_rationale_for_persona_1()` - Persona 1 (High Utilization) rationale generation
  - `generate_rationale_for_persona_2()` - Persona 2 (Variable Income Budgeter) rationale generation
  - `generate_rationale_for_persona_3()` - Persona 3 (Subscription-Heavy) rationale generation
  - `generate_rationale_for_persona_4()` - Persona 4 (Savings Builder) rationale generation
  - `generate_rationale_for_persona_5()` - Persona 5 (Custom Persona) rationale generation
  - `generate_rationale()` - Main method routing to persona-specific generators
- **Formatting Helpers**:
  - **Account Numbers**: Uses account `mask` field if available, falls back to last 4 digits of account_id
  - **Currency**: Formats as `$X,XXX.XX` with comma separators and 2 decimal places
  - **Dates**: Formats as `"Month Day, Year"` (e.g., "January 15, 2024")
  - **Percentages**: Formats with configurable decimal places (default: 1)
- **Persona-Specific Rationale Generation**:
  - **Persona 1 (High Utilization)**:
    - Cites account names with last 4 digits (e.g., "Visa ending in 4523")
    - Cites utilization percentages (e.g., "68% utilization")
    - Cites balance and limit amounts (e.g., "$3,400.00 of $5,000.00 limit")
    - Cites interest charges (e.g., "$87.50 per month in interest charges")
    - Cites minimum payment behavior
    - Cites overdue accounts
  - **Persona 2 (Variable Income Budgeter)**:
    - Cites payroll dates from recent transactions (e.g., "last payment was on January 15, 2024")
    - Cites median pay gaps (e.g., "median gap of 52 days")
    - Cites cash flow buffers (e.g., "0.6 months, below the recommended 1-2 months")
  - **Persona 3 (Subscription-Heavy)**:
    - Cites subscription counts (e.g., "5 recurring subscriptions")
    - Cites merchant names (e.g., "Netflix, Spotify, Gym, and 2 more")
    - Cites monthly recurring spend (e.g., "$125.50 per month")
    - Cites subscription share percentages (e.g., "15.2% of your total spending")
  - **Persona 4 (Savings Builder)**:
    - Cites savings account names with last 4 digits
    - Cites savings balances (e.g., "currently has a balance of $3,500.00")
    - Cites growth rates (e.g., "growing at 3.5%")
    - Cites net inflows (e.g., "$250.00 per month")
    - Cites emergency fund coverage (e.g., "covers 3.2 months of expenses")
  - **Persona 5 (Custom Persona)**:
    - Uses generic rationales with available signals
    - Tries to include any notable signals if available
- **Features**:
  - **Plain Language**: All rationales use plain language, avoid financial jargon
  - **Data Point Citations**: Cites specific accounts, amounts, dates, percentages
  - **Database Integration**: Fetches account details and transactions from database for accurate citations
  - **Fallback Handling**: Provides generic rationales when specific signals unavailable
  - **Persona-Aware**: Generates persona-specific rationales based on assigned persona
- **Integration**:
  - Updated `RecommendationGenerator` to use `RationaleGenerator` service
  - Removed old `generate_rationale` method from `RecommendationGenerator`
  - Rationales are generated for both education items and partner offers
  - Disclaimer shown prominently during consent flow (Task 8.4)
- **Example Rationale Output**:
  - Persona 1: "We noticed Visa ending in 4523 is at 68% utilization ($3,400.00 of $5,000.00 limit). You're paying $87.50 per month in interest charges."
  - Persona 2: "Your income arrives irregularly (last payment was on January 15, 2024, with a median gap of 52 days between payments). Your cash flow buffer is 0.6 months, below the recommended 1-2 months needed to handle irregular income."
  - Persona 3: "You have 5 recurring subscriptions including Netflix, Spotify, Gym, and 2 more, totaling $125.50 per month. This represents 15.2% of your total spending."
  - Persona 4: "Your High-Yield Savings ending in 7890 is growing at 3.5% and currently has a balance of $3,500.00. Your emergency fund covers 3.2 months of expenses."

**Key Files**:
- `service/app/recommendations/rationale.py` - Rationale generation service (680+ lines)
- `service/app/recommendations/example_rationale.py` - Usage examples
- `service/app/recommendations/generator.py` - Updated to use RationaleGenerator
- `service/app/recommendations/__init__.py` - Updated to export RationaleGenerator

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
  - Admin: `/admin/management` - Staff management page with Users and Staff tabs
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

#### ✅ Task 11.3: Recommendations View
- Created comprehensive recommendations list page with full filtering and sorting capabilities
- Created `recommendationsService` for fetching recommendations from API:
  - `getRecommendations(filters)` - Fetch recommendations with filtering and sorting
  - `getRecommendationDetail(id)` - Fetch single recommendation detail
  - `submitFeedback(id, feedback)` - Submit feedback for a recommendation
  - `dismissRecommendation(id)` - Dismiss a recommendation
  - `saveRecommendation(id)` - Save/bookmark a recommendation
  - Gracefully handles missing endpoints (404s) - returns empty list
  - Supports filters: type (education/partner_offer), status (approved/pending/rejected)
  - Supports sorting: date, relevance, type (ascending/descending)
- Implemented collapsible filters section with:
  - Type filter (all, education, partner offer) with button toggle
  - Status filter (all, approved, pending, rejected) with button toggle
  - Sort options (date, relevance, type) with ascending/descending order toggle
  - Visual indicators for active filters and sort direction
- Created `RecommendationCard` component displaying:
  - Type badges (Education/Partner Offer) with color coding
  - Status badges (Approved/Pending/Rejected) with icons
  - Eligibility badges for partner offers (Eligible/Not Eligible/Eligibility Pending)
  - Recommendation title and content
  - Partner name (for partner offers)
  - Prominent "Because" section explaining rationale with info icon
  - Eligibility reasons for ineligible partner offers
  - Action buttons (View Details, Save/Bookmark, Dismiss)
  - Created date display
  - Hover effects and proper spacing
- Implemented recommendation actions:
  - View Details - Links to `/recommendations/:id` detail page
  - Save/Bookmark - Toggle bookmark with visual feedback (saved state)
  - Dismiss - Removes recommendation from view (local state until backend ready)
- Implemented local state management for saved/dismissed recommendations:
  - Uses React state until backend endpoints are available
  - Saved recommendations persist during session
  - Dismissed recommendations filtered out from display
- Main Recommendations page features:
  - List view of all recommendations with rationales
  - Collapsible filters and sorting UI
  - Results count display (showing X of Y recommendations)
  - Empty states with helpful guidance (upload data prompt)
  - Loading skeletons while fetching data
  - Error states with retry functionality
  - Mobile-responsive design with touch-friendly buttons
  - Proper spacing and visual hierarchy
  - All components properly typed with TypeScript
- Recommendations service handles missing backend endpoints gracefully
- When recommendations API endpoints are implemented, page will automatically work with real data

**Key Files**:
- `frontend/src/pages/Recommendations.tsx` - Main recommendations list page (450+ lines)
- `frontend/src/services/recommendationsService.ts` - Recommendations data service
- `frontend/src/services/index.ts` - Updated to export recommendationsService and types

#### ✅ Task 12.1: Data Upload UI
- Created comprehensive data upload UI with drag-and-drop and file picker functionality
- Created `dataUploadService` (`frontend/src/services/dataUploadService.ts`) with:
  - `uploadFile(file, onProgress)` - Upload file with progress tracking via axios `onUploadProgress`
  - `validateFileType(file)` - Validate file extension and MIME type (JSON/CSV only)
  - `validateFileSize(file)` - Validate file size (10MB max)
  - `formatFileSize(bytes)` - Format file size for display (Bytes, KB, MB, GB)
  - `getUploadStatus(uploadId)` - Get upload status by upload ID
  - `getUploadHistory()` - Get upload history for current user (gracefully handles missing endpoint)
  - Constants: `MAX_FILE_SIZE` (10MB), `ALLOWED_FILE_TYPES` (json, csv), `ALLOWED_MIME_TYPES`
- Created `FileUpload` component (`frontend/src/components/FileUpload.tsx`) with:
  - **Drag-and-drop support**:
    - Visual feedback during drag (border color changes, background highlight)
    - Prevents default browser behavior
    - Handles drag enter, drag over, drag leave, and drop events
  - **File picker button**:
    - Browse Files button for traditional file selection
    - Hidden file input with proper accept attribute
  - **Real-time validation**:
    - File type validation (checks extension and MIME type)
    - File size validation (10MB max) before upload
    - Clear error messages for invalid files
  - **Upload progress indicator**:
    - Percentage display (0-100%)
    - Progress bar with smooth animation
    - Bytes uploaded / total bytes display
    - Spinner animation during upload
  - **Error handling**:
    - Error display with clear messages
    - Error dismiss functionality
    - Retry capability (reset and try again)
  - **Success state handling**:
    - Calls `onUploadSuccess` callback with upload data
    - Resets component state after successful upload
  - **Mobile-responsive design**:
    - Touch-friendly interface
    - Proper spacing and sizing for mobile
    - Responsive layout
- Updated `Upload` page (`frontend/src/pages/Upload.tsx`) with:
  - **FileUpload component integration**:
    - Handles upload success and error callbacks
    - Displays success messages with auto-dismiss (5 seconds)
  - **Upload history display**:
    - Fetches upload history using React Query
    - Displays uploads in list format with:
      - File name and icon
      - Status badges (pending, processing, completed, failed) with color coding
      - File size and type
      - Created date (formatted)
      - Processed date (if available)
      - Validation errors (if any)
    - Loading skeletons while fetching
    - Empty state for new users with helpful guidance
    - Error state with graceful handling (upload history endpoint may not exist yet)
  - **Status badges**:
    - Color-coded badges: green (completed), blue (processing), red (failed), yellow (pending)
    - Proper contrast for accessibility
  - **Page layout**:
    - Header with title and description
    - Success message display (auto-dismiss after 5 seconds)
    - File upload section
    - Upload history section
    - Mobile-responsive design
- **File validation**:
  - Matches backend requirements:
    - JSON files: `.json` extension, `application/json` or `text/json` MIME type
    - CSV files: `.csv` extension, `text/csv`, `application/csv`, or `text/plain` MIME type
    - Maximum file size: 10MB (10 * 1024 * 1024 bytes)
  - Validation happens before upload to save bandwidth
  - Clear error messages for validation failures
- **API integration**:
  - Integrates with backend API at `POST /api/v1/data/upload`
  - Uses `multipart/form-data` content type
  - Includes JWT token in Authorization header (via axios interceptor)
  - Handles API errors gracefully with user-friendly messages
- **Error handling**:
  - Network errors
  - API errors (400, 401, 403, 500)
  - File validation errors
  - Clear error messages for all error types
- **User experience**:
  - Loading states during upload
  - Progress feedback during upload
  - Success confirmation after upload
  - Error recovery (dismiss and try again)
  - Empty states with helpful guidance
  - Mobile-responsive design
- All code compiles successfully with no linting errors (TypeScript)
- All requirements met per PRD specifications (FE-US-010, FR-FE-006)

**Key Files**:
- `frontend/src/services/dataUploadService.ts` - Data upload service with validation and API integration
- `frontend/src/components/FileUpload.tsx` - File upload component with drag-and-drop
- `frontend/src/pages/Upload.tsx` - Upload page with history display
- `frontend/src/services/index.ts` - Updated to export dataUploadService functions and types

#### ✅ Task 12.2: Consent Management UI
- Enhanced existing `ConsentManagement` component (`frontend/src/components/ConsentManagement.tsx`) with consent history/audit log
- **Consent Management Settings Page**:
  - Component integrated into Settings page (`frontend/src/pages/Settings.tsx`)
  - Displays current consent status with color-coded indicators (green for granted, yellow for not granted)
  - Shows consent version and grant/revoke timestamps
  - Clear explanation of what consent enables
- **Consent Status Indicator**:
  - `ConsentStatusBadge` component (`frontend/src/components/ConsentStatusBadge.tsx`) displayed on dashboard
  - Shows consent status with visual indicators
  - Links to settings page for management
- **Consent Toggle with Explanation**:
  - Grant consent button with clear explanation of what consent enables
  - Revoke consent button with confirmation dialog
  - Financial advice disclaimer prominently displayed when consent not granted
  - By granting consent, users acknowledge they have read the disclaimer
- **Confirmation Dialog for Revocation**:
  - Confirmation UI appears before revoking consent
  - Explains consequences of revocation (stops personalized recommendations)
  - Offers data deletion option
  - Cancel option to abort revocation
- **Data Deletion Option**:
  - Two revocation options:
    - "Revoke Only" - Revokes consent without deleting data
    - "Revoke & Delete Data" - Revokes consent and deletes all user data
  - Clear warnings about data deletion consequences
- **Consent History/Audit Log**:
  - New consent history section displaying:
    - Consent granted timestamp with formatted date/time (e.g., "January 15, 2024, 10:30 AM")
    - Consent version displayed when granted
    - Consent revoked timestamp (if applicable)
    - Last updated timestamp (fallback when specific grant/revoke dates not available)
  - Visual timeline with color-coded status indicators:
    - Green background for granted events
    - Red background for revoked events
    - Gray background for general updates
  - Icons for visual clarity (FaCheckCircle, FaExclamationTriangle, FaClock, FaHistory)
  - Formatted timestamps using `toLocaleString()` with full date and time
- **UI/UX Features**:
  - Loading states with skeleton screens
  - Error handling with retry capability
  - Mobile-responsive design using Tailwind CSS
  - Proper accessibility features (focus states, keyboard navigation)
  - Immediate UI updates after consent changes (React Query invalidation)
- **API Integration**:
  - Uses `consentService` (`frontend/src/services/consentService.ts`):
    - `getConsentStatus()` - Fetches current consent status
    - `grantConsent(request)` - Grants consent with TOS acceptance
    - `revokeConsent(request)` - Revokes consent with optional data deletion
  - Integrates with backend API:
    - `GET /api/v1/consent` - Get consent status
    - `POST /api/v1/consent` - Grant consent
    - `DELETE /api/v1/consent` - Revoke consent
  - React Query for state management and caching
  - Automatic cache invalidation on consent changes
- **Error Handling**:
  - Network errors handled gracefully
  - API errors displayed with user-friendly messages
  - Loading states during async operations
  - Error recovery (retry capability)
- All code compiles successfully with no linting errors (TypeScript)
- All requirements met per PRD specifications (FE-US-009, FR-FE-005)

**Key Files**:
- `frontend/src/components/ConsentManagement.tsx` - Consent management component with history/audit log
- `frontend/src/components/ConsentStatusBadge.tsx` - Consent status badge component for dashboard
- `frontend/src/services/consentService.ts` - Consent API service
- `frontend/src/pages/Settings.tsx` - Settings page with consent management
- `frontend/src/pages/Dashboard.tsx` - Dashboard with consent status indicator

#### ✅ Task 12.3: Mobile Responsiveness
- Created comprehensive mobile-responsive design across all frontend pages
- **Mobile Navigation Component** (`frontend/src/components/Navigation.tsx`):
  - Mobile bottom navigation bar (< 1024px) with fixed positioning at bottom of screen
  - Desktop horizontal navigation bar (≥ 1024px) with sticky positioning at top
  - Hamburger menu for additional items on mobile (Settings, Logout)
  - Touch-friendly buttons with minimum 60x60px on mobile for easy tapping
  - Active state indicators showing current page
  - Smooth transitions and animations
  - Bottom padding spacer (80px) to prevent content overlap on mobile
  - User email display in mobile menu
  - Logout functionality integrated into navigation
- **Viewport & Meta Tags** (`frontend/index.html`):
  - Updated viewport meta tag: `width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes`
  - Added theme color meta tag for mobile browsers (`#2563eb`)
  - Proper scaling settings for iOS and Android
- **Touch Optimization CSS** (`frontend/src/styles/index.css`):
  - Minimum touch targets (44x44px) for accessibility compliance (WCAG 2.1 AA)
  - `touch-action: manipulation` for better touch response
  - Reduced tap highlight color (`-webkit-tap-highlight-color: rgba(0, 0, 0, 0.1)`)
  - Form input font size 16px to prevent iOS zoom on focus
  - Smooth scrolling (`scroll-behavior: smooth`)
  - Pull-to-refresh prevention (`overscroll-behavior-y: contain`)
  - Text size adjustment prevention (`-webkit-text-size-adjust: 100%`)
- **Responsive Breakpoints**:
  - Mobile-first design approach
  - Breakpoints: Mobile (320px+), Tablet (768px+), Desktop (1024px+)
  - Tailwind CSS breakpoints: `sm:` (640px), `md:` (768px), `lg:` (1024px)
- **Page Updates for Mobile Responsiveness**:
  - **Dashboard** (`frontend/src/pages/Dashboard.tsx`):
    - Mobile-first padding (`py-4 lg:py-8`)
    - Bottom padding for mobile navigation (`pb-24 lg:pb-8`)
    - Responsive text sizes (`text-2xl sm:text-3xl`)
    - Responsive grid layouts (`grid-cols-1 sm:grid-cols-2 md:grid-cols-3`)
  - **Profile** (`frontend/src/pages/Profile.tsx`):
    - Responsive header with stacked layout on mobile (`flex-col sm:flex-row`)
    - Export buttons show abbreviated labels on mobile ("CSV" instead of "Export CSV")
    - Full-width buttons on mobile (`w-full sm:w-auto`)
    - Touch-friendly button sizes (`touch-manipulation`)
  - **Recommendations** (`frontend/src/pages/Recommendations.tsx`):
    - Responsive filters and sort controls
    - Collapsible filter section for mobile
    - Responsive recommendation cards
    - Mobile-optimized spacing
  - **RecommendationDetail** (`frontend/src/pages/RecommendationDetail.tsx`):
    - Responsive layout with proper mobile padding
    - Touch-friendly action buttons
    - Mobile-optimized content display
  - **Settings** (`frontend/src/pages/Settings.tsx`):
    - Responsive layout with mobile padding
    - Mobile-optimized consent management display
  - **Upload** (`frontend/src/pages/Upload.tsx`):
    - Responsive layout with mobile padding
    - Mobile-optimized file upload component
    - Responsive upload history display
- **Mobile-Specific UI Improvements**:
  - Export buttons show abbreviated labels on mobile ("CSV"/"PDF" instead of "Export CSV"/"Export PDF")
  - Responsive grid layouts that stack on mobile (1 column) and expand on larger screens
  - Touch-friendly button sizes and spacing (minimum 44x44px)
  - Mobile navigation doesn't overlap content (proper bottom padding)
  - Responsive headers with flexible layouts (stacked on mobile, inline on desktop)
  - Proper spacing adjustments for mobile (reduced padding and margins)
- **Touch Interaction Optimization**:
  - All interactive elements meet minimum touch target size (44x44px)
  - Proper spacing between touch targets (minimum 8px)
  - Touch manipulation CSS for better touch response
  - Reduced tap highlight for cleaner mobile experience
  - Form inputs optimized to prevent iOS zoom
- **Accessibility Compliance**:
  - Touch targets meet WCAG 2.1 AA requirements (minimum 44x44px)
  - Proper focus indicators visible on all interactive elements
  - Keyboard navigation support maintained
  - Screen reader compatibility maintained
- **Device Optimization**:
  - Optimized for iOS devices (Safari, Chrome iOS)
  - Optimized for Android devices (Chrome, Firefox)
  - Tested breakpoints: 320px (iPhone SE), 375px (iPhone 12/13), 768px (iPad), 1024px+ (Desktop)
  - Proper scaling and zoom support
- **Navigation Integration**:
  - Added Navigation component to App.tsx
  - Navigation only shows for authenticated users
  - Public routes (login, register) don't show navigation
  - Operator routes show navigation with operator-specific items
- **Component Exports**:
  - Updated `frontend/src/components/index.ts` to export Navigation component
  - All components properly exported and accessible
- All code compiles successfully with no linting errors (TypeScript)
- All requirements met per PRD specifications (NFR-FE-002, Design Principles)

**Key Files**:
- `frontend/src/components/Navigation.tsx` - Mobile and desktop navigation component
- `frontend/src/styles/index.css` - Touch optimization CSS styles
- `frontend/index.html` - Updated viewport and meta tags
- `frontend/src/App.tsx` - Added Navigation component integration
- `frontend/src/pages/Dashboard.tsx` - Updated for mobile responsiveness
- `frontend/src/pages/Profile.tsx` - Updated for mobile responsiveness
- `frontend/src/pages/Recommendations.tsx` - Updated for mobile responsiveness
- `frontend/src/pages/RecommendationDetail.tsx` - Updated for mobile responsiveness
- `frontend/src/pages/Settings.tsx` - Updated for mobile responsiveness
- `frontend/src/pages/Upload.tsx` - Updated for mobile responsiveness
- `frontend/src/components/index.ts` - Updated to export Navigation component

#### ✅ Task 12.4: UI Polish & Accessibility
- Created comprehensive accessibility and UI polish improvements across the frontend application
- **Reusable Loading Components** (`frontend/src/components/LoadingSkeleton.tsx`):
  - `LoadingSkeleton` component with variants: text, card, list, table, circular
  - `PageSkeleton` component for full-page loading states
  - All loading states include ARIA labels (`role="status"`, `aria-label="Loading..."`)
  - Screen reader support with `.sr-only` class for "Loading..." text
  - Proper semantic HTML for accessibility
- **Reusable Error Component** (`frontend/src/components/ErrorState.tsx`):
  - Customizable error state component with title, message, and retry functionality
  - ARIA live regions (`role="alert"`, `aria-live="polite"`) for screen reader announcements
  - Proper error message structure with `id` attributes for ARIA `aria-describedby`
  - Consistent error display across all pages
  - Retry button with proper focus management
- **Reusable Empty State Component** (`frontend/src/components/EmptyState.tsx`):
  - Customizable empty state component with title, description, and actions
  - Support for primary and secondary action buttons (with optional icons)
  - Proper semantic HTML (`role="status"`, `aria-live="polite"`)
  - Helpful guidance text for users
  - Icon support with `aria-hidden="true"` for decorative icons
- **Skip Link Component** (`frontend/src/components/SkipLink.tsx`):
  - Skip link component for keyboard navigation accessibility
  - Hidden by default, visible on focus (`.sr-only` with `focus:not-sr-only`)
  - Proper styling for keyboard users (high contrast, visible outline)
  - Links to main content area (`#main-content`)
- **Enhanced CSS Accessibility** (`frontend/src/styles/index.css`):
  - Focus indicators: 2px solid blue outline (#3b82f6) with 2px offset on all interactive elements
  - Screen reader utilities: `.sr-only` class for screen reader-only content
  - High contrast mode support: `@media (prefers-contrast: high)` with enhanced borders
  - Reduced motion support: `@media (prefers-reduced-motion: reduce)` to disable animations
  - Color contrast verification: Primary colors meet WCAG AA standards (4.5:1 ratio)
  - Touch target optimization: Minimum 44x44px for accessibility compliance
  - Focus ring utilities: `.focus-ring` class for consistent focus styling
- **Semantic HTML Improvements**:
  - Added `<header>` tags to all page headers
  - Added `<nav>` tags with `aria-label="Main navigation"` to Navigation component
  - Added `<main id="main-content">` wrapper to App.tsx for skip link targeting
  - Proper heading hierarchy (h1 → h2 → h3)
- **ARIA Labels & Attributes**:
  - Added `aria-label` to all interactive elements (buttons, links, form inputs)
  - Added `aria-current="page"` to active navigation links
  - Added `aria-expanded` and `aria-controls` to collapsible elements (filters, mobile menu)
  - Added `aria-hidden="true"` to decorative icons
  - Added `role` attributes where appropriate (tablist, tab, tabpanel, menu, menuitem)
  - Added `aria-describedby` to error messages linking to title and message
  - Added `aria-live` regions for dynamic content updates
- **Keyboard Navigation Enhancements**:
  - Skip link added to main content area
  - Enhanced focus indicators on all interactive elements (2px solid blue outline)
  - Proper tab order maintained throughout application
  - Keyboard navigation support in Login tabs (tablist, tab, tabpanel roles)
  - Keyboard navigation support in Navigation menu (menu, menuitem roles)
  - Keyboard navigation support in filter panels (aria-expanded, aria-controls)
  - Focus management for modals and dialogs
- **Page Updates for Accessibility**:
  - **Dashboard** (`frontend/src/pages/Dashboard.tsx`):
    - Uses `PageSkeleton` for loading states
    - Uses `ErrorState` component for error handling
    - Uses `EmptyState` component for new user guidance
    - Added semantic `<header>` tag
    - Added `aria-label` to quick action links
    - Added `aria-hidden="true"` to decorative icons
  - **Profile** (`frontend/src/pages/Profile.tsx`):
    - Uses `PageSkeleton` for loading states
    - Uses `ErrorState` component for error handling
    - Uses `EmptyState` component for new user guidance
    - Added semantic `<header>` tag
    - Added `aria-label` to export buttons
    - Added `aria-hidden="true"` to icons
  - **Recommendations** (`frontend/src/pages/Recommendations.tsx`):
    - Uses `PageSkeleton` for loading states
    - Uses `ErrorState` component for error handling
    - Uses `EmptyState` component for empty states
    - Added semantic `<header>` tag
    - Added `aria-expanded` and `aria-controls` to filter toggle button
    - Added `aria-label` to all action buttons (View Details, Save, Dismiss)
    - Added `aria-hidden="true"` to icons
  - **Login** (`frontend/src/pages/Login.tsx`):
    - Added `role="tablist"` and `aria-label` to auth method tabs
    - Added `role="tab"`, `aria-selected`, `aria-controls` to tab buttons
    - Added `role="tabpanel"` and `aria-labelledby` to form panels
    - Added `role="alert"` and `aria-live="polite"` to error messages
    - Enhanced focus indicators on all form elements
  - **Navigation** (`frontend/src/components/Navigation.tsx`):
    - Added `aria-label="Main navigation"` to nav elements
    - Added `aria-current="page"` to active links
    - Added `aria-expanded` and `aria-controls` to mobile menu button
    - Added `role="menu"` and `role="menuitem"` to mobile menu panel
    - Added `aria-label` to all navigation links and buttons
    - Added `aria-hidden="true"` to icons
    - Enhanced focus indicators on all interactive elements
- **WCAG 2.1 AA Compliance**:
  - Color contrast: All text meets 4.5:1 contrast ratio minimum
  - Focus indicators: Visible on all interactive elements (2px solid outline)
  - Keyboard navigation: Full support with proper tab order
  - Screen reader support: ARIA labels, semantic HTML, live regions
  - Touch targets: Minimum 44x44px for all interactive elements
  - Skip links: Skip to main content functionality
  - Error messages: Properly associated with form fields via ARIA
  - Form labels: All form inputs have associated labels
- **Component Exports**:
  - Updated `frontend/src/components/index.ts` to export new components:
    - `LoadingSkeleton`, `PageSkeleton`
    - `ErrorState`
    - `EmptyState`
    - `SkipLink`
- All code compiles successfully with no linting errors (TypeScript)
- All requirements met per PRD specifications (NFR-FE-003, UX Features)

**Key Files**:
- `frontend/src/components/LoadingSkeleton.tsx` - Reusable loading skeleton components
- `frontend/src/components/ErrorState.tsx` - Reusable error state component
- `frontend/src/components/EmptyState.tsx` - Reusable empty state component
- `frontend/src/components/SkipLink.tsx` - Skip link component for accessibility
- `frontend/src/styles/index.css` - Enhanced accessibility CSS styles
- `frontend/src/App.tsx` - Added skip link and semantic main tag
- `frontend/src/pages/Dashboard.tsx` - Updated with reusable components and accessibility
- `frontend/src/pages/Profile.tsx` - Updated with reusable components and accessibility
- `frontend/src/pages/Recommendations.tsx` - Updated with reusable components and accessibility
- `frontend/src/pages/Login.tsx` - Enhanced with ARIA attributes and keyboard navigation
- `frontend/src/components/Navigation.tsx` - Enhanced with ARIA labels and keyboard navigation
- `frontend/src/components/index.ts` - Updated to export new components

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
- `user_id` (UUID, PK)
- `name` (String, nullable)
- `email` (String, unique, nullable, indexed)
- `phone_number` (String, unique, nullable, indexed)
- `password_hash` (String, nullable)
- `oauth_providers` (JSON, default: {})
- `role` (String: user, operator, admin, default: user)
- `consent_status` (Boolean, default: false)
- `consent_version` (String, default: "1.0")
- `monthly_income` (Numeric(15, 2), nullable) - User's monthly income (can be manually set or calculated from transactions)
- `created_at` (DateTime, timezone-aware)
- `updated_at` (DateTime, timezone-aware, nullable)

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
- `payment_channel` (String: online, in_store, other, ACH) - ACH added for payroll deposits
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
- `GET /api/v1/users/{user_id}/profile` - Get behavioral profile with signals (30d/180d) and persona assignment (cached 5min)
- `GET /api/v1/users/{user_id}/persona-history` - Get persona assignment history with pagination (skip/limit)
- `GET /api/v1/users/{user_id}/recommendations` - Get recommendations for a user (with filtering/sorting/pagination)

### Consent Endpoints
- `POST /api/v1/consent` - Grant consent for data processing
- `GET /api/v1/consent` - Get consent status
- `DELETE /api/v1/consent` - Revoke consent (with optional data deletion)

### Data Upload Endpoints
- `POST /api/v1/data/upload` - Upload transaction data file (JSON/CSV, max 10MB)
  - **Security**: User ID is automatically assigned from authenticated user (not from file)
  - Uploaded files should NOT contain `user_id` field (if present, it's ignored)
  - Files contain only: `accounts`, `transactions`, `liabilities` (and optional `upload_timestamp`)
- `GET /api/v1/data/upload/{upload_id}` - Get upload status

### Recommendations Endpoints
- `GET /api/v1/recommendations` - Get current user's recommendations (with filtering: status/type, sorting: date/relevance/type, pagination: skip/limit, cached 1hr)
- `GET /api/v1/recommendations/{recommendation_id}` - Get recommendation detail with decision trace
- `POST /api/v1/recommendations/{recommendation_id}/feedback` - Submit feedback (rating, helpful, comment)

### Operator Endpoints
- `GET /api/v1/operator/review` - Get review queue (with filters: status, user_id, type, persona_id, pagination: skip/limit)
- `GET /api/v1/operator/review/{recommendation_id}` - Get recommendation for review with decision trace
- `POST /api/v1/operator/review/{recommendation_id}/approve` - Approve recommendation (with logging)
- `POST /api/v1/operator/review/{recommendation_id}/reject` - Reject recommendation (with reason in request body, logging)
- `PUT /api/v1/operator/review/{recommendation_id}` - Modify recommendation (title, content, rationale) with logging
- `POST /api/v1/operator/review/bulk` - Bulk approve/reject recommendations (with action: approve/reject, recommendation_ids array, reason for reject)
- `GET /api/v1/operator/analytics` - Get system analytics (coverage, explainability, performance, engagement, fairness metrics) - Integrated with EvaluationService (Task 18.1, 18.3)
- `GET /api/v1/operator/analytics/export/json` - Export metrics as JSON file download (Task 18.3)
- `GET /api/v1/operator/analytics/export/csv` - Export metrics as CSV file download (Task 18.3)
- `GET /api/v1/operator/analytics/export/summary` - Export summary report as Markdown file download (Task 18.3)
- `GET /api/v1/operator/users/{user_id}` - Get user details (operator view)
- `GET /api/v1/operator/users/{user_id}/accounts` - Get user accounts (operator view)
- `GET /api/v1/operator/users/{user_id}/transactions` - Get user transactions (operator view, paginated)
- `GET /api/v1/operator/users/{user_id}/liabilities` - Get user liabilities (operator view)
- `GET /api/v1/operator/admin/users` - Get all users (admin only, paginated)
- `PUT /api/v1/operator/admin/users/{user_id}/role` - Update user role (admin only)

---

## Frontend Components

### Pages
- `Login.tsx` - Login page with email/phone/OAuth
- `Register.tsx` - Registration page with email/phone/OAuth
- `Dashboard.tsx` - User dashboard with persona, signals, recommendations, and consent status. For admins, includes UsersList component showing all regular users
- `StaffManagement.tsx` - Staff management page with tabs for Users and Staff (admin-only). Separates regular users from operators/admins
- `Profile.tsx` - User profile page with behavioral signals, trends, and persona history
- `Recommendations.tsx` - Recommendations list page with filtering, sorting, and actions
- `RecommendationDetail.tsx` - Recommendation detail (placeholder)
- `Settings.tsx` - Settings page with Income Settings, ConsentManagement, and Account Linking components
- `Upload.tsx` - Data upload page with drag-and-drop file upload (Task 12.1)
- `OperatorDashboard.tsx` - Operator dashboard with stats cards, quick actions, review queue preview, and system metrics (Task 17.1)
- `ReviewQueueList.tsx` - Full review queue list page with filtering (status, type, user, persona, date range), sorting (priority, date, user), search functionality, and bulk operations (approve/reject) (Task 17.1, 17.2)
- `OperatorReview.tsx` - Operator review page for individual recommendation review with full decision trace display, expandable sections for persona assignment logic, behavioral signals, guardrails checks, approve/reject functionality with confirmation dialogs, and modify recommendation functionality (edit title, content, rationale) (Task 17.3, 17.4)
- `OperatorAnalytics.tsx` - Operator analytics dashboard page with comprehensive metrics visualization: four key metric cards (Coverage, Explainability, Performance, Engagement), coverage metrics bar chart, explainability metrics bar chart with quality score, performance metrics line chart (latency percentiles), engagement metrics bar chart, fairness metrics section (persona balance score, persona distribution), detailed metrics tables, export buttons (JSON/CSV/Summary with actual functionality), back navigation, loading states, error handling, and mobile-responsive design using recharts library (Task 18.1, 18.3)

### Components
- `OAuthButtons.tsx` - OAuth provider buttons with icons
- `PhoneVerification.tsx` - Phone verification with countdown timer
- `AccountLinking.tsx` - Account linking component for managing linked authentication methods
- `PersonaBadge.tsx` - Persona display component with color-coded indicators
- `BehavioralSignals.tsx` - Behavioral signals display component (subscriptions, savings, credit, income)
- `RecommendationsList.tsx` - Recommendations list component with type badges and rationales
- `ConsentStatusBadge.tsx` - Consent status badge component with settings link
- `ConsentManagement.tsx` - Consent management component with prominent disclaimer display
- `IncomeSettings.tsx` - Monthly income settings component for viewing and editing user income
- `TimePeriodSelector.tsx` - Time period selector component (30-day vs 180-day)
- `ProfileBehavioralSignals.tsx` - Profile behavioral signals component with expandable sections
- `SignalTrends.tsx` - Signal trends visualization component with progress bars
- `PersonaHistoryTimeline.tsx` - Persona history timeline component
- `FileUpload.tsx` - File upload component with drag-and-drop and file picker (Task 12.1)
- `Navigation.tsx` - Navigation component with mobile bottom nav and desktop horizontal nav (Task 12.3)
- `LoadingSkeleton.tsx` - Reusable loading skeleton components with variants (text, card, list, table, circular) and PageSkeleton (Task 12.4)
- `ErrorState.tsx` - Reusable error state component with retry functionality and ARIA live regions (Task 12.4)
- `EmptyState.tsx` - Reusable empty state component with customizable actions and helpful guidance (Task 12.4)
- `SkipLink.tsx` - Skip link component for keyboard navigation accessibility (Task 12.4)
- `ConfirmationDialog.tsx` - Reusable confirmation dialog component supporting approve, reject, confirm, warning, and info types with customizable title, message, confirm/cancel labels, loading states, optional text input, and full accessibility support (Task 17.4)
- `ReviewQueue.tsx` - Review queue component displaying pending recommendations with status badges, type badges, persona badges, and auto-refresh (Task 17.1)
- `UsersList.tsx` - Users list component for admin dashboard displaying regular users only (filters out operators and admins) with personas and consent status
- `StaffList.tsx` - Staff list component for displaying operators and admins separately from regular users
- `StaffManagement.tsx` - Staff management page with tabs for Users and Staff (admin-only)

### Services
- `api.ts` - Axios instance with interceptors (enhanced error handling for 403/404/500, network errors, prevents redirect loops)
- `consentService.ts` - Consent management service
- `authService.ts` - Authentication service functions (including account linking)
- `userService.ts` - User profile service for fetching user data and updating profile (including monthly income)
- `dashboardService.ts` - Dashboard data service for fetching persona, signals, and recommendations
- `profileService.ts` - Profile data service for fetching behavioral profile and persona history (updated to use user-specific endpoints)
- `recommendationsService.ts` - Recommendations service for fetching recommendations, detail, feedback, dismiss, and save (integrated with new API endpoints)
- `dataUploadService.ts` - Data upload service with progress tracking (Task 12.1)
- `adminService.ts` - Admin service for user management (getAllUsers, getUserProfile, getUserAccounts, getUserTransactions, getUserBehavioralProfile, getUserLiabilities)
- `operatorService.ts` - Operator service for review queue operations and analytics (getReviewQueue with filters/sorting, getRecommendationForReview with RecommendationReviewDetail interface including DecisionTrace, GuardrailsInfo, SignalData types, approveRecommendation, rejectRecommendation with reason in request body, modifyRecommendation for editing title/content/rationale, bulkApproveRecommendations, bulkRejectRecommendations, getAnalytics returning SystemAnalytics interface with coverage, explainability, performance, engagement, and fairness metrics, exportMetricsJSON, exportMetricsCSV, exportSummaryReport returning Blob) (Task 17.1, 17.2, 17.3, 17.4, 18.1, 18.3)

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
- `OPENAI_API_KEY` - OpenAI API key (optional, for content generation)
- `OPENAI_MODEL` - OpenAI model (default: gpt-4-turbo-preview)
- `OPENAI_FALLBACK_MODEL` - OpenAI fallback model (default: gpt-3.5-turbo)

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
- `backend/app/api/v1/endpoints/recommendations.py` - Recommendations endpoints
- `backend/app/api/v1/endpoints/operator.py` - Operator endpoints (review queue, analytics with EvaluationService integration, export endpoints for JSON/CSV/summary reports, fairness metrics) (Task 17.1, 17.2, 17.3, 17.4, 18.1, 18.3)
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
- `frontend/src/components/` - Reusable components (OAuthButtons, PhoneVerification, AccountLinking, PersonaBadge, BehavioralSignals, RecommendationsList, ConsentStatusBadge, ConsentManagement, TimePeriodSelector, ProfileBehavioralSignals, SignalTrends, PersonaHistoryTimeline)
- `frontend/src/services/api.ts` - API client
- `frontend/src/services/consentService.ts` - Consent management service
- `frontend/src/services/authService.ts` - Auth service (including account linking)
- `frontend/src/services/userService.ts` - User profile service
- `frontend/src/services/dashboardService.ts` - Dashboard data service
- `frontend/src/services/profileService.ts` - Profile data service
- `frontend/src/services/recommendationsService.ts` - Recommendations data service
- `frontend/src/store/authStore.ts` - Auth state store
- `frontend/src/utils/validation.ts` - Validation utilities
- `frontend/src/styles/index.css` - Global styles with Tailwind

### Service Layer
- `service/app/ingestion/` - Data ingestion services
  - `parser.py` - Plaid data parser (JSON/CSV)
  - `storage.py` - PostgreSQL and S3 Parquet storage
  - `service.py` - Main ingestion service
  - `validator.py` - Plaid schema validator
  - `validation_results.py` - Validation results storage
  - `__init__.py` - Module exports
- `service/app/features/` - Feature engineering services
  - `subscriptions.py` - Subscription detection service (Task 5.1)
  - `savings.py` - Savings pattern detection service (Task 5.2)
  - `credit.py` - Credit utilization detection service (Task 5.3)
  - `income.py` - Income stability detection service (Task 5.4)
  - `persona_assignment.py` - Persona assignment service (Task 6.1)
  - `example_subscriptions.py` - Usage examples for subscription detection
  - `example_savings.py` - Usage examples for savings detection
  - `example_credit.py` - Usage examples for credit detection
  - `example_income.py` - Usage examples for income detection
  - `example_persona_assignment.py` - Usage examples for persona assignment
  - `__init__.py` - Module exports (SubscriptionDetector, SavingsDetector, CreditUtilizationDetector, IncomeStabilityDetector, PersonaAssignmentService)
- `service/app/recommendations/` - Recommendation generation services (Task 7.1, 7.2, 7.3, 7.4)
  - `generator.py` - Recommendation generation service (RecommendationGenerator)
  - `rationale.py` - Rationale generation service (RationaleGenerator)
  - `content_generator.py` - OpenAI content generation service (ContentGenerator) (Task 7.3)
  - `partner_offer_service.py` - Partner offer service with eligibility checking (PartnerOfferService) (Task 7.4)
  - `decision_trace.py` - Decision trace generation service (DecisionTraceGenerator) (Task 9.1)
  - `catalog.py` - Education and partner offer catalogs
  - `example_recommendations.py` - Usage examples for recommendation generation
  - `example_rationale.py` - Usage examples for rationale generation
  - `example_openai.py` - Usage examples for OpenAI integration (Task 7.3)
  - `example_partner_offers.py` - Usage examples for partner offer service (Task 7.4)
  - `example_decision_trace.py` - Usage examples for decision trace generation (Task 9.1)
  - `__init__.py` - Module exports (RecommendationGenerator, RationaleGenerator, DecisionTraceGenerator)
- `service/app/eval/` - Evaluation services (Task 9.2, 9.3)
  - `metrics.py` - Evaluation service (EvaluationService) (Task 9.2)
  - `report.py` - Report generation service (ReportGenerator) (Task 9.3)
  - `example_evaluation.py` - Usage examples for evaluation service (Task 9.2)
  - `example_report.py` - Usage examples for report generation (Task 9.3)
  - `__init__.py` - Module exports (EvaluationService, ReportGenerator)
- `service/app/common/` - Shared utilities
  - `validator.py` - Plaid schema validator (moved from ingestion/)
  - `feature_cache.py` - Feature caching utility (Task 5.5)
  - `openai_client.py` - OpenAI client utilities with retry logic and caching (Task 7.3)
  - `consent_guardrails.py` - Consent guardrails service (Task 8.1)
  - `eligibility_guardrails.py` - Eligibility guardrails service (Task 8.2)
  - `tone_validation_guardrails.py` - Tone validation guardrails service (Task 8.3)
  - `example_consent_guardrails.py` - Consent guardrails usage examples
  - `example_eligibility_guardrails.py` - Eligibility guardrails usage examples
  - `example_tone_validation_guardrails.py` - Tone validation guardrails usage examples
- `service/requirements.txt` - Service dependencies including OpenAI SDK 1.12.0 (Task 7.3)
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
  - `ADDITIONAL_PERSONAS.md` - Additional persona suggestions (7 personas)
- `backend/SMS_TESTING.md` - SMS testing guide
- `backend/OAUTH_SETUP.md` - OAuth setup guide
- `backend/DATABASE_SETUP.md` - Database setup guide
- `scripts/README.md` - Scripts documentation including synthetic data generator

---

## Next Steps

### Immediate (Phase 3 - Week 9)
- **Task 7.1**: Recommendation Engine Foundation ✅ (Completed)
- **Task 7.2**: Rationale Generation ✅ (Completed)
- **Task 7.3**: OpenAI Integration ✅ (Completed)
- **Task 7.4**: Partner Offer Service ✅ (Completed)
- **Task 8.1**: Consent Guardrails ✅ (Completed)
- **Task 8.2**: Eligibility Validation ✅ (Completed)
- **Task 8.3**: Tone Validation ✅ (Completed)
- **Task 8.4**: Regulatory Disclaimers ✅ (Completed)
- **Task 9.1**: Decision Trace Generation ✅ (Completed)
- **Task 9.2**: Evaluation Service ✅ (Completed)

### Immediate (Phase 4)
- **Task 11.3**: Recommendations View ✅ (Completed)
- **Task 11.4**: Recommendation Detail View
- **Task 12.1**: Data Upload UI ✅ (Completed)
- **Task 12.2**: Consent Management UI
- **Task 12.3**: Mobile Responsiveness ✅
- **Task 12.4**: UI Polish & Accessibility ✅

### Future (Phase 2 & 3)
- **Task 4.1**: Data Ingestion Service ✅ (Completed)
- **Task 4.2**: Data Validation Service ✅ (Completed)
- **Task 4.3**: Synthetic Data Generator ✅ (Completed)
- **Task 5.1**: Subscription Detection ✅ (Completed)
- **Task 5.2**: Savings Pattern Detection ✅ (Completed)
- **Task 5.3**: Credit Utilization Detection ✅ (Completed)
- **Task 5.4**: Income Stability Detection ✅ (Completed)
- **Task 5.5**: Feature Caching ✅ (Completed)
- **Task 6.1**: Persona Assignment Logic ✅ (Completed)
- **Task 6.2**: Priority Logic ✅ (Completed - part of Task 6.1)
- **Task 6.3**: Persona History Tracking ✅ (Completed - API endpoint moved to Task 13.1)
- **Task 7.1**: Recommendation Engine Foundation ✅ (Completed)
- **Task 7.2**: Rationale Generation ✅ (Completed)
- **Task 7.3**: OpenAI Integration ✅ (Completed)
- **Task 7.4**: Partner Offer Service ✅ (Completed)
- **Task 8.1**: Consent Guardrails ✅ (Completed)
- **Task 8.2**: Eligibility Validation ✅ (Completed)
- **Task 8.3**: Tone Validation ✅ (Completed)
- **Task 8.4**: Regulatory Disclaimers ✅ (Completed)
- **Task 9.1**: Decision Trace Generation ✅ (Completed)
- **Task 9.2**: Evaluation Service ✅ (Completed)
- **Task 9.3**: Report Generation ✅ (Completed)

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
  - Feature signals caching (24-hour TTL) - Task 5.5
  - OpenAI content caching (7-day TTL) - Task 7.3
- React Query caching for API responses (frontend)
- Token refresh mechanism to minimize re-authentication
- Cache invalidation on data updates to ensure consistency
- OpenAI rate limiting (100 requests/minute) to prevent quota exhaustion
- OpenAI retry logic with exponential backoff for reliability
- Fallback to pre-generated templates when OpenAI unavailable

---

### ✅ Task 18.1 - Operator Analytics Dashboard
- **Backend Analytics Endpoint**: Implemented comprehensive analytics endpoint (`GET /api/v1/operator/analytics`) in `backend/app/api/v1/endpoints/operator.py`:
  - Integrated with EvaluationService from service layer to calculate all metrics
  - Coverage metrics: users with persona, behaviors, both (counts and percentages)
  - Explainability metrics: recommendations with rationales, data points citations, quality score (0-10)
  - Performance metrics: latency percentiles (p50, p95, p99, mean, min, max), within-target percentage (<5s)
  - Engagement metrics: total users, active users (users with recommendations), recommendations sent/viewed/actioned
  - Error handling with graceful fallback if EvaluationService unavailable
  - Proper metric mapping to frontend SystemAnalytics interface
- **Frontend Analytics Dashboard**: Created comprehensive analytics page (`frontend/src/pages/OperatorAnalytics.tsx`):
  - Installed recharts library for data visualization
  - Four key metric cards with quick stats and icons (Coverage, Explainability, Performance, Engagement)
  - Coverage metrics bar chart showing users with persona, behaviors, and both with percentages and counts
  - Explainability metrics bar chart with rationale coverage and quality score visualization (0-10 scale with progress bar)
  - Performance metrics line chart displaying latency percentiles (p50, p95, p99, mean) in seconds with within-target percentage indicator
  - Engagement metrics bar chart showing recommendations sent, viewed, and actioned counts
  - Detailed metrics tables for performance (latency breakdown) and engagement (user activity breakdown)
  - Export buttons (JSON/CSV) with placeholder for future implementation
  - Back navigation to operator dashboard
  - Loading states, error handling with retry, and mobile-responsive design
  - All charts use ResponsiveContainer for mobile compatibility
  - Proper TypeScript typing with SystemAnalytics interface
- **Integration**: Frontend uses operatorService.getAnalytics() to fetch metrics, React Query for caching (5-minute stale time), proper error boundaries
- **Key Files**:
  - `backend/app/api/v1/endpoints/operator.py` - Analytics endpoint implementation
  - `frontend/src/pages/OperatorAnalytics.tsx` - Analytics dashboard page
  - `frontend/src/services/operatorService.ts` - Analytics service method (already existed)
  - `frontend/package.json` - Added recharts dependency

---

## Recent Updates (2025-11-04)

### ✅ Task 18.2 - User Detail View (Operator)
- **TimePeriodSelector Component**: Updated to support 3 time periods:
  - 30 Days (signals_30d)
  - 180 Days (signals_180d)
  - 365 Days (signals_365d, with fallback to signals_180d)
  - Component located at `frontend/src/components/TimePeriodSelector.tsx`
- **UserDetail Component**: Enhanced operator user detail view (`frontend/src/pages/UserDetail.tsx`):
  - Time period selector for switching between 30-day, 180-day, and 365-day analysis
  - Complete user profile display (name, email, role, consent status)
  - Current persona badge display
  - Behavioral signals display based on selected time period:
    - Income analysis with payroll deposits, payment frequency, variability, cash flow buffer
    - Period-specific labels (e.g., "Income Analysis (30 Days)")
  - Accounts section with detailed account information
  - Transactions section with pagination (50 per page)
  - Liabilities section with APR, payments, due dates
  - Recommendations section:
    - Displays all recommendations for the user
    - Shows recommendation type (education/partner_offer), status (pending/approved/rejected)
    - Displays title, content, and rationale
    - Includes creation date and status badges
  - Persona history timeline:
    - Visual timeline showing persona assignment history
    - Uses PersonaHistoryTimeline component
    - Shows current and previous personas with assignment dates
- **Service Layer Updates**:
  - Updated `adminService.ts` BehavioralProfile interface to support `signals_365d`
  - Added `getUserRecommendations()` method to fetch user recommendations
  - Added `getUserPersonaHistory()` method to fetch persona history
  - Updated `profileService.ts` BehavioralProfile interface to include `signals_365d`
- **Component Updates**:
  - Updated `ProfileBehavioralSignals` component to support 365d period
  - Updated `Profile.tsx` page to support all three time periods (30d, 180d, 365d)
- **Type Safety**: All TypeScript interfaces updated to support new time periods, no linter errors
- **Key Features**:
  - Graceful fallback: uses signals_180d when signals_365d is not available
  - Loading states with skeleton screens (6 sections)
  - Error handling with retry functionality
  - Mobile-responsive design
  - Proper data fetching with React Query caching

**Key Files**:
- `frontend/src/pages/UserDetail.tsx` - Main user detail view component
- `frontend/src/components/TimePeriodSelector.tsx` - Updated time period selector
- `frontend/src/components/ProfileBehavioralSignals.tsx` - Updated to support 365d
- `frontend/src/services/adminService.ts` - Added recommendation and persona history methods
- `frontend/src/services/profileService.ts` - Updated BehavioralProfile interface
- `frontend/src/pages/Profile.tsx` - Updated to support 365d period

### ✅ Task 18.3 - Evaluation System Integration
- **Backend Export Endpoints**: Added three new export endpoints in `backend/app/api/v1/endpoints/operator.py`:
  - `GET /api/v1/operator/analytics/export/json` - Exports all evaluation metrics as JSON file download
  - `GET /api/v1/operator/analytics/export/csv` - Exports flattened metrics as CSV file download
  - `GET /api/v1/operator/analytics/export/summary` - Generates Markdown summary report download
  - All endpoints use `ReportGenerator` service from service layer
  - Temporary file generation using `tempfile.TemporaryDirectory` with automatic cleanup
  - Proper Content-Disposition headers for file downloads with timestamped filenames
  - Requires operator role or higher (uses `require_operator` dependency)
- **Fairness Metrics Integration**: Enhanced `/api/v1/operator/analytics` endpoint to include fairness metrics:
  - `persona_balance_score`: Overall balance score across personas (0.0-1.0)
  - `persona_distribution`: Count and percentage of users per persona
  - `signal_detection_by_persona`: Signal detection counts per persona
- **Frontend Export Functionality**: Implemented export functionality in `frontend/src/pages/OperatorAnalytics.tsx`:
  - Three export buttons: Export JSON, Export CSV, Summary Report
  - Export state management with loading indicators per button
  - Blob download handling using `URL.createObjectURL` and temporary anchor elements
  - Error handling with user-friendly alerts
  - Timestamped filenames (YYYYMMDD format)
- **Frontend Service Updates**: Enhanced `frontend/src/services/operatorService.ts`:
  - Added `exportMetricsJSON()` method returning Blob
  - Added `exportMetricsCSV()` method returning Blob
  - Added `exportSummaryReport()` method returning Blob
  - Updated `SystemAnalytics` interface to include `fairness` property
- **Fairness Metrics Display**: Added fairness metrics visualization in OperatorAnalytics page:
  - Persona Balance Score display with progress bar (0.0-1.0 scale)
  - Persona Distribution table showing:
    - Persona name (Persona 1-5)
    - Recommendation counts per persona with percentage
    - User counts per persona with percentage
  - Conditional rendering when fairness data is available
- **API Client Updates**: Modified `frontend/src/services/api.ts`:
  - Updated response interceptor to skip JSON parsing for blob responses
  - Checks `response.config.responseType === 'blob'` before processing
  - Allows blob responses to pass through without transformation
- **Bug Fixes**:
  - Fixed SQL DISTINCT error with JSON columns: Changed from `.distinct()` on full query to `distinct(UserModel.user_id)` for active users count
  - Fixed React hooks order violation: Moved `useState` hook to top of component before any early returns
  - Temporarily removed RecommendationStatus enum filter to avoid PostgreSQL enum comparison issues (uses total count instead)
- **Integration**: Frontend integrates with backend export endpoints, handles file downloads properly, displays all metrics including fairness
- **Key Files**:
  - `backend/app/api/v1/endpoints/operator.py` - Added export endpoints and fairness metrics integration
  - `frontend/src/pages/OperatorAnalytics.tsx` - Added export functionality and fairness metrics display
  - `frontend/src/services/operatorService.ts` - Added export methods and updated SystemAnalytics interface
  - `frontend/src/services/api.ts` - Updated interceptor for blob response handling

### ✅ Task 18.1 - Operator Analytics Dashboard
- **Backend Analytics Endpoint**: Enhanced `/api/v1/operator/analytics` endpoint (`backend/app/api/v1/endpoints/operator.py`):
  - Coverage metrics: users with persona, behaviors, both (counts and percentages)
  - Explainability metrics: recommendations with rationales, data points citations, quality score (0-10)
  - Performance metrics: latency percentiles (p50, p95, p99, mean, min, max), within-target percentage (<5s)
  - Engagement metrics: total users, active users (users with recommendations), recommendations sent/viewed/actioned
  - Error handling with graceful fallback if EvaluationService unavailable
  - Proper metric mapping to frontend SystemAnalytics interface
- **Frontend Analytics Dashboard**: Created comprehensive analytics page (`frontend/src/pages/OperatorAnalytics.tsx`):
  - Installed recharts library for data visualization
  - Four key metric cards with quick stats and icons (Coverage, Explainability, Performance, Engagement)
  - Coverage metrics bar chart showing users with persona, behaviors, and both with percentages and counts
  - Explainability metrics bar chart with rationale coverage and quality score visualization (0-10 scale with progress bar)
  - Performance metrics line chart displaying latency percentiles (p50, p95, p99, mean) in seconds with within-target percentage indicator
  - Engagement metrics bar chart showing recommendations sent, viewed, and actioned counts
  - Detailed metrics tables for performance (latency breakdown) and engagement (user activity breakdown)
  - Export buttons (JSON/CSV) with placeholder for future implementation
  - Back navigation to operator dashboard
  - Loading states, error handling with retry, and mobile-responsive design
  - All charts use ResponsiveContainer for mobile compatibility
  - Proper TypeScript typing with SystemAnalytics interface
- **Integration**: Frontend uses operatorService.getAnalytics() to fetch metrics, React Query for caching (5-minute stale time), proper error boundaries
- **Key Files**:
  - `backend/app/api/v1/endpoints/operator.py` - Analytics endpoint implementation
  - `frontend/src/pages/OperatorAnalytics.tsx` - Analytics dashboard page
  - `frontend/src/services/operatorService.ts` - Analytics service method (already existed)
  - `frontend/package.json` - Added recharts dependency

### ✅ Task 17.4 - Approve/Reject Functionality
- **ConfirmationDialog Component**: Created reusable dialog component (`frontend/src/components/ConfirmationDialog.tsx`):
  - Supports multiple dialog types (approve, reject, confirm, warning, info)
  - Customizable title, message, confirm/cancel labels
  - Optional text input for rejection reasons (required validation)
  - Loading states and disabled states
  - Full accessibility support (ARIA labels, keyboard navigation, focus management)
- **Enhanced OperatorReview Page**:
  - Replaced `window.confirm()`/`window.prompt()` with proper React dialogs
  - Added approve confirmation dialog with clear messaging
  - Enhanced reject dialog with required reason input field
  - Implemented modify recommendation functionality:
    - Inline editing mode for title, content, and rationale
    - Save/Cancel buttons with loading states
    - Unsaved changes warning indicator
    - Change tracking (only sends modified fields)
- **Updated operatorService**:
  - Added `modifyRecommendation()` method for editing recommendations
  - Updated `rejectRecommendation()` to send reason in request body (not query param)
- **Backend Schemas**:
  - Created `RecommendationRejectRequest` schema (reason: string, 1-500 chars)
  - Created `RecommendationModifyRequest` schema (optional title, content, rationale)
- **Backend Endpoints**:
  - Updated `reject_recommendation()` to accept reason in request body via `Body(...)`
  - Added `modify_recommendation()` PUT endpoint (`/api/v1/operator/review/{recommendation_id}`)
  - Implemented comprehensive logging for all operator actions:
    - Approve: logs operator ID, email, recommendation ID
    - Reject: logs operator ID, email, recommendation ID, and rejection reason (truncated if >100 chars)
    - Modify: logs operator ID, email, recommendation ID, and which fields were modified

**Key Files**:
- `frontend/src/components/ConfirmationDialog.tsx` - Reusable confirmation dialog component
- `frontend/src/pages/OperatorReview.tsx` - Enhanced with modify functionality and improved dialogs
- `frontend/src/services/operatorService.ts` - Added modifyRecommendation method
- `backend/app/api/v1/schemas/recommendations.py` - Added RecommendationRejectRequest and RecommendationModifyRequest schemas
- `backend/app/api/v1/endpoints/operator.py` - Updated reject endpoint, added modify endpoint, added logging

### ✅ Database Seeding Enhancements
- **Enhanced Seeding Script**: Updated `backend/scripts/seed_db.py` to support multiple examples per persona:
  - Default: 50 users (10 per persona for personas 1-5)
  - Added `--users-per-persona` parameter to control distribution
  - Ensures balanced distribution across all personas
  - Shows target persona distribution during creation
  - Displays final persona distribution after assignment based on detected behavior
  - Each user gets a unique UUID automatically assigned
- **Synthetic Data Generator Updates**: Updated `scripts/synthetic_data_generator.py`:
  - Removed `user_id` from generated JSON files (security improvement)
  - User ID is now assigned by authenticated user during upload
  - Files contain only `accounts`, `transactions`, and `liabilities`
  - Export methods use generated UUIDs for filenames instead of user_id

### ✅ Synthetic Data Generator Fixes & Database Seeding
- **Fixed Income Deposit Generation**: Updated `scripts/synthetic_data_generator.py` to correctly generate income deposits:
  - Income transactions now use **positive amounts** (Plaid convention: deposits = positive)
  - Category set to `"PAYROLL"` (was incorrectly using "Financial/Income")
  - Payment channel set to `"ACH"` (was incorrectly using "online")
  - Added varied merchant names (e.g., "Direct Deposit", "Payroll Deposit", "Salary Deposit")
- **Fixed Spending Transactions**: Ensured all spending transactions explicitly use negative amounts (`-abs(amount)`)
- **Fixed Transfer Transactions**: Modified to create paired transactions:
  - Transfer out from checking (negative amount, `TRANSFER_OUT` category)
  - Transfer in to savings (positive amount, `TRANSFER_IN` category, same date)
- **Updated Validator**: Added `"ACH"` to `VALID_PAYMENT_CHANNELS` in `service/app/ingestion/validator.py`
- **Regenerated Synthetic Data**: All 100 synthetic data files regenerated with corrected income deposits (validation passes: 0 errors, 0 warnings)
- **Database Seeding Updates**:
  - Updated `backend/scripts/seed_db.py` to ensure all users have consistent password (`TestPassword123!`) for testing
  - Modified `create_test_user()` to update existing users' passwords to maintain consistency
  - Fixed path resolution for `synthetic_data` directory (now checks project root)
  - Seed script successfully loads data for multiple users

**Key Files**:
- `scripts/synthetic_data_generator.py` - Fixed income, spending, and transfer transaction generation
- `service/app/ingestion/validator.py` - Added "ACH" payment channel support
- `backend/scripts/seed_db.py` - Improved password consistency and path resolution
- `scripts/test_generation_calculations.py` - Test script for verifying financial metrics

### ✅ Monthly Income Management Feature
- **Database Schema**: Added `monthly_income` field to User model:
  - Type: `Numeric(15, 2)` (nullable)
  - Migration: `916ff7d6f997_add_monthly_income_to_users`
  - Allows users to manually set their monthly income or use calculated income from transactions
- **Backend API Updates**:
  - Updated `UserProfileResponse` schema to include `monthly_income` field
  - Updated `UserProfileUpdateRequest` schema to accept `monthly_income` (validation: `ge=0`)
  - Enhanced `/api/v1/users/me` PUT endpoint to handle income updates
  - Added Decimal to float conversion validator for proper API serialization
- **Frontend Components**:
  - Created `IncomeSettings` component (`frontend/src/components/IncomeSettings.tsx`):
    - Allows users to view and edit their monthly income
    - Shows current income or "Not set - will be calculated from transaction data"
    - Includes validation for positive numbers
    - Provides option to clear income (falls back to calculated income)
  - Updated Settings page to include Income Settings section at the top
  - Updated `userService` to include `monthly_income` in profile interface and update method
- **User Experience**:
  - Users can set their monthly income in Settings → Income Settings
  - Income can be left blank to use calculated income from transaction data
  - Income is validated to be non-negative
  - Income is stored in database and returned in all profile responses

**Key Files**:
- `backend/app/models/user.py` - Added `monthly_income` field
- `backend/alembic/versions/916ff7d6f997_add_monthly_income_to_users.py` - Migration
- `backend/app/api/v1/schemas/user.py` - Updated schemas with income field
- `backend/app/api/v1/endpoints/user.py` - Updated profile endpoint to handle income
- `frontend/src/components/IncomeSettings.tsx` - New income settings component
- `frontend/src/pages/Settings.tsx` - Added Income Settings section
- `frontend/src/services/userService.ts` - Updated to include income field

**Next Steps** (Optional):
- Update dashboard/profile to display income (stored or calculated)
- Update income calculation services to prefer stored income when available
- Show income in admin user detail view

### ✅ Persona Assignment with OpenAI Integration
- **OpenAI-Enhanced Rationales**: Integrated OpenAI into `PersonaAssignmentService` to generate personalized, empathetic rationales:
  - Enhanced `service/app/features/persona_assignment.py` with OpenAI client initialization
  - Added `_generate_openai_rationale()` method that creates context-aware rationales
  - Rationales cite specific data points from behavioral signals (utilization rates, subscription counts, income patterns, etc.)
  - Falls back to rule-based rationales when OpenAI API key is not configured
  - Rationales are stored in both `UserProfile` and `PersonaHistory` tables
- **UUID Serialization Fixes**: Fixed JSON serialization issues for persona assignment:
  - Added `_serialize_signals_for_json()` helper function to recursively convert UUIDs and dates to strings
  - Applied serialization to `UserProfile.signals_30d` and `signals_180d` before database storage
  - Applied serialization to `PersonaHistory.signals` before database storage
  - Fixed feature cache serialization in `service/app/common/feature_cache.py` to prevent UUID serialization warnings
- **Persona Backfill Script**: Created `backend/scripts/assign_personas.py`:
  - Finds users with transaction data but no assigned persona
  - Assigns personas using `PersonaAssignmentService` with OpenAI integration
  - Supports `--dry-run` mode for previewing changes
  - Includes proper error handling and transaction rollback on failures
  - Successfully assigned personas to all 5 users with data
- **Automatic Persona Assignment**: Verified that automatic persona assignment works:
  - After successful data ingestion in `process_upload_async()`, personas are automatically assigned
  - Creates/updates `UserProfile` with persona and signals
  - Uses OpenAI for enhanced rationales if API key is configured
  - Errors are logged but don't fail the upload process

**Key Files**:
- `service/app/features/persona_assignment.py` - Added OpenAI integration and UUID serialization
- `service/app/common/feature_cache.py` - Fixed UUID serialization in cache
- `backend/scripts/assign_personas.py` - New backfill script for existing users
- `backend/app/api/v1/endpoints/data_upload.py` - Automatic persona assignment after ingestion

**Usage**:
- Automatic: Personas are assigned automatically after data upload and processing
- Manual Backfill: Run `python backend/scripts/assign_personas.py` to assign personas to existing users
- Dry Run: Use `--dry-run` flag to preview changes without committing

### ✅ Analytics Page Bug Fixes (Task 18.3)
- **Fixed SQL DISTINCT Error**:
  - PostgreSQL cannot use DISTINCT with JSON columns (oauth_providers)
  - Changed active users query from `.distinct()` on full UserModel to `distinct(UserModel.user_id)`
  - Resolves `psycopg2.errors.UndefinedFunction: could not identify an equality operator for type json` error
- **Fixed React Hooks Order Violation**:
  - Moved `useState` hook for `isExporting` to top of OperatorAnalytics component
  - React hooks must be called unconditionally before any early returns
  - Resolves `Rendered more hooks than during the previous render` error
- **Fixed Enum Comparison Issue**:
  - Temporarily removed RecommendationStatus enum filter from recommendations_viewed query
  - PostgreSQL enum type comparison was causing `InvalidTextRepresentation` errors
  - Using total recommendations count instead (approximation acceptable for now)
  - TODO: Fix enum comparison when database enum type is properly configured
- **Fixed Frontend Error Handling**:
  - Updated API interceptor to handle blob responses correctly
  - Skips JSON parsing for `responseType: 'blob'` requests
  - Prevents blob responses from being incorrectly parsed as JSON

**Key Files**:
- `backend/app/api/v1/endpoints/operator.py` - Fixed SQL queries and enum handling
- `frontend/src/pages/OperatorAnalytics.tsx` - Fixed React hooks order
- `frontend/src/services/api.ts` - Fixed blob response handling

**Known Issues** (Non-Critical):
- CORS errors: Expected if backend isn't running or CORS is misconfigured
- 404 errors for `/api/v1/users/{user_id}/profile`: Endpoint may not exist yet for operator/admin use

---

## Recent Changes (November 2025)

### Income Signal Caching Fix (November 4, 2025)

**Problem**: Income data was showing "insufficient_data" in the frontend even though payroll transactions were present in the database. The issue was caused by **three layers of caching** preventing fresh data from being displayed:

1. **Feature Cache** (Redis) - `features:income:{user_id}` - 24h TTL
2. **Profile API Response Cache** (Redis) - `profile:{user_id}` - 5min TTL  
3. **React Query Cache** (Frontend) - Browser cache

**Root Cause**: When signals were regenerated using `regenerate_signals.py`, only the feature cache layer was cleared, but the profile API response cache was still serving stale data. Additionally, the `generate_income_signals()` method had a `@cache_feature_signals` decorator that returned cached results even when underlying data had changed.

**Solution Implemented**:

1. **Enhanced `backend/scripts/regenerate_signals.py`**:
   - Added import for `invalidate_user_profile_cache()` from `app.core.cache_service`
   - Clears all feature caches (income, subscriptions, savings, credit) before regeneration
   - Clears profile API response cache before and after database update
   - Calls `calculate_income_signals()` directly to bypass the `@cache_feature_signals` decorator
   - Added `_serialize_for_json()` helper function to convert UUIDs to strings before saving to database (prevents JSON serialization errors)
   - Clears profile cache again after database commit to ensure fresh data on next API call

2. **Removed Temporary Fix**:
   - Deleted `backend/scripts/fix_income_signals.py` as it's no longer needed

**Key Files Modified**:
- `backend/scripts/regenerate_signals.py` - Enhanced with comprehensive cache clearing
- `backend/scripts/fix_income_signals.py` - **DELETED** (temporary fix no longer needed)

**Cache Invalidation Strategy**:
- **Before Regeneration**: Clear all feature caches and profile API cache
- **During Regeneration**: Call calculation methods directly (bypass decorator caching)
- **After Database Update**: Clear profile API cache again to ensure fresh data on next request
- **Frontend**: Hard refresh (Ctrl+Shift+R) or backend restart clears React Query cache

**Result**: All 23 users now have correctly regenerated income signals stored in the database, and the caching layers are properly invalidated. Income data displays correctly in the frontend showing:
- Estimated Monthly Income: $4,500.00
- Payment Frequency: biweekly (6 deposits detected)
- Income Stability: low variability (0.0%)
- Payroll Deposits table with all 6 deposits

**Testing**: Verified that after running `regenerate_signals.py`, the frontend displays fresh income data without requiring manual cache clearing.

### UI/UX Improvements & Security Enhancements (November 5, 2025)

**User Management UI Separation**:
- **Separated Users and Staff**: Created separate management interfaces for regular users vs operators/admins:
  - `UsersList.tsx` component now filters out operators/admins (only shows `role='user'`)
  - Created new `StaffList.tsx` component for displaying operators and admins
  - Created `StaffManagement.tsx` page with tabs: "Users" and "Staff"
  - Dashboard shows `UsersList` directly for admins (regular users only)
  - Staff management accessible via `/admin/management` route (admin-only)
- **Navigation Updates**: Updated navigation to hide user-specific tabs for operators/admins:
  - Operators and admins don't see: Profile, Recommendations, Upload tabs
  - All users see: Dashboard, Settings
  - Admins additionally see: Management tab (links to staff management)
- **Component Updates**:
  - `UsersList.tsx` - Removed Role column (all entries are regular users), filters to `role='user'`
  - `StaffList.tsx` - New component displaying only operators/admins with role badges
  - `StaffManagement.tsx` - New page with tabbed interface for managing both groups
  - `Navigation.tsx` - Conditional navigation items based on user role
  - `Dashboard.tsx` - Shows UsersList for admins, removed direct link to management page

**Data Upload Security Enhancement**:
- **Removed user_id from Synthetic Data Files**: Enhanced security by removing `user_id` from generated files:
  - Updated `scripts/synthetic_data_generator.py` to NOT include `user_id` in JSON output
  - Files now contain only: `accounts`, `transactions`, `liabilities` (and optional `upload_timestamp`)
  - User ID is automatically assigned from authenticated user during upload (prevents users from uploading data for other users)
- **Parser Updates**: Updated `service/app/ingestion/parser.py`:
  - Parser ignores `user_id` if present in uploaded files (security measure)
  - Added documentation noting that user_id comes from authenticated user
- **Upload Flow**: Upload endpoint already correctly uses `current_user.user_id` from authentication:
  - No changes needed to upload endpoint - already secure
  - Ingestion service receives `user_id` as parameter (not from file)
  - Prevents users from specifying their own user_id in uploaded files

**Database Seeding Enhancements**:
- **Enhanced Seeding Script**: Updated `backend/scripts/seed_db.py`:
  - Default: 50 users (10 per persona for personas 1-5)
  - Added `--users-per-persona` parameter for flexible distribution
  - Ensures balanced distribution across all personas
  - Shows target persona distribution during user creation
  - Displays final persona distribution after assignment based on detected behavior
  - Each user gets unique UUID automatically assigned via `uuid.uuid4()`

**Key Files Modified**:
- `frontend/src/components/UsersList.tsx` - Filters out operators/admins, removed Role column
- `frontend/src/components/StaffList.tsx` - **NEW** - Staff management component
- `frontend/src/pages/StaffManagement.tsx` - **NEW** - Staff management page with tabs
- `frontend/src/pages/Dashboard.tsx` - Shows UsersList for admins
- `frontend/src/components/Navigation.tsx` - Conditional navigation based on role
- `frontend/src/App.tsx` - Added `/admin/management` route
- `scripts/synthetic_data_generator.py` - Removed user_id from output, updated export methods
- `service/app/ingestion/parser.py` - Ignores user_id from files
- `backend/scripts/seed_db.py` - Enhanced with persona distribution options

**Result**: 
- Regular users and staff are now properly separated in the UI
- Operators/admins have cleaner navigation without user-specific tabs
- Data upload is more secure - users cannot specify user_id in uploaded files
- Seeding script provides better control over persona distribution
- All changes maintain backward compatibility

---

**End of Memory Bank**

