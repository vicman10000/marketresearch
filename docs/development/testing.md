# Testing Guide

## Overview

The Market Research Visualization project uses pytest for comprehensive testing with a focus on maintainability and coverage.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── pytest.ini               # Configuration
├── fixtures/
│   ├── __init__.py
│   └── sample_data.py       # Test data generators
├── unit/
│   ├── __init__.py
│   ├── test_data_processor.py
│   ├── test_utils.py
│   └── test_models.py
└── integration/
    ├── __init__.py
    └── test_pipeline.py
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_data_processor.py

# Run specific test
pytest tests/unit/test_data_processor.py::test_calculate_returns

# Run tests matching pattern
pytest -k "test_calculate"
```

### Coverage Reports

```bash
# Run tests with coverage
pytest --cov=src

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests

# Coverage settings
addopts = 
    --cov=src
    --cov-report=term-missing
    --cov-fail-under=50
```

## Writing Tests

### Unit Test Example

```python
import pytest
import pandas as pd
from src.data_processor import DataProcessor

class TestDataProcessor:
    """Unit tests for DataProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a DataProcessor instance."""
        return DataProcessor()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample stock data."""
        return pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT'],
            'Close': [150.0, 300.0],
            'Date': pd.date_range('2024-01-01', periods=2)
        })
    
    def test_calculate_returns(self, processor, sample_data):
        """Test return calculation."""
        result = processor.calculate_returns(sample_data)
        
        assert 'Return' in result.columns
        assert not result['Return'].isna().all()
        assert result['Return'].dtype == float
    
    def test_calculate_returns_empty_data(self, processor):
        """Test with empty data."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            processor.calculate_returns(empty_df)
```

### Integration Test Example

```python
import pytest
from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor

@pytest.mark.integration
class TestDataPipeline:
    """Integration tests for complete pipeline."""
    
    def test_full_pipeline(self):
        """Test complete fetch -> process pipeline."""
        # Fetch data
        fetcher = DataFetcher()
        symbols = ['AAPL', 'MSFT']
        raw_data = fetcher.fetch_stock_data(
            symbols,
            start_date='2024-01-01',
            use_cache=True
        )
        
        # Process data
        processor = DataProcessor()
        results = processor.process_complete_pipeline(raw_data)
        
        # Assertions
        assert 'processed' in results
        assert 'animation' in results
        assert len(results['processed']) > 0
        assert 'Return' in results['processed'].columns
```

### Fixture Examples

```python
import pytest
import pandas as pd
from datetime import datetime, timedelta

@pytest.fixture
def sample_stock_prices():
    """Generate sample stock price data."""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    return pd.DataFrame({
        'Symbol': ['AAPL'] * len(dates),
        'Date': dates,
        'Open': 150.0,
        'High': 155.0,
        'Low': 148.0,
        'Close': 152.0,
        'Volume': 1000000
    })

@pytest.fixture
def mock_api_response():
    """Mock API response."""
    return {
        'chart': {
            'result': [{
                'timestamp': [1640000000, 1640086400],
                'indicators': {
                    'quote': [{
                        'close': [150.0, 152.0]
                    }]
                }
            }]
        }
    }
```

## Test Coverage Goals

### Current Coverage
- **Overall**: >50%
- **Core Modules**: >70%
- **Critical Paths**: >90%

### Target Coverage by Module

| Module | Target | Current |
|--------|--------|---------|
| data_processor.py | 80% | 75% |
| data_fetcher.py | 70% | 65% |
| static_visualizer.py | 60% | 55% |
| animated_visualizer.py | 60% | 55% |
| utils.py | 80% | 85% |
| services/ | 70% | 68% |
| storage/ | 75% | 72% |

## Mocking External Dependencies

### Mock API Calls

```python
import pytest
from unittest.mock import patch, MagicMock

