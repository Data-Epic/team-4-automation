import cohere
import re
import logging
import time
from typing import Tuple
import os
from cohere.errors import TooManyRequestsError
from cohere import ClassifyExample

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CohereAnalyzer:
    """Handles sentiment analysis and summarization using Cohere API."""

    def __init__(self):
        """Initialize Cohere client with API key."""
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            logger.error("COHERE_API_KEY is not set in environment variables")
            raise ValueError("COHERE_API_KEY is not set")
        logger.info(f"COHERE_API_KEY length: {len(api_key)}")  # Debug log
        self.client = cohere.Client(api_key)

    def analyze_review(self, text: str) -> Tuple[str, str]:
        """Analyzes a review for sentiment and generates a summary.

        Args:
            text: The review text to analyze.

        Returns:
            A tuple containing the sentiment (Positive, Negative, Neutral) and summary.
        """
        # Classification using custom model
        while True:
            try:
                classification = self.client.classify(
                    model='62cf2a52-4c96-494d-a344-2ee6edcab2e5-ft',
                    inputs=[text]
                )
                sentiment = classification.classifications[0].prediction
                break
            except TooManyRequestsError:
                logger.warning("Rate limit reached for classification. Sleeping for 60 seconds...")
                time.sleep(60)
            except Exception as e:
                logger.error(f"Classification error: {str(e)}")
                sentiment = "Neutral"
                break

        # Summarization using chat
        summarize_prompt = f"Summarize this review in one sentence: {text}"
        while True:
            try:
                summary_response = self.client.chat(
                    model="command-r-plus",
                    message=summarize_prompt,
                    temperature=0.3,
                )
                summary = summary_response.text.strip()
                break
            except TooManyRequestsError:
                logger.warning("Rate limit reached for chat. Sleeping for 60 seconds...")
                time.sleep(60)
            except Exception as e:
                logger.error(f"Chat error for summarization: {str(e)}")
                summary = ""
                break

        logger.info(f"Analyzed review. Sentiment: {sentiment}, Summary: {summary}")
        return sentiment, summary