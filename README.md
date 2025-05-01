# Automate Review Analysis using Python and GSpread
## Overview
This python script automates review analysis of the Redmi 6, using the GSpread library alongside with Cohere AI API. The project involves analyzing the sentiment and summarizing each review to generate actionable insights.

## Dataset Summary
The dataset consists of user reviews for the Redmi 6, collected from kaggle. Each entry
contains text feedback provided by users regarding their experiences with the device. 

## Tools
- Python
- GSpread
- Google Sheets API
- Cohere AI API

## Setup Instructions
**Clone the repository**:
```
git clone https://github.com/Data-Epic/team-4-automation.git
```
**Navigate to the project directory**:
```
cd google-sheets-automation
```
**Setup a python virtual environment and install the required dependencies**:
```
python -m venv myenv
myenv\Scripts\activate
```
```
pip install -r requirements.txt
```
**Configure API keys for GSpread and Cohere API**:
- Place your Google service account key file in the project directory and name it `credentials.json`.

- Create a `.env` file in the root directory and add the Credential file, GoogleSheet Name/ID and Cohere API key.
```
CREDENTIALS_FILE="credentials.json"
SHEET_NAME="Redmi6_Reviews"
COHERE_API_KEY = <your_api_key_here>
```
**Run the script**:
```
python main.py
```

## How It Works

1. Connects to the Google Sheets file containing user reviews using the provided credentials and reads all reviews from the “Review” column.

2. Sends each review to Cohere API for sentiment analysis (Positive, Negative, or Neutral) and one-sentence summary generation.

3. Writes back to Google sheets by populating the "AI Sentiment" column with the returned sentiment, the "AI Summary" column with the one-sentence summary and the "Action Needed?" column, with "Yes" if the sentiment is Negative, otherwise "No". 

4. Generates a pie chart displaying the percentage breakdown of each sentiment type and includes it within the Google Sheet.

## Contributors
- Awotunde Adenike
- Simon Dickson
- Glory Arowojolu
