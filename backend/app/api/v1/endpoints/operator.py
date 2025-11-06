"""Operator endpoints for reviewing recommendations and managing system."""

from typing import List, Optional
import uuid
import logging
import tempfile
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import distinct, cast, String

from app.database import get_db
from app.core.dependencies import require_operator, require_admin, check_user_access
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.liability import Liability
from app.api.v1.schemas.financial_data import (
    AccountResponse,
    TransactionResponse,
    LiabilityResponse,
    AccountsListResponse,
    TransactionsListResponse,
    LiabilitiesListResponse,
)
from app.api.v1.schemas.recommendations import (
    RecommendationRejectRequest,
    RecommendationModifyRequest,
)
from app.api.v1.schemas.rag_metrics import RAGDashboard, RAGHealthCheck, GenerationMetrics, ABTestStatus, ABTestMetrics, ABTestComparison, VectorStoreStats

logger = logging.getLogger(__name__)

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
    type_filter: Optional[str] = Query(None, alias="type"),
    persona_id: Optional[int] = Query(None),
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
        type_filter: Filter by recommendation type (education, partner_offer)
        persona_id: Filter by persona ID

    Returns:
        List of recommendations pending review
    """
    from app.models.recommendation import Recommendation, RecommendationStatus, RecommendationType
    
    logger.info(
        f"Operator {current_user.user_id} ({current_user.email}) accessing review queue "
        f"with filters: status={status_filter}, user_id={user_id}, type={type_filter}, persona_id={persona_id}"
    )
    
    # Build query - operators can see all recommendations
    query = db.query(Recommendation)
    
    # Apply status filter (default to pending if not specified)
    if status_filter:
        try:
            status_enum = RecommendationStatus(status_filter.lower())
            query = query.filter(Recommendation.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}. Valid values: pending, approved, rejected"
            )
    else:
        # Default to pending recommendations for review queue
        query = query.filter(Recommendation.status == RecommendationStatus.PENDING)
    
    # Apply user_id filter
    if user_id:
        try:
            user_uuid = uuid.UUID(user_id)
            query = query.filter(Recommendation.user_id == user_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user_id format: {user_id}"
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
    
    # Apply persona_id filter (from decision_trace JSON)
    if persona_id is not None:
        # Note: persona_id is stored in decision_trace JSON, so we need to query JSON field
        # This assumes the decision_trace has a structure like: {"persona_assignment": {"persona_id": 1}}
        # PostgreSQL JSON query syntax
        from sqlalchemy import text
        query = query.filter(
            text("decision_trace->'persona_assignment'->>'persona_id' = :persona_id")
        ).params(persona_id=str(persona_id))
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting (default to newest first)
    query = query.order_by(Recommendation.created_at.desc())
    
    # Apply pagination
    recommendations = query.offset(skip).limit(limit).all()
    
    # Batch fetch all users to avoid N+1 queries
    user_ids = [rec.user_id for rec in recommendations]
    users_dict = {}
    if user_ids:
        users = db.query(User).filter(User.user_id.in_(user_ids)).all()
        users_dict = {user.user_id: user for user in users}
    
    # Convert to response format with user information
    items = []
    for rec in recommendations:
        # Get user information from batch-loaded dict
        user = users_dict.get(rec.user_id)
        user_name = user.name if user else None
        user_email = user.email if user else None
        
        # Extract persona information from decision_trace
        persona_id = None
        persona_name = None
        if rec.decision_trace and isinstance(rec.decision_trace, dict):
            persona_assignment = rec.decision_trace.get("persona_assignment", {})
            persona_id = persona_assignment.get("persona_id")
            persona_name = persona_assignment.get("persona_name")
        
        # Build response item
        item = {
            "recommendation_id": str(rec.recommendation_id),
            "user_id": str(rec.user_id),
            "user_name": user_name,
            "user_email": user_email,
            "type": rec.type.value if isinstance(rec.type, RecommendationType) else rec.type,
            "status": rec.status.value if isinstance(rec.status, RecommendationStatus) else rec.status,
            "title": rec.title,
            "content": rec.content,
            "rationale": rec.rationale,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "approved_at": rec.approved_at.isoformat() if rec.approved_at else None,
            "approved_by": str(rec.approved_by) if rec.approved_by else None,
            "rejected_at": rec.rejected_at.isoformat() if rec.rejected_at else None,
            "rejected_by": str(rec.rejected_by) if rec.rejected_by else None,
            "rejection_reason": rec.rejection_reason,
            "persona_id": persona_id,
            "persona_name": persona_name,
            "decision_trace": rec.decision_trace,
        }
        items.append(item)
    
    logger.info(
        f"Review queue query returned {len(items)} recommendations (total: {total}, "
        f"skip: {skip}, limit: {limit})"
    )
    
    # Note: We're returning a dict instead of RecommendationsListResponse because
    # RecommendationResponse doesn't include user_name, user_email, persona_id, persona_name
    # The frontend expects these fields, so we'll return them directly
    return {
        "items": items,
        "total": total,
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
        400: {"description": "Bad request - invalid recommendation ID format"},
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
    from app.models.recommendation import Recommendation, RecommendationStatus, RecommendationType
    
    logger.info(
        f"Operator {current_user.user_id} ({current_user.email}) accessing recommendation {recommendation_id} for review"
    )
    
    try:
        # Convert recommendation_id to UUID
        rec_uuid = uuid.UUID(recommendation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recommendation ID format: {recommendation_id}"
        )
    
    # Get recommendation from database
    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == rec_uuid
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation not found: {recommendation_id}"
        )
    
    # Get user information
    user = db.query(User).filter(User.user_id == recommendation.user_id).first()
    user_name = user.name if user else None
    user_email = user.email if user else None
    
    # Extract persona info from decision_trace
    persona_id = None
    persona_name = None
    decision_trace = None
    
    if recommendation.decision_trace and isinstance(recommendation.decision_trace, dict):
        decision_trace = recommendation.decision_trace
        persona_assignment = decision_trace.get("persona_assignment", {})
        persona_id = persona_assignment.get("persona_id")
        persona_name = persona_assignment.get("persona_name")
    
    # Build response
    response_data = {
        "recommendation_id": str(recommendation.recommendation_id),
        "user_id": str(recommendation.user_id),
        "user_name": user_name,
        "user_email": user_email,
        "type": recommendation.type.value if isinstance(recommendation.type, RecommendationType) else recommendation.type,
        "status": recommendation.status.value if isinstance(recommendation.status, RecommendationStatus) else recommendation.status,
        "title": recommendation.title,
        "content": recommendation.content,
        "rationale": recommendation.rationale,
        "created_at": recommendation.created_at.isoformat() if recommendation.created_at else None,
        "approved_at": recommendation.approved_at.isoformat() if recommendation.approved_at else None,
        "approved_by": str(recommendation.approved_by) if recommendation.approved_by else None,
        "rejected_at": recommendation.rejected_at.isoformat() if recommendation.rejected_at else None,
        "rejected_by": str(recommendation.rejected_by) if recommendation.rejected_by else None,
        "rejection_reason": recommendation.rejection_reason,
        "persona_id": persona_id,
        "persona_name": persona_name,
        "decision_trace": decision_trace,
    }
    
    logger.info(
        f"Successfully retrieved recommendation {recommendation_id} for operator {current_user.user_id}"
    )
    
    return response_data


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
    from app.models.recommendation import Recommendation, RecommendationStatus
    from datetime import datetime
    
    # Log operator action
    logger.info(
        f"Operator {current_user.user_id} ({current_user.email}) attempting to approve recommendation {recommendation_id}"
    )
    
    try:
        # Convert recommendation_id to UUID
        rec_uuid = uuid.UUID(recommendation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recommendation ID format: {recommendation_id}"
        )
    
    # Get recommendation from database
    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == rec_uuid
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation not found: {recommendation_id}"
        )
    
    # Check if recommendation is already approved
    if recommendation.status == RecommendationStatus.APPROVED:
        logger.warning(
            f"Recommendation {recommendation_id} is already approved by {recommendation.approved_by} "
            f"at {recommendation.approved_at}"
        )
        return {
            "message": "Recommendation already approved",
            "recommendation_id": str(recommendation.recommendation_id),
            "status": recommendation.status.value,
            "approved_at": recommendation.approved_at.isoformat() if recommendation.approved_at else None,
        }
    
    # Check if recommendation is rejected (can't approve a rejected recommendation)
    if recommendation.status == RecommendationStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve a rejected recommendation. Recommendation {recommendation_id} was rejected."
        )
    
    # Update recommendation status to APPROVED
    recommendation.status = RecommendationStatus.APPROVED
    recommendation.approved_at = datetime.utcnow()
    recommendation.approved_by = current_user.user_id
    
    # Clear rejection fields if they were set
    recommendation.rejected_at = None
    recommendation.rejected_by = None
    recommendation.rejection_reason = None
    
    # Commit changes
    try:
        db.commit()
        db.refresh(recommendation)
        logger.info(
            f"Successfully approved recommendation {recommendation_id} by operator {current_user.user_id} ({current_user.email})"
        )
        
        # Invalidate recommendations cache for the user
        from app.core.cache_service import invalidate_recommendations_cache
        invalidate_recommendations_cache(recommendation.user_id)
        logger.debug(f"Invalidated recommendations cache for user {recommendation.user_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving recommendation {recommendation_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve recommendation: {str(e)}"
        )
    
    return {
        "message": "Recommendation approved successfully",
        "recommendation_id": str(recommendation.recommendation_id),
        "status": recommendation.status.value,
        "approved_at": recommendation.approved_at.isoformat() if recommendation.approved_at else None,
        "approved_by": str(recommendation.approved_by) if recommendation.approved_by else None,
    }


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
    request: RecommendationRejectRequest = Body(...),
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Reject a recommendation.

    Requires operator role or higher.

    Args:
        recommendation_id: Recommendation ID
        request: Reject request with reason
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        Rejection confirmation
    """
    from app.models.recommendation import Recommendation, RecommendationStatus
    from datetime import datetime
    
    # Log operator action
    logger.info(
        f"Operator {current_user.user_id} ({current_user.email}) attempting to reject recommendation {recommendation_id} "
        f"with reason: {request.reason[:100]}..." if len(request.reason) > 100 else f"with reason: {request.reason}"
    )
    
    try:
        # Convert recommendation_id to UUID
        rec_uuid = uuid.UUID(recommendation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recommendation ID format: {recommendation_id}"
        )
    
    # Get recommendation from database
    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == rec_uuid
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation not found: {recommendation_id}"
        )
    
    # Check if recommendation is already rejected
    if recommendation.status == RecommendationStatus.REJECTED:
        logger.warning(
            f"Recommendation {recommendation_id} is already rejected by {recommendation.rejected_by} "
            f"at {recommendation.rejected_at}"
        )
        return {
            "message": "Recommendation already rejected",
            "recommendation_id": str(recommendation.recommendation_id),
            "status": recommendation.status.value,
            "rejected_at": recommendation.rejected_at.isoformat() if recommendation.rejected_at else None,
        }
    
    # Check if recommendation is approved (can't reject an approved recommendation)
    if recommendation.status == RecommendationStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject an approved recommendation. Recommendation {recommendation_id} was already approved."
        )
    
    # Update recommendation status to REJECTED
    recommendation.status = RecommendationStatus.REJECTED
    recommendation.rejected_at = datetime.utcnow()
    recommendation.rejected_by = current_user.user_id
    recommendation.rejection_reason = request.reason
    
    # Clear approval fields if they were set
    recommendation.approved_at = None
    recommendation.approved_by = None
    
    # Commit changes
    try:
        db.commit()
        db.refresh(recommendation)
        logger.info(
            f"Successfully rejected recommendation {recommendation_id} by operator {current_user.user_id} ({current_user.email})"
        )
        
        # Invalidate recommendations cache for the user
        from app.core.cache_service import invalidate_recommendations_cache
        invalidate_recommendations_cache(recommendation.user_id)
        logger.debug(f"Invalidated recommendations cache for user {recommendation.user_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error rejecting recommendation {recommendation_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject recommendation: {str(e)}"
        )
    
    return {
        "message": "Recommendation rejected successfully",
        "recommendation_id": str(recommendation.recommendation_id),
        "status": recommendation.status.value,
        "rejected_at": recommendation.rejected_at.isoformat() if recommendation.rejected_at else None,
        "rejected_by": str(recommendation.rejected_by) if recommendation.rejected_by else None,
        "rejection_reason": recommendation.rejection_reason,
    }


