"""Unit tests for email/password authentication endpoints (Task 2.2)."""

import pytest
from datetime import datetime, timedelta
from fastapi import status

from app.models.user import User
from app.models.session import Session as SessionModel
from app.core.security import create_access_token, create_refresh_token


class TestRegister:
    """Tests for POST /api/v1/auth/register endpoint."""

    def test_register_success(self, client, mock_db_session):
        """Test successfully registering a new user."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "user_id" in data
        assert data["email"] == "newuser@example.com"
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify user was created
        user = db_session.query(User).filter(
            User.email == "newuser@example.com"
        ).first()
        assert user is not None
        assert user.role == "user"
        
        # Verify session was created
        session = db_session.query(SessionModel).filter(
            SessionModel.user_id == user.user_id
        ).first()
        assert session is not None
        assert session.refresh_token == data["refresh_token"]

    def test_register_email_already_exists(self, client, test_user):
        """Test registering with an email that already exists."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "SecurePassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_register_invalid_email_format(self, client):
        """Test registering with invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_weak_password(self, client):
        """Test registering with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "weak"
            }
        )
        
        # Should fail validation if password validation is implemented
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_register_missing_fields(self, client):
        """Test registering with missing fields."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "user@example.com"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Tests for POST /api/v1/auth/login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successfully logging in."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(test_user.user_id)
        assert data["email"] == test_user.email
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self, client):
        """Test logging in with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, test_user):
        """Test logging in with incorrect password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_user_without_password(self, client, mock_db_session):
        """Test logging in with OAuth user (no password)."""
        # Create user without password (OAuth user)
        oauth_user = User(
            email="oauth@example.com",
            password_hash=None,
            role="user",
            oauth_providers={"google": "provider_id"}
        )
        db_session.add(oauth_user)
        db_session.commit()
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": oauth_user.email,
                "password": "AnyPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_missing_fields(self, client):
        """Test logging in with missing fields."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRefreshToken:
    """Tests for POST /api/v1/auth/refresh endpoint."""

    def test_refresh_token_success(
        self, client, test_user, mock_db_session
    ):
        """Test successfully refreshing access token."""
        # Create a session with refresh token
        refresh_token = create_refresh_token(
            user_id=test_user.user_id,
            email=test_user.email or "",
            role=test_user.role,
            session_id=None
        )
        
        session = SessionModel(
            user_id=test_user.user_id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # New refresh token should be different
        assert data["refresh_token"] != refresh_token

    def test_refresh_token_invalid_token(self, client):
        """Test refreshing with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_expired_token(
        self, client, test_user, mock_db_session
    ):
        """Test refreshing with expired token."""
        # Create expired session
        expired_token = create_refresh_token(
            user_id=test_user.user_id,
            email=test_user.email or "",
            role=test_user.role,
            session_id=None
        )
        
        session = SessionModel(
            user_id=test_user.user_id,
            refresh_token=expired_token,
            expires_at=datetime.utcnow() - timedelta(days=1)  # Expired
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_missing_session(
        self, client, test_user
    ):
        """Test refreshing with token that has no session."""
        # Create refresh token without session in DB
        refresh_token = create_refresh_token(
            user_id=test_user.user_id,
            email=test_user.email or "",
            role=test_user.role,
            session_id=None
        )
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_missing_field(self, client):
        """Test refreshing with missing refresh_token field."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogout:
    """Tests for POST /api/v1/auth/logout endpoint."""

    def test_logout_success(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test successfully logging out."""
        # Create a session
        refresh_token = create_refresh_token(
            user_id=test_user.user_id,
            email=test_user.email or "",
            role=test_user.role,
            session_id=None
        )
        
        session = SessionModel(
            user_id=test_user.user_id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(session)
        db_session.commit()
        
        session_id = session.session_id
        
        response = client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        
        # Verify session was deleted
        deleted_session = db_session.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()
        assert deleted_session is None

    def test_logout_multiple_sessions(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test logging out with multiple sessions."""
        # Create multiple sessions
        for i in range(3):
            refresh_token = create_refresh_token(
                user_id=test_user.user_id,
                email=test_user.email or "",
                role=test_user.role,
                session_id=None
            )
            session = SessionModel(
                user_id=test_user.user_id,
                refresh_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db_session.add(session)
        
        db_session.commit()
        
        response = client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify all sessions for user were deleted
        sessions = db_session.query(SessionModel).filter(
            SessionModel.user_id == test_user.user_id
        ).all()
        assert len(sessions) == 0

    def test_logout_unauthorized(self, client):
        """Test logging out without authentication."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout_invalid_token(self, client):
        """Test logging out with invalid token."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

