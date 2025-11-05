# IAM Module Variables

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "s3_data_bucket_arn" {
  description = "ARN of the S3 data bucket"
  type        = string
}

variable "s3_logs_bucket_arn" {
  description = "ARN of the S3 logs bucket"
  type        = string
}

variable "s3_reports_bucket_arn" {
  description = "ARN of the S3 reports bucket"
  type        = string
}

