"""
CSV file-based storage implementation

Maintains backward compatibility with existing CSV cache structure.
"""
import os
import pandas as pd
from typing import Optional, List
from datetime import datetime, timedelta
import time
from .base import DataStore


class CSVDataStore(DataStore):
    """CSV file-based data storage (legacy compatible)"""
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize CSV data store
        
        Args:
            cache_dir: Directory for cache files
        """
        if cache_dir is None:
            try:
                import config
                cache_dir = config.CACHE_DIR
            except ImportError:
                cache_dir = './data/cache'
        
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def save_stock_prices(self, symbol: str, data: pd.DataFrame) -> bool:
        """Save stock price data to CSV"""
        try:
            # Determine date range from data
            if 'Date' in data.columns:
                start_date = data['Date'].min().strftime('%Y-%m-%d')
                end_date = data['Date'].max().strftime('%Y-%m-%d')
            else:
                start_date = 'unknown'
                end_date = 'unknown'
            
            filename = f"{symbol}_{start_date}_{end_date}.csv"
            filepath = os.path.join(self.cache_dir, filename)
            
            data.to_csv(filepath, index=False)
            return True
        except Exception:
            return False
    
    def load_stock_prices(self, symbol: str, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """Load stock price data from CSV"""
        # Find matching CSV files
        pattern = f"{symbol}_"
        matching_files = [f for f in os.listdir(self.cache_dir) if f.startswith(pattern)]
        
        if not matching_files:
            return pd.DataFrame()
        
        # Load the most recent file
        latest_file = max(matching_files, key=lambda f: os.path.getmtime(os.path.join(self.cache_dir, f)))
        filepath = os.path.join(self.cache_dir, latest_file)
        
        try:
            df = pd.read_csv(filepath, parse_dates=['Date'])
            
            # Apply date filters if provided
            if start_date:
                df = df[df['Date'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['Date'] <= pd.to_datetime(end_date)]
            
            return df
        except Exception:
            return pd.DataFrame()
    
    def save_stock_info(self, data: pd.DataFrame) -> bool:
        """Save stock information to CSV"""
        try:
            filepath = os.path.join(self.cache_dir, 'sp500_constituents.csv')
            data.to_csv(filepath, index=False)
            return True
        except Exception:
            return False
    
    def load_stock_info(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """Load stock information from CSV"""
        filepath = os.path.join(self.cache_dir, 'sp500_constituents.csv')
        
        if not os.path.exists(filepath):
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(filepath)
            
            if symbols:
                df = df[df['Symbol'].isin(symbols)]
            
            return df
        except Exception:
            return pd.DataFrame()
    
    def cache_exists(self, cache_key: str) -> bool:
        """Check if cache file exists"""
        filepath = os.path.join(self.cache_dir, f"{cache_key}.csv")
        return os.path.exists(filepath)
    
    def is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
        """Check if cache is valid based on age"""
        filepath = os.path.join(self.cache_dir, f"{cache_key}.csv")
        
        if not os.path.exists(filepath):
            return False
        
        cache_age = time.time() - os.path.getmtime(filepath)
        return cache_age < max_age_hours * 3600
    
    def clear_cache(self, cache_key: Optional[str] = None) -> bool:
        """Clear cache files"""
        try:
            if cache_key:
                # Clear specific cache
                filepath = os.path.join(self.cache_dir, f"{cache_key}.csv")
                if os.path.exists(filepath):
                    os.remove(filepath)
            else:
                # Clear all cache files
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.csv'):
                        os.remove(os.path.join(self.cache_dir, filename))
            return True
        except Exception:
            return False
    
    def get_available_symbols(self) -> List[str]:
        """Get list of symbols with cached data"""
        symbols = set()
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.csv') and filename != 'sp500_constituents.csv':
                # Extract symbol from filename (format: SYMBOL_date_date.csv)
                symbol = filename.split('_')[0]
                symbols.add(symbol)
        return sorted(list(symbols))
    
    def get_date_range(self, symbol: str) -> tuple[Optional[datetime], Optional[datetime]]:
        """Get date range for symbol's cached data"""
        try:
            df = self.load_stock_prices(symbol)
            if df.empty or 'Date' not in df.columns:
                return None, None
            return df['Date'].min(), df['Date'].max()
        except Exception:
            return None, None
