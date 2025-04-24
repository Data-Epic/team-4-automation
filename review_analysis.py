# Importing the required libraries
import cohere
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *
import matplotlib.pyplot as plt
import pandas as pd
import re
import time
from io import BytesIO
from cohere.errors import TooManyRequestsError
from googledrive import upload_image_to_drive  
from config import CREDENTIALS_FILE, SHEET_NAME, COHERE_API_KEY

# A class for google sheet handler
class GoogleSheetHandler:
    def __init__(self, creds_file, sheet_name):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name).sheet1
        
    # A function to read the reviews in the sheet
    def read_reviews(self):
        return self.sheet.get_all_records()
    
    # A Function to write the analysis to the sheet
    def write_analysis(self, row_index, sentiment, summary):
        action_needed = "Yes" if sentiment.lower() == "negative" else "No"
        self.sheet.update_cell(row_index, 4, sentiment)
        self.sheet.update_cell(row_index, 5, summary)
        self.sheet.update_cell(row_index, 6, action_needed)

        if sentiment.lower() == "negative":
            fmt = CellFormat(backgroundColor=Color(1, 0.9, 0.9))  # Light red
            format_cell_range(self.sheet, f"A{row_index}:D{row_index}", fmt)
    
    # A function for pie chart
    def insert_chart_image(self, image_buffer):
        """Uploads the chart image to Google Drive and inserts the image into the sheet."""
        # Save image to file
        file_path = "sentiment_chart.png"
        with open(file_path, "wb") as f:
            f.write(image_buffer.read())

        # Upload to Drive and insert URL using IMAGE formula
        image_url = upload_image_to_drive(file_path, "Sentiment_Chart.png")
        if image_url:
            self.sheet.update("F2", f'=IMAGE("{image_url}", 1)')

# Creating a class for the cohere analyzer
class CohereAnalyzer:
    def __init__(self, api_key):
        self.co = cohere.Client(api_key)

    def analyze_review(self, text):
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
                response = self.co.chat(
                    model="command-r-plus",
                    message=prompt,
                    temperature=0.3,
                )
                break
            except TooManyRequestsError:
                print("⚠️ Rate limit reached. Sleeping for 60 seconds...")
                time.sleep(60)

        full_text = response.text.strip()
        label_match = re.search(r"\*\*Label:\*\*\s*(\w+)", full_text, re.IGNORECASE)
        summary_match = re.search(r"\*\*Summary:\*\*\s*(.+)", full_text, re.IGNORECASE)

        sentiment = label_match.group(1).capitalize() if label_match else "Neutral"
        summary = summary_match.group(1).strip() if summary_match else ""

        print(f"✅ Review analyzed. Sentiment: {sentiment}, Summary: {summary}")
        return sentiment, summary

# Creating a class for pie chart generator
class PieChartGenerator:
    def __init__(self, sentiment_data):
        self.data = sentiment_data

    def generate_chart_image(self):
        df = pd.DataFrame(self.data)
        sentiment_counts = df['AI Sentiment'].value_counts()
        plt.figure(figsize=(6, 6))
        plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=["green", "red", "gray"])
        plt.title("Sentiment Breakdown")

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        return buffer

# The main function
def main():
    sheet_handler = GoogleSheetHandler(CREDENTIALS_FILE, SHEET_NAME)
    analyzer = CohereAnalyzer(COHERE_API_KEY)

    data = sheet_handler.read_reviews()
    sentiment_data = []

    for idx, row in enumerate(data, start=2):
        review = row.get("Review", "").strip()
        if not review:
            continue

        sentiment, summary = analyzer.analyze_review(review)
        sentiment_data.append({"AI Sentiment": sentiment})
        sheet_handler.write_analysis(idx, sentiment, summary)

    chart_generator = PieChartGenerator(sentiment_data)
    chart_image = chart_generator.generate_chart_image()
    sheet_handler.insert_chart_image(chart_image)


if __name__ == "__main__":
    main()
