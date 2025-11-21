"""
Sentry error tracking configuration

Provides error tracking and performance monitoring integration.
"""
import os
from typing import Optional
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def init_sentry(
    dsn: Optional[str] = None,
    environment: str = 'production',
    traces_sample_rate: float = 0.1,
    enable: bool = True
):
    """
    Initialize Sentry error tracking
    
    Args:
        dsn: Sentry DSN (from environment if not provided)
        environment: Environment name (dev/staging/production)
        traces_sample_rate: Performance monitoring sample rate (0.0-1.0)
        enable: Whether to enable Sentry
    """
    if not enable:
        return
    
    # Get DSN from environment if not provided
    if dsn is None:
        dsn = os.getenv('SENTRY_DSN', '')
    
    # Only initialize if DSN is configured
    if not dsn:
        return
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=traces_sample_rate,
        
        # Integrations
        integrations=[
            LoggingIntegration(
                level=None,  # Capture all logs
                event_level=None  # Send error logs as events
            ),
            SqlalchemyIntegration(),
        ],
        
        # Release tracking
        release=os.getenv('APP_VERSION', '1.0.0'),
        
        # Additional options
        attach_stacktrace=True,
        send_default_pii=False,  # Don't send personally identifiable information
        
        # Before send hook for filtering
        before_send=before_send_filter,
    )


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry
    
    Args:
        event: Sentry event dictionary
        hint: Additional context
        
    Returns:
        Modified event or None to drop event
    """
    # Filter out certain exceptions
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Don't send keyboard interrupts
        if isinstance(exc_value, KeyboardInterrupt):
            return None
        
        # Don't send certain test exceptions
        if 'test' in str(exc_value).lower():
            return None
    
    return event


def capture_exception(exception: Exception, **kwargs):
    """
    Manually capture an exception
    
    Args:
        exception: Exception to capture
        **kwargs: Additional context
    """
    sentry_sdk.capture_exception(exception, **kwargs)


def capture_message(message: str, level: str = 'info', **kwargs):
    """
    Manually capture a message
    
    Args:
        message: Message to capture
        level: Severity level (debug/info/warning/error/fatal)
        **kwargs: Additional context
    """
    sentry_sdk.capture_message(message, level=level, **kwargs)


def set_user(user_id: Optional[str] = None, username: Optional[str] = None, **kwargs):
    """
    Set user context for error tracking
    
    Args:
        user_id: User ID
        username: Username
        **kwargs: Additional user data
    """
    sentry_sdk.set_user({
        'id': user_id,
        'username': username,
        **kwargs
    })


def set_context(context_name: str, context_data: dict):
    """
    Set additional context for error tracking
    
    Args:
        context_name: Context name
        context_data: Context data dictionary
    """
    sentry_sdk.set_context(context_name, context_data)


def set_tag(key: str, value: str):
    """
    Set a tag for error grouping
    
    Args:
        key: Tag key
        value: Tag value
    """
    sentry_sdk.set_tag(key, value)


# Decorator for automatic error tracking
def track_errors(func):
    """Decorator to automatically track function errors"""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Add function context
            set_context('function', {
                'name': func.__name__,
                'module': func.__module__,
                'args': str(args),
                'kwargs': str(kwargs)
            })
            
            # Capture and re-raise
            capture_exception(e)
            raise
    
    return wrapper


def init_from_config():
    """
    Initialize Sentry from configuration settings
    
    Reads configuration from environment or config module.
    """
    try:
        from .config_settings import get_settings
        settings = get_settings()
        
        if settings.sentry_dsn:
            init_sentry(
                dsn=settings.sentry_dsn,
                environment=os.getenv('ENVIRONMENT', 'production'),
                enable=True
            )
    except ImportError:
        # Fall back to environment variables
        dsn = os.getenv('SENTRY_DSN', '')
        if dsn:
            init_sentry(
                dsn=dsn,
                environment=os.getenv('ENVIRONMENT', 'production'),
                enable=True
            )

