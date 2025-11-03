# SpendSense Service Layer

Data processing, feature engineering, persona assignment, and recommendation generation service.

## Technology Stack

- **Language**: Python 3.11.7
- **Framework**: FastAPI 0.109.0 (for service endpoints)
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.3
- **Storage**: PyArrow 15.0.0 (Parquet support)
- **AI Integration**: OpenAI SDK 1.12.0
- **Database**: PostgreSQL 16.10 (AWS RDS) / 15.6+ (local development) - via SQLAlchemy
- **Cache**: Redis 7.1 (AWS ElastiCache) / 7.2.4+ (local development)

## Project Structure

```
service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Service entry point
│   ├── config.py            # Configuration
│   ├── ingestion/           # Data ingestion services
│   │   ├── parser.py        # Plaid data parser
│   │   └── validator.py     # Data validation
│   ├── features/            # Feature engineering
│   │   ├── subscriptions.py # Subscription detection
│   │   ├── savings.py       # Savings pattern detection
│   │   ├── credit.py        # Credit utilization detection
│   │   └── income.py       # Income stability detection
│   ├── personas/            # Persona assignment
│   │   ├── assigner.py     # Persona assignment logic
│   │   └── priority.py     # Priority logic
│   ├── recommendations/     # Recommendation generation
│   │   ├── generator.py    # Recommendation engine
│   │   ├── rationale.py    # Rationale generation
│   │   └── openai.py       # OpenAI integration
│   ├── guardrails/          # Guardrails enforcement
│   │   ├── consent.py      # Consent guardrails
│   │   ├── eligibility.py  # Eligibility validation
│   │   └── tone.py         # Tone validation
│   └── evaluation/          # Evaluation and metrics
│       ├── metrics.py      # Evaluation metrics
│       └── traces.py       # Decision trace generation
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (OpenAI API key, database URL, etc.)
   ```

## Development Tasks

See [PROJECT-PLAN.md](../docs/PROJECT-PLAN.md) for detailed task breakdown.

- **Task 4.1**: Data Ingestion Service
- **Task 5.1**: Subscription Detection
- **Task 6.1**: Persona Assignment Logic
- **Task 7.1**: Recommendation Engine Foundation
- And more...


