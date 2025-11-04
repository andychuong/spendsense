# Product Requirements Document (PRD)
## SpendSense Platform - Service Layer

**Version**: 1.0
**Date**: 2025-11-04
**Status**: Development (Phase 1 - Task 1.1 Complete)
**Product Owner**: TBD
**Technical Lead**: TBD

---

## Executive Summary

The **Service Layer** of SpendSense is responsible for data processing, feature engineering, persona assignment, recommendation generation, guardrails enforcement, and evaluation. The service layer processes transaction data, detects behavioral patterns, assigns personas, generates personalized recommendations, and ensures regulatory compliance.

### Key Responsibilities
1. **Data Ingestion**: Process Plaid-style transaction data
2. **Feature Engineering**: Detect behavioral signals (subscriptions, savings, credit, income)
3. **Persona Assignment**: Assign users to behavioral personas
4. **Recommendation Generation**: Create personalized financial education recommendations
5. **Guardrails**: Enforce consent, eligibility, and tone validation
6. **Evaluation**: Measure system performance and fairness

---

## Service Layer Architecture

### Technology Stack

**Language & Framework**:
- **Python**: `3.11.7` (programming language)
- **FastAPI**: `0.109.0` (API framework for service endpoints)

**Data Processing**:
- **Pandas**: `2.1.4` (data analysis)
- **NumPy**: `1.26.3` (numerical computing)
- **PyArrow**: `15.0.0` (Parquet file support)

**AI/LLM Integration**:
- **OpenAI SDK**: `1.12.0` (content generation)
- **OpenAI API**: v1 (GPT-4-turbo-preview or GPT-3.5-turbo)

**Database**:
- **PostgreSQL**: `16.10` (RDS) - relational data (adjusted for us-west-1 availability)
- **S3**: Parquet files for analytics

**Caching**:
- **Redis**: `7.1` (ElastiCache) - computed features cache (adjusted for us-west-1 availability)

**AWS Services**:
- **S3**: File storage (Parquet analytics files)
- **SQS**: Async processing queues (optional)
- **Lambda**: Batch processing (optional)

---

## User Stories - Service Layer

### Data Ingestion

**SV-US-001: Data Ingestion Service**
- **As a** system
- **I want to** ingest Plaid-style transaction data
- **So that** I can process user financial behavior

**Acceptance Criteria**:
- [ ] Accept JSON and CSV file formats
- [ ] Validate Plaid data schema
- [ ] Handle 50-100 users worth of data
- [ ] Parse accounts (account_id, type, subtype, balances)
- [ ] Parse transactions (account_id, date, amount, merchant, category)
- [ ] Parse liabilities (APRs, payment amounts, overdue status)
- [ ] Store raw data in S3 (Parquet)
- [ ] Store metadata in PostgreSQL
- [ ] Generate ingestion report (errors, warnings)

**SV-US-002: Data Validation Service**
- **As a** system
- **I want to** validate uploaded transaction data
- **So that** only valid data is processed

**Acceptance Criteria**:
- [ ] Validate account structure (required fields, types)
- [ ] Validate transaction structure (required fields, date formats, amounts)
- [ ] Validate liability structure (APRs, payment amounts, dates)
- [ ] Check for duplicate accounts/transactions
- [ ] Validate data ranges (dates, amounts)
- [ ] Return validation errors with clear messages
- [ ] Log validation errors
- [ ] Store validation results

### Feature Engineering

**SV-US-003: Subscription Detection Service**
- **As a** system
- **I want to** detect recurring subscription patterns
- **So that** users can see their subscription spending

**Acceptance Criteria**:
- [ ] Identify merchants with ≥3 transactions in 90 days
- [ ] Calculate monthly/weekly cadence
- [ ] Compute monthly recurring spend
- [ ] Calculate subscription share of total spend
- [ ] Generate signals for 30-day and 180-day windows
- [ ] Store subscription signals in database
- [ ] Cache computed features in Redis

**SV-US-004: Savings Pattern Detection Service**
- **As a** system
- **I want to** detect savings behaviors
- **So that** users can see their savings progress

**Acceptance Criteria**:
- [ ] Calculate net inflow to savings accounts (savings, money market, HSA)
- [ ] Compute savings growth rate
- [ ] Calculate emergency fund coverage (savings balance / average monthly expenses)
- [ ] Track savings patterns over time windows
- [ ] Generate signals for 30-day and 180-day windows
- [ ] Store savings signals in database
- [ ] Cache computed features in Redis

