import cohere
from cohere.errors import TooManyRequestsError
import re
import time
import logging
from typing import Tuple
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CohereAnalyzer:
    """Handles sentiment analysis and summarization using Cohere API."""

    def __init__(self):
        """Initialize Cohere client with API key."""
        self.client = cohere.Client(settings.COHERE_API_KEY)

    def analyze_review(self, text: str) -> Tuple[str, str]:
        """Analyzes a review for sentiment and generates a summary.

        Args:
            text: The review text to analyze.

        Returns:
            A tuple containing the sentiment (Positive, Negative, Neutral) and summary.
        """
        prompt = (
            "You are a sentiment analysis and summarization assistant. "
            "Given the review below, respond with sentiment classification "
            "(Positive, Neutral, or Negative) and provide a one-sentence summary.\n\n"
            f"Review: {text}\n\n"
            "Format your response like this:\n"
            "**Label:** <Positive/Neutral/Negative>\n"
            "**Summary:** <Summary here>"
        )

        while True:
            try:
                response = self.client.chat(
                    model="command-r-plus",
                    message=prompt,
                    temperature=0.3,
                )
                break
            except TooManyRequestsError:
                logger.warning("Rate limit reached. Sleeping for 60 seconds...")
                time.sleep(60)

        full_text = response.text.strip()
        label_match = re.search(r"\*\*Label:\*\*\s*(\w+)", full_text, re.IGNORECASE)
        summary_match = re.search(r"\*\*Summary:\*\*\s*(.+)", full_text, re.IGNORECASE)

        sentiment = label_match.group(1).capitalize() if label_match else "Neutral"
        summary = summary_match.group(1).strip() if summary_match else ""
        
        logger.info(f"Analyzed review. Sentiment: {sentiment}, Summary: {summary}")
        return sentiment, summary