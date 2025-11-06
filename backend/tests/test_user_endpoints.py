"""Unit tests for user management endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi import status
from sqlalchemy.orm import Session

from app.models.user import User


class TestGetCurrentUserProfile:
    """Tests for GET /api/v1/users/me endpoint."""

    def test_get_current_user_profile_success(
        self, client, test_user, auth_headers
    ):
        """Test successfully getting current user profile."""
        response = client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(test_user.user_id)
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role
        assert data["consent_status"] == test_user.consent_status
        assert data["consent_version"] == test_user.consent_version

    def test_get_current_user_profile_unauthorized(self, client):
        """Test getting current user profile without authentication."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_profile_invalid_token(self, client):
        """Test getting current user profile with invalid token."""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateCurrentUserProfile:
    """Tests for PUT /api/v1/users/me endpoint."""

    def test_update_current_user_profile_email_success(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test successfully updating user email."""
        new_email = "newemail@example.com"
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": new_email}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == new_email

        # Verify in database
        db_session.refresh(test_user)
        assert test_user.email == new_email

    def test_update_current_user_profile_phone_success(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test successfully updating user phone number."""
        new_phone = "+1234567890"
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"phone_number": new_phone}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["phone_number"] == new_phone

        # Verify in database
        db_session.refresh(test_user)
        assert test_user.phone_number == new_phone

    def test_update_current_user_profile_both_fields_success(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test successfully updating both email and phone."""
        new_email = "updated@example.com"
        new_phone = "+1234567890"
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": new_email, "phone_number": new_phone}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == new_email
        assert data["phone_number"] == new_phone

        # Verify in database
        db_session.refresh(test_user)
        assert test_user.email == new_email
        assert test_user.phone_number == new_phone

    def test_update_current_user_profile_email_already_exists(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test updating email to one that already exists."""
        # Create another user with email
        other_user = User(
            email="existing@example.com",
            password_hash="hash",
            role="user"
        )
        db_session.add(other_user)
        db_session.commit()

        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "existing@example.com"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_update_current_user_profile_phone_already_exists(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test updating phone to one that already exists."""
        # Create another user with phone
        other_user = User(
            email="other@example.com",
            phone_number="+9876543210",
            password_hash="hash",
            role="user"
        )
        db_session.add(other_user)
        db_session.commit()

        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"phone_number": "+9876543210"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_update_current_user_profile_unauthorized(self, client):
        """Test updating profile without authentication."""
        response = client.put(
            "/api/v1/users/me",
            json={"email": "new@example.com"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_current_user_profile_invalid_email_format(
        self, client, test_user, auth_headers
    ):
        """Test updating profile with invalid email format."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"email": "invalid-email"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_current_user_profile_no_changes(
        self, client, test_user, auth_headers
    ):
        """Test updating profile with no fields (should succeed but no changes)."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email


class TestGetUserProfile:
    """Tests for GET /api/v1/users/{user_id} endpoint."""

    def test_get_user_profile_own_profile_success(
        self, client, test_user, auth_headers
    ):
        """Test user getting their own profile."""
        response = client.get(
            f"/api/v1/users/{test_user.user_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(test_user.user_id)

    def test_get_user_profile_operator_access(
        self, client, test_user, operator_auth_headers, test_operator_user
    ):
        """Test operator accessing another user's profile."""
        response = client.get(
            f"/api/v1/users/{test_user.user_id}",
            headers=operator_auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(test_user.user_id)

    def test_get_user_profile_admin_access(
        self, client, test_user, admin_auth_headers
    ):
        """Test admin accessing another user's profile."""
        response = client.get(
            f"/api/v1/users/{test_user.user_id}",
            headers=admin_auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(test_user.user_id)

    def test_get_user_profile_unauthorized_access(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test user accessing another user's profile (should fail)."""
        # Create another user
        other_user = User(
            email="other@example.com",
            password_hash="hash",
            role="user"
        )
        db_session.add(other_user)
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{other_user.user_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_profile_user_not_found(
        self, client, auth_headers
    ):
        """Test getting profile for non-existent user."""
        import uuid
        fake_user_id = uuid.uuid4()

        response = client.get(
            f"/api/v1/users/{fake_user_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_profile_consent_revoked(
        self, client, test_user, operator_auth_headers, mock_db_session
    ):
        """Test operator accessing user profile when consent is revoked."""
        # Revoke consent
        test_user.consent_status = False
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.user_id}",
            headers=operator_auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "consent" in response.json()["detail"].lower()

    def test_get_user_profile_unauthorized_no_auth(self, client, test_user):
        """Test getting user profile without authentication."""
        response = client.get(f"/api/v1/users/{test_user.user_id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteCurrentUserAccount:
    """Tests for DELETE /api/v1/users/me endpoint."""

    def test_delete_current_user_account_success(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test successfully deleting user account."""
        user_id = test_user.user_id

        response = client.delete(
            "/api/v1/users/me",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""  # No content

        # Verify user is deleted
        deleted_user = db_session.query(User).filter(User.user_id == user_id).first()
        assert deleted_user is None

    def test_delete_current_user_account_unauthorized(self, client):
        """Test deleting account without authentication."""
        response = client.delete("/api/v1/users/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_current_user_account_with_related_data(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test deleting user account with related data."""
        from app.models.session import Session as SessionModel
        from app.models.data_upload import DataUpload
        from app.models.recommendation import Recommendation
        from app.models.user_profile import UserProfile
        from app.models.persona_history import PersonaHistory

        # Create related data
        session = SessionModel(
            user_id=test_user.user_id,
            refresh_token="test_token",
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(session)
        db_session.commit()

        user_id = test_user.user_id

        response = client.delete(
            "/api/v1/users/me",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify user and related data are deleted
        deleted_user = db_session.query(User).filter(User.user_id == user_id).first()
        assert deleted_user is None

        deleted_session = db_session.query(SessionModel).filter(
            SessionModel.user_id == user_id
        ).first()
        assert deleted_session is None

    def test_delete_current_user_account_invalid_token(self, client):
        """Test deleting account with invalid token."""
        response = client.delete(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

