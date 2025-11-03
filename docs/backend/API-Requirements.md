# API Requirements
## SpendSense Platform - Backend Layer

**Version**: 1.0  
**Date**: 2024-01-15  
**Status**: Planning  

---

## Executive Summary

This document defines the REST API requirements for the SpendSense backend, including all API endpoints, request/response formats, authentication, and versioning.

---

## API Architecture

### Technology Stack

**Framework**:
- **FastAPI**: `0.109.0` (Python web framework)
- **Python**: `3.11.7` (programming language)
- **Uvicorn**: `0.27.0` (ASGI server)
- **Pydantic**: `2.5.0` (data validation)

### API Design Principles

- RESTful API design with OpenAPI 3.0 documentation
- API versioning (`/api/v1/`)
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response format
- Error handling with standard error responses
- Rate limiting (per user/IP)
- Request validation with Pydantic
- Response caching (Redis)

---

## API Endpoints

### Authentication Endpoints

**BE-US-001: User Registration API**
- **As a** system
- **I want to** provide registration endpoints
- **So that** users can create accounts

**Endpoints**:
- `POST /api/v1/auth/register` - Email/username + password registration
- `POST /api/v1/auth/phone/request` - Request SMS verification code
- `POST /api/v1/auth/phone/verify` - Verify SMS code and register/login
- `GET /api/v1/auth/oauth/{provider}/authorize` - Initiate OAuth flow
- `GET /api/v1/auth/oauth/{provider}/callback` - OAuth callback handler

**Acceptance Criteria**:
- [ ] Validate email format, password strength, phone E.164 format
- [ ] Store user credentials securely (hashed passwords)
- [ ] Generate JWT tokens on successful registration
- [ ] Create user record in PostgreSQL
- [ ] Log registration events

**BE-US-002: User Login API**
- **As a** system
- **I want to** provide login endpoints
- **So that** users can authenticate

**Endpoints**:
- `POST /api/v1/auth/login` - Email/username + password login
- `POST /api/v1/auth/phone/verify` - Phone + SMS code login
- `GET /api/v1/auth/oauth/{provider}/authorize` - OAuth login initiation

**Acceptance Criteria**:
- [ ] Validate credentials
- [ ] Generate JWT access token (1 hour) and refresh token (30 days)
- [ ] Store refresh token in database
- [ ] Log login events (success and failure)

**BE-US-003: Token Management API**
- **As a** system
- **I want to** provide token refresh and revocation
- **So that** users can maintain sessions securely

**Endpoints**:
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Revoke tokens

**Acceptance Criteria**:
- [ ] Validate refresh token
- [ ] Generate new access token
- [ ] Revoke old tokens on logout
- [ ] Support token blacklisting in Redis

**BE-US-004: Account Linking API**
- **As a** system
- **I want to** provide account linking endpoints
- **So that** users can link multiple authentication methods

**Endpoints**:
- `POST /api/v1/auth/oauth/link` - Link additional OAuth provider
- `POST /api/v1/auth/phone/link` - Link phone number
- `DELETE /api/v1/auth/oauth/unlink/{provider}` - Unlink OAuth provider
- `DELETE /api/v1/auth/phone/unlink` - Unlink phone number

**Acceptance Criteria**:
- [ ] Prevent duplicate account creation
- [ ] Merge accounts if needed
- [ ] Require authentication for linking
- [ ] Log account linking events

---

### User Management Endpoints

**BE-US-005: User Profile API**
- **As a** system
- **I want to** provide user profile endpoints
- **So that** users can manage their profiles

**Endpoints**:
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `DELETE /api/v1/users/me` - Delete user account

**Acceptance Criteria**:
- [ ] Require authentication
- [ ] Validate input data
- [ ] Log profile updates

**BE-US-006: Consent Management API**
- **As a** system
- **I want to** provide consent management endpoints
- **So that** users can control data processing

**Endpoints**:
- `POST /api/v1/consent` - Grant consent
- `DELETE /api/v1/consent` - Revoke consent
- `GET /api/v1/consent` - Get consent status

**Acceptance Criteria**:
- [ ] Store consent with timestamp and version
- [ ] Block recommendations if consent not granted
- [ ] Support data deletion on consent revocation
- [ ] Log consent events

---

### Data Management Endpoints

**BE-US-007: Transaction Data Upload API**
- **As a** system
- **I want to** provide data upload endpoints
- **So that** users can upload transaction data

