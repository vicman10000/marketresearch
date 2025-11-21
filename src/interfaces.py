"""
Protocol interfaces for major components

Defines type-safe interfaces using Python's Protocol feature for better
architecture and testability (duck typing with type checking).
"""
from typing import Protocol, Optional, List, runtime_checkable
import pandas as pd
from datetime import datetime


@runtime_checkable
class DataFetcherProtocol(Protocol):
    """Interface for data fetching components"""
    
    def fetch_sp500_constituents(self, use_cache: bool = True) -> pd.DataFrame:
        """Fetch S&P 500 constituent list"""
        ...
    
    def fetch_stock_data(self, symbols: List[str], start_date: Optional[str] = None,
                        end_date: Optional[str] = None, use_cache: bool = True) -> pd.DataFrame:
        """Fetch historical stock data"""
        ...
    
    def fetch_market_cap(self, symbols: List[str]) -> pd.DataFrame:
        """Fetch market capitalization data"""
        ...
    
    def fetch_complete_dataset(self, start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              max_stocks: Optional[int] = None,
                              use_cache: bool = True) -> pd.DataFrame:
        """Fetch complete dataset with all information"""
        ...


@runtime_checkable
class DataProcessorProtocol(Protocol):
    """Interface for data processing components"""
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data"""
        ...
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate return metrics"""
        ...
    
    def calculate_fundamentals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate fundamental metrics"""
        ...
    
    def aggregate_by_period(self, df: pd.DataFrame, period: str = 'M') -> pd.DataFrame:
        """Aggregate data by time period"""
        ...
    
    def prepare_animation_data(self, df: pd.DataFrame, period: str = 'M') -> pd.DataFrame:
        """Prepare data for animations"""
        ...
    
    def get_sector_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate sector-level summaries"""
        ...
    
    def process_complete_pipeline(self, raw_df: pd.DataFrame,
                                 animation_period: str = 'M') -> dict:
        """Run complete processing pipeline"""
        ...


@runtime_checkable
class VisualizerProtocol(Protocol):
    """Interface for visualization components"""
    
    def create_bubble_chart(self, df: pd.DataFrame, save_path: Optional[str] = None,
                           show: bool = True) -> object:
        """Create bubble chart visualization"""
        ...
    
    def create_sector_performance_chart(self, sector_summary: pd.DataFrame,
                                       save_path: Optional[str] = None,
                                       show: bool = True) -> object:
        """Create sector performance chart"""
        ...


@runtime_checkable
class DataStoreProtocol(Protocol):
    """Interface for data storage components"""
    
    def save_stock_prices(self, symbol: str, data: pd.DataFrame) -> bool:
        """Save stock price data"""
        ...
    
    def load_stock_prices(self, symbol: str, start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """Load stock price data"""
        ...
    
    def save_stock_info(self, data: pd.DataFrame) -> bool:
        """Save stock information"""
        ...
    
    def load_stock_info(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """Load stock information"""
        ...
    
    def cache_exists(self, cache_key: str) -> bool:
        """Check if cache exists"""
        ...
    
    def is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
        """Check if cache is valid"""
        ...


@runtime_checkable
class LoggerProtocol(Protocol):
    """Interface for logging components"""
    
    def info(self, event: str, **kwargs) -> None:
        """Log info level message"""
        ...
    
    def warning(self, event: str, **kwargs) -> None:
        """Log warning level message"""
        ...
    
    def error(self, event: str, **kwargs) -> None:
        """Log error level message"""
        ...
    
    def debug(self, event: str, **kwargs) -> None:
        """Log debug level message"""
        ...


@runtime_checkable
class MetricsCollectorProtocol(Protocol):
    """Interface for metrics collection"""
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[dict] = None) -> None:
        """Increment a counter metric"""
        ...
    
    def observe_histogram(self, name: str, value: float, labels: Optional[dict] = None) -> None:
        """Observe a histogram value"""
        ...
    
    def set_gauge(self, name: str, value: float, labels: Optional[dict] = None) -> None:
        """Set a gauge value"""
        ...
    
    def measure_time(self, name: str) -> object:
        """Context manager to measure execution time"""
        ...


@runtime_checkable
class HealthCheckProtocol(Protocol):
    """Interface for health check components"""
    
    def check_database(self) -> bool:
        """Check database connectivity"""
        ...
    
    def check_api(self) -> bool:
        """Check API availability"""
        ...
    
    def check_disk_space(self) -> bool:
        """Check available disk space"""
        ...
    
    def get_health_status(self) -> dict:
        """Get overall health status"""
        ...


# Type aliases for convenience
DataFetcher = DataFetcherProtocol
DataProcessor = DataProcessorProtocol
Visualizer = VisualizerProtocol
DataStore = DataStoreProtocol
Logger = LoggerProtocol
MetricsCollector = MetricsCollectorProtocol
HealthCheck = HealthCheckProtocol

