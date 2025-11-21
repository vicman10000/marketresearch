"""
Logging configuration for Market Research Visualization

Provides structured logging using structlog with console and file handlers.
"""
import logging
import logging.handlers
import sys
import os
from pathlib import Path
import structlog
from datetime import datetime


def setup_logging(log_level="INFO", log_file=None, enable_json=False):
    """
    Configure structured logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (None for console only)
        enable_json: Whether to output JSON format
        
    Returns:
        Configured structlog logger
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )
    
    # Create logs directory if using file logging
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Add file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        logging.root.addHandler(file_handler)
    
    # Configure structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add appropriate renderer based on format
    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback
            )
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


def get_logger(name=None):
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def log_function_call(logger, function_name, **kwargs):
    """
    Log a function call with parameters
    
    Args:
        logger: Logger instance
        function_name: Name of the function
        **kwargs: Function parameters to log
    """
    logger.debug(
        "function_called",
        function=function_name,
        **kwargs
    )


def log_error(logger, error, context=None):
    """
    Log an error with context
    
    Args:
        logger: Logger instance
        error: Exception object
        context: Additional context dictionary
    """
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        log_data.update(context)
    
    logger.error("error_occurred", **log_data, exc_info=True)


def log_performance(logger, operation, duration, **kwargs):
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        operation: Name of the operation
        duration: Duration in seconds
        **kwargs: Additional metrics
    """
    logger.info(
        "performance_metric",
        operation=operation,
        duration_seconds=duration,
        **kwargs
    )


# Default logger instance
_default_logger = None


def init_default_logger(log_level="INFO", log_dir=None):
    """
    Initialize the default application logger
    
    Args:
        log_level: Logging level
        log_dir: Directory for log files
    """
    global _default_logger
    
    log_file = None
    if log_dir:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"market_viz_{timestamp}.log")
    
    _default_logger = setup_logging(
        log_level=log_level,
        log_file=log_file,
        enable_json=False
    )
    
    return _default_logger


def get_default_logger():
    """
    Get the default application logger
    
    Returns:
        Default logger instance
    """
    global _default_logger
    
    if _default_logger is None:
        _default_logger = setup_logging()
    
    return _default_logger
