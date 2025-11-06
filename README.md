# SpendSense Platform

**Version**: 2.0
**Date**: November 6, 2025
**Status**: Production Ready with AI-Enhanced Features ✅

---

## Project Overview

**SpendSense** is an AI-powered financial education platform that transforms bank transaction data into personalized, actionable financial insights while maintaining strict regulatory compliance. The platform uses advanced RAG (Retrieval-Augmented Generation) technology to analyze Plaid-style transaction data, detect behavioral patterns, assign users to personas, and deliver highly personalized, explainable financial education recommendations—all without providing regulated financial advice.

### Key Features

#### 🤖 **AI & Intelligence**
- **RAG-Powered Recommendations**: Advanced retrieval-augmented generation for personalized content
- **AI Subscription Validator**: Smart detection and validation of recurring expenses
- **AI Income Interpreter**: Intelligent interpretation of complex income patterns
- **Explainable AI**: Every recommendation shows the "why" behind it with data citations

#### 📊 **Financial Analysis**
- **Behavioral Signal Detection**: Subscriptions, savings patterns, credit utilization, income stability
- **Spending Category Analysis**: Automatic categorization with visual breakdowns (pie charts)
- **Income Analysis**: 180-day income tracking with payment frequency detection
- **Credit Monitoring**: Real-time credit utilization tracking with threshold alerts

#### 👥 **User Experience**
- **Persona-Based Personalization**: 6 behavioral personas (Tech-Savvy Millennial, Budget-Conscious Parent, etc.)
- **Interactive Dashboard**: Collapsible sections, pagination, color-coded transactions
- **Transaction Insights**: Visual indicators (green for deposits, red for expenses) with category dots
- **Smart Summaries**: Clean, scannable recommendation cards with quick actions

#### 🛡️ **Compliance & Safety**
- **Regulatory Guardrails**: Consent management, eligibility checks, tone validation
- **Operator Dashboard**: Human-in-the-loop review and approval system
- **Audit Trails**: Complete decision traces for transparency
- **Disclaimer Management**: Automatic financial advice disclaimers

---

## Project Structure

```
SpendSense/
├── backend/          # FastAPI backend service
├── frontend/          # React frontend application
├── service/           # Data processing and recommendation service layer
├── infrastructure/    # Terraform/IaC configurations
├── scripts/           # Utility scripts
├── docs/             # Project documentation
└── research/         # Research materials and example data
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.11.7
- **Database**: PostgreSQL 16.10 (RDS) - adjusted for us-west-1 availability
- **Cache**: Redis 7.1 (ElastiCache) - adjusted for us-west-1 availability
- **ORM**: SQLAlchemy 2.0.23
- **Migrations**: Alembic 1.13.0
- **Authentication**: JWT tokens, OAuth 2.0 (Google, GitHub, Facebook, Apple)

### Frontend
- **Framework**: React 18.2.0 with TypeScript 5.3.3
- **Build Tool**: Vite 5.0.11
- **UI Library**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios 1.6.5
- **Icons**: React Icons
- **Charts**: Recharts
- **Routing**: React Router v6

### Service Layer (AI & Analytics)
- **Language**: Python 3.11.7
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.3
- **AI Integration**: OpenAI SDK 1.12.0 (GPT-4-turbo, GPT-3.5-turbo)
- **RAG System**: 
  - ChromaDB (vector database)
  - Sentence-Transformers (embeddings)
  - Langchain (orchestration)
  - Tiktoken (tokenization)
- **Storage**: S3 (Parquet files)

### Infrastructure
- **Cloud Provider**: AWS
- **Compute**: ECS Fargate
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis
- **Storage**: S3
- **IaC**: Terraform 1.6.6

---

## Getting Started

### Prerequisites

- Python 3.11.7+
- Node.js 20.10.0+ (LTS)
- PostgreSQL 16.10+ (for local development)
- Redis 7.1+ (for local development)
- Docker 24.0.7+ (optional)
- AWS CLI 2.15.25+ (for deployment)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SpendSense
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set up environment variables
   cp env.example .env
   # Edit .env with your configuration
   
   # Run migrations
   alembic upgrade head
   
   # Start the backend server
   uvicorn app.main:app --reload --port 8000
   ```

3. **Service Layer Setup (for RAG & AI features)**
   ```bash
   cd service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Build the RAG knowledge base
   python scripts/build_knowledge_base.py
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Start the development server
   npm run dev
   ```

5. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Environment Variables

Create `.env` files based on `env.example` templates:

**Backend (.env)**:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/spendsense

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for AI features)
OPENAI_API_KEY=your-openai-api-key

