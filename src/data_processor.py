"""
Data Processor Module
Handles data cleaning, transformation, and metric calculation
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class DataProcessor:
    """Processes and calculates metrics for financial data"""

    def __init__(self):
        """Initialize DataProcessor"""
        pass

    def clean_data(self, df):
        """
        Clean and prepare data for analysis

        Args:
            df: Raw DataFrame from DataFetcher

        Returns:
            Cleaned DataFrame
        """
        print("Cleaning data...")

        # Create a copy
        df = df.copy()

        # Convert Date to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])

        # Remove rows with missing critical data
        initial_rows = len(df)
        df = df.dropna(subset=['Close', 'Symbol', 'Date'])
        print(f"Removed {initial_rows - len(df)} rows with missing critical data")

        # Fill missing Sector with 'Unknown'
        if 'Sector' in df.columns:
            df['Sector'] = df['Sector'].fillna('Unknown')

        # Remove duplicate Date-Symbol combinations (keep last)
        df = df.drop_duplicates(subset=['Date', 'Symbol'], keep='last')

        # Sort by Symbol and Date
        df = df.sort_values(['Symbol', 'Date'])

        print(f"Cleaned data: {len(df)} rows")

        return df

    def calculate_returns(self, df):
        """
        Calculate various return metrics

        Args:
            df: DataFrame with Date, Symbol, Close columns

        Returns:
            DataFrame with additional return columns
        """
        print("Calculating returns...")

        df = df.copy()

        # Sort by Symbol and Date
        df = df.sort_values(['Symbol', 'Date'])

        # Calculate daily returns
        df['Daily_Return'] = df.groupby('Symbol')['Close'].pct_change()

        # Calculate returns from first date for each symbol
        df['Cumulative_Return'] = df.groupby('Symbol')['Close'].apply(
            lambda x: (x / x.iloc[0] - 1) * 100 if len(x) > 0 else 0
        ).reset_index(level=0, drop=True)

        # Calculate YTD return (from start of current year)
        current_year = datetime.now().year
        year_start = pd.to_datetime(f'{current_year}-01-01')

        def calculate_ytd_return(group):
            group = group.sort_values('Date')
            # Find first price of the year or first available price
            year_data = group[group['Date'] >= year_start]
            if len(year_data) > 0:
                first_price = year_data.iloc[0]['Close']
                group['YTD_Return'] = (group['Close'] / first_price - 1) * 100
            else:
                # Use cumulative return if no data from this year
                group['YTD_Return'] = group['Cumulative_Return']
            return group

        df = df.groupby('Symbol', group_keys=False).apply(calculate_ytd_return)

        # Calculate rolling metrics
        df['MA_20'] = df.groupby('Symbol')['Close'].transform(
            lambda x: x.rolling(window=20, min_periods=1).mean()
        )

        df['Volatility_20'] = df.groupby('Symbol')['Daily_Return'].transform(
            lambda x: x.rolling(window=20, min_periods=1).std() * np.sqrt(252) * 100
        )

        print("Returns calculated")

        return df

    def calculate_fundamentals(self, df):
        """
        Calculate or prepare fundamental metrics

        Args:
            df: DataFrame with stock data

        Returns:
            DataFrame with fundamental metrics
        """
        print("Processing fundamental metrics...")

        df = df.copy()

        # If Market_Cap is missing, estimate from Volume and Close
        if 'Market_Cap' not in df.columns or df['Market_Cap'].isna().all():
            print("Market cap data not available, using proxy based on volume")
            # Use volume * close as a proxy (not accurate but for visualization)
            df['Market_Cap'] = df['Volume'] * df['Close']

        # Handle missing or zero market caps
        df['Market_Cap'] = df['Market_Cap'].fillna(df['Market_Cap'].median())
        df.loc[df['Market_Cap'] <= 0, 'Market_Cap'] = df['Market_Cap'].median()

        # Calculate market cap in billions for display
        df['Market_Cap_Billions'] = df['Market_Cap'] / 1e9

        print("Fundamental metrics processed")

        return df

    def aggregate_by_period(self, df, period='M'):
        """
        Aggregate data by time period

        Args:
            df: DataFrame with Date column
            period: Pandas period string ('D', 'W', 'M', 'Q', 'Y')

        Returns:
            Aggregated DataFrame
        """
        print(f"Aggregating data by period: {period}")

        df = df.copy()

        # Create period column
        df['Period'] = df['Date'].dt.to_period(period)

        # Group by Symbol and Period, take last value
        agg_df = df.groupby(['Symbol', 'Period']).agg({
            'Date': 'last',
            'Close': 'last',
            'Volume': 'sum',
            'Security': 'first',
            'Sector': 'first',
            'Market_Cap': 'last',
            'Market_Cap_Billions': 'last',
            'Cumulative_Return': 'last',
            'YTD_Return': 'last',
            'Volatility_20': 'last'
        }).reset_index()

        # Convert Period back to timestamp
        agg_df['Date'] = agg_df['Period'].dt.to_timestamp()
        agg_df = agg_df.drop('Period', axis=1)

        print(f"Aggregated to {len(agg_df)} rows")

        return agg_df

    def prepare_animation_data(self, df, period='M'):
        """
        Prepare data specifically for animation

        Args:
            df: Processed DataFrame
            period: Aggregation period ('D', 'W', 'M')

        Returns:
            DataFrame ready for animated visualization
        """
        print("Preparing data for animation...")

        # Aggregate by period
        anim_df = self.aggregate_by_period(df, period=period)

        # Ensure we have all required columns
        required_cols = ['Date', 'Symbol', 'Security', 'Sector',
                        'Close', 'Market_Cap', 'YTD_Return']

        missing_cols = [col for col in required_cols if col not in anim_df.columns]
        if missing_cols:
            print(f"Warning: Missing columns: {missing_cols}")

        # Remove any remaining NaN values in critical columns
        anim_df = anim_df.dropna(subset=['YTD_Return', 'Market_Cap', 'Close'])

        # Create year-month label for animation frames
        anim_df['Year_Month'] = anim_df['Date'].dt.strftime('%Y-%m')

        # Sort by date
        anim_df = anim_df.sort_values('Date')

        print(f"Animation data ready: {len(anim_df)} rows across {anim_df['Year_Month'].nunique()} time periods")

        return anim_df

    def get_sector_summary(self, df):
        """
        Calculate sector-level summary statistics

        Args:
            df: Processed DataFrame

        Returns:
            DataFrame with sector summaries
        """
        if 'Sector' not in df.columns:
            print("No sector information available")
            return pd.DataFrame()

        # Get latest date data only
        latest_date = df['Date'].max()
        latest_df = df[df['Date'] == latest_date].copy()

        sector_summary = latest_df.groupby('Sector').agg({
            'Symbol': 'count',
            'Market_Cap': 'sum',
            'YTD_Return': 'mean',
            'Volatility_20': 'mean'
        }).reset_index()

        sector_summary.columns = ['Sector', 'Stock_Count', 'Total_Market_Cap',
                                  'Avg_YTD_Return', 'Avg_Volatility']

        sector_summary['Market_Cap_Billions'] = sector_summary['Total_Market_Cap'] / 1e9

        sector_summary = sector_summary.sort_values('Total_Market_Cap', ascending=False)

        return sector_summary

    def process_complete_pipeline(self, raw_df, animation_period='M'):
        """
        Run complete processing pipeline

        Args:
            raw_df: Raw DataFrame from DataFetcher
            animation_period: Period for animation aggregation

        Returns:
            Dictionary with processed data, animation data, and sector summary
        """
        print("\n" + "="*50)
        print("STARTING DATA PROCESSING PIPELINE")
        print("="*50)

        # Clean data
        cleaned_df = self.clean_data(raw_df)

        if cleaned_df.empty:
            print("No data to process!")
            return None

        # Calculate returns
        processed_df = self.calculate_returns(cleaned_df)

        # Calculate fundamentals
        processed_df = self.calculate_fundamentals(processed_df)

        # Prepare animation data
        animation_df = self.prepare_animation_data(processed_df, period=animation_period)

        # Get sector summary
        sector_summary = self.get_sector_summary(processed_df)

        print("\n" + "="*50)
        print("PROCESSING COMPLETE")
        print("="*50)

        print(f"\nProcessed data shape: {processed_df.shape}")
        print(f"Animation data shape: {animation_df.shape}")
        print(f"Sector summary shape: {sector_summary.shape}")

        return {
            'processed': processed_df,
            'animation': animation_df,
            'sector_summary': sector_summary
        }


def main():
    """Example usage"""
    from data_fetcher import DataFetcher

    # Fetch sample data
    fetcher = DataFetcher()
    raw_df = fetcher.fetch_complete_dataset(
        start_date=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        max_stocks=20,
        use_cache=True
    )

    if raw_df.empty:
        print("No data fetched!")
        return

    # Process data
    processor = DataProcessor()
    results = processor.process_complete_pipeline(raw_df, animation_period='M')

    if results:
        print("\nProcessed Data Sample:")
        print(results['processed'].head())

        print("\nAnimation Data Sample:")
        print(results['animation'].head())

        print("\nSector Summary:")
        print(results['sector_summary'])

        # Save processed data
        output_dir = config.DATA_DIR
        results['processed'].to_csv(
            os.path.join(output_dir, 'processed_data.csv'),
            index=False
        )
        results['animation'].to_csv(
            os.path.join(output_dir, 'animation_data.csv'),
            index=False
        )
        results['sector_summary'].to_csv(
            os.path.join(output_dir, 'sector_summary.csv'),
            index=False
        )
        print(f"\nData saved to {output_dir}")


if __name__ == '__main__':
    main()
