# Deployment & Infrastructure Requirements
## SpendSense Platform - Backend Layer

**Version**: 1.0  
**Date**: 2024-01-15  
**Status**: Planning  

---

## Executive Summary

This document defines the deployment and infrastructure requirements for the SpendSense backend, including containerization, ECS deployment, CI/CD pipeline, and Infrastructure as Code.

---

## Technology Stack

### Containerization
- **Docker**: `24.0.7+` (containerization)

### Deployment
- **ECS Fargate**: Container orchestration
- **ALB**: Load balancing
- **API Gateway**: API routing and throttling (optional)

### CI/CD
- **GitHub Actions**: Automated testing and deployment
- **AWS ECR**: Container registry
- **Terraform**: `1.6.6` (Infrastructure as Code)

---

## Containerization

### Dockerfile

**Multi-stage Build**:
```dockerfile
# Build stage
FROM python:3.11.7-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11.7-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Requirements**:
- Multi-stage build for optimization (smaller image size)
- Health check endpoint
- Non-root user (security)
- Python 3.11.7 base image
- Slim image (alpine or slim variant)

### Docker Image Optimization

**Best Practices**:
- Use multi-stage builds
- Minimize layers
- Use .dockerignore to exclude unnecessary files
- Cache dependencies (requirements.txt copied separately)
- Use specific version tags (not `latest`)

**Image Size Target**: <500MB

---

## ECS Fargate Deployment

### Task Definition

**Configuration**:
- **CPU**: 512 (.5 vCPU) for dev, 1024 (1 vCPU) for prod
- **Memory**: 1024 MB for dev, 2048 MB for prod
- **Network Mode**: awsvpc
- **Task Role**: IAM role for S3, RDS, ElastiCache access
- **Execution Role**: IAM role for ECR, CloudWatch Logs access

**Container Definition**:
- **Image**: ECR repository URI
- **Port Mappings**: 8000 (container) → 8000 (host)
- **Environment Variables**: 
  - Database connection string (Secrets Manager)
  - Redis endpoint (Secrets Manager)
  - JWT secret key (Secrets Manager)
  - OAuth credentials (Secrets Manager)
- **Health Check**: 
  - Command: `CMD-SHELL,curl -f http://localhost:8000/health || exit 1`
  - Interval: 30 seconds
  - Timeout: 5 seconds
  - Start period: 60 seconds
  - Retries: 3

### Service Configuration

**Service Definition**:
- **Service Name**: `spendsense-backend`
- **Launch Type**: Fargate
- **Task Definition**: Latest revision
- **Desired Count**: 2 (min), 10 (max)
- **Subnets**: Private subnets (VPC)
- **Security Groups**: Allow traffic from ALB (port 8000)
- **Load Balancer**: ALB target group
- **Auto Scaling**: 
  - CPU utilization: 70% threshold
  - Memory utilization: 80% threshold
  - Min capacity: 2
  - Max capacity: 10

### Load Balancing

**Application Load Balancer (ALB)**:
- **Type**: Application Load Balancer
- **Scheme**: Internet-facing
- **Listeners**: HTTPS (443) → HTTP (8000)
- **SSL Certificate**: ACM certificate
- **Target Group**: ECS service
- **Health Check**: `/health` endpoint
- **Health Check Interval**: 30 seconds
- **Health Check Timeout**: 5 seconds
- **Unhealthy Threshold**: 2
- **Healthy Threshold**: 2

**Target Group Configuration**:
- **Protocol**: HTTP
- **Port**: 8000
- **Health Check Path**: `/health`
- **Deregistration Delay**: 30 seconds

### Auto Scaling

**Target Tracking Policies**:
- **CPU Utilization**: 70% target
- **Memory Utilization**: 80% target
- **Request Count**: 1000 requests/minute per instance

**Scaling Configuration**:
- **Min Capacity**: 2 tasks
- **Max Capacity**: 10 tasks
- **Scale Out**: Add 1 task if threshold exceeded for 2 minutes
- **Scale In**: Remove 1 task if below threshold for 5 minutes

---

## CI/CD Pipeline

### GitHub Actions Workflow

**Workflow Stages**:
1. **Lint & Test**: Run linting and unit tests
2. **Build**: Build Docker image
3. **Push to ECR**: Push image to ECR registry
4. **Deploy to ECS**: Update ECS service with new image

**Workflow File**: `.github/workflows/deploy.yml`

**Example Workflow**:
```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
      - name: Run linting
        run: pylint app/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
      - name: Login to ECR
        run: aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
      - name: Build Docker image
        run: docker build -t $ECR_REGISTRY:$IMAGE_TAG .
      - name: Push Docker image
        run: docker push $ECR_REGISTRY:$IMAGE_TAG
      - name: Deploy to ECS
        run: aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment
```

**Environment Variables**:
- `ECR_REGISTRY`: ECR repository URI
- `IMAGE_TAG`: Image tag (commit SHA or version)
- `CLUSTER_NAME`: ECS cluster name
- `SERVICE_NAME`: ECS service name

### Deployment Strategy

**Rolling Update**:
- ECS service updates tasks one at a time
- Health checks ensure new tasks are healthy before removing old tasks
- Rollback: Revert to previous task definition if health checks fail

