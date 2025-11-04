"""Data upload model for tracking file uploads."""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Enum, Index, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID, ENUM
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


class FileTypeEnum(TypeDecorator):
    """Type decorator for FileType enum to ensure proper conversion."""

    impl = String(20)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Use String type - PostgreSQL enum validation happens at DB level."""
        return dialect.type_descriptor(String(20))

    def process_bind_param(self, value, dialect):
        """Convert enum to its lowercase value when binding to database."""
        if value is None:
            return None
        # Convert enum object to its lowercase value
        if isinstance(value, FileType):
            return value.value.lower()  # Return "json" or "csv"
        # Convert string to lowercase
        if isinstance(value, str):
            value_lower = value.lower()
            valid_values = [e.value for e in FileType]
            if value_lower in valid_values:
                return value_lower
            # Try to convert uppercase enum name to lowercase value
            try:
                enum_obj = FileType[value.upper()]
                return enum_obj.value.lower()
            except (KeyError, ValueError):
                return value_lower
        # Fallback: try to get value attribute and convert to lowercase
        return getattr(value, 'value', value).lower() if hasattr(value, 'value') else str(value).lower()

    def process_result_value(self, value, dialect):
        """Convert database value back to enum."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return FileType(value.lower())
            except ValueError:
                return value
        return value


class UploadStatusEnum(TypeDecorator):
    """Type decorator for UploadStatus enum to ensure proper conversion."""

    impl = String(20)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Use String type - PostgreSQL enum validation happens at DB level."""
        return dialect.type_descriptor(String(20))

    def process_bind_param(self, value, dialect):
        """Convert enum to its lowercase value when binding to database."""
        if value is None:
            return None
        # Convert enum object to its lowercase value
        if isinstance(value, UploadStatus):
            return value.value.lower()  # Return "pending", "processing", etc.
        # Convert string to lowercase
        if isinstance(value, str):
            value_lower = value.lower()
            valid_values = [e.value for e in UploadStatus]
            if value_lower in valid_values:
                return value_lower
            # Try to convert uppercase enum name to lowercase value
            try:
                enum_obj = UploadStatus[value.upper()]
                return enum_obj.value.lower()
            except (KeyError, ValueError):
                return value_lower
        # Fallback: try to get value attribute and convert to lowercase
        return getattr(value, 'value', value).lower() if hasattr(value, 'value') else str(value).lower()

    def process_result_value(self, value, dialect):
        """Convert database value back to enum."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return UploadStatus(value.lower())
            except ValueError:
                return value
        return value


class DataUpload(Base):
    """Data upload model for tracking user file uploads."""

    __tablename__ = "data_uploads"

    upload_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(FileTypeEnum(), nullable=False)
    s3_key = Column(String(500), nullable=False)
    s3_bucket = Column(String(255), nullable=False)
    status = Column(UploadStatusEnum(), default=UploadStatus.PENDING, nullable=False, index=True)
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

