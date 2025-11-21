"""
SQLite/PostgreSQL storage implementation using SQLAlchemy

Provides database-backed storage with better performance and queryability.
"""
import pandas as pd
from typing import Optional, List
from datetime import datetime, timedelta
from .base import DataStore
from ..database import get_database, Stock, StockPrice, StockMetric, CacheEntry


class SQLiteDataStore(DataStore):
    """Database-backed data storage using SQLAlchemy"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize SQLite data store
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.db = get_database(database_url)
    
    def save_stock_prices(self, symbol: str, data: pd.DataFrame) -> bool:
        """Save stock price data to database"""
        try:
            with self.db.get_session() as session:
                # Get or create stock
                stock = self.db.get_or_create_stock(
                    session,
                    symbol=symbol,
                    security=data['Security'].iloc[0] if 'Security' in data.columns else symbol,
                    sector=data['Sector'].iloc[0] if 'Sector' in data.columns else 'Unknown'
                )
                
                # Batch insert prices
                for _, row in data.iterrows():
                    price = StockPrice(
                        stock_id=stock.id,
                        date=row['Date'],
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        volume=row['Volume']
                    )
                    session.merge(price)  # Use merge to handle duplicates
                
                return True
        except Exception:
            return False
    
    def load_stock_prices(self, symbol: str, start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """Load stock price data from database"""
        try:
            with self.db.get_session() as session:
                stock = session.query(Stock).filter_by(symbol=symbol).first()
                
                if not stock:
                    return pd.DataFrame()
                
                query = session.query(StockPrice).filter_by(stock_id=stock.id)
                
                if start_date:
                    query = query.filter(StockPrice.date >= pd.to_datetime(start_date))
                if end_date:
                    query = query.filter(StockPrice.date <= pd.to_datetime(end_date))
                
                prices = query.all()
                
                if not prices:
                    return pd.DataFrame()
                
                data = [{
                    'Date': p.date,
                    'Open': p.open,
                    'High': p.high,
                    'Low': p.low,
                    'Close': p.close,
                    'Volume': p.volume,
                    'Symbol': symbol,
                    'Security': stock.security,
                    'Sector': stock.sector
                } for p in prices]
                
                return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()
    
    def save_stock_info(self, data: pd.DataFrame) -> bool:
        """Save stock information to database"""
        try:
            with self.db.get_session() as session:
                for _, row in data.iterrows():
                    self.db.get_or_create_stock(
                        session,
                        symbol=row['Symbol'],
                        security=row['Security'],
                        sector=row['Sector'],
                        sub_industry=row.get('Sub_Industry')
                    )
                return True
        except Exception:
            return False
    
    def load_stock_info(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """Load stock information from database"""
        try:
            with self.db.get_session() as session:
                query = session.query(Stock)
                
                if symbols:
                    query = query.filter(Stock.symbol.in_(symbols))
                
                stocks = query.all()
                
                data = [{
                    'Symbol': s.symbol,
                    'Security': s.security,
                    'Sector': s.sector,
                    'Sub_Industry': s.sub_industry
                } for s in stocks]
                
                return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()
    
    def cache_exists(self, cache_key: str) -> bool:
        """Check if cache entry exists"""
        try:
            with self.db.get_session() as session:
                entry = session.query(CacheEntry).filter_by(cache_key=cache_key).first()
                return entry is not None
        except Exception:
            return False
    
    def is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
        """Check if cache entry is valid"""
        try:
            with self.db.get_session() as session:
                entry = session.query(CacheEntry).filter_by(cache_key=cache_key).first()
                
                if not entry:
                    return False
                
                if entry.expires_at and entry.expires_at < datetime.utcnow():
                    return False
                
                age = datetime.utcnow() - entry.created_at
                return age < timedelta(hours=max_age_hours)
        except Exception:
            return False
    
    def clear_cache(self, cache_key: Optional[str] = None) -> bool:
        """Clear cache entries"""
        try:
            with self.db.get_session() as session:
                if cache_key:
                    session.query(CacheEntry).filter_by(cache_key=cache_key).delete()
                else:
                    session.query(CacheEntry).delete()
                return True
        except Exception:
            return False
    
    def get_available_symbols(self) -> List[str]:
        """Get list of all available stock symbols"""
        try:
            with self.db.get_session() as session:
                stocks = session.query(Stock.symbol).all()
                return [s[0] for s in stocks]
        except Exception:
            return []
    
    def get_date_range(self, symbol: str) -> tuple[Optional[datetime], Optional[datetime]]:
        """Get date range for symbol's data"""
        try:
            with self.db.get_session() as session:
                stock = session.query(Stock).filter_by(symbol=symbol).first()
                
                if not stock:
                    return None, None
                
                from sqlalchemy import func
                result = session.query(
                    func.min(StockPrice.date),
                    func.max(StockPrice.date)
                ).filter_by(stock_id=stock.id).first()
                
                return result if result else (None, None)
        except Exception:
            return None, None
