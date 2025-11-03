# SpendSense Platform

**Version**: 1.0  
**Date**: 2024-01-15  
**Status**: Development (Phase 1 - Task 1.1 Complete ✅)

---

## Project Overview

**SpendSense** is a financial education platform that transforms bank transaction data into personalized, actionable financial insights while maintaining strict regulatory compliance. The platform analyzes Plaid-style transaction data to detect behavioral patterns, assigns users to personas, and delivers explainable financial education recommendations—all without providing regulated financial advice.

### Key Features

- **Data Analysis Engine**: Detects behavioral signals (subscriptions, savings, credit, income patterns)
- **Persona Assignment**: Assigns users to behavioral personas based on their financial patterns
- **Recommendation System**: Generates personalized financial education content with explainable rationales
- **Regulatory Guardrails**: Ensures compliance through consent management, eligibility checks, and tone validation
- **Operator Dashboard**: Human-in-the-loop review and approval system

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

### Frontend
- **Framework**: React 18.2.0
- **Language**: TypeScript 5.3.3
- **Build Tool**: Vite 5.0.11
- **State Management**: Zustand or Redux
- **HTTP Client**: Axios 1.6.5

### Service Layer
- **Language**: Python 3.11.7
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.3
- **AI Integration**: OpenAI SDK 1.12.0
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

### Development Setup

1. **Clone the repository** (you'll handle this)

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Service Layer Setup**
   ```bash
   cd service
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Environment Variables

Create `.env` files in each directory (backend, frontend, service) based on `.env.example` templates.

---

## Project Phases

### Phase 1: Foundation & Backend Core (Weeks 1-3) ✅ Current
- ✅ Project setup and infrastructure (Task 1.1 Complete)
- ✅ Database schema design (Task 1.2 Complete)
- ✅ AWS Infrastructure Setup (Task 1.3 Complete) - Includes `owner_id` support for shared AWS accounts
- Authentication system
- Core API development

### Phase 2: Service Layer - Data Processing (Weeks 4-6)
- Data ingestion and validation
- Behavioral signal detection
- Persona assignment

### Phase 3: Service Layer - Recommendations & Guardrails (Weeks 7-9)
- Recommendation generation
- OpenAI integration
- Guardrails implementation

### Phase 4: Frontend Development (Weeks 10-12)
- React frontend development
- Operator dashboard
- API integration

### Phase 5-8: Integration, Testing, Deployment, Mobile (Weeks 13-18+)
- End-to-end testing
- AWS deployment
- CI/CD pipeline
- Mobile app (future)

---

## Documentation

- **[Main PRD](./docs/PRD.md)** - Complete project overview
- **[Project Plan](./docs/PROJECT-PLAN.md)** - Detailed task list and timeline
- **[Architecture Document](./docs/architecture.md)** - System architecture and technology stack
- **[Backend PRD](./docs/backend/PRD-Backend.md)** - Backend layer requirements
- **[Frontend PRD](./docs/frontend/PRD-Frontend.md)** - Frontend layer requirements
- **[Service PRD](./docs/service/PRD-Service.md)** - Service layer requirements

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

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request to `develop`

---

## License

[To be determined]

---

## Contact

- **Product Owner**: TBD
- **Technical Lead**: TBD
- **Project Manager**: TBD

---

**For detailed task breakdown, see [PROJECT-PLAN.md](./docs/PROJECT-PLAN.md)**


