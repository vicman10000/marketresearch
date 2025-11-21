"""
Data Fetcher Module
Handles fetching S&P 500 constituent data and stock prices
"""
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import json
from tqdm import tqdm
import time
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class DataFetcher:
    """Fetches financial data for S&P 500 stocks"""

    def __init__(self, cache_dir=None):
        """
        Initialize DataFetcher

        Args:
            cache_dir: Directory to store cached data
        """
        self.cache_dir = cache_dir or config.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_sp500_constituents(self, use_cache=True):
        """
        Fetch S&P 500 constituent list from Wikipedia

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with columns: Symbol, Security, Sector, Sub-Sector, etc.
        """
        cache_file = os.path.join(self.cache_dir, 'sp500_constituents.csv')

        # Check cache
        if use_cache and os.path.exists(cache_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < config.CACHE_EXPIRY_HOURS * 3600:
                print(f"Loading S&P 500 constituents from cache...")
                return pd.read_csv(cache_file)

        print("Fetching S&P 500 constituents from Wikipedia...")
        try:
            # Fetch from Wikipedia with headers to avoid 403 error
            import urllib.request
            req = urllib.request.Request(
                config.SP500_WIKIPEDIA_URL,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                html_content = response.read()

            tables = pd.read_html(html_content)
            df = tables[0]

            # Rename columns for consistency
            df = df.rename(columns={
                'Symbol': 'Symbol',
                'Security': 'Security',
                'GICS Sector': 'Sector',
                'GICS Sub-Industry': 'Sub_Industry'
            })

            # Save to cache
            df.to_csv(cache_file, index=False)
            print(f"Fetched {len(df)} S&P 500 constituents")

            return df

        except Exception as e:
            print(f"Error fetching S&P 500 constituents: {e}")
            # Return empty dataframe with expected columns
            return pd.DataFrame(columns=['Symbol', 'Security', 'Sector', 'Sub_Industry'])

    def fetch_stock_data(self, symbols, start_date=None, end_date=None, use_cache=True):
        """
        Fetch historical stock data for given symbols

        Args:
            symbols: List of stock symbols
            start_date: Start date (YYYY-MM-DD) or datetime
            end_date: End date (YYYY-MM-DD) or datetime
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with multi-index (Date, Symbol) containing OHLCV data
        """
        if start_date is None:
            start_date = config.DEFAULT_START_DATE
        if end_date is None:
            end_date = config.DEFAULT_END_DATE

        print(f"\nFetching stock data for {len(symbols)} symbols from {start_date} to {end_date}...")

        all_data = []
        failed_symbols = []

        # Fetch data for each symbol with progress bar
        for symbol in tqdm(symbols, desc="Downloading stock data"):
            try:
                # Check cache
                cache_file = os.path.join(
                    self.cache_dir,
                    f'{symbol}_{start_date}_{end_date}.csv'
                )

                if use_cache and os.path.exists(cache_file):
                    cache_age = time.time() - os.path.getmtime(cache_file)
                    if cache_age < config.CACHE_EXPIRY_HOURS * 3600:
                        df = pd.read_csv(cache_file, parse_dates=['Date'])
                        df['Symbol'] = symbol
                        all_data.append(df)
                        continue

                # Fetch from yfinance
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)

                if df.empty:
                    failed_symbols.append(symbol)
                    continue

                # Reset index to get Date as a column
                df = df.reset_index()
                df['Symbol'] = symbol

                # Save to cache
                df.to_csv(cache_file, index=False)

                all_data.append(df)

                # Small delay to avoid rate limiting
                time.sleep(0.1)

            except Exception as e:
                print(f"\nError fetching data for {symbol}: {e}")
                failed_symbols.append(symbol)
                continue

        if failed_symbols:
            print(f"\nFailed to fetch data for {len(failed_symbols)} symbols: {failed_symbols[:10]}...")

        if not all_data:
            print("No data fetched!")
            return pd.DataFrame()

        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"\nSuccessfully fetched data for {len(all_data)} symbols")

        return combined_df

    def fetch_market_cap(self, symbols):
        """
        Fetch current market capitalization for symbols

        Args:
            symbols: List of stock symbols

        Returns:
            DataFrame with Symbol and Market_Cap columns
        """
        print(f"\nFetching market cap data for {len(symbols)} symbols...")

        market_caps = []

        for symbol in tqdm(symbols, desc="Fetching market caps"):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                market_cap = info.get('marketCap', None)

                if market_cap:
                    market_caps.append({
                        'Symbol': symbol,
                        'Market_Cap': market_cap
                    })

                time.sleep(0.1)

            except Exception as e:
                print(f"\nError fetching market cap for {symbol}: {e}")
                continue

        df = pd.DataFrame(market_caps)
        print(f"Successfully fetched market cap for {len(df)} symbols")

        return df

    def fetch_complete_dataset(self, start_date=None, end_date=None,
                              max_stocks=None, use_cache=True):
        """
        Fetch complete dataset: constituents + stock data + market caps

        Args:
            start_date: Start date for historical data
            end_date: End date for historical data
            max_stocks: Maximum number of stocks to fetch (for testing)
            use_cache: Whether to use cached data

        Returns:
            DataFrame with all data merged
        """
        # Fetch S&P 500 constituents
        constituents = self.fetch_sp500_constituents(use_cache=use_cache)

        if constituents.empty:
            print("Failed to fetch S&P 500 constituents!")
            return pd.DataFrame()

        # Limit stocks if specified
        if max_stocks:
            constituents = constituents.head(max_stocks)

        symbols = constituents['Symbol'].tolist()

        # Fetch stock data
        stock_data = self.fetch_stock_data(
            symbols,
            start_date=start_date,
            end_date=end_date,
            use_cache=use_cache
        )

        if stock_data.empty:
            print("Failed to fetch stock data!")
            return pd.DataFrame()

        # Fetch market caps
        market_caps = self.fetch_market_cap(symbols)

        # Merge all data
        print("\nMerging datasets...")

        # Drop columns from stock_data that will come from constituents (avoid _x/_y suffixes)
        cols_to_drop = ['Security', 'Sector', 'Sub_Industry']
        for col in cols_to_drop:
            if col in stock_data.columns:
                stock_data = stock_data.drop(columns=[col])

        # Merge constituents with stock data
        merged = stock_data.merge(
            constituents[['Symbol', 'Security', 'Sector', 'Sub_Industry']],
            on='Symbol',
            how='left'
        )

        # Merge with market caps
        if not market_caps.empty:
            merged = merged.merge(market_caps, on='Symbol', how='left')

        print(f"\nFinal dataset: {len(merged)} rows, {merged['Symbol'].nunique()} unique stocks")

        return merged


def main():
    """Example usage"""
    fetcher = DataFetcher()

    # Fetch data for last 6 months, limit to 20 stocks for testing
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    df = fetcher.fetch_complete_dataset(
        start_date=start_date,
        end_date=end_date,
        max_stocks=20,  # Limit for testing
        use_cache=True
    )

    print("\nDataset preview:")
    print(df.head())
    print("\nColumns:", df.columns.tolist())
    print("\nSectors:", df['Sector'].unique())

    # Save to CSV
    output_file = os.path.join(config.DATA_DIR, 'sample_data.csv')
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")


if __name__ == '__main__':
    main()
