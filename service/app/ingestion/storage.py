"""Data storage module for PostgreSQL and S3 Parquet."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io
import boto3
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session

# Import backend models and services
# Note: This assumes the service layer is run from the project root
# and can access backend models via relative imports or PYTHONPATH
try:
    # Try direct import if service is in same project structure
    from backend.app.models.account import Account as AccountModel
    from backend.app.models.transaction import Transaction as TransactionModel
    from backend.app.models.liability import Liability as LiabilityModel
    from backend.app.models.data_upload import DataUpload as DataUploadModel
    from backend.app.core.s3_service import get_s3_client
except ImportError:
    # Fallback: assume backend is in PYTHONPATH or use absolute imports
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.account import Account as AccountModel
    from app.models.transaction import Transaction as TransactionModel
    from app.models.liability import Liability as LiabilityModel
    from app.models.data_upload import DataUpload as DataUploadModel
    from app.core.s3_service import get_s3_client

logger = logging.getLogger(__name__)


class DataStorage:
    """Storage service for storing Plaid data in PostgreSQL and S3 Parquet."""

    def __init__(self, db_session: Session, s3_bucket: str = "spendsense-analytics"):
        """
        Initialize data storage.
        
        Args:
            db_session: SQLAlchemy database session
            s3_bucket: S3 bucket name for Parquet files
        """
        self.db = db_session
        self.s3_bucket = s3_bucket
        self.s3_client = get_s3_client()

    def store_accounts_postgresql(
        self,
        accounts: List[Dict[str, Any]],
        user_id: uuid.UUID,
        upload_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, int]:
        """
        Store accounts in PostgreSQL.
        
        Args:
            accounts: List of account dictionaries
            user_id: User ID
            upload_id: Upload ID (optional)
            
        Returns:
            Dictionary with counts: {'inserted': int, 'updated': int, 'errors': int}
        """
        inserted = 0
        updated = 0
        errors = 0
        
        for account_data in accounts:
            try:
                account_id_str = account_data.get("account_id")
                
                # Check if account already exists
                existing_account = self.db.query(AccountModel).filter(
                    AccountModel.user_id == user_id,
                    AccountModel.account_id == account_id_str
                ).first()
                
                # Extract balances
                balances = account_data.get("balances", {})
                balance_available = self._to_decimal(balances.get("available"))
                balance_current = self._to_decimal(balances.get("current"))
                balance_limit = self._to_decimal(balances.get("limit"))
                
                if existing_account:
                    # Update existing account
                    existing_account.name = account_data.get("name", "")
                    existing_account.type = account_data.get("type")
                    existing_account.subtype = account_data.get("subtype")
                    existing_account.holder_category = account_data.get("holder_category", "individual")
                    existing_account.balance_available = balance_available
                    existing_account.balance_current = balance_current
                    existing_account.balance_limit = balance_limit
                    existing_account.iso_currency_code = account_data.get("iso_currency_code", "USD")
                    existing_account.mask = account_data.get("mask")
                    existing_account.upload_id = upload_id
                    existing_account.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # Create new account
                    new_account = AccountModel(
                        user_id=user_id,
                        account_id=account_id_str,
                        name=account_data.get("name", ""),
                        type=account_data.get("type"),
                        subtype=account_data.get("subtype"),
                        holder_category=account_data.get("holder_category", "individual"),
                        balance_available=balance_available,
                        balance_current=balance_current,
                        balance_limit=balance_limit,
                        iso_currency_code=account_data.get("iso_currency_code", "USD"),
                        mask=account_data.get("mask"),
                        upload_id=upload_id,
                    )
                    self.db.add(new_account)
                    inserted += 1
                
            except Exception as e:
                logger.error(f"Error storing account {account_data.get('account_id')}: {str(e)}")
                errors += 1
        
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing accounts to database: {str(e)}")
            self.db.rollback()
            errors += inserted + updated
            inserted = 0
            updated = 0
        
        return {"inserted": inserted, "updated": updated, "errors": errors}

    def store_transactions_postgresql(
        self,
        transactions: List[Dict[str, Any]],
        user_id: uuid.UUID,
        account_id_map: Dict[str, uuid.UUID],  # Maps Plaid account_id to database account.id
        upload_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, int]:
        """
        Store transactions in PostgreSQL.
        
        Args:
            transactions: List of transaction dictionaries
            user_id: User ID
            account_id_map: Mapping from Plaid account_id to database account.id
            upload_id: Upload ID (optional)
            
        Returns:
            Dictionary with counts: {'inserted': int, 'updated': int, 'errors': int}
        """
        inserted = 0
        updated = 0
        errors = 0
        
        for transaction_data in transactions:
            try:
                transaction_id_str = transaction_data.get("transaction_id")
                plaid_account_id = transaction_data.get("account_id")
                
                # Get database account ID
                db_account_id = account_id_map.get(plaid_account_id)
                if not db_account_id:
                    logger.warning(f"Transaction references account_id '{plaid_account_id}' that doesn't exist")
                    errors += 1
                    continue
                
                # Check if transaction already exists
                existing_transaction = self.db.query(TransactionModel).filter(
                    TransactionModel.user_id == user_id,
                    TransactionModel.transaction_id == transaction_id_str
                ).first()
                
                # Parse date
                date_value = self._parse_date(transaction_data.get("date"))
                if not date_value:
                    logger.warning(f"Invalid date for transaction {transaction_id_str}")
                    errors += 1
                    continue
                
                # Extract category
                category = transaction_data.get("personal_finance_category", {})
                category_primary = category.get("primary", "")
                category_detailed = category.get("detailed")
                
                if existing_transaction:
                    # Update existing transaction
                    existing_transaction.account_id = db_account_id
                    existing_transaction.date = date_value
                    existing_transaction.amount = self._to_decimal(transaction_data.get("amount"))
                    existing_transaction.merchant_name = transaction_data.get("merchant_name")
                    existing_transaction.merchant_entity_id = transaction_data.get("merchant_entity_id")
                    existing_transaction.payment_channel = transaction_data.get("payment_channel", "other")
                    existing_transaction.category_primary = category_primary
                    existing_transaction.category_detailed = category_detailed
                    existing_transaction.pending = transaction_data.get("pending", False)
                    existing_transaction.iso_currency_code = transaction_data.get("iso_currency_code", "USD")
                    existing_transaction.upload_id = upload_id
                    updated += 1
                else:
                    # Create new transaction
                    new_transaction = TransactionModel(
                        account_id=db_account_id,
                        user_id=user_id,
                        transaction_id=transaction_id_str,
                        date=date_value,
                        amount=self._to_decimal(transaction_data.get("amount")),
                        merchant_name=transaction_data.get("merchant_name"),
                        merchant_entity_id=transaction_data.get("merchant_entity_id"),
                        payment_channel=transaction_data.get("payment_channel", "other"),
                        category_primary=category_primary,
                        category_detailed=category_detailed,
                        pending=transaction_data.get("pending", False),
                        iso_currency_code=transaction_data.get("iso_currency_code", "USD"),
                        upload_id=upload_id,
                    )
                    self.db.add(new_transaction)
                    inserted += 1
                
            except Exception as e:
                logger.error(f"Error storing transaction {transaction_data.get('transaction_id')}: {str(e)}")
                errors += 1
        
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing transactions to database: {str(e)}")
            self.db.rollback()
            errors += inserted + updated
            inserted = 0
            updated = 0
        
        return {"inserted": inserted, "updated": updated, "errors": errors}

    def store_liabilities_postgresql(
        self,
        liabilities: List[Dict[str, Any]],
        user_id: uuid.UUID,
        account_id_map: Dict[str, uuid.UUID],  # Maps Plaid account_id to database account.id
        upload_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, int]:
        """
        Store liabilities in PostgreSQL.
        
        Args:
            liabilities: List of liability dictionaries
            user_id: User ID
            account_id_map: Mapping from Plaid account_id to database account.id
            upload_id: Upload ID (optional)
            
        Returns:
            Dictionary with counts: {'inserted': int, 'updated': int, 'errors': int}
        """
        inserted = 0
        updated = 0
        errors = 0
        
        for liability_data in liabilities:
            try:
                plaid_account_id = liability_data.get("account_id")
                
                # Get database account ID
                db_account_id = account_id_map.get(plaid_account_id)
                if not db_account_id:
                    logger.warning(f"Liability references account_id '{plaid_account_id}' that doesn't exist")
                    errors += 1
                    continue
                
                # Check if liability already exists for this account
                existing_liability = self.db.query(LiabilityModel).filter(
                    LiabilityModel.user_id == user_id,
                    LiabilityModel.account_id == db_account_id
                ).first()
                
                # Parse dates
                last_payment_date = self._parse_date(liability_data.get("last_payment_date"))
                next_payment_due_date = self._parse_date(liability_data.get("next_payment_due_date"))
                
                if existing_liability:
                    # Update existing liability
                    existing_liability.apr_percentage = self._to_decimal(liability_data.get("apr_percentage"))
                    existing_liability.apr_type = liability_data.get("apr_type")
                    existing_liability.minimum_payment_amount = self._to_decimal(liability_data.get("minimum_payment_amount"))
                    existing_liability.last_payment_amount = self._to_decimal(liability_data.get("last_payment_amount"))
                    existing_liability.last_payment_date = last_payment_date
                    existing_liability.last_statement_balance = self._to_decimal(liability_data.get("last_statement_balance"))
                    existing_liability.is_overdue = liability_data.get("is_overdue")
                    existing_liability.next_payment_due_date = next_payment_due_date
                    existing_liability.interest_rate = self._to_decimal(liability_data.get("interest_rate"))
                    existing_liability.upload_id = upload_id
                    existing_liability.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # Create new liability
                    new_liability = LiabilityModel(
                        account_id=db_account_id,
                        user_id=user_id,
                        apr_percentage=self._to_decimal(liability_data.get("apr_percentage")),
                        apr_type=liability_data.get("apr_type"),
                        minimum_payment_amount=self._to_decimal(liability_data.get("minimum_payment_amount")),
                        last_payment_amount=self._to_decimal(liability_data.get("last_payment_amount")),
                        last_payment_date=last_payment_date,
                        last_statement_balance=self._to_decimal(liability_data.get("last_statement_balance")),
                        is_overdue=liability_data.get("is_overdue"),
                        next_payment_due_date=next_payment_due_date,
                        interest_rate=self._to_decimal(liability_data.get("interest_rate")),
                        upload_id=upload_id,
                    )
                    self.db.add(new_liability)
                    inserted += 1
                
            except Exception as e:
                logger.error(f"Error storing liability for account {liability_data.get('account_id')}: {str(e)}")
                errors += 1
        
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing liabilities to database: {str(e)}")
            self.db.rollback()
            errors += inserted + updated
            inserted = 0
            updated = 0
        
        return {"inserted": inserted, "updated": updated, "errors": errors}

    def store_parquet_s3(
        self,
        data: Dict[str, Any],
        user_id: uuid.UUID,
        upload_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, str]:
        """
        Store data in S3 as Parquet files.
        
        Args:
            data: Parsed Plaid data dictionary
            user_id: User ID
            upload_id: Upload ID (optional)
            
        Returns:
            Dictionary with S3 keys: {'accounts': str, 'transactions': str, 'liabilities': str}
        """
        s3_keys = {}
        ingestion_date = datetime.utcnow().date()
        
        # Store accounts as Parquet
        if data.get("accounts"):
            accounts_df = self._create_accounts_dataframe(data["accounts"], user_id, upload_id, ingestion_date)
            accounts_key = self._upload_parquet_to_s3(accounts_df, "accounts", user_id, ingestion_date)
            s3_keys["accounts"] = accounts_key
        
        # Store transactions as Parquet
        if data.get("transactions"):
            transactions_df = self._create_transactions_dataframe(data["transactions"], user_id, upload_id, ingestion_date)
            transactions_key = self._upload_parquet_to_s3(transactions_df, "transactions", user_id, ingestion_date)
            s3_keys["transactions"] = transactions_key
        
        # Store liabilities as Parquet
        if data.get("liabilities"):
            liabilities_df = self._create_liabilities_dataframe(data["liabilities"], user_id, upload_id, ingestion_date)
            liabilities_key = self._upload_parquet_to_s3(liabilities_df, "liabilities", user_id, ingestion_date)
            s3_keys["liabilities"] = liabilities_key
        
        return s3_keys

    def _create_accounts_dataframe(
        self,
        accounts: List[Dict[str, Any]],
        user_id: uuid.UUID,
        upload_id: Optional[uuid.UUID],
        ingestion_date: date,
    ) -> pd.DataFrame:
        """Create pandas DataFrame for accounts."""
        rows = []
        for account in accounts:
            balances = account.get("balances", {})
            row = {
                "user_id": str(user_id),
                "account_id": account.get("account_id"),
                "name": account.get("name", ""),
                "type": account.get("type"),
                "subtype": account.get("subtype"),
                "holder_category": account.get("holder_category", "individual"),
                "balance_available": balances.get("available"),
                "balance_current": balances.get("current"),
                "balance_limit": balances.get("limit"),
                "iso_currency_code": account.get("iso_currency_code", "USD"),
                "mask": account.get("mask"),
                "upload_id": str(upload_id) if upload_id else None,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "ingestion_date": ingestion_date.isoformat(),
            }
            rows.append(row)
        
        return pd.DataFrame(rows)

    def _create_transactions_dataframe(
        self,
        transactions: List[Dict[str, Any]],
        user_id: uuid.UUID,
        upload_id: Optional[uuid.UUID],
        ingestion_date: date,
    ) -> pd.DataFrame:
        """Create pandas DataFrame for transactions."""
        rows = []
        for transaction in transactions:
            category = transaction.get("personal_finance_category", {})
            row = {
                "user_id": str(user_id),
                "account_id": transaction.get("account_id"),
                "transaction_id": transaction.get("transaction_id"),
                "date": transaction.get("date"),
                "amount": transaction.get("amount"),
                "merchant_name": transaction.get("merchant_name"),
                "merchant_entity_id": transaction.get("merchant_entity_id"),
                "payment_channel": transaction.get("payment_channel", "other"),
                "category_primary": category.get("primary", ""),
                "category_detailed": category.get("detailed"),
                "pending": transaction.get("pending", False),
                "iso_currency_code": transaction.get("iso_currency_code", "USD"),
                "upload_id": str(upload_id) if upload_id else None,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "ingestion_date": ingestion_date.isoformat(),
            }
            rows.append(row)
        
        return pd.DataFrame(rows)

    def _create_liabilities_dataframe(
        self,
        liabilities: List[Dict[str, Any]],
        user_id: uuid.UUID,
        upload_id: Optional[uuid.UUID],
        ingestion_date: date,
    ) -> pd.DataFrame:
        """Create pandas DataFrame for liabilities."""
        rows = []
        for liability in liabilities:
            row = {
                "user_id": str(user_id),
                "account_id": liability.get("account_id"),
                "apr_percentage": liability.get("apr_percentage"),
                "apr_type": liability.get("apr_type"),
                "minimum_payment_amount": liability.get("minimum_payment_amount"),
                "last_payment_amount": liability.get("last_payment_amount"),
                "last_payment_date": liability.get("last_payment_date"),
                "last_statement_balance": liability.get("last_statement_balance"),
                "is_overdue": liability.get("is_overdue"),
                "next_payment_due_date": liability.get("next_payment_due_date"),
                "interest_rate": liability.get("interest_rate"),
                "upload_id": str(upload_id) if upload_id else None,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "ingestion_date": ingestion_date.isoformat(),
            }
            rows.append(row)
        
        return pd.DataFrame(rows)

    def _upload_parquet_to_s3(
        self,
        df: pd.DataFrame,
        data_type: str,  # accounts, transactions, liabilities
        user_id: uuid.UUID,
        ingestion_date: date,
    ) -> str:
        """Upload DataFrame to S3 as Parquet file."""
        # Generate S3 key
        s3_key = f"{data_type}/user_id={user_id}/ingestion_date={ingestion_date.isoformat()}/{data_type}.parquet"
        
        # Convert DataFrame to Parquet
        parquet_buffer = io.BytesIO()
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_buffer)
        parquet_buffer.seek(0)
        
        # Upload to S3
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=parquet_buffer.getvalue(),
                ServerSideEncryption="AES256",
                ContentType="application/octet-stream",
            )
            logger.info(f"Successfully uploaded {data_type} Parquet to S3: s3://{self.s3_bucket}/{s3_key}")
            return s3_key
        except ClientError as e:
            logger.error(f"Error uploading {data_type} Parquet to S3: {str(e)}")
            raise

    def _to_decimal(self, value: Any) -> Optional[Decimal]:
        """Convert value to Decimal."""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None

    def _parse_date(self, value: Any) -> Optional[date]:
        """Parse date string to date object."""
        if not value:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