**Endpoints**:
- `POST /api/v1/data/upload` - Upload transaction data file
- `GET /api/v1/data/upload/{upload_id}` - Get upload status

**Acceptance Criteria**:
- [ ] Support JSON and CSV file formats
- [ ] Validate file format and size (max 10MB)
- [ ] Validate Plaid data schema
- [ ] Store file in S3
- [ ] Store metadata in PostgreSQL
- [ ] Trigger data processing pipeline (async)
- [ ] Return upload status and file ID
- [ ] Log upload events

**BE-US-008: Data Validation API**
- **As a** system
- **I want to** validate uploaded data
- **So that** only valid data is processed

**Acceptance Criteria**:
- [ ] Validate account structure (account_id, type, subtype, balances)
- [ ] Validate transaction structure (account_id, date, amount, merchant, category)
- [ ] Validate liability structure (APRs, payment amounts, overdue status)
- [ ] Return validation errors with clear messages
- [ ] Store validation results
- [ ] Log validation errors

---

### Profile & Recommendations Endpoints

**BE-US-009: User Profile API**
- **As a** system
- **I want to** provide behavioral profile endpoints
- **So that** users can view their financial insights

**Endpoints**:
- `GET /api/v1/users/{user_id}/profile` - Get user behavioral profile
- `GET /api/v1/users/{user_id}/signals` - Get detected behavioral signals
- `GET /api/v1/users/{user_id}/persona` - Get assigned persona

**Acceptance Criteria**:
- [ ] Require authentication and authorization (own profile or operator)
- [ ] Return detected signals (subscriptions, savings, credit, income)
- [ ] Return 30-day and 180-day analysis
- [ ] Return persona history
- [ ] Cache responses in Redis

**BE-US-010: Recommendations API**
- **As a** system
- **I want to** provide recommendations endpoints
- **So that** users can view personalized recommendations

**Endpoints**:
- `GET /api/v1/users/{user_id}/recommendations` - Get user recommendations
- `GET /api/v1/recommendations/{recommendation_id}` - Get recommendation detail
- `POST /api/v1/recommendations/{recommendation_id}/feedback` - Submit feedback

**Acceptance Criteria**:
- [ ] Require authentication and consent
- [ ] Return 3-5 education items and 1-3 partner offers
- [ ] Include plain-language rationales
- [ ] Include regulatory disclaimers
- [ ] Cache recommendations in Redis

---

### Operator Endpoints

**BE-US-011: Operator Review API**
- **As a** system
- **I want to** provide operator review endpoints
- **So that** operators can review recommendations

**Endpoints**:
- `GET /api/v1/operator/review` - Get review queue
- `GET /api/v1/operator/review/{recommendation_id}` - Get recommendation for review
- `POST /api/v1/operator/review/{recommendation_id}/approve` - Approve recommendation
- `POST /api/v1/operator/review/{recommendation_id}/reject` - Reject recommendation
- `PUT /api/v1/operator/review/{recommendation_id}` - Modify recommendation
- `POST /api/v1/operator/review/bulk` - Bulk approve/reject

**Acceptance Criteria**:
- [ ] Require operator role authentication
- [ ] Filter and sort functionality
- [ ] Return decision traces
- [ ] Log all operator actions

**BE-US-012: Operator Analytics API**
- **As a** system
- **I want to** provide analytics endpoints
- **So that** operators can monitor system health

**Endpoints**:
- `GET /api/v1/operator/analytics` - Get system metrics
- `GET /api/v1/operator/analytics/coverage` - Get coverage metrics
- `GET /api/v1/operator/analytics/performance` - Get performance metrics

**Acceptance Criteria**:
- [ ] Require operator role authentication
- [ ] Return coverage, explainability, performance, engagement metrics
- [ ] Support date range filtering
- [ ] Return aggregated data (JSON)

---

### Health Check Endpoints

**Health**:
- `GET /health` - Health check
- `GET /ready` - Readiness check

---

## Functional Requirements

### FR-BE-001: REST API
**Priority**: Must Have

- RESTful API design with OpenAPI 3.0 documentation
- API versioning (`/api/v1/`)
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response format
- Error handling with standard error responses
- Rate limiting (per user/IP)
- Request validation with Pydantic
- Response caching (Redis)

---

## Technical Requirements

### TR-BE-001: FastAPI Application Structure

