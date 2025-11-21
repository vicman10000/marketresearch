"""
Prometheus metrics collection

Provides performance monitoring and observability metrics.
"""
from prometheus_client import Counter, Histogram, Gauge, Summary, Info
from contextlib import contextmanager
import time
from typing import Optional, Dict
from functools import wraps


# Application metrics

# Counters
api_calls_total = Counter(
    'market_viz_api_calls_total',
    'Total number of API calls',
    ['endpoint', 'status']
)

data_fetch_total = Counter(
    'market_viz_data_fetch_total',
    'Total number of data fetch operations',
    ['source', 'status']
)

visualization_created_total = Counter(
    'market_viz_visualizations_total',
    'Total number of visualizations created',
    ['type', 'status']
)

cache_operations_total = Counter(
    'market_viz_cache_operations_total',
    'Total cache operations',
    ['operation', 'status']
)

errors_total = Counter(
    'market_viz_errors_total',
    'Total number of errors',
    ['error_type', 'component']
)

# Histograms
api_call_duration = Histogram(
    'market_viz_api_call_duration_seconds',
    'API call duration in seconds',
    ['endpoint']
)

processing_duration = Histogram(
    'market_viz_processing_duration_seconds',
    'Data processing duration in seconds',
    ['stage']
)

visualization_duration = Histogram(
    'market_viz_visualization_duration_seconds',
    'Visualization creation duration in seconds',
    ['type']
)

# Gauges
active_requests = Gauge(
    'market_viz_active_requests',
    'Number of active requests'
)

cache_size_bytes = Gauge(
    'market_viz_cache_size_bytes',
    'Total cache size in bytes'
)

stocks_processed = Gauge(
    'market_viz_stocks_processed',
    'Number of stocks currently processed'
)

memory_usage_bytes = Gauge(
    'market_viz_memory_usage_bytes',
    'Current memory usage in bytes'
)

# Info
app_info = Info(
    'market_viz_app',
    'Application information'
)


class MetricsCollector:
    """Centralized metrics collection"""
    
    @staticmethod
    def record_api_call(endpoint: str, status: str = 'success'):
        """Record an API call"""
        api_calls_total.labels(endpoint=endpoint, status=status).inc()
    
    @staticmethod
    def record_data_fetch(source: str, status: str = 'success'):
        """Record a data fetch operation"""
        data_fetch_total.labels(source=source, status=status).inc()
    
    @staticmethod
    def record_visualization(viz_type: str, status: str = 'success'):
        """Record a visualization creation"""
        visualization_created_total.labels(type=viz_type, status=status).inc()
    
    @staticmethod
    def record_cache_operation(operation: str, status: str = 'success'):
        """Record a cache operation"""
        cache_operations_total.labels(operation=operation, status=status).inc()
    
    @staticmethod
    def record_error(error_type: str, component: str):
        """Record an error"""
        errors_total.labels(error_type=error_type, component=component).inc()
    
    @staticmethod
    @contextmanager
    def measure_api_call(endpoint: str):
        """Context manager to measure API call duration"""
        start = time.time()
        try:
            yield
            duration = time.time() - start
            api_call_duration.labels(endpoint=endpoint).observe(duration)
        except Exception as e:
            duration = time.time() - start
            api_call_duration.labels(endpoint=endpoint).observe(duration)
            MetricsCollector.record_api_call(endpoint, 'error')
            raise
    
    @staticmethod
    @contextmanager
    def measure_processing(stage: str):
        """Context manager to measure processing duration"""
        start = time.time()
        try:
            yield
            duration = time.time() - start
            processing_duration.labels(stage=stage).observe(duration)
        except Exception:
            duration = time.time() - start
            processing_duration.labels(stage=stage).observe(duration)
            raise
    
    @staticmethod
    @contextmanager
    def measure_visualization(viz_type: str):
        """Context manager to measure visualization duration"""
        start = time.time()
        try:
            yield
            duration = time.time() - start
            visualization_duration.labels(type=viz_type).observe(duration)
        except Exception:
            duration = time.time() - start
            visualization_duration.labels(type=viz_type).observe(duration)
            raise
    
    @staticmethod
    def set_active_requests(count: int):
        """Set number of active requests"""
        active_requests.set(count)
    
    @staticmethod
    def set_cache_size(size_bytes: int):
        """Set total cache size"""
        cache_size_bytes.set(size_bytes)
    
    @staticmethod
    def set_stocks_processed(count: int):
        """Set number of stocks processed"""
        stocks_processed.set(count)
    
    @staticmethod
    def set_memory_usage(bytes_used: int):
        """Set current memory usage"""
        memory_usage_bytes.set(bytes_used)
    
    @staticmethod
    def set_app_info(version: str, environment: str):
        """Set application information"""
        app_info.info({'version': version, 'environment': environment})


# Decorator for automatic metrics collection

def track_api_call(endpoint: str):
    """Decorator to track API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with MetricsCollector.measure_api_call(endpoint):
                try:
                    result = func(*args, **kwargs)
                    MetricsCollector.record_api_call(endpoint, 'success')
                    return result
                except Exception as e:
                    MetricsCollector.record_api_call(endpoint, 'error')
                    raise
        return wrapper
    return decorator


def track_processing(stage: str):
    """Decorator to track data processing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with MetricsCollector.measure_processing(stage):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def track_visualization(viz_type: str):
    """Decorator to track visualization creation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with MetricsCollector.measure_visualization(viz_type):
                try:
                    result = func(*args, **kwargs)
                    MetricsCollector.record_visualization(viz_type, 'success')
                    return result
                except Exception:
                    MetricsCollector.record_visualization(viz_type, 'error')
                    raise
        return wrapper
    return decorator
