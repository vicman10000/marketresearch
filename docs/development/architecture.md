# System Architecture

## Overview

The Market Research Visualization application is built using a clean, layered architecture that promotes maintainability, testability, and scalability.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                     Presentation Layer                   │
│          (CLI, Static Files, Interactive HTML)          │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                     Service Layer                        │
│     (MarketAnalysisService, VisualizationService)       │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                     Business Logic                       │
│   (DataProcessor, StaticVisualizer, AnimatedVisualizer) │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                     Data Access Layer                    │
│        (DataFetcher, DataStore Abstraction)             │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   External Services                      │
│    (Yahoo Finance, CSV/Database, File System)           │
└─────────────────────────────────────────────────────────┘
```

## Component Diagram

```
┌──────────────────┐     ┌──────────────────┐
│   DataFetcher    │────▶│   DataStore      │
│  (API Client)    │     │  (CSV/SQLite)    │
└──────────────────┘     └──────────────────┘
         │                        │
         ▼                        │
┌──────────────────┐              │
│  DataProcessor   │              │
│  (Transform)     │              │
└──────────────────┘              │
         │                        │
         ▼                        │
┌──────────────────┐              │
│   Visualizers    │              │
│ (Static/Animated)│              │
└──────────────────┘              │
         │                        │
         ▼                        ▼
┌──────────────────────────────────┐
│      Service Orchestration       │
│  (MarketAnalysisService, etc.)   │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│         Application CLI          │
│           (app.py)               │
└──────────────────────────────────┘
```

## Design Patterns

### 1. Protocol-Based Interfaces
- **Location**: `src/interfaces.py`
- **Pattern**: Protocol Pattern (Duck Typing with Type Safety)
- **Benefits**: 
  - Loose coupling
  - Easy testing with mocks
  - Flexibility in implementation

```python
from typing import Protocol

class DataFetcherProtocol(Protocol):
    def fetch_stock_data(self, symbols: List[str]) -> pd.DataFrame:
        ...
```

### 2. Dependency Injection
- **Location**: Service layer
- **Pattern**: Constructor Injection
- **Benefits**:
  - Testability
  - Flexibility
  - Reduced coupling

```python
class MarketAnalysisService:
    def __init__(
        self,
        data_fetcher: DataFetcherProtocol,
        data_processor: DataProcessorProtocol,
        logger: Any
    ):
        self.fetcher = data_fetcher
        self.processor = data_processor
        self.logger = logger
```

### 3. Storage Abstraction
- **Location**: `src/storage/`
- **Pattern**: Abstract Factory + Strategy
- **Benefits**:
  - Pluggable backends (CSV, SQLite, PostgreSQL)
  - Easy migration
  - Consistent interface

```python
class DataStore(ABC):
    @abstractmethod
    def save_stock_prices(self, symbol: str, data: pd.DataFrame):
        pass
```

### 4. Retry Pattern
- **Location**: `src/resilience.py`
- **Pattern**: Retry with Exponential Backoff
- **Benefits**:
  - Resilience to transient failures
  - Configurable retry logic
  - Error recovery

```python
@with_retry(max_attempts=3)
def fetch_data():
    # API call with automatic retry
    pass
```

## Data Flow

### 1. Data Fetching Pipeline

```
User Input
    │
    ▼
Fetch S&P 500 List (Wikipedia)
    │
    ▼
For Each Symbol:
    │
    ├─▶ Check Cache (DataStore)
    │   └─▶ Return if valid
    │
    ├─▶ Fetch Stock Prices (yfinance)
    │   └─▶ Retry on failure
    │
    └─▶ Save to Cache (DataStore)
    │
    ▼
Aggregate Results
```

### 2. Data Processing Pipeline

```
Raw Stock Data
    │
    ▼
Clean & Validate (Pydantic)
    │
    ▼
Calculate Metrics:
    ├─▶ Returns (YTD, period)
    ├─▶ Volatility
    ├─▶ Market Cap
    └─▶ Sector Aggregations
    │
    ▼
Prepare Animation Data:
    ├─▶ Time-based aggregation
    └─▶ Period grouping (D/W/M/Q)
    │
    ▼
Processed Data (CSV/Database)
```

### 3. Visualization Pipeline

```
Processed Data
    │
    ├─▶ Static Visualizations
    │   ├─▶ Bubble Chart
    │   ├─▶ Sector Performance
    │   ├─▶ Market Cap Distribution
    │   └─▶ Dashboard
    │
    └─▶ Animated Visualizations
        ├─▶ Animated Bubble Chart
        ├─▶ Sector Race
        ├─▶ Swarm Plot
        └─▶ 3D Visualization
    │
    ▼
