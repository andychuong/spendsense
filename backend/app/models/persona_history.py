"""Persona history model for tracking persona assignments over time."""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class PersonaHistory(Base):
    """Persona history model for tracking persona assignments over time."""

    __tablename__ = "persona_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    persona_id = Column(Integer, nullable=False)
    persona_name = Column(String(100), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    signals = Column(JSON, nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_persona_history_user_id_assigned_at", "user_id", "assigned_at"),
    )

    def __repr__(self) -> str:
        """String representation of PersonaHistory."""
        return f"<PersonaHistory(history_id={self.history_id}, user_id={self.user_id}, persona_id={self.persona_id})>"

