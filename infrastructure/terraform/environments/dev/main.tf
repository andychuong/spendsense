# SpendSense Development Environment
# This configuration sets up AWS infrastructure for the development environment

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  }
}

# Get availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  owner_id             = var.owner_id
  vpc_cidr             = var.vpc_cidr
  availability_zones   = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  database_subnet_cidrs = var.database_subnet_cidrs
}

# ECS Security Group (for use by RDS and Redis modules)
resource "aws_security_group" "ecs" {
  name        = "${var.project_name}-${var.environment}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = module.vpc.vpc_id

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-ecs-sg"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# S3 Buckets Module
module "s3" {
  source = "../../modules/s3"

  project_name = var.project_name
  environment  = var.environment
  owner_id     = var.owner_id
}

# RDS Module
module "rds" {
  source = "../../modules/rds"

  project_name         = var.project_name
  environment          = var.environment
  owner_id             = var.owner_id
  vpc_id               = module.vpc.vpc_id
  database_subnet_ids  = module.vpc.database_subnet_ids
  ecs_security_group_id = aws_security_group.ecs.id

  db_instance_class      = var.db_instance_class
  db_allocated_storage   = var.db_allocated_storage
  db_max_allocated_storage = var.db_max_allocated_storage
  db_backup_retention_period = var.db_backup_retention_period
}

# ElastiCache Redis Module
module "redis" {
  source = "../../modules/redis"

  project_name         = var.project_name
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  database_subnet_ids  = module.vpc.database_subnet_ids
  ecs_security_group_id = aws_security_group.ecs.id

  redis_node_type = var.redis_node_type
}

# IAM Roles Module
module "iam" {
  source = "../../modules/iam"

  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  s3_data_bucket_arn    = module.s3.data_bucket_arn
  s3_logs_bucket_arn    = module.s3.logs_bucket_arn
  s3_reports_bucket_arn = module.s3.reports_bucket_arn
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-${var.environment}-ecs-logs"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

