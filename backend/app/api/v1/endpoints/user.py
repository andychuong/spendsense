"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.api.v1.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile
    """
    return UserProfileResponse.model_validate(current_user)


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    request: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update current user profile.
    
    Args:
        request: User profile update request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user profile
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Update email if provided
    if request.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(
            User.email == request.email,
            User.user_id != current_user.user_id,
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = request.email
    
    # Update phone number if provided
    if request.phone_number is not None:
        # Check if phone number is already taken by another user
        existing_user = db.query(User).filter(
            User.phone_number == request.phone_number,
            User.user_id != current_user.user_id,
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        current_user.phone_number = request.phone_number
    
    try:
        db.commit()
        db.refresh(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone number already registered"
        )
    
    return UserProfileResponse.model_validate(current_user)

