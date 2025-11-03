# ElastiCache Redis Module

# Random password for Redis (if not provided)
resource "random_password" "redis_password" {
  count   = var.create_redis_password && var.redis_auth_token_enabled ? 1 : 0
  length  = 32
  special = true
}

# Store Redis password in Secrets Manager (if auth token is enabled)
resource "aws_secretsmanager_secret" "redis_password" {
  count       = var.redis_auth_token_enabled ? 1 : 0
  name        = "${var.project_name}-${var.environment}-redis-password"
  description = "Redis auth token for ${var.project_name} ${var.environment}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis-password"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret_version" "redis_password" {
  count     = var.redis_auth_token_enabled && var.create_redis_password ? 1 : 0
  secret_id = aws_secretsmanager_secret.redis_password[0].id
  secret_string = jsonencode({
    auth_token = random_password.redis_password[0].result
  })
}

# ElastiCache Parameter Group
resource "aws_elasticache_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-redis-params"
  family = var.redis_parameter_group_family

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis-params"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# ElastiCache Security Group
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Security group for ElastiCache Redis"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Redis from ECS"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis-sg"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# ElastiCache Subnet Group (passed from VPC module)
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-cache-subnet-group"
  subnet_ids = var.database_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-cache-subnet-group"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# ElastiCache Replication Group (for dev: single node, for prod: cluster mode)
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  description                = "Redis cluster for ${var.project_name} ${var.environment}"

  # Engine configuration
  engine               = var.redis_engine
  engine_version       = var.redis_engine_version
  node_type            = var.redis_node_type
  port                 = var.redis_port

  # Network configuration
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  # Cluster configuration
  num_cache_clusters   = var.environment == "dev" ? 1 : var.redis_num_cache_nodes
  parameter_group_name = aws_elasticache_parameter_group.main.name

  # Encryption (transit encryption requires auth token)
  at_rest_encryption_enabled = var.redis_at_rest_encryption_enabled
  transit_encryption_enabled = var.redis_transit_encryption_enabled
  
  # Auth token (required when transit encryption is enabled)
  auth_token = var.redis_transit_encryption_enabled ? (var.create_redis_password && var.redis_auth_token_enabled ? random_password.redis_password[0].result : (var.redis_auth_token_enabled ? var.redis_auth_token : null)) : null

  # Snapshot configuration
  snapshot_retention_limit = var.redis_snapshot_retention_limit
  snapshot_window         = var.redis_snapshot_window

  # Maintenance window
  maintenance_window = var.redis_maintenance_window

  # Auto-failover (for production)
  automatic_failover_enabled = var.environment == "prod" ? true : false

  # Multi-AZ (for production)
  multi_az_enabled = var.environment == "prod" ? true : false

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

