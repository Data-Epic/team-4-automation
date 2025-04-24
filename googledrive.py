from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.auth import credentials
from google.oauth2 import service_account


# Load your service account credentials file
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'

# Set up your credentials (make sure you handle the credentials appropriately)
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
def upload_image_to_drive(file_path, file_name):
    """Uploads an image file to Google Drive and returns the image URL."""
    try:
        # Build the Google Drive service
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Metadata for the file
        file_metadata = {'name': file_name}
        
        # Create the media body with the image
        media = MediaFileUpload(file_path, mimetype='image/png')
        
        # Upload the file
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        # Get the file URL
        file_id = uploaded_file.get('id')
        file_url = f"https://drive.google.com/uc?id={file_id}"
        return file_url
    
    except Exception as e:
        print(f"An error occurred while uploading the image: {e}")
        return None