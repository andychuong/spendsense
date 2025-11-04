# SpendSense Project Plan
## Order of Operations & Task List

**Version**: 1.1  
**Date**: 2025-11-03
**Status**: Development (Phase 1 - Task 2.4 Complete)  
**Project Manager**: TBD  

---

## Document Overview

This document provides a comprehensive order of operations and task list for the SpendSense project, with links to relevant PRD documents for each task.

**Main PRD Documents**:
- [Main PRD Overview](./PRD.md) - Complete project overview
- [Backend Layer PRD](./backend/PRD-Backend.md) - Backend overview
- [Frontend Layer PRD](./frontend/PRD-Frontend.md) - Frontend overview
- [Service Layer PRD](./service/PRD-Service.md) - Service layer overview
- [Architecture Document](./architecture.md) - Complete system architecture

---

## Project Phases Overview

### Phase 1: Foundation & Backend Core (Weeks 1-3)
**Goal**: Set up infrastructure and core backend services

### Phase 2: Service Layer - Data Processing (Weeks 4-6)
**Goal**: Implement data ingestion, feature engineering, and persona assignment

### Phase 3: Service Layer - Recommendations & Guardrails (Weeks 7-9)
**Goal**: Build recommendation engine with OpenAI integration and guardrails

### Phase 4: Frontend Development (Weeks 10-12)
**Goal**: Build React frontend and operator dashboard

### Phase 5: Integration & Testing (Weeks 13-14)
**Goal**: Integrate all layers, end-to-end testing, mobile API compatibility

### Phase 6: AWS Deployment & CI/CD (Weeks 15-16)
**Goal**: Deploy to AWS, set up CI/CD pipeline, production readiness

### Phase 7: Operator View & Evaluation (Weeks 17-18)
**Goal**: Complete operator dashboard, evaluation system, final testing

### Phase 8: Mobile App (Future - Weeks 19+)
**Goal**: iOS mobile app development (if time permits)

---

## Phase 1: Foundation & Backend Core (Weeks 1-3)

### Week 1: Project Setup & Infrastructure