**SV-US-005: Credit Utilization Detection Service**
- **As a** system
- **I want to** detect credit card utilization patterns
- **So that** users can improve their credit health

**Acceptance Criteria**:
- [ ] Calculate utilization = balance / limit for each card
- [ ] Flag cards at ≥30%, ≥50%, ≥80% utilization
- [ ] Detect minimum-payment-only behavior (last 3 payments ≈ minimum payment)
- [ ] Identify interest charges
- [ ] Flag overdue accounts
- [ ] Generate signals for 30-day and 180-day windows
- [ ] Store credit signals in database
- [ ] Cache computed features in Redis

**SV-US-006: Income Stability Detection Service**
- **As a** system
- **I want to** detect income patterns
- **So that** users can understand their cash flow

**Acceptance Criteria**:
- [ ] Detect payroll ACH deposits
- [ ] Calculate payment frequency and variability
- [ ] Calculate cash-flow buffer in months
- [ ] Identify variable income patterns
- [ ] Generate signals for 30-day and 180-day windows
- [ ] Store income signals in database
- [ ] Cache computed features in Redis

### Persona Assignment

**SV-US-007: Persona Assignment Service**
- **As a** system
- **I want to** assign users to behavioral personas
- **So that** recommendations can be personalized

**Acceptance Criteria**:
- [ ] Assign users to one of 5 personas based on detected behaviors
- [ ] Implement priority logic when multiple personas match
- [ ] Store persona assignments with timestamps
- [ ] Support persona history tracking
- [ ] Allow custom persona definition with clear criteria
- [ ] Generate persona rationale
- [ ] Store persona assignment in database

**Persona Definitions**:

**Persona 1: High Utilization**
- Criteria: Any card utilization ≥50% OR interest charges > 0 OR minimum-payment-only OR is_overdue = true
- Priority: 1 (highest)
- Focus: Reduce utilization, payment planning, autopay education

**Persona 2: Variable Income Budgeter**
- Criteria: Median pay gap > 45 days AND cash-flow buffer < 1 month
- Priority: 2
- Focus: Percent-based budgets, emergency fund basics, smoothing strategies

**Persona 3: Subscription-Heavy**
- Criteria: Recurring merchants ≥3 AND (monthly recurring spend ≥$50 in 30d OR subscription spend share ≥10%)
- Priority: 3
- Focus: Subscription audit, cancellation/negotiation tips, bill alerts

**Persona 4: Savings Builder**
- Criteria: Savings growth rate ≥2% over window OR net savings inflow ≥$200/month, AND all card utilizations < 30%
- Priority: 4
- Focus: Goal setting, automation, APY optimization (HYSA/CD basics)

**Persona 5: Custom Persona**
- Criteria: User-defined based on specific behavioral signals
- Priority: 5 (lowest)
- Focus: Customized educational content

### Recommendation Generation

**SV-US-008: Recommendation Generation Service**
- **As a** system
- **I want to** generate personalized financial education recommendations
- **So that** users can improve their financial health

**Acceptance Criteria**:
- [ ] Generate 3-5 education items per user
- [ ] Generate 1-3 partner offers per user
- [ ] Every recommendation includes a "because" rationale
- [ ] Rationales cite specific data points (account numbers, amounts, dates)
- [ ] Recommendations match assigned persona
- [ ] Generation time <5 seconds per user
- [ ] Store recommendations in database
- [ ] Cache recommendations in Redis

**SV-US-009: Rationale Generation Service**
- **As a** system
- **I want to** generate explainable rationales for recommendations
- **So that** users can trust and act on recommendations

**Acceptance Criteria**:
- [ ] Generate plain-language rationales
- [ ] Cite specific accounts, amounts, dates
- [ ] Avoid financial jargon
- [ ] Use OpenAI API for content generation (optional)
- [ ] Example format: "We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could improve your credit score and reduce interest charges of $87/month."
- [ ] Store rationales with recommendations

**SV-US-010: Content Generation Service**
- **As a** system
- **I want to** generate educational content using OpenAI
- **So that** recommendations are personalized and relevant

**Acceptance Criteria**:
- [ ] Generate education items using OpenAI GPT-4 or GPT-3.5
- [ ] Use persona and detected signals as context
- [ ] Generate content matching persona focus areas
- [ ] Include regulatory disclaimers
- [ ] Cache generated content in Redis
- [ ] Fallback to pre-generated content templates if OpenAI fails

