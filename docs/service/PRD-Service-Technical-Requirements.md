# Product Requirements Document (PRD)
## SpendSense Platform - Service Layer: Technical Requirements

**Version**: 1.0  
**Date**: 2025-11-04  
**Status**: Planning  
**Product Owner**: TBD  
**Technical Lead**: TBD  

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

**Document Status**: Draft  
**Next Review Date**: TBD  
**Approval Required From**: Product Owner, Service Layer Lead, Data Science Team


