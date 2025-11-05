"""Plaid data schema validator."""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, date, timedelta
from collections import Counter

logger = logging.getLogger(__name__)

# Valid account types and subtypes
VALID_ACCOUNT_TYPES = ["depository", "credit", "loan"]
VALID_ACCOUNT_SUBTYPES = {
    "depository": ["checking", "savings", "money market", "HSA"],
    "credit": ["credit card"],
    "loan": ["mortgage", "student", "auto"],
}
VALID_HOLDER_CATEGORIES = ["individual", "business"]
VALID_PAYMENT_CHANNELS = ["online", "in_store", "other", "ACH"]
VALID_APR_TYPES = ["purchase", "cash", "balance_transfer"]


class ValidationError:
    """Represents a validation error."""

    def __init__(self, type: str, field: str, value: Any, message: str, severity: str = "error"):
        self.type = type  # account, transaction, liability
        self.field = field
        self.value = value
        self.message = message
        self.severity = severity  # error, warning

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "field": self.field,
            "value": str(self.value) if self.value is not None else None,
            "error": self.message,
            "severity": self.severity,
        }


class PlaidValidator:
    """Validator for Plaid data schema."""

    # Date range validation (reasonable ranges)
    MIN_DATE = date(1900, 1, 1)  # Minimum date (realistic for financial data)
    MAX_DATE = date.today() + timedelta(days=365)  # Maximum date (1 year in future for pending transactions)

    # Amount range validation (reasonable transaction amounts)
    MIN_TRANSACTION_AMOUNT = -1000000.0  # Minimum transaction amount ($1M in negative)
    MAX_TRANSACTION_AMOUNT = 1000000.0   # Maximum transaction amount ($1M in positive)

    # Amount range validation for account balances
    MIN_BALANCE = -10000000.0  # Minimum balance ($10M in negative)
    MAX_BALANCE = 10000000.0   # Maximum balance ($10M in positive)

    def __init__(self, enable_duplicate_detection: bool = True, enable_range_validation: bool = True):
        """
        Initialize the Plaid validator.

        Args:
            enable_duplicate_detection: Enable duplicate account/transaction detection
            enable_range_validation: Enable data range validation (dates, amounts)
        """
        self.enable_duplicate_detection = enable_duplicate_detection
        self.enable_range_validation = enable_range_validation

    def validate_account(self, account: Dict[str, Any], account_index: Optional[int] = None) -> List[ValidationError]:
        """
        Validate account structure.

        Args:
            account: Account dictionary
            account_index: Index of account in list (for error reporting)

        Returns:
            List of validation errors
        """
        errors = []
        prefix = f"account[{account_index}]" if account_index is not None else "account"

        # Required fields
        required_fields = ["account_id", "type", "subtype", "balances", "iso_currency_code"]
        for field in required_fields:
            if field not in account:
                errors.append(ValidationError(
                    type="account",
                    field=field,
                    value=None,
                    message=f"Missing required field: {field}",
                    severity="error"
                ))

        # Validate account_id
        if "account_id" in account:
            account_id = account["account_id"]
            if not account_id or not isinstance(account_id, str):
                errors.append(ValidationError(
                    type="account",
                    field="account_id",
                    value=account_id,
                    message="account_id must be a non-empty string",
                    severity="error"
                ))

        # Validate type
        if "type" in account:
            account_type = account["type"]
            if account_type not in VALID_ACCOUNT_TYPES:
                errors.append(ValidationError(
                    type="account",
                    field="type",
                    value=account_type,
                    message=f"Invalid account type: {account_type}. Valid types: {', '.join(VALID_ACCOUNT_TYPES)}",
                    severity="error"
                ))

        # Validate subtype
        if "type" in account and "subtype" in account:
            account_type = account.get("type")
            subtype = account.get("subtype")
            if account_type in VALID_ACCOUNT_SUBTYPES:
                valid_subtypes = VALID_ACCOUNT_SUBTYPES[account_type]
                if subtype not in valid_subtypes:
                    errors.append(ValidationError(
                        type="account",
                        field="subtype",
                        value=subtype,
                        message=f"Invalid subtype '{subtype}' for type '{account_type}'. Valid subtypes: {', '.join(valid_subtypes)}",
                        severity="error"
                    ))

        # Validate holder_category
        if "holder_category" in account:
            holder_category = account["holder_category"]
            if holder_category not in VALID_HOLDER_CATEGORIES:
                errors.append(ValidationError(
                    type="account",
                    field="holder_category",
                    value=holder_category,
                    message=f"Invalid holder_category: {holder_category}. Valid categories: {', '.join(VALID_HOLDER_CATEGORIES)}",
                    severity="error"
                ))
            # Exclude business accounts
            if holder_category != "individual":
                errors.append(ValidationError(
                    type="account",
                    field="holder_category",
                    value=holder_category,
                    message=f"Business accounts are excluded. holder_category must be 'individual'",
                    severity="error"
                ))

        # Validate balances
        if "balances" in account:
            balances = account["balances"]
            if not isinstance(balances, dict):
                errors.append(ValidationError(
                    type="account",
                    field="balances",
                    value=balances,
                    message="balances must be a dictionary",
                    severity="error"
                ))
            else:
                # Validate balance values
                for balance_key in ["available", "current", "limit"]:
                    if balance_key in balances:
                        balance_value = balances[balance_key]
                        if balance_value is not None:
                            try:
                                balance_float = float(balance_value)

                                # Range validation
                                if self.enable_range_validation:
                                    if balance_float < self.MIN_BALANCE:
                                        errors.append(ValidationError(
                                            type="account",
                                            field=f"balances.{balance_key}",
                                            value=balance_value,
                                            message=f"balance.{balance_key} {balance_float} is below minimum {self.MIN_BALANCE}",
                                            severity="warning"
                                        ))
                                    elif balance_float > self.MAX_BALANCE:
                                        errors.append(ValidationError(
                                            type="account",
                                            field=f"balances.{balance_key}",
                                            value=balance_value,
                                            message=f"balance.{balance_key} {balance_float} is above maximum {self.MAX_BALANCE}",
                                            severity="warning"
                                        ))
                            except (ValueError, TypeError):
                                errors.append(ValidationError(
                                    type="account",
                                    field=f"balances.{balance_key}",
                                    value=balance_value,
                                    message=f"balance.{balance_key} must be a number or null",
                                    severity="error"
                                ))

        # Validate iso_currency_code
        if "iso_currency_code" in account:
            iso_code = account["iso_currency_code"]
            if not iso_code or not isinstance(iso_code, str):
                errors.append(ValidationError(
                    type="account",
                    field="iso_currency_code",
                    value=iso_code,
                    message="iso_currency_code must be a non-empty string",
                    severity="error"
                ))

        return errors

    def validate_transaction(self, transaction: Dict[str, Any], transaction_index: Optional[int] = None) -> List[ValidationError]:
        """
        Validate transaction structure.

        Args:
            transaction: Transaction dictionary
            transaction_index: Index of transaction in list (for error reporting)

        Returns:
            List of validation errors
        """
        errors = []
        prefix = f"transaction[{transaction_index}]" if transaction_index is not None else "transaction"

        # Required fields
        required_fields = ["account_id", "date", "amount"]
        for field in required_fields:
            if field not in transaction:
                errors.append(ValidationError(
                    type="transaction",
                    field=field,
                    value=None,
                    message=f"Missing required field: {field}",
                    severity="error"
                ))

        # Validate transaction_id
        if "transaction_id" in transaction:
            transaction_id = transaction["transaction_id"]
            if not transaction_id or not isinstance(transaction_id, str):
                errors.append(ValidationError(
                    type="transaction",
                    field="transaction_id",
                    value=transaction_id,
                    message="transaction_id must be a non-empty string",
                    severity="error"
                ))

        # Validate account_id
        if "account_id" in transaction:
            account_id = transaction["account_id"]
            if not account_id or not isinstance(account_id, str):
                errors.append(ValidationError(
                    type="transaction",
                    field="account_id",
                    value=account_id,
                    message="account_id must be a non-empty string",
                    severity="error"
                ))

        # Validate date
        if "date" in transaction:
            date_value = transaction["date"]
            if not date_value:
                errors.append(ValidationError(
                    type="transaction",
                    field="date",
                    value=date_value,
                    message="date is required",
                    severity="error"
                ))
            else:
                try:
                    # Try to parse date format YYYY-MM-DD
                    parsed_date = datetime.strptime(str(date_value), "%Y-%m-%d").date()

                    # Range validation
                    if self.enable_range_validation:
                        if parsed_date < self.MIN_DATE:
                            errors.append(ValidationError(
                                type="transaction",
                                field="date",
                                value=date_value,
                                message=f"date {date_value} is before minimum date {self.MIN_DATE.isoformat()}",
                                severity="error"
                            ))
                        elif parsed_date > self.MAX_DATE:
                            errors.append(ValidationError(
                                type="transaction",
                                field="date",
                                value=date_value,
                                message=f"date {date_value} is after maximum date {self.MAX_DATE.isoformat()}",
                                severity="warning"
                            ))
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        type="transaction",
                        field="date",
                        value=date_value,
                        message="date must be in format YYYY-MM-DD",
                        severity="error"
                    ))

        # Validate amount
        if "amount" in transaction:
            amount = transaction["amount"]
            if amount is None:
                errors.append(ValidationError(
                    type="transaction",
                    field="amount",
                    value=amount,
                    message="amount is required",
                    severity="error"
                ))
            else:
                try:
                    amount_float = float(amount)
                    if amount_float == 0:
                        errors.append(ValidationError(
                            type="transaction",
                            field="amount",
                            value=amount,
                            message="amount must be non-zero",
                            severity="warning"
                        ))

                    # Range validation
                    if self.enable_range_validation:
                        if amount_float < self.MIN_TRANSACTION_AMOUNT:
                            errors.append(ValidationError(
                                type="transaction",
                                field="amount",
                                value=amount,
                                message=f"amount {amount_float} is below minimum {self.MIN_TRANSACTION_AMOUNT}",
                                severity="warning"
                            ))
                        elif amount_float > self.MAX_TRANSACTION_AMOUNT:
                            errors.append(ValidationError(
                                type="transaction",
                                field="amount",
                                value=amount,
                                message=f"amount {amount_float} is above maximum {self.MAX_TRANSACTION_AMOUNT}",
                                severity="warning"
                            ))
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        type="transaction",
                        field="amount",
                        value=amount,
                        message="amount must be a number",
                        severity="error"
                    ))

        # Validate payment_channel
        if "payment_channel" in transaction:
            payment_channel = transaction["payment_channel"]
            if payment_channel not in VALID_PAYMENT_CHANNELS:
                errors.append(ValidationError(
                    type="transaction",
                    field="payment_channel",
                    value=payment_channel,
                    message=f"Invalid payment_channel: {payment_channel}. Valid channels: {', '.join(VALID_PAYMENT_CHANNELS)}",
                    severity="error"
                ))

        # Validate personal_finance_category
        if "personal_finance_category" in transaction:
            category = transaction["personal_finance_category"]
            if not isinstance(category, dict):
                errors.append(ValidationError(
                    type="transaction",
                    field="personal_finance_category",
                    value=category,
                    message="personal_finance_category must be a dictionary",
                    severity="error"
                ))
            elif "primary" not in category:
                errors.append(ValidationError(
                    type="transaction",
                    field="personal_finance_category.primary",
                    value=None,
                    message="personal_finance_category.primary is required",
                    severity="error"
                ))

        # Validate pending
        if "pending" in transaction:
            pending = transaction["pending"]
            if not isinstance(pending, bool):
                errors.append(ValidationError(
                    type="transaction",
                    field="pending",
                    value=pending,
                    message="pending must be a boolean",
                    severity="error"
                ))

        return errors

    def validate_liability(self, liability: Dict[str, Any], liability_index: Optional[int] = None) -> List[ValidationError]:
        """
        Validate liability structure.

        Args:
            liability: Liability dictionary
            liability_index: Index of liability in list (for error reporting)

        Returns:
            List of validation errors
        """
        errors = []

        # Required field: account_id
        if "account_id" not in liability:
            errors.append(ValidationError(
                type="liability",
                field="account_id",
                value=None,
                message="Missing required field: account_id",
                severity="error"
            ))

        # Validate account_id
        if "account_id" in liability:
            account_id = liability["account_id"]
            if not account_id or not isinstance(account_id, str):
                errors.append(ValidationError(
                    type="liability",
                    field="account_id",
                    value=account_id,
                    message="account_id must be a non-empty string",
                    severity="error"
                ))

        # Validate APR fields (for credit cards)
        if "apr_percentage" in liability and liability["apr_percentage"] is not None:
            apr_percentage = liability["apr_percentage"]
            try:
                apr_float = float(apr_percentage)
                if apr_float < 0 or apr_float > 100:
                    errors.append(ValidationError(
                        type="liability",
                        field="apr_percentage",
                        value=apr_percentage,
                        message="apr_percentage must be between 0 and 100",
                        severity="error"
                    ))
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    type="liability",
                    field="apr_percentage",
                    value=apr_percentage,
                    message="apr_percentage must be a number",
                    severity="error"
                ))

        if "apr_type" in liability and liability["apr_type"] is not None:
            apr_type = liability["apr_type"]
            if apr_type not in VALID_APR_TYPES:
                errors.append(ValidationError(
                    type="liability",
                    field="apr_type",
                    value=apr_type,
                    message=f"Invalid apr_type: {apr_type}. Valid types: {', '.join(VALID_APR_TYPES)}",
                    severity="error"
                ))

        # Validate date fields
        date_fields = ["last_payment_date", "next_payment_due_date"]
        for field in date_fields:
            if field in liability and liability[field] is not None:
                date_value = liability[field]
                try:
                    parsed_date = datetime.strptime(str(date_value), "%Y-%m-%d").date()

                    # Range validation
                    if self.enable_range_validation:
                        if parsed_date < self.MIN_DATE:
                            errors.append(ValidationError(
                                type="liability",
                                field=field,
                                value=date_value,
                                message=f"{field} {date_value} is before minimum date {self.MIN_DATE.isoformat()}",
                                severity="error"
                            ))
                        elif parsed_date > self.MAX_DATE:
                            errors.append(ValidationError(
                                type="liability",
                                field=field,
                                value=date_value,
                                message=f"{field} {date_value} is after maximum date {self.MAX_DATE.isoformat()}",
                                severity="warning"
                            ))
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        type="liability",
                        field=field,
                        value=date_value,
                        message=f"{field} must be in format YYYY-MM-DD",
                        severity="error"
                    ))

        # Validate is_overdue
        if "is_overdue" in liability and liability["is_overdue"] is not None:
            is_overdue = liability["is_overdue"]
            if not isinstance(is_overdue, bool):
                errors.append(ValidationError(
                    type="liability",
                    field="is_overdue",
                    value=is_overdue,
                    message="is_overdue must be a boolean",
                    severity="error"
                ))

        # Validate interest_rate (for mortgages/student loans)
        if "interest_rate" in liability and liability["interest_rate"] is not None:
            interest_rate = liability["interest_rate"]
            try:
                rate_float = float(interest_rate)
                if rate_float < 0 or rate_float > 100:
                    errors.append(ValidationError(
                        type="liability",
                        field="interest_rate",
                        value=interest_rate,
                        message="interest_rate must be between 0 and 100",
                        severity="error"
                    ))
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    type="liability",
                    field="interest_rate",
                    value=interest_rate,
                    message="interest_rate must be a number",
                    severity="error"
                ))

        return errors

    def _detect_duplicate_accounts(self, accounts: List[Dict[str, Any]]) -> List[ValidationError]:
        """
        Detect duplicate accounts based on account_id.

        Args:
            accounts: List of account dictionaries

        Returns:
            List of validation errors for duplicates
        """
        errors = []
        account_ids = [acc.get("account_id") for acc in accounts if acc.get("account_id")]
        duplicates = [account_id for account_id, count in Counter(account_ids).items() if count > 1]

        for duplicate_id in duplicates:
            # Find indices of duplicate accounts
            duplicate_indices = [i for i, acc in enumerate(accounts) if acc.get("account_id") == duplicate_id]
            errors.append(ValidationError(
                type="account",
                field="account_id",
                value=duplicate_id,
                message=f"Duplicate account_id '{duplicate_id}' found at indices {duplicate_indices}",
                severity="error"
            ))
            logger.warning(f"Duplicate account_id detected: {duplicate_id} (found {len(duplicate_indices)} times)")

        return errors

    def _detect_duplicate_transactions(self, transactions: List[Dict[str, Any]]) -> List[ValidationError]:
        """
        Detect duplicate transactions based on transaction_id.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            List of validation errors for duplicates
        """
        errors = []
        transaction_ids = [txn.get("transaction_id") for txn in transactions if txn.get("transaction_id")]
        duplicates = [txn_id for txn_id, count in Counter(transaction_ids).items() if count > 1]

        for duplicate_id in duplicates:
            # Find indices of duplicate transactions
            duplicate_indices = [i for i, txn in enumerate(transactions) if txn.get("transaction_id") == duplicate_id]
            errors.append(ValidationError(
                type="transaction",
                field="transaction_id",
                value=duplicate_id,
                message=f"Duplicate transaction_id '{duplicate_id}' found at indices {duplicate_indices}",
                severity="error"
            ))
            logger.warning(f"Duplicate transaction_id detected: {duplicate_id} (found {len(duplicate_indices)} times)")

        return errors

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate Plaid data structure.

        Args:
            data: Parsed Plaid data dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        logger.info("Starting Plaid data validation")

        # Validate accounts
        accounts = data.get("accounts", [])
        if not isinstance(accounts, list):
            errors.append(ValidationError(
                type="data",
                field="accounts",
                value=accounts,
                message="accounts must be a list",
                severity="error"
            ))
            logger.error(f"Invalid accounts structure: {type(accounts)}")
        else:
            logger.info(f"Validating {len(accounts)} accounts")

            # Duplicate detection for accounts
            if self.enable_duplicate_detection:
                duplicate_errors = self._detect_duplicate_accounts(accounts)
                errors.extend(duplicate_errors)

            # Validate each account
            for i, account in enumerate(accounts):
                account_errors = self.validate_account(account, i)
                errors.extend(account_errors)

                # Log account validation errors
                if account_errors:
                    error_count = sum(1 for e in account_errors if e.severity == "error")
                    warning_count = sum(1 for e in account_errors if e.severity == "warning")
                    logger.warning(f"Account {i} ({account.get('account_id', 'unknown')}): {error_count} errors, {warning_count} warnings")

        # Validate transactions
        transactions = data.get("transactions", [])
        if not isinstance(transactions, list):
            errors.append(ValidationError(
                type="data",
                field="transactions",
                value=transactions,
                message="transactions must be a list",
                severity="error"
            ))
            logger.error(f"Invalid transactions structure: {type(transactions)}")
        else:
            logger.info(f"Validating {len(transactions)} transactions")

            # Duplicate detection for transactions
            if self.enable_duplicate_detection:
                duplicate_errors = self._detect_duplicate_transactions(transactions)
                errors.extend(duplicate_errors)

            # Validate each transaction
            for i, transaction in enumerate(transactions):
                transaction_errors = self.validate_transaction(transaction, i)
                errors.extend(transaction_errors)

                # Cross-reference: validate transaction account_id exists in accounts
                if "account_id" in transaction:
                    account_id = transaction["account_id"]
                    account_ids = [acc.get("account_id") for acc in accounts if "account_id" in acc]
                    if account_id not in account_ids:
                        errors.append(ValidationError(
                            type="transaction",
                            field="account_id",
                            value=account_id,
                            message=f"Transaction references account_id '{account_id}' that does not exist in accounts",
                            severity="error"
                        ))
                        logger.warning(f"Transaction {i} references non-existent account_id: {account_id}")

                # Log transaction validation errors (only if significant)
                if transaction_errors and len(transaction_errors) > 2:
                    error_count = sum(1 for e in transaction_errors if e.severity == "error")
                    warning_count = sum(1 for e in transaction_errors if e.severity == "warning")
                    logger.warning(f"Transaction {i} ({transaction.get('transaction_id', 'unknown')}): {error_count} errors, {warning_count} warnings")

        # Validate liabilities (optional)
        liabilities = data.get("liabilities", [])
        if liabilities:
            if not isinstance(liabilities, list):
                errors.append(ValidationError(
                    type="data",
                    field="liabilities",
                    value=liabilities,
                    message="liabilities must be a list",
                    severity="error"
                ))
                logger.error(f"Invalid liabilities structure: {type(liabilities)}")
            else:
                logger.info(f"Validating {len(liabilities)} liabilities")

                # Validate each liability
                for i, liability in enumerate(liabilities):
                    liability_errors = self.validate_liability(liability, i)
                    errors.extend(liability_errors)

                    # Cross-reference: validate liability account_id exists in accounts
                    if "account_id" in liability:
                        account_id = liability["account_id"]
                        account_ids = [acc.get("account_id") for acc in accounts if "account_id" in acc]
                        if account_id not in account_ids:
                            errors.append(ValidationError(
                                type="liability",
                                field="account_id",
                                value=account_id,
                                message=f"Liability references account_id '{account_id}' that does not exist in accounts",
                                severity="error"
                            ))
                            logger.warning(f"Liability {i} references non-existent account_id: {account_id}")

        # Separate errors and warnings
        error_count = sum(1 for e in errors if e.severity == "error")
        warning_count = sum(1 for e in errors if e.severity == "warning")

        is_valid = error_count == 0

        # Log validation summary
        logger.info(f"Validation complete: {error_count} errors, {warning_count} warnings. Valid: {is_valid}")
        if error_count > 0:
            logger.error(f"Validation failed with {error_count} errors")
        if warning_count > 0:
            logger.warning(f"Validation completed with {warning_count} warnings")

        return is_valid, errors

