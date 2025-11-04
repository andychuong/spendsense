"""add_monthly_income_to_users

Revision ID: 916ff7d6f997
Revises: 0b436e74aaff
Create Date: 2025-11-04 15:31:26.823653

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '916ff7d6f997'
down_revision = '0b436e74aaff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add monthly_income column to users table
    op.add_column('users', sa.Column('monthly_income', sa.Numeric(precision=15, scale=2), nullable=True))


def downgrade() -> None:
    # Remove monthly_income column from users table
    op.drop_column('users', 'monthly_income')

