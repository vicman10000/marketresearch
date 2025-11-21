"""
Market Data API Endpoints
Provides access to stock data, sectors, and data refresh operations
"""
import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
import pandas as pd
import structlog

# Add src to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor
import config

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["Market Data"])


# Response Models
class StockSummary(BaseModel):
    """Summary information for a stock"""
    symbol: str
    security: str
    sector: str
    current_price: Optional[float] = None
    ytd_return: Optional[float] = None
    volatility: Optional[float] = None
    market_cap: Optional[float] = None


class StockDetail(BaseModel):
    """Detailed stock information"""
    symbol: str
    security: str
    sector: str
    sub_industry: Optional[str] = None
    current_price: Optional[float] = None
    ytd_return: Optional[float] = None
    volatility: Optional[float] = None
    market_cap: Optional[float] = None
    price_history: Optional[List[dict]] = None
    last_updated: Optional[str] = None


class SectorPerformance(BaseModel):
    """Sector performance summary"""
    sector: str
    stock_count: int
    avg_return: float
    avg_volatility: float
    total_market_cap: float


class DataRefreshResponse(BaseModel):
    """Response for data refresh operation"""
    status: str
    message: str
    started_at: str
    estimated_completion: Optional[str] = None


# Helper function to load processed data
def load_processed_data() -> Optional[pd.DataFrame]:
    """Load processed data from CSV or database"""
    try:
        data_file = Path(config.DATA_DIR) / "processed_data.csv"
        if data_file.exists():
            df = pd.read_csv(data_file)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            return df
        return None
    except Exception as e:
        logger.error("error_loading_processed_data", error=str(e))
        return None


def load_sector_summary() -> Optional[pd.DataFrame]:
    """Load sector summary data"""
    try:
        sector_file = Path(config.DATA_DIR) / "sector_summary.csv"
        if sector_file.exists():
            return pd.read_csv(sector_file)
        return None
    except Exception as e:
        logger.error("error_loading_sector_summary", error=str(e))
        return None


# Endpoints
@router.get("", response_model=List[StockSummary])
async def list_stocks(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of stocks to return"),
    skip: int = Query(0, ge=0, description="Number of stocks to skip")
):
    """
    Get list of all stocks with summary information
    """
    df = load_processed_data()
    
    if df is None:
        raise HTTPException(
            status_code=404, 
            detail="No data available. Please run data generation first."
        )
    
    # Get latest data for each stock
    latest_data = df.sort_values('Date').groupby('Symbol').last().reset_index()
    
    # Filter by sector if specified
    if sector:
        latest_data = latest_data[latest_data['Sector'] == sector]
    
    # Apply pagination
    latest_data = latest_data.iloc[skip:skip+limit]
    
    # Convert to response model
    stocks = []
    for _, row in latest_data.iterrows():
        stocks.append(StockSummary(
            symbol=row.get('Symbol', ''),
            security=row.get('Security', ''),
            sector=row.get('Sector', ''),
            current_price=row.get('Close', None),
            ytd_return=row.get('YTD_Return', None),
            volatility=row.get('Volatility', None),
            market_cap=row.get('Market_Cap', None)
        ))
    
    logger.info("stocks_listed", count=len(stocks), sector=sector)
    return stocks


@router.get("/{symbol}", response_model=StockDetail)
async def get_stock_detail(symbol: str):
    """
    Get detailed information for a specific stock
    """
    symbol = symbol.upper()
    df = load_processed_data()
    
    if df is None:
        raise HTTPException(
            status_code=404,
            detail="No data available"
        )
    
    # Filter data for this symbol
    stock_data = df[df['Symbol'] == symbol]
    
    if stock_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found"
        )
    
    # Get latest data
    latest = stock_data.sort_values('Date').iloc[-1]
    
    # Get price history (last 30 days)
    recent_data = stock_data.sort_values('Date').tail(30)
    price_history = [
        {
            "date": row['Date'].strftime('%Y-%m-%d') if pd.notna(row.get('Date')) else None,
            "close": row.get('Close', None),
            "volume": row.get('Volume', None)
        }
        for _, row in recent_data.iterrows()
    ]
    
    detail = StockDetail(
        symbol=latest.get('Symbol', symbol),
        security=latest.get('Security', ''),
        sector=latest.get('Sector', ''),
        sub_industry=latest.get('Sub_Industry', None),
        current_price=latest.get('Close', None),
        ytd_return=latest.get('YTD_Return', None),
        volatility=latest.get('Volatility', None),
        market_cap=latest.get('Market_Cap', None),
        price_history=price_history,
        last_updated=latest.get('Date').strftime('%Y-%m-%d %H:%M:%S') if pd.notna(latest.get('Date')) else None
    )
    
    logger.info("stock_detail_fetched", symbol=symbol)
    return detail


