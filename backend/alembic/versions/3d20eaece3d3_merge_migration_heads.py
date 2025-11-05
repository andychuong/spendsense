"""Merge migration heads

Revision ID: 3d20eaece3d3
Revises: 916ff7d6f997, dbad1091a604
Create Date: 2025-11-04 16:58:14.135799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d20eaece3d3'
down_revision = ('916ff7d6f997', 'dbad1091a604')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

