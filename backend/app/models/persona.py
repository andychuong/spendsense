from sqlalchemy import Column, String, Integer, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PersonaId(int, enum.Enum):
    """Persona ID enumeration."""

    HIGH_UTILIZATION = 1
    VARIABLE_INCOME_BUDGETER = 2
    SUBSCRIPTION_HEAVY = 3
    SAVINGS_BUILDER = 4
    BALANCED_SPENDER = 5  # Renamed from CUSTOM
    DEBT_CONSOLIDATOR = 6
    EMERGENCY_FUND_SEEKER = 7
    FOODIE = 8
    FREQUENT_TRAVELER = 9
    HOME_IMPROVER = 10


class Persona(Base):
    """Model for persona definitions."""

    __tablename__ = "personas"

    persona_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)

    # Relationship to user_persona_assignments
    assignments = relationship("UserPersonaAssignment", back_populates="persona")

    __table_args__ = (
        Index("ix_personas_name", "name"),
    )

    def __repr__(self) -> str:
        """String representation of Persona."""
        return f"<Persona(persona_id={self.persona_id}, name='{self.name}')>"