@router.put(
    "/review/{recommendation_id}",
    summary="Modify recommendation",
    description="Modify a recommendation's title, content, or rationale. Requires operator role or higher.",
    responses={
        200: {"description": "Recommendation modified successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
        404: {"description": "Recommendation not found"},
        501: {"description": "Not implemented - endpoint not yet available"},
    },
)
async def modify_recommendation(
    recommendation_id: str,
    request: RecommendationModifyRequest = Body(...),
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Modify a recommendation.

    Requires operator role or higher.
    Only pending recommendations can be modified.

    Args:
        recommendation_id: Recommendation ID
        request: Modify request with updated fields
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        Modified recommendation
    """
    # Log operator action
    changes = []
    if request.title is not None:
        changes.append("title")
    if request.content is not None:
        changes.append("content")
    if request.rationale is not None:
        changes.append("rationale")

    logger.info(
        f"Operator {current_user.user_id} ({current_user.email}) attempting to modify recommendation {recommendation_id} "
        f"fields: {', '.join(changes)}"
    )

    # TODO: Implement when Recommendation model is created
    # When implemented, should:
    # 1. Get recommendation from database
    # 2. Check if recommendation exists and is pending
    # 3. Update fields that are provided in request
    # 4. Commit changes
    # 5. Log success with changed fields
    # 6. Return updated recommendation

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.post(
    "/review/bulk",
    summary="Bulk approve or reject recommendations",
    description="Approve or reject multiple recommendations at once. Requires operator role or higher.",
    responses={
        200: {"description": "Bulk operation completed successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
        400: {"description": "Bad request - invalid action or recommendation IDs"},
    },
)
async def bulk_review_recommendations(
    action: str = Body(..., description="Action to perform: 'approve' or 'reject'"),
    recommendation_ids: List[str] = Body(..., description="List of recommendation IDs"),
    reason: Optional[str] = Body(None, description="Reason for rejection (required if action is 'reject')"),
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Bulk approve or reject recommendations.

    Requires operator role or higher.

    Args:
        action: Action to perform ('approve' or 'reject')
        recommendation_ids: List of recommendation IDs
        reason: Reason for rejection (required if action is 'reject')
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        Bulk operation results
    """
    from app.models.recommendation import Recommendation, RecommendationStatus
    from datetime import datetime
    
    # Validate action
    if action not in ['approve', 'reject']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {action}. Must be 'approve' or 'reject'"
        )
    
    # Require reason for reject action
    if action == 'reject' and not reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reason is required when rejecting recommendations"
        )
    
    # Validate recommendation IDs
    if not recommendation_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one recommendation ID is required"
        )
    
    # Convert recommendation IDs to UUIDs
    rec_uuids = []
    for rec_id in recommendation_ids:
        try:
            rec_uuids.append(uuid.UUID(rec_id))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid recommendation ID format: {rec_id}"
            )
    
    # Log operator action
    logger.info(
        f"Operator {current_user.user_id} ({current_user.email}) attempting to {action} "
        f"{len(rec_uuids)} recommendations"
    )
    
    # Get all recommendations
    recommendations = db.query(Recommendation).filter(
        Recommendation.recommendation_id.in_(rec_uuids)
    ).all()
    
    # Check if all recommendations exist
    found_ids = {rec.recommendation_id for rec in recommendations}
    missing_ids = set(rec_uuids) - found_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendations not found: {[str(id) for id in missing_ids]}"
        )
    
    # Process each recommendation
    approved_count = 0
    rejected_count = 0
    already_processed = []
    errors = []
    
    for recommendation in recommendations:
        try:
            if action == 'approve':
                # Check if already approved
                if recommendation.status == RecommendationStatus.APPROVED:
                    already_processed.append(str(recommendation.recommendation_id))
                    continue
                
                # Check if rejected (can't approve a rejected recommendation)
                if recommendation.status == RecommendationStatus.REJECTED:
                    errors.append(f"Cannot approve rejected recommendation {recommendation.recommendation_id}")
                    continue
                
                # Approve
                recommendation.status = RecommendationStatus.APPROVED
                recommendation.approved_at = datetime.utcnow()
                recommendation.approved_by = current_user.user_id
                recommendation.rejected_at = None
                recommendation.rejected_by = None
                recommendation.rejection_reason = None
                approved_count += 1
                
            else:  # reject
                # Check if already rejected
                if recommendation.status == RecommendationStatus.REJECTED:
                    already_processed.append(str(recommendation.recommendation_id))
                    continue
                
                # Check if approved (can't reject an approved recommendation)
                if recommendation.status == RecommendationStatus.APPROVED:
                    errors.append(f"Cannot reject approved recommendation {recommendation.recommendation_id}")
                    continue
                
                # Reject
                recommendation.status = RecommendationStatus.REJECTED
                recommendation.rejected_at = datetime.utcnow()
                recommendation.rejected_by = current_user.user_id
                recommendation.rejection_reason = reason
                recommendation.approved_at = None
                recommendation.approved_by = None
                rejected_count += 1
                
        except Exception as e:
            errors.append(f"Error processing recommendation {recommendation.recommendation_id}: {str(e)}")
            logger.error(f"Error processing recommendation {recommendation.recommendation_id}: {str(e)}", exc_info=True)
    
    # Commit changes
    try:
        db.commit()
        logger.info(
            f"Successfully {action}ed {approved_count + rejected_count} recommendations "
            f"by operator {current_user.user_id} ({current_user.email})"
        )
        
        # Invalidate recommendations cache for all affected users
        from app.core.cache_service import invalidate_recommendations_cache
        affected_user_ids = {rec.user_id for rec in recommendations}
        for user_id in affected_user_ids:
            invalidate_recommendations_cache(user_id)
        logger.debug(f"Invalidated recommendations cache for {len(affected_user_ids)} users")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing bulk {action} operation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to {action} recommendations: {str(e)}"
        )
    
    return {
        "message": f"Bulk {action} operation completed",
        "action": action,
        "total_requested": len(rec_uuids),
        "approved": approved_count if action == 'approve' else 0,
        "rejected": rejected_count if action == 'reject' else 0,
        "already_processed": len(already_processed),
        "errors": errors if errors else None,
    }


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
    logger.info(f"Operator {current_user.user_id} ({current_user.email}) requesting system analytics")

    # Import EvaluationService from service layer
    import sys
    import os
    _current_file = os.path.abspath(__file__)
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_file))))
    _project_root = os.path.dirname(_backend_dir)
    _service_dir = os.path.join(_project_root, "service")

    # Add paths if not already there
    for path in [_backend_dir, _service_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)

    try:
        from app.eval.metrics import EvaluationService
        logger.info("EvaluationService imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import EvaluationService: {e}")
        # Return empty metrics if service not available
        return {
            "coverage": {
                "users_with_persona": 0,
                "users_with_persona_percent": 0.0,
                "users_with_behaviors": 0,
                "users_with_behaviors_percent": 0.0,
                "users_with_both": 0,
                "users_with_both_percent": 0.0,
            },
            "explainability": {
                "recommendations_with_rationales": 0,
                "recommendations_with_rationales_percent": 0.0,
                "rationales_with_data_points": 0,
                "rationales_with_data_points_percent": 0.0,
                "rationale_quality_score": 0.0,
            },
            "performance": {
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "mean_latency_ms": 0.0,
                "min_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "recommendations_within_target": 0,
                "recommendations_within_target_percent": 0.0,
            },
            "engagement": {
                "total_users": 0,
                "active_users": 0,
                "recommendations_sent": 0,
                "recommendations_viewed": 0,
                "recommendations_actioned": 0,
            },
        }

    # Initialize evaluation service
    eval_service = EvaluationService(db_session=db)

    # Calculate all metrics
    try:
        all_metrics = eval_service.calculate_all_metrics()

        # Calculate engagement metrics
        from app.models.user import User as UserModel
        from app.models.recommendation import Recommendation, RecommendationStatus
        from datetime import datetime, timedelta

        # Total users (excluding operators and admins)
        total_users = db.query(UserModel).filter(UserModel.role == "user").count()

        # Active users (users who have logged in within last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        # Note: This assumes we track last_login in User model. For now, use users with recent activity
        # We'll use users with recommendations or data uploads as proxy for active users
        # Use distinct on user_id only to avoid JSON column issues in PostgreSQL
        from sqlalchemy import distinct
        active_users = db.query(distinct(UserModel.user_id)).filter(
            UserModel.role == "user"
        ).join(
            Recommendation, UserModel.user_id == Recommendation.user_id
        ).count()

        # Total recommendations sent (all recommendations)
        recommendations_sent = db.query(Recommendation).count()

        # Recommendations viewed (approximated by approved recommendations)
        # In a real system, we'd track views separately
        # For now, count all recommendations as viewed (status filtering causes enum issues)
        # TODO: Fix enum comparison when database enum type is properly configured
        recommendations_viewed = db.query(Recommendation).count()

        # Recommendations actioned (users who clicked/dismissed, approximated by approved)
        recommendations_actioned = recommendations_viewed

        engagement = {
            "total_users": total_users,
            "active_users": active_users,
            "recommendations_sent": recommendations_sent,
            "recommendations_viewed": recommendations_viewed,
            "recommendations_actioned": recommendations_actioned,
        }

        # Map metrics to expected format
        coverage = {
            "users_with_persona": all_metrics["coverage"].get("users_with_persona_count", 0),
            "users_with_persona_percent": all_metrics["coverage"].get("users_with_persona_percent", 0.0),
            "users_with_behaviors": all_metrics["coverage"].get("users_with_behaviors_count", 0),
            "users_with_behaviors_percent": all_metrics["coverage"].get("users_with_behaviors_percent", 0.0),
            "users_with_both": all_metrics["coverage"].get("users_with_both_count", 0),
            "users_with_both_percent": all_metrics["coverage"].get("users_with_both_percent", 0.0),
        }

        explainability = {
            "recommendations_with_rationales": all_metrics["explainability"].get("recommendations_with_rationales_count", 0),
            "recommendations_with_rationales_percent": all_metrics["explainability"].get("recommendations_with_rationales_percent", 0.0),
            "rationales_with_data_points": all_metrics["explainability"].get("rationales_with_data_points_count", 0),
            "rationales_with_data_points_percent": all_metrics["explainability"].get("rationales_with_data_points_percent", 0.0),
            "rationale_quality_score": all_metrics["explainability"].get("rationale_quality_score", 0.0),
        }

        performance = {
            "p50_latency_ms": all_metrics["latency"].get("recommendation_generation_latency_p50", 0.0),
            "p95_latency_ms": all_metrics["latency"].get("recommendation_generation_latency_p95", 0.0),
            "p99_latency_ms": all_metrics["latency"].get("recommendation_generation_latency_p99", 0.0),
            "mean_latency_ms": all_metrics["latency"].get("recommendation_generation_latency_mean", 0.0),
            "min_latency_ms": all_metrics["latency"].get("recommendation_generation_latency_min", 0.0),
            "max_latency_ms": all_metrics["latency"].get("recommendation_generation_latency_max", 0.0),
            "recommendations_within_target": all_metrics["latency"].get("recommendations_within_target", 0),
            "recommendations_within_target_percent": all_metrics["latency"].get("recommendations_within_target_percent", 0.0),
        }

        fairness = {
            "persona_balance_score": all_metrics["fairness"].get("persona_balance_score", 0.0),
            "persona_distribution": all_metrics["fairness"].get("persona_distribution", {}),
            "signal_detection_by_persona": all_metrics["fairness"].get("signal_detection_by_persona", {}),
        }

        logger.info(f"Analytics calculated successfully: {total_users} users, {recommendations_sent} recommendations")

        return {
            "coverage": coverage,
            "explainability": explainability,
            "performance": performance,
            "engagement": engagement,
            "fairness": fairness,
        }

    except Exception as e:
        logger.error(f"Error calculating analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate analytics: {str(e)}"
        )


