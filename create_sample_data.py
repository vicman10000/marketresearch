#!/usr/bin/env python3
"""
Create sample data for demonstration when APIs are unavailable
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

# Sample stocks
stocks = [
    ('AAPL', 'Apple Inc.', 'Information Technology'),
    ('MSFT', 'Microsoft Corporation', 'Information Technology'),
    ('GOOGL', 'Alphabet Inc.', 'Communication Services'),
    ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary'),
    ('NVDA', 'NVIDIA Corporation', 'Information Technology'),
    ('META', 'Meta Platforms Inc.', 'Communication Services'),
    ('TSLA', 'Tesla Inc.', 'Consumer Discretionary'),
    ('JPM', 'JPMorgan Chase', 'Financials'),
    ('JNJ', 'Johnson & Johnson', 'Health Care'),
    ('XOM', 'Exxon Mobil', 'Energy'),
]

# Generate dates (last 12 months)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Generate data for each stock
all_data = []

for symbol, name, sector in stocks:
    # Generate price data with random walk
    initial_price = np.random.uniform(100, 300)
    returns = np.random.normal(0.0005, 0.02, len(dates))  # Daily returns
    prices = initial_price * np.exp(np.cumsum(returns))

    # Generate volume
    base_volume = np.random.uniform(1e7, 5e7)
    volumes = base_volume * (1 + np.random.normal(0, 0.3, len(dates)))
    volumes = np.abs(volumes)

    # Market cap (billions)
    market_cap = initial_price * base_volume * np.random.uniform(10, 100)

    for i, date in enumerate(dates):
        all_data.append({
            'Date': date,
            'Symbol': symbol,
            'Security': name,
            'Sector': sector,
            'Open': prices[i] * np.random.uniform(0.98, 1.00),
            'High': prices[i] * np.random.uniform(1.00, 1.02),
            'Low': prices[i] * np.random.uniform(0.98, 1.00),
            'Close': prices[i],
            'Volume': int(volumes[i]),
            'Dividends': 0,
            'Stock Splits': 0,
            'Market_Cap': market_cap * (prices[i] / initial_price),  # Scale with price
            'Sub_Industry': 'Sample Industry'
        })

# Create DataFrame
df = pd.DataFrame(all_data)

# Save to cache directory
cache_dir = '/home/user/marketresearchvisualization/data/cache'
os.makedirs(cache_dir, exist_ok=True)

# Save individual stock files (mimicking yfinance cache)
for symbol in df['Symbol'].unique():
    stock_df = df[df['Symbol'] == symbol].copy()
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    cache_file = os.path.join(cache_dir, f'{symbol}_{start_str}_{end_str}.csv')
    stock_df.to_csv(cache_file, index=False)
    print(f"Created {cache_file}")

# Also save complete dataset
output_file = '/home/user/marketresearchvisualization/data/sample_complete_data.csv'
df.to_csv(output_file, index=False)
print(f"\nCreated complete dataset: {output_file}")
print(f"Total rows: {len(df)}")
print(f"Stocks: {df['Symbol'].nunique()}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Sectors: {df['Sector'].unique().tolist()}")
