"""Validation results storage and reporting."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

# Import backend models
try:
    from backend.app.models.data_upload import DataUpload as DataUploadModel
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.data_upload import DataUpload as DataUploadModel

from app.ingestion.validator import ValidationError

logger = logging.getLogger(__name__)


class ValidationResultsStorage:
    """Storage and reporting for validation results."""

    def __init__(self, db_session: Session):
        """
        Initialize validation results storage.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def store_validation_results(
        self,
        upload_id: uuid.UUID,
        errors: List[ValidationError],
        is_valid: bool,
    ) -> None:
        """
        Store validation results in DataUpload table.

        Args:
            upload_id: Upload ID
            errors: List of validation errors
            is_valid: Whether validation passed
        """
        try:
            upload = self.db.query(DataUploadModel).filter(
                DataUploadModel.upload_id == upload_id
            ).first()

            if upload:
                # Convert errors to dictionaries
                errors_dict = [e.to_dict() for e in errors]

                # Store validation results
                upload.validation_errors = {
                    "is_valid": is_valid,
                    "error_count": sum(1 for e in errors if e.severity == "error"),
                    "warning_count": sum(1 for e in errors if e.severity == "warning"),
                    "errors": errors_dict,
                    "validated_at": datetime.utcnow().isoformat(),
                }

                self.db.commit()
                logger.info(f"Stored validation results for upload {upload_id}: {len(errors)} errors/warnings")
            else:
                logger.warning(f"Upload {upload_id} not found, cannot store validation results")

        except Exception as e:
            logger.error(f"Error storing validation results: {str(e)}")
            self.db.rollback()
            raise

    def get_validation_results(self, upload_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Get validation results for an upload.

        Args:
            upload_id: Upload ID

        Returns:
            Validation results dictionary or None if not found
        """
        try:
            upload = self.db.query(DataUploadModel).filter(
                DataUploadModel.upload_id == upload_id
            ).first()

            if upload and upload.validation_errors:
                return upload.validation_errors
            return None

        except Exception as e:
            logger.error(f"Error getting validation results: {str(e)}")
            return None

    def generate_validation_report(
        self,
        errors: List[ValidationError],
        accounts_count: int,
        transactions_count: int,
        liabilities_count: int,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.

        Args:
            errors: List of validation errors
            accounts_count: Number of accounts processed
            transactions_count: Number of transactions processed
            liabilities_count: Number of liabilities processed

        Returns:
            Validation report dictionary
        """
        error_count = sum(1 for e in errors if e.severity == "error")
        warning_count = sum(1 for e in errors if e.severity == "warning")

        # Group errors by type
        errors_by_type = {}
        warnings_by_type = {}

        for error in errors:
            error_type = error.type
            if error.severity == "error":
                if error_type not in errors_by_type:
                    errors_by_type[error_type] = []
                errors_by_type[error_type].append(error.to_dict())
            else:
                if error_type not in warnings_by_type:
                    warnings_by_type[error_type] = []
                warnings_by_type[error_type].append(error.to_dict())

        # Group errors by field
        errors_by_field = {}
        warnings_by_field = {}

        for error in errors:
            field_key = f"{error.type}.{error.field}"
            if error.severity == "error":
                if field_key not in errors_by_field:
                    errors_by_field[field_key] = []
                errors_by_field[field_key].append(error.to_dict())
            else:
                if field_key not in warnings_by_field:
                    warnings_by_field[field_key] = []
                warnings_by_field[field_key].append(error.to_dict())

        report = {
            "summary": {
                "is_valid": error_count == 0,
                "error_count": error_count,
                "warning_count": warning_count,
                "total_errors": len(errors),
                "accounts_processed": accounts_count,
                "transactions_processed": transactions_count,
                "liabilities_processed": liabilities_count,
            },
            "errors_by_type": errors_by_type,
            "warnings_by_type": warnings_by_type,
            "errors_by_field": errors_by_field,
            "warnings_by_field": warnings_by_field,
            "all_errors": [e.to_dict() for e in errors if e.severity == "error"],
            "all_warnings": [e.to_dict() for e in errors if e.severity == "warning"],
            "generated_at": datetime.utcnow().isoformat(),
        }

        return report

    def log_validation_summary(
        self,
        errors: List[ValidationError],
        accounts_count: int,
        transactions_count: int,
        liabilities_count: int,
    ) -> None:
        """
        Log validation summary with structured logging.

        Args:
            errors: List of validation errors
            accounts_count: Number of accounts processed
            transactions_count: Number of transactions processed
            liabilities_count: Number of liabilities processed
        """
        error_count = sum(1 for e in errors if e.severity == "error")
        warning_count = sum(1 for e in errors if e.severity == "warning")

        # Log structured summary
        logger.info(
            "Validation summary",
            extra={
                "accounts_processed": accounts_count,
                "transactions_processed": transactions_count,
                "liabilities_processed": liabilities_count,
                "error_count": error_count,
                "warning_count": warning_count,
                "is_valid": error_count == 0,
            }
        )

        # Log errors by type
        if errors:
            errors_by_type = {}
            for error in errors:
                error_type = error.type
                if error_type not in errors_by_type:
                    errors_by_type[error_type] = 0
                errors_by_type[error_type] += 1

            logger.info(
                "Validation errors by type",
                extra={"errors_by_type": errors_by_type}
            )

            # Log top error fields
            errors_by_field = {}
            for error in errors:
                field_key = f"{error.type}.{error.field}"
                if field_key not in errors_by_field:
                    errors_by_field[field_key] = 0
                errors_by_field[field_key] += 1

            # Sort by count and log top 10
            top_errors = sorted(errors_by_field.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_errors:
                logger.info(
                    "Top validation error fields",
                    extra={"top_errors": dict(top_errors)}
                )

