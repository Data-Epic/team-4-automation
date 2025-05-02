import pytest
from io import BytesIO
from services.chart_generator import PieChartGenerator

def test_generate_chart_success():
    sample_data = [
        {"AI Sentiment": "Positive"},
        {"AI Sentiment": "Negative"},
        {"AI Sentiment": "Neutral"}
    ]
    chart_generator = PieChartGenerator(sample_data)
    chart = chart_generator.generate_chart()

    assert isinstance(chart, BytesIO)