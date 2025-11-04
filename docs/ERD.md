# SpendSense Database ERD (Entity Relationship Diagram)

**Version**: 1.0
**Date**: 2025-11-04
**Database**: PostgreSQL 16.10

---

## ERD Diagram

```mermaid
erDiagram
    USERS ||--o{ SESSIONS : "has"
    USERS ||--o| USER_PROFILES : "has"
    USERS ||--o{ DATA_UPLOADS : "uploads"
    USERS ||--o{ RECOMMENDATIONS : "receives"
    USERS ||--o{ RECOMMENDATIONS_APPROVED : "approves"
    USERS ||--o{ RECOMMENDATIONS_REJECTED : "rejects"
    USERS ||--o{ PERSONA_HISTORY : "has"

    USERS {
        uuid user_id PK
        string email UK "nullable"
        string phone_number UK "nullable"
        string password_hash "nullable"
        json oauth_providers "default: {}"
        enum role "user|operator|admin, default: user"
        boolean consent_status "default: false"
        string consent_version "default: '1.0'"
        timestamp created_at
        timestamp updated_at "nullable"
    }

    SESSIONS {
        uuid session_id PK
        uuid user_id FK
        string refresh_token UK "length: 1000"
        timestamp expires_at
        timestamp created_at
        timestamp last_used_at
    }

    DATA_UPLOADS {
        uuid upload_id PK
        uuid user_id FK
        string file_name
        integer file_size
        enum file_type "json|csv"
        string s3_key
        string s3_bucket
        enum status "pending|processing|completed|failed"
        json validation_errors "nullable"
        timestamp created_at
        timestamp updated_at "nullable"
        timestamp processed_at "nullable"
    }

    RECOMMENDATIONS {
        uuid recommendation_id PK
        uuid user_id FK
        enum type "education|partner_offer"
        string title
        text content
        text rationale
        enum status "pending|approved|rejected, default: pending"
        json decision_trace "nullable"
        timestamp created_at
        timestamp approved_at "nullable"
        uuid approved_by FK "nullable"
        timestamp rejected_at "nullable"
        uuid rejected_by FK "nullable"
        string rejection_reason "nullable"
    }

    USER_PROFILES {
        uuid profile_id PK
        uuid user_id FK UK
        integer persona_id "1-5"
        string persona_name
        json signals_30d "nullable"
        json signals_180d "nullable"
        timestamp updated_at
    }

    PERSONA_HISTORY {
        uuid history_id PK
        uuid user_id FK
        integer persona_id
        string persona_name
        timestamp assigned_at
        json signals "nullable"
    }
```

---

## Table Relationships

### 1. Users → Sessions (One-to-Many)
- One user can have multiple active sessions
- Foreign Key: `sessions.user_id` → `users.user_id`
- Cascade delete: Sessions are deleted when user is deleted

### 2. Users → User Profiles (One-to-One)
- One user has exactly one profile
- Foreign Key: `user_profiles.user_id` → `users.user_id` (UNIQUE)
- Cascade delete: Profile is deleted when user is deleted

### 3. Users → Data Uploads (One-to-Many)
- One user can have multiple data uploads
- Foreign Key: `data_uploads.user_id` → `users.user_id`
- Cascade delete: Uploads are deleted when user is deleted

### 4. Users → Recommendations (One-to-Many)
- One user can receive multiple recommendations
- Foreign Key: `recommendations.user_id` → `users.user_id`
- Cascade delete: Recommendations are deleted when user is deleted

### 5. Users → Recommendations (Approver/Rejector - One-to-Many)
- One operator/admin can approve/reject multiple recommendations
- Foreign Keys:
  - `recommendations.approved_by` → `users.user_id` (nullable)
  - `recommendations.rejected_by` → `users.user_id` (nullable)
- No cascade delete: Recommendations remain if operator is deleted

### 6. Users → Persona History (One-to-Many)
- One user can have multiple persona assignments over time
- Foreign Key: `persona_history.user_id` → `users.user_id`
- Cascade delete: History is deleted when user is deleted

---

## Table Details

### USERS
**Primary Key**: `user_id` (UUID)
**Unique Constraints**:
- `email` (nullable)
- `phone_number` (nullable)

**Indexes**:
- `ix_users_email` (unique)
- `ix_users_phone_number` (unique)

**Notes**:
- At least one of `email`, `phone_number`, or `oauth_providers` must be present
- `oauth_providers` stores JSON: `{"google": "provider_id", "github": "provider_id", ...}`
- `role` enum: `user`, `operator`, `admin`

---

### SESSIONS
**Primary Key**: `session_id` (UUID)
**Foreign Keys**: `user_id` → `users.user_id`

**Indexes**:
- `ix_sessions_user_id`
- `ix_sessions_refresh_token` (unique)
- `ix_sessions_expires_at`

**Notes**:
- Stores refresh tokens for JWT authentication
- `refresh_token` length: 1000 characters
- Used for token refresh and logout

---

### DATA_UPLOADS
**Primary Key**: `upload_id` (UUID)
**Foreign Keys**: `user_id` → `users.user_id`

**Indexes**:
- `ix_data_uploads_user_id`
- `ix_data_uploads_status`
- `ix_data_uploads_created_at`
- `ix_data_uploads_user_id_status` (composite)

**Notes**:
- Tracks file uploads (JSON/CSV) for Plaid data ingestion
- Files stored in S3, metadata in PostgreSQL
- `validation_errors` stores JSON array of validation issues

---

### RECOMMENDATIONS
**Primary Key**: `recommendation_id` (UUID)
**Foreign Keys**:
- `user_id` → `users.user_id`
- `approved_by` → `users.user_id` (nullable)
- `rejected_by` → `users.user_id` (nullable)

