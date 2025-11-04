# SpendSense Development Environment

This directory contains the Terraform configuration for the SpendSense development environment.

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.6.6 installed
3. **AWS Account** with appropriate permissions

## Setup

1. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Review the plan**:
   ```bash
   terraform plan
   ```

4. **Apply the configuration**:
   ```bash
   terraform apply
   ```

## Configuration

The configuration sets up:
- **VPC** with public, private, and database subnets
- **RDS PostgreSQL** instance (db.t3.micro) - PostgreSQL 16.10 (adjusted for us-west-1 availability)
- **ElastiCache Redis** cluster (cache.t3.micro) - Redis 7.1 (adjusted for us-west-1 availability)
- **S3 buckets** for data, logs, reports, frontend, and Terraform state
- **IAM roles** for ECS tasks
- **Security groups** for network access control
- **CloudWatch log groups** for application logs

**AWS Region**: `us-west-1` (default)

**Shared Account Support**:
- Set `owner_id` variable (e.g., `-var="owner_id=chuong"`) when deploying to shared AWS accounts
- This prevents naming conflicts by including the identifier in resource names
- **Resource Naming Convention**:
  - VPC: `spendsense-{owner_id}-{env}-vpc` (e.g., `spendsense-chuong-dev-vpc`)
  - S3 Buckets: `spendsense-{resource}-{env}-{owner_id}` (e.g., `spendsense-data-dev-chuong`)
  - RDS Instance: `spendsense-{env}-db-{owner_id}` (e.g., `spendsense-dev-db-chuong`)
  - RDS Parameter Group: `spendsense-{env}-db-params-{owner_id}` (e.g., `spendsense-dev-db-params-chuong`)
  - RDS Subnet Group: `spendsense-{env}-db-subnet-group-{owner_id}` (e.g., `spendsense-dev-db-subnet-group-chuong`)
  - RDS Security Group: `spendsense-{env}-rds-sg-{owner_id}` (e.g., `spendsense-dev-rds-sg-chuong`)
  - Secrets Manager: `spendsense-{env}-db-password-{owner_id}` (e.g., `spendsense-dev-db-password-chuong`)
  - Redis: `spendsense-{env}-redis` (replication group ID doesn't include owner_id)

## Variables

Default variables are set in `variables.tf`. You can override them by:
- Creating a `terraform.tfvars` file (not committed to git)
- Using `-var` flags with terraform commands
- Setting environment variables with `TF_VAR_` prefix

## Outputs

After applying, you can view outputs with:
```bash
terraform output
```

Important outputs include:
- RDS endpoint and credentials (stored in Secrets Manager)
- Redis endpoint and credentials (stored in Secrets Manager)
- S3 bucket names
- IAM role ARNs
- Security group IDs

## Cost Estimation

Development environment costs approximately **$50-70/month**:
- RDS db.t3.micro: ~$15/month
- ElastiCache cache.t3.micro: ~$12/month
- NAT Gateway: ~$32/month
- S3 storage: ~$1-5/month (depending on usage)
- Data transfer: ~$5/month

## Cleanup

To destroy all resources:
```bash
terraform destroy
```

**Note**: This will permanently delete all resources. Make sure to backup any important data first.

## Security Notes

- Database and Redis passwords are stored in AWS Secrets Manager
- All S3 buckets are private by default
- Security groups restrict access to only necessary ports
- Encryption is enabled for RDS and ElastiCache

## Next Steps

After infrastructure is set up:
1. Configure backend application to use RDS and Redis endpoints
2. Update environment variables with secrets from Secrets Manager
3. Set up ECS cluster and service (Task 15.3)
4. Configure CI/CD pipeline (Task 16.1)

