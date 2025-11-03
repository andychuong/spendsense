"""User profile model for storing behavioral profiles and personas."""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum

from app.database import Base


class PersonaId(int, enum.Enum):
    """Persona ID enumeration."""

    HIGH_UTILIZATION = 1
    VARIABLE_INCOME_BUDGETER = 2
    SUBSCRIPTION_HEAVY = 3
    SAVINGS_BUILDER = 4
    CUSTOM = 5


class UserProfile(Base):
    """User profile model for storing behavioral profiles and personas."""

    __tablename__ = "user_profiles"

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    persona_id = Column(Integer, nullable=False, index=True)
    persona_name = Column(String(100), nullable=False)
    signals_30d = Column(JSON, nullable=True)
    signals_180d = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Constraint to ensure persona_id is between 1 and 5
    __table_args__ = (
        CheckConstraint("persona_id >= 1 AND persona_id <= 5", name="check_persona_id_range"),
    )

    def __repr__(self) -> str:
        """String representation of UserProfile."""
        return f"<UserProfile(profile_id={self.profile_id}, user_id={self.user_id}, persona_id={self.persona_id})>"

