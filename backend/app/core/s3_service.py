"""S3 service for file storage using AWS S3."""

import logging
import uuid
from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from botocore.config import Config
from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)

# S3 configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["json", "csv"]
ALLOWED_MIME_TYPES = {
    "json": ["application/json", "text/json"],
    "csv": ["text/csv", "application/csv", "text/plain"],
}


def get_s3_client():
    """
    Get S3 client with configuration.
    
    Returns:
        boto3 S3 client
    """
    config = Config(
        region_name=settings.aws_region,
        retries={"max_attempts": 3, "mode": "standard"},
    )
    
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        return boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=config,
        )
    else:
        # Use default credentials (IAM role, environment variables, etc.)
        return boto3.client("s3", config=config)


def validate_file_type(file_name: str, content_type: Optional[str] = None) -> str:
    """
    Validate file type based on extension and content type.
    
    Args:
        file_name: Name of the uploaded file
        content_type: MIME type of the file (optional)
        
    Returns:
        File type ("json" or "csv")
        
    Raises:
        ValueError: If file type is not supported
    """
    # Check file extension
    file_extension = file_name.lower().split(".")[-1] if "." in file_name else ""
    
    if file_extension not in ALLOWED_FILE_TYPES:
        raise ValueError(
            f"Unsupported file type. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    
    # Optionally validate content type if provided
    if content_type:
        allowed_mimes = ALLOWED_MIME_TYPES.get(file_extension, [])
        if content_type.lower() not in [mime.lower() for mime in allowed_mimes]:
            logger.warning(
                f"Content type {content_type} does not match file extension {file_extension}"
            )
    
    return file_extension


def validate_file_size(file_size: int) -> None:
    """
    Validate file size.
    
    Args:
        file_size: Size of the file in bytes
        
    Raises:
        ValueError: If file size exceeds maximum allowed size
    """
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)"
        )
    
    if file_size <= 0:
        raise ValueError("File size must be greater than 0")


def generate_s3_key(user_id: uuid.UUID, upload_id: uuid.UUID, file_name: str) -> str:
    """
    Generate S3 key for uploaded file.
    
    Format: uploads/{user_id}/{upload_id}/{filename}
    
    Args:
        user_id: User ID
        upload_id: Upload ID
        file_name: Original file name
        
    Returns:
        S3 key string
    """
    # Sanitize file name (remove path separators and other dangerous characters)
    safe_file_name = file_name.replace("/", "_").replace("\\", "_")
    
    return f"uploads/{user_id}/{upload_id}/{safe_file_name}"


def upload_file_to_s3(
    file_content: bytes,
    bucket: str,
    key: str,
    content_type: Optional[str] = None,
) -> None:
    """
    Upload file to S3.
    
    Args:
        file_content: File content as bytes
        bucket: S3 bucket name
        key: S3 object key
        content_type: Content type of the file (optional)
        
    Raises:
        ClientError: If S3 upload fails
        BotoCoreError: If AWS service error occurs
    """
    try:
        s3_client = get_s3_client()
        
        upload_kwargs = {
            "Bucket": bucket,
            "Key": key,
            "Body": file_content,
            "ServerSideEncryption": "AES256",
        }
        
        if content_type:
            upload_kwargs["ContentType"] = content_type
        
        s3_client.put_object(**upload_kwargs)
        
        logger.info(f"Successfully uploaded file to S3: s3://{bucket}/{key}")
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"S3 upload failed: {error_code} - {error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to S3: {error_message}",
        )
    except BotoCoreError as e:
        logger.error(f"AWS service error during S3 upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AWS service error: {str(e)}",
        )


def get_file_from_s3(bucket: str, key: str) -> bytes:
    """
    Get file from S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        
    Returns:
        File content as bytes
        
    Raises:
        ClientError: If S3 download fails
        BotoCoreError: If AWS service error occurs
    """
    try:
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "NoSuchKey":
            raise ValueError(f"File not found in S3: {key}")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"S3 download failed: {error_code} - {error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file from S3: {error_message}",
        )
    except BotoCoreError as e:
        logger.error(f"AWS service error during S3 download: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AWS service error: {str(e)}",
        )


def delete_file_from_s3(bucket: str, key: str) -> None:
    """
    Delete file from S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        
    Raises:
        ClientError: If S3 deletion fails
        BotoCoreError: If AWS service error occurs
    """
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=bucket, Key=key)
        logger.info(f"Successfully deleted file from S3: s3://{bucket}/{key}")
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"S3 deletion failed: {error_code} - {error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file from S3: {error_message}",
        )
    except BotoCoreError as e:
        logger.error(f"AWS service error during S3 deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AWS service error: {str(e)}",
        )

