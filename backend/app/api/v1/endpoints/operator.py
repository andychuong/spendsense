"""Operator endpoints for reviewing recommendations and managing system."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_operator, require_admin, check_user_access
from app.models.user import User

router = APIRouter(prefix="/operator", tags=["operator"])


@router.get(
    "/review",
    summary="Get review queue",
    description="Get the review queue for operators. Returns list of recommendations pending review. Requires operator role or higher.",
    responses={
        200: {"description": "Review queue retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
    },
)
async def get_review_queue(
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    user_id: Optional[str] = Query(None),
):
    """
    Get review queue for operators.
    
    Requires operator role or higher.
    
    Args:
        current_user: Current authenticated user (operator/admin)
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        status_filter: Filter by recommendation status (pending, approved, rejected)
        user_id: Filter by user ID
        
    Returns:
        List of recommendations pending review
    """
    # TODO: Implement when Recommendation model is created
    # This is a placeholder endpoint
    return {
        "items": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
    }


@router.get(
    "/review/{recommendation_id}",
    summary="Get recommendation for review",
    description="Get a specific recommendation with decision trace for operator review. Requires operator role or higher.",
    responses={
        200: {"description": "Recommendation retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
        404: {"description": "Recommendation not found"},
        501: {"description": "Not implemented - endpoint not yet available"},
    },
)
async def get_recommendation_for_review(
    recommendation_id: str,
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Get a specific recommendation for review.
    
    Requires operator role or higher.
    
    Args:
        recommendation_id: Recommendation ID
        current_user: Current authenticated user (operator/admin)
        db: Database session
        
    Returns:
        Recommendation details with decision trace
    """
    # TODO: Implement when Recommendation model is created
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.post(
    "/review/{recommendation_id}/approve",
    summary="Approve recommendation",
    description="Approve a recommendation for delivery to the user. Requires operator role or higher.",
    responses={
        200: {"description": "Recommendation approved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
        404: {"description": "Recommendation not found"},
        501: {"description": "Not implemented - endpoint not yet available"},
    },
)
async def approve_recommendation(
    recommendation_id: str,
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Approve a recommendation.
    
    Requires operator role or higher.
    
    Args:
        recommendation_id: Recommendation ID
        current_user: Current authenticated user (operator/admin)
        db: Database session
        
    Returns:
        Approval confirmation
    """
    # TODO: Implement when Recommendation model is created
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.post(
    "/review/{recommendation_id}/reject",
    summary="Reject recommendation",
    description="Reject a recommendation with a reason. Requires operator role or higher.",
    responses={
        200: {"description": "Recommendation rejected successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
        404: {"description": "Recommendation not found"},
        501: {"description": "Not implemented - endpoint not yet available"},
    },
)
async def reject_recommendation(
    recommendation_id: str,
    reason: str = Query(..., description="Reason for rejection"),
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Reject a recommendation.
    
    Requires operator role or higher.
    
    Args:
        recommendation_id: Recommendation ID
        reason: Reason for rejection (query parameter)
        current_user: Current authenticated user (operator/admin)
        db: Database session
        
    Returns:
        Rejection confirmation
    """
    # TODO: Implement when Recommendation model is created
    # TODO: Create schema for reject request body (reason should be in request body, not query param)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.get(
    "/analytics",
    summary="Get system analytics",
    description="Get system-wide analytics and metrics including coverage, explainability, performance, and engagement metrics. Requires operator role or higher.",
    responses={
        200: {"description": "Analytics retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
    },
)
async def get_analytics(
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Get system analytics.
    
    Requires operator role or higher.
    
    Args:
        current_user: Current authenticated user (operator/admin)
        db: Database session
        
    Returns:
        System metrics and analytics
    """
    # TODO: Implement when analytics service is created
    return {
        "coverage": 0,
        "explainability": 0,
        "performance": {},
        "engagement": {},
    }


@router.get(
    "/users/{user_id}",
    summary="Get user details (operator)",
    description="Get detailed user information for operator view. Operators can view any user's data but must respect user consent. Requires operator role or higher.",
    responses={
        200: {"description": "User details retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "User not found"},
        501: {"description": "Not implemented - endpoint not yet available"},
    },
)
async def get_user_details(
    user_id: str,
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Get user details for operator view.
    
    Requires operator role or higher.
    Operators can view any user's data, but must respect user consent.
    If user has revoked consent or never granted consent, access is denied.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user (operator/admin)
        db: Database session
        
    Returns:
        User details with profile and recommendations
        
    Raises:
        HTTPException: 403 Forbidden if user has revoked consent
        HTTPException: 404 Not Found if user doesn't exist
    """
    # Check if operator can access this user's data (respects consent)
    if not check_user_access(user_id, current_user, db=db, check_consent=True):
        # Check if it's a consent issue
        from app.models.user import User as UserModel
        target_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
        
        if target_user and not target_user.consent_status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's data. User has revoked consent or not granted consent."
            )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's data"
        )
    
    # TODO: Implement when user profile endpoints are created
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


# Admin-only endpoints
@router.get(
    "/admin/users",
    summary="List all users (admin)",
    description="List all users in the system with pagination. Requires admin role.",
    responses={
        200: {"description": "Users list retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - admin role required"},
    },
)
async def list_all_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    List all users (admin only).
    
    Requires admin role.
    
    Args:
        current_user: Current authenticated user (admin)
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of all users
    """
    # TODO: Implement when user management is needed
    from app.models.user import User as UserModel
    
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return {
        "items": [{"user_id": str(u.user_id), "email": u.email, "role": u.role} for u in users],
        "total": db.query(UserModel).count(),
        "skip": skip,
        "limit": limit,
    }


@router.put(
    "/admin/users/{user_id}/role",
    summary="Update user role (admin)",
    description="Update a user's role (user, operator, admin). Requires admin role.",
    responses={
        200: {"description": "User role updated successfully"},
        400: {"description": "Invalid role"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - admin role required"},
        404: {"description": "User not found"},
    },
)
async def update_user_role(
    user_id: str,
    new_role: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Update user role (admin only).
    
    Requires admin role.
    
    Args:
        user_id: User ID
        new_role: New role (user, operator, admin)
        current_user: Current authenticated user (admin)
        db: Database session
        
    Returns:
        Updated user information
    """
    from app.models.user import User as UserModel, UserRole
    
    # Validate role
    try:
        role_enum = UserRole(new_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {new_role}. Must be one of: user, operator, admin"
        )
    
    # Find user
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update role
    user.role = role_enum.value
    db.commit()
    db.refresh(user)
    
    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "role": user.role,
    }

