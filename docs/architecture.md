# SpendSense Architecture Documentation
## Version 1.0.0

**Last Updated**: 2025-11-04  
**Status**: Development Phase (Phase 1 - Task 1.1 Complete)

---

## Technology Stack Versions

### Backend Framework
- **FastAPI**: `0.109.0` (latest stable)
- **Python**: `3.11.7` (recommended) or `3.10+`
- **Uvicorn**: `0.27.0` (ASGI server)
- **Pydantic**: `2.5.0` (data validation)
- **email-validator**: `2.3.0` (email validation for Pydantic)
- **SQLAlchemy**: `2.0.23` (ORM)
- **Alembic**: `1.13.0` (database migrations)

### Frontend Framework
- **React**: `18.2.0`
- **TypeScript**: `5.3.3`
- **Vite**: `5.0.11` (build tool) or Create React App
- **React Router**: `6.21.1`
- **Axios**: `1.6.5` (HTTP client)
- **React Query**: `5.17.0` (data fetching)

### Mobile (Future)
- **Swift**: `5.9+` (iOS 17+)
- **SwiftUI**: `5.0+`
- **iOS**: `17.0+` (minimum deployment target)

### AI/LLM Integration
- **OpenAI SDK (Python)**: `1.12.0`
- **OpenAI API Version**: `v1`
- **Model**: `gpt-4-turbo-preview` or `gpt-3.5-turbo` (for cost optimization)

### Database & Data Processing
- **PostgreSQL**: `16.10` (RDS) - Note: Version adjusted for us-west-1 availability
- **psycopg2**: `2.9.9` (PostgreSQL adapter)
- **Pandas**: `2.1.4` (data analysis)
- **NumPy**: `1.26.3` (numerical computing)
- **PyArrow**: `15.0.0` (Parquet file support)

### Caching & Sessions
- **Redis**: `7.1` (ElastiCache) - Note: Version adjusted for us-west-1 availability
- **redis-py**: `5.0.1` (Python Redis client)
- **hiredis**: `2.2.3` (C parser for performance)

### AWS SDK
- **boto3**: `1.34.34` (AWS SDK for Python)
- **botocore**: `1.34.34`
- **aioboto3**: `12.3.0` (async AWS operations)

### Testing Frameworks
- **pytest**: `7.4.4`
- **pytest-asyncio**: `0.23.3`
- **pytest-cov**: `4.1.0` (coverage)
- **httpx**: `0.26.0` (async HTTP client for testing)
- **Jest**: `29.7.0` (React testing)
- **React Testing Library**: `14.1.2`
- **Playwright**: `1.41.0` (E2E testing)

### CI/CD & DevOps
- **GitHub Actions**: Latest (workflow files)
- **Docker**: `24.0.7+` (containerization)
- **Terraform**: `1.6.6` (Infrastructure as Code)
- **AWS CLI**: `2.15.25+`

### Code Quality
- **black**: `24.1.1` (Python formatter)
- **pylint**: `3.0.3` (Python linter)
- **mypy**: `1.8.0` (type checking)
- **ESLint**: `8.56.0` (JavaScript/TypeScript linter)
- **Prettier**: `3.2.4` (code formatter)

### Documentation
- **Sphinx**: `7.2.6` (Python docs) - Optional
- **MkDocs**: `1.5.3` (Markdown docs) - Optional

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  React Web App   │  │  Swift iOS App   │  │  Operator View   │       │
│  │  (S3+CloudFront) │  │  (App Store)     │  │  (React Web)     │       │
│  │  React 18.2.0    │  │  Swift 5.9+      │  │  React 18.2.0    │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                                 │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              AWS API Gateway v2                                  │   │
│  │  • REST API Routing                                               │   │
│  │  • Authentication (FastAPI-managed)                                  │   │
│  │  • Rate Limiting & Throttling                                    │   │
│  │  • Request Validation                                             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Load Balancer Layer                                 │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │          Application Load Balancer (ALB)                         │   │
│  │  • SSL Termination (TLS 1.3)                                     │   │
│  │  • Health Checks                                                 │   │
│  │  • Request Routing                                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐
│    ECS Fargate Services     │  │    ECS Fargate Services     │
│  ┌─────────────────────────┐│  │  ┌─────────────────────────┐│
│  │ FastAPI Backend         ││  │  │ Feature Processing      ││
│  │ FastAPI 0.109.0         ││  │  │ Python 3.11             ││
│  │ Uvicorn 0.27.0          ││  │  │ Pandas 2.1.4            ││
│  │ Python 3.11.7           ││  │  │ NumPy 1.26.3            ││
│  │ Container (Docker)      ││  │  │ PyArrow 15.0.0          ││
│  └─────────────────────────┘│  │  └─────────────────────────┘│
└─────────────────────────────┘  └─────────────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ RDS PostgreSQL   │  │  Amazon S3       │  │ ElastiCache      │    │
│  │ Version 16.10    │  │  (S3 Standard)   │  │ Redis 7.1         │    │
│  │ • User Data      │  │  • Parquet Files │  │ • Caching        │    │
│  │ • Transactions   │  │  • Logs          │  │ • Sessions       │    │
│  │ • Personas       │  │  • Reports       │  │ • Rate Limiting  │    │
│  │ • Recommendations│  │  • Analytics     │  └──────────────────┘    │
│  └──────────────────┘  └──────────────────┘                          │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Processing & Integration Layer                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ AWS Lambda       │  │  AWS EventBridge │  │ OpenAI API       │   │
│  │ Python 3.11      │  │  • Scheduled Jobs│  │ API v1           │   │
│  │ • Batch Process  │  │  • Event Routing │  │ GPT-4/GPT-3.5    │   │
│  │ • Data Ingestion │  │                  │  │ • Content Gen    │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐                         │
│  │ Amazon SQS       │  │  Amazon SNS      │                         │
│  │ • Async Tasks    │  │  • Notifications │                         │
│  │ • Recommendation │  │  • Mobile Push   │                         │
│  │   Generation     │  │                  │                         │
│  └──────────────────┘  └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Monitoring & Observability                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ CloudWatch       │  │  CloudWatch      │  │ X-Ray (Optional) │   │
│  │ • Logs           │  │  • Metrics       │  │ • Tracing        │   │
│  │ • Monitoring     │  │  • Alarms        │  │ • Performance    │   │
│  │ • Audit Trails   │  │                  │  └──────────────────┘   │
│  └──────────────────┘  └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Versions & Specifications

