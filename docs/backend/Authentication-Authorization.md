# Authentication & Authorization Requirements
## SpendSense Platform - Backend Layer

**Version**: 1.0  
**Date**: 2024-01-15  
**Status**: Planning  

---

## Executive Summary

This document defines the authentication and authorization requirements for the SpendSense backend, including multi-method authentication (email, phone, OAuth), JWT token management, role-based access control, and account linking.

---

## Authentication Methods

### Email/Username + Password

**Flow**:
1. User submits email + password
2. Validate credentials
3. Generate JWT access token (1 hour) + refresh token (30 days)
4. Store refresh token in database
5. Return tokens to client

**Endpoints**:
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login

**Requirements**:
- Password hashing with bcrypt (cost factor 12)
- Password strength validation (min 12 characters, uppercase, lowercase, numbers, symbols)
- Email format validation
- Rate limiting on login attempts (5 per hour per IP)
- Log login events (success and failure)

---

### Phone Number + SMS

**Flow**:
1. User submits phone number
2. Generate 6-digit code
3. Send SMS via AWS SNS
4. Store code in Redis (10-minute TTL)
5. User submits code
6. Validate code
7. Generate JWT tokens
8. Return tokens to client

**Endpoints**:
- `POST /api/v1/auth/phone/request` - Request SMS verification code
- `POST /api/v1/auth/phone/verify` - Verify SMS code and register/login

**Requirements**:
- Phone format validation (E.164 format: +1234567890)
- 6-digit numeric code generation (random)
- Code storage in Redis (10-minute TTL)
- Code expiration: 10 minutes
- Max attempts: 3 verification attempts per code
- Rate limiting: 5 SMS per phone per hour, 10 per day
- SMS provider: AWS SNS
- CAPTCHA required after 3 failed attempts
- Block suspicious phone numbers (fraud detection)

---

### OAuth 2.0 (Google, GitHub, Facebook, Apple)

**Flow**:
1. User clicks OAuth provider button
2. Redirect to provider authorization URL
3. User authenticates with provider
4. Provider redirects to callback URL with code
5. Exchange code for access token
6. Retrieve user info from provider
7. Create/update user in database
8. Generate JWT tokens
9. Return tokens to client

**Endpoints**:
- `GET /api/v1/auth/oauth/{provider}/authorize` - Initiate OAuth flow
- `GET /api/v1/auth/oauth/{provider}/callback` - OAuth callback handler

**Supported Providers**:
- Google OAuth 2.0
- GitHub OAuth 2.0
- Facebook Login
- Apple Sign In

**Provider Details**:

**Google OAuth 2.0**:
- Scopes: `email`, `profile`, `openid`
- Callback URL: `https://api.spendsense.example.com/auth/oauth/google/callback`
- Client ID and Secret: Store in Secrets Manager

**GitHub OAuth 2.0**:
- Scopes: `user:email`
- Callback URL: `https://api.spendsense.example.com/auth/oauth/github/callback`
- Client ID and Secret: Store in Secrets Manager

**Facebook Login**:
- Permissions: `email`, `public_profile`
- Callback URL: `https://api.spendsense.example.com/auth/oauth/facebook/callback`
- App ID and App Secret: Store in Secrets Manager

**Apple Sign In**:
- Client ID: Service ID
- Callback URL: `https://api.spendsense.example.com/auth/oauth/apple/callback`
- Service ID, Key ID, Team ID: Store in Secrets Manager
- Private Key (P8 file): Store securely in Secrets Manager

---

## Token Management

### JWT Tokens

**Access Token**:
- Type: JWT
- Algorithm: RS256
- Expiration: 1 hour
- Claims: `user_id`, `email`, `role`, `iat`, `exp`

**Refresh Token**:
- Type: JWT
- Algorithm: RS256
- Expiration: 30 days
- Storage: Database (Sessions table)
- Claims: `user_id`, `token_id`, `iat`, `exp`

**Token Blacklisting**:
- Store revoked tokens in Redis (TTL: token expiration time)
- Check blacklist on token validation
- Redis key: `blacklist:token:{token_id}`

**Endpoints**:
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Revoke tokens

---

## Account Linking

### Link Additional Authentication Methods

**Flow**:
1. User authenticates with primary method
2. User requests to link additional method
3. Complete authentication flow for additional method
4. Link additional method to existing account
5. Store linked providers in database

**Endpoints**:
- `POST /api/v1/auth/oauth/link` - Link additional OAuth provider
- `POST /api/v1/auth/phone/link` - Link phone number
- `DELETE /api/v1/auth/oauth/unlink/{provider}` - Unlink OAuth provider
- `DELETE /api/v1/auth/phone/unlink` - Unlink phone number

