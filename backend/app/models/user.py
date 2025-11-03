"""User model."""

import uuid
from sqlalchemy import Column, String, Boolean, JSON, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""

    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    oauth_providers = Column(JSON, default=dict, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    consent_status = Column(Boolean, default=False, nullable=False)
    consent_version = Column(String(10), default="1.0", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(user_id={self.user_id}, email={self.email}, role={self.role})>"

