"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class UserRegisterRequest(BaseModel):
    """User registration request schema."""

    email: EmailStr = Field(..., description="User email address", examples=["user@example.com"])
    password: str = Field(..., min_length=12, description="User password", examples=["SecurePass123!"])

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength.
        
        Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")
        
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError("Password must contain at least one special character")
        
        return v


class UserRegisterResponse(BaseModel):
    """User registration response schema."""

    user_id: str
    email: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request schema."""

    email: EmailStr = Field(..., description="User email address", examples=["user@example.com"])
    password: str = Field(..., description="User password", examples=["SecurePass123!"])

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class UserLoginResponse(BaseModel):
    """User login response schema."""

    user_id: str
    email: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema."""

    refresh_token: str = Field(..., description="Refresh token", examples=["eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."])

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class TokenRefreshResponse(BaseModel):
    """Token refresh response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class PhoneVerificationRequest(BaseModel):
    """Phone verification request schema."""

    phone: str = Field(..., description="Phone number in E.164 format (e.g., +1234567890)", examples=["+1234567890"])

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "phone": "+1234567890"
            }
        }


class PhoneVerificationRequestResponse(BaseModel):
    """Phone verification request response schema."""

    message: str = "Verification code sent successfully"
    phone: str = Field(..., description="Normalized phone number in E.164 format")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Verification code sent successfully",
                "phone": "+1234567890"
            }
        }


class PhoneVerificationVerifyRequest(BaseModel):
    """Phone verification verify request schema."""

    phone: str = Field(..., description="Phone number in E.164 format (e.g., +1234567890)", examples=["+1234567890"])
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code", examples=["123456"])

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "phone": "+1234567890",
                "code": "123456"
            }
        }


class PhoneVerificationVerifyResponse(BaseModel):
    """Phone verification verify response schema."""

    user_id: str
    phone: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = Field(..., description="True if user was just created, False if existing user logged in")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "phone": "+1234567890",
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "is_new_user": True
            }
        }


class OAuthAuthorizeResponse(BaseModel):
    """OAuth authorization response schema."""

    authorize_url: str = Field(..., description="OAuth authorization URL to redirect user to")
    state: str = Field(..., description="OAuth state parameter for CSRF protection")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
                "state": "abc123def456"
            }
        }


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response schema."""

    user_id: str
    email: Optional[str] = None
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = Field(..., description="True if user was just created, False if existing user logged in")
    provider: str = Field(..., description="OAuth provider name (google, github, facebook, apple)")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "is_new_user": True,
                "provider": "google"
            }
        }


class OAuthLinkRequest(BaseModel):
    """OAuth link request schema."""

    code: str = Field(..., description="Authorization code from OAuth callback")
    state: str = Field(..., description="OAuth state parameter for CSRF protection")
    redirect_uri: str = Field(..., description="Callback URL used in authorization")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "code": "4/0AeanS...",
                "state": "abc123def456",
                "redirect_uri": "http://localhost:3000/auth/oauth/callback"
            }
        }


class OAuthLinkResponse(BaseModel):
    """OAuth link response schema."""

    message: str = "OAuth provider linked successfully"
    provider: str = Field(..., description="OAuth provider name (google, github, facebook, apple)")
    merged_account: bool = Field(
        default=False,
        description="True if accounts were merged, False if provider was just linked"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "OAuth provider linked successfully",
                "provider": "google",
                "merged_account": False
            }
        }


class PhoneLinkRequest(BaseModel):
    """Phone link request schema."""

    phone: str = Field(..., description="Phone number in E.164 format (e.g., +1234567890)", examples=["+1234567890"])
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code", examples=["123456"])

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "phone": "+1234567890",
                "code": "123456"
            }
        }


class PhoneLinkResponse(BaseModel):
    """Phone link response schema."""

    message: str = "Phone number linked successfully"
    phone: str = Field(..., description="Normalized phone number in E.164 format")
    merged_account: bool = Field(
        default=False,
        description="True if accounts were merged, False if phone was just linked"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Phone number linked successfully",
                "phone": "+1234567890",
                "merged_account": False
            }
        }


class UnlinkResponse(BaseModel):
    """Unlink response schema."""

    message: str = Field(..., description="Success message")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "OAuth provider unlinked successfully"
            }
        }

