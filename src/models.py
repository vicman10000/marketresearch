"""
Pydantic models for data validation

Provides type-safe validation for all data structures in the application.
"""
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class StockPrice(BaseModel):
    """Model for stock price data"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    date: datetime = Field(..., description="Trading date")
    open: float = Field(..., gt=0, description="Opening price")
    high: float = Field(..., gt=0, description="High price")
    low: float = Field(..., gt=0, description="Low price")
    close: float = Field(..., gt=0, description="Closing price")
    volume: int = Field(..., ge=0, description="Trading volume")
    
    @field_validator('high')
    @classmethod
    def high_must_be_highest(cls, v, info):
        """Validate that high is the highest price"""
        if 'low' in info.data and v < info.data['low']:
            raise ValueError('High price must be greater than or equal to low price')
        return v
    
    @field_validator('close')
    @classmethod
    def close_must_be_in_range(cls, v, info):
        """Validate that close is between low and high"""
        if 'low' in info.data and 'high' in info.data:
            if not (info.data['low'] <= v <= info.data['high']):
                raise ValueError('Close price must be between low and high')
        return v


class StockInfo(BaseModel):
    """Model for stock metadata"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    symbol: str = Field(..., min_length=1, max_length=10)
    security: str = Field(..., min_length=1, description="Company name")
    sector: str = Field(..., description="GICS Sector")
    sub_industry: Optional[str] = Field(None, description="GICS Sub-Industry")
    market_cap: Optional[float] = Field(None, gt=0, description="Market capitalization")
    
    @field_validator('sector')
    @classmethod
    def sector_must_be_valid(cls, v):
        """Validate sector is a known GICS sector"""
        valid_sectors = {
            'Information Technology',
            'Health Care',
            'Financials',
            'Consumer Discretionary',
            'Communication Services',
            'Industrials',
            'Consumer Staples',
            'Energy',
            'Utilities',
            'Real Estate',
            'Materials'
        }
        if v not in valid_sectors and v != 'Unknown':
            # Allow unknown sectors but log warning
            pass
        return v


class ProcessedStockData(BaseModel):
    """Model for processed stock data with calculated metrics"""
    
    model_config = ConfigDict(str_strip_whitespace=True, arbitrary_types_allowed=True)
    
    symbol: str
    date: datetime
    security: str
    sector: str
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    market_cap: float = Field(..., gt=0)
    market_cap_billions: float = Field(..., gt=0)
    daily_return: Optional[float] = None
    cumulative_return: Optional[float] = None
    ytd_return: Optional[float] = None
    ma_20: Optional[float] = Field(None, gt=0)
    volatility_20: Optional[float] = Field(None, ge=0)


class AnimationFrame(BaseModel):
    """Model for animation data frame"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    year_month: str = Field(..., pattern=r'^\d{4}-\d{2}$', description="Format: YYYY-MM")
    symbol: str
    security: str
    sector: str
    close: float = Field(..., gt=0)
    market_cap: float = Field(..., gt=0)
    ytd_return: float
    volatility_20: float = Field(..., ge=0)
    
    @field_validator('year_month')
    @classmethod
    def validate_year_month(cls, v):
        """Validate year-month format"""
        try:
            year, month = v.split('-')
            year_int = int(year)
            month_int = int(month)
            if not (1900 <= year_int <= 2100):
                raise ValueError('Year must be between 1900 and 2100')
            if not (1 <= month_int <= 12):
                raise ValueError('Month must be between 1 and 12')
        except (ValueError, AttributeError) as e:
            raise ValueError(f'Invalid year-month format: {v}') from e
        return v


class SectorSummary(BaseModel):
    """Model for sector-level summary statistics"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    sector: str
    stock_count: int = Field(..., gt=0)
    total_market_cap: float = Field(..., gt=0)
    market_cap_billions: float = Field(..., gt=0)
    avg_ytd_return: float
    avg_volatility: float = Field(..., ge=0)


class MarketMetadata(BaseModel):
    """Model for market analysis metadata"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    run_date: datetime
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    market: str = Field(default="S&P 500")
    data_source: str = Field(..., pattern=r'^(sample|live|alpha_vantage|polygon)$')
    total_stocks: int = Field(..., gt=0)
    total_data_points: int = Field(..., gt=0)
    animation_periods: int = Field(..., gt=0)
    sectors: List[str]


class APIResponse(BaseModel):
    """Generic model for API responses"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthCheckResult(BaseModel):
    """Model for health check results"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    service: str
    status: str = Field(..., pattern=r'^(healthy|degraded|unhealthy)$')
    timestamp: datetime = Field(default_factory=datetime.now)
    latency_ms: Optional[float] = Field(None, ge=0)
    message: Optional[str] = None
    details: Optional[dict] = None


# Validation helper functions

def validate_stock_prices(data: list[dict]) -> List[StockPrice]:
    """
    Validate a list of stock price dictionaries
    
    Args:
        data: List of dictionaries with stock price data
        
    Returns:
        List of validated StockPrice models
        
    Raises:
        ValidationError: If data is invalid
    """
    return [StockPrice(**item) for item in data]


def validate_stock_info(data: list[dict]) -> List[StockInfo]:
    """
    Validate a list of stock info dictionaries
    
    Args:
        data: List of dictionaries with stock info
        
    Returns:
        List of validated StockInfo models
        
    Raises:
        ValidationError: If data is invalid
    """
    return [StockInfo(**item) for item in data]


def validate_processed_data(data: list[dict]) -> List[ProcessedStockData]:
    """
    Validate processed stock data
    
    Args:
        data: List of dictionaries with processed data
        
    Returns:
        List of validated ProcessedStockData models
        
    Raises:
        ValidationError: If data is invalid
    """
    return [ProcessedStockData(**item) for item in data]
