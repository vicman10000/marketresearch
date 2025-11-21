"""
Analytics API Endpoints
Provides analytics, summaries, and custom queries for market data
"""
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
import structlog

# Add src to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import config

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# Response Models
class DashboardSummary(BaseModel):
    """Dashboard summary statistics"""
    total_stocks: int
    total_market_cap: float
    avg_ytd_return: float
    avg_volatility: float
    top_sector: str
    total_sectors: int
    last_updated: str
    date_range: Dict[str, str]


class TopPerformer(BaseModel):
    """Top performing stock"""
    rank: int
    symbol: str
    security: str
    sector: str
    ytd_return: float
    market_cap: Optional[float] = None


class SectorBreakdown(BaseModel):
    """Sector breakdown with counts and performance"""
    sector: str
    stock_count: int
    avg_return: float
    avg_volatility: float
    total_market_cap: float
    percentage_of_total: float


class CustomQueryRequest(BaseModel):
    """Request model for custom queries"""
    filters: Optional[Dict[str, Any]] = None
    aggregations: Optional[List[str]] = None
    sort_by: Optional[str] = None
    limit: Optional[int] = 100


# Helper functions
def load_processed_data() -> Optional[pd.DataFrame]:
    """Load processed data"""
    try:
        data_file = Path(config.DATA_DIR) / "processed_data.csv"
        if data_file.exists():
            df = pd.read_csv(data_file)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            return df
        return None
    except Exception as e:
        logger.error("error_loading_data", error=str(e))
        return None


# Endpoints
@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary():
    """
    Get comprehensive dashboard summary statistics
    """
    df = load_processed_data()
    
    if df is None or df.empty:
        raise HTTPException(
            status_code=404,
            detail="No data available. Please run data generation first."
        )
    
    # Get latest data for each stock
    latest_data = df.sort_values('Date').groupby('Symbol').last().reset_index()
    
    # Calculate summary statistics
    total_stocks = len(latest_data)
    total_market_cap = latest_data['Market_Cap'].sum() if 'Market_Cap' in latest_data.columns else 0
    avg_ytd_return = latest_data['YTD_Return'].mean() if 'YTD_Return' in latest_data.columns else 0
    avg_volatility = latest_data['Volatility'].mean() if 'Volatility' in latest_data.columns else 0
    
    # Get sector information
    sector_counts = latest_data['Sector'].value_counts()
    top_sector = sector_counts.index[0] if len(sector_counts) > 0 else "Unknown"
    total_sectors = len(sector_counts)
    
    # Get date range
    date_range = {
        "start": df['Date'].min().strftime('%Y-%m-%d') if pd.notna(df['Date'].min()) else "",
        "end": df['Date'].max().strftime('%Y-%m-%d') if pd.notna(df['Date'].max()) else ""
    }
    
    last_updated = df['Date'].max().strftime('%Y-%m-%d %H:%M:%S') if pd.notna(df['Date'].max()) else ""
    
    summary = DashboardSummary(
        total_stocks=total_stocks,
        total_market_cap=float(total_market_cap),
        avg_ytd_return=float(avg_ytd_return),
        avg_volatility=float(avg_volatility),
        top_sector=top_sector,
        total_sectors=total_sectors,
        last_updated=last_updated,
        date_range=date_range
    )
    
    logger.info("dashboard_summary_generated", total_stocks=total_stocks)
    return summary


@router.get("/top-performers", response_model=List[TopPerformer])
async def get_top_performers(
    count: int = Query(10, ge=1, le=100, description="Number of top performers to return"),
    metric: str = Query("ytd_return", description="Metric to sort by (ytd_return, market_cap, volatility)")
):
    """
    Get top performing stocks based on specified metric
    """
    df = load_processed_data()
    
    if df is None or df.empty:
        raise HTTPException(
            status_code=404,
            detail="No data available"
        )
    
    # Get latest data for each stock
    latest_data = df.sort_values('Date').groupby('Symbol').last().reset_index()
    
    # Determine sort column
    sort_col_map = {
        "ytd_return": "YTD_Return",
        "market_cap": "Market_Cap",
        "volatility": "Volatility"
    }
    
    sort_col = sort_col_map.get(metric, "YTD_Return")
    
    if sort_col not in latest_data.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Metric '{metric}' not available in data"
        )
    
    # Sort and get top performers
    top_stocks = latest_data.sort_values(sort_col, ascending=False).head(count)
    
    performers = []
    for rank, (_, row) in enumerate(top_stocks.iterrows(), 1):
        performers.append(TopPerformer(
            rank=rank,
            symbol=row.get('Symbol', ''),
            security=row.get('Security', ''),
            sector=row.get('Sector', ''),
            ytd_return=float(row.get('YTD_Return', 0.0)),
            market_cap=float(row.get('Market_Cap', 0.0)) if pd.notna(row.get('Market_Cap')) else None
        ))
    
    logger.info("top_performers_fetched", count=len(performers), metric=metric)
    return performers


