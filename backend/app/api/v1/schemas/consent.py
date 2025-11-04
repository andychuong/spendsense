"""Consent management schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConsentGrantRequest(BaseModel):
    """Request schema for granting consent."""

    consent_version: str = Field(
        default="1.0",
        description="Version of the consent/terms of service the user is agreeing to"
    )
    tos_accepted: bool = Field(
        True,
        description="Whether the user has accepted the Terms of Service"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "consent_version": "1.0",
                "tos_accepted": True
            }
        }


class ConsentStatusResponse(BaseModel):
    """Response schema for consent status."""

    user_id: str
    consent_status: bool
    consent_version: str
    consent_granted_at: Optional[datetime] = None
    consent_revoked_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "consent_status": True,
                "consent_version": "1.0",
                "consent_granted_at": "2024-01-15T10:30:00Z",
                "consent_revoked_at": None,
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class ConsentRevokeRequest(BaseModel):
    """Request schema for revoking consent."""

    delete_data: bool = Field(
        default=False,
        description="Whether to delete all user data when revoking consent"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "delete_data": False
            }
        }

