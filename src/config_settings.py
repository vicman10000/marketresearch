"""
Production-ready configuration using Pydantic Settings
Supports environment variables and .env files

Create a .env file in the project root with:
    LOG_LEVEL=INFO
    USE_SAMPLE_DATA=false
    ALPHA_VANTAGE_API_KEY=your_key_here
    etc.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Base directories (computed from BASE_DIR)
    base_dir: str = Field(default_factory=lambda: os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")
    log_file: Optional[str] = Field(default=None, description="Log file path (None for console only)")
    
    # Data fetching settings
    use_sample_data: bool = Field(default=False, description="Use sample data instead of live API")
    cache_expiry_hours: int = Field(default=24, description="Hours to keep cached data")
    default_start_date: str = Field(
        default_factory=lambda: (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
        description="Default start date for data fetching"
    )
    default_end_date: str = Field(
        default_factory=lambda: datetime.now().strftime('%Y-%m-%d'),
        description="Default end date for data fetching"
    )
    
    # API Keys
    alpha_vantage_api_key: str = Field(default="", description="Alpha Vantage API key")
    polygon_api_key: str = Field(default="", description="Polygon.io API key")
    
    # Database settings (Phase 3)
    use_database: bool = Field(default=False, description="Use database instead of CSV files")
    database_url: str = Field(
        default="sqlite:///./data/market_viz.db",
        description="Database connection URL"
    )
    
    # S&P 500 data source
    sp500_wikipedia_url: str = Field(
        default="https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        description="Wikipedia URL for S&P 500 constituents"
    )
    
    # Visualization settings
    max_stocks_to_display: int = Field(default=200, description="Maximum stocks to display")
    animation_frame_duration: int = Field(default=800, description="Animation frame duration (ms)")
    animation_transition_duration: int = Field(default=600, description="Animation transition duration (ms)")
    bubble_size_max: int = Field(default=60, description="Maximum bubble size")
    bubble_opacity: float = Field(default=0.7, description="Bubble opacity")
    bubble_border_width: int = Field(default=1, description="Bubble border width")
    
    # Monitoring settings (Phase 5)
    enable_metrics: bool = Field(default=False, description="Enable Prometheus metrics")
    sentry_dsn: str = Field(default="", description="Sentry DSN for error tracking")
    
    # Computed properties
    @property
    def data_dir(self) -> str:
        """Data directory path"""
        return os.path.join(self.base_dir, 'data')
    
    @property
    def cache_dir(self) -> str:
        """Cache directory path"""
        return os.path.join(self.data_dir, 'cache')
    
    @property
    def output_dir(self) -> str:
        """Output directory path"""
        return os.path.join(self.base_dir, 'outputs')
    
    @property
    def static_output_dir(self) -> str:
        """Static visualizations output directory"""
        return os.path.join(self.output_dir, 'static')
    
    @property
    def animated_output_dir(self) -> str:
        """Animated visualizations output directory"""
        return os.path.join(self.output_dir, 'animated')
    
    @property
    def log_dir(self) -> str:
        """Log directory path"""
        return os.path.join(self.base_dir, 'logs')
    
    @property
    def sector_colors(self) -> Dict[str, str]:
        """Sector color mapping"""
        return {
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
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.static_output_dir, exist_ok=True)
        os.makedirs(self.animated_output_dir, exist_ok=True)
        if self.log_file:
            os.makedirs(self.log_dir, exist_ok=True)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance (singleton pattern)
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_directories()
    return _settings


# Convenience function for backward compatibility
def load_settings() -> Settings:
    """Load and return settings"""
    return get_settings()

