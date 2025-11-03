# Redis Module Variables

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where ElastiCache will be created"
  type        = string
}

variable "database_subnet_ids" {
  description = "List of database subnet IDs"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  type        = string
}

variable "redis_engine" {
  description = "Redis engine"
  type        = string
  default     = "redis"
}

variable "redis_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.1"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes (for production)"
  type        = number
  default     = 2
}

variable "redis_parameter_group_family" {
  description = "Parameter group family"
  type        = string
  default     = "redis7"
}

variable "redis_auth_token_enabled" {
  description = "Enable Redis auth token"
  type        = bool
  default     = true
}

variable "redis_auth_token" {
  description = "Redis auth token (if not creating random)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "create_redis_password" {
  description = "Whether to create a random Redis auth token"
  type        = bool
  default     = true
}

variable "redis_at_rest_encryption_enabled" {
  description = "Enable encryption at rest"
  type        = bool
  default     = true
}

variable "redis_transit_encryption_enabled" {
  description = "Enable encryption in transit"
  type        = bool
  default     = true
}

variable "redis_snapshot_retention_limit" {
  description = "Snapshot retention limit in days"
  type        = number
  default     = 7
}

variable "redis_snapshot_window" {
  description = "Snapshot window"
  type        = string
  default     = "03:00-05:00"
}

variable "redis_maintenance_window" {
  description = "Maintenance window"
  type        = string
  default     = "mon:05:00-mon:07:00"
}

