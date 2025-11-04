"""Account, Transaction, and Liability schemas for admin user detail view."""

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import uuid


class AccountResponse(BaseModel):
    """Account response schema."""

    id: str
    user_id: str
    account_id: str
    name: str
    type: str
    subtype: str
    holder_category: str
    balance_available: Optional[Decimal] = None
    balance_current: Decimal
    balance_limit: Optional[Decimal] = None
    iso_currency_code: str = "USD"
    mask: Optional[str] = None
    upload_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('id', 'user_id', 'upload_id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string if needed."""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Transaction response schema."""

    id: str
    account_id: str
    user_id: str
    transaction_id: str
    date: date
    amount: Decimal
    merchant_name: Optional[str] = None
    merchant_entity_id: Optional[str] = None
    payment_channel: str
    category_primary: str
    category_detailed: Optional[str] = None
    pending: bool = False
    iso_currency_code: str = "USD"
    upload_id: Optional[str] = None
    created_at: datetime

    @field_validator('id', 'account_id', 'user_id', 'upload_id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string if needed."""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class LiabilityResponse(BaseModel):
    """Liability response schema."""

    id: str
    account_id: str
    user_id: str
    apr_percentage: Optional[Decimal] = None
    apr_type: Optional[str] = None
    minimum_payment_amount: Optional[Decimal] = None
    last_payment_amount: Optional[Decimal] = None
    last_payment_date: Optional[date] = None
    last_statement_balance: Optional[Decimal] = None
    is_overdue: Optional[bool] = None
    next_payment_due_date: Optional[date] = None
    interest_rate: Optional[Decimal] = None
    upload_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('id', 'account_id', 'user_id', 'upload_id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string if needed."""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class TransactionsListResponse(BaseModel):
    """Transactions list response with pagination."""

    items: List[TransactionResponse]
    total: int
    skip: int = 0
    limit: int = 100

    class Config:
        from_attributes = True


class AccountsListResponse(BaseModel):
    """Accounts list response."""

    items: List[AccountResponse]
    total: int

    class Config:
        from_attributes = True


class LiabilitiesListResponse(BaseModel):
    """Liabilities list response."""

    items: List[LiabilityResponse]
    total: int

    class Config:
        from_attributes = True