### Backend API Service

**Technology Stack:**
```
FastAPI 0.109.0
Python 3.11.7
Uvicorn 0.27.0
Pydantic 2.5.0
SQLAlchemy 2.0.23
Alembic 1.13.0
```

**Container Specifications:**
- **Base Image**: `python:3.11-slim`
- **Platform**: Linux/amd64
- **CPU**: 0.5 vCPU (minimum), 1-2 vCPU (production)
- **Memory**: 1GB (minimum), 2-4GB (production)
- **Port**: 8000

**Dependencies:**
```python
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.3.0
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
redis==5.0.1
boto3==1.34.34
aioboto3==12.3.0
openai==1.12.0
pandas==2.1.4
numpy==1.26.3
pyarrow==15.0.0
httpx==0.26.0
# Authentication & OAuth
authlib==1.3.0              # OAuth 2.0 client library
python-jose[cryptography]==3.3.0  # JWT token handling
passlib[bcrypt]==1.7.4      # Password hashing
phonenumbers==8.13.27       # Phone number validation and formatting
python-multipart==0.0.6     # Form data parsing (for OAuth callbacks)
# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
# Code Quality
black==24.1.1
pylint==3.0.3
mypy==1.8.0
```

### Frontend Web Application

**Technology Stack:**
```
React 18.2.0
TypeScript 5.3.3
Vite 5.0.11
React Router 6.21.1
Axios 1.6.5
React Query 5.17.0
```

**Build Specifications:**
- **Node.js**: `20.10.0` (LTS)
- **Build Tool**: Vite 5.0.11
- **Target Browsers**: 
  - Chrome 90+
  - Firefox 88+
  - Safari 14+
  - Edge 90+
- **Mobile Support**: iOS 14+, Android 8+

