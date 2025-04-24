import logging
from dotenv import load_dotenv
import os

load_dotenv()

from services.google_sheets import GoogleSheetsService
from services.cohere_analyzer import CohereAnalyzer
from services.chart_generator import PieChartGenerator
from services.google_drive import GoogleDriveService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to orchestrate review analysis workflow."""
    try:
        # Initialize services
        sheets_service = GoogleSheetsService()
        cohere_analyzer = CohereAnalyzer()
        drive_service = GoogleDriveService()

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

        # Generate and insert pie chart
        chart_generator = PieChartGenerator(sentiment_data)
        chart_buffer = chart_generator.generate_chart()
        
        # Save chart temporarily and upload to Drive
        file_path = "sentiment_chart.png"
        with open(file_path, "wb") as f:
            f.write(chart_buffer.read())
        
        image_url = drive_service.upload_image(file_path, "Sentiment_Chart.png")
        if image_url:
            sheets_service.insert_chart_image(image_url)
        
        logger.info("Review analysis completed successfully")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()