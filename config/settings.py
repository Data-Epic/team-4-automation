import os
from typing import List

class Settings:
    """Configuration settings for the review analysis application."""
    
    CREDENTIALS_FILE: str = os.getenv("CREDENTIALS_FILE", "credentials.json")
    SHEET_NAME: str = os.getenv("SHEET_NAME", "Redmi6_Reviews_Team4")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    SCOPES: List[str] = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

settings = Settings()