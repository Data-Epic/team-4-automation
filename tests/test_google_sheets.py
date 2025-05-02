import pytest
from services.google_sheets import GoogleSheetsService
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_sheets_setup():
    with patch("services.google_sheets.gspread.authorize") as mock_auth, \
         patch("services.google_sheets.ServiceAccountCredentials.from_json_keyfile_name") as mock_creds:
        mock_sheet = MagicMock()
        mock_client = MagicMock()
        mock_client.open.return_value.sheet1 = mock_sheet
        mock_auth.return_value = MagicMock()
        mock_auth_instance = mock_auth.return_value
        mock_auth_instance.authorize.return_value = mock_client

        google_sheets = GoogleSheetsService()
        google_sheets.sheet = mock_sheet

        yield google_sheets, mock_sheet

def test_read_reviews_success(mock_sheets_setup):
    google_sheets, mock_sheet = mock_sheets_setup
    mock_sheet.get_all_records.return_value = [{"Review": "Great!"}]

    result = google_sheets.read_reviews()
    assert result == [{"Review": "Great!"}]
    mock_sheet.get_all_records.assert_called_once()

def test_write_analysis_writes_to_sheet(mock_sheets_setup):
    google_sheets, mock_sheet = mock_sheets_setup
   
    google_sheets.write_analysis(2, "Negative", "Not a good product")
    assert mock_sheet.update_cell.call_count == 3
    mock_sheet.update_cell.assert_any_call(2, 4, "Negative")
    mock_sheet.update_cell.assert_any_call(2, 5, "Not a good product")
    mock_sheet.update_cell.assert_any_call(2, 6, "Yes")

@patch("services.google_sheets.build")
def test_create_pie_chart_updates_sheet(mock_build, mock_sheets_setup):
    google_sheets, mock_sheet = mock_sheets_setup
   
    sentiment_data = [
        {"AI Sentiment": "Positive"},
        {"AI Sentiment": "Negative"},
        {"AI Sentiment": "Neutral"}
    ]

    # Mock Sheets API
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_batch_update = mock_service.spreadsheets.return_value.batchUpdate
    mock_batch_update.return_value.execute.return_value = {}

    # Using a fake spreadsheet id
    mock_sheet.spreadsheet.id = "fake_spreadsheet_id"
    mock_sheet.id = 1

    google_sheets.create_pie_chart(sentiment_data)

    # Verify that the chart data was written
    mock_sheet.update.assert_any_call("H1:I4", [["Sentiment", "Count"], ["Positive", 1], ["Negative", 1], ["Neutral", 1]])

    # Verify that the Sheets API was called
    mock_sheet.update_cell.assert_called_once()