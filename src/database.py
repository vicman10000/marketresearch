"""
Database configuration and models using SQLAlchemy

Provides ORM models and database session management for SQLite/PostgreSQL.
"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Index,
    UniqueConstraint,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

Base = declarative_base()


# Database Models

class Stock(Base):
    """Stock information table"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    security = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=False, index=True)
    sub_industry = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    metrics = relationship("StockMetric", back_populates="stock", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_stock_sector', 'sector'),
    )


class StockPrice(Base):
    """Stock price data table"""
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="prices")
    
    __table_args__ = (
        UniqueConstraint('stock_id', 'date', name='uix_stock_date'),
        Index('idx_price_date', 'date'),
        Index('idx_price_stock_date', 'stock_id', 'date'),
    )


class StockMetric(Base):
    """Calculated stock metrics table"""
    __tablename__ = 'stock_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    market_cap = Column(Float)
    market_cap_billions = Column(Float)
    daily_return = Column(Float)
    cumulative_return = Column(Float)
    ytd_return = Column(Float)
    ma_20 = Column(Float)
    volatility_20 = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="metrics")
    
    __table_args__ = (
        UniqueConstraint('stock_id', 'date', name='uix_metric_stock_date'),
        Index('idx_metric_date', 'date'),
        Index('idx_metric_stock_date', 'stock_id', 'date'),
    )


class CacheEntry(Base):
    """Cache metadata table"""
    __tablename__ = 'cache_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    cache_type = Column(String(50), nullable=False)  # 'stock_data', 'constituents', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    metadata = Column(String(1000))  # JSON string
    
    __table_args__ = (
        Index('idx_cache_type', 'cache_type'),
        Index('idx_cache_expires', 'expires_at'),
    )


# Database Engine Management

class Database:
    """Database connection and session manager"""
    
    def __init__(self, database_url: str = "sqlite:///./data/market_viz.db", echo: bool = False):
        """
        Initialize database connection
        
        Args:
            database_url: SQLAlchemy database URL
            echo: Whether to echo SQL statements (for debugging)
        """
        # Special handling for SQLite in-memory databases
        if database_url == "sqlite:///:memory:":
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=echo
            )
        else:
            self.engine = create_engine(database_url, echo=echo)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session with automatic cleanup
        
        Yields:
            SQLAlchemy Session object
            
        Example:
            with db.get_session() as session:
                stock = session.query(Stock).filter_by(symbol='AAPL').first()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_or_create_stock(self, session: Session, symbol: str, security: str, sector: str, sub_industry: str = None) -> Stock:
        """
        Get existing stock or create new one
        
        Args:
            session: Database session
            symbol: Stock ticker symbol
            security: Company name
            sector: GICS sector
            sub_industry: GICS sub-industry
            
        Returns:
            Stock object
        """
        stock = session.query(Stock).filter_by(symbol=symbol).first()
        
        if not stock:
            stock = Stock(
                symbol=symbol,
                security=security,
                sector=sector,
                sub_industry=sub_industry
            )
            session.add(stock)
            session.flush()  # Get the ID without committing
        
        return stock


# Global database instance
_db_instance: Optional[Database] = None


def get_database(database_url: str = None, echo: bool = False) -> Database:
    """
    Get or create the global database instance (singleton)
    
    Args:
        database_url: SQLAlchemy database URL (only used on first call)
        echo: Whether to echo SQL (only used on first call)
        
    Returns:
        Database instance
    """
    global _db_instance
    
    if _db_instance is None:
        if database_url is None:
            # Use default from config
            try:
                from src.config_settings import get_settings
                settings = get_settings()
                database_url = settings.database_url
            except ImportError:
                database_url = "sqlite:///./data/market_viz.db"
        
        _db_instance = Database(database_url, echo)
        _db_instance.create_tables()
    
    return _db_instance


def reset_database():
    """Reset the global database instance (for testing)"""
    global _db_instance
    if _db_instance:
        _db_instance.drop_tables()
    _db_instance = None