**Task 1.1: Project Setup** ✅
- [x] Initialize project repository
- [x] Set up project structure (backend, frontend, service)
- [x] Configure development environment
- [x] Set up version control and branch strategy
- **PRD Reference**: [Architecture Document](./architecture.md#technology-stack-versions)

**Task 1.2: Database Design & Setup** ✅
- [x] Design PostgreSQL schema
- [x] Create Alembic migrations
- [x] Set up local PostgreSQL database
- [x] Create SQLAlchemy models
- **PRD References**:
  - [Database & Storage](./backend/Database-Storage.md#database-schema)
  - [Architecture Document](./architecture.md#database-postgresql)

**Task 1.3: AWS Infrastructure Setup (Development)** ✅
- [x] Set up AWS account and IAM roles
- [x] Create VPC and networking (dev environment)
- [x] Set up RDS PostgreSQL instance (dev)
- [x] Set up ElastiCache Redis (dev)
- [x] Set up S3 buckets (dev)
- **PRD References**:
  - [Deployment & Infrastructure](./backend/Deployment-Infrastructure.md#terraform)
  - [Architecture Document](./architecture.md#aws-services)

### Week 2: Authentication & Authorization

**Task 2.1: Authentication Foundation** ✅
- [x] Implement JWT token generation/validation
- [x] Set up password hashing (bcrypt)
- [x] Create authentication middleware
- [x] Implement token refresh mechanism
- **PRD References**:
  - [Authentication & Authorization](./backend/Authentication-Authorization.md#token-management)
  - [Security](./backend/Security.md#sr-be-001-authentication-security)

**Task 2.2: Email/Password Authentication** ✅
- [x] Implement user registration (email + password)
- [x] Implement user login (email + password)
- [x] Create user management endpoints
- [x] Add input validation (email, password strength)
- **PRD References**:
  - [API Requirements](./backend/API-Requirements.md#authentication-endpoints)
  - [Authentication & Authorization](./backend/Authentication-Authorization.md#emailusername--password)

**Task 2.3: Phone/SMS Authentication** ✅
- [x] Integrate AWS SNS for SMS
- [x] Implement phone verification code generation
- [x] Create phone verification endpoints
- [x] Add rate limiting for SMS
- **PRD References**:
  - [API Requirements](./backend/API-Requirements.md#authentication-endpoints)
  - [Authentication & Authorization](./backend/Authentication-Authorization.md#phone-number--sms)
  - [Security](./backend/Security.md#rate-limiting)

**Task 2.4: OAuth Integration** ✅
- [x] Set up Google OAuth
- [x] Set up GitHub OAuth (structure ready, credentials needed)
- [x] Set up Facebook OAuth (structure ready, credentials needed)
- [x] Set up Apple Sign In (structure ready, credentials needed)
- [x] Implement OAuth callback handlers
- **PRD References**:
  - [API Requirements](./backend/API-Requirements.md#authentication-endpoints)
  - [Authentication & Authorization](./backend/Authentication-Authorization.md#oauth-20-google-github-facebook-apple)
  - [Security](./backend/Security.md#oauth-security)

**Task 2.5: Account Linking**
- [ ] Implement account linking endpoints
- [ ] Create account merging logic
- [ ] Add account unlinking functionality
- **PRD References**:
  - [API Requirements](./backend/API-Requirements.md#account-linking-endpoints)
  - [Authentication & Authorization](./backend/Authentication-Authorization.md#account-linking)

**Task 2.6: Authorization (RBAC)**
- [ ] Implement role-based access control
- [ ] Create authorization middleware
- [ ] Add endpoint-level authorization checks
- [ ] Add resource-level authorization checks
- **PRD References**:
  - [Authentication & Authorization](./backend/Authentication-Authorization.md#authorization)
  - [Security](./backend/Security.md#sr-be-002-authorization)

### Week 3: Core API & Data Models

**Task 3.1: User Management API**
- [ ] Implement user profile endpoints
- [ ] Create consent management API
- [ ] Add user data deletion endpoint
- **PRD References**:
  - [API Requirements](./backend/API-Requirements.md#user-management-endpoints)
  - [Database & Storage](./backend/Database-Storage.md#database-schema)

**Task 3.2: Data Upload API**
- [ ] Create file upload endpoint
- [ ] Implement file validation (format, size)
- [ ] Integrate S3 file storage
- [ ] Create upload status tracking
- **PRD References**:
  - [API Requirements](./backend/API-Requirements.md#data-management-endpoints)
  - [Database & Storage](./backend/Database-Storage.md#file-storage)
  - [File Upload Flow](./backend/Database-Storage.md#file-upload-flow)

**Task 3.3: Caching Infrastructure**
- [ ] Set up Redis connection
- [ ] Implement session storage in Redis
- [ ] Create API response caching
- [ ] Implement cache invalidation strategy
- **PRD References**:
  - [Database & Storage](./backend/Database-Storage.md#caching)
  - [Non-Functional Requirements](./backend/Non-Functional-Requirements.md#nfr-be-001-performance)

**Task 3.4: API Documentation**
- [ ] Set up OpenAPI/Swagger documentation
- [ ] Document all API endpoints
- [ ] Add request/response examples
- **PRD References**:
  - [API Requirements](./backend/API-Requirements.md#openapi-documentation)
  - [Technical Requirements](./backend/API-Requirements.md#technical-requirements)

---

## Phase 2: Service Layer - Data Processing (Weeks 4-6)

### Week 4: Data Ingestion & Validation

**Task 4.1: Data Ingestion Service**
- [ ] Create Plaid data parser (JSON/CSV)
- [ ] Implement data validation
- [ ] Store data in PostgreSQL
- [ ] Store data in S3 (Parquet)
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-001-data-ingestion-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-001-data-ingestion)

**Task 4.2: Data Validation Service**
- [ ] Validate account structure
- [ ] Validate transaction structure
- [ ] Validate liability structure
- [ ] Create validation error reporting
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-002-data-validation-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-001-data-ingestion)

**Task 4.3: Synthetic Data Generator**
- [ ] Create synthetic Plaid data generator
- [ ] Generate 50-100 diverse user profiles
- [ ] Validate generated data
- [ ] Export to JSON/CSV formats
- **PRD References**:
  - [Main PRD](./PRD.md#fr-001-data-ingestion)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-001-service-structure)

### Week 5: Feature Engineering - Signals Detection

**Task 5.1: Subscription Detection**
- [ ] Identify recurring merchants (≥3 in 90 days)
- [ ] Calculate monthly/weekly cadence
- [ ] Compute monthly recurring spend
- [ ] Calculate subscription share of total spend
- [ ] Generate signals for 30-day and 180-day windows
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-003-subscription-detection-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-002-behavioral-signal-detection)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-004-feature-engineering)

**Task 5.2: Savings Pattern Detection**
- [ ] Calculate net inflow to savings accounts
- [ ] Compute savings growth rate
- [ ] Calculate emergency fund coverage
- [ ] Track savings patterns over time windows
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-004-savings-pattern-detection-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-002-behavioral-signal-detection)

**Task 5.3: Credit Utilization Detection**
- [ ] Calculate utilization = balance / limit for each card
- [ ] Flag cards at ≥30%, ≥50%, ≥80% utilization
- [ ] Detect minimum-payment-only behavior
- [ ] Identify interest charges
- [ ] Flag overdue accounts
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-005-credit-utilization-detection-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-002-behavioral-signal-detection)

**Task 5.4: Income Stability Detection**
- [ ] Detect payroll ACH deposits
- [ ] Calculate payment frequency and variability
- [ ] Calculate cash-flow buffer in months
- [ ] Identify variable income patterns
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-006-income-stability-detection-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-002-behavioral-signal-detection)

**Task 5.5: Feature Caching**
- [ ] Implement Redis caching for computed features
- [ ] Set TTL for cached features (24 hours)
- [ ] Create cache invalidation on data updates
- **PRD References**:
  - [Database & Storage](./backend/Database-Storage.md#cache-strategy)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-004-feature-engineering)

### Week 6: Persona Assignment

**Task 6.1: Persona Assignment Logic**
- [ ] Implement Persona 1: High Utilization
- [ ] Implement Persona 2: Variable Income Budgeter
- [ ] Implement Persona 3: Subscription-Heavy
- [ ] Implement Persona 4: Savings Builder
- [ ] Implement Persona 5: Custom Persona
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-007-persona-assignment-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-003-persona-assignment)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-005-persona-assignment-logic)

**Task 6.2: Priority Logic**
- [ ] Implement priority-based assignment when multiple personas match
- [ ] Create persona rationale generation
- [ ] Store persona assignments with timestamps
- **PRD References**:
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-005-persona-assignment-logic)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-003-persona-assignment)

**Task 6.3: Persona History Tracking**
- [ ] Track persona transitions over time
- [ ] Store persona history in database
- [ ] Create persona history API endpoint
- **PRD References**:
  - [Database & Storage](./backend/Database-Storage.md#persona-history-table)
  - [API Requirements](./backend/API-Requirements.md#profile--recommendations-endpoints)

---

## Phase 3: Service Layer - Recommendations & Guardrails (Weeks 7-9)

### Week 7: Recommendation Generation

**Task 7.1: Recommendation Engine Foundation**
- [ ] Create recommendation generation service
- [ ] Implement education item selection (3-5 per user)
- [ ] Implement partner offer selection (1-3 per user)
- [ ] Match recommendations to personas
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-008-recommendation-generation-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-004-recommendation-generation)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-006-recommendation-generation)

**Task 7.2: Rationale Generation**
- [ ] Create rationale generation service
- [ ] Implement plain-language rationale generation
- [ ] Cite specific data points (accounts, amounts, dates)
- [ ] Avoid financial jargon
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-009-rationale-generation-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-004-recommendation-generation)

**Task 7.3: OpenAI Integration**
- [ ] Set up OpenAI SDK
- [ ] Create OpenAI client utilities
- [ ] Implement content generation using GPT-4/GPT-3.5
- [ ] Add fallback to pre-generated templates
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-010-content-generation-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-005-content-generation-openai)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-003-openai-integration)

**Task 7.4: Partner Offer Service**
- [ ] Create partner offer catalog
- [ ] Implement offer selection logic
- [ ] Add eligibility checking
- [ ] Filter offers for products user already has
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-011-partner-offer-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-004-recommendation-generation)

### Week 8: Guardrails Implementation

**Task 8.1: Consent Guardrails**
- [ ] Check consent status before data processing
- [ ] Block recommendations if consent not granted
- [ ] Log consent checks
- [ ] Support data deletion on consent revocation
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-012-consent-guardrails-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-006-consent-guardrails)
  - [Main PRD](./PRD.md#cr-002-consent-management)

**Task 8.2: Eligibility Validation**
- [ ] Check minimum income requirements
- [ ] Check minimum credit score requirements
- [ ] Filter offers for products user already has
- [ ] Block harmful products (payday loans, predatory loans)
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-013-eligibility-validation-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-007-eligibility-guardrails)
  - [Main PRD](./PRD.md#cr-004-eligibility-checks)

**Task 8.3: Tone Validation**
- [ ] Validate recommendation text for shaming language
- [ ] Enforce empowering, educational tone
- [ ] Avoid judgmental phrases
- [ ] Use OpenAI for tone validation (optional)
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-014-tone-validation-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-008-tone-validation)
  - [Main PRD](./PRD.md#cr-005-harmful-product-filtering)

**Task 8.4: Regulatory Disclaimers**
- [ ] Add disclaimer to every recommendation
- [ ] Validate disclaimer presence
- [ ] Ensure disclaimers are prominent
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-015-regulatory-disclaimers-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-009-regulatory-disclaimers)
  - [Main PRD](./PRD.md#cr-001-financial-advice-disclaimer)

### Week 9: Decision Traces & Evaluation

**Task 9.1: Decision Trace Generation**
- [ ] Create decision trace structure
- [ ] Store decision traces for all recommendations
- [ ] Include detected signals, persona logic, guardrails checks
- [ ] Generate human-readable decision traces
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-017-decision-trace-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-011-decision-trace-generation)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-009-decision-trace-structure)

**Task 9.2: Evaluation Service**
- [ ] Implement coverage metrics (% users with persona + ≥3 behaviors)
- [ ] Implement explainability metrics (% recommendations with rationales)
- [ ] Implement relevance metrics (education-persona fit)
- [ ] Implement latency metrics (generation time <5 seconds)
- [ ] Implement fairness metrics (demographic parity)
- **PRD References**:
  - [Service Layer PRD](./service/PRD-Service.md#sv-us-016-evaluation-service)
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-010-evaluation--metrics)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-008-evaluation-metrics)

**Task 9.3: Report Generation**
- [ ] Generate JSON/CSV metrics file
- [ ] Generate brief summary report (1-2 pages)
- [ ] Generate per-user decision traces
- **PRD References**:
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-010-evaluation--metrics)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-008-evaluation-metrics)

---

## Phase 4: Frontend Development (Weeks 10-12)

### Week 10: Frontend Foundation & Authentication

**Task 10.1: Frontend Project Setup**
- [ ] Initialize React project with TypeScript
- [ ] Set up Vite build tool
- [ ] Configure React Router
- [ ] Set up state management (Zustand/Redux)
- [ ] Configure Axios for API calls
- **PRD References**:
  - [Frontend Technical Requirements](./frontend/Technical-Requirements.md#tr-fe-001-react-application-structure)
  - [Frontend Technical Requirements](./frontend/Technical-Requirements.md#tr-fe-002-routing)

**Task 10.2: Authentication UI**
- [ ] Create login/registration pages
- [ ] Implement email/password authentication UI
- [ ] Implement phone/SMS authentication UI
- [ ] Implement OAuth buttons (Google, GitHub, Facebook, Apple)
- [ ] Add form validation and error handling
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-001-user-registration-ui)
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-002-user-login-ui)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-001-authentication-ui)

**Task 10.3: Token Management**
- [ ] Implement token storage (localStorage/sessionStorage)
- [ ] Create token refresh mechanism
- [ ] Implement logout functionality
- [ ] Add token expiration handling
- **PRD References**:
  - [Frontend Technical Requirements](./frontend/Technical-Requirements.md#tr-fe-003-api-integration)
  - [Frontend Technical Requirements](./frontend/Technical-Requirements.md#tr-fe-004-state-management)

**Task 10.4: Account Linking UI**
- [ ] Create account linking settings page
- [ ] Implement OAuth provider linking
- [ ] Implement phone number linking
- [ ] Add account unlinking functionality
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-003-account-linking-ui)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-001-authentication-ui)

### Week 11: User Dashboard & Profile

**Task 11.1: Dashboard Page**
- [ ] Create personalized dashboard layout
- [ ] Display assigned persona
- [ ] Show key behavioral signals
- [ ] Display recommendations list
- [ ] Show consent status
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-005-personalized-dashboard)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-002-user-dashboard)
  - [Frontend User Experience](./frontend/User-Experience-Requirements.md#key-screens)

**Task 11.2: Profile View**
- [ ] Create profile page layout
- [ ] Display detected signals (subscriptions, savings, credit, income)
- [ ] Show 30-day and 180-day analysis with time selector
- [ ] Display persona history timeline
- [ ] Show signal trends (charts/graphs)
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-006-profile-view)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-003-profile-view)

**Task 11.3: Recommendations View**
- [ ] Create recommendations list page
- [ ] Display recommendations with rationales
- [ ] Show partner offers with eligibility badges
- [ ] Add "Because" section explaining each recommendation
- [ ] Implement recommendation actions (View, Dismiss, Save)
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-007-recommendations-view)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-004-recommendations-ui)

**Task 11.4: Recommendation Detail View**
- [ ] Create recommendation detail page
- [ ] Display full recommendation content
- [ ] Show detailed rationale with cited data points
- [ ] Show eligibility explanation for partner offers
- [ ] Display regulatory disclaimer prominently
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-008-recommendation-detail-view)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-004-recommendations-ui)

### Week 12: Data Upload & Consent Management

**Task 12.1: Data Upload UI**
- [ ] Create file upload component (drag-and-drop + file picker)
- [ ] Support JSON and CSV formats
- [ ] Add file format validation
- [ ] Implement upload progress indicator
- [ ] Show upload status and errors
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-010-transaction-data-upload)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-006-data-upload-ui)