**Dependencies:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.1",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.5",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "typescript": "^5.3.3",
    "vite": "^5.0.11",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.56.0",
    "@typescript-eslint/eslint-plugin": "^6.17.0",
    "prettier": "^3.2.4",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "jest": "^29.7.0"
  }
}
```

### Database (RDS PostgreSQL)

**Specifications:**
- **Engine**: PostgreSQL 16.10 (adjusted for us-west-1 availability)
- **Instance Class**: `db.t3.medium` (dev), `db.t3.large` (production)
- **Storage**: 100GB GP3 (dev), 500GB+ GP3 (production)
- **Multi-AZ**: Enabled for production
- **Backup Retention**: 7 days (dev), 30 days (production)
- **Connection Pooling**: PgBouncer or SQLAlchemy pool

**Connection Settings:**
- **Max Connections**: 100 (dev), 500 (production)
- **Connection Pool Size**: 10-20 connections
- **SSL**: Required

### Caching (ElastiCache Redis)

**Specifications:**
- **Engine**: Redis 7.1 (adjusted for us-west-1 availability)
- **Node Type**: `cache.t3.micro` (dev), `cache.t3.small` (production)
- **Cluster Mode**: Disabled (single node) or Enabled (multi-node)
- **Encryption**: At rest and in transit
- **Auth Token**: Enabled

**Use Cases:**
- Session storage
- API response caching
- Rate limiting counters
- Feature computation caching

### Object Storage (S3)

**Buckets:**
1. **spendsense-data-{env}[-{owner_id}]**
   - Parquet analytics files
   - Transaction data archives
   - Lifecycle: Move to Glacier after 90 days
   - Note: `{owner_id}` is optional for shared AWS accounts to avoid naming conflicts

2. **spendsense-logs-{env}[-{owner_id}]**
   - Application logs
   - CloudWatch log exports
   - Lifecycle: Delete after 90 days
   - Note: `{owner_id}` is optional for shared AWS accounts to avoid naming conflicts

3. **spendsense-reports-{env}[-{owner_id}]**
   - Evaluation reports
   - Decision traces
   - Lifecycle: Delete after 1 year
   - Note: `{owner_id}` is optional for shared AWS accounts to avoid naming conflicts

4. **spendsense-frontend-{env}[-{owner_id}]**
   - React build artifacts
   - Static assets
   - CloudFront origin
   - Note: `{owner_id}` is optional for shared AWS accounts to avoid naming conflicts

**Versioning**: Enabled
**Encryption**: AES-256 (SSE-S3)

### Container Registry (ECR)

**Repository**: `spendsense-api`
- **Image Tags**: `latest`, `{git-sha}`, `v{version}`
- **Image Scanning**: Enabled (security)
- **Lifecycle Policy**: Keep last 10 images, delete untagged >30 days

### Compute (ECS Fargate)

**Cluster**: `spendsense-cluster`
**Service**: `spendsense-api-service`

**Task Definition:**
- **Family**: `spendsense-api`
- **CPU**: 512-2048 (0.5-2 vCPU)
- **Memory**: 1024-4096 MB (1-4 GB)
- **Network Mode**: `awsvpc`
- **Platform Version**: `LATEST`

**Auto Scaling:**
- **Min Capacity**: 1
- **Max Capacity**: 10
- **Target Metric**: CPU 70%, Memory 80%
- **Scale Out**: +1 task when threshold exceeded
- **Scale In**: -1 task when below 50% for 5 minutes

### API Gateway

**Type**: REST API (HTTP API v2 recommended for cost)
- **Protocol**: HTTP/1.1, HTTP/2
- **TLS Version**: 1.3
- **CORS**: Enabled
- **Throttling**: 1000 req/s per API key
- **Rate Limiting**: Per IP and per user

### Authentication

**Implementation**: FastAPI-managed authentication with JWT tokens

**Sign-in Methods**: 
- ✅ Email/Username (primary) - Password hashing with bcrypt (cost factor 12)
- ✅ Phone number (SMS verification) - AWS SNS for SMS delivery
- ✅ OAuth providers (Google, GitHub, Facebook, Apple Sign In) - FastAPI-managed OAuth flows

**Password Policy**: 
- Min length: 12
- Require uppercase, lowercase, numbers, symbols

**Token Management**:
- JWT tokens (RS256 algorithm)
- Access token expiration: 1 hour
- Refresh token expiration: 30 days
- Token storage: PostgreSQL (Sessions table)
- Token blacklisting: Redis (optional)

**MFA**: Optional (recommended for operators) - Future enhancement

**Note**: The implementation uses FastAPI-managed OAuth (not AWS Cognito) for direct control and flexibility. OAuth credentials are stored in environment variables (development) or AWS Secrets Manager (production).

**OAuth Identity Providers Configuration:**

*Note: The implementation uses FastAPI-Managed OAuth (Option 2) for direct control and flexibility.*

**Current Implementation: FastAPI-Managed OAuth**
- FastAPI handles OAuth flows directly using `authlib` library
- Direct integration with OAuth providers (Google, GitHub, Facebook, Apple)
- OAuth state management via Redis (CSRF protection)
- User data stored in PostgreSQL database
- JWT tokens generated after successful OAuth authentication

**Alternative: Cognito-Managed OAuth (Not currently used)**
- Configure identity providers in Cognito User Pool
- Cognito handles OAuth redirects and token exchange
- FastAPI validates Cognito tokens

**OAuth Provider Details:**

- **Google OAuth 2.0** ✅ (Configured and tested)
  - Client ID and Secret: Store in Secrets Manager or `.env` for development
  - Scopes: `email`, `profile`, `openid`
  - Callback URL: `https://api.spendsense.example.com/api/v1/auth/oauth/google/callback`
  - Endpoints: 
    - `GET /api/v1/auth/oauth/google/authorize` - Initiate OAuth flow
    - `GET /api/v1/auth/oauth/google/callback` - Handle OAuth callback
  
- **GitHub OAuth 2.0** (Structure ready, credentials needed)
  - Client ID and Secret: Store in Secrets Manager or `.env` for development
  - Scopes: `user:email`
  - Callback URL: `https://api.spendsense.example.com/api/v1/auth/oauth/github/callback`
  - Endpoints:
    - `GET /api/v1/auth/oauth/github/authorize` - Initiate OAuth flow
    - `GET /api/v1/auth/oauth/github/callback` - Handle OAuth callback
  