**Framework**: FastAPI 0.109.0  
**Language**: Python 3.11.7

**Project Structure**:
```
app/
  api/
    v1/
      endpoints/    # API route handlers
      schemas/      # Pydantic models
  core/
    config.py      # Configuration
    security.py    # Authentication/authorization
    database.py    # Database connection
  models/          # SQLAlchemy models
  services/        # Business logic
  utils/           # Utility functions
tests/             # Test suite
```

### TR-BE-002: API Endpoints Summary

**Authentication**:
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/phone/request` - Request SMS code
- `POST /api/v1/auth/phone/verify` - Verify SMS code
- `GET /api/v1/auth/oauth/{provider}/authorize` - OAuth initiation
- `GET /api/v1/auth/oauth/{provider}/callback` - OAuth callback
- `POST /api/v1/auth/oauth/link` - Link OAuth provider
- `DELETE /api/v1/auth/oauth/unlink/{provider}` - Unlink provider

**User Management**:
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update user
- `DELETE /api/v1/users/me` - Delete user
- `GET /api/v1/users/{user_id}/profile` - Get user profile
- `GET /api/v1/users/{user_id}/signals` - Get behavioral signals
- `GET /api/v1/users/{user_id}/persona` - Get assigned persona

**Consent**:
- `POST /api/v1/consent` - Grant consent
- `DELETE /api/v1/consent` - Revoke consent
- `GET /api/v1/consent` - Get consent status

**Data Upload**:
- `POST /api/v1/data/upload` - Upload transaction data
- `GET /api/v1/data/upload/{upload_id}` - Get upload status

**Recommendations**:
- `GET /api/v1/users/{user_id}/recommendations` - Get recommendations
- `GET /api/v1/recommendations/{recommendation_id}` - Get recommendation detail
- `POST /api/v1/recommendations/{recommendation_id}/feedback` - Submit feedback

**Operator**:
- `GET /api/v1/operator/review` - Get review queue
- `GET /api/v1/operator/review/{recommendation_id}` - Get recommendation for review
- `POST /api/v1/operator/review/{recommendation_id}/approve` - Approve
- `POST /api/v1/operator/review/{recommendation_id}/reject` - Reject
- `PUT /api/v1/operator/review/{recommendation_id}` - Modify
- `POST /api/v1/operator/review/bulk` - Bulk operations
- `GET /api/v1/operator/analytics` - Get analytics

**Health**:
- `GET /health` - Health check
- `GET /ready` - Readiness check

---

## API Request/Response Formats

### Request Format

**Headers**:
- `Content-Type: application/json`
- `Authorization: Bearer <token>` (for authenticated endpoints)

**Body**: JSON format

**Example**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### Response Format

**Success Response**:
- Status Code: `200 OK`, `201 Created`, `204 No Content`
- Body: JSON format

**Error Response**:
- Status Code: `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `500 Internal Server Error`
- Body: JSON format with error details

**Example Error**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "reason": "must be a valid email address"
    }
  }
}
```

---

## API Versioning

### Current Version
- **Version**: `v1`
- **Base Path**: `/api/v1/`

### Versioning Strategy
- URL-based versioning (`/api/v1/`, `/api/v2/`)
- Maintain backward compatibility for at least 1 major version
- Deprecation notice: 6 months before removal

---

## Rate Limiting

### Limits
- **Per User/IP**: 1000 requests/hour
- **Per Endpoint**: Varies by endpoint
- **Authentication**: 5 attempts/hour per IP

### Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

---

## Response Caching

### Cache Strategy
- Cache user profiles (TTL: 5 minutes)
- Cache recommendations (TTL: 1 hour)
- Cache behavioral signals (TTL: 24 hours)
- Invalidate cache on data updates

### Cache Headers
```
Cache-Control: public, max-age=3600
ETag: "abc123"
```

---

## OpenAPI Documentation

### Documentation Requirements
- Automatic OpenAPI/Swagger documentation
- Available at `/docs` (Swagger UI)
- Available at `/redoc` (ReDoc)
- Available at `/openapi.json` (OpenAPI JSON)

### Documentation Sections
- API overview and authentication
- All endpoints with request/response schemas
- Error responses and status codes
- Code examples (curl, Python, JavaScript)

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial API Requirements | TBD |

---

**Document Status**: Draft  
**Next Review Date**: TBD  
**Approval Required From**: Product Owner, Backend Lead, API Team


