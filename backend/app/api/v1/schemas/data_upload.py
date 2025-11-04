"""Data upload schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from app.models.data_upload import FileType, UploadStatus


class DataUploadResponse(BaseModel):
    """Data upload response schema."""

    upload_id: str
    user_id: str
    file_name: str
    file_size: int
    file_type: FileType
    status: UploadStatus
    validation_errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to response schema."""
        return cls(
            upload_id=str(obj.upload_id),
            user_id=str(obj.user_id),
            file_name=obj.file_name,
            file_size=obj.file_size,
            file_type=obj.file_type,
            status=obj.status,
            validation_errors=obj.validation_errors,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            processed_at=obj.processed_at,
        )

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "upload_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "file_name": "transactions.json",
                "file_size": 1024000,
                "file_type": "json",
                "status": "pending",
                "validation_errors": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": None,
                "processed_at": None
            }
        }


class DataUploadStatusResponse(BaseModel):
    """Data upload status response schema."""

    upload_id: str
    user_id: str
    file_name: str
    file_size: int
    file_type: FileType
    status: UploadStatus
    validation_errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to response schema."""
        return cls(
            upload_id=str(obj.upload_id),
            user_id=str(obj.user_id),
            file_name=obj.file_name,
            file_size=obj.file_size,
            file_type=obj.file_type,
            status=obj.status,
            validation_errors=obj.validation_errors,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            processed_at=obj.processed_at,
        )

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "upload_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "file_name": "transactions.json",
                "file_size": 1024000,
                "file_type": "json",
                "status": "pending",
                "validation_errors": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": None,
                "processed_at": None
            }
        }