- **Facebook Login** (Structure ready, credentials needed)
  - App ID and App Secret: Store in Secrets Manager or `.env` for development
  - Permissions: `email`, `public_profile`
  - Callback URL: `https://api.spendsense.example.com/api/v1/auth/oauth/facebook/callback`
  - Endpoints:
    - `GET /api/v1/auth/oauth/facebook/authorize` - Initiate OAuth flow
    - `GET /api/v1/auth/oauth/facebook/callback` - Handle OAuth callback
  
- **Apple Sign In** (Structure ready, credentials needed)
  - Service ID, Key ID, Team ID: Store in Secrets Manager
  - Private Key (P8 file): Store securely in Secrets Manager
  - Client ID: Service ID
  - Callback URL: `https://api.spendsense.example.com/api/v1/auth/oauth/apple/callback`
  - Endpoints:
    - `GET /api/v1/auth/oauth/apple/authorize` - Initiate OAuth flow
    - `GET /api/v1/auth/oauth/apple/callback` - Handle OAuth callback (supports POST for form_post)

**Phone Number Authentication:**
- **SMS Provider**: AWS SNS (Simple Notification Service)
- **SNS Configuration**:
  - Region: us-west-1 (or preferred region)
  - Delivery Status: CloudWatch Logs enabled
  - Default SMS Type: Transactional
  - Monthly Spending Limit: Configured (e.g., $100/month)
  - Cost: ~$0.00645 per SMS (US)
- **Phone Format**: E.164 format (+1234567890)
- **Verification Code**: 6-digit numeric code (random generation)
- **Code Storage**: Redis with key `verify:{phone_number}` (10-minute TTL)
- **Code Expiration**: 10 minutes
- **Max Attempts**: 3 verification attempts per code (tracked in Redis)
- **Rate Limiting**: 
  - Max 5 SMS per phone number per hour
  - Max 10 SMS per phone number per day
  - Tracked in Redis: `ratelimit:sms:{phone_number}`
- **Security**: 
  - CAPTCHA required after 3 failed attempts
  - Block suspicious phone numbers (fraud detection)

### CI/CD Pipeline

**GitHub Actions:**
- **Workflow Runner**: `ubuntu-latest` (GitHub-hosted)
- **Node.js Version**: 20.x
- **Python Version**: 3.11

**Docker Build:**
- **BuildKit**: Enabled
- **Multi-stage Build**: Yes
- **Image Size Optimization**: Alpine-based slim images

### AI/LLM Integration

**OpenAI Configuration:**
- **SDK Version**: 1.12.0
- **API Version**: v1
- **Default Model**: `gpt-4-turbo-preview` (recommendations)
- **Fallback Model**: `gpt-3.5-turbo` (cost optimization)
- **Temperature**: 0.7 (balanced creativity)
- **Max Tokens**: 1000 (rationale generation)
- **Rate Limiting**: Built-in with exponential backoff

---

## Network Architecture

### VPC Configuration

**AWS Region:**
- **Primary Region**: `us-west-1` (selected for resource availability and capacity)
- **Note**: Database and cache engine versions were adjusted for us-west-1 availability:
  - PostgreSQL: 16.10 (was 15.6)
  - Redis: 7.1 (was 7.2.4)

