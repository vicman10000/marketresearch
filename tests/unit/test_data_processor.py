"""
Unit tests for DataProcessor module
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_processor import DataProcessor


class TestDataProcessor:
    """Test suite for DataProcessor class"""
    
    def test_init(self):
        """Test DataProcessor initialization"""
        processor = DataProcessor()
        assert processor is not None
    
    def test_clean_data_removes_missing_values(self, sample_stock_data):
        """Test that clean_data removes rows with missing critical values"""
        processor = DataProcessor()
        
        # Add some NaN values
        df = sample_stock_data.copy()
        df.loc[0, 'Close'] = np.nan
        df.loc[1, 'Symbol'] = None
        
        cleaned = processor.clean_data(df)
        
        # Should have removed 2 rows
        assert len(cleaned) == len(df) - 2
        # No NaN in critical columns
        assert cleaned['Close'].isna().sum() == 0
        assert cleaned['Symbol'].isna().sum() == 0
    
    def test_clean_data_fills_missing_sector(self, sample_stock_data):
        """Test that clean_data fills missing Sector with 'Unknown'"""
        processor = DataProcessor()
        
        df = sample_stock_data.copy()
        df.loc[0, 'Sector'] = np.nan
        
        cleaned = processor.clean_data(df)
        
        assert 'Unknown' in cleaned['Sector'].values
        assert cleaned['Sector'].isna().sum() == 0
    
    def test_clean_data_removes_duplicates(self, sample_stock_data):
        """Test that clean_data removes duplicate Date-Symbol combinations"""
        processor = DataProcessor()
        
        df = sample_stock_data.copy()
        # Add duplicate row
        dup_row = df.iloc[0].copy()
        df = pd.concat([df, pd.DataFrame([dup_row])], ignore_index=True)
        
        cleaned = processor.clean_data(df)
        
        # Check no duplicates
        assert cleaned.duplicated(subset=['Date', 'Symbol']).sum() == 0
    
    def test_clean_data_sorts_by_symbol_and_date(self, sample_stock_data):
        """Test that clean_data sorts data correctly"""
        processor = DataProcessor()
        
        # Shuffle the data
        df = sample_stock_data.copy().sample(frac=1).reset_index(drop=True)
        
        cleaned = processor.clean_data(df)
        
        # Check if sorted
        assert cleaned['Symbol'].is_monotonic_increasing or \
               (cleaned.groupby('Symbol')['Date'].apply(lambda x: x.is_monotonic_increasing).all())
    
    def test_calculate_returns_adds_daily_return(self, sample_stock_data):
        """Test that calculate_returns adds daily return column"""
        processor = DataProcessor()
        
        df = processor.clean_data(sample_stock_data)
        result = processor.calculate_returns(df)
        
        assert 'Daily_Return' in result.columns
        # First row per symbol should be NaN
        first_rows = result.groupby('Symbol').first()
        assert first_rows['Daily_Return'].isna().all()
    
    def test_calculate_returns_adds_cumulative_return(self, sample_stock_data):
        """Test that calculate_returns adds cumulative return"""
        processor = DataProcessor()
        
        df = processor.clean_data(sample_stock_data)
        result = processor.calculate_returns(df)
        
        assert 'Cumulative_Return' in result.columns
        # First row per symbol should be 0 (or close to 0)
        first_rows = result.groupby('Symbol').first()
        assert (first_rows['Cumulative_Return'].abs() < 0.01).all()
    
    def test_calculate_returns_adds_ytd_return(self, sample_stock_data):
        """Test that calculate_returns adds YTD return"""
        processor = DataProcessor()
        
        df = processor.clean_data(sample_stock_data)
        result = processor.calculate_returns(df)
        
        assert 'YTD_Return' in result.columns
        assert not result['YTD_Return'].isna().all()
    
    def test_calculate_returns_adds_moving_average(self, sample_stock_data):
        """Test that calculate_returns adds 20-day moving average"""
        processor = DataProcessor()
        
        df = processor.clean_data(sample_stock_data)
        result = processor.calculate_returns(df)
        
        assert 'MA_20' in result.columns
        # Moving average should be between min and max price
        assert (result['MA_20'] >= result['Close'].min()).all()
        assert (result['MA_20'] <= result['Close'].max()).all()
    
    def test_calculate_returns_adds_volatility(self, sample_stock_data):
        """Test that calculate_returns adds volatility metric"""
        processor = DataProcessor()
        
        df = processor.clean_data(sample_stock_data)
        result = processor.calculate_returns(df)
        
        assert 'Volatility_20' in result.columns
        # Volatility should be positive
        assert (result['Volatility_20'] >= 0).all()
    
    def test_calculate_fundamentals_adds_market_cap(self, sample_stock_data):
        """Test that calculate_fundamentals handles market cap"""
        processor = DataProcessor()
        
        df = processor.clean_data(sample_stock_data)
        df = processor.calculate_returns(df)
        result = processor.calculate_fundamentals(df)
        
        assert 'Market_Cap' in result.columns
        # Market cap should be positive
        assert (result['Market_Cap'] > 0).all()
    
    def test_calculate_fundamentals_adds_market_cap_billions(self, sample_stock_data):
        """Test that calculate_fundamentals adds market cap in billions"""
        processor = DataProcessor()
        
        df = processor.clean_data(sample_stock_data)
        df = processor.calculate_returns(df)
        result = processor.calculate_fundamentals(df)
        
        assert 'Market_Cap_Billions' in result.columns
        # Should be Market_Cap / 1e9
        expected = result['Market_Cap'] / 1e9
        pd.testing.assert_series_equal(
            result['Market_Cap_Billions'],
            expected,
            check_names=False
        )
    
    def test_aggregate_by_period_monthly(self, sample_processed_data):
        """Test aggregation by monthly period"""
        processor = DataProcessor()
        
        result = processor.aggregate_by_period(sample_processed_data, period='M')
        
        # Should have fewer rows than daily data
        assert len(result) < len(sample_processed_data)
        # Should have one row per symbol per month
        assert result.groupby(['Symbol', result['Date'].dt.to_period('M')]).size().max() == 1
    
    def test_aggregate_by_period_weekly(self, sample_processed_data):
        """Test aggregation by weekly period"""
        processor = DataProcessor()
        
        result = processor.aggregate_by_period(sample_processed_data, period='W')
        
        # Should have fewer rows than daily data
        assert len(result) < len(sample_processed_data)
        assert 'Date' in result.columns
    
    def test_prepare_animation_data(self, sample_processed_data):
        """Test animation data preparation"""
        processor = DataProcessor()
        
        result = processor.prepare_animation_data(sample_processed_data, period='M')
        
        assert 'Year_Month' in result.columns
        # Check format of Year_Month
        assert result['Year_Month'].iloc[0].count('-') == 1  # Format: YYYY-MM
        # Should not have NaN in critical columns
        assert result['YTD_Return'].isna().sum() == 0
        assert result['Market_Cap'].isna().sum() == 0
    
    def test_get_sector_summary(self, sample_processed_data):
        """Test sector summary calculation"""
        processor = DataProcessor()
        
        result = processor.get_sector_summary(sample_processed_data)
        
        assert not result.empty
        assert 'Sector' in result.columns
        assert 'Stock_Count' in result.columns
        assert 'Total_Market_Cap' in result.columns
        assert 'Avg_YTD_Return' in result.columns
        # Should be sorted by market cap
        assert result['Total_Market_Cap'].is_monotonic_decreasing
    
    def test_get_sector_summary_no_sector_column(self):
        """Test sector summary with missing sector column"""
        processor = DataProcessor()
        
        df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Symbol': ['AAPL'],
            'Close': [150.0]
        })
        df['Date'] = pd.to_datetime(df['Date'])
        
        result = processor.get_sector_summary(df)
        
        assert result.empty
    
    def test_process_complete_pipeline(self, sample_stock_data):
        """Test complete processing pipeline"""
        processor = DataProcessor()
        
        result = processor.process_complete_pipeline(sample_stock_data, animation_period='M')
        
        assert result is not None
        assert 'processed' in result
        assert 'animation' in result
        assert 'sector_summary' in result
        
        # Check processed data
        processed = result['processed']
        assert 'Daily_Return' in processed.columns
        assert 'YTD_Return' in processed.columns
        assert 'Volatility_20' in processed.columns
        
        # Check animation data
        animation = result['animation']
        assert 'Year_Month' in animation.columns
        
        # Check sector summary
        sector_summary = result['sector_summary']
        assert not sector_summary.empty
    
    def test_process_complete_pipeline_empty_data(self):
        """Test pipeline with empty DataFrame"""
        processor = DataProcessor()
        
        empty_df = pd.DataFrame(columns=['Date', 'Symbol', 'Close'])
        result = processor.process_complete_pipeline(empty_df)
        
        assert result is None
    
    def test_process_complete_pipeline_different_periods(self, sample_stock_data):
        """Test pipeline with different animation periods"""
        processor = DataProcessor()
        
        # Test daily
        result_daily = processor.process_complete_pipeline(
            sample_stock_data,
            animation_period='D'
        )
        assert result_daily is not None
        
        # Test weekly
        result_weekly = processor.process_complete_pipeline(
            sample_stock_data,
            animation_period='W'
        )
        assert result_weekly is not None
        
        # Daily should have more rows than weekly
        assert len(result_daily['animation']) >= len(result_weekly['animation'])


class TestDataProcessorEdgeCases:
    """Test edge cases and error handling"""
    
    def test_clean_data_with_all_nan(self):
        """Test cleaning data that's all NaN"""
        processor = DataProcessor()
        
        df = pd.DataFrame({
            'Date': [None, None],
            'Symbol': [None, None],
            'Close': [None, None]
        })
        
        result = processor.clean_data(df)
        assert len(result) == 0
    
    def test_calculate_returns_single_row(self):
        """Test returns calculation with single row per symbol"""
        processor = DataProcessor()
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01']),
            'Symbol': ['AAPL'],
            'Close': [150.0]
        })
        
        result = processor.calculate_returns(df)
        
        # Should not crash
        assert len(result) == 1
        assert 'Daily_Return' in result.columns
    
    def test_aggregate_by_period_invalid_period(self, sample_processed_data):
        """Test aggregation with unsupported period"""
        processor = DataProcessor()
        
        # Should still work as pandas will handle it
        result = processor.aggregate_by_period(sample_processed_data, period='Y')
        assert len(result) > 0