@router.get(
    "/analytics/export/json",
    summary="Export metrics as JSON",
    description="Export evaluation metrics as JSON file. Requires operator role or higher.",
    responses={
        200: {"description": "JSON file downloaded successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
    },
)
async def export_metrics_json(
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Export evaluation metrics as JSON file.

    Requires operator role or higher.

    Args:
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        JSON file download
    """
    logger.info(f"Operator {current_user.user_id} ({current_user.email}) exporting metrics as JSON")

    # Import ReportGenerator from service layer
    import sys
    import os
    _current_file = os.path.abspath(__file__)
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_file))))
    _project_root = os.path.dirname(_backend_dir)
    _service_dir = os.path.join(_project_root, "service")

    # Add paths if not already there
    for path in [_backend_dir, _service_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)

    try:
        from app.eval.report import ReportGenerator
    except ImportError as e:
        logger.error(f"Failed to import ReportGenerator: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evaluation service not available"
        )

    # Create temporary directory for report generation
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Initialize report generator
            report_generator = ReportGenerator(db_session=db, output_dir=temp_dir)

            # Generate JSON metrics file
            json_filepath = report_generator.generate_metrics_json()

            # Read file content
            with open(json_filepath, 'rb') as f:
                file_content = f.read()

            # Generate filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"

            # Return file as download
            return Response(
                content=file_content,
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                }
            )

        except Exception as e:
            logger.error(f"Error generating JSON export: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate JSON export: {str(e)}"
            )


@router.get(
    "/analytics/export/csv",
    summary="Export metrics as CSV",
    description="Export evaluation metrics as CSV file. Requires operator role or higher.",
    responses={
        200: {"description": "CSV file downloaded successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
    },
)
async def export_metrics_csv(
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Export evaluation metrics as CSV file.

    Requires operator role or higher.

    Args:
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        CSV file download
    """
    logger.info(f"Operator {current_user.user_id} ({current_user.email}) exporting metrics as CSV")

    # Import ReportGenerator from service layer
    import sys
    import os
    _current_file = os.path.abspath(__file__)
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_file))))
    _project_root = os.path.dirname(_backend_dir)
    _service_dir = os.path.join(_project_root, "service")

    # Add paths if not already there
    for path in [_backend_dir, _service_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)

    try:
        from app.eval.report import ReportGenerator
    except ImportError as e:
        logger.error(f"Failed to import ReportGenerator: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evaluation service not available"
        )

    # Create temporary directory for report generation
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Initialize report generator
            report_generator = ReportGenerator(db_session=db, output_dir=temp_dir)

            # Generate CSV metrics file
            csv_filepath = report_generator.generate_metrics_csv()

            # Read file content
            with open(csv_filepath, 'rb') as f:
                file_content = f.read()

            # Generate filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.csv"

            # Return file as download
            return Response(
                content=file_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                }
            )

        except Exception as e:
            logger.error(f"Error generating CSV export: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate CSV export: {str(e)}"
            )


