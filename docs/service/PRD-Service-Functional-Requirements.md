# Product Requirements Document (PRD)
## SpendSense Platform - Service Layer: Functional Requirements

**Version**: 1.0  
**Date**: 2024-01-15  
**Status**: Planning  
**Product Owner**: TBD  
**Technical Lead**: TBD  

---

## Functional Requirements - Service Layer

### FR-SV-001: Data Ingestion
**Priority**: Must Have

- Accept JSON and CSV file formats
- Validate Plaid data schema:
  - Accounts: account_id, type, subtype, balances, iso_currency_code
  - Transactions: account_id, date, amount, merchant_name, payment_channel, personal_finance_category, pending
  - Liabilities: APRs, minimum_payment_amount, last_payment_amount, is_overdue, next_payment_due_date
- Handle account types: checking, savings, credit cards, money market, HSA
- Exclude business accounts (holder_category = "individual" only)
- Store data in PostgreSQL (relational) and S3 (Parquet for analytics)
- Generate ingestion reports

### FR-SV-002: Behavioral Signal Detection
**Priority**: Must Have

**Subscriptions**:
- Detect recurring merchants (≥3 occurrences in 90 days with monthly/weekly cadence)
- Calculate monthly recurring spend
- Calculate subscription share of total spend
- Generate signals for 30-day and 180-day windows

**Savings**:
- Calculate net inflow to savings-like accounts (savings, money market, HSA)
- Compute savings growth rate
- Calculate emergency fund coverage = savings balance / average monthly expenses
- Generate signals for 30-day and 180-day windows

**Credit**:
- Calculate utilization = balance / limit for each card
- Flag utilization thresholds: ≥30%, ≥50%, ≥80%
- Detect minimum-payment-only behavior (last 3 payments ≈ minimum payment)
- Identify interest charges
- Flag overdue accounts
- Generate signals for 30-day and 180-day windows

**Income Stability**:
- Detect payroll ACH deposits
- Calculate payment frequency and variability
- Calculate cash-flow buffer in months
- Identify variable income patterns
- Generate signals for 30-day and 180-day windows

**Caching**: Cache computed features in Redis (TTL: 24 hours)

### FR-SV-003: Persona Assignment
**Priority**: Must Have

- Assign users to one of 5 personas based on detected behaviors
- Implement priority logic when multiple personas match (Persona 1 > Persona 2 > ... > Persona 5)
- Store persona assignments with timestamps
- Support persona history tracking
- Allow custom persona definition with clear criteria
- Generate persona rationale
- Update personas when signals change

### FR-SV-004: Recommendation Generation
**Priority**: Must Have

- Generate 3-5 education items per user
- Generate 1-3 partner offers per user
- Every recommendation must include a "because" rationale
- Rationales must cite concrete data points (account numbers, amounts, dates)
- Recommendations must match assigned persona
- Generation time must be <5 seconds per user
- Cache recommendations in Redis (TTL: 1 hour)

**Education Content Types**:
- Articles on debt paydown strategies
- Budget templates for variable income
- Subscription audit checklists
- Emergency fund calculators
- Credit utilization explainers

**Partner Offer Types**:
- Balance transfer credit cards (if credit utilization high)
- High-yield savings accounts (if building emergency fund)
- Budgeting apps (if variable income)
- Subscription management tools (if subscription-heavy)

### FR-SV-005: Content Generation (OpenAI)
**Priority**: Should Have

- Generate educational content using OpenAI GPT-4-turbo-preview or GPT-3.5-turbo
- Use persona and detected signals as context for prompts
- Generate content matching persona focus areas
- Include regulatory disclaimers in generated content
- Cache generated content in Redis (TTL: 7 days)
- Fallback to pre-generated content templates if OpenAI fails
- Rate limiting on OpenAI API calls (100 requests/minute)

### FR-SV-006: Consent Guardrails
**Priority**: Must Have

- Check consent status before data processing
- Block recommendations if consent not granted
- Log consent checks
- Support data deletion on consent revocation
- Track consent version for policy updates

### FR-SV-007: Eligibility Guardrails
**Priority**: Must Have

- Don't recommend products user isn't eligible for
- Check minimum income requirements
- Check minimum credit score requirements
- Filter based on existing accounts (don't offer savings account if they have one)
- Avoid harmful suggestions (no payday loans, predatory products)
- Log all eligibility checks
- Generate eligibility explanations

### FR-SV-008: Tone Validation
**Priority**: Must Have

- Validate recommendation text for shaming language
- Enforce empowering, educational tone
- Avoid judgmental phrases like "you're overspending"
- Use neutral, supportive language
- Use OpenAI API for tone validation (optional)
- Block recommendations with inappropriate tone
- Log tone validation failures

### FR-SV-009: Regulatory Disclaimers
**Priority**: Must Have

- Add disclaimer to every recommendation: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
- Ensure disclaimers are prominently displayed
- Validate disclaimers are present before recommendation approval
- Log disclaimer validation

### FR-SV-010: Evaluation & Metrics
**Priority**: Must Have

- Measure coverage: % of users with assigned persona and ≥3 detected behaviors
- Measure explainability: % of recommendations with plain-language rationales
- Measure relevance: manual review or simple scoring of education-persona fit
- Measure latency: time to generate recommendations (target: <5 seconds)
- Measure fairness: basic demographic parity check if synthetic data includes demographics
- Generate JSON/CSV metrics file
- Generate brief summary report (1-2 pages)
- Generate per-user decision traces

### FR-SV-011: Decision Trace Generation
**Priority**: Must Have

- Store complete decision trace for each recommendation
- Include detected behavioral signals
- Include persona assignment logic
- Include guardrails checks performed
- Include recommendation generation logic
- Store decision traces in database (JSON)
- Generate human-readable decision traces
- Export decision traces (JSON/PDF)

---

**Document Status**: Draft  
**Next Review Date**: TBD  
**Approval Required From**: Product Owner, Service Layer Lead, Data Science Team


