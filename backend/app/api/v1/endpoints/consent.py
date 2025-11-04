"""Consent management endpoints."""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.cache_service import invalidate_all_user_caches
from app.models.user import User
from app.models.data_upload import DataUpload
from app.models.recommendation import Recommendation
from app.models.user_profile import UserProfile
from app.models.persona_history import PersonaHistory
from app.api.v1.schemas.consent import (
    ConsentGrantRequest,
    ConsentStatusResponse,
    ConsentRevokeRequest,
)

router = APIRouter(prefix="/consent", tags=["consent"])

logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=ConsentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Grant consent",
    description="Grant consent for data processing. Requires explicit opt-in (TOS acceptance). Stores consent with timestamp and version.",
    responses={
        200: {"description": "Consent granted successfully"},
        400: {"description": "Terms of Service must be accepted"},
        401: {"description": "Unauthorized - authentication required"},
    },
)
async def grant_consent(
    request: ConsentGrantRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Grant consent for data processing.
    
    This endpoint:
    1. Requires explicit opt-in (TOS acceptance)
    2. Stores consent with timestamp and version
    3. Logs consent grant event
    
    Args:
        request: Consent grant request with version and TOS acceptance
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Consent status response
        
    Raises:
        HTTPException: If TOS not accepted or validation fails
    """
    # Require explicit opt-in (TOS acceptance)
    if not request.tos_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms of Service must be accepted to grant consent"
        )
    
    # Update user consent status
    current_user.consent_status = True
    current_user.consent_version = request.consent_version
    current_user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(current_user)
        
        # Log consent grant event
        logger.info(
            f"Consent granted: User {current_user.user_id} granted consent "
            f"(version: {request.consent_version})"
        )
        
        return ConsentStatusResponse(
            user_id=str(current_user.user_id),
            consent_status=current_user.consent_status,
            consent_version=current_user.consent_version,
            consent_granted_at=current_user.updated_at,
            updated_at=current_user.updated_at,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error granting consent for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant consent"
        )


@router.get(
    "",
    response_model=ConsentStatusResponse,
    summary="Get consent status",
    description="Get the current user's consent status for data processing.",
    responses={
        200: {"description": "Consent status retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
    },
)
async def get_consent_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's consent status.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Consent status response
    """
    # Get consent status from user record
    # Note: We don't store separate consent_granted_at/revoked_at timestamps yet
    # This could be added in a future migration if needed
    
    return ConsentStatusResponse(
        user_id=str(current_user.user_id),
        consent_status=current_user.consent_status,
        consent_version=current_user.consent_version,
        consent_granted_at=current_user.updated_at if current_user.consent_status else None,
        consent_revoked_at=current_user.updated_at if not current_user.consent_status else None,
        updated_at=current_user.updated_at,
    )


@router.delete(
    "",
    response_model=ConsentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke consent",
    description="Revoke consent for data processing. Optionally delete all user data. Blocks future recommendations.",
    responses={
        200: {"description": "Consent revoked successfully"},
        401: {"description": "Unauthorized - authentication required"},
        500: {"description": "Internal server error - revocation failed"},
    },
)
async def revoke_consent(
    request: ConsentRevokeRequest = ConsentRevokeRequest(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Revoke consent for data processing.
    
    This endpoint:
    1. Allows users to revoke consent at any time
    2. Optionally deletes all user data if requested
    3. Blocks future recommendations (consent_status = False)
    4. Logs consent revocation event
    
    Args:
        request: Consent revoke request with optional data deletion
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Consent status response
        
    Raises:
        HTTPException: If revocation fails
    """
    # Update user consent status
    current_user.consent_status = False
    current_user.updated_at = datetime.utcnow()
    
    # Optionally delete all user data
    if request.delete_data:
        try:
            # Delete user data (excluding user record itself)
            # DataUpload records
            db.query(DataUpload).filter(
                DataUpload.user_id == current_user.user_id
            ).delete()
            
            # Recommendation records
            db.query(Recommendation).filter(
                Recommendation.user_id == current_user.user_id
            ).delete()
            
            # UserProfile records
            db.query(UserProfile).filter(
                UserProfile.user_id == current_user.user_id
            ).delete()
            
            # PersonaHistory records
            db.query(PersonaHistory).filter(
                PersonaHistory.user_id == current_user.user_id
            ).delete()
            
            logger.info(
                f"Consent revoked with data deletion: User {current_user.user_id} "
                f"revoked consent and deleted all user data"
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Error deleting user data for user {current_user.user_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user data"
            )
    else:
        logger.info(
            f"Consent revoked: User {current_user.user_id} revoked consent "
            f"(data deletion not requested)"
        )
    
    try:
        db.commit()
        db.refresh(current_user)
        
        # Invalidate all user caches (consent affects recommendations)
        invalidate_all_user_caches(current_user.user_id)
        
        return ConsentStatusResponse(
            user_id=str(current_user.user_id),
            consent_status=current_user.consent_status,
            consent_version=current_user.consent_version,
            consent_revoked_at=current_user.updated_at,
            updated_at=current_user.updated_at,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking consent for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke consent"
        )


def check_consent(user: User) -> bool:
    """
    Check if user has granted consent for data processing.
    
    This function should be used before processing user data or generating recommendations.
    
    Args:
        user: User object to check
        
    Returns:
        True if user has granted consent, False otherwise
    """
    return user.consent_status is True


def require_consent(user: User) -> None:
    """
    Require consent for data processing.
    
    Raises HTTPException if user has not granted consent.
    
    Args:
        user: User object to check
        
    Raises:
        HTTPException: 403 Forbidden if consent not granted
    """
    if not check_consent(user):
        logger.warning(
            f"Consent check failed: User {user.user_id} attempted to access "
            f"data processing without consent"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required for data processing. Please grant consent first."
        )

