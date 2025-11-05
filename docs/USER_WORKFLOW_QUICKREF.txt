#!/usr/bin/env python3
"""Quick reference script showing the complete user workflow."""

print("""
================================================================================
SPENDSENSE - NEW USER WORKFLOW QUICK REFERENCE
================================================================================

STEP 1: REGISTRATION
    POST /api/v1/auth/register
    Creates: user, session, tokens

STEP 2: LOGIN
    POST /api/v1/auth/login
    Returns: access_token, refresh_token

STEP 3: GRANT CONSENT (Required!)
    POST /api/v1/consent
    Updates: users.consent_status = true

STEP 4: UPLOAD DATA
    POST /api/v1/data/upload
    Creates: data_uploads, accounts, transactions, liabilities

STEP 5: FEATURE ENGINEERING (Automatic)
    Service Layer processes data
    Detects: subscriptions, savings, credit, income signals
    Caches: Redis (24h TTL)

STEP 6: PERSONA ASSIGNMENT (Automatic)
    Service Layer assigns persona (1-5)
    Creates: user_profiles, persona_history

STEP 7: RECOMMENDATION GENERATION
    Service Layer generates recommendations
    Creates: recommendations (status='pending')

STEP 8: OPERATOR REVIEW
    PUT /api/v1/operator/review/{id}
    Updates: recommendations.status = 'approved'

STEP 9: USER VIEWS RECOMMENDATIONS
    GET /api/v1/users/me/recommendations
    Returns: Approved recommendations with content

================================================================================
DATABASE TABLES INVOLVED:
================================================================================
1. users              - User accounts
2. sessions           - Active sessions
3. data_uploads       - Upload tracking
4. accounts           - Financial accounts
5. transactions       - Transaction records
6. liabilities        - Credit card/loan data
7. user_profiles      - Persona assignments & signals
8. persona_history    - Persona change history
9. recommendations    - Generated recommendations

================================================================================
KEY POINTS:
================================================================================
✓ Consent is REQUIRED before data processing
✓ Feature engineering happens AUTOMATICALLY after upload
✓ Persona assignment happens AUTOMATICALLY after signals detected
✓ Recommendations require OPERATOR APPROVAL before user sees them
✓ Signals are CACHED in Redis for 24 hours
✓ Every recommendation includes a DECISION TRACE for explainability

================================================================================
""")



