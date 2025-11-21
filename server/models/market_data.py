"""
Market Data Models
Database models for storing market data snapshots and history
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from server.database import Base


class StockSnapshot(Base):
    """Historical stock data snapshots"""
    __tablename__ = "stock_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    
    # Stock identification
    symbol = Column(String(10), nullable=False, index=True)
    security = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True, index=True)
    sub_industry = Column(String(100), nullable=True)
    
    # Date
    date = Column(Date, nullable=False, index=True)
    
    # Price data
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    
    # Calculated metrics
    ytd_return = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    
    # Additional data
    dividends = Column(Float, default=0.0)
    stock_splits = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_stock_snapshots_symbol_date', 'symbol', 'date'),
        Index('idx_stock_snapshots_sector_date', 'sector', 'date'),
    )
    
    def __repr__(self):
        return f"<StockSnapshot(symbol='{self.symbol}', date='{self.date}', close={self.close})>"


class SectorSnapshot(Base):
    """Aggregated sector performance snapshots"""
    __tablename__ = "sector_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    
    # Sector identification
    sector = Column(String(100), nullable=False, index=True)
    
    # Date
    date = Column(Date, nullable=False, index=True)
    
    # Aggregate metrics
    stock_count = Column(Integer, nullable=False)
    avg_return = Column(Float, nullable=True)
    avg_volatility = Column(Float, nullable=True)
    total_market_cap = Column(Float, nullable=True)
    median_return = Column(Float, nullable=True)
    
    # Top performers in sector
    top_performers = Column(JSON, default=list)  # List of top stock symbols
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_sector_snapshots_sector_date', 'sector', 'date'),
    )
    
    def __repr__(self):
        return f"<SectorSnapshot(sector='{self.sector}', date='{self.date}', stock_count={self.stock_count})>"