# RAG Configuration
RAG_ENABLED=true
RAG_ROLLOUT_PERCENTAGE=100
RAG_OPENAI_MODEL=gpt-4-turbo-preview
RAG_VECTOR_DB_PATH=./rag_vector_store
```

**Frontend (.env)**:
```env
VITE_API_URL=http://localhost:8000
```

---

## Recent Enhancements (v2.0)

### 🎯 **November 2025 Updates**

#### AI & Machine Learning
- ✅ **RAG Implementation**: Full RAG system with ChromaDB and GPT-4
- ✅ **AI Recommendation Explainer**: "Why this recommendation?" feature with data citations
- ✅ **AI Subscription Validator**: Smart validation with anomaly detection
- ✅ **AI Income Interpreter**: Complex income pattern analysis

#### User Interface
- ✅ **Markdown Formatting**: Clean, professional rendering of recommendations
- ✅ **Spending Category Analyzer**: Pie charts and visual breakdowns
- ✅ **Transaction Indicators**: Green/red color coding for deposits/expenses
- ✅ **Category Dots**: Visual category identification in transactions
- ✅ **Collapsible Sections**: Organized, scannable dashboard layout
- ✅ **Pagination**: Efficient transaction browsing

#### Financial Intelligence
- ✅ **Enhanced Behavioral Signals**: Improved subscription, credit, savings, income detection
- ✅ **13 New Category Recommendations**: Food, transport, shopping, healthcare, housing
- ✅ **180-Day Income Analysis**: Extended income tracking window
- ✅ **Smart Credit Monitoring**: Multi-threshold utilization tracking

#### Developer Experience
- ✅ **RAG Deployment Scripts**: One-command setup
- ✅ **A/B Testing Framework**: Compare RAG vs catalog performance
- ✅ **Metrics Collection**: Real-time system health monitoring
- ✅ **Comprehensive Documentation**: RAG guides, testing procedures

---

## Documentation

### Core Documentation
- **[Main PRD](./docs/PRD.md)** - Complete project overview
- **[Project Plan](./docs/PROJECT-PLAN.md)** - Detailed task list and timeline
- **[Architecture Document](./docs/architecture.md)** - System architecture and technology stack

### Layer-Specific Documentation
- **[Backend PRD](./docs/backend/PRD-Backend.md)** - Backend layer requirements
- **[Frontend PRD](./docs/frontend/PRD-Frontend.md)** - Frontend layer requirements
- **[Service PRD](./docs/service/PRD-Service.md)** - Service layer requirements

### Feature Documentation
- **[RAG Implementation Plan](./docs/RAG_IMPLEMENTATION_PLAN.md)** - RAG system architecture and roadmap
- **[RAG Deployment Guide](./docs/RAG_DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[AI Enhancement Plan](./docs/AI_ENHANCEMENT_PLAN.md)** - AI strategy and benefits
- **[User Workflow](./docs/USER_WORKFLOW_QUICKREF.md)** - End-user experience flows

### Data & Testing
- **[Testing Data Guide](./docs/TESTING_DATA_GUIDE.md)** - Test data generation
- **[User Types Reference](./docs/USER_TYPES.md)** - Persona definitions
- **[Database Setup](./backend/DATABASE_SETUP.md)** - Database configuration
- **[Database Seeding](./backend/DATABASE_SEEDING.md)** - Sample data setup

---

## Development Workflow

### Branch Strategy

See [BRANCH_STRATEGY.md](./BRANCH_STRATEGY.md) for detailed branch strategy.

**Main Branches:**
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `hotfix/*` - Critical production fixes
- `release/*` - Release preparation branches

### Code Quality

- **Python**: Black (formatter), Pylint (linter), MyPy (type checking)
- **TypeScript**: ESLint, Prettier
- **Testing**: pytest (backend), Jest (frontend)
- **Coverage Target**: ≥80%

---

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Service Layer Tests
```bash
cd service
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### RAG System Tests
```bash
cd service
python scripts/test_rag_basic.py
python scripts/test_rag_quality.py
```

---

## Contributing

1. Create a feature branch from `develop`
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Run linters:
   ```bash
   # Backend
   black backend/ && pylint backend/
   
   # Frontend
   npm run lint
   ```
6. Submit a pull request to `develop`

---

## Key Technologies & Libraries

### Backend Stack
- FastAPI, SQLAlchemy, Alembic, Pydantic
- PostgreSQL, Redis
- JWT, OAuth 2.0
- Pytest

### Frontend Stack
- React, TypeScript, Vite
- Tailwind CSS, React Icons
- TanStack Query, React Router
- Recharts (for data visualization)
- Axios

### AI/ML Stack
- OpenAI (GPT-4-turbo, GPT-3.5-turbo)
- ChromaDB (vector database)
- Sentence-Transformers (all-MiniLM-L6-v2)
- Langchain
- Pandas, NumPy

---

## License

[To be determined]

---

## Contact

- **Product Owner**: TBD
- **Technical Lead**: TBD
- **Project Manager**: TBD

---

## Changelog

### v2.0 (November 2025)
- ✨ RAG-powered personalized recommendations
- ✨ AI recommendation explainer with data citations
- ✨ Spending category analysis with pie charts
- ✨ 180-day income analysis tracking
- ✨ Enhanced behavioral signal detection
- ✨ Transaction color indicators (green/red)
- ✨ Category dots for visual categorization
- ✨ 13 new category-based recommendations
- ✨ Improved dashboard UI/UX
- ✨ Markdown formatting for clean content display
- 🐛 Fixed subscription detection (filtered utilities)
- 🐛 Fixed credit utilization display
- 🐛 Fixed transport/transportation category consistency
- ⚡ Reduced vertical spacing across pages
- ⚡ Improved link cursor indicators

### v1.0 (January 2024)
- 🎉 Initial release
- ✅ Core authentication system
- ✅ Basic recommendation engine
- ✅ Operator dashboard
- ✅ Behavioral signal detection

---

**For detailed task breakdown, see [PROJECT-PLAN.md](./docs/PROJECT-PLAN.md)**