**Education Content Types**:
- Articles on debt paydown strategies
- Budget templates for variable income
- Subscription audit checklists
- Emergency fund calculators
- Credit utilization explainers

**SV-US-011: Partner Offer Service**
- **As a** system
- **I want to** generate eligible partner offers
- **So that** users can take advantage of relevant financial products

**Acceptance Criteria**:
- [ ] Show 1-3 partner offers per user
- [ ] Only show offers user is eligible for (income, credit score requirements)
- [ ] Filter out offers for products user already has
- [ ] Include eligibility explanation
- [ ] No predatory products (payday loans, etc.)
- [ ] Store partner offers with recommendations

**Partner Offer Types**:
- Balance transfer credit cards (if credit utilization high)
- High-yield savings accounts (if building emergency fund)
- Budgeting apps (if variable income)
- Subscription management tools (if subscription-heavy)

### Guardrails

**SV-US-012: Consent Guardrails Service**
- **As a** system
- **I want to** enforce consent before processing data
- **So that** users maintain control over their data

**Acceptance Criteria**:
- [ ] Check consent status before data processing
- [ ] Block recommendations if consent not granted
- [ ] Log consent checks
- [ ] Support data deletion on consent revocation
- [ ] Track consent version

**SV-US-013: Eligibility Validation Service**
- **As a** system
- **I want to** validate user eligibility for partner offers
- **So that** users only see relevant offers

**Acceptance Criteria**:
- [ ] Check minimum income requirements
- [ ] Check minimum credit score requirements
- [ ] Filter offers for products user already has
- [ ] Block harmful products (payday loans, predatory loans)
- [ ] Log eligibility checks
- [ ] Generate eligibility explanations

**SV-US-014: Tone Validation Service**
- **As a** system
- **I want to** ensure all recommendations use appropriate tone
- **So that** users feel empowered, not shamed

**Acceptance Criteria**:
- [ ] Validate recommendation text for shaming language
- [ ] Enforce empowering, educational tone
- [ ] Avoid judgmental phrases like "you're overspending"
- [ ] Use neutral, supportive language
- [ ] Use OpenAI API for tone validation (optional)
- [ ] Block recommendations with inappropriate tone
- [ ] Log tone validation failures

**SV-US-015: Regulatory Disclaimers Service**
- **As a** system
- **I want to** add regulatory disclaimers to all recommendations
- **So that** users understand this is education, not advice

**Acceptance Criteria**:
- [ ] Add disclaimer to every recommendation: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
- [ ] Ensure disclaimers are prominently displayed
- [ ] Validate disclaimers are present before recommendation approval
- [ ] Log disclaimer validation

### Evaluation

**SV-US-016: Evaluation Service**
- **As a** system
- **I want to** measure system performance and fairness
- **So that** I can improve recommendations

**Acceptance Criteria**:
- [ ] Measure coverage: % of users with assigned persona and ≥3 detected behaviors
- [ ] Measure explainability: % of recommendations with plain-language rationales
- [ ] Measure relevance: manual review or simple scoring of education-persona fit
- [ ] Measure latency: time to generate recommendations (target: <5 seconds)
- [ ] Measure fairness: basic demographic parity check if synthetic data includes demographics
- [ ] Generate JSON/CSV metrics file
- [ ] Generate brief summary report (1-2 pages)
- [ ] Generate per-user decision traces

**SV-US-017: Decision Trace Service**
- **As a** system
- **I want to** generate decision traces for all recommendations
- **So that** operators can audit decision-making

**Acceptance Criteria**:
- [ ] Store complete decision trace for each recommendation
- [ ] Include detected behavioral signals
- [ ] Include persona assignment logic
- [ ] Include guardrails checks performed
- [ ] Include recommendation generation logic
- [ ] Store decision traces in database (JSON)
- [ ] Generate human-readable decision traces
- [ ] Export decision traces (JSON/PDF)

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

## Non-Functional Requirements - Service Layer

### NFR-SV-001: Performance
- **Recommendation Generation**: <5 seconds per user (p95)
- **Feature Extraction**: <2 seconds per user (p95)
- **Data Ingestion**: <10 seconds per 100 users (p95)
- **Caching Hit Rate**: ≥80% for computed features

### NFR-SV-002: Reliability
- **Data Processing Accuracy**: 100% (no data corruption)
- **Error Rate**: <0.1% of processed records
- **Retry Logic**: Exponential backoff for external API calls
- **Data Loss**: Zero data loss tolerance

