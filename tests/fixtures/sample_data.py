"""
Sample data generators for testing
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_sample_stock_prices(symbols=['AAPL', 'MSFT'], days=100, start_price=100):
    """
    Generate sample stock price data
    
    Args:
        symbols: List of stock symbols
        days: Number of trading days
        start_price: Starting price
        
    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=days),
        periods=days,
        freq='D'
    )
    
    data = []
    for symbol in symbols:
        price = start_price
        for date in dates:
            # Random walk with drift
            price = price * (1 + np.random.randn() * 0.02)
            
            data.append({
                'Date': date,
                'Symbol': symbol,
                'Open': price * (1 + np.random.randn() * 0.01),
                'High': price * 1.02,
                'Low': price * 0.98,
                'Close': price,
                'Volume': int(1e6 + np.random.randn() * 1e5)
            })
    
    return pd.DataFrame(data)


def create_sample_market_data(n_stocks=10, days=100):
    """
    Generate complete market dataset with sectors
    
    Args:
        n_stocks: Number of stocks to generate
        days: Number of trading days
        
    Returns:
        DataFrame with complete market data
    """
    sectors = [
        'Information Technology',
        'Health Care',
        'Financials',
        'Consumer Discretionary'
    ]
    
    symbols = [f'STOCK{i:03d}' for i in range(n_stocks)]
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=days),
        periods=days,
        freq='D'
    )
    
    data = []
    for symbol in symbols:
        sector = np.random.choice(sectors)
        price = 100 + np.random.randn() * 20
        
        for date in dates:
            price = price * (1 + np.random.randn() * 0.015)
            
            data.append({
                'Date': date,
                'Symbol': symbol,
                'Security': f'{symbol} Corporation',
                'Sector': sector,
                'Sub_Industry': f'{sector} Sub',
                'Open': price * (1 + np.random.randn() * 0.01),
                'High': price * 1.02,
                'Low': price * 0.98,
                'Close': price,
                'Volume': int(1e6 + np.random.randn() * 1e5),
                'Market_Cap': 1e12 + np.random.randn() * 1e11
            })
    
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def create_empty_dataframe():
    """
    Create empty DataFrame with expected columns
    
    Returns:
        Empty DataFrame with proper schema
    """
    return pd.DataFrame(columns=[
        'Date', 'Symbol', 'Security', 'Sector', 'Sub_Industry',
        'Open', 'High', 'Low', 'Close', 'Volume', 'Market_Cap'
    ])


def create_invalid_dataframe():
    """
    Create DataFrame with invalid/missing data
    
    Returns:
        DataFrame with data quality issues
    """
    return pd.DataFrame({
        'Date': ['2024-01-01', None, '2024-01-03'],
        'Symbol': ['AAPL', 'MSFT', None],
        'Close': [150.0, None, 200.0],
        'Volume': [1000000, 2000000, -1000]  # Negative volume
    })