**Indexes**:
- `ix_recommendations_user_id`
- `ix_recommendations_status`
- `ix_recommendations_created_at`
- `ix_recommendations_approved_at`
- `ix_recommendations_user_id_status` (composite)

**Notes**:
- `type` enum: `education`, `partner_offer`
- `status` enum: `pending`, `approved`, `rejected`
- `decision_trace` stores JSON with decision-making logic
- Operator approval workflow: pending → approved/rejected

---

### USER_PROFILES
**Primary Key**: `profile_id` (UUID)
**Foreign Keys**: `user_id` → `users.user_id` (UNIQUE)

**Indexes**:
- `ix_user_profiles_user_id` (unique)
- `ix_user_profiles_persona_id`

**Constraints**:
- `check_persona_id_range`: `persona_id >= 1 AND persona_id <= 5`
- `persona_id` values:
  1. HIGH_UTILIZATION
  2. VARIABLE_INCOME_BUDGETER
  3. SUBSCRIPTION_HEAVY
  4. SAVINGS_BUILDER
  5. CUSTOM

**Notes**:
- One-to-one relationship with Users
- Stores current persona assignment and behavioral signals
- `signals_30d` and `signals_180d` store JSON with detected behaviors

---

### PERSONA_HISTORY
**Primary Key**: `history_id` (UUID)
**Foreign Keys**: `user_id` → `users.user_id`

**Indexes**:
- `ix_persona_history_user_id`
- `ix_persona_history_assigned_at`
- `ix_persona_history_user_id_assigned_at` (composite)

**Notes**:
- Tracks persona assignment changes over time
- Stores historical persona assignments with timestamps
- `signals` stores JSON snapshot of signals at assignment time

---

## Data Flow

### User Registration & Authentication Flow
1. User registers → `users` table created
2. User logs in → `sessions` table entry created
3. User grants consent → `users.consent_status` = `true`

### Data Ingestion Flow
1. User uploads file → `data_uploads` entry created (`status` = `pending`)
2. File validated → `data_uploads.status` = `processing`
3. File processed → `data_uploads.status` = `completed` or `failed`
4. Behavioral signals extracted → stored in `user_profiles.signals_30d` and `signals_180d`

### Persona Assignment Flow
1. Signals detected → `user_profiles` updated with `persona_id` and `persona_name`
2. Persona history → `persona_history` entry created with timestamp
3. Profile updated → `user_profiles.updated_at` updated

### Recommendation Flow
1. Recommendation generated → `recommendations` entry created (`status` = `pending`)
2. Operator reviews → `recommendations.status` = `approved` or `rejected`
3. If approved → `approved_by`, `approved_at` set
4. If rejected → `rejected_by`, `rejected_at`, `rejection_reason` set

---

## Indexes Summary

### Performance Indexes
- **User lookups**: `email`, `phone_number` (unique indexes)
- **Session management**: `refresh_token`, `expires_at`
- **Data upload tracking**: `user_id`, `status`, `created_at`
- **Recommendation queries**: `user_id`, `status`, `created_at`, `approved_at`
- **Persona queries**: `user_id`, `persona_id`, `assigned_at`

### Composite Indexes
- `ix_data_uploads_user_id_status`: Optimize user upload queries by status
- `ix_recommendations_user_id_status`: Optimize user recommendation queries by status
- `ix_persona_history_user_id_assigned_at`: Optimize persona history timeline queries

---

## Foreign Key Constraints

All foreign keys have CASCADE DELETE behavior except:
- `recommendations.approved_by` → `users.user_id` (SET NULL)
- `recommendations.rejected_by` → `users.user_id` (SET NULL)

This ensures that if an operator/admin is deleted, their approval/rejection records remain but the foreign key is set to NULL.

---

## JSON Fields

### users.oauth_providers
```json
{
  "google": "google_user_id_123",
  "github": "github_user_id_456",
  "facebook": "facebook_user_id_789",
  "apple": "apple_user_id_012"
}
```

### user_profiles.signals_30d / signals_180d
```json
{
  "subscriptions": {
    "monthly_recurring_spend": 150.50,
    "subscription_share": 0.15,
    "merchants": ["Netflix", "Spotify", "Amazon Prime"]
  },
  "savings": {
    "net_inflow": 500.00,
    "growth_rate": 0.05,
    "emergency_fund_coverage": 3.5
  },
  "credit": {
    "utilization_rate": 0.75,
    "cards_at_risk": ["acc_cc_001"],
    "minimum_payment_only": true
  },
  "income": {
    "stability_score": 0.85,
    "cash_flow_buffer": 2.5,
    "variable_income": false
  }
}
```

### data_uploads.validation_errors
```json
[
  {
    "type": "transaction",
    "transaction_id": "txn_999",
    "error": "account_id 'acc_invalid' does not exist",
    "severity": "error"
  }
]
```

### recommendations.decision_trace
```json
{
  "detected_signals": {
    "subscriptions": {...},
    "credit_utilization": {...}
  },
  "persona_assignment": {
    "persona_id": 1,
    "persona_name": "High Utilization",
    "matching_criteria": [...]
  },
  "guardrails_checks": {
    "consent": true,
    "eligibility": true,
    "tone_validation": true
  },
  "recommendation_logic": {
    "selected_education_items": [...],
    "selected_partner_offers": [...]
  }
}
```

### persona_history.signals
```json
{
  "subscriptions": {...},
  "savings": {...},
  "credit": {...},
  "income": {...}
}
```

---

**Document Status**: Draft
**Last Updated**: 2025-11-04

