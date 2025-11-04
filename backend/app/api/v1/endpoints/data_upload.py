"""Data upload endpoints."""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.data_upload import DataUpload, FileType, UploadStatus
from app.core.s3_service import (
    validate_file_type,
    validate_file_size,
    generate_s3_key,
    upload_file_to_s3,
    MAX_FILE_SIZE,
)
from app.config import settings
from app.api.v1.schemas.data_upload import DataUploadResponse, DataUploadStatusResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["data"])


@router.post(
    "/upload",
    response_model=DataUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload transaction data file",
    description="Upload a transaction data file in JSON or CSV format. Maximum file size: 10MB. File is stored in S3 and metadata is saved in the database.",
    responses={
        201: {"description": "File uploaded successfully"},
        400: {"description": "Invalid file format or size exceeded"},
        401: {"description": "Unauthorized - authentication required"},
        500: {"description": "Internal server error - upload failed"},
    },
)
async def upload_data_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload transaction data file.
    
    Supports JSON and CSV file formats.
    Maximum file size: 10MB.
    
    Args:
        file: Uploaded file
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Data upload response with upload_id and status
    """
    try:
        # Validate file type
        try:
            file_type_str = validate_file_type(file.filename, file.content_type)
            file_type = FileType(file_type_str)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        try:
            validate_file_size(file_size)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        
        # Generate upload ID and S3 key
        upload_id = uuid.uuid4()
        s3_key = generate_s3_key(current_user.user_id, upload_id, file.filename)
        s3_bucket = settings.s3_bucket_data
        
        # Upload file to S3
        try:
            upload_file_to_s3(
                file_content,
                s3_bucket,
                s3_key,
                content_type=file.content_type,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to S3: {str(e)}",
            )
        
        # Create data upload record in database
        data_upload = DataUpload(
            upload_id=upload_id,
            user_id=current_user.user_id,
            file_name=file.filename,
            file_size=file_size,
            file_type=file_type,
            s3_key=s3_key,
            s3_bucket=s3_bucket,
            status=UploadStatus.PENDING,
        )
        
        try:
            db.add(data_upload)
            db.commit()
            db.refresh(data_upload)
            
            logger.info(
                f"Data upload created: upload_id={upload_id}, user_id={current_user.user_id}, "
                f"file_name={file.filename}, file_size={file_size}"
            )
            
            # TODO: Trigger async processing pipeline
            # This will be implemented in Phase 2 (Service Layer)
            
            return DataUploadResponse.from_orm(data_upload)
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database error creating data upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create upload record",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating data upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create upload record",
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_data_file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/upload/{upload_id}",
    response_model=DataUploadStatusResponse,
    summary="Get upload status",
    description="Get the status of a data upload by upload ID. Users can only view their own uploads. Operators and admins can view any user's uploads.",
    responses={
        200: {"description": "Upload status retrieved successfully"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Upload not found"},
    },
)
async def get_upload_status(
    upload_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get upload status by upload ID.
    
    Users can only view their own uploads.
    Operators and admins can view any user's uploads.
    
    Args:
        upload_id: Upload ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Data upload status response
    """
    # Get upload record
    data_upload = db.query(DataUpload).filter(DataUpload.upload_id == upload_id).first()
    
    if not data_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )
    
    # Check authorization: users can only view their own uploads
    # Operators and admins can view any user's uploads
    if current_user.role == "user" and data_upload.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this upload",
        )
    
    return DataUploadStatusResponse.from_orm(data_upload)

