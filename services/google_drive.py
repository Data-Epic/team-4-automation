from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from config.settings import settings
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDriveService:
    """Handles file uploads to Google Drive."""

    def __init__(self):
        """Initialize Google Drive service with credentials."""
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.creds = service_account.Credentials.from_service_account_file(
            settings.CREDENTIALS_FILE, scopes=self.scopes
        )
        self.service = build('drive', 'v3', credentials=self.creds)

    def upload_image(self, file_path: str, file_name: str) -> Optional[str]:
        """Uploads an image file to Google Drive and returns the image URL.

        Args:
            file_path: Path to the image file.
            file_name: Name for the file on Google Drive.

        Returns:
            The URL of the uploaded file, or None if upload fails.
        """
        try:
            file_metadata = {'name': file_name}
            media = MediaFileUpload(file_path, mimetype='image/png')
            uploaded_file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id'
            ).execute()
            file_id = uploaded_file.get('id')
            file_url = f"https://drive.google.com/uc?id={file_id}"
            logger.info(f"Successfully uploaded image: {file_url}")
            return file_url
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return None