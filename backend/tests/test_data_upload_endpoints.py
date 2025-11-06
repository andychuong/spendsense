"""Unit tests for data upload endpoints."""

import pytest
import uuid
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch, Mock
from fastapi import status
from fastapi.testclient import TestClient

from app.models.data_upload import DataUpload, FileType, UploadStatus
from app.models.user import User, UserRole


class TestUploadDataFile:
    """Tests for POST /api/v1/data/upload endpoint."""

    @patch("app.api.v1.endpoints.data_upload.upload_file_to_s3")
    @patch("app.api.v1.endpoints.data_upload.generate_s3_key")
    @patch("app.api.v1.endpoints.data_upload.validate_file_size")
    @patch("app.api.v1.endpoints.data_upload.validate_file_type")
    def test_upload_data_file_json_success(
        self,
        mock_validate_file_type,
        mock_validate_file_size,
        mock_generate_s3_key,
        mock_upload_file_to_s3,
        client,
        test_user,
        auth_headers,
    ):
        """Test successfully uploading a JSON file."""
        from app.main import app
        from app.database import get_db

        # Setup mocks
        mock_validate_file_type.return_value = "json"
        mock_validate_file_size.return_value = None
        mock_generate_s3_key.return_value = "uploads/test-user-id/test-upload-id/test.json"
        mock_upload_file_to_s3.return_value = None

        # Create mock upload record
        upload_id = uuid.uuid4()
        data_upload = DataUpload(
            upload_id=upload_id,
            user_id=test_user.user_id,
            file_name="test.json",
            file_size=1024,
            file_type=FileType.JSON,
            s3_key="uploads/test-user-id/test-upload-id/test.json",
            s3_bucket="spendsense-data",
            status=UploadStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Setup database mocks
        mock_db_session = MagicMock()
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        def mock_refresh(obj):
            """Mock refresh that sets attributes."""
            obj.upload_id = upload_id
            obj.user_id = test_user.user_id
            obj.file_name = "test.json"
            obj.file_size = 1024
            obj.file_type = FileType.JSON
            obj.s3_key = "uploads/test-user-id/test-upload-id/test.json"
            obj.s3_bucket = "spendsense-data"
            obj.status = UploadStatus.PENDING
            obj.created_at = datetime.utcnow()

        mock_db_session.refresh = mock_refresh

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        # Mock uuid.uuid4 to return fixed upload_id
        with patch("app.api.v1.endpoints.data_upload.uuid.uuid4", return_value=upload_id):
            # Create file content
            file_content = b'{"test": "data"}'
            file = ("test.json", BytesIO(file_content), "application/json")

            response = client.post(
                "/api/v1/data/upload",
                headers=auth_headers,
                files={"file": file}
            )

        app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["upload_id"] == str(upload_id)
        assert data["file_name"] == "test.json"
        assert data["file_type"] == "json"
        assert data["status"] == "pending"
        assert data["user_id"] == str(test_user.user_id)

        # Verify mocks were called
        mock_validate_file_type.assert_called_once()
        mock_validate_file_size.assert_called_once()
        mock_generate_s3_key.assert_called_once()
        mock_upload_file_to_s3.assert_called_once()
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("app.api.v1.endpoints.data_upload.upload_file_to_s3")
    @patch("app.api.v1.endpoints.data_upload.generate_s3_key")
    @patch("app.api.v1.endpoints.data_upload.validate_file_size")
    @patch("app.api.v1.endpoints.data_upload.validate_file_type")
    def test_upload_data_file_csv_success(
        self,
        mock_validate_file_type,
        mock_validate_file_size,
        mock_generate_s3_key,
        mock_upload_file_to_s3,
        client,
        test_user,
        auth_headers,
    ):
        """Test successfully uploading a CSV file."""
        from app.main import app
        from app.database import get_db

        # Setup mocks
        mock_validate_file_type.return_value = "csv"
        mock_validate_file_size.return_value = None
        mock_generate_s3_key.return_value = "uploads/test-user-id/test-upload-id/test.csv"
        mock_upload_file_to_s3.return_value = None

        # Create mock upload record
        upload_id = uuid.uuid4()

        # Setup database mocks
        mock_db_session = MagicMock()
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        def mock_refresh(obj):
            """Mock refresh that sets attributes."""
            obj.upload_id = upload_id
            obj.user_id = test_user.user_id
            obj.file_name = "test.csv"
            obj.file_size = 2048
            obj.file_type = FileType.CSV
            obj.s3_key = "uploads/test-user-id/test-upload-id/test.csv"
            obj.s3_bucket = "spendsense-data"
            obj.status = UploadStatus.PENDING
            obj.created_at = datetime.utcnow()

        mock_db_session.refresh = mock_refresh

        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        # Mock uuid.uuid4 to return fixed upload_id
        with patch("app.api.v1.endpoints.data_upload.uuid.uuid4", return_value=upload_id):
            # Create file content
            file_content = b"date,amount,merchant\n2024-01-01,100.00,Store"
            file = ("test.csv", BytesIO(file_content), "text/csv")

            response = client.post(
                "/api/v1/data/upload",
                headers=auth_headers,
                files={"file": file}
            )

        app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["upload_id"] == str(upload_id)
        assert data["file_name"] == "test.csv"
        assert data["file_type"] == "csv"
        assert data["status"] == "pending"

        # Verify mocks were called
        mock_validate_file_type.assert_called_once()
        mock_validate_file_size.assert_called_once()
        mock_generate_s3_key.assert_called_once()
        mock_upload_file_to_s3.assert_called_once()

    def test_upload_data_file_unauthorized(self, mock_db_session):
        """Test uploading a file without authentication."""
        from app.main import app
        from app.database import get_db
        from fastapi.testclient import TestClient

        # Create client without auth override
        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        file_content = b'{"test": "data"}'
        file = ("test.json", BytesIO(file_content), "application/json")

        with TestClient(app) as test_client:
            response = test_client.post(
                "/api/v1/data/upload",
                files={"file": file}
            )

        app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.v1.endpoints.data_upload.validate_file_type")
    def test_upload_data_file_invalid_type(
        self,
        mock_validate_file_type,
        client,
        test_user,
        auth_headers,
    ):
        """Test uploading a file with invalid file type."""
        mock_validate_file_type.side_effect = ValueError("Unsupported file type. Allowed types: json, csv")

        file_content = b"test content"
        file = ("test.txt", BytesIO(file_content), "text/plain")

        response = client.post(
            "/api/v1/data/upload",
            headers=auth_headers,
            files={"file": file}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Unsupported file type" in data["detail"]

    @patch("app.api.v1.endpoints.data_upload.validate_file_type")
    @patch("app.api.v1.endpoints.data_upload.validate_file_size")
    def test_upload_data_file_too_large(
        self,
        mock_validate_file_size,
        mock_validate_file_type,
        client,
        test_user,
        auth_headers,
    ):
        """Test uploading a file that exceeds maximum size."""
        mock_validate_file_type.return_value = "json"
        mock_validate_file_size.side_effect = ValueError(
            "File size (15000000 bytes) exceeds maximum allowed size (10485760 bytes)"
        )

        file_content = b"x" * 15000000  # 15MB
        file = ("test.json", BytesIO(file_content), "application/json")

        response = client.post(
            "/api/v1/data/upload",
            headers=auth_headers,
            files={"file": file}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "exceeds maximum allowed size" in data["detail"]

    @patch("app.api.v1.endpoints.data_upload.upload_file_to_s3")
    @patch("app.api.v1.endpoints.data_upload.generate_s3_key")
    @patch("app.api.v1.endpoints.data_upload.validate_file_size")
    @patch("app.api.v1.endpoints.data_upload.validate_file_type")
    def test_upload_data_file_s3_upload_failure(
        self,
        mock_validate_file_type,
        mock_validate_file_size,
        mock_generate_s3_key,
        mock_upload_file_to_s3,
        client,
        test_user,
        auth_headers,
    ):
        """Test handling S3 upload failure."""
        mock_validate_file_type.return_value = "json"
        mock_validate_file_size.return_value = None
        mock_generate_s3_key.return_value = "uploads/test-user-id/test-upload-id/test.json"
        mock_upload_file_to_s3.side_effect = Exception("S3 upload failed")

        file_content = b'{"test": "data"}'
        file = ("test.json", BytesIO(file_content), "application/json")

        response = client.post(
            "/api/v1/data/upload",
            headers=auth_headers,
            files={"file": file}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Failed to upload file to S3" in data["detail"]


class TestGetUploadStatus:
    """Tests for GET /api/v1/data/upload/{upload_id} endpoint."""

    def test_get_upload_status_success(
        self,
        client,
        test_user,
        auth_headers,
        mock_db_session,
    ):
        """Test successfully getting upload status."""
        upload_id = uuid.uuid4()
        data_upload = DataUpload(
            upload_id=upload_id,
            user_id=test_user.user_id,
            file_name="test.json",
            file_size=1024,
            file_type=FileType.JSON,
            s3_key="uploads/test-user-id/test-upload-id/test.json",
            s3_bucket="spendsense-data",
            status=UploadStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Setup database mocks
        mock_filter = MagicMock()
        mock_filter.first.return_value = data_upload
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        response = client.get(
            f"/api/v1/data/upload/{upload_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["upload_id"] == str(upload_id)
        assert data["file_name"] == "test.json"
        assert data["status"] == "pending"
        assert data["user_id"] == str(test_user.user_id)

    def test_get_upload_status_not_found(
        self,
        client,
        test_user,
        auth_headers,
        mock_db_session,
    ):
        """Test getting upload status for non-existent upload."""
        upload_id = uuid.uuid4()

        # Setup database mocks
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        response = client.get(
            f"/api/v1/data/upload/{upload_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Upload not found" in data["detail"]

    def test_get_upload_status_unauthorized(
        self,
        mock_db_session,
    ):
        """Test getting upload status without authentication."""
        from app.main import app
        from app.database import get_db
        from fastapi.testclient import TestClient

        # Create client without auth override
        def override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        upload_id = uuid.uuid4()

        with TestClient(app) as test_client:
            response = test_client.get(
                f"/api/v1/data/upload/{upload_id}"
            )

        app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_upload_status_other_user_forbidden(
        self,
        client,
        test_user,
        auth_headers,
        mock_db_session,
    ):
        """Test that users cannot view other users' uploads."""
        upload_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        data_upload = DataUpload(
            upload_id=upload_id,
            user_id=other_user_id,  # Different user
            file_name="test.json",
            file_size=1024,
            file_type=FileType.JSON,
            s3_key="uploads/other-user-id/test-upload-id/test.json",
            s3_bucket="spendsense-data",
            status=UploadStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Setup database mocks
        mock_filter = MagicMock()
        mock_filter.first.return_value = data_upload
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        response = client.get(
            f"/api/v1/data/upload/{upload_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "Not authorized to view this upload" in data["detail"]

    def test_get_upload_status_operator_access(
        self,
        client,
        test_operator_user,
        operator_auth_headers,
        mock_db_session,
    ):
        """Test that operators can view any user's uploads."""
        upload_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        data_upload = DataUpload(
            upload_id=upload_id,
            user_id=other_user_id,  # Different user
            file_name="test.json",
            file_size=1024,
            file_type=FileType.JSON,
            s3_key="uploads/other-user-id/test-upload-id/test.json",
            s3_bucket="spendsense-data",
            status=UploadStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Setup database mocks
        mock_filter = MagicMock()
        mock_filter.first.return_value = data_upload
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Override get_current_active_user to return operator
        from app.main import app
        from app.core.dependencies import get_current_active_user

        def override_get_current_active_user():
            return test_operator_user

        app.dependency_overrides[get_current_active_user] = override_get_current_active_user

        response = client.get(
            f"/api/v1/data/upload/{upload_id}",
            headers=operator_auth_headers
        )

        app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["upload_id"] == str(upload_id)

    def test_get_upload_status_admin_access(
        self,
        client,
        test_admin_user,
        admin_auth_headers,
        mock_db_session,
    ):
        """Test that admins can view any user's uploads."""
        upload_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        data_upload = DataUpload(
            upload_id=upload_id,
            user_id=other_user_id,  # Different user
            file_name="test.json",
            file_size=1024,
            file_type=FileType.JSON,
            s3_key="uploads/other-user-id/test-upload-id/test.json",
            s3_bucket="spendsense-data",
            status=UploadStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Setup database mocks
        mock_filter = MagicMock()
        mock_filter.first.return_value = data_upload
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Override get_current_active_user to return admin
        from app.main import app
        from app.core.dependencies import get_current_active_user

        def override_get_current_active_user():
            return test_admin_user

        app.dependency_overrides[get_current_active_user] = override_get_current_active_user

        response = client.get(
            f"/api/v1/data/upload/{upload_id}",
            headers=admin_auth_headers
        )

        app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["upload_id"] == str(upload_id)

