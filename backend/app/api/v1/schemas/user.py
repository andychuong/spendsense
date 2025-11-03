"""User management schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserProfileResponse(BaseModel):
    """User profile response schema."""

    user_id: str
    email: Optional[str]
    phone_number: Optional[str]
    role: UserRole
    consent_status: bool
    consent_version: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    """User profile update request schema."""

    email: Optional[EmailStr] = Field(None, description="User email address")
    phone_number: Optional[str] = Field(None, description="User phone number")

