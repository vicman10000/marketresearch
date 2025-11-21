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
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from logging_config import get_logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from exceptions import (
    APIError,
    NetworkError,
    DataNotFoundError,
    wrap_api_error,
    is_retryable_error
)

# Initialize logger
logger = get_logger(__name__)
from src.logging_config import get_logger
from src.resilience import retry_on_network_error, retry_on_api_error


class DataFetcher:
    """Fetches financial data for S&P 500 stocks"""

    def __init__(self, cache_dir=None):
        """
        Initialize DataFetcher

        Args:
            cache_dir: Directory to store cached data
        """
        self.logger = get_logger(__name__)
        self.cache_dir = cache_dir or config.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        self.logger.debug("data_fetcher_initialized", cache_dir=self.cache_dir)

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
                self.logger.info("loading_sp500_from_cache", cache_file=cache_file)
                return pd.read_csv(cache_file)

        self.logger.info("fetching_sp500_from_wikipedia")
        return self._fetch_sp500_with_retry(cache_file)
    
    @retry_on_network_error(max_attempts=3)
    def _fetch_sp500_with_retry(self, cache_file):
        """Internal method with retry logic for fetching S&P 500 data"""
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
            self.logger.info("fetched_sp500_constituents", total_stocks=len(df))

            return df

        except Exception as e:
            self.logger.error("error_fetching_sp500_constituents", error=str(e), exc_info=True)
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

        self.logger.info("fetching_stock_data_started",
                        total_symbols=len(symbols),
                        start_date=start_date,
                        end_date=end_date)

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

                # Fetch from yfinance with retry
                df = self._fetch_single_stock_with_retry(symbol, start_date, end_date)

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
                self.logger.warning("error_fetching_symbol_data", 
                                   symbol=symbol, 
                                   error=str(e))
                failed_symbols.append(symbol)
                continue

        if failed_symbols:
            self.logger.warning("failed_to_fetch_symbols",
                               failed_count=len(failed_symbols),
                               failed_symbols=failed_symbols[:10])

        if not all_data:
            self.logger.error("no_data_fetched")
            return pd.DataFrame()

        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        self.logger.info("fetching_stock_data_completed",
                        successful_symbols=len(all_data),
                        total_rows=len(combined_df))

        return combined_df
    
    @retry_on_api_error(max_attempts=3, min_wait=1, max_wait=10)
    def _fetch_single_stock_with_retry(self, symbol, start_date, end_date):
        """Fetch single stock data with retry logic"""
        ticker = yf.Ticker(symbol)
        return ticker.history(start=start_date, end=end_date)

    def fetch_market_cap(self, symbols):
        """
        Fetch current market capitalization for symbols

        Args:
            symbols: List of stock symbols

        Returns:
            DataFrame with Symbol and Market_Cap columns
        """
        self.logger.info("fetching_market_caps_started", total_symbols=len(symbols))

        market_caps = []

        for symbol in tqdm(symbols, desc="Fetching market caps"):
            try:
                market_cap = self._fetch_single_market_cap_with_retry(symbol)

                if market_cap:
                    market_caps.append({
                        'Symbol': symbol,
                        'Market_Cap': market_cap
                    })

                time.sleep(0.1)

            except Exception as e:
                self.logger.warning("error_fetching_market_cap",
                                   symbol=symbol,
                                   error=str(e))
                continue

        df = pd.DataFrame(market_caps)
        self.logger.info("fetching_market_caps_completed", successful_count=len(df))

        return df
    
    @retry_on_api_error(max_attempts=3, min_wait=1, max_wait=10)
    def _fetch_single_market_cap_with_retry(self, symbol):
        """Fetch single market cap with retry logic"""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('marketCap', None)

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
        # Check if we should use sample data
        use_sample_data = os.environ.get('USE_SAMPLE_DATA', 'false').lower() == 'true'
        
        if use_sample_data:
            sample_file = os.path.join(os.path.dirname(self.cache_dir), 'sample_complete_data.csv')
            if os.path.exists(sample_file):
                self.logger.info("loading_sample_data", sample_file=sample_file)
                df = pd.read_csv(sample_file)
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Limit stocks if specified
                if max_stocks:
                    symbols = df['Symbol'].unique()[:max_stocks]
                    df = df[df['Symbol'].isin(symbols)]
                
                self.logger.info("loaded_sample_data", 
                                total_rows=len(df),
                                unique_stocks=df['Symbol'].nunique())
                return df
            else:
                self.logger.warning("sample_data_not_found",
                                   sample_file=sample_file,
                                   action="falling_back_to_live_data")
        
        # Fetch S&P 500 constituents
        constituents = self.fetch_sp500_constituents(use_cache=use_cache)

        if constituents.empty:
            self.logger.error("failed_to_fetch_sp500_constituents")
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
            self.logger.error("failed_to_fetch_stock_data")
            return pd.DataFrame()

        # Fetch market caps
        market_caps = self.fetch_market_cap(symbols)

        # Merge all data
        self.logger.info("merging_datasets")

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

        self.logger.info("fetch_complete_dataset_finished",
                        total_rows=len(merged),
                        unique_stocks=merged['Symbol'].nunique())

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
