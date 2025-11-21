"""
Pytest configuration and shared fixtures
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_stock_data():
    """
    Create sample stock data for testing
    
    Returns:
        DataFrame with sample stock data (OHLCV format)
    """
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    data = []
    for symbol in symbols:
        for i, date in enumerate(dates):
            # Generate realistic price data with some trend and noise
            base_price = 100 + (i * 0.1) + np.random.randn() * 2
            data.append({
                'Date': date,
                'Symbol': symbol,
                'Open': base_price,
                'High': base_price * 1.02,
                'Low': base_price * 0.98,
                'Close': base_price + np.random.randn(),
                'Volume': int(1000000 + np.random.randn() * 100000),
                'Security': f'{symbol} Inc.',
                'Sector': 'Information Technology',
                'Sub_Industry': 'Software'
            })
    
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


@pytest.fixture
def sample_processed_data(sample_stock_data):
    """
    Create sample processed data with calculated metrics
    
    Returns:
        DataFrame with processed data including returns and metrics
    """
    df = sample_stock_data.copy()
    
    # Add market cap
    df['Market_Cap'] = 1e12 + np.random.randn(len(df)) * 1e10
    
    # Add calculated metrics
    df['Daily_Return'] = df.groupby('Symbol')['Close'].pct_change()
    df['Cumulative_Return'] = df.groupby('Symbol')['Close'].apply(
        lambda x: (x / x.iloc[0] - 1) * 100
    ).reset_index(level=0, drop=True)
    df['YTD_Return'] = df['Cumulative_Return']  # Simplified for test
    df['MA_20'] = df.groupby('Symbol')['Close'].transform(
        lambda x: x.rolling(window=20, min_periods=1).mean()
    )
    df['Volatility_20'] = df.groupby('Symbol')['Daily_Return'].transform(
        lambda x: x.rolling(window=20, min_periods=1).std() * np.sqrt(252) * 100
    )
    df['Market_Cap_Billions'] = df['Market_Cap'] / 1e9
    
    return df


@pytest.fixture
def sample_sector_summary():
    """
    Create sample sector summary data
    
    Returns:
        DataFrame with sector-level statistics
    """
    data = {
        'Sector': ['Information Technology', 'Health Care', 'Financials'],
        'Stock_Count': [10, 8, 12],
        'Total_Market_Cap': [5e12, 3e12, 4e12],
        'Avg_YTD_Return': [15.5, 10.2, 8.7],
        'Avg_Volatility': [25.3, 18.9, 22.1],
        'Market_Cap_Billions': [5000, 3000, 4000]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_animation_data(sample_processed_data):
    """
    Create sample animation data
    
    Returns:
        DataFrame aggregated by month for animations
    """
    df = sample_processed_data.copy()
    df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')
    
    # Take last value per month per symbol
    agg_df = df.groupby(['Symbol', 'Year_Month']).last().reset_index()
    
    return agg_df


@pytest.fixture
def mock_config():
    """
    Create mock configuration for testing
    
    Returns:
        Dictionary with test configuration
    """
    return {
        'BASE_DIR': '/test/base',
        'DATA_DIR': '/test/data',
        'CACHE_DIR': '/test/cache',
        'OUTPUT_DIR': '/test/outputs',
        'DEFAULT_START_DATE': '2024-01-01',
        'DEFAULT_END_DATE': '2024-12-31',
        'CACHE_EXPIRY_HOURS': 24,
        'BUBBLE_SIZE_MAX': 60,
        'BUBBLE_OPACITY': 0.7,
        'MAX_STOCKS_TO_DISPLAY': 200
    }

