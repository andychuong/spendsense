"""add_name_to_users

Revision ID: dbad1091a604
Revises: 002_accounts_transactions_liabilities
Create Date: 2025-11-04 14:41:25.657226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbad1091a604'
down_revision = '002_accounts_transactions_liabilities'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add name column to users table
    op.add_column('users', sa.Column('name', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove name column from users table
    op.drop_column('users', 'name')

