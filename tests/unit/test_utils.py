"""
Unit tests for utilities module
"""
import pytest
import pandas as pd
import json
import os
import tempfile
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils import (
    save_metadata,
    format_currency,
    format_percentage,
    validate_dataframe
)


class TestSaveMetadata:
    """Tests for save_metadata function"""
    
    def test_save_metadata_creates_file(self):
        """Test that save_metadata creates a JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_metadata.json')
            data = {'test_key': 'test_value', 'number': 42}
            
            save_metadata(data, output_path)
            
            assert os.path.exists(output_path)
    
    def test_save_metadata_correct_content(self):
        """Test that saved metadata has correct content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_metadata.json')
            data = {'test_key': 'test_value', 'number': 42}
            
            save_metadata(data, output_path)
            
            with open(output_path, 'r') as f:
                loaded = json.load(f)
            
            assert loaded == data
    
    def test_save_metadata_creates_directory(self):
        """Test that save_metadata creates parent directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'subdir', 'test_metadata.json')
            data = {'test_key': 'test_value'}
            
            save_metadata(data, output_path)
            
            assert os.path.exists(output_path)


class TestFormatCurrency:
    """Tests for format_currency function"""
    
    def test_format_currency_billions(self):
        """Test formatting billions"""
        result = format_currency(5_000_000_000)
        assert result == '$5.00B'
    
    def test_format_currency_millions(self):
        """Test formatting millions"""
        result = format_currency(5_000_000)
        assert result == '$5.00M'
    
    def test_format_currency_thousands(self):
        """Test formatting thousands"""
        result = format_currency(5_000)
        assert result == '$5.00K'
    
    def test_format_currency_small(self):
        """Test formatting small amounts"""
        result = format_currency(50.75)
        assert result == '$50.75'
    
    def test_format_currency_zero(self):
        """Test formatting zero"""
        result = format_currency(0)
        assert result == '$0.00'
    
    def test_format_currency_negative(self):
        """Test formatting negative values"""
        result = format_currency(-1_000_000)
        assert result == '$-1.00M'


class TestFormatPercentage:
    """Tests for format_percentage function"""
    
    def test_format_percentage_positive(self):
        """Test formatting positive percentage"""
        result = format_percentage(15.5)
        assert result == '15.50%'
    
    def test_format_percentage_negative(self):
        """Test formatting negative percentage"""
        result = format_percentage(-5.25)
        assert result == '-5.25%'
    
    def test_format_percentage_zero(self):
        """Test formatting zero percentage"""
        result = format_percentage(0)
        assert result == '0.00%'
    
    def test_format_percentage_large(self):
        """Test formatting large percentage"""
        result = format_percentage(150.75)
        assert result == '150.75%'


class TestValidateDataFrame:
    """Tests for validate_dataframe function"""
    
    def test_validate_dataframe_valid(self):
        """Test validation of valid DataFrame"""
        df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Symbol': ['AAPL'],
            'Close': [150.0]
        })
        
        result = validate_dataframe(df, ['Date', 'Symbol', 'Close'])
        assert result is True
    
    def test_validate_dataframe_missing_columns(self):
        """Test validation with missing columns"""
        df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Symbol': ['AAPL']
        })
        
        result = validate_dataframe(df, ['Date', 'Symbol', 'Close'])
        assert result is False
    
    def test_validate_dataframe_extra_columns(self):
        """Test validation with extra columns (should pass)"""
        df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Symbol': ['AAPL'],
            'Close': [150.0],
            'Volume': [1000000]
        })
        
        result = validate_dataframe(df, ['Date', 'Symbol', 'Close'])
        assert result is True
    
    def test_validate_dataframe_empty(self):
        """Test validation of empty DataFrame"""
        df = pd.DataFrame()
        
        result = validate_dataframe(df, ['Date', 'Symbol'])
        assert result is False
    
    def test_validate_dataframe_no_requirements(self):
        """Test validation with no required columns"""
        df = pd.DataFrame({
            'Date': ['2024-01-01']
        })
        
        result = validate_dataframe(df, [])
        assert result is True


@pytest.mark.integration
class TestPrintSummaryStats:
    """Tests for print_summary_stats function"""
    
    def test_print_summary_stats(self, sample_stock_data, capsys):
        """Test that summary stats are printed"""
        from src.utils import print_summary_stats
        
        print_summary_stats(sample_stock_data)
        
        captured = capsys.readouterr()
        assert 'DATASET SUMMARY' in captured.out
        assert 'Total rows:' in captured.out
        assert 'Unique stocks:' in captured.out


@pytest.mark.integration
class TestGenerateReport:
    """Tests for generate_report function"""
    
    def test_generate_report_creates_file(self, sample_processed_data, sample_sector_summary):
        """Test that report file is created"""
        from src.utils import generate_report
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.txt')
            
            generate_report(sample_processed_data, sample_sector_summary, output_path)
            
            assert os.path.exists(output_path)
    
    def test_generate_report_content(self, sample_processed_data, sample_sector_summary):
        """Test that report contains expected content"""
        from src.utils import generate_report
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.txt')
            
            generate_report(sample_processed_data, sample_sector_summary, output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
            
            assert 'MARKET RESEARCH VISUALIZATION REPORT' in content
            assert 'OVERVIEW' in content
            assert 'SECTOR PERFORMANCE' in content
            assert 'TOP 10 PERFORMERS' in content
            assert 'BOTTOM 10 PERFORMERS' in content
