import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import CellFormat, Color, format_cell_range
from config.settings import settings
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Handles interactions with Google Sheets."""

    def __init__(self):
        """Initialize Google Sheets client with credentials."""
        scope = settings.SCOPES
        creds = ServiceAccountCredentials.from_json_keyfile_name(settings.CREDENTIALS_FILE, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(settings.SHEET_NAME).sheet1

    def read_reviews(self) -> List[Dict[str, Any]]:
        """Reads all reviews from the Google Sheet.

        Returns:
            A list of dictionaries containing review data.
        """
        try:
            reviews = self.sheet.get_all_records()
            logger.info(f"Read {len(reviews)} reviews from Google Sheet")
            return reviews
        except Exception as e:
            logger.error(f"Failed to read reviews: {e}")
            raise

    def write_analysis(self, row_index: int, sentiment: str, summary: str) -> None:
        """Writes sentiment analysis results to the Google Sheet.

        Args:
            row_index: Row number to write to (1-based indexing).
            sentiment: Sentiment classification (Positive, Negative, Neutral).
            summary: One-sentence summary of the review.
        """
        try:
            action_needed = "Yes" if sentiment.lower() == "negative" else "No"
            self.sheet.update_cell(row_index, 4, sentiment)
            self.sheet.update_cell(row_index, 5, summary)
            self.sheet.update_cell(row_index, 6, action_needed)

            if sentiment.lower() == "negative":
                fmt = CellFormat(backgroundColor=Color(1, 0.9, 0.9))
                format_cell_range(self.sheet, f"A{row_index}:D{row_index}", fmt)
            logger.info(f"Wrote analysis to row {row_index}: Sentiment={sentiment}")
        except Exception as e:
            logger.error(f"Failed to write analysis to row {row_index}: {e}")
            raise
        
    def insert_chart_image(self, image_url: str) -> None:
        """Inserts a chart image into the Google Sheet using IMAGE formula.

        Args:
            image_url: URL of the image to insert.
        """
        try:
            self.sheet.update_cell(2, 6, f'=IMAGE("{image_url}", 1)')
            logger.info("Inserted chart image into sheet")
        except Exception as e:
            logger.error(f"Failed to insert chart image: {e}")
            raise