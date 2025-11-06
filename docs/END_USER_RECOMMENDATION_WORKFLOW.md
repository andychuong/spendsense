# End User Recommendation Workflow

This document explains the complete workflow for how an end user receives personalized financial recommendations in SpendSense.

## Overview

The recommendation system follows a multi-step process that ensures user consent, data privacy, and quality control through operator review before recommendations are shown to users.

---

## Complete Workflow Steps

### Step 1: User Registration & Authentication

**User Action:**
- User creates an account via `POST /api/v1/auth/register`
- User logs in via `POST /api/v1/auth/login`
- Receives authentication tokens (access_token, refresh_token)

**System Actions:**
- Creates user record in `users` table
- Creates session record
- Default role: `USER` (regular end user)

**Database Tables:**
- `users` - User account created
- `sessions` - Active session created

---

### Step 2: Grant Consent (REQUIRED)

**User Action:**
- User grants consent via `POST /api/v1/consent` or through UI consent form

**System Actions:**
- Updates `users.consent_status = true`
- This is **mandatory** - without consent, no data processing occurs

**Why Required:**
- Protects user privacy
- Complies with data protection regulations
- Blocks all data processing until consent is granted

**Database Tables:**
- `users` - Consent status updated

---

### Step 3: Upload Financial Data

**User Action:**
- User uploads financial data file (JSON or CSV format) via `POST /api/v1/data/upload`
- File contains: `accounts`, `transactions`, `liabilities` arrays
- Maximum file size: 10MB

**System Actions (Synchronous):**
- Validates file type and size
- Uploads file to S3 storage
- Creates `data_uploads` record with status `PENDING`
- Returns upload_id to user

**System Actions (Asynchronous - Background Task):**
- Updates status to `PROCESSING`
- Calls `IngestionService` to parse and validate data
- Stores data in database:
  - `accounts` table
  - `transactions` table
  - `liabilities` table
- Updates upload status to `COMPLETED` or `FAILED`

**Database Tables:**
- `data_uploads` - Upload tracking record
- `accounts` - Financial accounts stored
- `transactions` - Transaction records stored
- `liabilities` - Credit card/loan data stored

**API Response:**
```json
{
  "upload_id": "uuid",
  "status": "pending",
  "message": "File uploaded successfully. Processing will begin shortly."
}
```

---

### Step 4: Feature Engineering (Automatic)

**Trigger:** Automatic after data upload completes

**System Actions:**
- **Service Layer** processes uploaded data:
  - `SubscriptionDetector` - Detects recurring subscriptions
  - `SavingsDetector` - Detects savings patterns
  - `CreditUtilizationDetector` - Detects credit card utilization
  - `IncomeStabilityDetector` - Detects income patterns

**Signals Generated:**
- **30-day window signals:**
  - Subscription count, monthly recurring spend
  - Savings growth rate, net inflow
  - Credit utilization percentages, interest charges
  - Income variability, cash-flow buffer

- **180-day window signals:**
  - Same as above but for longer time period
  - Used for comparison and trend analysis

**Caching:**
- Signals cached in Redis (TTL: 24 hours)
- Cache key format: `signals:{user_id}:{window}`

**Database Tables:**
- `user_profiles` - Signals stored in `signals_30d` and `signals_180d` JSON fields

**Example Signals:**
```json
{
  "signals_30d": {
    "subscriptions": {
      "subscription_count": 5,
      "total_recurring_spend": 125.50,
      "subscription_share_percent": 15.2
    },
    "credit": {
      "critical_utilization_cards": [
        {
          "account_name": "Visa ending in 4523",
          "utilization_percent": 68.5,
          "current_balance": 3400.00,
          "credit_limit": 5000.00
        }
      ],
      "total_interest_paid_30d": 87.50
    }
  }
}
```

---

### Step 5: Persona Assignment (Automatic)

**Trigger:** Automatic after signals are generated (during data upload processing)

**System Actions:**
- `PersonaAssignmentService.assign_persona()` is called
- Checks persona criteria in priority order:
  1. **Persona 1: High Utilization** (utilization ≥50% OR interest charges OR minimum payments)
  2. **Persona 2: Variable Income Budgeter** (pay gap >45 days AND buffer <1 month)
  3. **Persona 3: Subscription-Heavy** (≥3 subscriptions AND ≥$50/month OR ≥10% spending)
  4. **Persona 4: Savings Builder** (savings growth ≥2% OR inflow ≥$200/month AND all utilizations <30%)
  5. **Persona 5: Custom Persona** (default fallback)

- Assigns highest priority persona that matches
- Creates/updates `UserProfile` with:
  - Assigned persona ID and name
  - Signals (30-day and 180-day)
  - Persona assignment timestamp

**Database Tables:**
- `user_profiles` - Persona assignment stored
- `user_persona_assignment` - Persona assignment history