@router.get("/sectors/list", response_model=List[SectorPerformance])
async def get_sectors():
    """
    Get performance summary for all sectors
    """
    df = load_sector_summary()
    
    if df is None:
        # Try to calculate from processed data
        processed_df = load_processed_data()
        if processed_df is None:
            raise HTTPException(
                status_code=404,
                detail="No sector data available"
            )
        
        # Calculate sector summary
        latest_data = processed_df.sort_values('Date').groupby('Symbol').last().reset_index()
        df = latest_data.groupby('Sector').agg({
            'Symbol': 'count',
            'YTD_Return': 'mean',
            'Volatility': 'mean',
            'Market_Cap': 'sum'
        }).reset_index()
        df.columns = ['Sector', 'Stock_Count', 'Avg_Return', 'Avg_Volatility', 'Total_Market_Cap']
    
    sectors = []
    for _, row in df.iterrows():
        sectors.append(SectorPerformance(
            sector=row.get('Sector', ''),
            stock_count=int(row.get('Stock_Count', 0)),
            avg_return=float(row.get('Avg_Return', 0.0)),
            avg_volatility=float(row.get('Avg_Volatility', 0.0)),
            total_market_cap=float(row.get('Total_Market_Cap', 0.0))
        ))
    
    logger.info("sectors_listed", count=len(sectors))
    return sectors


async def refresh_data_background(max_stocks: Optional[int] = None):
    """Background task to refresh market data"""
    try:
        logger.info("data_refresh_started", max_stocks=max_stocks)
        
        # Initialize data fetcher
        fetcher = DataFetcher()
        processor = DataProcessor()
        
        # Fetch data
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        raw_data = fetcher.fetch_complete_dataset(
            start_date=start_date,
            end_date=end_date,
            max_stocks=max_stocks
        )
        
        if raw_data.empty:
            logger.error("data_refresh_failed", reason="no_data_fetched")
            return
        
        # Process data
        processed_data, sector_summary, _ = processor.process_complete_dataset(
            raw_data,
            animation_period='M'
        )
        
        # Save to files
        processed_data.to_csv(Path(config.DATA_DIR) / "processed_data.csv", index=False)
        sector_summary.to_csv(Path(config.DATA_DIR) / "sector_summary.csv", index=False)
        
        logger.info("data_refresh_completed", 
                   rows=len(processed_data),
                   stocks=processed_data['Symbol'].nunique())
        
    except Exception as e:
        logger.error("data_refresh_error", error=str(e), exc_info=True)


@router.post("/refresh", response_model=DataRefreshResponse)
async def refresh_data(
    background_tasks: BackgroundTasks,
    max_stocks: Optional[int] = Query(None, description="Maximum number of stocks to refresh")
):
    """
    Trigger a data refresh operation
    This runs in the background and doesn't block the response
    """
    start_time = datetime.now()
    
    # Add background task
    background_tasks.add_task(refresh_data_background, max_stocks)
    
    # Estimate completion time (rough estimate)
    estimated_minutes = 5 if max_stocks and max_stocks < 50 else 15
    estimated_completion = start_time + timedelta(minutes=estimated_minutes)
    
    logger.info("data_refresh_triggered", max_stocks=max_stocks)
    
    return DataRefreshResponse(
        status="started",
        message=f"Data refresh started for {max_stocks or 'all'} stocks",
        started_at=start_time.isoformat(),
        estimated_completion=estimated_completion.isoformat()
    )

