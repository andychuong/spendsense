"""User management endpoints."""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.database import get_db
from app.core.dependencies import (
    get_current_active_user,
    require_owner_or_operator_factory,
    check_user_access,
)
from app.core.cache_service import invalidate_all_user_caches
from app.models.user import User
from app.models.session import Session as SessionModel
from app.models.data_upload import DataUpload
from app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus
from app.models.user_profile import UserProfile
from app.models.persona_history import PersonaHistory
from app.api.v1.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    BehavioralProfileResponse,
    PersonaHistoryResponse,
    PersonaHistoryEntry,
    BehavioralSignals,
)
from app.api.v1.schemas.recommendations import (
    RecommendationResponse,
    RecommendationsListResponse,
)
from app.core.cache_service import cache_profile_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Retrieve the profile of the currently authenticated user.",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
    },
)
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


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user. Can update email and/or phone number.",
    responses={
        200: {"description": "User profile updated successfully"},
        400: {"description": "Email or phone number already registered"},
        401: {"description": "Unauthorized - authentication required"},
    },
)
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

    # Update monthly income if provided
    if request.monthly_income is not None:
        if request.monthly_income < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monthly income cannot be negative"
            )
        current_user.monthly_income = request.monthly_income

    try:
        db.commit()
        db.refresh(current_user)

        # Log profile update
        changes = []
        if request.email is not None:
            changes.append(f"email={request.email}")
        if request.phone_number is not None:
            changes.append(f"phone_number={request.phone_number}")
        if request.monthly_income is not None:
            changes.append(f"monthly_income={request.monthly_income}")

        logger.info(
            f"Profile updated: User {current_user.user_id} updated profile "
            f"({', '.join(changes) if changes else 'no changes'})"
        )

        # Invalidate user profile cache
        invalidate_all_user_caches(current_user.user_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone number already registered"
        )

    return UserProfileResponse.model_validate(current_user)


