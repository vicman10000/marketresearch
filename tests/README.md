# Test Suite

Comprehensive test suite for Market Research Visualization application.

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures and pytest configuration
├── fixtures/             # Test data generators
│   └── sample_data.py
├── unit/                 # Unit tests (fast, isolated)
│   ├── test_data_processor.py
│   └── test_utils.py
└── integration/          # Integration tests (full pipeline)
    └── test_pipeline.py
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=src --cov-report=html
```

### Run only unit tests
```bash
pytest tests/unit/ -m unit
```

### Run only integration tests
```bash
pytest tests/integration/ -m integration
```

### Run specific test file
```bash
pytest tests/unit/test_data_processor.py
```

### Run specific test function
```bash
pytest tests/unit/test_data_processor.py::TestDataProcessor::test_clean_data_removes_missing_values
```

## Test Markers

- `@pytest.mark.unit` - Fast unit tests with no external dependencies
- `@pytest.mark.integration` - Integration tests that test full workflows
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.api` - Tests that make actual API calls
- `@pytest.mark.db` - Tests that require database

## Coverage Goals

- **Overall**: >80% code coverage
- **Core modules**: >90% coverage (data_processor, data_fetcher)
- **Utils**: >85% coverage

## Writing New Tests

1. Create test file in appropriate directory (`unit/` or `integration/`)
2. Name file with `test_` prefix (e.g., `test_my_module.py`)
3. Group related tests in classes with `Test` prefix
4. Use fixtures from `conftest.py` for common test data
5. Add appropriate markers to categorize tests

Example:
```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    def test_basic_functionality(self, sample_stock_data):
        # Your test here
        pass
```

## Fixtures Available

- `sample_stock_data` - Basic stock price data (OHLCV)
- `sample_processed_data` - Processed data with calculated metrics
- `sample_sector_summary` - Sector-level aggregated data
- `sample_animation_data` - Monthly aggregated data for animations
- `mock_config` - Mock configuration dictionary

See `conftest.py` for complete fixture definitions.

