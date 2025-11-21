"""
Configuration file for Market Research Visualization
"""
import os
from datetime import datetime, timedelta

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
STATIC_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'static')
ANIMATED_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'animated')

# Data fetching settings
DEFAULT_START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')

# S&P 500 data source
SP500_WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

# API keys (set as environment variables)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')

# Cache settings
CACHE_EXPIRY_HOURS = 24  # How long to keep cached data

# Visualization settings
SECTOR_COLORS = {
    'Information Technology': '#007ACC',
    'Health Care': '#27AE60',
    'Financials': '#003366',
    'Consumer Discretionary': '#9B59B6',
    'Communication Services': '#E74C3C',
    'Industrials': '#7F8C8D',
    'Consumer Staples': '#8E44AD',
    'Energy': '#E37900',
    'Utilities': '#3498DB',
    'Real Estate': '#8D6E63',
    'Materials': '#95A5A6'
}

# Animation settings
ANIMATION_FRAME_DURATION = 800  # milliseconds
ANIMATION_TRANSITION_DURATION = 600  # milliseconds

# Bubble chart settings
BUBBLE_SIZE_MAX = 60
BUBBLE_OPACITY = 0.7
BUBBLE_BORDER_WIDTH = 1

# Performance settings
MAX_STOCKS_TO_DISPLAY = 200  # Limit for performance