HTML Output Files
```

## Module Structure

### Core Modules

#### `src/data_fetcher.py`
- **Responsibility**: Fetch data from external APIs
- **Dependencies**: yfinance, requests, beautifulsoup4
- **Features**:
  - S&P 500 constituent fetching
  - Stock price data retrieval
  - Market cap fetching
  - Retry logic integration

#### `src/data_processor.py`
- **Responsibility**: Transform and calculate metrics
- **Dependencies**: pandas, numpy
- **Features**:
  - Data cleaning and validation
  - Return calculations
  - Volatility calculations
  - Animation data preparation

#### `src/static_visualizer.py`
- **Responsibility**: Generate static charts
- **Dependencies**: plotly
- **Features**:
  - Bubble charts
  - Bar charts
  - Sunburst charts
  - Dashboard layouts

#### `src/animated_visualizer.py`
- **Responsibility**: Generate animated charts
- **Dependencies**: plotly
- **Features**:
  - Time-series animations
  - Frame-based visualizations
  - Smooth transitions

### Infrastructure Modules

#### `src/storage/`
- **Responsibility**: Data persistence abstraction
- **Implementations**:
  - `csv_store.py`: CSV-based storage
  - `sqlite_store.py`: SQLite database storage
- **Interface**: `base.py`

#### `src/services/`
- **Responsibility**: Business logic orchestration
- **Services**:
  - `market_service.py`: Market analysis operations
  - `visualization_service.py`: Visualization coordination

#### `src/database.py`
- **Responsibility**: SQLAlchemy ORM models
- **Features**:
  - Stock table
  - Price table
  - Metric table
  - Cache table

### Cross-Cutting Concerns

#### `src/logging_config.py`
- **Responsibility**: Structured logging setup
- **Features**:
  - Console and file handlers
  - JSON output format
  - Log rotation

#### `src/metrics.py`
- **Responsibility**: Prometheus metrics collection
- **Features**:
  - Counters (operations, errors)
  - Histograms (durations)
  - Gauges (resources)

#### `src/health.py`
- **Responsibility**: Health check system
- **Features**:
  - Database health
  - API health
  - System resource checks

#### `src/exceptions.py`
- **Responsibility**: Exception hierarchy
- **Features**:
  - Typed exceptions
  - Error context
  - Retry determination

## Configuration Management

```
Environment Variables (.env)
    │
    ▼
Pydantic Settings (config_settings.py)
    │
    ▼
Backward Compatible Wrapper (config.py)
    │
    ▼
Application Components
```

## Error Handling Strategy

### 1. Exception Hierarchy

```
BaseMarketVizException
├── DataFetchError
│   ├── APIError
│   └── NetworkError
├── DataProcessingError
│   ├── DataValidationError
│   └── CalculationError
├── VisualizationError
│   ├── RenderError
│   └── SaveError
└── StorageError
    ├── ReadError
    └── WriteError
```

### 2. Error Recovery

```
Try Operation
    │
    ├─▶ Transient Error?
    │   └─▶ Retry with backoff
    │
    ├─▶ Validation Error?
    │   └─▶ Log and skip
    │
    └─▶ Critical Error?
        └─▶ Capture (Sentry) & Fail
```

## Observability

### Logging

```
structlog Logger
├─▶ Console Handler (Development)
├─▶ File Handler (Production)
└─▶ JSON Handler (Parsing/Analysis)
```

### Metrics

```
Prometheus Metrics
├─▶ API Call Counter
├─▶ Fetch Duration Histogram
├─▶ Error Counter
├─▶ Cache Hit Rate
└─▶ System Resource Gauges
```

### Health Checks

```
Overall Health
├─▶ Database Connectivity
├─▶ API Availability
├─▶ Disk Space
├─▶ Memory Usage
└─▶ Cache Status
```

## Testing Strategy

### Unit Tests
- **Target**: Individual components
- **Location**: `tests/unit/`
- **Coverage**: DataProcessor, utils, models

### Integration Tests
- **Target**: Component interactions
- **Location**: `tests/integration/`
- **Coverage**: Complete pipelines

### Test Fixtures
- **Location**: `tests/fixtures/`
- **Purpose**: Sample data for testing

## Deployment Architecture

### Docker Container

```
┌─────────────────────────────────────┐
│         Docker Container             │
│  ┌───────────────────────────────┐  │
│  │   Python 3.11 Runtime         │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │   Application Code       │  │  │
│  │  │   (src/, app.py)         │  │  │
│  │  └─────────────────────────┘  │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │   Dependencies           │  │  │
│  │  │   (requirements.txt)     │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
│                                      │
│  Volumes:                            │
│  ├─▶ /app/data (cache)              │
│  └─▶ /app/outputs (results)         │
└─────────────────────────────────────┘
```

## Performance Considerations

### 1. Caching Strategy
- **Level**: File-based (CSV) or Database
- **TTL**: 24 hours (configurable)
- **Invalidation**: Time-based

### 2. Batch Processing
- **Approach**: Process stocks in parallel where possible
- **Rate Limiting**: Respect API limits with delays

### 3. Memory Management
- **Strategy**: Process in chunks for large datasets
- **Limit**: Configurable max stocks to prevent OOM

## Security Considerations

### 1. Secrets Management
- **Approach**: Environment variables only
- **Never**: Hardcode API keys

### 2. Data Validation
- **Tool**: Pydantic models
- **Level**: Input and output validation

### 3. Error Information
- **Public**: Sanitized error messages
- **Private**: Detailed logs/metrics

## Future Enhancements

### Planned Improvements
1. **API Layer**: FastAPI REST endpoints
2. **Background Tasks**: Celery task queue
3. **Real-time Data**: WebSocket support
4. **Distributed Caching**: Redis integration
5. **Advanced Analytics**: ML-based insights

## References

- [Implementation Summary](implementation-summary.md)
- [Migration Notes](migration-notes.md)
- [API Documentation](../api/overview.md)
- [Testing Guide](testing.md)

