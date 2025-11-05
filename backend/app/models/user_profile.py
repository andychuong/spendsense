"""User profile model for storing behavioral profiles."""

import uuid
from sqlalchemy import Column, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class UserProfile(Base):
    """User profile model for storing behavioral profiles."""

    __tablename__ = "user_profiles"

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    signals_30d = Column(JSON, nullable=True)
    signals_180d = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        """String representation of UserProfile."""
        return f"<UserProfile(profile_id={self.profile_id}, user_id={self.user_id})>"

