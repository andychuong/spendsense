"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import MagicMock, Mock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    session.query = MagicMock()
    session.add = MagicMock()
    session.delete = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    session.filter = MagicMock(return_value=session)
    session.first = MagicMock()
    session.all = MagicMock(return_value=[])
    session.offset = MagicMock(return_value=session)
    session.limit = MagicMock(return_value=session)
    session.count = MagicMock(return_value=0)
    return session


@pytest.fixture
def client(mock_db_session, test_user):
    """Create a test client with mocked database."""
    from app.main import app
    from app.database import get_db
    from app.core.dependencies import get_current_user, get_current_active_user

    # Setup mock query chain to return test_user by default
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = test_user
    mock_filter.filter.return_value = mock_filter
    mock_query.filter.return_value = mock_filter
    mock_query.return_value = mock_query
    mock_db_session.query = mock_query

    def override_get_db():
        try:
            yield mock_db_session
        finally:
            pass

    def override_get_current_user():
        return test_user

    def override_get_current_active_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Create a test user."""
    import uuid
    from datetime import datetime
    user = User(
        user_id=uuid.uuid4(),
        email="test@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        role=UserRole.USER.value,
        consent_status=False,
        consent_version="1.0",
        created_at=datetime.utcnow(),
    )
    return user


@pytest.fixture
def test_operator_user():
    """Create a test operator user."""
    import uuid
    from datetime import datetime
    user = User(
        user_id=uuid.uuid4(),
        email="operator@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        role=UserRole.OPERATOR.value,
        consent_status=True,
        consent_version="1.0",
        created_at=datetime.utcnow(),
    )
    return user


@pytest.fixture
def test_admin_user():
    """Create a test admin user."""
    import uuid
    from datetime import datetime
    user = User(
        user_id=uuid.uuid4(),
        email="admin@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        role=UserRole.ADMIN.value,
        consent_status=True,
        consent_version="1.0",
        created_at=datetime.utcnow(),
    )
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    access_token = create_access_token({
        "user_id": str(test_user.user_id),
        "email": test_user.email or "",
        "role": test_user.role
    })
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def operator_auth_headers(test_operator_user):
    """Create authentication headers for operator user."""
    access_token = create_access_token({
        "user_id": str(test_operator_user.user_id),
        "email": test_operator_user.email or "",
        "role": test_operator_user.role
    })
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_auth_headers(test_admin_user):
    """Create authentication headers for admin user."""
    access_token = create_access_token({
        "user_id": str(test_admin_user.user_id),
        "email": test_admin_user.email or "",
        "role": test_admin_user.role
    })
    return {"Authorization": f"Bearer {access_token}"}
