"""Plaid data parser for JSON and CSV formats."""

import json
import csv
import io
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PlaidParser:
    """Parser for Plaid-style transaction data (JSON and CSV formats)."""

    def __init__(self):
        """Initialize the Plaid parser."""
        pass

    def parse_json(self, file_content: bytes) -> Dict[str, Any]:
        """
        Parse Plaid JSON data format.

        Args:
            file_content: Raw file content as bytes

        Returns:
            Dictionary with 'accounts', 'transactions', and optional 'user_id', 'upload_timestamp'

        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            data = json.loads(file_content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

        # Validate top-level structure
        if not isinstance(data, dict):
            raise ValueError("JSON data must be a dictionary")

        # Extract accounts, transactions
        accounts = data.get("accounts", [])
        transactions = data.get("transactions", [])

        if not isinstance(accounts, list):
            raise ValueError("'accounts' must be a list")
        if not isinstance(transactions, list):
            raise ValueError("'transactions' must be a list")

        return {
            "user_id": data.get("user_id"),
            "upload_timestamp": data.get("upload_timestamp"),
            "accounts": accounts,
            "transactions": transactions,
        }

    def parse_csv(self, file_content: bytes) -> Dict[str, Any]:
        """
        Parse Plaid CSV data format.

        CSV format expects separate sections for accounts, transactions, and liabilities.
        Sections are separated by empty lines or headers.

        Args:
            file_content: Raw file content as bytes

        Returns:
            Dictionary with 'accounts', 'transactions', and optional 'liabilities'

        Raises:
            ValueError: If CSV format is invalid
        """
        try:
            content = file_content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))

            # Read all rows
            rows = list(reader)

            if not rows:
                raise ValueError("CSV file is empty")

            # Determine section by checking column names
            first_row = rows[0]

            # Check if this is accounts section
            if "account_id" in first_row and "account_name" in first_row:
                accounts = self._parse_accounts_csv(rows)
                return {"accounts": accounts, "transactions": [], "liabilities": []}

            # Check if this is transactions section
            elif "transaction_id" in first_row and "account_id" in first_row:
                transactions = self._parse_transactions_csv(rows)
                return {"accounts": [], "transactions": transactions, "liabilities": []}

            # Check if this is liabilities section
            elif "liability_account_id" in first_row or "account_id" in first_row:
                liabilities = self._parse_liabilities_csv(rows)
                return {"accounts": [], "transactions": [], "liabilities": liabilities}

            else:
                raise ValueError("CSV format not recognized. Expected columns: account_id, transaction_id, or liability_account_id")

        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")

    def _parse_accounts_csv(self, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Parse accounts from CSV rows."""
        accounts = []
        for row in rows:
            account = {
                "account_id": row.get("account_id"),
                "name": row.get("account_name", ""),
                "type": row.get("account_type", ""),
                "subtype": row.get("account_subtype", ""),
                "holder_category": row.get("holder_category", "individual"),
                "balances": {
                    "available": self._parse_decimal(row.get("balance_available")),
                    "current": self._parse_decimal(row.get("balance_current")),
                    "limit": self._parse_decimal(row.get("balance_limit")),
                },
                "iso_currency_code": row.get("iso_currency_code", "USD"),
                "mask": row.get("mask"),
            }
            accounts.append(account)
        return accounts

    def _parse_transactions_csv(self, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Parse transactions from CSV rows."""
        transactions = []
        for row in rows:
            transaction = {
                "transaction_id": row.get("transaction_id"),
                "account_id": row.get("account_id"),
                "date": row.get("date"),
                "amount": self._parse_decimal(row.get("amount")),
                "merchant_name": row.get("merchant_name"),
                "merchant_entity_id": row.get("merchant_entity_id"),
                "payment_channel": row.get("payment_channel", "other"),
                "personal_finance_category": {
                    "primary": row.get("category_primary", ""),
                    "detailed": row.get("category_detailed", ""),
                },
                "pending": row.get("pending", "false").lower() == "true",
                "iso_currency_code": row.get("iso_currency_code", "USD"),
            }
            transactions.append(transaction)
        return transactions

    def _parse_liabilities_csv(self, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Parse liabilities from CSV rows."""
        liabilities = []
        for row in rows:
            liability = {
                "account_id": row.get("liability_account_id") or row.get("account_id"),
                "apr_percentage": self._parse_decimal(row.get("apr_percentage")),
                "apr_type": row.get("apr_type"),
                "minimum_payment_amount": self._parse_decimal(row.get("minimum_payment_amount")),
                "last_payment_amount": self._parse_decimal(row.get("last_payment_amount")),
                "last_payment_date": row.get("last_payment_date"),
                "last_statement_balance": self._parse_decimal(row.get("last_statement_balance")),
                "is_overdue": row.get("is_overdue", "false").lower() == "true",
                "next_payment_due_date": row.get("next_payment_due_date"),
                "interest_rate": self._parse_decimal(row.get("interest_rate")),
            }
            liabilities.append(liability)
        return liabilities

    def _parse_decimal(self, value: Optional[str]) -> Optional[float]:
        """Parse decimal string to float, handling None and empty strings."""
        if not value or value.strip() == "":
            return None
        try:
            return float(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None

    def parse(self, file_content: bytes, file_type: str) -> Dict[str, Any]:
        """
        Parse Plaid data from file content.

        Args:
            file_content: Raw file content as bytes
            file_type: File type ('json' or 'csv')

        Returns:
            Dictionary with parsed data

        Raises:
            ValueError: If file type is unsupported or parsing fails
        """
        if file_type.lower() == "json":
            return self.parse_json(file_content)
        elif file_type.lower() == "csv":
            return self.parse_csv(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Supported types: json, csv")