### NFR-SV-003: Scalability
- **Horizontal Scaling**: Support processing 1000+ users concurrently
- **Batch Processing**: Process 50-100 users per batch
- **Async Processing**: Use SQS for heavy computations (optional)
- **Caching**: Redis for frequently accessed data

### NFR-SV-004: Maintainability
- **Code Coverage**: ≥80% test coverage
- **Documentation**: Complete API documentation
- **Code Quality**: Linting, type checking, formatting
- **Modularity**: Clear separation of concerns (ingest/, features/, personas/, recommend/, guardrails/)

### NFR-SV-005: External API Integration
- **OpenAI API**: Rate limiting (100 requests/minute)
- **Retry Logic**: Exponential backoff for API failures
- **Fallback**: Pre-generated content templates if OpenAI fails
- **Caching**: Cache generated content (7-day TTL)
- **Cost Optimization**: Use GPT-3.5-turbo for cost-sensitive operations

---

## Technical Requirements - Service Layer

### TR-SV-001: Service Structure

**Project Structure**:
```
services/
  ingest/
    __init__.py
    parser.py        # Parse JSON/CSV files
    validator.py     # Validate Plaid schema
    storage.py       # Store data (PostgreSQL, S3)
  features/
    __init__.py
    subscriptions.py # Subscription detection
    savings.py       # Savings pattern detection
    credit.py        # Credit utilization detection
    income.py        # Income stability detection
    signals.py       # Signal aggregation
  personas/
    __init__.py
    assigner.py     # Persona assignment logic
    priority.py      # Priority logic
  recommend/
    __init__.py
    generator.py     # Recommendation generation
    content.py       # Content generation (OpenAI)
    rationales.py   # Rationale generation
    offers.py       # Partner offer generation
  guardrails/
    __init__.py
    consent.py      # Consent validation
    eligibility.py  # Eligibility checks
    tone.py         # Tone validation
    disclaimer.py   # Regulatory disclaimers
  eval/
    __init__.py
    metrics.py     # Metrics calculation
    traces.py      # Decision trace generation
    report.py      # Report generation
  utils/
    __init__.py
    cache.py       # Redis caching utilities
    openai.py      # OpenAI client
    logging.py     # Logging utilities
```

### TR-SV-002: Data Processing Pipeline

**Pipeline Flow**:
1. **Data Ingestion** → Parse and validate Plaid data
2. **Feature Extraction** → Detect behavioral signals
3. **Persona Assignment** → Assign users to personas
4. **Recommendation Generation** → Generate personalized recommendations
5. **Guardrails Enforcement** → Validate consent, eligibility, tone
6. **Decision Trace Generation** → Store decision traces
7. **Storage** → Store recommendations in database

**Processing Modes**:
- **Synchronous**: Process single user on-demand (<5 seconds)
- **Asynchronous**: Process batch of users in background (SQS)

### TR-SV-003: OpenAI Integration

**API Configuration**:
- **Provider**: OpenAI API v1
- **SDK**: OpenAI Python SDK 1.12.0
- **Model**: GPT-4-turbo-preview (default) or GPT-3.5-turbo (fallback)
- **Rate Limiting**: 100 requests/minute
- **Retry Logic**: Exponential backoff (max 3 retries)
- **Timeout**: 30 seconds per request

**Use Cases**:
1. **Content Generation**: Generate educational content based on persona and signals
2. **Rationale Generation**: Create explainable rationales for recommendations
3. **Tone Validation**: Validate recommendation tone (optional)

**Prompt Templates**:
- Persona-specific content generation prompts
- Rationale generation prompts (include data points)
- Tone validation prompts

**Caching Strategy**:
- Cache generated content in Redis (TTL: 7 days)
- Cache key: `openai:content:{persona}:{signal_hash}`
- Fallback to pre-generated templates if cache miss and API failure

### TR-SV-004: Feature Engineering

**Subscription Detection**:
- Identify recurring merchants (merchant_name, merchant_entity_id)
- Calculate transaction frequency (monthly/weekly cadence)
- Compute monthly recurring spend
- Calculate subscription share = (recurring spend / total spend) * 100

**Savings Pattern Detection**:
- Calculate net inflow = sum of deposits to savings accounts
- Compute growth rate = (current balance - previous balance) / previous balance * 100
- Calculate emergency fund coverage = savings balance / average monthly expenses