**Example Assignment:**
```json
{
  "persona_id": 1,
  "persona_name": "High Utilization",
  "rationale": "User has credit card at 68% utilization with $87/month in interest charges",
  "signals_30d": {...},
  "signals_180d": {...}
}
```

---

### Step 6: Recommendation Generation

**Trigger:** Manual (via operator endpoint or script)

**Note:** Recommendations are NOT automatically generated after persona assignment. They must be triggered by:
- An operator via `POST /api/v1/operator/users/{user_id}/generate-recommendations`
- A script (e.g., `generate_all_recommendations.py`)
- Or a scheduled job (future enhancement)

**System Actions:**

1. **Consent Check:**
   - Verifies `users.consent_status = true`
   - Blocks generation if consent not granted

2. **Get User Profile:**
   - Retrieves `UserProfile` with persona and signals
   - Verifies persona is assigned

3. **Select Recommendations:**
   - **Education Items:** Selects 3-5 items matching persona from `EDUCATION_CATALOG`
   - **Partner Offers:** Selects 1-3 offers matching persona and eligibility from `PARTNER_OFFER_CATALOG`

4. **Generate Rationales:**
   - Creates personalized "because" explanations for each recommendation
   - Cites specific data points: account numbers (last 4 digits), amounts, dates
   - Example: *"We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could improve your credit score and reduce interest charges of $87/month."*

5. **Apply Guardrails:**
   - **Consent Guardrails:** Verifies consent is still granted
   - **Eligibility Guardrails:** Checks user eligibility for partner offers (credit score, income, existing products)
   - **Tone Validation:** Ensures language is empowering, not shaming
   - Filters out harmful products (payday loans, etc.)

6. **Store Recommendations:**
   - Creates `recommendations` records with status `PENDING`
   - Each recommendation includes:
     - `type`: `education` or `partner_offer`
     - `title`: Recommendation title
     - `content`: Full recommendation content
     - `rationale`: Personalized "because" explanation
     - `status`: `pending` (awaiting operator review)
     - `persona_id`: Assigned persona ID

**Database Tables:**
- `recommendations` - Recommendations stored with `status='pending'`

**Example Recommendation:**
```json
{
  "recommendation_id": "uuid",
  "user_id": "uuid",
  "type": "education",
  "title": "Debt Paydown Strategies: The Snowball vs. Avalanche Method",
  "content": "Learn two proven strategies...",
  "rationale": "We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could significantly improve your credit score. It could also help you save on interest charges (you paid $87.50 last month).",
  "status": "pending",
  "persona_id": 1
}
```

---

### Step 7: Operator Review (Required)

**User Action:** None (this is a platform operator action)

**System Actions:**
- Platform operator reviews recommendations via operator dashboard
- Reviews recommendation queue via `GET /api/v1/operator/review`
- For each recommendation, operator can:
  - **Approve:** `POST /api/v1/operator/review/{recommendation_id}/approve`
  - **Reject:** `POST /api/v1/operator/review/{recommendation_id}/reject`
  - **Modify:** `PUT /api/v1/operator/review/{recommendation_id}` (edit title, content, rationale)

**Database Tables:**
- `recommendations` - Status updated to `approved` or `rejected`

**Why Required:**
- Quality control
- Compliance verification
- Content accuracy check
- Prevents harmful recommendations from reaching users

---

### Step 8: User Views Recommendations

**User Action:**
- User navigates to Recommendations page in UI
- Frontend calls `GET /api/v1/recommendations`
- Can filter by:
  - `status`: `approved`, `pending`, `rejected` (users see only `approved`)
  - `type`: `education`, `partner_offer`
  - Sorting: `date`, `relevance`, `type`
  - Pagination: `skip`, `limit`

**System Actions:**
- Verifies user consent (if consent revoked, returns 403 Forbidden)
- Queries `recommendations` table filtered by:
  - `user_id = current_user.user_id`
  - `status = 'approved'` (only approved recommendations are visible)
- Returns recommendations with:
  - Title, content, rationale
  - Type (education or partner_offer)
  - Created date
  - Personalized data points

