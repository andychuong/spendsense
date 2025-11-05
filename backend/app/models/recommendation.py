"""Recommendation model for storing user recommendations."""

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum

from app.database import Base


class RecommendationType(str, enum.Enum):
    """Recommendation type enumeration."""

    EDUCATION = "education"
    PARTNER_OFFER = "partner_offer"


class RecommendationStatus(str, enum.Enum):
    """Recommendation status enumeration."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Recommendation(Base):
    """Recommendation model for storing user recommendations."""

    __tablename__ = "recommendations"

    recommendation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    type = Column(Enum(RecommendationType, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    status = Column(Enum(RecommendationStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=RecommendationStatus.PENDING, nullable=False, index=True)
    decision_trace = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True, index=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    rejection_reason = Column(String(500), nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_recommendations_user_id_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        """String representation of Recommendation."""
        return f"<Recommendation(recommendation_id={self.recommendation_id}, user_id={self.user_id}, type={self.type})>"

