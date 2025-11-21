"""
Configuration file for Market Research Visualization
Backward-compatible wrapper around pydantic-settings

For new code, import from src.config_settings directly:
    from src.config_settings import get_settings
    settings = get_settings()
    
For legacy code, this module provides the same interface as before
"""
import os
from datetime import datetime, timedelta

# Try to load pydantic settings, fall back to legacy if not available
try:
    from src.config_settings import get_settings
    _settings = get_settings()
    _use_pydantic = True
except ImportError:
    _use_pydantic = False
    _settings = None

# Base directories
if _use_pydantic and _settings:
    BASE_DIR = _settings.base_dir
    DATA_DIR = _settings.data_dir
    CACHE_DIR = _settings.cache_dir
    OUTPUT_DIR = _settings.output_dir
    STATIC_OUTPUT_DIR = _settings.static_output_dir
    ANIMATED_OUTPUT_DIR = _settings.animated_output_dir
    LOG_DIR = _settings.log_dir
else:
    # Legacy fallback
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    CACHE_DIR = os.path.join(DATA_DIR, 'cache')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
    STATIC_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'static')
    ANIMATED_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'animated')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Data fetching settings
if _use_pydantic and _settings:
    DEFAULT_START_DATE = _settings.default_start_date
    DEFAULT_END_DATE = _settings.default_end_date
    SP500_WIKIPEDIA_URL = _settings.sp500_wikipedia_url
    ALPHA_VANTAGE_API_KEY = _settings.alpha_vantage_api_key
    CACHE_EXPIRY_HOURS = _settings.cache_expiry_hours
else:
    DEFAULT_START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')
    SP500_WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    CACHE_EXPIRY_HOURS = 24

# Visualization settings
if _use_pydantic and _settings:
    SECTOR_COLORS = _settings.sector_colors
    ANIMATION_FRAME_DURATION = _settings.animation_frame_duration
    ANIMATION_TRANSITION_DURATION = _settings.animation_transition_duration
    BUBBLE_SIZE_MAX = _settings.bubble_size_max
    BUBBLE_OPACITY = _settings.bubble_opacity
    BUBBLE_BORDER_WIDTH = _settings.bubble_border_width
    MAX_STOCKS_TO_DISPLAY = _settings.max_stocks_to_display
else:
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
    ANIMATION_FRAME_DURATION = 800
    ANIMATION_TRANSITION_DURATION = 600
    BUBBLE_SIZE_MAX = 60
    BUBBLE_OPACITY = 0.7
    BUBBLE_BORDER_WIDTH = 1
    MAX_STOCKS_TO_DISPLAY = 200

# Logging settings
if _use_pydantic and _settings:
    LOG_LEVEL = _settings.log_level
    LOG_FILE = _settings.log_file
else:
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', None)

# Ensure directories exist
if _use_pydantic and _settings:
    _settings.ensure_directories()
else:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(STATIC_OUTPUT_DIR, exist_ok=True)
    os.makedirs(ANIMATED_OUTPUT_DIR, exist_ok=True)
    if LOG_FILE:
        os.makedirs(LOG_DIR, exist_ok=True)
