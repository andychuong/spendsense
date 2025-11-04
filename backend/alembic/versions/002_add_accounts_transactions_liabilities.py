"""Add accounts transactions liabilities tables

Revision ID: 002_accounts_transactions_liabilities
Revises: 001_initial
Create Date: 2025-11-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_accounts_transactions_liabilities'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('subtype', sa.String(length=50), nullable=False),
        sa.Column('holder_category', sa.String(length=50), nullable=False),
        sa.Column('balance_available', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('balance_current', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('balance_limit', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('iso_currency_code', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('mask', sa.String(length=20), nullable=True),
        sa.Column('upload_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['upload_id'], ['data_uploads.upload_id']),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("holder_category IN ('individual', 'business')", name='check_holder_category'),
    )
    op.create_index('ix_accounts_user_id', 'accounts', ['user_id'])
    op.create_index('ix_accounts_account_id', 'accounts', ['account_id'])
    op.create_index('ix_accounts_upload_id', 'accounts', ['upload_id'])
    op.create_index('ix_accounts_user_id_account_id', 'accounts', ['user_id', 'account_id'])
    op.create_index('ix_accounts_type_subtype', 'accounts', ['type', 'subtype'])

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', sa.String(length=255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('merchant_name', sa.String(length=255), nullable=True),
        sa.Column('merchant_entity_id', sa.String(length=255), nullable=True),
        sa.Column('payment_channel', sa.String(length=50), nullable=False),
        sa.Column('category_primary', sa.String(length=100), nullable=False),
        sa.Column('category_detailed', sa.String(length=100), nullable=True),
        sa.Column('pending', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('iso_currency_code', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('upload_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['upload_id'], ['data_uploads.upload_id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_transactions_account_id', 'transactions', ['account_id'])
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'])
    op.create_index('ix_transactions_transaction_id', 'transactions', ['transaction_id'])
    op.create_index('ix_transactions_date', 'transactions', ['date'])
    op.create_index('ix_transactions_upload_id', 'transactions', ['upload_id'])
    op.create_index('ix_transactions_user_id_date', 'transactions', ['user_id', 'date'])
    op.create_index('ix_transactions_account_id_date', 'transactions', ['account_id', 'date'])
    op.create_index('ix_transactions_merchant_name', 'transactions', ['merchant_name'])
    op.create_index('ix_transactions_user_id_transaction_id', 'transactions', ['user_id', 'transaction_id'])

    # Create liabilities table
    op.create_table(
        'liabilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('apr_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('apr_type', sa.String(length=50), nullable=True),
        sa.Column('minimum_payment_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('last_payment_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('last_payment_date', sa.Date(), nullable=True),
        sa.Column('last_statement_balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('is_overdue', sa.Boolean(), nullable=True),
        sa.Column('next_payment_due_date', sa.Date(), nullable=True),
        sa.Column('interest_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('upload_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['upload_id'], ['data_uploads.upload_id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_liabilities_account_id', 'liabilities', ['account_id'])
    op.create_index('ix_liabilities_user_id', 'liabilities', ['user_id'])
    op.create_index('ix_liabilities_upload_id', 'liabilities', ['upload_id'])
    op.create_index('ix_liabilities_next_payment_due_date', 'liabilities', ['next_payment_due_date'])
    op.create_index('ix_liabilities_user_id_account_id', 'liabilities', ['user_id', 'account_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_liabilities_user_id_account_id', table_name='liabilities')
    op.drop_index('ix_liabilities_next_payment_due_date', table_name='liabilities')
    op.drop_index('ix_liabilities_upload_id', table_name='liabilities')
    op.drop_index('ix_liabilities_user_id', table_name='liabilities')
    op.drop_index('ix_liabilities_account_id', table_name='liabilities')
    op.drop_index('ix_transactions_user_id_transaction_id', table_name='transactions')
    op.drop_index('ix_transactions_merchant_name', table_name='transactions')
    op.drop_index('ix_transactions_account_id_date', table_name='transactions')
    op.drop_index('ix_transactions_user_id_date', table_name='transactions')
    op.drop_index('ix_transactions_upload_id', table_name='transactions')
    op.drop_index('ix_transactions_date', table_name='transactions')
    op.drop_index('ix_transactions_transaction_id', table_name='transactions')
    op.drop_index('ix_transactions_user_id', table_name='transactions')
    op.drop_index('ix_transactions_account_id', table_name='transactions')
    op.drop_index('ix_accounts_type_subtype', table_name='accounts')
    op.drop_index('ix_accounts_user_id_account_id', table_name='accounts')
    op.drop_index('ix_accounts_upload_id', table_name='accounts')
    op.drop_index('ix_accounts_account_id', table_name='accounts')
    op.drop_index('ix_accounts_user_id', table_name='accounts')

    # Drop tables
    op.drop_table('liabilities')
    op.drop_table('transactions')
    op.drop_table('accounts')

