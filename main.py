import logging
from services.google_sheets import GoogleSheetsService
from services.cohere_analyzer import CohereAnalyzer
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to orchestrate review analysis workflow."""
    try:
        # Initialize services
        sheets_service = GoogleSheetsService()
        cohere_analyzer = CohereAnalyzer()

        # Read reviews
        reviews = sheets_service.read_reviews()
        sentiment_data = []

        # Analyze reviews
        for idx, row in enumerate(reviews, start=2):
            review = row.get("Review", "").strip()
            if not review:
                logger.warning(f"Empty review at row {idx}")
                continue

            sentiment, summary = cohere_analyzer.analyze_review(review)
            sentiment_data.append({"AI Sentiment": sentiment})
            sheets_service.write_analysis(idx, sentiment, summary)

        # Create pie chart directly in the sheet
        sheets_service.create_pie_chart(sentiment_data)
        
        logger.info("Review analysis completed successfully")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()