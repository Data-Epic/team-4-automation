import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import CellFormat, Color, format_cell_range
from googleapiclient.discovery import build
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

    def create_pie_chart(self, sentiment_data: List[Dict[str, str]]) -> None:
        """Creates a pie chart in the Google Sheet using sentiment data.

        Args:
            sentiment_data: List of dictionaries containing sentiment information.
        """
        try:
            self.sheet.update_cell(2, 7, '')

            # Initialize Sheets API service
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                settings.CREDENTIALS_FILE, settings.SCOPES
            )
            service = build('sheets', 'v4', credentials=creds)
            spreadsheet_id = self.sheet.spreadsheet.id

            # Write sentiment counts to a temporary range (e.g., H1:I4)
            from pandas import DataFrame
            df = DataFrame(sentiment_data)
            sentiment_counts = df['AI Sentiment'].value_counts()
            
            # Prepare data for the chart
            chart_data = [["Sentiment", "Count"]]
            for sentiment, count in sentiment_counts.items():
                chart_data.append([sentiment, count])
            
            # Write the data to H1:I4
            self.sheet.update('H1:I4', chart_data)

            # Create the pie chart
            requests = [{
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "Sentiment Distribution",
                            "pieChart": {
                                "legendPosition": "LABELED_LEGEND",
                                "threeDimensional": True,
                                "domain": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": self.sheet.id,
                                            "startRowIndex": 0,
                                            "endRowIndex": len(chart_data),
                                            "startColumnIndex": 7,  # H
                                            "endColumnIndex": 8     # I
                                        }]
                                    }
                                },
                                "series": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": self.sheet.id,
                                            "startRowIndex": 0,
                                            "endRowIndex": len(chart_data),
                                            "startColumnIndex": 8,  # I
                                            "endColumnIndex": 9     # J
                                        }]
                                    }
                                }
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": self.sheet.id,
                                    "rowIndex": 1,  # Row 2
                                    "columnIndex": 9  # Column J
                                },
                                "widthPixels": 500,
                                "heightPixels": 500
                            }
                        }
                    }
                }
            }]

            # Execute the request
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": requests}
            ).execute()

            logger.info("Inserted pie chart into sheet")
        except Exception as e:
            logger.error(f"Failed to insert pie chart: {e}")
            raise