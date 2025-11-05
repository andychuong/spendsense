import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserPersonaAssignment(Base):
    """Association table for many-to-many relationship between users and personas."""

    __tablename__ = "user_persona_assignments"

    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    persona_id = Column(Integer, ForeignKey("personas.persona_id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rationale = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="persona_assignments")
    persona = relationship("Persona", back_populates="assignments")

    __table_args__ = (
        Index("ix_user_persona_assignments_user_id_persona_id", "user_id", "persona_id", unique=True),
    )

    def __repr__(self) -> str:
        """String representation of UserPersonaAssignment."""
        return f"<UserPersonaAssignment(user_id={self.user_id}, persona_id={self.persona_id})>"