**Shared Account Support:**
- **Owner ID**: Optional identifier (e.g., `chuong`, `jane`) for shared AWS accounts
- **Usage**: Set `owner_id` variable when deploying: `terraform apply -var="owner_id=chuong"`
- **Naming Convention**: Resources include `{owner_id}` when specified:
  - VPC: `spendsense-{owner_id}-{env}-vpc` (e.g., `spendsense-chuong-dev-vpc`)
  - S3 Buckets: `spendsense-{resource}-{env}-{owner_id}` (e.g., `spendsense-data-dev-chuong`)
  - RDS Instance: `spendsense-{env}-db-{owner_id}` (e.g., `spendsense-dev-db-chuong`)
  - RDS Parameter Group: `spendsense-{env}-db-params-{owner_id}` (e.g., `spendsense-dev-db-params-chuong`)
  - RDS Subnet Group: `spendsense-{env}-db-subnet-group-{owner_id}`
  - RDS Security Group: `spendsense-{env}-rds-sg-{owner_id}`
  - Secrets Manager: `spendsense-{env}-db-password-{owner_id}`
  - Redis: `spendsense-{env}-redis` (replication group ID doesn't include owner_id)
- **Purpose**: Prevents naming conflicts when multiple developers deploy to the same AWS account

**CIDR Block**: `10.0.0.0/16`

**Subnets:**
- **Public Subnets** (for ALB, NAT Gateway):
  - `10.0.1.0/24` (Availability Zone A)
  - `10.0.2.0/24` (Availability Zone B)

- **Private Subnets** (for ECS, RDS):
  - `10.0.10.0/24` (Availability Zone A)
  - `10.0.11.0/24` (Availability Zone B)

- **Database Subnets** (for RDS):
  - `10.0.20.0/24` (Availability Zone A)
  - `10.0.21.0/24` (Availability Zone B)

**Internet Gateway**: 1 (for public subnets)
**NAT Gateway**: 2 (one per AZ for high availability)
**VPC Endpoints**: S3, ECR, Secrets Manager (for private subnet access)

### Security Groups

**ALB Security Group:**
- Inbound: HTTP (80) from 0.0.0.0/0, HTTPS (443) from 0.0.0.0/0
- Outbound: All traffic to ECS security group

**ECS Security Group:**
- Inbound: HTTP (8000) from ALB security group only
- Outbound: HTTPS (443) to internet, PostgreSQL (5432) to RDS SG, Redis (6379) to ElastiCache SG

**RDS Security Group:**
- Inbound: PostgreSQL (5432) from ECS security group only
- Outbound: None

**ElastiCache Security Group:**
- Inbound: Redis (6379) from ECS security group only
- Outbound: None

---

## Data Flow Architecture

### Request Flow (Web/Mobile)

```
1. User Request
   ↓
2. CloudFront CDN (for frontend) / API Gateway (for API)
   ↓
3. Application Load Balancer
   ↓
4. ECS Fargate (FastAPI Service)
   ↓
5. Database Query (RDS PostgreSQL)
   ↓
6. Cache Check (ElastiCache Redis)
   ↓
7. Feature Processing (if needed)
   ↓
8. Recommendation Generation (with OpenAI API call)
   ↓
9. Response with Recommendations
```

### Async Processing Flow

```
1. API Request (Generate Recommendations)
   ↓
2. ECS Fargate (FastAPI)
   ↓
3. Send Message to SQS Queue
   ↓
4. AWS Lambda (or ECS Task) Processes Message
   ↓
5. Feature Calculation (if heavy computation)
   ↓
6. OpenAI API Call (content generation)
   ↓
7. Store Results in RDS
   ↓
8. Send Notification (SNS) if needed
   ↓
9. User Polls or Receives Push Notification
```

---

## Authentication Flows

### OAuth 2.0 Flow (Google, GitHub, Facebook)

```
1. User clicks "Sign in with {Provider}"
   ↓
2. Frontend redirects to /auth/oauth/{provider}/authorize
   ↓
3. FastAPI backend redirects to provider's authorization URL
   ↓
4. User authenticates with provider
   ↓
5. Provider redirects to callback URL with authorization code
   ↓
6. FastAPI receives code at /auth/oauth/{provider}/callback
   ↓
7. FastAPI exchanges code for access token with provider
   ↓
8. FastAPI retrieves user info from provider
   ↓
9. FastAPI creates/updates user in Cognito or database
   ↓
10. FastAPI generates JWT tokens and returns to frontend
    ↓
11. Frontend stores tokens and redirects to dashboard
```

### Apple Sign In Flow

```
1. User clicks "Sign in with Apple"
   ↓
2. Frontend initiates Apple Sign In (native SDK or web)
   ↓
3. User authenticates with Apple
   ↓
4. Apple returns identity token (JWT)
   ↓
5. Frontend sends identity token to /auth/oauth/apple/token
   ↓
6. FastAPI validates Apple identity token
   ↓
7. FastAPI creates/updates user in Cognito or database
   ↓
8. FastAPI generates app JWT tokens and returns to frontend
```

### Phone Number Authentication Flow

```
1. User enters phone number
   ↓
2. Frontend calls POST /auth/phone/request with phone number
   ↓
3. FastAPI validates phone format (E.164)
   ↓
4. FastAPI generates 6-digit verification code
   ↓
5. FastAPI sends SMS via AWS SNS
   ↓
6. FastAPI stores code in Redis (10-minute expiration)
   ↓
7. User enters verification code
   ↓
8. Frontend calls POST /auth/phone/verify with code
   ↓
9. FastAPI validates code against Redis
   ↓
10. FastAPI creates/updates user in Cognito or database
    ↓
11. FastAPI generates JWT tokens and returns to frontend
```

### Account Linking ✅

**Multiple Authentication Methods:**
- Users can link multiple authentication methods to one account
- Example: User signs up with Google, later adds phone number
- Database schema supports multiple identity providers per user

**Account Linking Endpoints:**
- `POST /api/v1/auth/oauth/link` - Link additional OAuth provider (requires authentication)
- `POST /api/v1/auth/phone/link` - Link phone number (requires authentication)
- `DELETE /api/v1/auth/oauth/unlink/{provider}` - Unlink OAuth provider
- `DELETE /api/v1/auth/phone/unlink` - Unlink phone number

**Account Merging:**
- Automatically merges accounts if duplicate found during linking
- Merges user data from duplicate accounts:
  - DataUpload records
  - Recommendation records
  - PersonaHistory records
  - UserProfile records
- Preserves primary authentication method
- Ensures at least one authentication method remains after unlinking
- CSRF protection via OAuth state verification

**Linking Flow:**
1. Authenticated user initiates OAuth flow or phone verification
2. System checks for duplicate accounts (by email or provider ID)
3. If duplicate found, merges accounts automatically
4. Links new authentication method to current user account
5. Returns merge status to user

---

## API Architecture

### REST API Structure

**Base URL**: `https://api.spendsense.example.com/v1`

**Authentication:**
- **Method**: Bearer Token (JWT)
- **Header**: `Authorization: Bearer <token>`
- **Token Source**: AWS Cognito (supports OAuth, phone, email)

**Endpoints:**

```
# Traditional Authentication
POST   /auth/login          - User login (email/username + password)
POST   /auth/register       - User registration (email/username + password)
POST   /auth/refresh        - Refresh token
POST   /auth/logout         - User logout

# Phone Number Authentication
POST   /auth/phone/request  - Request SMS verification code
POST   /auth/phone/verify   - Verify SMS code and login/register
POST   /auth/phone/resend   - Resend verification code

# OAuth Authentication
GET    /auth/oauth/{provider}/authorize - Initiate OAuth flow
                               (provider: google, github, facebook, apple)
GET    /auth/oauth/{provider}/callback  - OAuth callback handler
POST   /auth/oauth/{provider}/token     - Exchange OAuth code for tokens
POST   /auth/oauth/link                 - Link additional OAuth provider to account
DELETE /auth/oauth/unlink/{provider}    - Unlink OAuth provider from account

# Account Management
POST   /users               - Create user (internal, usually via auth flows)
GET    /users/{user_id}     - Get user
PUT    /users/{user_id}     - Update user

POST   /consent             - Record consent
GET    /consent/{user_id}   - Get consent status
DELETE /consent/{user_id}   - Revoke consent

GET    /profile/{user_id}           - Get behavioral profile
GET    /profile/{user_id}/signals    - Get detected signals
GET    /profile/{user_id}/persona   - Get assigned persona

GET    /recommendations/{user_id}      - Get recommendations
POST   /recommendations/{user_id}/feedback - Submit feedback

GET    /operator/review                - Get review queue
POST   /operator/approve               - Approve recommendation
POST   /operator/override              - Override recommendation

GET    /health              - Health check
GET    /metrics             - System metrics
```

### API Versioning

- **Current Version**: v1
- **Versioning Strategy**: URL path (`/v1/`, `/v2/`)
- **Backward Compatibility**: Maintain for 6 months after new version

---

## Mobile API Compatibility

### Design Principles

1. **RESTful Design**: Standard REST for easy Swift integration
2. **JSON Responses**: Lightweight, minimal nesting
3. **Pagination**: All list endpoints support pagination
4. **Caching**: ETags and Cache-Control headers
5. **Offline Support**: Cache-friendly responses

### Mobile-Optimized Endpoints

```
GET /mobile/recommendations/{user_id}?format=mobile
GET /mobile/profile/{user_id}?format=mobile
POST /mobile/consent/{user_id}
```

### Push Notifications

- **Service**: Amazon SNS
- **Platform**: APNs (Apple Push Notification service)
- **Endpoint**: `/mobile/push/register` (register device token)

---

## CI/CD Pipeline Architecture

### GitHub Actions Workflows

**1. CI Pipeline** (`.github/workflows/ci.yml`):
```yaml
Triggers:
  - Push to main
  - Pull requests
  - Manual trigger

Steps:
  1. Checkout code
  2. Setup Python 3.11
  3. Install dependencies
  4. Run linting (black, pylint, mypy)
  5. Run tests (pytest)
  6. Generate coverage report
  7. Upload artifacts
```

**2. Build & Push** (`.github/workflows/build.yml`):
```yaml
Triggers:
  - Push to main (after CI passes)
  
Steps:
  1. Configure AWS credentials
  2. Login to ECR
  3. Build Docker image
  4. Tag with git SHA
  5. Push to ECR
```

**3. Deploy** (`.github/workflows/deploy.yml`):
```yaml
Triggers:
  - Push to main (after build)
  
Steps:
  1. Update ECS task definition
  2. Deploy to staging environment
  3. Run smoke tests
  4. Deploy to production (manual approval)
  5. Verify deployment health
```

**4. API Testing** (`.github/workflows/api-tests.yml`):
```yaml
Triggers:
  - Scheduled (daily)
  - Manual trigger
  
Steps:
  1. Deploy to test environment
  2. Run API contract tests
  3. Run integration tests
  4. Run E2E tests
  5. Generate test report
  6. Cleanup test environment
```

### Testing Strategy

**Unit Tests**:
- Framework: pytest 7.4.4
- Coverage Target: ≥80%
- Mocking: unittest.mock, pytest-mock

**Integration Tests**:
- Framework: pytest with test database
- Database: PostgreSQL test container
- External Services: Mocked (OpenAI API, AWS services)

**API Contract Tests**:
- Framework: pytest with OpenAPI validation
- Tool: openapi-core or fastapi.testclient

**E2E Tests**:
- Framework: pytest with httpx
- Environment: Test environment (RDS, S3, Redis test instances)

---

## Security Architecture

### Authentication & Authorization

- **Authentication**: FastAPI-managed authentication with JWT tokens (Email, Phone/SMS, OAuth 2.0)
  - Email/Username + Password
  - Phone number + SMS verification
  - OAuth 2.0 (Google, GitHub, Facebook)
  - Apple Sign In
- **Authorization**: Role-based (RBAC) ✅
  - **Roles**: `user`, `operator`, `admin` (hierarchy: USER < OPERATOR < ADMIN)
  - **Endpoint-Level Authorization**: FastAPI dependencies check role before route handler
  - **Resource-Level Authorization**: Users can access own resources, operators can access all user resources (with consent), admins can access all resources (with consent)
  - **Consent Enforcement**: Operators and admins must respect user consent when accessing other users' data. If consent is revoked or not granted, access is denied.
  - **Authorization Dependencies**: `require_role()`, `require_operator`, `require_admin`
  - **Resource-Level Helpers**: `check_resource_access()`, `check_user_access()`, factory functions for owner/operator/admin access
  - **Consent Checks**: `check_resource_access()` and `check_user_access()` verify target user's `consent_status` before allowing operator/admin access
  - **Authorization Logging**: All authorization failures are logged with user ID, role, and resource details, including consent violations
- **Token Expiration**: 1 hour (access), 30 days (refresh)
- **Token Storage**: HTTP-only cookies (web) or secure storage (mobile)
- **Social Provider Linking**: Users can link multiple providers to one account

### Data Encryption

- **In Transit**: TLS 1.3
- **At Rest**: 
  - RDS: AES-256 encryption
  - S3: SSE-S3 (AES-256)
  - ElastiCache: Encryption at rest enabled

### Secrets Management

- **Service**: AWS Secrets Manager
- **Secrets**:
  - Database credentials
  - OpenAI API key
  - JWT signing keys
  - AWS access keys
  - OAuth Client IDs and Secrets:
    - Google OAuth credentials
    - GitHub OAuth credentials
    - Facebook App ID and Secret
    - Apple Sign In credentials (Service ID, Key ID, Team ID, Private Key)
  - SMS Provider credentials (AWS SNS API keys)

### Network Security

- **VPC**: Private subnets for compute
- **Security Groups**: Least-privilege access
- **WAF**: Optional (API Gateway protection)
- **DDoS Protection**: AWS Shield Standard

### Compliance

- **Audit Logging**: CloudWatch Logs (retention: 1 year)
- **Decision Traces**: Stored in RDS, backed up to S3
- **Data Privacy**: User consent tracking, data deletion support

---

## Monitoring & Observability

### CloudWatch Metrics

**Application Metrics:**
- API request count, latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Recommendation generation time
- OpenAI API call latency

**Infrastructure Metrics:**
- ECS task CPU/memory utilization
- RDS connection count, query latency
- ElastiCache hit rate
- S3 request metrics

### CloudWatch Logs

**Log Groups:**
- `/ecs/spendsense-api` - Application logs
- `/aws/rds/postgresql` - Database logs
- `/aws/lambda/spendsense-processor` - Lambda logs

**Log Format**: JSON structured logging

### Alarms

- **High Error Rate**: >5% errors triggers alarm
- **High Latency**: p95 >500ms triggers alarm
- **Database Connections**: >80% capacity triggers alarm
- **Container OOM**: Memory >90% triggers alarm

### Dashboards

- **Operational Dashboard**: System health, metrics
- **Business Dashboard**: User metrics, recommendation performance
- **Security Dashboard**: Authentication failures, suspicious activity

---

## Disaster Recovery & Backup

### Backup Strategy

**Database:**
- **Automated Backups**: Daily, 30-day retention
- **Manual Snapshots**: Before major changes
- **Cross-Region Replication**: Optional for production

**Application State:**
- **ECS Task Definitions**: Versioned in ECR
- **Infrastructure**: Terraform state in S3
- **Configuration**: Secrets in Secrets Manager (automatically backed up)

### Recovery Objectives

- **RTO (Recovery Time Objective)**: <1 hour
- **RPO (Recovery Point Objective)**: <15 minutes
- **Strategy**: Multi-AZ deployment, automated failover

---

## Cost Optimization

### Resource Sizing

**Development:**
- ECS: 0.5 vCPU, 1GB RAM
- RDS: db.t3.micro
- ElastiCache: cache.t3.micro
- Estimated: ~$50/month

**Production:**
- ECS: 1-2 vCPU, 2-4GB RAM (auto-scaling)
- RDS: db.t3.large (with read replicas)
- ElastiCache: cache.t3.small
- Estimated: ~$200-500/month (depending on scale)

### Cost-Saving Strategies

- **Reserved Instances**: For RDS (1-year commitment)
- **Spot Instances**: For non-critical batch processing
- **S3 Lifecycle Policies**: Move old data to Glacier
- **OpenAI Model Selection**: Use GPT-3.5 for non-critical content
- **CloudFront Caching**: Reduce API calls
- **ElastiCache**: Reduce database load

---

## Scaling Strategy

### Horizontal Scaling

- **ECS Auto Scaling**: Based on CPU/memory metrics
- **RDS Read Replicas**: For read-heavy workloads
- **ElastiCache Cluster**: Multi-node for high availability
- **S3**: Automatically scales (no action needed)

### Vertical Scaling

- **ECS**: Increase CPU/memory in task definition
- **RDS**: Upgrade instance class (with minimal downtime)
- **ElastiCache**: Upgrade node type

### Performance Targets

- **API Response Time**: <200ms (p95)
- **Recommendation Generation**: <5 seconds per user
- **Database Query Time**: <100ms (p95)
- **Concurrent Users**: Support 1000+ concurrent users

---

## Deployment Environments

### Development

- **Purpose**: Local development and testing
- **Infrastructure**: Single AZ, minimal resources
- **Database**: db.t3.micro
- **Auto Scaling**: Disabled

### Staging

- **Purpose**: Pre-production testing
- **Infrastructure**: Production-like setup
- **Database**: db.t3.small
- **Auto Scaling**: Enabled (min: 1, max: 3)

### Production

- **Purpose**: Live user traffic
- **Infrastructure**: Multi-AZ, high availability
- **Database**: db.t3.large (Multi-AZ)
- **Auto Scaling**: Enabled (min: 2, max: 10)
- **Backup**: Automated daily backups

---

## Technology Update Strategy

### Version Pinning Strategy

- **Major Versions**: Pin to specific version (e.g., `fastapi==0.109.0`)
- **Minor/Patch Versions**: Allow updates with `~=` (e.g., `pydantic~=2.5.0`)
- **Security Updates**: Update immediately when available

### Dependency Management

- **Python**: Use `requirements.txt` with pinned versions
- **Node.js**: Use `package-lock.json` (auto-generated)
- **Docker**: Pin base image tags (avoid `latest`)

### Update Process

1. Test updates in development environment
2. Run full test suite
3. Deploy to staging
4. Run integration tests
5. Deploy to production with rollback plan

---

## Documentation Requirements

### API Documentation

- **Format**: OpenAPI 3.0 (auto-generated by FastAPI)
- **Location**: `/docs` (Swagger UI), `/redoc` (ReDoc)
- **Examples**: Included in schema examples

### Code Documentation

- **Python**: Docstrings (Google style)
- **TypeScript**: JSDoc comments
- **API Routes**: OpenAPI annotations

### Architecture Documentation

- **This Document**: Architecture overview
- **Decision Log**: Document key architectural decisions
- **Runbooks**: Operator procedures

---

## Future Considerations

### Phase 8: Swift Mobile App

**Technology Stack:**
- Swift 5.9+
- SwiftUI 5.0+
- iOS 17.0+ (minimum)
- Alamofire (HTTP client) or URLSession
- SwiftData or Core Data (local storage)

**Architecture:**
- MVVM pattern
- Combine framework (reactive programming)
- SwiftUI for UI
- Networking layer consuming FastAPI REST endpoints

### Potential Enhancements

- **GraphQL API**: For flexible data fetching (mobile optimization)
- **WebSocket Support**: Real-time updates
- **Multi-Region Deployment**: For global users
- **CDN for API**: CloudFront for API responses (edge caching)
- **Machine Learning**: Custom models for persona prediction

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial architecture document |
| 1.1.0 | 2024-01-15 | Added OAuth authentication (Google, GitHub, Facebook, Apple), phone number authentication, account linking capabilities |

---

## Appendix: Dependency Versions Summary

### Python Backend
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.3.0
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
redis==5.0.1
boto3==1.34.34
aioboto3==12.3.0
openai==1.12.0
pandas==2.1.4
numpy==1.26.3
pyarrow==15.0.0
authlib==1.3.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
phonenumbers==8.13.27
python-multipart==0.0.6
pytest==7.4.4
pytest-asyncio==0.23.3
```

### Node.js Frontend
```
react==18.2.0
typescript==5.3.3
vite==5.0.11
react-router-dom==6.21.1
@tanstack/react-query==5.17.0
axios==1.6.5
```

### AWS Services
```
RDS PostgreSQL: 16.10 (adjusted for us-west-1 availability)
ElastiCache Redis: 7.1 (adjusted for us-west-1 availability)
ECS Platform: LATEST
API Gateway: HTTP API v2
Cognito: Managed service (latest)
SNS (SMS): Managed service (latest)
```

### Development Tools
```
Docker: 24.0.7+
Terraform: 1.6.6
AWS CLI: 2.15.25+
Node.js: 20.10.0 (LTS)
Python: 3.11.7
```

---

**End of Architecture Documentation**

