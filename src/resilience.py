"""
Resilience patterns for production reliability
Includes retry logic, circuit breakers, and fallback strategies
"""
import time
from functools import wraps
from typing import Callable, Any, Optional, Type, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import logging

# Get standard logger for tenacity
logger = logging.getLogger(__name__)


# Predefined retry strategies for common scenarios

def retry_on_api_error(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    exception_types: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Retry decorator for API calls with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        exception_types: Tuple of exception types to retry on
        
    Returns:
        Decorated function with retry logic
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(exception_types),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.DEBUG),
        reraise=True
    )


def retry_on_network_error(max_attempts: int = 5):
    """
    Retry decorator specifically for network-related errors
    
    Args:
        max_attempts: Maximum number of retry attempts
        
    Returns:
        Decorated function with retry logic
    """
    import requests.exceptions
    
    return retry_on_api_error(
        max_attempts=max_attempts,
        min_wait=2,
        max_wait=30,
        exception_types=(
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
            ConnectionError,
            TimeoutError
        )
    )


def retry_on_rate_limit(max_attempts: int = 10):
    """
    Retry decorator for rate-limited APIs with longer backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        
    Returns:
        Decorated function with retry logic
    """
    return retry_on_api_error(
        max_attempts=max_attempts,
        min_wait=5,
        max_wait=60,
        exception_types=(Exception,)
    )


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    
    Prevents repeated calls to a failing service by "opening the circuit"
    after a threshold of failures is reached.
    
    States:
        - CLOSED: Normal operation, requests pass through
        - OPEN: Service is failing, requests fail fast
        - HALF_OPEN: Testing if service has recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to count as failure
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. "
                    f"Will retry after {self.recovery_timeout}s."
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
    
    def reset(self):
        """Manually reset the circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60
):
    """
    Decorator to apply circuit breaker pattern
    
    Args:
        failure_threshold: Number of failures before opening
        recovery_timeout: Seconds to wait before retry
        
    Returns:
        Decorated function
    """
    circuit_breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


def with_fallback(fallback_func: Callable):
    """
    Decorator to provide fallback function on failure
    
    Args:
        fallback_func: Function to call if primary function fails
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"Primary function {func.__name__} failed: {e}. "
                    f"Using fallback."
                )
                return fallback_func(*args, **kwargs)
        return wrapper
    return decorator


def with_timeout(seconds: int):
    """
    Decorator to add timeout to function execution
    
    Args:
        seconds: Timeout in seconds
        
    Returns:
        Decorated function
        
    Note: This uses a simple alarm-based approach.
    For async code, use asyncio.wait_for instead.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds}s")
            
            # Set alarm
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Cancel alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            
            return result
        return wrapper
    return decorator

