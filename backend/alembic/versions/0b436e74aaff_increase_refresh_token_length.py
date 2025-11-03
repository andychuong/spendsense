"""increase_refresh_token_length

Revision ID: 0b436e74aaff
Revises: 9a34438a9f36
Create Date: 2025-11-03 17:10:46.833491

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b436e74aaff'
down_revision = '9a34438a9f36'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Increase refresh_token column size from 255 to 1000 characters
    op.alter_column('sessions', 'refresh_token',
                   existing_type=sa.String(length=255),
                   type_=sa.String(length=1000),
                   existing_nullable=False)


def downgrade() -> None:
    # Revert refresh_token column size back to 255
    op.alter_column('sessions', 'refresh_token',
                   existing_type=sa.String(length=1000),
                   type_=sa.String(length=255),
                   existing_nullable=False)

