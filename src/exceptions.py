"""
Custom exception hierarchy for Market Research Visualization

Provides structured exception handling with clear error types and context.
"""


class MarketVizError(Exception):
    """Base exception for all market visualization errors"""
    
    def __init__(self, message, context=None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self):
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


# Data Fetching Errors
class DataFetchError(MarketVizError):
    """Base exception for data fetching errors"""
    pass


class APIError(DataFetchError):
    """Error communicating with external API"""
    pass


class APIRateLimitError(APIError):
    """API rate limit exceeded"""
    pass


class APIAuthenticationError(APIError):
    """API authentication failed"""
    pass


class DataNotFoundError(DataFetchError):
    """Requested data not found"""
    pass


class NetworkError(DataFetchError):
    """Network connection error"""
    pass


# Data Processing Errors
class DataProcessingError(MarketVizError):
    """Base exception for data processing errors"""
    pass


class DataValidationError(DataProcessingError):
    """Data validation failed"""
    pass


class MissingDataError(DataProcessingError):
    """Required data is missing"""
    pass


class InvalidDataError(DataProcessingError):
    """Data format or content is invalid"""
    pass


class CalculationError(DataProcessingError):
    """Error during metric calculation"""
    pass


# Storage Errors
class StorageError(MarketVizError):
    """Base exception for storage errors"""
    pass


class CacheError(StorageError):
    """Error reading or writing cache"""
    pass


class DatabaseError(StorageError):
    """Database operation error"""
    pass


class FileSystemError(StorageError):
    """File system operation error"""
    pass


# Visualization Errors
class VisualizationError(MarketVizError):
    """Base exception for visualization errors"""
    pass


class RenderError(VisualizationError):
    """Error rendering visualization"""
    pass


class ExportError(VisualizationError):
    """Error exporting visualization"""
    pass


# Configuration Errors
class ConfigurationError(MarketVizError):
    """Configuration is invalid or missing"""
    pass


class MissingConfigError(ConfigurationError):
    """Required configuration is missing"""
    pass


class InvalidConfigError(ConfigurationError):
    """Configuration value is invalid"""
    pass


# Utility functions for error handling
def wrap_api_error(exception, context=None):
    """
    Wrap a generic exception as a specific API error
    
    Args:
        exception: The original exception
        context: Additional context dictionary
        
    Returns:
        Appropriate APIError subclass
    """
    error_message = str(exception)
    
    # Check for rate limiting
    if 'rate limit' in error_message.lower() or 'too many requests' in error_message.lower():
        return APIRateLimitError(error_message, context)
    
    # Check for authentication errors
    if 'auth' in error_message.lower() or 'unauthorized' in error_message.lower():
        return APIAuthenticationError(error_message, context)
    
    # Check for network errors
    if 'connection' in error_message.lower() or 'timeout' in error_message.lower():
        return NetworkError(error_message, context)
    
    # Generic API error
    return APIError(error_message, context)


def is_retryable_error(exception):
    """
    Determine if an error is retryable
    
    Args:
        exception: The exception to check
        
    Returns:
        Boolean indicating if retry should be attempted
    """
    # Network errors are retryable
    if isinstance(exception, NetworkError):
        return True
    
    # Rate limit errors are retryable (after backoff)
    if isinstance(exception, APIRateLimitError):
        return True
    
    # Generic API errors are retryable
    if isinstance(exception, APIError) and not isinstance(exception, APIAuthenticationError):
        return True
    
    # Authentication errors are NOT retryable
    if isinstance(exception, APIAuthenticationError):
        return False
    
    # Data validation errors are NOT retryable
    if isinstance(exception, DataValidationError):
        return False
    
    # Configuration errors are NOT retryable
    if isinstance(exception, ConfigurationError):
        return False
    
    return False
