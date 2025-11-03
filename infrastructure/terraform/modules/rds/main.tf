# RDS PostgreSQL Module

# Random password for RDS (if not provided)
# RDS password requirements: Only printable ASCII characters besides '/', '@', '"', ' ' may be used
resource "random_password" "db_password" {
  count   = var.create_db_password ? 1 : 0
  length  = 32
  special = true
  # Exclude characters that RDS doesn't allow: /, @, ", and space
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store database password in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name        = var.owner_id != "" ? "${var.project_name}-${var.environment}-db-password-${var.owner_id}" : "${var.project_name}-${var.environment}-db-password"
  description = "Database password for ${var.project_name} ${var.environment}"

  tags = {
    Name        = var.owner_id != "" ? "${var.project_name}-${var.environment}-db-password-${var.owner_id}" : "${var.project_name}-${var.environment}-db-password"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = var.create_db_password ? jsonencode({
    username = var.db_username
    password = random_password.db_password[0].result
  }) : jsonencode({
    username = var.db_username
    password = var.db_password
  })
}

# RDS Parameter Group
resource "aws_db_parameter_group" "main" {
  name   = var.owner_id != "" ? "${var.project_name}-${var.environment}-db-params-${var.owner_id}" : "${var.project_name}-${var.environment}-db-params"
  family = var.db_parameter_group_family

  tags = {
    Name        = var.owner_id != "" ? "${var.project_name}-${var.environment}-db-params-${var.owner_id}" : "${var.project_name}-${var.environment}-db-params"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# RDS Subnet Group (passed from VPC module)
resource "aws_db_subnet_group" "main" {
  name       = var.owner_id != "" ? "${var.project_name}-${var.environment}-db-subnet-group-${var.owner_id}" : "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.database_subnet_ids

  tags = {
    Name        = var.owner_id != "" ? "${var.project_name}-${var.environment}-db-subnet-group-${var.owner_id}" : "${var.project_name}-${var.environment}-db-subnet-group"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name        = var.owner_id != "" ? "${var.project_name}-${var.environment}-rds-sg-${var.owner_id}" : "${var.project_name}-${var.environment}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
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
    Name        = var.owner_id != "" ? "${var.project_name}-${var.environment}-rds-sg-${var.owner_id}" : "${var.project_name}-${var.environment}-rds-sg"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = var.owner_id != "" ? "${var.project_name}-${var.environment}-db-${var.owner_id}" : "${var.project_name}-${var.environment}-db"

  engine         = var.db_engine
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = var.db_storage_type
  storage_encrypted      = var.db_storage_encrypted

  db_name  = var.db_name
  username = var.db_username
  password = var.create_db_password ? random_password.db_password[0].result : var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name

  backup_retention_period = var.db_backup_retention_period
  backup_window          = var.db_backup_window
  maintenance_window     = var.db_maintenance_window

  # Multi-AZ for production, single AZ for dev
  multi_az = var.environment == "prod" ? true : false

  # Enable deletion protection for production
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment == "dev" ? true : false
  final_snapshot_identifier = var.environment == "dev" ? null : "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Performance Insights
  performance_insights_enabled          = var.environment == "prod" ? true : false
  performance_insights_retention_period = var.environment == "prod" ? 7 : null

  # Monitoring
  monitoring_interval = var.environment == "prod" ? 60 : 0
  monitoring_role_arn = var.environment == "prod" ? aws_iam_role.rds_monitoring[0].arn : null

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Name        = var.owner_id != "" ? "${var.project_name}-${var.environment}-db-${var.owner_id}" : "${var.project_name}-${var.environment}-db"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }

  depends_on = [aws_secretsmanager_secret_version.db_password]
}

# IAM Role for RDS Enhanced Monitoring (production only)
resource "aws_iam_role" "rds_monitoring" {
  count = var.environment == "prod" ? 1 : 0
  name  = var.owner_id != "" ? "${var.project_name}-${var.environment}-rds-monitoring-role-${var.owner_id}" : "${var.project_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = var.owner_id != "" ? "${var.project_name}-${var.environment}-rds-monitoring-role-${var.owner_id}" : "${var.project_name}-${var.environment}-rds-monitoring-role"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count      = var.environment == "prod" ? 1 : 0
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