**API Response:**
```json
{
  "items": [
    {
      "recommendation_id": "uuid",
      "type": "education",
      "title": "Debt Paydown Strategies: The Snowball vs. Avalanche Method",
      "content": "Learn two proven strategies...",
      "rationale": "We noticed your Visa ending in 4523 is at 68% utilization...",
      "status": "approved",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "recommendation_id": "uuid",
      "type": "partner_offer",
      "title": "Balance Transfer Credit Card - 0% APR for 18 Months",
      "content": "Transfer high-interest credit card debt...",
      "rationale": "Based on your current credit utilization...",
      "status": "approved",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

**Database Tables:**
- `recommendations` - Read-only query

**Caching:**
- Recommendations cached in Redis (TTL: 1 hour)
- Cache key: `recommendations:{user_id}`

---

### Step 9: User Provides Feedback (Optional)

**User Action:**
- User rates recommendation helpfulness
- User submits feedback via `POST /api/v1/recommendations/{recommendation_id}/feedback`

**System Actions:**
- Stores feedback (currently logged, future: feedback table)
- Feedback includes:
  - `rating`: 1-5 stars
  - `helpful`: boolean
  - `comment`: optional text

**Database Tables:**
- Feedback table (future enhancement)
- Currently logged for analytics

---

## Workflow Summary Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     END USER WORKFLOW                            │
└─────────────────────────────────────────────────────────────────┘

1. REGISTRATION
   POST /api/v1/auth/register
   ↓
   User account created

2. LOGIN
   POST /api/v1/auth/login
   ↓
   Access token received

3. GRANT CONSENT (Required!)
   POST /api/v1/consent
   ↓
   consent_status = true

4. UPLOAD DATA
   POST /api/v1/data/upload
   ↓
   File uploaded to S3
   ↓
   [Background Processing]
   ↓
   Data ingested → accounts, transactions, liabilities stored

5. FEATURE ENGINEERING (Automatic)
   Service Layer detects signals
   ↓
   user_profiles.signals_30d and signals_180d populated

6. PERSONA ASSIGNMENT (Automatic)
   PersonaAssignmentService.assign_persona()
   ↓
   user_profiles.persona_id assigned (1-5)

7. RECOMMENDATION GENERATION (Manual Trigger)
   POST /api/v1/operator/users/{user_id}/generate-recommendations
   ↓
   Recommendations created with status='pending'
   ↓
   - 3-5 education items
   - 1-3 partner offers
   - Each with personalized rationale

8. OPERATOR REVIEW (Required)
   Operator approves/rejects recommendations
   ↓
   recommendations.status = 'approved'

9. USER VIEWS RECOMMENDATIONS
   GET /api/v1/recommendations?status=approved
   ↓
   User sees approved recommendations with personalized content

10. USER PROVIDES FEEDBACK (Optional)
    POST /api/v1/recommendations/{id}/feedback
    ↓
    Feedback logged for analytics
```

---

## Key Points

### Consent is Mandatory
- **No data processing** occurs without consent
- Consent checked at multiple stages:
  - Before feature engineering
  - Before persona assignment
  - Before recommendation generation
  - Before viewing recommendations

### Automatic vs Manual Steps

**Automatic (Happens Behind the Scenes):**
- Feature engineering (signals detection)
- Persona assignment
- Data validation and storage

**Manual (Requires Action):**
- User consent (user action)
- Data upload (user action)
- Recommendation generation (operator action)
- Operator review (operator action)

### Recommendation Status Flow

```
pending → approved → visible to user
         ↓
       rejected → hidden from user
```

- Users **only see** `approved` recommendations
- `pending` recommendations await operator review
- `rejected` recommendations are hidden

### Personalization

Every recommendation includes:
1. **Personalized Content:** Matched to user's persona
2. **Data-Driven Rationale:** Cites specific account numbers, amounts, dates
3. **Plain Language:** No financial jargon
4. **Empowering Tone:** Supportive, not shaming

### Guardrails Applied

1. **Consent Guardrails:** Blocks processing without consent
2. **Eligibility Guardrails:** Only shows offers user is eligible for
3. **Tone Validation:** Ensures empowering, supportive language
4. **Harmful Product Filter:** Blocks payday loans, predatory products

---

## Example Timeline

**Day 1:**
- 10:00 AM - User registers and logs in
- 10:05 AM - User grants consent
- 10:10 AM - User uploads financial data file
- 10:11 AM - Upload processing starts (background)
- 10:15 AM - Processing completes, signals generated, persona assigned (Persona 1: High Utilization)

**Day 1 (Later):**
- 2:00 PM - Operator triggers recommendation generation
- 2:01 PM - 5 recommendations created (3 education, 2 partner offers) with status='pending'
- 2:30 PM - Operator reviews and approves 4 recommendations, rejects 1

**Day 2:**
- 9:00 AM - User logs in and views recommendations
- 9:01 AM - User sees 4 approved recommendations with personalized rationales
- 9:05 AM - User clicks on recommendation and provides feedback

---

## API Endpoints Summary

| Step | Endpoint | Method | User Action |
|------|----------|--------|-------------|
| 1 | `/api/v1/auth/register` | POST | Register account |
| 2 | `/api/v1/auth/login` | POST | Login |
| 3 | `/api/v1/consent` | POST | Grant consent |
| 4 | `/api/v1/data/upload` | POST | Upload data file |
| 5-6 | (Automatic) | - | - |
| 7 | `/api/v1/operator/users/{id}/generate-recommendations` | POST | (Operator) |
| 8 | `/api/v1/operator/review/{id}/approve` | POST | (Operator) |
| 9 | `/api/v1/recommendations` | GET | View recommendations |
| 10 | `/api/v1/recommendations/{id}/feedback` | POST | Submit feedback |

---

This workflow ensures that users receive high-quality, personalized recommendations while maintaining privacy, consent, and quality control throughout the process.

