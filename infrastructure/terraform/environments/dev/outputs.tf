# Development Environment Outputs

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "VPC CIDR block"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = module.vpc.database_subnet_ids
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
}

output "rds_address" {
  description = "RDS instance address"
  value       = module.rds.db_instance_address
}

output "rds_port" {
  description = "RDS instance port"
  value       = module.rds.db_instance_port
}

output "rds_secret_arn" {
  description = "ARN of the database password secret"
  value       = module.rds.db_secret_arn
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = module.redis.redis_primary_endpoint_address
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = module.redis.redis_port
}

output "redis_secret_arn" {
  description = "ARN of the Redis auth token secret"
  value       = module.redis.redis_secret_arn
  sensitive   = true
}

output "s3_data_bucket" {
  description = "S3 data bucket name"
  value       = module.s3.data_bucket_id
}

output "s3_logs_bucket" {
  description = "S3 logs bucket name"
  value       = module.s3.logs_bucket_id
}

output "s3_reports_bucket" {
  description = "S3 reports bucket name"
  value       = module.s3.reports_bucket_id
}

output "s3_frontend_bucket" {
  description = "S3 frontend bucket name"
  value       = module.s3.frontend_bucket_id
}

output "s3_terraform_state_bucket" {
  description = "S3 Terraform state bucket name"
  value       = module.s3.terraform_state_bucket_id
}

output "ecs_execution_role_arn" {
  description = "ECS task execution role ARN"
  value       = module.iam.ecs_execution_role_arn
}

output "ecs_task_role_arn" {
  description = "ECS task role ARN"
  value       = module.iam.ecs_task_role_arn
}

output "ecs_security_group_id" {
  description = "ECS security group ID"
  value       = aws_security_group.ecs.id
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = module.rds.db_security_group_id
}

output "redis_security_group_id" {
  description = "Redis security group ID"
  value       = module.redis.redis_security_group_id
}
