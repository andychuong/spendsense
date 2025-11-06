"""Unit tests for consent management endpoints."""

import pytest
from datetime import datetime
from fastapi import status

from app.models.user import User
from app.models.data_upload import DataUpload
from app.models.recommendation import Recommendation
from app.models.user_profile import UserProfile
from app.models.persona_history import PersonaHistory


class TestGrantConsent:
    """Tests for POST /api/v1/consent endpoint."""

    def test_grant_consent_success(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test successfully granting consent."""
        response = client.post(
            "/api/v1/consent",
            headers=auth_headers,
            json={
                "consent_version": "1.0",
                "tos_accepted": True
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["consent_status"] is True
        assert data["consent_version"] == "1.0"
        assert data["user_id"] == str(test_user.user_id)
        assert data["consent_granted_at"] is not None

        # Verify in database
        db_session.refresh(test_user)
        assert test_user.consent_status is True
        assert test_user.consent_version == "1.0"

    def test_grant_consent_tos_not_accepted(
        self, client, test_user, auth_headers
    ):
        """Test granting consent without accepting TOS."""
        response = client.post(
            "/api/v1/consent",
            headers=auth_headers,
            json={
                "consent_version": "1.0",
                "tos_accepted": False
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Terms of Service" in response.json()["detail"]

    def test_grant_consent_unauthorized(self, client):
        """Test granting consent without authentication."""
        response = client.post(
            "/api/v1/consent",
            json={
                "consent_version": "1.0",
                "tos_accepted": True
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_grant_consent_update_version(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test updating consent version."""
        # First grant consent
        test_user.consent_status = True
        test_user.consent_version = "1.0"
        db_session.commit()

        # Update to new version
        response = client.post(
            "/api/v1/consent",
            headers=auth_headers,
            json={
                "consent_version": "2.0",
                "tos_accepted": True
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["consent_version"] == "2.0"

        # Verify in database
        db_session.refresh(test_user)
        assert test_user.consent_version == "2.0"


class TestGetConsentStatus:
    """Tests for GET /api/v1/consent endpoint."""

    def test_get_consent_status_granted(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test getting consent status when consent is granted."""
        test_user.consent_status = True
        test_user.consent_version = "1.0"
        db_session.commit()

        response = client.get(
            "/api/v1/consent",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["consent_status"] is True
        assert data["consent_version"] == "1.0"
        assert data["user_id"] == str(test_user.user_id)
        assert data["consent_granted_at"] is not None

    def test_get_consent_status_not_granted(
        self, client, test_user, auth_headers
    ):
        """Test getting consent status when consent is not granted."""
        response = client.get(
            "/api/v1/consent",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["consent_status"] is False
        assert data["consent_revoked_at"] is None

    def test_get_consent_status_unauthorized(self, client):
        """Test getting consent status without authentication."""
        response = client.get("/api/v1/consent")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRevokeConsent:
    """Tests for DELETE /api/v1/consent endpoint."""

    def test_revoke_consent_success(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test successfully revoking consent."""
        # First grant consent
        test_user.consent_status = True
        test_user.consent_version = "1.0"
        db_session.commit()

        response = client.delete(
            "/api/v1/consent",
            headers=auth_headers,
            json={"delete_data": False}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["consent_status"] is False
        assert data["consent_revoked_at"] is not None

        # Verify in database
        db_session.refresh(test_user)
        assert test_user.consent_status is False

    def test_revoke_consent_with_data_deletion(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test revoking consent and deleting all user data."""
        # First grant consent
        test_user.consent_status = True
        test_user.consent_version = "1.0"
        db_session.commit()

        # Create related data
        data_upload = DataUpload(
            user_id=test_user.user_id,
            file_name="test.json",
            file_size=1000,
            file_type="json",
            s3_key="test/key",
            s3_bucket="test-bucket",
            status="completed"
        )
        recommendation = Recommendation(
            user_id=test_user.user_id,
            type="education",
            title="Test",
            content="Test content",
            rationale="Test rationale",
            status="pending"
        )
        user_profile = UserProfile(
            user_id=test_user.user_id,
            persona_id=1,
            persona_name="Test Persona"
        )
        persona_history = PersonaHistory(
            user_id=test_user.user_id,
            persona_id=1,
            persona_name="Test Persona"
        )

        db_session.add_all([data_upload, recommendation, user_profile, persona_history])
        db_session.commit()

        user_id = test_user.user_id

        response = client.delete(
            "/api/v1/consent",
            headers=auth_headers,
            json={"delete_data": True}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["consent_status"] is False

        # Verify user data is deleted
        db_session.refresh(test_user)
        assert test_user.consent_status is False

        assert db_session.query(DataUpload).filter(
            DataUpload.user_id == user_id
        ).first() is None
        assert db_session.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).first() is None
        assert db_session.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first() is None
        assert db_session.query(PersonaHistory).filter(
            PersonaHistory.user_id == user_id
        ).first() is None

    def test_revoke_consent_without_data_deletion(
        self, client, test_user, auth_headers, mock_db_session
    ):
        """Test revoking consent without deleting data."""
        # First grant consent
        test_user.consent_status = True
        test_user.consent_version = "1.0"
        db_session.commit()

        # Create related data
        data_upload = DataUpload(
            user_id=test_user.user_id,
            file_name="test.json",
            file_size=1000,
            file_type="json",
            s3_key="test/key",
            s3_bucket="test-bucket",
            status="completed"
        )
        db_session.add(data_upload)
        db_session.commit()

        response = client.delete(
            "/api/v1/consent",
            headers=auth_headers,
            json={"delete_data": False}
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify data is NOT deleted
        assert db_session.query(DataUpload).filter(
            DataUpload.user_id == test_user.user_id
        ).first() is not None

    def test_revoke_consent_unauthorized(self, client):
        """Test revoking consent without authentication."""
        response = client.delete(
            "/api/v1/consent",
            json={"delete_data": False}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_revoke_consent_default_no_deletion(
        self, client, test_user, auth_headers, db_session
    ):
        """Test revoking consent with default (no deletion)."""
        # First grant consent
        test_user.consent_status = True
        test_user.consent_version = "1.0"
        db_session.commit()

        response = client.delete(
            "/api/v1/consent",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["consent_status"] is False

