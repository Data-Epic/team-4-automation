import pytest
import re
from unittest.mock import patch, MagicMock
from services.cohere_analyzer import CohereAnalyzer
from cohere.errors import TooManyRequestsError

@pytest.fixture
def analyzer_with_mocked_client():
    """Returns a CohereAnalyzer instance and its mocked Cohere client."""
    with patch("services.cohere_analyzer.os.getenv", return_value = "fake-api-key"):
        with patch("services.cohere_analyzer.cohere.Client") as MockCohereClient:
            mocked_client = MagicMock()
            MockCohereClient.return_value = mocked_client
            analyzer = CohereAnalyzer()
            return analyzer, mocked_client

def test_analyze_review_returns_correct_sentiment_and_summary(analyzer_with_mocked_client):
    analyzer, mock_client = analyzer_with_mocked_client
    
    # Mock the classify and chat responses
    mock_classify_response = MagicMock()
    mock_classify_response.classifications = [MagicMock(prediction="Positive")]
    mock_client.classify.return_value = mock_classify_response
    
    mock_response = MagicMock()
    mock_response.text = "This product is amazing!"
    mock_client.chat.return_value = mock_response

    # Act
    sentiment, summary = analyzer.analyze_review("I loved this product!")

    # Assert
    assert sentiment == "Positive"
    assert summary == "This product is amazing!"

def test_analyze_review_retries_on_rate_limit(analyzer_with_mocked_client):
    analyzer, mock_client = analyzer_with_mocked_client

    # Mock TooManyRequestErrors for classify and chat methods
    first_error = TooManyRequestsError("Rate limit hit")
    valid_classify_response = MagicMock()
    valid_classify_response.classifications = [MagicMock(prediction="Neutral")]
    mock_client.classify.side_effect = [first_error, valid_classify_response]
    
    valid_response = MagicMock()
    valid_response.text = "It was okay."
    mock_client.chat.side_effect = [first_error, valid_response]

    # Act
    with patch("time.sleep") as mock_sleep:
        sentiment, summary = analyzer.analyze_review("It was okay.")

     # Assert
    assert sentiment == "Neutral"
    assert summary == "It was okay."

    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(60)
