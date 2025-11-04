"""Unit tests for phone/SMS authentication endpoints (Task 2.3)."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

from app.models.user import User
from app.models.session import Session as SessionModel


class TestRequestPhoneVerification:
    """Tests for POST /api/v1/auth/phone/request endpoint."""

    @patch('app.core.sms_service.send_verification_code')
    @patch('app.core.sms_service.validate_phone_number')
    def test_request_phone_verification_success(
        self, mock_validate, mock_send_code, client
    ):
        """Test successfully requesting phone verification."""
        mock_validate.return_value = "+1234567890"
        mock_send_code.return_value = (True, None)
        
        response = client.post(
            "/api/v1/auth/phone/request",
            json={"phone": "+1234567890"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Verification code sent successfully"
        assert data["phone"] == "+1234567890"
        
        mock_validate.assert_called_once_with("+1234567890")
        mock_send_code.assert_called_once_with("+1234567890")

    @patch('app.core.sms_service.validate_phone_number')
    def test_request_phone_verification_invalid_phone(
        self, mock_validate, client
    ):
        """Test requesting verification with invalid phone number."""
        mock_validate.side_effect = ValueError("Invalid phone number format")
        
        response = client.post(
            "/api/v1/auth/phone/request",
            json={"phone": "invalid"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid phone number" in response.json()["detail"]

    @patch('app.core.sms_service.send_verification_code')
    @patch('app.core.sms_service.validate_phone_number')
    def test_request_phone_verification_send_failure(
        self, mock_validate, mock_send_code, client
    ):
        """Test requesting verification when SMS sending fails."""
        mock_validate.return_value = "+1234567890"
        mock_send_code.return_value = (False, "Rate limit exceeded")
        
        response = client.post(
            "/api/v1/auth/phone/request",
            json={"phone": "+1234567890"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Failed to send" in response.json()["detail"]

    def test_request_phone_verification_missing_field(self, client):
        """Test requesting verification with missing phone field."""
        response = client.post(
            "/api/v1/auth/phone/request",
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestVerifyPhoneCode:
    """Tests for POST /api/v1/auth/phone/verify endpoint."""

    @patch('app.core.sms_service.verify_verification_code')
    @patch('app.core.sms_service.validate_phone_number')
    def test_verify_phone_code_new_user_success(
        self, mock_validate, mock_verify, client, mock_db_session
    ):
        """Test successfully verifying code for new user."""
        mock_validate.return_value = "+1234567890"
        mock_verify.return_value = True
        
        response = client.post(
            "/api/v1/auth/phone/verify",
            json={
                "phone": "+1234567890",
                "code": "123456"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["phone"] == "+1234567890"
        assert data["is_new_user"] is True
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify user was created
        user = db_session.query(User).filter(
            User.phone_number == "+1234567890"
        ).first()
        assert user is not None
        assert user.role == "user"

    @patch('app.core.sms_service.verify_verification_code')
    @patch('app.core.sms_service.validate_phone_number')
    def test_verify_phone_code_existing_user_success(
        self, mock_validate, mock_verify, client, mock_db_session
    ):
        """Test successfully verifying code for existing user."""
        # Create existing user
        existing_user = User(
            phone_number="+1234567890",
            role="user"
        )
        db_session.add(existing_user)
        db_session.commit()
        
        mock_validate.return_value = "+1234567890"
        mock_verify.return_value = True
        
        response = client.post(
            "/api/v1/auth/phone/verify",
            json={
                "phone": "+1234567890",
                "code": "123456"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["phone"] == "+1234567890"
        assert data["is_new_user"] is False
        assert data["user_id"] == str(existing_user.user_id)
        assert "access_token" in data
        assert "refresh_token" in data

    @patch('app.core.sms_service.verify_verification_code')
    @patch('app.core.sms_service.validate_phone_number')
    def test_verify_phone_code_invalid_code(
        self, mock_validate, mock_verify, client
    ):
        """Test verifying with invalid code."""
        mock_validate.return_value = "+1234567890"
        mock_verify.return_value = False
        
        response = client.post(
            "/api/v1/auth/phone/verify",
            json={
                "phone": "+1234567890",
                "code": "wrong_code"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or expired" in response.json()["detail"]

    @patch('app.core.sms_service.verify_verification_code')
    @patch('app.core.sms_service.validate_phone_number')
    def test_verify_phone_code_max_attempts_exceeded(
        self, mock_validate, mock_verify, client
    ):
        """Test verifying when max attempts exceeded."""
        mock_validate.return_value = "+1234567890"
        mock_verify.side_effect = ValueError("Max attempts exceeded")
        
        response = client.post(
            "/api/v1/auth/phone/verify",
            json={
                "phone": "+1234567890",
                "code": "123456"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Max attempts exceeded" in response.json()["detail"]

    @patch('app.core.sms_service.validate_phone_number')
    def test_verify_phone_code_invalid_phone(
        self, mock_validate, client
    ):
        """Test verifying with invalid phone number."""
        mock_validate.side_effect = ValueError("Invalid phone number format")
        
        response = client.post(
            "/api/v1/auth/phone/verify",
            json={
                "phone": "invalid",
                "code": "123456"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_phone_code_missing_fields(self, client):
        """Test verifying with missing fields."""
        response = client.post(
            "/api/v1/auth/phone/verify",
            json={"phone": "+1234567890"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.core.sms_service.verify_verification_code')
    @patch('app.core.sms_service.validate_phone_number')
    def test_verify_phone_code_phone_already_registered_different_user(
        self, mock_validate, mock_verify, client, mock_db_session
    ):
        """Test verifying when phone is registered to another user."""
        # This shouldn't happen due to unique constraint, but test error handling
        existing_user = User(
            phone_number="+1234567890",
            email="existing@example.com",
            role="user"
        )
        db_session.add(existing_user)
        db_session.commit()
        
        mock_validate.return_value = "+1234567890"
        mock_verify.return_value = True
        
        # Try to verify - should succeed and login existing user
        response = client.post(
            "/api/v1/auth/phone/verify",
            json={
                "phone": "+1234567890",
                "code": "123456"
            }
        )
        
        # Should succeed and login existing user
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(existing_user.user_id)
        assert data["is_new_user"] is False

