"""Add recommendation_feedback table

Revision ID: add_feedback_table
Revises: <latest_revision>
Create Date: 2025-11-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_feedback_table'
down_revision = None  # TODO: Update with latest revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create recommendation_feedback table
    op.create_table(
        'recommendation_feedback',
        sa.Column('feedback_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),  # 1-5 rating
        sa.Column('helpful', sa.Boolean(), nullable=True),  # True/False
        sa.Column('comment', sa.Text(), nullable=True),  # Optional text comment
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.recommendation_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('feedback_id')
    )
    
    # Create indexes for performance
    op.create_index('ix_feedback_recommendation_id', 'recommendation_feedback', ['recommendation_id'])
    op.create_index('ix_feedback_user_id', 'recommendation_feedback', ['user_id'])
    op.create_index('ix_feedback_created_at', 'recommendation_feedback', ['created_at'])
    op.create_index('ix_feedback_user_recommendation', 'recommendation_feedback', ['user_id', 'recommendation_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_feedback_user_recommendation', table_name='recommendation_feedback')
    op.drop_index('ix_feedback_created_at', table_name='recommendation_feedback')
    op.drop_index('ix_feedback_user_id', table_name='recommendation_feedback')
    op.drop_index('ix_feedback_recommendation_id', table_name='recommendation_feedback')
    
    # Drop table
    op.drop_table('recommendation_feedback')

