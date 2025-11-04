"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class UserRegisterRequest(BaseModel):
    """User registration request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=12, description="User password")

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


class UserLoginRequest(BaseModel):
    """User login request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserLoginResponse(BaseModel):
    """User login response schema."""

    user_id: str
    email: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema."""

    refresh_token: str = Field(..., description="Refresh token")


class TokenRefreshResponse(BaseModel):
    """Token refresh response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PhoneVerificationRequest(BaseModel):
    """Phone verification request schema."""

    phone: str = Field(..., description="Phone number in E.164 format (e.g., +1234567890)")


class PhoneVerificationRequestResponse(BaseModel):
    """Phone verification request response schema."""

    message: str = "Verification code sent successfully"
    phone: str = Field(..., description="Normalized phone number in E.164 format")


class PhoneVerificationVerifyRequest(BaseModel):
    """Phone verification verify request schema."""

    phone: str = Field(..., description="Phone number in E.164 format (e.g., +1234567890)")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class PhoneVerificationVerifyResponse(BaseModel):
    """Phone verification verify response schema."""

    user_id: str
    phone: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = Field(..., description="True if user was just created, False if existing user logged in")


class OAuthAuthorizeResponse(BaseModel):
    """OAuth authorization response schema."""

    authorize_url: str = Field(..., description="OAuth authorization URL to redirect user to")
    state: str = Field(..., description="OAuth state parameter for CSRF protection")


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response schema."""

    user_id: str
    email: Optional[str] = None
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = Field(..., description="True if user was just created, False if existing user logged in")
    provider: str = Field(..., description="OAuth provider name (google, github, facebook, apple)")