**Task 12.2: Consent Management UI**
- [ ] Create consent management settings page
- [ ] Display consent status indicator
- [ ] Add consent toggle with explanation
- [ ] Implement confirmation dialog for revocation
- [ ] Show data deletion option
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-009-consent-management-ui)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-005-consent-management-ui)

**Task 12.3: Mobile Responsiveness**
- [ ] Ensure all pages are mobile-responsive
- [ ] Test on various screen sizes
- [ ] Optimize for touch interactions
- [ ] Add mobile-specific UI improvements
- **PRD References**:
  - [Frontend Non-Functional Requirements](./frontend/Non-Functional-Requirements.md#nfr-fe-002-responsiveness)
  - [Frontend User Experience](./frontend/User-Experience-Requirements.md#design-principles)

**Task 12.4: UI Polish & Accessibility**
- [ ] Add loading states (skeleton screens/spinners)
- [ ] Implement error states with retry actions
- [ ] Add empty states with helpful guidance
- [ ] Ensure WCAG 2.1 AA compliance
- [ ] Add keyboard navigation support
- **PRD References**:
  - [Frontend Non-Functional Requirements](./frontend/Non-Functional-Requirements.md#nfr-fe-003-accessibility)
  - [Frontend User Experience](./frontend/User-Experience-Requirements.md#ux-features)

---

## Phase 5: Integration & Testing (Weeks 13-14)

### Week 13: Backend-Frontend Integration

**Task 13.1: API Integration**
- [ ] Integrate all frontend pages with backend APIs
- [ ] Add error handling for API calls
- [ ] Implement request/response interceptors
- [ ] Add loading states for async operations
- **PRD References**:
  - [Frontend Technical Requirements](./frontend/Technical-Requirements.md#tr-fe-003-api-integration)
  - [Backend API Requirements](./backend/API-Requirements.md)

**Task 13.2: End-to-End Testing**
- [ ] Test complete user flows (registration → upload → recommendations)
- [ ] Test authentication flows (email, phone, OAuth)
- [ ] Test consent management flow
- [ ] Test data upload and processing flow
- **PRD References**:
  - [Main PRD](./PRD.md#acceptance-criteria-summary)
  - [Backend Non-Functional Requirements](./backend/Non-Functional-Requirements.md#nfr-be-005-maintainability)

**Task 13.3: Mobile API Compatibility**
- [ ] Optimize API responses for mobile
- [ ] Add mobile-specific endpoints if needed
- [ ] Test API performance on mobile networks
- **PRD References**:
  - [Main PRD](./PRD.md#phase-5-mobile-api-compatibility-weeks-13-14)
  - [Architecture Document](./architecture.md#mobile-compatibility)

### Week 14: Testing & Quality Assurance

**Task 14.1: Unit Testing**
- [ ] Write unit tests for backend services (≥80% coverage)
- [ ] Write unit tests for frontend components
- [ ] Write unit tests for service layer (feature engineering, personas)
- **PRD References**:
  - [Backend Non-Functional Requirements](./backend/Non-Functional-Requirements.md#nfr-be-005-maintainability)
  - [Frontend Technical Requirements](./frontend/Technical-Requirements.md#tr-fe-006-testing)

**Task 14.2: Integration Testing**
- [ ] Test API endpoint integration
- [ ] Test database interactions
- [ ] Test Redis caching
- [ ] Test S3 file operations
- **PRD References**:
  - [Backend Non-Functional Requirements](./backend/Non-Functional-Requirements.md#nfr-be-005-maintainability)
  - [Service Non-Functional Requirements](./service/PRD-Service-Non-Functional-Requirements.md#nfr-sv-004-maintainability)

**Task 14.3: Performance Testing**
- [ ] Test API response times (<200ms p95)
- [ ] Test database query times (<100ms p95)
- [ ] Test recommendation generation (<5 seconds)
- [ ] Load testing (1000+ concurrent users)
- **PRD References**:
  - [Backend Non-Functional Requirements](./backend/Non-Functional-Requirements.md#nfr-be-001-performance)
  - [Service Non-Functional Requirements](./service/PRD-Service-Non-Functional-Requirements.md#nfr-sv-001-performance)

**Task 14.4: Security Testing**
- [ ] Test authentication security
- [ ] Test authorization checks
- [ ] Test input validation
- [ ] Test rate limiting
- [ ] Penetration testing (if time permits)
- **PRD References**:
  - [Backend Security](./backend/Security.md)
  - [Main PRD](./PRD.md#compliance--regulatory-requirements)

---

## Phase 6: AWS Deployment & CI/CD (Weeks 15-16)

### Week 15: Containerization & ECS Setup

**Task 15.1: Docker Containerization**
- [ ] Create Dockerfile for backend
- [ ] Optimize Docker image (multi-stage build)
- [ ] Set up health check endpoint
- [ ] Configure non-root user
- **PRD References**:
  - [Deployment & Infrastructure](./backend/Deployment-Infrastructure.md#containerization)
  - [Backend Technical Requirements](./backend/Deployment-Infrastructure.md#tr-be-005-deployment)

**Task 15.2: ECS Fargate Deployment**
- [ ] Create ECS task definition
- [ ] Set up ECS service with auto-scaling
- [ ] Configure Application Load Balancer (ALB)
- [ ] Set up health checks
- **PRD References**:
  - [Deployment & Infrastructure](./backend/Deployment-Infrastructure.md#ecs-fargate-deployment)
  - [Architecture Document](./architecture.md#aws-services)

**Task 15.3: Terraform Infrastructure**
- [ ] Create Terraform configuration
- [ ] Set up VPC and networking (production)
- [ ] Create RDS PostgreSQL instance (production)
- [ ] Create ElastiCache Redis (production)
- [ ] Set up S3 buckets (production)
- [ ] Configure security groups and IAM roles
- **PRD References**:
  - [Deployment & Infrastructure](./backend/Deployment-Infrastructure.md#infrastructure-as-code)
  - [Architecture Document](./architecture.md#aws-services)

### Week 16: CI/CD Pipeline

**Task 16.1: GitHub Actions Setup**
- [ ] Create GitHub Actions workflow
- [ ] Set up automated testing in CI
- [ ] Configure Docker image building
- [ ] Set up ECR image push
- **PRD References**:
  - [Deployment & Infrastructure](./backend/Deployment-Infrastructure.md#cicd-pipeline)
  - [Architecture Document](./architecture.md#cicd-pipeline)

**Task 16.2: Automated Deployment**
- [ ] Set up ECS deployment automation
- [ ] Configure environment-specific deployments (dev, staging, prod)
- [ ] Add deployment rollback capability
- [ ] Set up deployment notifications
- **PRD References**:
  - [Deployment & Infrastructure](./backend/Deployment-Infrastructure.md#deployment-strategy)
  - [Architecture Document](./architecture.md#cicd-pipeline)

**Task 16.3: Monitoring & Logging**
- [ ] Set up CloudWatch Logs
- [ ] Configure CloudWatch Metrics
- [ ] Create CloudWatch Alarms
- [ ] Set up dashboards
- **PRD References**:
  - [Deployment & Infrastructure](./backend/Deployment-Infrastructure.md#monitoring--logging)
  - [Backend Non-Functional Requirements](./backend/Non-Functional-Requirements.md#monitoring--alerting)
  - [Architecture Document](./architecture.md#monitoring)

**Task 16.4: Secrets Management**
- [ ] Set up AWS Secrets Manager
- [ ] Store database credentials
- [ ] Store JWT secrets
- [ ] Store OAuth credentials
- [ ] Store OpenAI API key
- **PRD References**:
  - [Security](./backend/Security.md#sr-be-003-data-security)
  - [Architecture Document](./architecture.md#secrets-management)

---

## Phase 7: Operator View & Evaluation (Weeks 17-18)

### Week 17: Operator Dashboard

**Task 17.1: Operator Dashboard Foundation**
- [ ] Create operator dashboard layout
- [ ] Set up operator authentication/authorization
- [ ] Create review queue page
- **PRD References**:
  - [Frontend Operator Dashboard](./frontend/Operator-Dashboard.md)
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-011-review-queue-dashboard)
  - [Backend API Requirements](./backend/API-Requirements.md#operator-endpoints)

**Task 17.2: Review Queue Features**
- [ ] Display pending recommendations list
- [ ] Add filters (user, persona, recommendation type, date)
- [ ] Add sorting (priority, date, user)
- [ ] Implement search functionality
- [ ] Add bulk operations (bulk approve/reject)
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-011-review-queue-dashboard)
  - [Frontend Functional Requirements](./frontend/Functional-Requirements.md#fr-fe-007-operator-dashboard)

**Task 17.3: Recommendation Review View**
- [ ] Create recommendation review detail page
- [ ] Display full recommendation content
- [ ] Show decision trace with expandable sections
- [ ] Display detected behavioral signals
- [ ] Show persona assignment logic
- [ ] Display guardrails checks performed
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-012-recommendation-review-view)
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-014-decision-trace-view)

**Task 17.4: Approve/Reject Functionality**
- [ ] Implement approve button
- [ ] Implement reject button with reason
- [ ] Implement modify recommendation functionality
- [ ] Add approval/rejection confirmation dialogs
- [ ] Log all operator actions
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-012-recommendation-review-view)
  - [Backend API Requirements](./backend/API-Requirements.md#operator-endpoints)

### Week 18: Analytics & Final Testing

**Task 18.1: Operator Analytics Dashboard**
- [ ] Create analytics dashboard page
- [ ] Display coverage metrics
- [ ] Display explainability metrics
- [ ] Display performance metrics
- [ ] Display user engagement metrics
- [ ] Add charts and graphs
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-015-analytics-dashboard-operator)
  - [Backend API Requirements](./backend/API-Requirements.md#operator-endpoints)

**Task 18.2: User Detail View (Operator)**
- [ ] Create user detail view for operators
- [ ] Display complete user profile
- [ ] Show all detected signals
- [ ] Display 30-day and 180-day analysis
- [ ] Show persona history timeline
- [ ] Display all recommendations for user
- **PRD References**:
  - [Frontend User Stories](./frontend/User-Stories.md#fe-us-013-user-detail-view-operator)
  - [Backend API Requirements](./backend/API-Requirements.md#operator-endpoints)

**Task 18.3: Evaluation System Integration**
- [ ] Integrate evaluation service with operator dashboard
- [ ] Display evaluation metrics in dashboard
- [ ] Add export functionality (JSON/CSV)
- [ ] Generate summary reports
- **PRD References**:
  - [Service Functional Requirements](./service/PRD-Service-Functional-Requirements.md#fr-sv-010-evaluation--metrics)
  - [Service Technical Requirements](./service/PRD-Service-Technical-Requirements.md#tr-sv-008-evaluation-metrics)

**Task 18.4: Final Testing & Documentation**
- [ ] Complete end-to-end testing
- [ ] Performance testing in production-like environment
- [ ] Security audit
- [ ] Update API documentation
- [ ] Create user documentation
- [ ] Create operator documentation
- **PRD References**:
  - [Main PRD](./PRD.md#acceptance-criteria-summary)
  - [Backend Non-Functional Requirements](./backend/Non-Functional-Requirements.md#nfr-be-005-maintainability)

---

## Phase 8: Mobile App (Future - Weeks 19+)

**Note**: This phase is planned for future implementation and is not part of the MVP.

**Task 19.1: Swift App Foundation**
- [ ] Initialize Swift/iOS project
- [ ] Set up SwiftUI structure
- [ ] Configure API client
- **PRD References**:
  - [Architecture Document](./architecture.md#mobile-compatibility)
  - [Main PRD](./PRD.md#phase-8-swift-mobile-app-future-weeks-19)

**Task 19.2: Mobile Authentication**
- [ ] Implement native authentication UI
- [ ] Add Face ID / Touch ID support
- [ ] Integrate with backend auth APIs
- **PRD References**:
  - [Architecture Document](./architecture.md#mobile-compatibility)
  - [Backend Authentication](./backend/Authentication-Authorization.md)

**Task 19.3: Mobile Dashboard & Features**
- [ ] Create mobile dashboard
- [ ] Implement recommendations view
- [ ] Add push notifications
- [ ] Implement offline caching
- **PRD References**:
  - [Architecture Document](./architecture.md#mobile-compatibility)
  - [Main PRD](./PRD.md#phase-8-swift-mobile-app-future-weeks-19)

---

## Dependencies Matrix

### Critical Path Dependencies

**Phase 1 → Phase 2**: Backend API must be ready before service layer can integrate  
**Phase 2 → Phase 3**: Feature engineering must be complete before recommendation generation  
**Phase 3 → Phase 4**: Recommendations must be generated before frontend can display them  
**Phase 4 → Phase 5**: Frontend must be functional before integration testing  
**Phase 5 → Phase 6**: Integration testing must pass before production deployment  
**Phase 6 → Phase 7**: Production deployment must be stable before operator dashboard completion  

### Parallel Work Opportunities

- **Week 4-6**: Service layer data processing (independent from frontend)
- **Week 10-12**: Frontend development (independent from service layer recommendations)
- **Week 13**: API integration and testing can be done in parallel
- **Week 17-18**: Operator dashboard and evaluation can be done in parallel

---

## Success Criteria Checklist

### Must Have (MVP)

- [x] Synthetic data generator (50-100 users)
- [x] Feature pipeline (subscriptions, savings, credit, income)
- [x] Persona assignment (5 personas)
- [x] Recommendation engine with rationales
- [x] Consent and eligibility guardrails
- [x] Operator view
- [x] Evaluation harness with metrics
- [x] React web application
- [x] AWS deployment
- [x] CI/CD pipeline

### Should Have

- [ ] OAuth authentication (all providers)
- [ ] Phone number authentication
- [ ] Account linking
- [ ] Comprehensive test suite (≥80% coverage)
- [ ] Complete API documentation

### Nice to Have

- [ ] Swift mobile app (Phase 8)
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] Real-time WebSocket updates

---

## Risk Management

### High-Risk Items

**Risk 1**: OpenAI API Downtime → Mitigation: Fallback to pre-generated templates  
**PRD Reference**: [Service Risks](./service/PRD-Service-Metrics-Dependencies-Risks.md#risk-sv-001-openai-api-downtime)

**Risk 2**: Performance Degradation → Mitigation: Caching, async processing, auto-scaling  
**PRD Reference**: [Backend Risks](./backend/PRD-Backend.md#risk-be-004-scalability-issues)

**Risk 3**: OAuth Provider Changes → Mitigation: Monitor API changes, version integrations  
**PRD Reference**: [Backend Risks](./backend/PRD-Backend.md#risk-be-003-oauth-provider-changes)

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial project plan | TBD |
| 1.1 | 2024-01-15 | Task 1.1 completed - Project setup, structure, gitignore, documentation | TBD |
| 1.2 | 2025-11-03 | Task 1.2 completed - Database design, Alembic migrations, PostgreSQL setup, SQLAlchemy models | TBD |
| 1.3 | 2025-11-03 | Task 1.3 completed - AWS Infrastructure Setup (Development): Terraform modules for VPC, RDS PostgreSQL 16.10, ElastiCache Redis 7.1, S3 buckets, IAM roles. Includes owner_id support for shared AWS accounts (us-west-1 region). | TBD |
| 1.4 | 2025-11-03 | Task 2.1 completed - Authentication Foundation: JWT token generation/validation (RS256), password hashing (bcrypt cost factor 12), authentication middleware, token refresh mechanism. Includes RSA key generation utilities and authentication dependencies. | TBD |
| 1.5 | 2025-11-03 | Task 2.2 completed - Email/Password Authentication: User registration and login endpoints, password validation (12+ chars, uppercase, lowercase, digit, special char), email validation, user management endpoints (GET/PUT /api/v1/users/me), token refresh and logout. Fixed enum role storage, refresh token length (1000 chars), and session management. | TBD |
| 1.6 | 2025-11-03 | Task 2.3 completed - Phone/SMS Authentication: Integrated AWS SNS for SMS sending, implemented phone verification code generation (6-digit cryptographically secure), created Redis connection utility for code storage (10-minute TTL), added rate limiting (5 SMS/hour, 10 SMS/day per phone), implemented phone validation using phonenumbers library (E.164 format), created POST /api/v1/auth/phone/request and POST /api/v1/auth/phone/verify endpoints with automatic user registration/login. | TBD |

---

**Document Status**: Draft  
**Next Review Date**: TBD  
**Approval Required From**: Product Owner, Project Manager, Technical Leads


