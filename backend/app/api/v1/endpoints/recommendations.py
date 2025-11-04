"""Recommendations endpoints."""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.core.dependencies import (
    get_current_active_user,
    require_owner_or_operator_factory,
    check_user_access,
)
from app.core.cache_service import cache_recommendations_response
from app.models.user import User
from app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus
from app.api.v1.schemas.recommendations import (
    RecommendationResponse,
    RecommendationsListResponse,
    RecommendationFeedbackRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get(
    "",
    response_model=RecommendationsListResponse,
    summary="Get recommendations for current user",
    description="Get recommendations for the currently authenticated user. Requires consent.",
    responses={
        200: {"description": "Recommendations retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - consent required"},
    },
)
@cache_recommendations_response
async def get_recommendations(
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
    Get recommendations for the currently authenticated user.

    Requires consent to be granted.

    Args:
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
        HTTPException: 403 Forbidden if consent not granted
    """
    # Check consent
    if not current_user.consent_status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent required to view recommendations. Please grant consent in settings."
        )

    # Build query
    query = db.query(Recommendation).filter(Recommendation.user_id == current_user.user_id)

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


@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
    summary="Get recommendation detail",
    description="Get a specific recommendation by ID. Users can access their own recommendations. Operators can access any recommendation.",
    responses={
        200: {"description": "Recommendation retrieved successfully"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "Recommendation not found"},
    },
)
async def get_recommendation_detail(
    recommendation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific recommendation by ID.

    Resource-level authorization:
    - Users can access their own recommendations
    - Operators and admins can access any recommendation

    Args:
        recommendation_id: Recommendation ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Recommendation details

    Raises:
        HTTPException: 403 Forbidden if user doesn't have permission
        HTTPException: 404 Not Found if recommendation doesn't exist
    """
    # Get recommendation
    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == recommendation_id
    ).first()

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )

    # Check resource access (users can access own recommendations, operators can access any)
    # Operators and admins must respect user consent when accessing other users' recommendations
    if not check_user_access(recommendation.user_id, current_user, db=db, check_consent=True):
        # Check if it's a consent issue
        user = db.query(User).filter(User.user_id == recommendation.user_id).first()
        if user and not user.consent_status and current_user.user_id != recommendation.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this recommendation. User has revoked consent or not granted consent."
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this recommendation"
        )

    # Check consent for own recommendations
    if current_user.user_id == recommendation.user_id and not current_user.consent_status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent required to view recommendations. Please grant consent in settings."
        )

    return RecommendationResponse.model_validate(recommendation)


@router.post(
    "/{recommendation_id}/feedback",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Submit feedback for a recommendation",
    description="Submit feedback (rating, helpfulness, comment) for a recommendation. Users can only provide feedback for their own recommendations.",
    responses={
        204: {"description": "Feedback submitted successfully"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Recommendation not found"},
    },
)
async def submit_recommendation_feedback(
    recommendation_id: uuid.UUID,
    feedback: RecommendationFeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Submit feedback for a recommendation.

    Users can only provide feedback for their own recommendations.

    Args:
        recommendation_id: Recommendation ID
        feedback: Feedback data (rating, helpful, comment)
        current_user: Current authenticated user
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 403 Forbidden if user doesn't have permission
        HTTPException: 404 Not Found if recommendation doesn't exist
    """
    # Get recommendation
    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == recommendation_id
    ).first()

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )

    # Check resource access (users can only provide feedback for their own recommendations)
    if recommendation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only provide feedback for your own recommendations"
        )

    # Store feedback (currently just logging - could add a feedback table in the future)
    logger.info(
        f"Feedback submitted for recommendation {recommendation_id} by user {current_user.user_id}: "
        f"rating={feedback.rating}, helpful={feedback.helpful}, comment={feedback.comment}"
    )

    # TODO: Store feedback in database if feedback table is created

    return None


