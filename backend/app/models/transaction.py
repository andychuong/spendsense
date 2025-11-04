"""Transaction model for storing Plaid transaction data."""

import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Boolean, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class Transaction(Base):
    """Transaction model for storing Plaid transaction data."""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    transaction_id = Column(String(255), nullable=False, index=True)  # Plaid transaction_id
    date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    merchant_name = Column(String(255), nullable=True)
    merchant_entity_id = Column(String(255), nullable=True)
    payment_channel = Column(String(50), nullable=False)  # online, in_store, other
    category_primary = Column(String(100), nullable=False)
    category_detailed = Column(String(100), nullable=True)
    pending = Column(Boolean, default=False, nullable=False)
    iso_currency_code = Column(String(10), nullable=False, default="USD")
    upload_id = Column(UUID(as_uuid=True), ForeignKey("data_uploads.upload_id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_transactions_user_id_date", "user_id", "date"),
        Index("ix_transactions_account_id_date", "account_id", "date"),
        Index("ix_transactions_merchant_name", "merchant_name"),
        Index("ix_transactions_user_id_transaction_id", "user_id", "transaction_id"),
    )

    def __repr__(self) -> str:
        """String representation of Transaction."""
        return f"<Transaction(id={self.id}, transaction_id={self.transaction_id}, date={self.date}, amount={self.amount})>"

