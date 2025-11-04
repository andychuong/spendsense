"""API v1 schemas."""

from app.api.v1.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from app.api.v1.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
)
from app.api.v1.schemas.consent import (
    ConsentGrantRequest,
    ConsentStatusResponse,
    ConsentRevokeRequest,
)
from app.api.v1.schemas.data_upload import (
    DataUploadResponse,
    DataUploadStatusResponse,
)

__all__ = [
    "UserRegisterRequest",
    "UserRegisterResponse",
    "UserLoginRequest",
    "UserLoginResponse",
    "TokenRefreshRequest",
    "TokenRefreshResponse",
    "UserProfileResponse",
    "UserProfileUpdateRequest",
    "ConsentGrantRequest",
    "ConsentStatusResponse",
    "ConsentRevokeRequest",
    "DataUploadResponse",
    "DataUploadStatusResponse",
]

