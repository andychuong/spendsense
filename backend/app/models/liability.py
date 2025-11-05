"""Liability model for storing Plaid liability data (credit cards, mortgages, student loans)."""

import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Boolean, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class Liability(Base):
    """Liability model for storing Plaid liability data."""

    __tablename__ = "liabilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)

    # Credit card specific fields
    apr_percentage = Column(Numeric(5, 2), nullable=True)  # APR percentage (0-100)
    apr_type = Column(String(50), nullable=True)  # purchase, cash, balance_transfer
    minimum_payment_amount = Column(Numeric(15, 2), nullable=True)
    last_payment_amount = Column(Numeric(15, 2), nullable=True)
    last_payment_date = Column(Date, nullable=True)
    last_statement_balance = Column(Numeric(15, 2), nullable=True)
    is_overdue = Column(Boolean, default=False, nullable=True)
    next_payment_due_date = Column(Date, nullable=True, index=True)

    # Mortgage/Student loan specific fields
    interest_rate = Column(Numeric(5, 2), nullable=True)  # Interest rate percentage (0-100)

    upload_id = Column(UUID(as_uuid=True), ForeignKey("data_uploads.upload_id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_liabilities_user_id_account_id", "user_id", "account_id"),
        Index("ix_liabilities_account_id", "account_id"),
        Index("ix_liabilities_next_payment_due_date", "next_payment_due_date"),
    )

    def __repr__(self) -> str:
        """String representation of Liability."""
        return f"<Liability(id={self.id}, account_id={self.account_id}, apr_percentage={self.apr_percentage})>"


