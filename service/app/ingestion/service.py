"""Main data ingestion service."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.ingestion.parser import PlaidParser
from app.ingestion.validator import PlaidValidator, ValidationError
from app.ingestion.storage import DataStorage
from app.ingestion.validation_results import ValidationResultsStorage

# Import AccountModel for account_id_map
try:
    from backend.app.models.account import Account as AccountModel
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.account import Account as AccountModel

logger = logging.getLogger(__name__)


class IngestionService:
    """Main service for Plaid data ingestion."""

    def __init__(self, db_session: Session, s3_bucket: str = "spendsense-analytics"):
        """
        Initialize ingestion service.

        Args:
            db_session: SQLAlchemy database session
            s3_bucket: S3 bucket name for Parquet files
        """
        self.parser = PlaidParser()
        self.validator = PlaidValidator(
            enable_duplicate_detection=True,
            enable_range_validation=True
        )
        self.storage = DataStorage(db_session, s3_bucket)
        self.validation_results = ValidationResultsStorage(db_session)
        self.db = db_session

    def ingest(
        self,
        file_content: bytes,
        file_type: str,
        user_id: uuid.UUID,
        upload_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """
        Ingest Plaid data from file.

        Args:
            file_content: Raw file content as bytes
            file_type: File type ('json' or 'csv')
            user_id: User ID
            upload_id: Upload ID (optional)

        Returns:
            Ingestion report dictionary with summary, errors, warnings, and storage info
        """
        report = {
            "upload_id": str(upload_id) if upload_id else None,
            "user_id": str(user_id),
            "status": "pending",
            "ingestion_timestamp": None,
            "summary": {
                "accounts_processed": 0,
                "accounts_valid": 0,
                "accounts_invalid": 0,
                "transactions_processed": 0,
                "transactions_valid": 0,
                "transactions_invalid": 0,
                "liabilities_processed": 0,
                "liabilities_valid": 0,
                "liabilities_invalid": 0,
            },
            "errors": [],
            "warnings": [],
            "storage": {
                "postgresql": {
                    "accounts_inserted": 0,
                    "accounts_updated": 0,
                    "transactions_inserted": 0,
                    "transactions_updated": 0,
                    "liabilities_inserted": 0,
                    "liabilities_updated": 0,
                },
                "s3": {
                    "accounts_parquet": None,
                    "transactions_parquet": None,
                    "liabilities_parquet": None,
                },
            },
        }

        try:
            from datetime import datetime
            report["ingestion_timestamp"] = datetime.utcnow().isoformat()

            # Step 1: Parse file
            logger.info(f"Parsing {file_type} file for user {user_id}")
            try:
                parsed_data = self.parser.parse(file_content, file_type)
            except Exception as e:
                logger.error(f"Error parsing file: {str(e)}")
                report["status"] = "failed"
                report["errors"].append({
                    "type": "parsing",
                    "field": "file",
                    "error": f"Failed to parse file: {str(e)}",
                    "severity": "error",
                })
                return report

            # Step 2: Validate data
            logger.info(f"Validating data for user {user_id}")
            is_valid, validation_errors = self.validator.validate(parsed_data)

            # Store validation results
            if upload_id:
                try:
                    self.validation_results.store_validation_results(
                        upload_id, validation_errors, is_valid
                    )
                except Exception as e:
                    logger.warning(f"Failed to store validation results: {str(e)}")

            # Get counts for validation report
            accounts = parsed_data.get("accounts", [])
            transactions = parsed_data.get("transactions", [])
            liabilities = parsed_data.get("liabilities", [])

            # Generate validation report
            validation_report = self.validation_results.generate_validation_report(
                validation_errors,
                len(accounts),
                len(transactions),
                len(liabilities),
            )

            # Log validation summary
            self.validation_results.log_validation_summary(
                validation_errors,
                len(accounts),
                len(transactions),
                len(liabilities),
            )

            # Separate errors and warnings
            errors = [e.to_dict() for e in validation_errors if e.severity == "error"]
            warnings = [e.to_dict() for e in validation_errors if e.severity == "warning"]

            report["errors"] = errors
            report["warnings"] = warnings
            report["validation_report"] = validation_report

            # Update summary using validation report
            accounts = parsed_data.get("accounts", [])
            transactions = parsed_data.get("transactions", [])
            liabilities = parsed_data.get("liabilities", [])

            report["summary"]["accounts_processed"] = len(accounts)
            report["summary"]["accounts_valid"] = len(accounts) - len([e for e in errors if e["type"] == "account"])
            report["summary"]["accounts_invalid"] = len([e for e in errors if e["type"] == "account"])

            report["summary"]["transactions_processed"] = len(transactions)
            report["summary"]["transactions_valid"] = len(transactions) - len([e for e in errors if e["type"] == "transaction"])
            report["summary"]["transactions_invalid"] = len([e for e in errors if e["type"] == "transaction"])

            report["summary"]["liabilities_processed"] = len(liabilities)
            report["summary"]["liabilities_valid"] = len(liabilities) - len([e for e in errors if e["type"] == "liability"])
            report["summary"]["liabilities_invalid"] = len([e for e in errors if e["type"] == "liability"])

            # If there are critical errors, stop processing
            if not is_valid:
                logger.warning(f"Validation failed for user {user_id}. Errors: {len(errors)}")
                report["status"] = "failed"
                return report

            # Step 3: Store in PostgreSQL
            logger.info(f"Storing data in PostgreSQL for user {user_id}")
            try:
                # Store accounts
                accounts_result = self.storage.store_accounts_postgresql(
                    accounts, user_id, upload_id
                )
                report["storage"]["postgresql"]["accounts_inserted"] = accounts_result["inserted"]
                report["storage"]["postgresql"]["accounts_updated"] = accounts_result["updated"]

                # Get account_id mapping (Plaid account_id -> database account.id)
                # This is needed for transactions and liabilities
                account_id_map = self._get_account_id_map(accounts, user_id)

                # Store transactions
                if transactions:
                    transactions_result = self.storage.store_transactions_postgresql(
                        transactions, user_id, account_id_map, upload_id
                    )
                    report["storage"]["postgresql"]["transactions_inserted"] = transactions_result["inserted"]
                    report["storage"]["postgresql"]["transactions_updated"] = transactions_result["updated"]

                # Store liabilities
                if liabilities:
                    liabilities_result = self.storage.store_liabilities_postgresql(
                        liabilities, user_id, account_id_map, upload_id
                    )
                    report["storage"]["postgresql"]["liabilities_inserted"] = liabilities_result["inserted"]
                    report["storage"]["postgresql"]["liabilities_updated"] = liabilities_result["updated"]

            except Exception as e:
                logger.error(f"Error storing data in PostgreSQL: {str(e)}")
                report["status"] = "failed"
                report["errors"].append({
                    "type": "storage",
                    "field": "postgresql",
                    "error": f"Failed to store data in PostgreSQL: {str(e)}",
                    "severity": "error",
                })
                return report

            # Step 4: Store in S3 as Parquet
            logger.info(f"Storing data in S3 as Parquet for user {user_id}")
            try:
                s3_keys = self.storage.store_parquet_s3(parsed_data, user_id, upload_id)
                report["storage"]["s3"]["accounts_parquet"] = s3_keys.get("accounts")
                report["storage"]["s3"]["transactions_parquet"] = s3_keys.get("transactions")
                report["storage"]["s3"]["liabilities_parquet"] = s3_keys.get("liabilities")
            except Exception as e:
                logger.error(f"Error storing data in S3: {str(e)}")
                # Don't fail ingestion if S3 storage fails, but log it
                report["warnings"].append({
                    "type": "storage",
                    "field": "s3",
                    "error": f"Failed to store data in S3: {str(e)}",
                    "severity": "warning",
                })

            report["status"] = "completed"
            logger.info(f"Ingestion completed for user {user_id}")

        except Exception as e:
            logger.error(f"Unexpected error during ingestion: {str(e)}")
            report["status"] = "failed"
            report["errors"].append({
                "type": "ingestion",
                "field": "service",
                "error": f"Unexpected error: {str(e)}",
                "severity": "error",
            })

        return report

    def _get_account_id_map(
        self,
        accounts: List[Dict[str, Any]],
        user_id: uuid.UUID,
    ) -> Dict[str, uuid.UUID]:
        """
        Get mapping from Plaid account_id to database account.id.

        Args:
            accounts: List of account dictionaries
            user_id: User ID

        Returns:
            Dictionary mapping Plaid account_id to database account.id
        """
        account_id_map = {}

        for account in accounts:
            plaid_account_id = account.get("account_id")
            if not plaid_account_id:
                continue

            # Query database for account
            db_account = self.db.query(AccountModel).filter(
                AccountModel.user_id == user_id,
                AccountModel.account_id == plaid_account_id
            ).first()

            if db_account:
                account_id_map[plaid_account_id] = db_account.id

        return account_id_map

