# SpendSense Infrastructure

Infrastructure as Code (IaC) configurations for AWS deployment.

## Technology Stack

- **IaC Tool**: Terraform 1.6.6
- **Cloud Provider**: AWS
- **Container Registry**: ECR
- **Container Runtime**: Docker 24.0.7+

## Project Structure

```
infrastructure/
├── terraform/
│   ├── environments/
│   │   ├── dev/             # Development environment ✅
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   ├── versions.tf
│   │   │   ├── README.md
│   │   │   └── .gitignore
│   │   ├── staging/         # Staging environment (future)
│   │   └── prod/            # Production environment (future)
│   ├── modules/
│   │   ├── vpc/             # VPC configuration ✅
│   │   ├── rds/             # RDS PostgreSQL ✅
│   │   ├── redis/           # ElastiCache Redis ✅
│   │   ├── s3/              # S3 buckets ✅
│   │   ├── iam/             # IAM roles and policies ✅
│   │   ├── ecs/             # ECS Fargate setup (future)
│   │   └── alb/             # Application Load Balancer (future)
│   └── .gitignore
├── docker/
│   ├── backend/
│   │   └── Dockerfile
│   └── frontend/
│       └── Dockerfile
└── README.md
```

## Setup

1. Install Terraform:
   ```bash
   # macOS
   brew install terraform

   # Or download from https://www.terraform.io/downloads
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```

3. Initialize Terraform:
   ```bash
   cd terraform/environments/dev
   terraform init
   ```

4. Plan and apply:
   ```bash
   # For shared AWS accounts, specify your owner_id:
   terraform plan -var="owner_id=your-identifier"
   terraform apply -var="owner_id=your-identifier"

   # For dedicated accounts, you can omit owner_id:
   terraform plan
   terraform apply
   ```

**Shared Account Support:**
When deploying to a shared AWS account, use the `owner_id` variable to avoid naming conflicts:
- Resources will include your identifier in their names (e.g., `spendsense-dev-db-chuong`)
- VPC: `spendsense-{owner_id}-{env}-vpc`
- S3 Buckets: `spendsense-{resource}-{env}-{owner_id}`
- RDS: `spendsense-{env}-db-{owner_id}`
- Redis: `spendsense-{env}-redis` (no owner_id needed for Redis replication group ID)

See the `terraform/` and `n8n/` directories for infrastructure code and workflows.