**Requirements**:
- Require authentication for linking
- Prevent duplicate account creation
- Merge accounts if needed (handle existing accounts)
- Log account linking events
- Support multiple OAuth providers per user
- Support phone number linking

**Account Merging Strategy**:
- If OAuth provider email matches existing account, link to existing account
- If phone number matches existing account, link to existing account
- Merge user data (recommendations, profiles, signals)
- Preserve primary authentication method

---

## Authorization

### Role-Based Access Control (RBAC)

**Roles**:
- **User**: Default role for end users
  - Can access own profile, recommendations, data
  - Can upload transaction data
  - Can manage consent
  - Cannot access operator endpoints

- **Operator**: Role for platform operators
  - Can access all user data
  - Can review recommendations
  - Can approve/reject recommendations
  - Can view analytics
  - Cannot access admin endpoints

- **Admin**: Role for administrators
  - Can access all endpoints
  - Can manage users
  - Can manage system configuration
  - Can access audit logs

**Authorization Checks**:
- Endpoint-level authorization (check role in route handler)
- Resource-level authorization (users can only access their own data)
- Operator can access all user data
- Admin can access all endpoints

**Implementation**:
- JWT token includes `role` claim
- Middleware checks role before route handler
- Resource-level checks in service layer
- Log authorization failures

---

## Security Requirements

### SR-BE-001: Authentication Security

- **Password Hashing**: bcrypt with cost factor 12
- **JWT Token Signing**: RS256 algorithm
- **Token Expiration**: 1 hour (access), 30 days (refresh)
- **Token Blacklisting**: Redis for revoked tokens
- **Rate Limiting**: 5 login attempts per hour per IP
- **SMS Rate Limiting**: 5 SMS per phone per hour, 10 per day
- **CAPTCHA**: Required after 3 failed attempts
- **Fraud Detection**: Block suspicious phone numbers
- **OAuth State**: Validate state parameter to prevent CSRF
- **Secrets Management**: OAuth credentials in AWS Secrets Manager

### SR-BE-002: Authorization

- **Role-Based Access Control**: `user`, `operator`, `admin` roles
- **Endpoint-Level Checks**: Verify role in route handler
- **Resource-Level Checks**: Verify ownership in service layer
- **Operator Access**: Can access all user data
- **Admin Access**: Can access all endpoints
- **Authorization Logging**: Log authorization failures

---

## User Stories

### Authentication & Authorization

**BE-US-001: User Registration API**
- [See API-Requirements.md](./API-Requirements.md#be-us-001-user-registration-api)

**BE-US-002: User Login API**
- [See API-Requirements.md](./API-Requirements.md#be-us-002-user-login-api)

**BE-US-003: Token Management API**
- [See API-Requirements.md](./API-Requirements.md#be-us-003-token-management-api)

**BE-US-004: Account Linking API**
- [See API-Requirements.md](./API-Requirements.md#be-us-004-account-linking-api)

---

## Functional Requirements

### FR-BE-002: Authentication & Authorization
**Priority**: Must Have

- Multi-method authentication (email, phone, OAuth)
- JWT token generation and validation
- Token refresh mechanism
- Role-based access control (RBAC)
- Account linking support
- Session management (Redis)
- Password hashing (bcrypt)
- OAuth 2.0 integration (Google, GitHub, Facebook, Apple)

---

## Technical Requirements

### TR-BE-004: Authentication Flow

**Email/Password**:
1. User submits email + password
2. Validate credentials
3. Generate JWT access token (1 hour) + refresh token (30 days)
4. Store refresh token in database
5. Return tokens to client

**Phone/SMS**:
1. User submits phone number
2. Generate 6-digit code
3. Send SMS via AWS SNS
4. Store code in Redis (10-minute TTL)
5. User submits code
6. Validate code
7. Generate JWT tokens
8. Return tokens to client

**OAuth 2.0**:
1. User clicks OAuth provider button
2. Redirect to provider authorization URL
3. User authenticates with provider
4. Provider redirects to callback URL with code
5. Exchange code for access token
6. Retrieve user info from provider
7. Create/update user in database
8. Generate JWT tokens
9. Return tokens to client

### Authentication Implementation

**Libraries**:
- `authlib==1.3.0` - OAuth 2.0 client library
- `python-jose[cryptography]==3.3.0` - JWT token handling
- `passlib[bcrypt]==1.7.4` - Password hashing
- `phonenumbers==8.13.27` - Phone number validation
- `python-multipart==0.0.6` - Form data parsing (for OAuth callbacks)

**Configuration**:
- OAuth credentials in AWS Secrets Manager
- JWT secret key in Secrets Manager
- SMS provider configuration (AWS SNS)

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial Authentication & Authorization Requirements | TBD |

---

**Document Status**: Draft  
**Next Review Date**: TBD  
**Approval Required From**: Product Owner, Backend Lead, Security Team


