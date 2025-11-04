"""Recommendations schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class RecommendationResponse(BaseModel):
    """Recommendation response schema."""

    recommendation_id: str
    user_id: str
    type: str  # "education" or "partner_offer"
    title: str
    content: str
    rationale: str
    status: str  # "pending", "approved", "rejected"
    decision_trace: Optional[Dict[str, Any]] = Field(None, description="Decision trace data")
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    # Partner offer specific fields (extracted from decision_trace or stored separately)
    eligibility_status: Optional[str] = Field(None, description="eligible, ineligible, or pending")
    eligibility_reason: Optional[str] = None
    partner_name: Optional[str] = None
    partner_logo_url: Optional[str] = None
    offer_details: Optional[Dict[str, Any]] = None

    @field_validator('recommendation_id', 'user_id', 'approved_by', 'rejected_by', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string if needed."""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "recommendation_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "education",
                "title": "Understanding Credit Utilization",
                "content": "Credit utilization is the percentage of your credit limit that you're using...",
                "rationale": "Based on your credit card utilization of 65%, understanding how utilization affects your credit score can help you improve your financial health.",
                "status": "approved",
                "decision_trace": {
                    "persona_assignment": {"persona_id": 1, "persona_name": "High Utilization"},
                    "detected_signals": {"credit": {"utilization": 0.65}}
                },
                "created_at": "2024-01-15T10:30:00Z",
                "approved_at": "2024-01-15T11:00:00Z",
                "eligibility_status": "eligible",
                "eligibility_reason": "User meets all eligibility requirements"
            }
        }


class RecommendationsListResponse(BaseModel):
    """Recommendations list response schema."""

    items: List[RecommendationResponse]
    total: int
    skip: int = 0
    limit: int = 100

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "recommendation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "type": "education",
                        "title": "Understanding Credit Utilization",
                        "content": "Credit utilization is...",
                        "rationale": "Based on your credit card utilization...",
                        "status": "approved",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }


class RecommendationFeedbackRequest(BaseModel):
    """Recommendation feedback request schema."""

    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    helpful: Optional[bool] = Field(None, description="Whether the recommendation was helpful")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "rating": 5,
                "helpful": True,
                "comment": "Very helpful information about credit utilization."
            }
        }


class RecommendationRejectRequest(BaseModel):
    """Recommendation reject request schema."""

    reason: str = Field(..., min_length=1, max_length=500, description="Reason for rejection")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "reason": "Content does not match user's financial situation."
            }
        }


class RecommendationModifyRequest(BaseModel):
    """Recommendation modify request schema."""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated title")
    content: Optional[str] = Field(None, min_length=1, description="Updated content")
    rationale: Optional[str] = Field(None, min_length=1, description="Updated rationale")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "title": "Updated Title",
                "content": "Updated content...",
                "rationale": "Updated rationale..."
            }
        }