**Blue/Green Deployment** (Optional):
- Create new service with new task definition
- Switch ALB target group to new service
- Monitor new service health
- Rollback: Switch target group back to old service

---

## Infrastructure as Code

### Terraform

**Configuration**:
- **Provider**: AWS
- **Version**: Terraform 1.6.6
- **State**: Remote state in S3 (with DynamoDB lock)

**Resources**:
- VPC (Virtual Private Cloud)
- Subnets (public and private)
- Internet Gateway
- NAT Gateway
- Security Groups
- RDS PostgreSQL instance
- ElastiCache Redis cluster
- S3 buckets
- ECS Cluster
- ECS Service
- ECS Task Definition
- Application Load Balancer
- Target Groups
- IAM Roles and Policies
- CloudWatch Log Groups
- Secrets Manager secrets

**Structure**:
```
terraform/
  main.tf           # Main configuration
  variables.tf      # Input variables
  outputs.tf        # Output values
  modules/
    vpc/           # VPC module
    rds/           # RDS module
    ecs/           # ECS module
    alb/           # ALB module
```

**Environments**:
- **Dev**: Minimal resources, low cost ✅ **COMPLETE** (Task 1.3)
  - VPC, RDS PostgreSQL 16.10, ElastiCache Redis 7.1, S3 buckets, IAM roles
  - Includes `owner_id` support for shared AWS accounts (us-west-1 region)
- **Staging**: Production-like configuration (future)
- **Prod**: High availability, multiple AZs (future)

**Shared Account Support**:
When deploying to a shared AWS account, use the `owner_id` variable:
```bash
terraform apply -var="owner_id=your-identifier"
```
This prevents naming conflicts by including your identifier in resource names. See [infrastructure README](../../../infrastructure/README.md) for details.

### Terraform Variables

**Required Variables**:
- `environment`: Environment name (dev, staging, prod)
- `aws_region`: AWS region (default: `us-west-1`)
- `vpc_cidr`: VPC CIDR block (default: `10.1.0.0/16`)
- `db_instance_class`: RDS instance class
- `redis_node_type`: ElastiCache node type
- `ecs_cpu`: ECS task CPU
- `ecs_memory`: ECS task memory
- `min_capacity`: Auto-scaling min capacity
- `max_capacity`: Auto-scaling max capacity

**Optional Variables**:
- `owner_id`: Owner/creator identifier for shared AWS accounts (e.g., `chuong`, `jane`)
  - When specified, resources include this identifier in their names to avoid conflicts
  - Example: `terraform apply -var="owner_id=chuong"`
  - Resources affected: VPC, S3 buckets, RDS instances, parameter groups, subnet groups, security groups, Secrets Manager secrets

### Terraform State Management

**Remote State**:
- S3 bucket for state storage
- DynamoDB table for state locking
- State encryption at rest (S3 SSE)

**State Access**:
- IAM roles restrict state access
- State versioning enabled
- State backup enabled

---

## Monitoring & Logging

### CloudWatch Logs

**Log Groups**:
- `/ecs/spendsense-backend` - Application logs
- `/ecs/spendsense-backend/access` - Access logs
- `/ecs/spendsense-backend/errors` - Error logs

**Log Configuration**:
- Log level: INFO (production), DEBUG (development)
- Structured logging (JSON format)
- Log retention: 30 days

### CloudWatch Metrics

**Metrics**:
- CPU utilization
- Memory utilization
- Request count
- Error rate
- Response time

**Alarms**:
- High CPU utilization (>80% for 5 minutes)
- High memory utilization (>90% for 5 minutes)
- High error rate (>1% for 5 minutes)
- Service unavailable (health check failures)

---

## Security

### Network Security

**VPC Configuration**:
- Private subnets for ECS tasks
- Public subnets for ALB and NAT Gateway
- Security groups: Restrict traffic to necessary ports
- Network ACLs: Additional layer of security

**Security Groups**:
- ALB: Allow HTTPS (443) from internet
- ECS: Allow HTTP (8000) from ALB security group
- RDS: Allow PostgreSQL (5432) from ECS security group
- Redis: Allow Redis (6379) from ECS security group

### Secrets Management

**AWS Secrets Manager**:
- Database connection strings
- JWT secret keys
- OAuth credentials
- Redis endpoints

**Secret Rotation**:
- Automatic rotation for database passwords (optional)
- Manual rotation for OAuth credentials
- Secret versioning enabled

---

## Disaster Recovery

### Backup Strategy

**RDS Backups**:
- Automated daily backups
- Retention: 30 days
- Point-in-time recovery: 7 days

**S3 Backups**:
- Versioning enabled
- Cross-region replication (optional)

### Recovery Procedures

**RTO (Recovery Time Objective)**: <1 hour  
**RPO (Recovery Point Objective)**: <15 minutes

**Recovery Steps**:
1. Restore RDS from backup
2. Restore S3 files from versioning
3. Recreate ECS service with latest task definition
4. Update ALB target group
5. Verify health checks

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial Deployment & Infrastructure Requirements | TBD |

---

**Document Status**: Draft  
**Next Review Date**: TBD  
**Approval Required From**: Product Owner, Backend Lead, DevOps Team


