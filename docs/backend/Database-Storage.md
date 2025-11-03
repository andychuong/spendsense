# Database & Storage Requirements
## SpendSense Platform - Backend Layer

**Version**: 1.0  
**Date**: 2024-01-15  
**Status**: Planning  

---

## Executive Summary

This document defines the database and storage requirements for the SpendSense backend, including PostgreSQL for relational data, Redis for caching, and S3 for file storage.

---

## Database Architecture

### Technology Stack

**Relational Database**:
- **PostgreSQL**: `16.10` (RDS) - adjusted for us-west-1 availability
- **SQLAlchemy**: `2.0.23` (ORM)
- **Alembic**: `1.13.0` (migrations)

**Caching**:
- **Redis**: `7.1` (ElastiCache) - session cache, rate limiting (adjusted for us-west-1 availability)

**File Storage**:
- **S3**: Parquet files for analytics, static assets

---

## Database Schema

### Users Table

**Schema**:
- `user_id` (UUID, PK)
- `email` (String, unique, nullable)
- `phone_number` (String, unique, nullable)
- `password_hash` (String, nullable)
- `oauth_providers` (JSON, linked providers: `{"google": "provider_id", "github": "provider_id"}`)
- `role` (String, default: "user", enum: user, operator, admin)
- `consent_status` (Boolean, default: false)
- `consent_version` (String, default: "1.0")
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

**Indexes**:
- Index on `email` (unique)
- Index on `phone_number` (unique)
- Index on `user_id`

---

### Sessions Table

**Schema**:
- `session_id` (UUID, PK)
- `user_id` (UUID, FK → Users.user_id)
- `refresh_token` (String, unique)
- `expires_at` (Timestamp)
- `created_at` (Timestamp)
- `last_used_at` (Timestamp)

**Indexes**:
- Index on `user_id`
- Index on `refresh_token` (unique)
- Index on `expires_at` (for cleanup)

---

### Data Uploads Table

**Schema**:
- `upload_id` (UUID, PK)
- `user_id` (UUID, FK → Users.user_id)
- `file_name` (String)
- `file_size` (Integer)
- `file_type` (String, enum: json, csv)
- `s3_key` (String)
- `s3_bucket` (String)
- `status` (String, enum: pending, processing, completed, failed)
- `validation_errors` (JSON, nullable)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)
- `processed_at` (Timestamp, nullable)

**Indexes**:
- Index on `user_id`
- Index on `status`
- Index on `created_at`

---

### Recommendations Table

**Schema**:
- `recommendation_id` (UUID, PK)
- `user_id` (UUID, FK → Users.user_id)
- `type` (String, enum: education, partner_offer)
- `title` (String)
- `content` (Text)
- `rationale` (Text)
- `status` (String, enum: pending, approved, rejected)
- `decision_trace` (JSON)
- `created_at` (Timestamp)
- `approved_at` (Timestamp, nullable)
- `approved_by` (UUID, nullable, FK → Users.user_id)
- `rejected_at` (Timestamp, nullable)
- `rejected_by` (UUID, nullable, FK → Users.user_id)
- `rejection_reason` (String, nullable)

**Indexes**:
- Index on `user_id`
- Index on `status`
- Index on `created_at`
- Index on `approved_at`
- Composite index on `(user_id, status)`

---

### User Profiles Table

**Schema**:
- `profile_id` (UUID, PK)
- `user_id` (UUID, FK → Users.user_id, unique)
- `persona_id` (Integer, enum: 1, 2, 3, 4, 5)
- `persona_name` (String)
- `signals_30d` (JSON) - 30-day signals
- `signals_180d` (JSON) - 180-day signals
- `updated_at` (Timestamp)

**Indexes**:
- Index on `user_id` (unique)
- Index on `persona_id`

---

### Persona History Table

**Schema**:
- `history_id` (UUID, PK)
- `user_id` (UUID, FK → Users.user_id)
- `persona_id` (Integer)
- `persona_name` (String)
- `assigned_at` (Timestamp)
- `signals` (JSON)

**Indexes**:
- Index on `user_id`
- Index on `assigned_at`
- Composite index on `(user_id, assigned_at)`

---

## Database Management

### FR-BE-003: Database Management
**Priority**: Must Have

- PostgreSQL for relational data
- SQLAlchemy ORM for data access
- Alembic for database migrations
- Connection pooling
- Query optimization
- Transaction management
- Data backup and recovery

### Connection Pooling

**Configuration**:
- Min connections: 5
- Max connections: 20
- Connection timeout: 30 seconds
- Idle timeout: 600 seconds

**Connection String**:
```
postgresql://user:password@host:5432/dbname?pool_size=20&max_overflow=10
```

### Database Migrations

**Alembic**:
- Version control for database schema
- Migrations stored in `alembic/versions/`
- Migration commands:
  - `alembic revision --autogenerate -m "description"`
  - `alembic upgrade head`
  - `alembic downgrade -1`

**Migration Strategy**:
- Create migrations for all schema changes
- Test migrations in staging before production
- Backup database before migrations
- Rollback plan for failed migrations

