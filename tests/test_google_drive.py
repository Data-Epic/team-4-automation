import pytest
from services.google_drive import GoogleDriveService
from unittest.mock import MagicMock, patch, mock_open
import os

@pytest.fixture
def drive_service_with_mocks():
    with patch("services.google_drive.MediaFileUpload") as mock_media_upload, \
         patch("services.google_drive.build") as mock_build, \
         patch("services.google_drive.service_account.Credentials.from_service_account_file") as mock_creds:
         
        # Setup MediaFileUpload mock
        mock_media = MagicMock()
        mock_media_upload.return_value = mock_media

        # Setup Drive API mocks
        mock_service = MagicMock()

        mock_files = MagicMock()
        mock_file_create = MagicMock()
        mock_file_create.execute.return_value = {"id": "test113"}
        mock_files.create.return_value = mock_file_create
        mock_service.files.return_value = mock_files

        mock_build.return_value = mock_service

        return GoogleDriveService(), mock_files, mock_media_upload

def test_upload_image_success(drive_service_with_mocks):
    drive_service, mock_files, mock_media_upload = drive_service_with_mocks

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", new_callable=mock_open, read_data=b"data"), \
         patch("services.google_drive.MediaFileUpload") as mock_media_upload:
        file_url = drive_service.upload_image("test.png", "test_file")

        assert file_url == "https://drive.google.com/uc?id=test113"
        mock_files.create.assert_called_once()
        mock_media_upload.assert_called_once_with("test.png", mimetype="image/png")

def test_upload_image_failure(drive_service_with_mocks):
    drive_service, mock_files, mock_media_upload = drive_service_with_mocks

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", new_callable=mock_open, read_data=b"data"):
         
        # Simulate an exception when creating the file
        mock_files.create.side_effect = Exception("Upload failed")

        file_url = drive_service.upload_image("test.png", "test_file")

        assert file_url is None
        mock_files.create.assert_called_once()
