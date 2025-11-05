# S3 Module Outputs

output "data_bucket_id" {
  description = "ID of the data bucket"
  value       = aws_s3_bucket.data.id
}

output "data_bucket_arn" {
  description = "ARN of the data bucket"
  value       = aws_s3_bucket.data.arn
}

output "logs_bucket_id" {
  description = "ID of the logs bucket"
  value       = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  description = "ARN of the logs bucket"
  value       = aws_s3_bucket.logs.arn
}

output "reports_bucket_id" {
  description = "ID of the reports bucket"
  value       = aws_s3_bucket.reports.id
}

output "reports_bucket_arn" {
  description = "ARN of the reports bucket"
  value       = aws_s3_bucket.reports.arn
}

output "frontend_bucket_id" {
  description = "ID of the frontend bucket"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_bucket_arn" {
  description = "ARN of the frontend bucket"
  value       = aws_s3_bucket.frontend.arn
}

output "terraform_state_bucket_id" {
  description = "ID of the Terraform state bucket"
  value       = aws_s3_bucket.terraform_state.id
}

output "terraform_state_bucket_arn" {
  description = "ARN of the Terraform state bucket"
  value       = aws_s3_bucket.terraform_state.arn
}

