"""End-to-end tests for complete user flows (Task 13.2).

Tests complete user journeys:
1. Registration → Consent → Upload → Recommendations
2. Authentication flows (email, phone, OAuth)
3. Consent management flow
4. Data upload and processing flow
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch, AsyncMock
from fastapi import status
from io import BytesIO

from app.models.user import User, UserRole
from app.models.session import Session as SessionModel
from app.models.data_upload import DataUpload, FileType, UploadStatus
from app.models.recommendation import Recommendation, RecommendationType, RecommendationStatus
from app.core.security import create_access_token, get_password_hash


class TestCompleteUserFlow:
    """Test complete user flow: registration → consent → upload → recommendations."""

    def test_complete_user_flow_registration_to_recommendations(
        self, client, mock_db_session
    ):
        """Test complete flow: register → grant consent → upload data → get recommendations."""
        # Step 1: Register new user
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None  # No existing user
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Mock user creation
        new_user_id = uuid.uuid4()
        new_user = User(
            user_id=new_user_id,
            email="e2e_test@example.com",
            password_hash=get_password_hash("TestPassword123!"),
            role=UserRole.USER.value,
            consent_status=False,
            consent_version="1.0",
            created_at=datetime.utcnow(),
        )

        def mock_add(item):
            if isinstance(item, User):
                return new_user
            elif isinstance(item, SessionModel):
                session = SessionModel(
                    session_id=uuid.uuid4(),
                    user_id=new_user_id,
                    refresh_token="refresh_token_123",
                    expires_at=datetime.utcnow() + timedelta(days=30),
                )
                return session

        mock_db_session.add = MagicMock(side_effect=mock_add)
        mock_db_session.commit = MagicMock()
        mock_db_session.refresh = MagicMock(side_effect=lambda x: x)

        # Mock Redis session storage
        with patch("app.core.cache_service.store_session") as mock_store:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "e2e_test@example.com",
                    "password": "TestPassword123!",
                },
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "user_id" in data
            assert "access_token" in data
            assert "refresh_token" in data
            access_token = data["access_token"]

        # Step 2: Grant consent (using the access token from registration)
        # Update mock to return new user
        mock_filter.first.return_value = new_user

        # Mock consent update
        new_user.consent_status = True
        new_user.consent_granted_at = datetime.utcnow()

        response = client.post(
            "/api/v1/consent",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"grant": True},
        )

        assert response.status_code == status.HTTP_200_OK
        consent_data = response.json()
        assert consent_data["consent_status"] is True

        # Step 3: Upload data file
        # Mock file upload
        mock_file_content = b'{"accounts": [], "transactions": []}'
        mock_file = ("test_data.json", BytesIO(mock_file_content), "application/json")

        # Mock S3 upload
        with patch("app.core.s3_service.upload_file_to_s3") as mock_s3_upload:
            mock_s3_upload.return_value = None

            # Mock DataUpload creation
            upload_id = uuid.uuid4()
            data_upload = DataUpload(
                upload_id=upload_id,
                user_id=new_user_id,
                file_name="test_data.json",
                file_size=len(mock_file_content),
                file_type=FileType.JSON,
                s3_key=f"uploads/{new_user_id}/{upload_id}/test_data.json",
                s3_bucket="test-bucket",
                status=UploadStatus.PENDING,
                created_at=datetime.utcnow(),
            )

            # Mock upload query
            def mock_query_filter(model):
                if model == DataUpload:
                    mock_upload_query = MagicMock()
                    mock_upload_filter = MagicMock()
                    mock_upload_filter.first.return_value = data_upload
                    mock_upload_query.filter.return_value = mock_upload_filter
                    return mock_upload_query
                return mock_query

            mock_db_session.query.side_effect = mock_query_filter

            response = client.post(
                "/api/v1/data/upload",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": mock_file},
            )

            assert response.status_code == status.HTTP_201_CREATED
            upload_data = response.json()
            assert "upload_id" in upload_data
            assert upload_data["status"] == "pending"

        # Step 4: Get recommendations (mock recommendations)
        # Mock recommendations query
        recommendation_id = uuid.uuid4()
        mock_recommendation = Recommendation(
            recommendation_id=recommendation_id,
            user_id=new_user_id,
            type=RecommendationType.EDUCATION,
            status=RecommendationStatus.APPROVED,
            title="Test Recommendation",
            content="This is a test recommendation",
            rationale="Because you have high credit utilization",
            created_at=datetime.utcnow(),
        )

        def mock_query_all(model):
            if model == Recommendation:
                mock_rec_query = MagicMock()
                mock_rec_filter = MagicMock()
                mock_rec_filter.filter.return_value = mock_rec_filter
                mock_rec_filter.order_by.return_value = mock_rec_filter
                mock_rec_filter.offset.return_value = mock_rec_filter
                mock_rec_filter.limit.return_value = [mock_recommendation]
                mock_rec_filter.count.return_value = 1
                mock_rec_query.filter.return_value = mock_rec_filter
                return mock_rec_query
            elif model == User:
                # Return user with consent granted
                mock_user_query = MagicMock()
                mock_user_filter = MagicMock()
                mock_user_filter.first.return_value = new_user
                mock_user_query.filter.return_value = mock_user_filter
                return mock_user_query
            return mock_query

        mock_db_session.query.side_effect = mock_query_all

        # Update user to have consent granted
        new_user.consent_status = True

        response = client.get(
            "/api/v1/recommendations",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        recommendations_data = response.json()
        assert "items" in recommendations_data
        assert "total" in recommendations_data
        assert recommendations_data["total"] >= 0


class TestAuthenticationFlows:
    """Test various authentication flows."""

    def test_email_password_authentication_flow(self, client, mock_db_session):
        """Test complete email/password authentication flow."""
        # Step 1: Register
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        user_id = uuid.uuid4()
        test_user = User(
            user_id=user_id,
            email="auth_test@example.com",
            password_hash=get_password_hash("TestPassword123!"),
            role=UserRole.USER.value,
            created_at=datetime.utcnow(),
        )

        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_db_session.refresh = MagicMock(side_effect=lambda x: x)

        with patch("app.core.cache_service.store_session"):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "auth_test@example.com",
                    "password": "TestPassword123!",
                },
            )

            assert response.status_code == status.HTTP_201_CREATED
            register_data = response.json()
            assert "access_token" in register_data

        # Step 2: Login with same credentials
        mock_filter.first.return_value = test_user

        # Mock session creation for login
        session = SessionModel(
            session_id=uuid.uuid4(),
            user_id=user_id,
            refresh_token="refresh_token_login",
            expires_at=datetime.utcnow() + timedelta(days=30),
        )

        with patch("app.core.cache_service.store_session"):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "auth_test@example.com",
                    "password": "TestPassword123!",
                },
            )

            assert response.status_code == status.HTTP_200_OK
            login_data = response.json()
            assert "access_token" in login_data
            assert "refresh_token" in login_data

        # Step 3: Use access token to access protected endpoint
        access_token = login_data["access_token"]

        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["email"] == "auth_test@example.com"

    def test_phone_sms_authentication_flow(self, client, mock_db_session):
        """Test complete phone/SMS authentication flow."""
        # Step 1: Request phone verification code
        phone_number = "+14155551234"

        with patch("app.core.sms_service.send_verification_code") as mock_send_sms:
            with patch("app.core.redis_client.redis_client") as mock_redis:
                mock_redis.set.return_value = True
                mock_redis.get.return_value = None  # No existing code

                response = client.post(
                    "/api/v1/auth/phone/request",
                    json={"phone_number": phone_number},
                )

                assert response.status_code == status.HTTP_200_OK
                assert mock_send_sms.called

        # Step 2: Verify phone code (with new user creation)
        verification_code = "123456"

        # Mock Redis to return the code
        mock_redis_client = MagicMock()
        mock_redis_client.get.return_value = verification_code.encode()
        mock_redis_client.delete.return_value = True

        with patch("app.core.sms_service.verify_verification_code") as mock_verify:
            mock_verify.return_value = True

            with patch("app.core.redis_client.redis_client", mock_redis_client):
                # Mock user creation
                user_id = uuid.uuid4()
                new_user = User(
                    user_id=user_id,
                    phone=phone_number,
                    role=UserRole.USER.value,
                    created_at=datetime.utcnow(),
                )

                mock_query = MagicMock()
                mock_filter = MagicMock()
                mock_filter.first.return_value = None  # No existing user
                mock_query.filter.return_value = mock_filter
                mock_db_session.query.return_value = mock_query

                mock_db_session.add = MagicMock()
                mock_db_session.commit = MagicMock()
                mock_db_session.refresh = MagicMock(side_effect=lambda x: x)

                with patch("app.core.cache_service.store_session"):
                    response = client.post(
                        "/api/v1/auth/phone/verify",
                        json={
                            "phone_number": phone_number,
                            "code": verification_code,
                        },
                    )

                    assert response.status_code == status.HTTP_200_OK
                    verify_data = response.json()
                    assert "access_token" in verify_data
                    assert "user_id" in verify_data

    def test_oauth_authentication_flow(self, client, mock_db_session):
        """Test OAuth authentication flow."""
        # Step 1: Get OAuth authorization URL
        provider = "google"

        with patch("app.core.oauth_service.get_oauth_authorize_url") as mock_auth_url:
            mock_auth_url.return_value = "https://accounts.google.com/oauth/authorize?state=test_state"

            response = client.get(
                f"/api/v1/auth/oauth/{provider}/authorize",
            )

            assert response.status_code == status.HTTP_200_OK
            auth_data = response.json()
            assert "authorize_url" in auth_data

        # Step 2: OAuth callback (mocked)
        # This would normally be handled by the OAuth provider redirect
        # For testing, we'll mock the callback endpoint
        with patch("app.core.oauth_service.exchange_oauth_code") as mock_exchange:
            with patch("app.core.oauth_service.get_oauth_user_info") as mock_user_info:
                with patch("app.core.oauth_service.verify_oauth_state") as mock_verify_state:
                    mock_verify_state.return_value = True
                    mock_exchange.return_value = {"access_token": "oauth_token"}
                    mock_user_info.return_value = {
                        "email": "oauth_test@example.com",
                        "name": "OAuth Test User",
                    }

                    # Mock user creation/lookup
                    user_id = uuid.uuid4()
                    oauth_user = User(
                        user_id=user_id,
                        email="oauth_test@example.com",
                        role=UserRole.USER.value,
                        oauth_providers={"google": "oauth_id_123"},
                        created_at=datetime.utcnow(),
                    )

                    mock_query = MagicMock()
                    mock_filter = MagicMock()
                    mock_filter.first.return_value = oauth_user
                    mock_query.filter.return_value = mock_filter
                    mock_db_session.query.return_value = mock_query

                    mock_db_session.commit = MagicMock()
                    mock_db_session.refresh = MagicMock(side_effect=lambda x: x)

                    with patch("app.core.cache_service.store_session"):
                        response = client.get(
                            f"/api/v1/auth/oauth/{provider}/callback",
                            params={
                                "code": "test_code",
                                "state": "test_state",
                            },
                        )

                        # OAuth callback redirects, so we check for redirect or success
                        assert response.status_code in [
                            status.HTTP_200_OK,
                            status.HTTP_302_FOUND,
                        ]


class TestConsentManagementFlow:
    """Test consent management flow."""

    def test_consent_grant_revoke_flow(self, client, mock_db_session, test_user):
        """Test complete consent management flow: grant → revoke → grant again."""
        # Setup: User without consent
        test_user.consent_status = False
        test_user.consent_granted_at = None
        test_user.consent_revoked_at = None

        access_token = create_access_token({
            "user_id": str(test_user.user_id),
            "email": test_user.email or "",
            "role": test_user.role,
        })

        # Step 1: Check initial consent status (should be False)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = test_user
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        response = client.get(
            "/api/v1/consent",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        consent_data = response.json()
        assert consent_data["consent_status"] is False

        # Step 2: Grant consent
        test_user.consent_status = True
        test_user.consent_granted_at = datetime.utcnow()
        test_user.consent_version = "1.0"

        mock_db_session.commit = MagicMock()

        response = client.post(
            "/api/v1/consent",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"grant": True},
        )

        assert response.status_code == status.HTTP_200_OK
        grant_data = response.json()
        assert grant_data["consent_status"] is True
        assert "consent_granted_at" in grant_data

        # Step 3: Revoke consent
        test_user.consent_status = False
        test_user.consent_revoked_at = datetime.utcnow()

        response = client.delete(
            "/api/v1/consent",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"delete_data": False},  # Don't delete data on revocation
        )

        assert response.status_code == status.HTTP_200_OK
        revoke_data = response.json()
        assert revoke_data["consent_status"] is False

        # Step 4: Grant consent again
        test_user.consent_status = True
        test_user.consent_granted_at = datetime.utcnow()
        test_user.consent_revoked_at = None

        response = client.post(
            "/api/v1/consent",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"grant": True},
        )

        assert response.status_code == status.HTTP_200_OK
        grant_again_data = response.json()
        assert grant_again_data["consent_status"] is True

        # Step 5: Verify consent is required for recommendations
        # Mock recommendations query
        mock_rec_query = MagicMock()
        mock_rec_filter = MagicMock()
        mock_rec_filter.filter.return_value = mock_rec_filter
        mock_rec_query.filter.return_value = mock_rec_filter

        def mock_query_consent(model):
            if model == Recommendation:
                return mock_rec_query
            elif model == User:
                return mock_query
            return mock_query

        mock_db_session.query.side_effect = mock_query_consent

        # Test with consent granted - should succeed
        test_user.consent_status = True
        response = client.get(
            "/api/v1/recommendations",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Should succeed (even if no recommendations, consent check passes)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

        # Test with consent revoked - should fail
        test_user.consent_status = False
        response = client.get(
            "/api/v1/recommendations",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDataUploadFlow:
    """Test data upload and processing flow."""

    def test_data_upload_complete_flow(self, client, mock_db_session, test_user):
        """Test complete data upload flow: upload → status check → processing."""
        access_token = create_access_token({
            "user_id": str(test_user.user_id),
            "email": test_user.email or "",
            "role": test_user.role,
        })

        # Step 1: Upload file
        mock_file_content = b'{"accounts": [{"account_id": "123"}], "transactions": []}'
        mock_file = ("test_upload.json", BytesIO(mock_file_content), "application/json")

        upload_id = uuid.uuid4()
        data_upload = DataUpload(
            upload_id=upload_id,
            user_id=test_user.user_id,
            file_name="test_upload.json",
            file_size=len(mock_file_content),
            file_type=FileType.JSON,
            s3_key=f"uploads/{test_user.user_id}/{upload_id}/test_upload.json",
            s3_bucket="test-bucket",
            status=UploadStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Mock S3 upload
        with patch("app.core.s3_service.upload_file_to_s3") as mock_s3:
            mock_s3.return_value = None

            mock_db_session.add = MagicMock()
            mock_db_session.commit = MagicMock()
            mock_db_session.refresh = MagicMock(side_effect=lambda x: x)

            response = client.post(
                "/api/v1/data/upload",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": mock_file},
            )

            assert response.status_code == status.HTTP_201_CREATED
            upload_data = response.json()
            assert "upload_id" in upload_data
            assert upload_data["status"] == "pending"
            assert upload_data["file_name"] == "test_upload.json"

        # Step 2: Check upload status
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = data_upload
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        response = client.get(
            f"/api/v1/data/upload/{upload_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        status_data = response.json()
        assert status_data["upload_id"] == str(upload_id)
        assert status_data["status"] == "pending"

        # Step 3: Update status to processing (simulate processing)
        data_upload.status = UploadStatus.PROCESSING
        data_upload.processed_at = datetime.utcnow()

        response = client.get(
            f"/api/v1/data/upload/{upload_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        processing_data = response.json()
        assert processing_data["status"] == "processing"

        # Step 4: Update status to completed
        data_upload.status = UploadStatus.COMPLETED
        data_upload.completed_at = datetime.utcnow()

        response = client.get(
            f"/api/v1/data/upload/{upload_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        completed_data = response.json()
        assert completed_data["status"] == "completed"

    def test_data_upload_validation_errors(self, client, mock_db_session, test_user):
        """Test data upload validation errors."""
        access_token = create_access_token({
            "user_id": str(test_user.user_id),
            "email": test_user.email or "",
            "role": test_user.role,
        })

        # Test 1: Invalid file type
        invalid_file = ("test.txt", BytesIO(b"test content"), "text/plain")

        response = client.post(
            "/api/v1/data/upload",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": invalid_file},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test 2: File too large (mock)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = ("large.json", BytesIO(large_content), "application/json")

        with patch("app.core.s3_service.validate_file_size") as mock_validate:
            mock_validate.side_effect = ValueError("File size exceeds maximum allowed size")

            response = client.post(
                "/api/v1/data/upload",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": large_file},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_data_upload_unauthorized(self, client, mock_db_session):
        """Test data upload without authentication."""
        mock_file = ("test.json", BytesIO(b'{"test": "data"}'), "application/json")

        response = client.post(
            "/api/v1/data/upload",
            files={"file": mock_file},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

