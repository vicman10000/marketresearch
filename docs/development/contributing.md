# Contributing Guide

Thank you for considering contributing to the Market Research Visualization project! This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/marketresearchvisualization.git
cd marketresearchvisualization
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov pytest-mock black flake8 mypy
```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/issue-description
```

## Development Workflow

### 1. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add docstrings to functions and classes
- Keep changes focused and atomic

### 2. Write Tests

```bash
# Add tests for new features
# Location: tests/unit/ or tests/integration/

# Run tests
pytest

# Check coverage
pytest --cov=src --cov-report=html
```

### 3. Format Code

```bash
# Format with Black
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new visualization type"
# Or: "fix: resolve data fetch timeout issue"
# Or: "docs: update installation instructions"
```

#### Commit Message Convention

Follow conventional commits format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Build process or auxiliary tool changes

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Provide clear description of changes
```

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names

```python
# Good
def calculate_returns(prices: pd.DataFrame, period: str = 'ytd') -> pd.DataFrame:
    """Calculate returns for given period."""
    ...

# Bad
def calc(df, p='ytd'):
    ...
```

### Docstring Style

Use Google-style docstrings:

```python
def fetch_stock_data(symbols: List[str], start_date: str) -> pd.DataFrame:
    """Fetch stock price data for given symbols.
    
    Args:
        symbols: List of stock ticker symbols
        start_date: Start date in YYYY-MM-DD format
        
    Returns:
        DataFrame with stock price data
        
    Raises:
        DataFetchError: If API request fails
    """
    ...
```

### Import Organization

```python
# Standard library
import os
from datetime import datetime

# Third-party
import pandas as pd
import numpy as np

# Local
from src.data_fetcher import DataFetcher
from src.exceptions import DataFetchError
```

## Testing Guidelines

### Test Coverage

- Aim for >70% coverage for new code
- All new features must have tests
- Bug fixes should include regression tests

### Test Structure

```python
class TestDataProcessor:
    """Test suite for DataProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return DataProcessor()
    
    def test_calculate_returns(self, processor):
        """Test return calculation."""
        # Arrange
        data = create_sample_data()
        
        # Act
        result = processor.calculate_returns(data)
        
        # Assert
        assert 'Return' in result.columns
        assert not result['Return'].isna().all()
```

### Test Naming

- Use descriptive names: `test_calculate_returns_with_empty_data`
- Start with `test_`
- Describe what is being tested

## Documentation

### Updating Documentation

- Update relevant docs when changing functionality
- Add examples for new features
- Keep README.md current
- Update API documentation

### Documentation Structure

```
docs/
├── README.md                   # Documentation index
├── quickstart.md              # Getting started
├── guides/                    # User guides
│   ├── usage.md
│   ├── configuration.md
│   └── troubleshooting.md
├── development/               # Developer docs
│   ├── architecture.md
│   ├── testing.md
│   └── contributing.md (this file)
└── api/                      # API reference
    └── overview.md
```

## Architecture Guidelines

### Adding New Features

1. **Consider the architecture**
   - Does it fit existing patterns?
   - Should it use Protocol interfaces?
   - Does it need a service layer?

2. **Maintain separation of concerns**
   - Data fetching → `data_fetcher.py`
   - Data processing → `data_processor.py`
   - Visualization → `*_visualizer.py`
   - Business logic → `services/`

3. **Use dependency injection**
   ```python
   class MyService:
       def __init__(self, fetcher: DataFetcherProtocol):
           self.fetcher = fetcher
   ```

4. **Add proper error handling**
   ```python
   from src.exceptions import DataProcessingError
   
   try:
       result = process_data(data)
   except Exception as e:
       raise DataProcessingError(f"Failed to process: {e}")
   ```

### Backward Compatibility

- Maintain backward compatibility when possible
- If breaking changes are necessary, document them
- Provide migration path for users
- Use deprecation warnings before removal

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass: `pytest`
- [ ] Code formatted: `black src/ tests/`
- [ ] Linting passes: `flake8 src/ tests/`
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Backward compatible (or breaking changes documented)
```

### Review Process

1. Submit PR with clear description
2. Address review feedback
3. Maintain discussion in PR comments
4. Update PR based on feedback
5. Merge once approved

## Areas for Contribution

### High Priority

- [ ] Additional visualization types
- [ ] Performance optimizations
- [ ] More comprehensive tests
- [ ] Documentation improvements
- [ ] Bug fixes

### Feature Ideas

- [ ] Real-time data streaming
- [ ] Additional data sources (Polygon, IEX)
- [ ] Export to video (MP4)
- [ ] Dash/Streamlit dashboard
- [ ] Technical indicators
- [ ] Portfolio tracking
- [ ] Comparison mode

### Infrastructure

- [ ] CI/CD pipeline improvements
- [ ] Docker optimization
- [ ] Database migrations
- [ ] API rate limiting improvements
- [ ] Caching enhancements

## Resources

### Project Documentation
- [Architecture Overview](architecture.md)
- [Testing Guide](testing.md)
- [API Reference](../api/overview.md)

### External Resources
- [pytest Documentation](https://docs.pytest.org/)
- [Plotly Documentation](https://plotly.com/python/)
- [pandas Documentation](https://pandas.pydata.org/)

## Questions?

- Open a discussion on GitHub
- Ask in pull request comments
- Check existing issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

**Thank you for contributing!** 🎉

