"""RecommendationFeedback model for storing user feedback on recommendations."""

import uuid
from sqlalchemy import Column, Integer, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class RecommendationFeedback(Base):
    """Model for storing user feedback on recommendations."""

    __tablename__ = "recommendation_feedback"

    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.recommendation_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    helpful = Column(Boolean, nullable=True)  # True/False
    comment = Column(Text, nullable=True)  # Optional text comment
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("ix_feedback_user_recommendation", "user_id", "recommendation_id", unique=True),
    )

    def __repr__(self) -> str:
        """String representation of RecommendationFeedback."""
        return f"<RecommendationFeedback(feedback_id={self.feedback_id}, recommendation_id={self.recommendation_id}, rating={self.rating})>"

