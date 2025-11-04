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
    # Log operator action
    logger.info(
        f"Operator {current_user.user_id} ({current_user.email}) attempting to approve recommendation {recommendation_id}"
    )

    # TODO: Implement when Recommendation model is created
    # When implemented, should:
    # 1. Get recommendation from database
    # 2. Check if recommendation exists and is pending
    # 3. Update status to APPROVED
    # 4. Set approved_at to current timestamp
    # 5. Set approved_by to current_user.user_id
    # 6. Commit changes
    # 7. Log success

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
    # Log operator action
    logger.info(
        f"Operator {current_user.user_id} ({current_user.email}) attempting to reject recommendation {recommendation_id} "
        f"with reason: {request.reason[:100]}..." if len(request.reason) > 100 else f"with reason: {request.reason}"
    )

    # TODO: Implement when Recommendation model is created
    # When implemented, should:
    # 1. Get recommendation from database
    # 2. Check if recommendation exists and is pending
    # 3. Update status to REJECTED
    # 4. Set rejected_at to current timestamp
    # 5. Set rejected_by to current_user.user_id
    # 6. Set rejection_reason to request.reason
    # 7. Commit changes
    # 8. Log success

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


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

    # Get users with their profiles (left join to include users without profiles)
    users = db.query(UserModel).offset(skip).limit(limit).all()

    # Build response with persona information
    items = []
    for user in users:
        # Get user profile if exists
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()

        user_data = {
            "user_id": str(user.user_id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "consent_status": user.consent_status,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

        # Add persona information if profile exists
        if profile:
            user_data["persona_id"] = profile.persona_id
            user_data["persona_name"] = profile.persona_name
            user_data["profile_updated_at"] = profile.updated_at.isoformat() if profile.updated_at else None
        else:
            user_data["persona_id"] = None
            user_data["persona_name"] = None
            user_data["profile_updated_at"] = None

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