@patch('src.data_fetcher.yf.Ticker')
def test_fetch_stock_data_mock(mock_ticker):
    """Test with mocked yfinance."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.history.return_value = pd.DataFrame({
        'Close': [150.0, 152.0]
    })
    mock_ticker.return_value = mock_instance
    
    # Test
    fetcher = DataFetcher()
    result = fetcher.fetch_stock_data(['AAPL'])
    
    # Assertions
    assert len(result) > 0
    mock_ticker.assert_called_once_with('AAPL')
```

### Mock File I/O

```python
@patch('pandas.read_csv')
def test_load_cached_data(mock_read_csv):
    """Test with mocked file reading."""
    mock_read_csv.return_value = pd.DataFrame({
        'Symbol': ['AAPL'],
        'Close': [150.0]
    })
    
    # Your test code here
    result = load_data('test.csv')
    
    assert len(result) == 1
```

## Parameterized Tests

```python
@pytest.mark.parametrize("input_value,expected", [
    (100, 110),
    (200, 220),
    (0, 0),
    (-100, -110),
])
def test_calculation_with_params(input_value, expected):
    """Test calculation with multiple inputs."""
    result = calculate(input_value)
    assert result == expected
```

## Testing Best Practices

### 1. Test Organization
- ✅ One test class per source class
- ✅ Descriptive test names
- ✅ Group related tests
- ✅ Use fixtures for setup

### 2. Test Independence
- ✅ Tests should not depend on each other
- ✅ Use fixtures for shared setup
- ✅ Clean up after tests
- ✅ Use temporary files/directories

### 3. Assertions
- ✅ Use specific assertions
- ✅ One logical assertion per test
- ✅ Include failure messages
- ✅ Test edge cases

### 4. Test Data
- ✅ Use realistic data
- ✅ Test with empty data
- ✅ Test with invalid data
- ✅ Use fixtures for complex data

## Common Testing Patterns

### Testing Exceptions

```python
def test_invalid_input():
    """Test that invalid input raises ValueError."""
    processor = DataProcessor()
    
    with pytest.raises(ValueError) as exc_info:
        processor.process_data(invalid_data)
    
    assert "Invalid data format" in str(exc_info.value)
```

### Testing Warnings

```python
import warnings

def test_deprecated_function():
    """Test that deprecated function warns."""
    with pytest.warns(DeprecationWarning):
        old_function()
```

### Testing with Temporary Files

```python
def test_save_to_file(tmp_path):
    """Test file saving with temporary directory."""
    output_file = tmp_path / "output.csv"
    
    save_data(data, output_file)
    
    assert output_file.exists()
    loaded = pd.read_csv(output_file)
    assert len(loaded) > 0
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Maintenance

### Regular Tasks
1. **Update fixtures** when data structures change
2. **Add tests** for new features
3. **Remove obsolete tests** for removed features
4. **Refactor tests** to reduce duplication
5. **Review coverage** reports monthly

### When to Write Tests
- ✅ Before fixing bugs (reproduce issue)
- ✅ When adding new features
- ✅ When refactoring code
- ✅ For critical business logic

## Debugging Failed Tests

### Verbose Output
```bash
pytest -vv tests/unit/test_data_processor.py::test_failing
```

### Print Debugging
```python
def test_with_debug():
    result = calculate(10)
    print(f"Result: {result}")  # Visible with -s flag
    assert result == expected
```

### Run with -s flag
```bash
pytest -s tests/unit/test_data_processor.py
```

### Using pdb
```python
def test_with_debugger():
    result = calculate(10)
    import pdb; pdb.set_trace()  # Breakpoint
    assert result == expected
```

## Performance Testing

### Mark Slow Tests
```python
@pytest.mark.slow
def test_full_sp500_processing():
    """Test with all S&P 500 stocks (slow)."""
    # This test takes >30 seconds
    pass
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Test Examples](../../tests/)
- [Sample Fixtures](../../tests/fixtures/)

## Support

For testing questions:
1. Check test examples in `tests/` directory
2. Review this guide
3. Consult pytest documentation
4. Ask in project discussions

---

**Remember**: Good tests are the foundation of maintainable code!

