# Product Requirements Document (PRD)
## SpendSense Platform - Service Layer: User Stories

**Version**: 1.0  
**Date**: 2024-01-15  
**Status**: Planning  
**Product Owner**: TBD  
**Technical Lead**: TBD  

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

**Document Status**: Draft  
**Next Review Date**: TBD  
**Approval Required From**: Product Owner, Service Layer Lead, Data Science Team