@router.get(
    "/analytics/export/summary",
    summary="Export summary report",
    description="Generate and download summary evaluation report as Markdown file. Requires operator role or higher.",
    responses={
        200: {"description": "Summary report downloaded successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
    },
)
async def export_summary_report(
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Generate and download summary evaluation report as Markdown file.

    Requires operator role or higher.

    Args:
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        Markdown report file download
    """
    logger.info(f"Operator {current_user.user_id} ({current_user.email}) exporting summary report")

    # Import ReportGenerator from service layer
    import sys
    import os
    _current_file = os.path.abspath(__file__)
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_file))))
    _project_root = os.path.dirname(_backend_dir)
    _service_dir = os.path.join(_project_root, "service")

    # Add paths if not already there
    for path in [_backend_dir, _service_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)

    try:
        from app.eval.report import ReportGenerator
    except ImportError as e:
        logger.error(f"Failed to import ReportGenerator: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evaluation service not available"
        )

    # Create temporary directory for report generation
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Initialize report generator
            report_generator = ReportGenerator(db_session=db, output_dir=temp_dir)

            # Generate summary report
            report_filepath = report_generator.generate_summary_report()

            # Read file content
            with open(report_filepath, 'rb') as f:
                file_content = f.read()

            # Generate filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.md"

            # Return file as download
            return Response(
                content=file_content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                }
            )

        except Exception as e:
            logger.error(f"Error generating summary report: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate summary report: {str(e)}"
            )


@router.post(
    "/users/{user_id}/generate-recommendations",
    summary="Generate recommendations for a user",
    description="Manually trigger recommendation generation for a user. Requires operator role or higher.",
    responses={
        200: {"description": "Recommendations generated successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
        404: {"description": "User not found"},
    },
)
async def generate_recommendations_for_user(
    user_id: str,
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Generate recommendations for a user.

    Requires operator role or higher.
    This will:
    1. Check if user has consent granted
    2. Check if user has a profile with signals
    3. Check if user has assigned personas
    4. Generate 3-5 education items and 1-3 partner offers
    5. Store recommendations with PENDING status

    Args:
        user_id: User ID
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        Recommendation generation result

    Raises:
        HTTPException: 404 Not Found if user doesn't exist
        HTTPException: 400 Bad Request if user doesn't have profile/persona
    """
    logger.info(f"Operator {current_user.user_id} ({current_user.email}) generating recommendations for user {user_id}")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # Check if user exists
    target_user = db.query(User).filter(User.user_id == user_uuid).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Import RecommendationGenerator from service layer
    import sys
    import os
    _current_file = os.path.abspath(__file__)
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_file))))
    _project_root = os.path.dirname(_backend_dir)
    _service_dir = os.path.join(_project_root, "service")

    # Add paths if not already there
    for path in [_backend_dir, _service_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)

    try:
        from app.recommendations.rag_integration import create_enhanced_generator
        logger.info("EnhancedRecommendationGenerator with RAG support imported successfully")
        # Initialize enhanced recommendation generator
        generator = create_enhanced_generator(db_session=db)
    except ImportError as e:
        logger.warning(f"RAG integration not available, falling back to legacy generator: {e}")
        try:
            from app.recommendations.generator import RecommendationGenerator
            logger.info("RecommendationGenerator (legacy) imported successfully")
            # Initialize legacy recommendation generator
            generator = RecommendationGenerator(db_session=db, use_openai=True)
        except ImportError as e:
            logger.error(f"Failed to import RecommendationGenerator: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Recommendation service not available: {str(e)}"
            )

    # Generate recommendations
    try:
        result = generator.generate_recommendations(user_uuid)

        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error")
            )

        logger.info(
            f"Generated {len(result.get('recommendations', []))} recommendations for user {user_id}: "
            f"{result.get('education_count', 0)} education, {result.get('partner_offer_count', 0)} partner offers"
        )

        return {
            "user_id": user_id,
            "recommendations_generated": len(result.get("recommendations", [])),
            "education_count": result.get("education_count", 0),
            "partner_offer_count": result.get("partner_offer_count", 0),
            "generated_at": result.get("generated_at"),
            "persona_ids": result.get("persona_ids", []),
            "persona_names": result.get("persona_names", []),
        }

    except HTTPException:
        # Re-raise HTTPException (400, 404, etc.) without modification
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


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
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    if not check_user_access(user_uuid, current_user, db=db, check_consent=True):
        # Check if it's a consent issue
        from app.models.user import User as UserModel
        target_user = db.query(UserModel).filter(UserModel.user_id == user_uuid).first()

        if target_user and not target_user.consent_status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's data. User has revoked consent or not granted consent."
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's data"
        )

    # Return user profile
    from app.models.user import User as UserModel
    from app.api.v1.schemas.user import UserProfileResponse
    target_user = db.query(UserModel).filter(UserModel.user_id == user_uuid).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserProfileResponse.model_validate(target_user)


