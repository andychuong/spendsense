"""User management schemas."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Union
from datetime import datetime
import uuid
from app.models.user import UserRole


class UserProfileResponse(BaseModel):
    """User profile response schema."""

    user_id: str
    email: Optional[str]
    phone_number: Optional[str]
    oauth_providers: Optional[dict] = Field(default_factory=dict, description="Linked OAuth providers")
    role: UserRole
    consent_status: bool
    consent_version: str
    created_at: datetime
    updated_at: Optional[datetime]

    @field_validator('user_id', mode='before')
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
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "phone_number": "+1234567890",
                "oauth_providers": {"google": True},
                "role": "user",
                "consent_status": True,
                "consent_version": "1.0",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class UserProfileUpdateRequest(BaseModel):
    """User profile update request schema."""

    email: Optional[EmailStr] = Field(None, description="User email address", examples=["user@example.com"])
    phone_number: Optional[str] = Field(None, description="User phone number", examples=["+1234567890"])

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "phone_number": "+1234567890"
            }
        }

