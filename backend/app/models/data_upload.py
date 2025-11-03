"""Data upload model for tracking file uploads."""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum

from app.database import Base


class FileType(str, enum.Enum):
    """File type enumeration."""

    JSON = "json"
    CSV = "csv"


class UploadStatus(str, enum.Enum):
    """Upload status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DataUpload(Base):
    """Data upload model for tracking user file uploads."""

    __tablename__ = "data_uploads"

    upload_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    s3_key = Column(String(500), nullable=False)
    s3_bucket = Column(String(255), nullable=False)
    status = Column(Enum(UploadStatus), default=UploadStatus.PENDING, nullable=False, index=True)
    validation_errors = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_data_uploads_user_id_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        """String representation of DataUpload."""
        return f"<DataUpload(upload_id={self.upload_id}, user_id={self.user_id}, status={self.status})>"

