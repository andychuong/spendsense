"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('oauth_providers', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('role', sa.Enum('user', 'operator', 'admin', name='userrole'), nullable=False, server_default=sa.text("'user'")),
        sa.Column('consent_status', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('consent_version', sa.String(length=10), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_phone_number', 'users', ['phone_number'], unique=True)

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_sessions_refresh_token', 'sessions', ['refresh_token'], unique=True)
    op.create_index('ix_sessions_expires_at', 'sessions', ['expires_at'])

    # Create data_uploads table
    op.create_table(
        'data_uploads',
        sa.Column('upload_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.Enum('json', 'csv', name='filetype'), nullable=False),
        sa.Column('s3_key', sa.String(length=500), nullable=False),
        sa.Column('s3_bucket', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='uploadstatus'), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('validation_errors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('upload_id')
    )
    op.create_index('ix_data_uploads_user_id', 'data_uploads', ['user_id'])
    op.create_index('ix_data_uploads_status', 'data_uploads', ['status'])
    op.create_index('ix_data_uploads_created_at', 'data_uploads', ['created_at'])
    op.create_index('ix_data_uploads_user_id_status', 'data_uploads', ['user_id', 'status'])

    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum('education', 'partner_offer', name='recommendationtype'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='recommendationstatus'), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('decision_trace', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['rejected_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('recommendation_id')
    )
    op.create_index('ix_recommendations_user_id', 'recommendations', ['user_id'])
    op.create_index('ix_recommendations_status', 'recommendations', ['status'])
    op.create_index('ix_recommendations_created_at', 'recommendations', ['created_at'])
    op.create_index('ix_recommendations_approved_at', 'recommendations', ['approved_at'])
    op.create_index('ix_recommendations_user_id_status', 'recommendations', ['user_id', 'status'])

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('persona_name', sa.String(length=100), nullable=False),
        sa.Column('signals_30d', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('signals_180d', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('profile_id'),
        sa.CheckConstraint('persona_id >= 1 AND persona_id <= 5', name='check_persona_id_range'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'], unique=True)
    op.create_index('ix_user_profiles_persona_id', 'user_profiles', ['persona_id'])

    # Create persona_history table
    op.create_table(
        'persona_history',
        sa.Column('history_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('persona_name', sa.String(length=100), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('signals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('history_id')
    )
    op.create_index('ix_persona_history_user_id', 'persona_history', ['user_id'])
    op.create_index('ix_persona_history_assigned_at', 'persona_history', ['assigned_at'])
    op.create_index('ix_persona_history_user_id_assigned_at', 'persona_history', ['user_id', 'assigned_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_persona_history_user_id_assigned_at', table_name='persona_history')
    op.drop_index('ix_persona_history_assigned_at', table_name='persona_history')
    op.drop_index('ix_persona_history_user_id', table_name='persona_history')
    op.drop_index('ix_user_profiles_persona_id', table_name='user_profiles')
    op.drop_index('ix_user_profiles_user_id', table_name='user_profiles')
    op.drop_index('ix_recommendations_user_id_status', table_name='recommendations')
    op.drop_index('ix_recommendations_approved_at', table_name='recommendations')
    op.drop_index('ix_recommendations_created_at', table_name='recommendations')
    op.drop_index('ix_recommendations_status', table_name='recommendations')
    op.drop_index('ix_recommendations_user_id', table_name='recommendations')
    op.drop_index('ix_data_uploads_user_id_status', table_name='data_uploads')
    op.drop_index('ix_data_uploads_created_at', table_name='data_uploads')
    op.drop_index('ix_data_uploads_status', table_name='data_uploads')
    op.drop_index('ix_data_uploads_user_id', table_name='data_uploads')
    op.drop_index('ix_sessions_expires_at', table_name='sessions')
    op.drop_index('ix_sessions_refresh_token', table_name='sessions')
    op.drop_index('ix_sessions_user_id', table_name='sessions')
    op.drop_index('ix_users_phone_number', table_name='users')
    op.drop_index('ix_users_email', table_name='users')

    # Drop tables
    op.drop_table('persona_history')
    op.drop_table('user_profiles')
    op.drop_table('recommendations')
    op.drop_table('data_uploads')
    op.drop_table('sessions')
    op.drop_table('users')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS recommendationstatus')
    op.execute('DROP TYPE IF EXISTS recommendationtype')
    op.execute('DROP TYPE IF EXISTS uploadstatus')
    op.execute('DROP TYPE IF EXISTS filetype')
    op.execute('DROP TYPE IF EXISTS userrole')

