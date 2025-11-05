"""Account model for storing Plaid account data."""

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, JSON, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class Account(Base):
    """Account model for storing Plaid account data."""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    account_id = Column(String(255), nullable=False, index=True)  # Plaid account_id
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # depository, credit, loan
    subtype = Column(String(50), nullable=False)  # checking, savings, credit card, money market, HSA, mortgage, student
    holder_category = Column(String(50), nullable=False)  # individual, business
    balance_available = Column(Numeric(15, 2), nullable=True)
    balance_current = Column(Numeric(15, 2), nullable=False)
    balance_limit = Column(Numeric(15, 2), nullable=True)
    iso_currency_code = Column(String(10), nullable=False, default="USD")
    mask = Column(String(20), nullable=True)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("data_uploads.upload_id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_accounts_user_id_account_id", "user_id", "account_id"),
        Index("ix_accounts_type_subtype", "type", "subtype"),
        CheckConstraint("holder_category IN ('individual', 'business')", name="check_holder_category"),
    )

    def __repr__(self) -> str:
        """String representation of Account."""
        return f"<Account(id={self.id}, account_id={self.account_id}, type={self.type}, subtype={self.subtype})>"


