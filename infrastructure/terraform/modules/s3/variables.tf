# S3 Module Variables

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "owner_id" {
  description = "Owner/creator identifier to avoid conflicts in shared AWS accounts"
  type        = string
  default     = ""
}