### Query Optimization

**Best Practices**:
- Use indexes for frequently queried columns
- Avoid N+1 queries (use eager loading)
- Use database functions for aggregations
- Cache frequently accessed data (Redis)
- Monitor slow queries (CloudWatch)

**Query Monitoring**:
- Log queries exceeding 100ms
- Monitor query performance metrics
- Regular query optimization reviews

### Data Backup and Recovery

**Backup Strategy**:
- Automated daily backups (RDS automated backups)
- Retention: 30 days
- Point-in-time recovery: 7 days
- Cross-region backup: Optional

**Recovery**:
- RTO (Recovery Time Objective): <1 hour
- RPO (Recovery Point Objective): <15 minutes
- Test recovery procedures quarterly

---

## Caching

### FR-BE-004: Caching
**Priority**: Must Have

- Redis for session storage
- Redis for API response caching
- Redis for rate limiting
- Cache invalidation strategy
- TTL management

### Redis Configuration

**ElastiCache Redis**:
- Version: 7.1 (adjusted for us-west-1 availability)
- Node type: cache.t3.micro (dev), cache.t3.small (prod)
- Cluster mode: Disabled (single node)
- Multi-AZ: Enabled (production)
- Backup: Daily backups

**Connection**:
- Host: ElastiCache endpoint
- Port: 6379
- SSL: Enabled (TLS 1.3)
- Timeout: 5 seconds

### Cache Strategy

**Session Storage**:
- Key: `session:{session_id}`
- TTL: 30 days (refresh token expiration)
- Value: JSON with user_id, role, last_used_at

**API Response Caching**:
- User profiles: `profile:{user_id}` (TTL: 5 minutes)
- Recommendations: `recommendations:{user_id}` (TTL: 1 hour)
- Behavioral signals: `signals:{user_id}` (TTL: 24 hours)

**Rate Limiting**:
- Login attempts: `ratelimit:login:{ip}` (TTL: 1 hour)
- SMS requests: `ratelimit:sms:{phone}` (TTL: 1 hour)
- API requests: `ratelimit:api:{user_id}` (TTL: 1 hour)

**Token Blacklisting**:
- Revoked tokens: `blacklist:token:{token_id}` (TTL: token expiration)

**SMS Verification Codes**:
- Verification codes: `verify:{phone_number}` (TTL: 10 minutes)
- Max attempts: `verify:attempts:{phone_number}` (TTL: 10 minutes)

**Cache Invalidation**:
- Invalidate on data updates (user profile, recommendations)
- Invalidate on consent revocation
- Invalidate on user deletion

---

## File Storage

### FR-BE-005: File Storage
**Priority**: Must Have

- S3 for file storage (uploaded data files)
- S3 for Parquet analytics files
- Pre-signed URLs for file access
- File lifecycle management
- Encryption at rest (S3)

### S3 Configuration

**Buckets**:
- `spendsense-data` - Transaction data files (JSON/CSV)
- `spendsense-analytics` - Parquet analytics files
- `spendsense-static` - Static assets (optional)

**Bucket Configuration**:
- Encryption: AES-256 (SSE-S3)
- Versioning: Enabled
- Lifecycle rules:
  - Data files: Move to Glacier after 90 days, delete after 365 days
  - Analytics files: Move to Glacier after 180 days, delete after 730 days

**Access Control**:
- IAM roles for application access
- Pre-signed URLs for temporary file access (15-minute expiration)
- Bucket policy: Deny public access

### File Upload Flow

1. User uploads file via API
2. Validate file format and size (max 10MB)
3. Generate unique file key: `uploads/{user_id}/{upload_id}/{filename}`
4. Upload to S3
5. Store metadata in PostgreSQL (Data Uploads table)
6. Trigger async processing pipeline

### Pre-signed URLs

**Use Case**: Allow frontend to upload files directly to S3

**Flow**:
1. Frontend requests pre-signed URL from backend
2. Backend generates pre-signed POST URL with constraints
3. Frontend uploads file directly to S3
4. Frontend notifies backend of upload completion
5. Backend validates upload and triggers processing

**URL Expiration**: 15 minutes

---

## Data Models

### SQLAlchemy Models

**Location**: `app/models/`

**Example User Model**:
```python
from sqlalchemy import Column, String, Boolean, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, nullable=True)
    phone_number = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    oauth_providers = Column(JSON)
    role = Column(String, default="user")
    consent_status = Column(Boolean, default=False)
    consent_version = Column(String, default="1.0")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

---

## Performance Requirements

### NFR-BE-001: Performance

- **Database Query Time**: <100ms (p95)
- **Cache Hit Rate**: ≥80%
- **File Upload Time**: <10 seconds (10MB file)
- **Connection Pool Efficiency**: ≥90% connection utilization

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial Database & Storage Requirements | TBD |

---

**Document Status**: Draft  
**Next Review Date**: TBD  
**Approval Required From**: Product Owner, Backend Lead, Database Team