@router.get(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Get user profile by ID",
    description="Get a user profile by user ID. Users can access their own profile. Operators and admins can access any user's profile.",
    responses={
        200: {"description": "User profile retrieved successfully"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "User not found"},
    },
)
async def get_user_profile(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get user profile by user ID.

    Resource-level authorization:
    - Users can access their own profile
    - Operators and admins can access any user's profile

    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        User profile

    Raises:
        HTTPException: 403 Forbidden if user doesn't have permission
        HTTPException: 404 Not Found if user doesn't exist
    """
    # Find user first
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check resource access (users can access own data, operators can access any)
    # Operators and admins must respect user consent when accessing other users' data
    if not check_user_access(user_id, current_user, db=db, check_consent=True):
        # Check if it's a consent issue
        if not user.consent_status and current_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's data. User has revoked consent or not granted consent."
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's profile"
        )

    return UserProfileResponse.model_validate(user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user account",
    description="Delete the current user's account and all associated data. This action is irreversible and deletes all user data including sessions, uploads, recommendations, profiles, and persona history.",
    responses={
        204: {"description": "Account deleted successfully"},
        401: {"description": "Unauthorized - authentication required"},
        500: {"description": "Internal server error - deletion failed"},
    },
)
async def delete_current_user_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete current user account and all associated data.

    This endpoint:
    1. Deletes all user-related data (sessions, data uploads, recommendations, profiles, persona history)
    2. Deletes the user record itself
    3. Logs the account deletion event

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        HTTPException: If deletion fails
    """
    user_id = current_user.user_id

    try:
        # Delete all user-related data
        # Sessions (refresh tokens)
        db.query(SessionModel).filter(
            SessionModel.user_id == user_id
        ).delete()

        # DataUpload records
        db.query(DataUpload).filter(
            DataUpload.user_id == user_id
        ).delete()

        # Recommendation records (including those approved/rejected by this user as operator)
        # First, update recommendations that were approved/rejected by this user
        db.query(Recommendation).filter(
            Recommendation.approved_by == user_id
        ).update({"approved_by": None})
        db.query(Recommendation).filter(
            Recommendation.rejected_by == user_id
        ).update({"rejected_by": None})

        # Then delete recommendations owned by this user
        db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).delete()

        # UserProfile records
        db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).delete()

        # PersonaHistory records
        db.query(PersonaHistory).filter(
            PersonaHistory.user_id == user_id
        ).delete()

        # Delete the user record itself
        db.delete(current_user)

        # Commit all deletions
        db.commit()

        # Invalidate all user caches
        invalidate_all_user_caches(user_id)

        # Log account deletion event
        logger.info(
            f"Account deleted: User {user_id} deleted their account and all associated data"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user account {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )

    # Return 204 No Content (no response body)
    return None


@router.get(
    "/{user_id}/profile",
    response_model=BehavioralProfileResponse,
    summary="Get user behavioral profile",
    description="Get behavioral profile with detected signals and persona assignment. Users can access their own profile. Operators and admins can access any user's profile.",
    responses={
        200: {"description": "Behavioral profile retrieved successfully"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "User profile not found"},
    },
)
@cache_profile_response
async def get_user_behavioral_profile(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get user behavioral profile with detected signals and persona assignment.

    Resource-level authorization:
    - Users can access their own profile
    - Operators and admins can access any user's profile

    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Behavioral profile with signals and persona

    Raises:
        HTTPException: 403 Forbidden if user doesn't have permission
        HTTPException: 404 Not Found if profile doesn't exist
    """
    # Check resource access (users can access own data, operators can access any)
    # Operators and admins must respect user consent when accessing other users' data
    if not check_user_access(user_id, current_user, db=db, check_consent=True):
        # Check if it's a consent issue
        user = db.query(User).filter(User.user_id == user_id).first()
        if user and not user.consent_status and current_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's data. User has revoked consent or not granted consent."
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's profile"
        )

    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behavioral profile not found for this user"
        )

    # Convert signals JSON to BehavioralSignals objects
    signals_30d = None
    if profile.signals_30d:
        signals_30d = BehavioralSignals(**profile.signals_30d)

    signals_180d = None
    if profile.signals_180d:
        signals_180d = BehavioralSignals(**profile.signals_180d)

    return BehavioralProfileResponse(
        profile_id=str(profile.profile_id),
        user_id=str(profile.user_id),
        persona_id=profile.persona_id,
        persona_name=profile.persona_name,
        signals_30d=signals_30d,
        signals_180d=signals_180d,
        updated_at=profile.updated_at,
    )


@router.get(
    "/{user_id}/persona-history",
    response_model=PersonaHistoryResponse,
    summary="Get user persona history",
    description="Get persona assignment history for a user. Users can access their own history. Operators and admins can access any user's history.",
    responses={
        200: {"description": "Persona history retrieved successfully"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "User not found"},
    },
)
async def get_user_persona_history(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
):
    """
    Get persona assignment history for a user.

    Resource-level authorization:
    - Users can access their own history
    - Operators and admins can access any user's history

    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        Persona history with pagination info

    Raises:
        HTTPException: 403 Forbidden if user doesn't have permission
        HTTPException: 404 Not Found if user doesn't exist
    """
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check resource access (users can access own data, operators can access any)
    # Operators and admins must respect user consent when accessing other users' data
    if not check_user_access(user_id, current_user, db=db, check_consent=True):
        # Check if it's a consent issue
        if not user.consent_status and current_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's data. User has revoked consent or not granted consent."
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's persona history"
        )

    # Get total count
    total = db.query(PersonaHistory).filter(PersonaHistory.user_id == user_id).count()

    # Get persona history ordered by assigned_at descending
    history_records = (
        db.query(PersonaHistory)
        .filter(PersonaHistory.user_id == user_id)
        .order_by(PersonaHistory.assigned_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Convert to response format
    items = [
        PersonaHistoryEntry.model_validate(record) for record in history_records
    ]

    return PersonaHistoryResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}/recommendations",
    response_model=RecommendationsListResponse,
    summary="Get recommendations for a user",
    description="Get recommendations for a specific user. Users can access their own recommendations. Operators and admins can access any user's recommendations.",
    responses={
        200: {"description": "Recommendations retrieved successfully"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "User not found"},
    },
)
async def get_user_recommendations(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (pending, approved, rejected)"),
    type_filter: Optional[str] = Query(None, alias="type", description="Filter by type (education, partner_offer)"),
    sort_by: Optional[str] = Query("date", description="Sort by field (date, relevance, type)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
):
    """
    Get recommendations for a specific user.

    Resource-level authorization:
    - Users can access their own recommendations
    - Operators and admins can access any user's recommendations

    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session
        status_filter: Filter by status
        type_filter: Filter by type
        sort_by: Sort field
        sort_order: Sort order
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of recommendations with pagination info

    Raises:
        HTTPException: 403 Forbidden if user doesn't have permission
        HTTPException: 404 Not Found if user doesn't exist
    """
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check resource access (users can access own recommendations, operators can access any)
    # Operators and admins must respect user consent when accessing other users' recommendations
    if not check_user_access(user_id, current_user, db=db, check_consent=True):
        # Check if it's a consent issue
        if not user.consent_status and current_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's recommendations. User has revoked consent or not granted consent."
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's recommendations"
        )

    # Check consent for own recommendations
    if current_user.user_id == user_id and not current_user.consent_status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent required to view recommendations. Please grant consent in settings."
        )

    # Build query
    query = db.query(Recommendation).filter(Recommendation.user_id == user_id)

    # Apply status filter
    if status_filter:
        try:
            status_enum = RecommendationStatus(status_filter.lower())
            query = query.filter(Recommendation.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}. Valid values: pending, approved, rejected"
            )

    # Apply type filter
    if type_filter:
        try:
            type_enum = RecommendationType(type_filter.lower())
            query = query.filter(Recommendation.type == type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid type filter: {type_filter}. Valid values: education, partner_offer"
            )

    # Get total count
    total = query.count()

    # Apply sorting
    if sort_by == "date":
        if sort_order == "asc":
            query = query.order_by(Recommendation.created_at.asc())
        else:
            query = query.order_by(Recommendation.created_at.desc())
    elif sort_by == "type":
        if sort_order == "asc":
            query = query.order_by(Recommendation.type.asc())
        else:
            query = query.order_by(Recommendation.type.desc())
    else:  # relevance (default to date)
        query = query.order_by(Recommendation.created_at.desc())

    # Apply pagination
    recommendations = query.offset(skip).limit(limit).all()

    # Convert to response format
    items = [RecommendationResponse.model_validate(rec) for rec in recommendations]

    return RecommendationsListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )

