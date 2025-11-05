"""User management schemas."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Union, Dict, Any, List
from datetime import datetime
import uuid
from decimal import Decimal
from app.models.user import UserRole


class UserProfileResponse(BaseModel):
    """User profile response schema."""

    user_id: str
    name: Optional[str] = Field(None, description="User's full name")
    email: Optional[str]
    phone_number: Optional[str]
    oauth_providers: Optional[dict] = Field(default_factory=dict, description="Linked OAuth providers")
    role: UserRole
    consent_status: bool
    consent_version: str
    monthly_income: Optional[float] = Field(None, description="User's monthly income (manually set or calculated from transactions)")
    created_at: datetime
    updated_at: Optional[datetime]

    @field_validator('user_id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string if needed."""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('monthly_income', mode='before')
    @classmethod
    def convert_decimal_to_float(cls, v):
        """Convert Decimal to float if needed."""
        if isinstance(v, Decimal):
            return float(v)
        return v

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
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
    monthly_income: Optional[float] = Field(None, description="User's monthly income", ge=0, examples=[5000.0])

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "phone_number": "+1234567890",
                "monthly_income": 5000.0
            }
        }


class BehavioralSignals(BaseModel):
    """Behavioral signals schema for 30-day or 180-day window."""

    subscriptions: Optional[Dict[str, Any]] = Field(None, description="Subscription detection signals")
    savings: Optional[Dict[str, Any]] = Field(None, description="Savings pattern signals")
    credit: Optional[Dict[str, Any]] = Field(None, description="Credit utilization signals")
    income: Optional[Dict[str, Any]] = Field(None, description="Income stability signals")


class BehavioralProfileResponse(BaseModel):
    """Behavioral profile response schema. Persona info only included for operators/admins."""

    profile_id: str
    user_id: str
    persona_id: Optional[int] = Field(None, description="Persona ID (operator/admin only)")
    persona_name: Optional[str] = Field(None, description="Persona name (operator/admin only)")
    signals_30d: Optional[BehavioralSignals] = Field(None, description="30-day behavioral signals")
    signals_180d: Optional[BehavioralSignals] = Field(None, description="180-day behavioral signals")
    updated_at: datetime

    @field_validator('profile_id', 'user_id', mode='before')
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
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "persona_id": 1,
                "persona_name": "High Utilization",
                "signals_30d": {
                    "subscriptions": {"recurring_merchants": 3},
                    "credit": {"utilization": 0.65}
                },
                "signals_180d": {
                    "subscriptions": {"recurring_merchants": 5},
                    "credit": {"utilization": 0.70}
                },
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class PersonaHistoryEntry(BaseModel):
    """Persona history entry schema."""

    history_id: str
    user_id: str
    persona_id: int
    persona_name: str
    assigned_at: datetime
    signals: Optional[Dict[str, Any]] = Field(None, description="Signals at time of assignment")

    @field_validator('history_id', 'user_id', mode='before')
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
                "history_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "persona_id": 1,
                "persona_name": "High Utilization",
                "assigned_at": "2024-01-15T10:30:00Z",
                "signals": {"credit": {"utilization": 0.65}}
            }
        }


class PersonaHistoryResponse(BaseModel):
    """Persona history response schema."""

    items: List[PersonaHistoryEntry]
    total: int
    skip: int = 0
    limit: int = 100

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "history_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "persona_id": 1,
                        "persona_name": "High Utilization",
                        "assigned_at": "2024-01-15T10:30:00Z",
                        "signals": {"credit": {"utilization": 0.65}}
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }

