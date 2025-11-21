# Market Research Visualization

A complete end-to-end, **production-ready** solution for creating **animated financial market visualizations** like Chartfleau's viral S&P 500 bubble charts. This Python-based toolkit provides data fetching, processing, and both static and animated visualizations for financial market analysis.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Plotly](https://img.shields.io/badge/plotly-5.17%2B-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-50%25%2B-yellow)

## 🆕 Latest Updates - Production-Ready Architecture

**NEW in v2.0**: The project has been completely modernized with enterprise-grade features:
- ✅ **Testing Framework**: 30+ unit & integration tests with pytest
- ✅ **Database Support**: SQLite/PostgreSQL backend with SQLAlchemy
- ✅ **Structured Logging**: Production-ready logging with structlog
- ✅ **Error Handling**: Comprehensive exception hierarchy and retry logic
- ✅ **Monitoring**: Prometheus metrics and health checks
- ✅ **Clean Architecture**: Service layer, protocols, and dependency injection

📖 See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for complete details.

## Features

### 🎯 Complete End-to-End Pipeline
- **Data Fetching**: Automatic S&P 500 constituent list from Wikipedia + stock data from Yahoo Finance (yfinance)
- **Data Processing**: Clean data, calculate returns, volatility, and fundamental metrics
- **Static Visualizations**: Bubble charts, sector performance, market cap distribution, dashboards
- **Animated Visualizations**: Time-based bubble chart animations, sector races, swarm plots, 3D visualizations

### 🚀 Production-Ready Features
- **Testing**: Comprehensive test suite with pytest (30+ tests, >50% coverage)
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support for scalable data storage
- **Logging**: Structured logging with rotation, multiple output formats
- **Resilience**: Automatic retry logic with exponential backoff for API calls
- **Validation**: Type-safe data validation with Pydantic models
- **Monitoring**: Prometheus metrics for performance tracking
- **Health Checks**: System health monitoring for all dependencies
- **Error Tracking**: Sentry integration for production error monitoring
- **Clean Architecture**: Service layer, protocol interfaces, dependency injection

### 📊 Visualization Types

#### Static Visualizations
- **Bubble Charts**: Multi-dimensional visualization (sector, return, volatility, market cap)
- **Sector Performance**: Horizontal bar charts showing average returns by sector
- **Market Cap Distribution**: Sunburst/pie charts of sector composition
- **Top Performers**: Ranked bar charts of best/worst performers
- **Comprehensive Dashboard**: Multi-panel overview combining all metrics

#### Animated Visualizations
- **Animated Bubble Chart**: Chartfleau-style time-series bubble animation
- **Animated Sector Race**: Bar chart race showing sector performance evolution
- **Animated Swarm Plot**: Organic grouping by sector with vertical return positioning
- **3D Animated Visualization**: Three-dimensional market analysis

### 🎨 Design Features
- **Sector-specific color scheme**: Following financial industry conventions
- **Fixed axis ranges**: Smooth animations without jarring transitions
- **Area-based bubble sizing**: Accurate visual perception of market cap
- **Interactive tooltips**: Rich hover information for all data points
- **Responsive layouts**: Works on desktop and mobile browsers

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd marketresearchvisualization

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

**Core Dependencies:**
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `yfinance` - Yahoo Finance data API
- `plotly` - Interactive visualizations
- `beautifulsoup4` - Web scraping for S&P 500 list

**Production Dependencies:**
- `pytest` - Testing framework
- `structlog` - Structured logging
- `pydantic` - Data validation
- `SQLAlchemy` - Database ORM
- `tenacity` - Retry logic
- `prometheus-client` - Metrics
- `sentry-sdk` - Error tracking

See `requirements.txt` for complete list.

## Quick Start

### 🧪 Run Tests First (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run test suite to verify installation
pytest

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Option 1: Use the Main Application (Recommended)

```bash
# Run with default settings (last 1 year, all S&P 500 stocks)
python app.py

# Run with limited stocks for testing (faster)
python app.py --max-stocks 30

# Run with specific date range
python app.py --start-date 2023-01-01 --end-date 2024-01-01

# Skip animations for faster processing
python app.py --skip-animated

# Use weekly animation periods instead of monthly
python app.py --animation-period W
```

### ⚙️ Configuration via Environment Variables

Create a `.env` file in the project root:

```bash
# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/market_viz.log

# Database (optional - CSV is default)
USE_DATABASE=false
DATABASE_URL=sqlite:///./data/market_viz.db

# APIs
ALPHA_VANTAGE_API_KEY=your_key_here

# Monitoring (optional)
ENABLE_METRICS=false
SENTRY_DSN=your_sentry_dsn
```

### Option 2: Interactive Examples

```bash
# Run interactive examples
python examples/example_usage.py

# Choose from 6 different example scenarios
```

### Option 3: Use as Python Package

```python
from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor
from src.static_visualizer import StaticVisualizer
from src.animated_visualizer import AnimatedVisualizer

# Fetch data
fetcher = DataFetcher()
raw_data = fetcher.fetch_complete_dataset(
    start_date='2023-01-01',
    max_stocks=30,  # Limit for testing
    use_cache=True
)

# Process data
processor = DataProcessor()
results = processor.process_complete_pipeline(raw_data, animation_period='M')

# Create static bubble chart
visualizer = StaticVisualizer()
visualizer.create_bubble_chart(
    results['processed'],
    save_path='outputs/static/my_chart.html'
)

# Create animated bubble chart
animator = AnimatedVisualizer()
animator.create_animated_bubble_chart(
    results['animation'],
    save_path='outputs/animated/my_animation.html'
)
```

## 🐳 Docker Deployment (Recommended)

### Why Docker?
- ✅ **Zero dependency issues** - Everything packaged and ready to run
- ✅ **Consistent environment** - Works the same everywhere
- ✅ **Easy deployment** - One command to start
- ✅ **Portable** - Run on any system with Docker

### Quick Start with Docker

```bash
# Build and run with Docker Compose (easiest)
docker-compose up market-viz

# Or use Docker directly
docker build -t market-viz .
docker run -v $(pwd)/outputs:/app/outputs market-viz --max-stocks 30
```

Your visualizations will appear in `./outputs/` directory!

### Common Docker Commands

```bash
# Quick test with sample data (2 minutes)
docker-compose --profile test up market-viz-test

# Full S&P 500 analysis (30 minutes first run)
docker-compose --profile full up market-viz-full

# Custom date range
docker-compose run market-viz --start-date 2023-01-01 --max-stocks 50

# Weekly animations
docker-compose run market-viz --animation-period W --max-stocks 100
```

### Docker Benefits

- **No Python installation needed** - Just Docker
- **No dependency conflicts** - Clean isolated environment
- **Persistent cache** - Data cached between runs via volumes
- **Easy CI/CD integration** - Perfect for automated reports

📖 **See [DOCKER.md](DOCKER.md) for complete Docker documentation**

## Usage Guide

### Command Line Interface

The main application supports the following options:

```bash
python app.py [OPTIONS]

Options:
  --start-date DATE         Start date (YYYY-MM-DD). Default: 1 year ago
  --end-date DATE          End date (YYYY-MM-DD). Default: today
  --max-stocks N           Max stocks to process. Default: all S&P 500
  --no-cache               Fetch fresh data (ignore cache)
  --skip-static            Skip static visualizations
  --skip-animated          Skip animated visualizations
  --animation-period P     D=Daily, W=Weekly, M=Monthly, Q=Quarterly
  -h, --help              Show help message
```

### Examples

```bash
# Quick test with 20 stocks
python app.py --max-stocks 20

# Last 6 months with weekly animations
python app.py --start-date 2024-06-01 --animation-period W

# Full S&P 500 with monthly animations (default)
python app.py

# Static visualizations only (faster)
python app.py --skip-animated

# Fresh data without cache
python app.py --no-cache --max-stocks 50
```

## Project Structure

```
marketresearchvisualization/
├── README.md                    # This file
├── IMPLEMENTATION_SUMMARY.md    # 🆕 Production modernization details
├── MIGRATION_NOTES.md          # 🆕 Implementation guide
├── requirements.txt             # Python dependencies
├── pytest.ini                   # 🆕 Test configuration
├── config.py                    # Configuration (backward compatible)
├── app.py                       # Main application
│
├── src/                         # Source code
│   ├── __init__.py
│   ├── config_settings.py      # 🆕 Pydantic settings
│   ├── data_fetcher.py         # Fetch S&P 500 & stock data (with retry logic)
│   ├── data_processor.py       # Process & calculate metrics
│   ├── static_visualizer.py    # Static visualizations
│   ├── animated_visualizer.py  # Animated visualizations
│   ├── utils.py                # Utility functions
│   │
│   ├── exceptions.py           # 🆕 Exception hierarchy
│   ├── logging_config.py       # 🆕 Structured logging
│   ├── models.py               # 🆕 Pydantic data models
│   ├── database.py             # 🆕 SQLAlchemy models
│   ├── interfaces.py           # 🆕 Protocol definitions
│   ├── resilience.py           # 🆕 Retry & circuit breakers
│   ├── metrics.py              # 🆕 Prometheus metrics
│   ├── health.py               # 🆕 Health checks
│   ├── sentry_config.py        # 🆕 Error tracking
│   │
│   ├── services/               # 🆕 Service layer
│   │   ├── market_service.py
│   │   └── visualization_service.py
│   │
│   └── storage/                # 🆕 Storage abstraction
│       ├── base.py             # Abstract interface
│       ├── csv_store.py        # CSV implementation
│       └── sqlite_store.py     # Database implementation
│
├── tests/                       # 🆕 Test suite
│   ├── conftest.py             # Test fixtures
│   ├── unit/                   # Unit tests
│   │   ├── test_data_processor.py
│   │   └── test_utils.py
│   ├── integration/            # Integration tests
│   │   └── test_pipeline.py
│   └── fixtures/               # Test data
│
├── data/                        # Data storage
│   ├── cache/                  # Cached API responses (CSV)
│   ├── market_viz.db           # 🆕 SQLite database (optional)
│   ├── processed_data.csv      # Processed dataset
│   └── animation_data.csv      # Animation-ready data
│
├── outputs/                     # Generated visualizations
│   ├── static/                 # HTML static charts
│   ├── animated/               # HTML animated charts
│   ├── market_report.txt       # Text report
│   └── metadata.json           # Run metadata
│
├── logs/                        # 🆕 Application logs
│   └── market_viz_*.log        # Rotating log files
│
└── examples/                    # Example scripts
    └── example_usage.py        # Interactive examples
```

## Configuration

### Environment-Based Configuration (Recommended)

Create a `.env` file for environment-specific settings:

```bash
# Logging Configuration
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/market_viz.log    # Optional log file path

# Data Configuration
USE_SAMPLE_DATA=false           # Use sample data for testing
CACHE_EXPIRY_HOURS=24           # Cache duration in hours

# Database Configuration (Optional)
USE_DATABASE=false              # Switch to database storage
DATABASE_URL=sqlite:///./data/market_viz.db

# API Keys (Optional)
ALPHA_VANTAGE_API_KEY=          # For reliable data source
POLYGON_API_KEY=                # For real-time data

# Monitoring (Optional)
ENABLE_METRICS=false            # Enable Prometheus metrics
SENTRY_DSN=                     # Sentry error tracking DSN

# Visualization Settings
MAX_STOCKS_TO_DISPLAY=200       # Performance limit
ANIMATION_FRAME_DURATION=800    # Animation speed (ms)
```

### Legacy Configuration

Edit `config.py` directly for backward compatibility (all settings work without `.env`):

```python
# Date ranges
DEFAULT_START_DATE = '2023-01-01'
DEFAULT_END_DATE = '2024-01-01'

# Cache settings
CACHE_EXPIRY_HOURS = 24

# Visualization
ANIMATION_FRAME_DURATION = 800
BUBBLE_SIZE_MAX = 60

# Sector colors
SECTOR_COLORS = {
    'Information Technology': '#007ACC',
    'Health Care': '#27AE60',
    # ...
}
```

## Data Sources

### S&P 500 Constituents
- **Source**: Wikipedia - [List of S&P 500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
- **Method**: Web scraping with pandas
- **Update Frequency**: Daily (cached for 24 hours)
- **Data**: Ticker symbols, company names, GICS sectors

### Stock Price Data
- **Source**: Yahoo Finance via `yfinance` library
- **Method**: API calls (unofficial, free)
- **Data**: OHLCV (Open, High, Low, Close, Volume)
- **Limitations**:
  - Unofficial API (may break if Yahoo changes structure)
  - No API key required
  - Rate limiting via small delays
  - For personal/educational use only

### Market Capitalization
- **Source**: Yahoo Finance via `yfinance`
- **Method**: Ticker.info endpoint
- **Fallback**: Estimated from volume × price if unavailable

## Output Files

After running the application, you'll find:

### Static Visualizations (`outputs/static/`)
- `bubble_chart.html` - Main bubble chart (Return vs Volatility)
- `sector_performance.html` - Sector bar chart
- `market_cap_distribution.html` - Sunburst chart
- `top_performers.html` - Top 20 stocks
- `dashboard.html` - Comprehensive multi-panel dashboard

### Animated Visualizations (`outputs/animated/`)
- `animated_bubble_chart.html` - Time-series bubble animation
- `animated_sector_race.html` - Sector performance race
- `animated_swarm_plot.html` - Chartfleau-style swarm plot
- `animated_3d_visualization.html` - 3D market visualization

### Data Files (`data/`)
- `processed_data.csv` - Full processed dataset
- `animation_data.csv` - Time-aggregated data for animations
- `sector_summary.csv` - Sector-level statistics

### Reports (`outputs/`)
- `market_report.txt` - Text summary report
- `metadata.json` - Run configuration and statistics

## Performance Tips

### For Fast Testing
```bash
# Use fewer stocks and skip animations
python app.py --max-stocks 20 --skip-animated
```

### For Full Production Run
```bash
# Use cache and monthly periods
python app.py --animation-period M
```

### For Best Animation Quality
```bash
# Use weekly periods (more frames)
python app.py --animation-period W --max-stocks 100
```

### Data Caching
- First run downloads all data (slow: 10-30 minutes for full S&P 500)
- Subsequent runs use cache (fast: 1-2 minutes)
- Cache expires after 24 hours (configurable)
- Use `--no-cache` to force fresh data

## Troubleshooting

### Common Issues

**Problem**: `ModuleNotFoundError: No module named 'yfinance'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem**: Data fetching is very slow
```bash
# Solution: Use cache and limit stocks for testing
python app.py --max-stocks 30
```

**Problem**: yfinance fails to fetch data
```bash
# Solution: Yahoo Finance may be rate limiting or down
# Try again later or use --no-cache
python app.py --no-cache
```

**Problem**: Animations are choppy
```bash
# Solution: Reduce number of stocks or use monthly periods
python app.py --max-stocks 50 --animation-period M
```

**Problem**: Memory errors with full S&P 500
```bash
# Solution: Process in batches or limit stocks
python app.py --max-stocks 250
```

## Advanced Usage

### Using the Service Layer (New)

```python
from src.services import MarketAnalysisService
from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor
from src.logging_config import get_logger

# Initialize service with dependencies
service = MarketAnalysisService(
    data_fetcher=DataFetcher(),
    data_processor=DataProcessor(),
    logger=get_logger(__name__)
)

# Run complete analysis
results = service.analyze_market(
    start_date='2024-01-01',
    max_stocks=30,
    use_cache=True
)

if results['success']:
    print(f"Analyzed {results['metadata']['total_stocks']} stocks")
    # Use results['processed_data'], results['animation_data'], etc.
```

### Using Database Storage (New)

```python
from src.storage import get_datastore

# Use database instead of CSV
db_store = get_datastore('sqlite', database_url='sqlite:///./data/market.db')

# Unified interface - works same as CSV
db_store.save_stock_prices(symbol, data)
prices = db_store.load_stock_prices(symbol, start_date='2024-01-01')
```

### Monitoring with Metrics (New)

```python
from src.metrics import MetricsCollector, track_api_call

# Manual metrics
MetricsCollector.record_data_fetch('yfinance', 'success')
MetricsCollector.set_stocks_processed(30)

# Automatic tracking via decorator
@track_api_call('fetch_stock_data')
def my_fetch_function():
    # Your code here
    pass
```

### Health Checks (New)

```python
from src.health import get_health_check

health = get_health_check()

# Check individual services
db_status = health.check_database()
api_status = health.check_api()
disk_status = health.check_disk_space()

# Get overall health
status = health.get_overall_health()
print(f"System Status: {status['status']}")  # healthy/degraded/unhealthy
```

### Custom Stock List

```python
from src.data_fetcher import DataFetcher

fetcher = DataFetcher()

# Define your stocks
my_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Fetch stock data
stock_data = fetcher.fetch_stock_data(
    my_stocks,
    start_date='2023-01-01',
    end_date='2024-01-01'
)

# Fetch market caps
market_caps = fetcher.fetch_market_cap(my_stocks)

# Process and visualize as normal
```

### Custom Metrics

```python
from src.data_processor import DataProcessor

processor = DataProcessor()

# Add your own calculated columns
def add_custom_metrics(df):
    # Example: Calculate price momentum
    df['Momentum'] = df.groupby('Symbol')['Close'].pct_change(20)
    return df

results = processor.process_complete_pipeline(raw_data)
results['processed'] = add_custom_metrics(results['processed'])

# Visualize with custom metrics
from src.static_visualizer import StaticVisualizer

visualizer = StaticVisualizer()
visualizer.create_bubble_chart(
    results['processed'],
    x_col='Momentum',
    y_col='YTD_Return',
    title='Momentum vs Return Analysis'
)
```

### Alpha Vantage Integration

If you have an Alpha Vantage API key:

```python
# Set environment variable
import os
os.environ['ALPHA_VANTAGE_API_KEY'] = 'your_key_here'

# Modify data_fetcher.py to use Alpha Vantage instead of yfinance
# (Implementation left as exercise - see Alpha Vantage docs)
```

## Inspiration & Credits

This project is inspired by:
- **Chartfleau** ([Jan Varsava](https://chartfleau.com)) - Viral S&P 500 animated bubble charts
- **Hans Rosling** - Gapminder animated visualizations
- **D3.js Force Simulations** - Organic swarm plot animations

Data sources:
- Wikipedia - S&P 500 constituent list
- Yahoo Finance - Stock price and fundamental data

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Future Enhancements

Potential additions:
- [ ] Real-time data streaming with WebSockets
- [ ] D3.js force simulation implementation (pure Chartfleau style)
- [ ] Integration with additional data sources (Alpha Vantage, Polygon, IEX)
- [ ] Dash/Streamlit dashboard for interactive filtering
- [ ] Export to video (MP4) for social media
- [ ] Technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Comparison mode (multiple time periods side-by-side)
- [ ] Custom sector groupings
- [ ] Portfolio tracking features

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the examples folder for usage patterns
- Review the configuration options in config.py

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/ -m unit          # Unit tests only
pytest tests/integration/ -m integration  # Integration tests only

# Run specific test file
pytest tests/unit/test_data_processor.py -v
```

### Test Coverage

- **30+ tests** covering core functionality
- **Unit tests**: DataProcessor, utils, models
- **Integration tests**: Complete pipeline workflows
- **Target**: >50% code coverage (configurable in pytest.ini)

See `tests/README.md` for detailed testing guide.

## Documentation

- **[README.md](README.md)** - This file (getting started)
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Complete modernization overview
- **[MIGRATION_NOTES.md](MIGRATION_NOTES.md)** - Phase-by-phase implementation details
- **[DOCKER.md](DOCKER.md)** - Docker deployment guide
- **[tests/README.md](tests/README.md)** - Testing guide

## Changelog

### Version 2.0.0 (2024-11-21) - Production-Ready Release 🚀
**Major modernization with enterprise-grade features:**
- ✅ Added comprehensive testing framework (pytest)
- ✅ Implemented structured logging (structlog)
- ✅ Added database support (SQLAlchemy + SQLite/PostgreSQL)
- ✅ Created storage abstraction layer
- ✅ Implemented retry logic and error handling
- ✅ Added data validation (Pydantic models)
- ✅ Created service layer architecture
- ✅ Added Protocol interfaces
- ✅ Implemented Prometheus metrics
- ✅ Added health check system
- ✅ Integrated Sentry error tracking
- ✅ Complete backward compatibility maintained
- 📚 Added comprehensive documentation

**All changes are backward compatible - existing code continues to work!**

### Version 1.0.0 (2024-11-21)
- Initial release
- Complete data fetching pipeline
- Static and animated visualizations
- Command-line interface
- Docker support
- Comprehensive documentation

---

## Migration from v1.0 to v2.0

**Good News**: All v1.0 code continues to work! No breaking changes.

**To adopt new features:**
1. Install new dependencies: `pip install -r requirements.txt`
2. Optionally create `.env` file for configuration
3. Run tests to verify: `pytest`
4. Gradually adopt new features (database, metrics, etc.)

See [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for detailed migration guide.

---

**Note**: This tool uses unofficial APIs (Yahoo Finance via yfinance) and web scraping. Use responsibly and for personal/educational purposes. For commercial use, consider paid data providers like Alpha Vantage, Polygon, or Financial Modeling Prep.
