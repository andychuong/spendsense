"""User model."""

import uuid
from sqlalchemy import Column, String, Boolean, JSON, DateTime, Enum, TypeDecorator, Numeric
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func
import enum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.user_persona_assignment import UserPersonaAssignment # Import here to resolve relationship


class UserRole(str, enum.Enum):
    """User role enumeration."""

    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"


class UserRoleEnum(TypeDecorator):
    """Type decorator for UserRole enum to ensure proper conversion."""

    # Use String as the underlying type, but PostgreSQL will use the enum
    impl = String(20)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Use PostgreSQL ENUM type when available."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(
                ENUM(UserRole, name='userrole', create_type=False, native_enum=True)
            )
        return dialect.type_descriptor(String(20))

    def process_bind_param(self, value, dialect):
        """Convert enum to its value when binding to database."""
        if value is None:
            return None
        # Convert enum to its string value - this is critical
        if isinstance(value, UserRole):
            return value.value  # Return "user", "operator", or "admin"
        # If it's already a string, validate and return it
        if isinstance(value, str):
            # Validate it's a valid enum value
            valid_values = [e.value for e in UserRole]
            if value in valid_values:
                return value
            # If it's the enum name (USER, OPERATOR, ADMIN), convert to value
            try:
                enum_obj = UserRole[value]  # Get enum by name
                return enum_obj.value
            except KeyError:
                return value
        # Fallback: try to get value attribute
        return getattr(value, 'value', value)

    def process_result_value(self, value, dialect):
        """Convert database value back to enum."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return UserRole(value)
            except ValueError:
                # If value doesn't match enum, return as-is
                return value
        return value


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    oauth_providers = Column(JSON, default=dict, nullable=False)
    role = Column(
        String(20),  # Use String directly - PostgreSQL will validate against enum
        default="user",  # Use string value directly
        nullable=False
    )
    consent_status = Column(Boolean, default=False, nullable=False)
    consent_version = Column(String(10), default="1.0", nullable=False)
    monthly_income = Column(Numeric(15, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationship to UserPersonaAssignment
    persona_assignments = relationship("UserPersonaAssignment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(user_id={self.user_id}, name={self.name}, email={self.email}, role={self.role})>"

