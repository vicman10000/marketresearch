"""
Abstract base class for data storage

Defines the interface that all storage backends must implement.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
import pandas as pd
from datetime import datetime


class DataStore(ABC):
    """Abstract base class for data storage backends"""
    
    @abstractmethod
    def save_stock_prices(self, symbol: str, data: pd.DataFrame) -> bool:
        """
        Save stock price data
        
        Args:
            symbol: Stock ticker symbol
            data: DataFrame with OHLCV data
            
        Returns:
            Boolean indicating success
        """
        pass
    
    @abstractmethod
    def load_stock_prices(self, symbol: str, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Load stock price data
        
        Args:
            symbol: Stock ticker symbol
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            DataFrame with stock price data
        """
        pass
    
    @abstractmethod
    def save_stock_info(self, data: pd.DataFrame) -> bool:
        """
        Save stock information (symbol, name, sector, etc.)
        
        Args:
            data: DataFrame with stock information
            
        Returns:
            Boolean indicating success
        """
        pass
    
    @abstractmethod
    def load_stock_info(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load stock information
        
        Args:
            symbols: Optional list of symbols to filter
            
        Returns:
            DataFrame with stock information
        """
        pass
    
    @abstractmethod
    def cache_exists(self, cache_key: str) -> bool:
        """
        Check if cached data exists
        
        Args:
            cache_key: Unique cache identifier
            
        Returns:
            Boolean indicating if cache exists
        """
        pass
    
    @abstractmethod
    def is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
        """
        Check if cached data is still valid
        
        Args:
            cache_key: Unique cache identifier
            max_age_hours: Maximum age in hours
            
        Returns:
            Boolean indicating if cache is valid
        """
        pass
    
    @abstractmethod
    def clear_cache(self, cache_key: Optional[str] = None) -> bool:
        """
        Clear cached data
        
        Args:
            cache_key: Specific cache to clear (None = clear all)
            
        Returns:
            Boolean indicating success
        """
        pass
    
    @abstractmethod
    def get_available_symbols(self) -> List[str]:
        """
        Get list of all available stock symbols
        
        Returns:
            List of stock symbols
        """
        pass
    
    @abstractmethod
    def get_date_range(self, symbol: str) -> tuple[Optional[datetime], Optional[datetime]]:
        """
        Get date range for a symbol's data
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Tuple of (start_date, end_date) or (None, None) if no data
        """
        pass
