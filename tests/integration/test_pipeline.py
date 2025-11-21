"""
Integration tests for complete data pipeline
"""
import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_processor import DataProcessor


@pytest.mark.integration
class TestCompletePipeline:
    """Integration tests for complete pipeline"""
    
    def test_end_to_end_processing(self, sample_stock_data):
        """Test complete pipeline from raw data to processed output"""
        processor = DataProcessor()
        
        # Run complete pipeline
        result = processor.process_complete_pipeline(
            sample_stock_data,
            animation_period='M'
        )
        
        # Verify all outputs exist
        assert result is not None
        assert 'processed' in result
        assert 'animation' in result
        assert 'sector_summary' in result
        
        # Verify processed data quality
        processed = result['processed']
        assert len(processed) > 0
        assert processed['Close'].notna().all()
        assert processed['YTD_Return'].notna().all()
        
        # Verify animation data quality
        animation = result['animation']
        assert len(animation) > 0
        assert 'Year_Month' in animation.columns
        
        # Verify sector summary
        sector_summary = result['sector_summary']
        assert len(sector_summary) > 0
        assert sector_summary['Avg_YTD_Return'].notna().all()
    
    def test_pipeline_with_multiple_periods(self, sample_stock_data):
        """Test pipeline works with different aggregation periods"""
        processor = DataProcessor()
        
        periods = ['D', 'W', 'M']
        results = {}
        
        for period in periods:
            result = processor.process_complete_pipeline(
                sample_stock_data,
                animation_period=period
            )
            assert result is not None
            results[period] = result
        
        # Daily should have more animation frames than monthly
        assert len(results['D']['animation']) >= len(results['M']['animation'])
    
    def test_pipeline_preserves_symbols(self, sample_stock_data):
        """Test that pipeline preserves all symbols"""
        processor = DataProcessor()
        
        original_symbols = set(sample_stock_data['Symbol'].unique())
        
        result = processor.process_complete_pipeline(sample_stock_data)
        
        processed_symbols = set(result['processed']['Symbol'].unique())
        animation_symbols = set(result['animation']['Symbol'].unique())
        
        # All symbols should be preserved
        assert processed_symbols == original_symbols
        assert animation_symbols == original_symbols