**Credit Utilization Detection**:
- Calculate utilization = (current balance / credit limit) * 100
- Flag thresholds: ≥30%, ≥50%, ≥80%
- Detect minimum-payment-only: last 3 payments ≈ minimum_payment_amount
- Identify interest charges: transactions with category "INTEREST_CHARGE"
- Flag overdue: is_overdue = true

**Income Stability Detection**:
- Detect payroll ACH: transactions with category "PAYROLL" and payment_channel "ACH"
- Calculate payment frequency: median time between payroll deposits
- Calculate payment variability: coefficient of variation of payment amounts
- Calculate cash-flow buffer: (current balance - minimum balance) / average monthly expenses

**Time Windows**:
- Compute signals for 30-day window (last 30 days)
- Compute signals for 180-day window (last 180 days)
- Store both sets of signals for comparison

### TR-SV-005: Persona Assignment Logic

**Priority Logic**:
1. Check Persona 1 (High Utilization) → Assign if criteria met
2. If not Persona 1, check Persona 2 (Variable Income Budgeter)
3. If not Persona 2, check Persona 3 (Subscription-Heavy)
4. If not Persona 3, check Persona 4 (Savings Builder)
5. If not Persona 4, assign Persona 5 (Custom Persona) or default

**Assignment Rules**:
- If multiple personas match, assign highest priority (lowest number)
- Store persona assignment with timestamp
- Update persona when signals change (detect persona transitions)
- Generate persona rationale explaining why persona was assigned

### TR-SV-006: Recommendation Generation

**Content Catalog**:
- Pre-defined education items per persona
- Pre-defined partner offers per persona
- OpenAI-generated content (dynamic)

**Generation Process**:
1. Get assigned persona
2. Get detected behavioral signals
3. Select education items matching persona (3-5 items)
4. Select partner offers matching persona and eligibility (1-3 offers)
5. Generate rationales for each recommendation
6. Apply guardrails (consent, eligibility, tone)
7. Add regulatory disclaimers
8. Store recommendations in database
9. Generate decision traces

**Rationale Generation**:
- Cite specific data points: account numbers (last 4 digits), amounts, dates
- Plain language, avoid financial jargon
- Example: "We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could improve your credit score and reduce interest charges of $87/month."
- Use OpenAI for dynamic rationale generation (optional)

### TR-SV-007: Guardrails Implementation

**Consent Guardrails**:
- Check consent status before data processing
- Block recommendations if consent not granted
- Log consent checks with user_id and timestamp
- Support data deletion on consent revocation

**Eligibility Guardrails**:
- Check minimum income requirements (from partner offer config)
- Check minimum credit score requirements (from partner offer config)
- Filter offers for products user already has (check existing accounts)
- Block harmful products (blocklist: payday loans, predatory loans)
- Log eligibility checks with results

**Tone Validation**:
- Validate recommendation text for shaming language (keywords: "overspending", "irresponsible", "wasteful")
- Enforce empowering tone (keywords: "opportunity", "improve", "potential")
- Use OpenAI for tone validation (optional): "Analyze this text for shaming language and provide a tone score (0-10, where 10 is empowering)."
- Block recommendations with tone score < 7

**Regulatory Disclaimers**:
- Add disclaimer to every recommendation: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
- Validate disclaimer presence before recommendation approval
- Log disclaimer validation

### TR-SV-008: Evaluation Metrics

**Coverage Metrics**:
- % of users with assigned persona
- % of users with ≥3 detected behaviors
- % of users with both persona and ≥3 behaviors

**Explainability Metrics**:
- % of recommendations with plain-language rationales
- % of rationales citing specific data points
- Rationale quality score (manual review or automated)

**Relevance Metrics**:
- Education-persona fit score (manual review or automated)
- Partner offer-persona fit score (manual review or automated)
- User feedback scores

**Performance Metrics**:
- Recommendation generation latency (p50, p95, p99)
- Feature extraction latency (p50, p95, p99)
- Data ingestion latency (p50, p95, p99)

**Fairness Metrics**:
- Demographic parity check (if demographics available in data)
- Recommendation distribution across demographics
- Signal detection accuracy across demographics

**Output Formats**:
- JSON metrics file
- CSV metrics file
- Summary report (Markdown/PDF)
- Per-user decision traces (JSON)

### TR-SV-009: Decision Trace Structure

