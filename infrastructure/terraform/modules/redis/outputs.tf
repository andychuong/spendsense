# Redis Module Outputs

output "redis_replication_group_id" {
  description = "ElastiCache replication group ID"
  value       = aws_elasticache_replication_group.main.replication_group_id
}

output "redis_replication_group_arn" {
  description = "ElastiCache replication group ARN"
  value       = aws_elasticache_replication_group.main.arn
}

output "redis_primary_endpoint_address" {
  description = "ElastiCache primary endpoint address"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "redis_reader_endpoint_address" {
  description = "ElastiCache reader endpoint address"
  value       = aws_elasticache_replication_group.main.reader_endpoint_address
}

output "redis_port" {
  description = "ElastiCache port"
  value       = aws_elasticache_replication_group.main.port
}

output "redis_security_group_id" {
  description = "Security group ID for ElastiCache"
  value       = aws_security_group.redis.id
}

output "redis_secret_arn" {
  description = "ARN of the Redis auth token secret (if enabled)"
  value       = var.redis_auth_token_enabled ? aws_secretsmanager_secret.redis_password[0].arn : null
}

output "redis_secret_name" {
  description = "Name of the Redis auth token secret (if enabled)"
  value       = var.redis_auth_token_enabled ? aws_secretsmanager_secret.redis_password[0].name : null
}