@router.get(
    "/users/{user_id}/accounts",
    response_model=AccountsListResponse,
    summary="Get user accounts (operator)",
    description="Get all accounts for a user. Requires operator role or higher.",
    responses={
        200: {"description": "Accounts retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "User not found"},
    },
)
async def get_user_accounts(
    user_id: str,
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Get all accounts for a user.

    Requires operator role or higher.

    Args:
        user_id: User ID
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        List of accounts for the user
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # Check access
    if not check_user_access(user_uuid, current_user, db=db, check_consent=True):
        from app.models.user import User as UserModel
        target_user = db.query(UserModel).filter(UserModel.user_id == user_uuid).first()

        if target_user and not target_user.consent_status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's data. User has revoked consent or not granted consent."
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's data"
        )

    # Get accounts
    accounts = db.query(Account).filter(Account.user_id == user_uuid).all()

    return AccountsListResponse(
        items=[AccountResponse.model_validate(account) for account in accounts],
        total=len(accounts),
    )


@router.get(
    "/users/{user_id}/transactions",
    response_model=TransactionsListResponse,
    summary="Get user transactions (operator)",
    description="Get paginated transactions for a user. Requires operator role or higher.",
    responses={
        200: {"description": "Transactions retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "User not found"},
    },
)
async def get_user_transactions(
    user_id: str,
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get paginated transactions for a user.

    Requires operator role or higher.

    Args:
        user_id: User ID
        current_user: Current authenticated user (operator/admin)
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        Paginated list of transactions for the user
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # Check access
    if not check_user_access(user_uuid, current_user, db=db, check_consent=True):
        from app.models.user import User as UserModel
        target_user = db.query(UserModel).filter(UserModel.user_id == user_uuid).first()

        if target_user and not target_user.consent_status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's data. User has revoked consent or not granted consent."
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's data"
        )

    # Get transactions (ordered by date descending, most recent first)
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_uuid)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Get total count
    total = db.query(Transaction).filter(Transaction.user_id == user_uuid).count()

    return TransactionsListResponse(
        items=[TransactionResponse.model_validate(txn) for txn in transactions],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/users/{user_id}/liabilities",
    response_model=LiabilitiesListResponse,
    summary="Get user liabilities (operator)",
    description="Get all liabilities for a user. Requires operator role or higher.",
    responses={
        200: {"description": "Liabilities retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - insufficient permissions or consent revoked"},
        404: {"description": "User not found"},
    },
)
async def get_user_liabilities(
    user_id: str,
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Get all liabilities for a user.

    Requires operator role or higher.

    Args:
        user_id: User ID
        current_user: Current authenticated user (operator/admin)
        db: Database session

    Returns:
        List of liabilities for the user
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # Check access
    if not check_user_access(user_uuid, current_user, db=db, check_consent=True):
        from app.models.user import User as UserModel
        target_user = db.query(UserModel).filter(UserModel.user_id == user_uuid).first()

        if target_user and not target_user.consent_status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access this user's data. User has revoked consent or not granted consent."
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's data"
        )

    # Get liabilities
    liabilities = db.query(Liability).filter(Liability.user_id == user_uuid).all()

    return LiabilitiesListResponse(
        items=[LiabilityResponse.model_validate(liability) for liability in liabilities],
        total=len(liabilities),
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
        List of all users with persona information
    """
    from app.models.user import User as UserModel
    from app.models.user_profile import UserProfile
    from app.models.user_persona_assignment import UserPersonaAssignment
    from app.models.persona import Persona

    # Get users with their profiles (left join to include users without profiles)
    users = db.query(UserModel).offset(skip).limit(limit).all()

    # Build response with persona information
    items = []
    for user in users:
        # Get user profile if exists
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()

        # Get persona assignment if exists
        persona_assignment = db.query(UserPersonaAssignment).filter(
            UserPersonaAssignment.user_id == user.user_id
        ).first()
        
        persona_id = None
        persona_name = None
        if persona_assignment:
            persona = db.query(Persona).filter(Persona.persona_id == persona_assignment.persona_id).first()
            if persona:
                persona_id = persona.persona_id  # Already an integer
                persona_name = persona.name

        user_data = {
            "user_id": str(user.user_id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "consent_status": user.consent_status,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "persona_id": persona_id,
            "persona_name": persona_name,
            "profile_updated_at": profile.updated_at.isoformat() if profile and profile.updated_at else None,
        }

        items.append(user_data)

    return {
        "items": items,
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


@router.get(
    "/rag/dashboard",
    response_model=RAGDashboard,
    summary="Get RAG system dashboard",
    description="Get comprehensive RAG system status including health, metrics, and A/B test results. Requires operator role.",
    responses={
        200: {"description": "Dashboard data retrieved successfully"},
        401: {"description": "Unauthorized - authentication required"},
        403: {"description": "Forbidden - operator role required"},
    },
)
async def get_rag_dashboard(
    current_user: User = Depends(require_operator),
    db: Session = Depends(get_db),
):
    """
    Get RAG system dashboard with health, metrics, and A/B test results.
    
    Requires operator role or higher.
    
    Args:
        current_user: Current authenticated user (operator/admin)
        db: Database session
    
    Returns:
        RAG dashboard data
    """
    import sys
    import os
    from datetime import datetime
    
    logger.info(f"Operator {current_user.user_id} ({current_user.email}) accessing RAG dashboard")
    
    # Add service path
    _current_file = os.path.abspath(__file__)
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_file))))
    _project_root = os.path.dirname(_backend_dir)
    _service_dir = os.path.join(_project_root, "service")
    
    if _service_dir not in sys.path:
        sys.path.insert(0, _service_dir)
    
    # Health check
    health_data = {
        "vector_store_healthy": False,
        "vector_store_stats": None,
        "rag_enabled": False,
        "rag_rollout_percentage": 0.0,
        "openai_configured": False,
        "last_check": datetime.utcnow(),
    }
    
    # Check RAG configuration
    from app.config import settings
    health_data["rag_enabled"] = settings.rag_enabled
    health_data["rag_rollout_percentage"] = settings.rag_rollout_percentage
    health_data["openai_configured"] = bool(settings.openai_api_key)
    
    # Check vector store
    try:
        from app.rag import VectorStore
        vs = VectorStore()
        stats = vs.get_stats()
        
        health_data["vector_store_healthy"] = True
        health_data["vector_store_stats"] = VectorStoreStats(
            total_documents=stats["total_documents"],
            embedding_model=stats["embedding_model"],
            embedding_dimensions=stats["embedding_dimensions"],
            document_types=stats.get("document_types", {}),
        )
    except Exception as e:
        logger.warning(f"Vector store health check failed: {e}")
    
    # Get generation metrics
    rag_metrics_data = None
    catalog_metrics_data = None
    
    try:
        from app.eval import get_metrics_collector
        metrics = get_metrics_collector()
        
        rag_metrics = metrics.get_generation_metrics(method="rag")
        if rag_metrics["sample_size"] > 0:
            rag_metrics_data = GenerationMetrics(
                sample_size=rag_metrics["sample_size"],
                successful_generations=rag_metrics["successful_generations"],
                success_rate=rag_metrics["success_rate"],
                avg_generation_time_ms=rag_metrics["avg_generation_time_ms"],
                avg_recommendation_count=rag_metrics["avg_recommendation_count"],
                avg_citation_rate=rag_metrics.get("avg_citation_rate"),
            )
        
        catalog_metrics = metrics.get_generation_metrics(method="catalog")
        if catalog_metrics["sample_size"] > 0:
            catalog_metrics_data = GenerationMetrics(
                sample_size=catalog_metrics["sample_size"],
                successful_generations=catalog_metrics["successful_generations"],
                success_rate=catalog_metrics["success_rate"],
                avg_generation_time_ms=catalog_metrics["avg_generation_time_ms"],
                avg_recommendation_count=catalog_metrics["avg_recommendation_count"],
            )
    except Exception as e:
        logger.warning(f"Failed to get generation metrics: {e}")
    
    # Get A/B test status
    ab_test_data = None
    
    try:
        from app.eval import create_ab_tester
        ab_tester = create_ab_tester(
            rollout_percentage=settings.rag_rollout_percentage,
            enabled=settings.rag_enabled
        )
        
        if ab_tester.is_enabled():
            metrics = ab_tester.get_metrics()
            
            # Control variant
            control = metrics.get("control", {})
            control_metrics = ABTestMetrics(
                variant="control",
                method="catalog",
                sample_size=control.get("sample_size", 0),
                success_rate=control.get("success_rate", 0.0),
                avg_generation_time_ms=control.get("avg_generation_time_ms", 0.0),
                avg_rating=control.get("avg_rating"),
                helpful_rate=control.get("helpful_rate"),
            )
            
            # Variant A
            variant_a = metrics.get("variant_a", {})
            variant_a_metrics = ABTestMetrics(
                variant="variant_a",
                method="rag",
                sample_size=variant_a.get("sample_size", 0),
                success_rate=variant_a.get("success_rate", 0.0),
                avg_generation_time_ms=variant_a.get("avg_generation_time_ms", 0.0),
                avg_rating=variant_a.get("avg_rating"),
                helpful_rate=variant_a.get("helpful_rate"),
            )
            
            # Comparison
            comparison = metrics.get("comparison", {})
            comparison_data = ABTestComparison(
                variant_faster=comparison.get("variant_faster", False),
                speed_improvement=comparison.get("speed_improvement", 0.0),
                rating_improvement=comparison.get("rating_improvement", 0.0),
                helpful_rate_improvement=comparison.get("helpful_rate_improvement", 0.0),
                statistically_significant=comparison.get("statistically_significant", False),
            )
            
            recommendation = ab_tester.get_recommendation()
            
            ab_test_data = ABTestStatus(
                enabled=True,
                rollout_percentage=settings.rag_rollout_percentage,
                control=control_metrics,
                variant_a=variant_a_metrics,
                comparison=comparison_data,
                recommendation=recommendation,
            )
    except Exception as e:
        logger.warning(f"Failed to get A/B test status: {e}")
    
    # Build dashboard
    dashboard = RAGDashboard(
        health=RAGHealthCheck(**health_data),
        rag_metrics=rag_metrics_data,
        catalog_metrics=catalog_metrics_data,
        ab_test_status=ab_test_data,
    )
    
    return dashboard