**Decision Trace Schema**:
```json
{
  "recommendation_id": "uuid",
  "user_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "detected_signals": {
    "subscriptions": {...},
    "savings": {...},
    "credit": {...},
    "income": {...}
  },
  "persona_assignment": {
    "persona_id": 1,
    "persona_name": "High Utilization",
    "criteria_met": [...],
    "priority": 1,
    "rationale": "..."
  },
  "recommendations": [
    {
      "recommendation_id": "uuid",
      "type": "education",
      "content": "...",
      "rationale": "...",
      "guardrails": {
        "consent": true,
        "eligibility": true,
        "tone": 8,
        "disclaimer": true
      }
    }
  ],
  "generation_time_ms": 3500
}
```

**Human-Readable Format**:
- Markdown or HTML format
- Expandable sections for details
- Visual decision tree (optional)

---

## Success Metrics - Service Layer

### Performance Metrics
- **Recommendation Generation**: <5 seconds (p95)
- **Feature Extraction**: <2 seconds (p95)
- **Data Ingestion**: <10 seconds per 100 users (p95)
- **Caching Hit Rate**: ≥80%

### Quality Metrics
- **Coverage**: 100% of users with assigned persona and ≥3 behaviors
- **Explainability**: 100% of recommendations with rationales
- **Relevance**: ≥80% education-persona fit score
- **Fairness**: Demographic parity across all personas

### Reliability Metrics
- **Data Processing Accuracy**: 100% (no corruption)
- **Error Rate**: <0.1% of processed records
- **OpenAI API Success Rate**: ≥95%
- **Guardrails Enforcement**: 100% compliance

---

## Dependencies - Service Layer

### External Dependencies
- **OpenAI API**: For content generation and tone validation
- **AWS S3**: For Parquet analytics files
- **PostgreSQL**: For relational data storage
- **Redis**: For caching computed features
- **AWS SQS**: For async processing (optional)

### Internal Dependencies
- **Backend Layer**: API endpoints for triggering services
- **Frontend Layer**: UI for displaying recommendations
- **Content Catalog**: Pre-defined education items and partner offers

---

## Risks & Mitigation - Service Layer

### Risk-SV-001: OpenAI API Downtime
**Risk**: Cannot generate recommendations
**Impact**: Service unavailability
**Mitigation**:
- Fallback to pre-generated content templates
- Caching of generated content (7-day TTL)
- Retry logic with exponential backoff
- Monitoring and alerting
- Use GPT-3.5-turbo as fallback (cheaper, faster)

### Risk-SV-002: Performance Degradation
**Risk**: Recommendation generation exceeds 5-second target
**Impact**: Poor user experience
**Mitigation**:
- Caching of computed features (Redis)
- Async processing for heavy computations (SQS)
- Database query optimization
- Batch processing for multiple users
- Load balancing and auto-scaling

### Risk-SV-003: Data Processing Errors
**Risk**: Invalid data causes processing failures
**Impact**: Incorrect recommendations
**Mitigation**:
- Comprehensive data validation
- Error handling and logging
- Data quality checks
- Fallback to default values
- Regular data audits

### Risk-SV-004: Persona Assignment Errors
**Risk**: Users assigned to incorrect personas
**Impact**: Irrelevant recommendations
**Mitigation**:
- Clear persona criteria documentation
- Regular validation of persona assignments
- Operator review and override capability
- User feedback loop
- A/B testing of persona logic

### Risk-SV-005: Guardrails Bypass
**Risk**: Recommendations bypass guardrails
**Impact**: Regulatory compliance issues
**Mitigation**:
- Multiple guardrails checks at different stages
- Operator review and approval
- Audit logging of all guardrails checks
- Regular guardrails testing
- Automated alerts on guardrails failures

---

## Out of Scope (MVP)

### Not Included in Initial Release
- Advanced ML models for persona prediction (rules-based only)
- Real-time transaction sync (batch processing only)
- Advanced fraud detection
- Multi-language content generation (English only)
- Advanced analytics dashboard
- A/B testing framework
- User segmentation beyond personas

### Future Enhancements
- Machine learning models for persona prediction
- Real-time transaction processing (stream processing)
- Advanced fraud detection
- Multi-language content generation
- Advanced analytics and visualization
- A/B testing framework
- User segmentation and clustering

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial Service Layer PRD | TBD |

---

**Document Status**: Draft
**Next Review Date**: TBD
**Approval Required From**: Product Owner, Service Layer Lead, Data Science Team