@router.get("/sector-breakdown", response_model=List[SectorBreakdown])
async def get_sector_breakdown():
    """
    Get detailed breakdown of performance by sector
    """
    df = load_processed_data()
    
    if df is None or df.empty:
        raise HTTPException(
            status_code=404,
            detail="No data available"
        )
    
    # Get latest data for each stock
    latest_data = df.sort_values('Date').groupby('Symbol').last().reset_index()
    
    # Calculate total market cap for percentage
    total_market_cap = latest_data['Market_Cap'].sum() if 'Market_Cap' in latest_data.columns else 1
    
    # Group by sector
    sector_stats = latest_data.groupby('Sector').agg({
        'Symbol': 'count',
        'YTD_Return': 'mean',
        'Volatility': 'mean',
        'Market_Cap': 'sum'
    }).reset_index()
    
    sector_stats.columns = ['Sector', 'Stock_Count', 'Avg_Return', 'Avg_Volatility', 'Total_Market_Cap']
    
    # Calculate percentage
    sector_stats['Percentage'] = (sector_stats['Total_Market_Cap'] / total_market_cap * 100) if total_market_cap > 0 else 0
    
    # Sort by market cap
    sector_stats = sector_stats.sort_values('Total_Market_Cap', ascending=False)
    
    breakdown = []
    for _, row in sector_stats.iterrows():
        breakdown.append(SectorBreakdown(
            sector=row['Sector'],
            stock_count=int(row['Stock_Count']),
            avg_return=float(row['Avg_Return']),
            avg_volatility=float(row['Avg_Volatility']),
            total_market_cap=float(row['Total_Market_Cap']),
            percentage_of_total=float(row['Percentage'])
        ))
    
    logger.info("sector_breakdown_generated", sectors=len(breakdown))
    return breakdown


@router.post("/custom-query")
async def custom_query(query_request: CustomQueryRequest):
    """
    Execute a custom query with filters and aggregations
    
    Example request:
    {
        "filters": {"Sector": "Information Technology", "YTD_Return": {">": 50}},
        "aggregations": ["mean", "median"],
        "sort_by": "Market_Cap",
        "limit": 20
    }
    """
    df = load_processed_data()
    
    if df is None or df.empty:
        raise HTTPException(
            status_code=404,
            detail="No data available"
        )
    
    # Get latest data for each stock
    result_df = df.sort_values('Date').groupby('Symbol').last().reset_index()
    
    # Apply filters
    if query_request.filters:
        for column, value in query_request.filters.items():
            if column not in result_df.columns:
                continue
            
            if isinstance(value, dict):
                # Handle comparison operators
                for op, threshold in value.items():
                    if op == ">":
                        result_df = result_df[result_df[column] > threshold]
                    elif op == "<":
                        result_df = result_df[result_df[column] < threshold]
                    elif op == ">=":
                        result_df = result_df[result_df[column] >= threshold]
                    elif op == "<=":
                        result_df = result_df[result_df[column] <= threshold]
                    elif op == "==":
                        result_df = result_df[result_df[column] == threshold]
            else:
                # Direct equality filter
                result_df = result_df[result_df[column] == value]
    
    # Apply sorting
    if query_request.sort_by and query_request.sort_by in result_df.columns:
        result_df = result_df.sort_values(query_request.sort_by, ascending=False)
    
    # Apply limit
    if query_request.limit:
        result_df = result_df.head(query_request.limit)
    
    # Apply aggregations if requested
    result = {}
    if query_request.aggregations:
        numeric_cols = result_df.select_dtypes(include=['number']).columns
        for agg in query_request.aggregations:
            if hasattr(result_df[numeric_cols], agg):
                result[agg] = result_df[numeric_cols].agg(agg).to_dict()
    
    # Add filtered data
    result['data'] = result_df.to_dict('records')
    result['count'] = len(result_df)
    
    logger.info("custom_query_executed", 
               filters=query_request.filters,
               result_count=len(result_df))
    
    return result


@router.get("/visualizations/list")
async def list_visualizations():
    """
    List all available visualizations
    """
    outputs_dir = Path(config.OUTPUT_DIR)
    
    visualizations = {
        "static": [],
        "animated": [],
        "main_dashboard": None
    }
    
    # Check for main dashboard
    index_path = outputs_dir / "index.html"
    if index_path.exists():
        visualizations["main_dashboard"] = "/index.html"
    
    # List static visualizations
    static_dir = outputs_dir / "static"
    if static_dir.exists():
        for file in static_dir.glob("*.html"):
            visualizations["static"].append({
                "name": file.stem.replace('_', ' ').title(),
                "filename": file.name,
                "url": f"/static/{file.name}",
                "size": file.stat().st_size,
                "modified": file.stat().st_mtime
            })
    
    # List animated visualizations
    animated_dir = outputs_dir / "animated"
    if animated_dir.exists():
        for file in animated_dir.glob("*.html"):
            visualizations["animated"].append({
                "name": file.stem.replace('_', ' ').title(),
                "filename": file.name,
                "url": f"/animated/{file.name}",
                "size": file.stat().st_size,
                "modified": file.stat().st_mtime
            })
    
    logger.info("visualizations_listed",
               static_count=len(visualizations["static"]),
               animated_count=len(visualizations["animated"]))
    
    return visualizations

