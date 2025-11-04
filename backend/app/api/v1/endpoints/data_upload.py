"""Data upload endpoints."""

import logging
import uuid
import sys
import os
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
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
    get_file_from_s3,
    MAX_FILE_SIZE,
)
from app.config import settings
from app.api.v1.schemas.data_upload import DataUploadResponse, DataUploadStatusResponse

logger = logging.getLogger(__name__)

# Import ingestion service
# Add service and backend directories to path for imports
# File is at: backend/app/api/v1/endpoints/data_upload.py
# We need: backend/ and service/ directories
_current_file = os.path.abspath(__file__)
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_file))))
_project_root = os.path.dirname(_backend_dir)
_service_dir = os.path.join(_project_root, "service")

# Add paths if not already there - backend must come first so service can import from it
for path in [_backend_dir, _service_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from app.ingestion.service import IngestionService
    logger.info("IngestionService imported successfully")
except ImportError as e:
    logger.warning(f"Failed to import IngestionService: {e}. File processing will be disabled.")
    IngestionService = None  # Will be checked before use

try:
    from app.features.persona_assignment import PersonaAssignmentService
    logger.info("PersonaAssignmentService imported successfully")
except ImportError as e:
    logger.warning(f"Failed to import PersonaAssignmentService: {e}. Persona assignment will be skipped.")
    PersonaAssignmentService = None  # Will be checked before use

router = APIRouter(prefix="/data", tags=["data"])


def process_upload_async(
    upload_id: uuid.UUID,
    user_id: uuid.UUID,
    file_content: bytes,
    file_type: str,
    s3_bucket: str,
    s3_key: str,
):
    """
    Process uploaded file asynchronously.

    This function runs in the background to:
    1. Update upload status to "processing"
    2. Call ingestion service to parse, validate, and store data
    3. Update upload status to "completed" or "failed" based on results

    Args:
        upload_id: Upload ID
        user_id: User ID
        file_content: File content as bytes
        file_type: File type ("json" or "csv")
        s3_bucket: S3 bucket name
        s3_key: S3 key
    """
    # Get a new database session for background processing
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        # Get upload record
        data_upload = db.query(DataUpload).filter(DataUpload.upload_id == upload_id).first()
        if not data_upload:
            logger.error(f"Upload not found: {upload_id}")
            return

        # Update status to processing
        data_upload.status = UploadStatus.PROCESSING.value.lower()
        db.commit()
        logger.info(f"Started processing upload {upload_id}")

        # Check if IngestionService is available
        if IngestionService is None:
            logger.warning("IngestionService not available. Upload will remain in processing status.")
            data_upload.status = UploadStatus.FAILED.value.lower()
            data_upload.validation_errors = {
                "error": "Processing service not available",
                "detail": "IngestionService could not be imported. Please check service layer installation."
            }
            db.commit()
            return

        # Initialize ingestion service
        ingestion_service = IngestionService(
            db_session=db,
            s3_bucket=settings.s3_bucket_analytics
        )

        # Process the file
        try:
            report = ingestion_service.ingest(
                file_content=file_content,
                file_type=file_type,
                user_id=user_id,
                upload_id=upload_id,
            )

            # Update status based on ingestion report
            if report.get("status") == "completed":
                data_upload.status = UploadStatus.COMPLETED.value.lower()
                data_upload.processed_at = datetime.utcnow()
                logger.info(
                    f"Processing completed for upload {upload_id}: "
                    f"{report.get('summary', {}).get('transactions_processed', 0)} transactions processed"
                )

                # Trigger persona assignment after successful ingestion
                # This creates/updates the UserProfile which is needed for the Dashboard
                if PersonaAssignmentService is not None:
                    try:
                        logger.info(f"Triggering persona assignment for user {user_id}")
                        persona_service = PersonaAssignmentService(db_session=db)
                        persona_result = persona_service.assign_persona(user_id)
                        logger.info(
                            f"Persona assigned for user {user_id}: {persona_result.get('persona_name')} "
                            f"(ID: {persona_result.get('persona_id')})"
                        )
                    except Exception as persona_error:
                        # Log error but don't fail the upload - persona can be assigned later
                        logger.warning(
                            f"Failed to assign persona for user {user_id}: {str(persona_error)}",
                            exc_info=True
                        )
                else:
                    logger.warning("PersonaAssignmentService not available. UserProfile will not be created.")

            elif report.get("status") == "failed":
                data_upload.status = UploadStatus.FAILED.value.lower()
                data_upload.validation_errors = {
                    "errors": report.get("errors", []),
                    "warnings": report.get("warnings", []),
                    "summary": report.get("summary", {}),
                }
                logger.error(
                    f"Processing failed for upload {upload_id}: "
                    f"{len(report.get('errors', []))} errors"
                )
            else:
                # Unexpected status
                data_upload.status = UploadStatus.FAILED.value.lower()
                data_upload.validation_errors = {
                    "error": "Unexpected processing status",
                    "status": report.get("status"),
                }
                logger.error(f"Unexpected processing status for upload {upload_id}: {report.get('status')}")

            db.commit()

        except Exception as e:
            logger.error(f"Error during ingestion for upload {upload_id}: {str(e)}", exc_info=True)
            data_upload.status = UploadStatus.FAILED.value.lower()
            data_upload.validation_errors = {
                "error": "Processing failed",
                "detail": str(e),
            }
            db.commit()

    except Exception as e:
        logger.error(f"Unexpected error in process_upload_async for upload {upload_id}: {str(e)}", exc_info=True)
        # Try to update status to failed
        try:
            data_upload = db.query(DataUpload).filter(DataUpload.upload_id == upload_id).first()
            if data_upload:
                data_upload.status = UploadStatus.FAILED.value.lower()
                data_upload.validation_errors = {
                    "error": "Unexpected processing error",
                    "detail": str(e),
                }
                db.commit()
        except Exception:
            pass  # If we can't update, log and continue
    finally:
        db.close()


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
    background_tasks: BackgroundTasks = BackgroundTasks(),
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
            file_type_enum = FileType(file_type_str.lower())  # Ensure lowercase
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
        # Explicitly pass lowercase string values to ensure PostgreSQL enum compatibility
        file_type_value = file_type_enum.value.lower()  # Ensure lowercase: "json" or "csv"
        status_value = UploadStatus.PENDING.value.lower()  # Ensure lowercase: "pending"

        logger.debug(f"Creating upload record with file_type={file_type_value}, status={status_value}")

        data_upload = DataUpload(
            upload_id=upload_id,
            user_id=current_user.user_id,
            file_name=file.filename,
            file_size=file_size,
            file_type=file_type_value,  # Lowercase string: "json" or "csv"
            s3_key=s3_key,
            s3_bucket=s3_bucket,
            status=status_value,  # Lowercase string: "pending"
        )

        try:
            db.add(data_upload)
            db.commit()
            db.refresh(data_upload)

            logger.info(
                f"Data upload created: upload_id={upload_id}, user_id={current_user.user_id}, "
                f"file_name={file.filename}, file_size={file_size}"
            )

            # Trigger async processing pipeline
            # Process in background so upload response returns immediately
            background_tasks.add_task(
                process_upload_async,
                upload_id=upload_id,
                user_id=current_user.user_id,
                file_content=file_content,
                file_type=file_type_value,
                s3_bucket=s3_bucket,
                s3_key=s3_key,
            )

            return DataUploadResponse.from_orm(data_upload)

        except IntegrityError as e:
            db.rollback()
            error_detail = str(e.orig) if hasattr(e, 'orig') else str(e)
            logger.error(f"Database integrity error creating data upload: {error_detail}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create upload record: {error_detail}",
            )
        except Exception as e:
            db.rollback()
            error_detail = str(e)
            logger.error(f"Unexpected error creating data upload: {error_detail}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create upload record: {error_detail}",
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
    "/uploads",
    response_model=List[DataUploadResponse],
    summary="Get upload history",
    description="Get upload history for the current user. Users can only view their own uploads. Operators and admins can view any user's uploads.",
    responses={
        200: {"description": "Upload history retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
    },
)
async def get_upload_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get upload history for the current user.

    Users can only view their own uploads.
    Operators and admins can view any user's uploads.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of data uploads ordered by creation date (newest first)
    """
    # Get uploads for the current user
    # Users can only view their own uploads
    # Operators and admins can view any user's uploads (for now, limit to own uploads)
    if current_user.role == "user":
        uploads = db.query(DataUpload).filter(
            DataUpload.user_id == current_user.user_id
        ).order_by(DataUpload.created_at.desc()).all()
    else:
        # For operators/admins, could show all uploads, but for now show own uploads
        uploads = db.query(DataUpload).filter(
            DataUpload.user_id == current_user.user_id
        ).order_by(DataUpload.created_at.desc()).all()

    return [DataUploadResponse.from_orm(upload) for upload in uploads]


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

