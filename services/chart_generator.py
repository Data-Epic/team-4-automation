import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PieChartGenerator:
    """Generates a pie chart for sentiment distribution."""

    def __init__(self, sentiment_data: List[Dict[str, str]]):
        """Initialize with sentiment data.

        Args:
            sentiment_data: List of dictionaries containing sentiment information.
        """
        self.data = sentiment_data

    def generate_chart(self) -> BytesIO:
        """Generates a pie chart and returns it as a BytesIO buffer.

        Returns:
            A BytesIO buffer containing the pie chart image.
        """
        try:
            df = pd.DataFrame(self.data)
            sentiment_counts = df['AI Sentiment'].value_counts()
            
            plt.figure(figsize=(8, 8))
            plt.pie(
                sentiment_counts,
                labels=sentiment_counts.index,
                autopct='%1.1f%%',
                colors=["green", "red", "gray"]
            )
            plt.title("Sentiment Breakdown")
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150)  # High DPI for better quality
            buffer.seek(0)
            plt.close()
            
            logger.info("Generated pie chart")
            return buffer
        except Exception as e:
            logger.error(f"Failed to generate pie chart: {e}")
            raise