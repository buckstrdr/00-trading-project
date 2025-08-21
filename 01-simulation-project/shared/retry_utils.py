#!/usr/bin/env python3
"""
Retry utilities for service communication and error handling
"""

import time
import logging
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps

logger = logging.getLogger(__name__)

class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_delay: float = 30.0,
        retry_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
        self.retry_exceptions = retry_exceptions

def retry_with_backoff(config: RetryConfig = None):
    """
    Decorator for retrying function calls with exponential backoff
    
    Args:
        config: RetryConfig object, uses defaults if None
        
    Usage:
        @retry_with_backoff(RetryConfig(max_attempts=5))
        def risky_operation():
            # Your code here
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt}")
                    return result
                    
                except config.retry_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {config.max_attempts} attempts. "
                            f"Last error: {e}"
                        )
                        break
                    
                    logger.warning(
                        f"{func.__name__} failed on attempt {attempt}/{config.max_attempts}: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * config.backoff_multiplier, config.max_delay)
            
            # All attempts failed, raise the last exception
            raise last_exception
            
        return wrapper
    return decorator

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception
):
    """
    Circuit breaker pattern decorator
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time to wait before attempting recovery
        expected_exception: Exception type that triggers the circuit breaker
    """
    def decorator(func: Callable) -> Callable:
        # Circuit breaker state
        state = {
            'failures': 0,
            'last_failure_time': None,
            'state': 'closed'  # closed, open, half-open
        }
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            
            # Check if circuit should move from open to half-open
            if (state['state'] == 'open' and 
                state['last_failure_time'] and 
                current_time - state['last_failure_time'] > recovery_timeout):
                state['state'] = 'half-open'
                logger.info(f"Circuit breaker for {func.__name__} entering half-open state")
            
            # Reject calls if circuit is open
            if state['state'] == 'open':
                raise RuntimeError(f"Circuit breaker open for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset circuit breaker
                if state['failures'] > 0:
                    logger.info(f"Circuit breaker for {func.__name__} reset after success")
                state['failures'] = 0
                state['state'] = 'closed'
                return result
                
            except expected_exception as e:
                state['failures'] += 1
                state['last_failure_time'] = current_time
                
                if state['failures'] >= failure_threshold:
                    state['state'] = 'open'
                    logger.error(
                        f"Circuit breaker opened for {func.__name__} after {state['failures']} failures"
                    )
                else:
                    logger.warning(
                        f"Circuit breaker failure {state['failures']}/{failure_threshold} for {func.__name__}: {e}"
                    )
                
                raise
        
        return wrapper
    return decorator

class HealthChecker:
    """Service health checking utilities"""
    
    @staticmethod
    @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.5))
    def check_redis_health(redis_client) -> bool:
        """Check Redis connection health with retries"""
        try:
            return redis_client.health_check()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            raise
    
    @staticmethod
    @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=1.0))
    def check_service_health(url: str, timeout: float = 5.0) -> bool:
        """Check HTTP service health with retries"""
        import requests
        
        try:
            response = requests.get(f"{url}/health", timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Service health check failed for {url}: {e}")
            raise
    
    @staticmethod
    def check_database_health(db_path: str) -> bool:
        """Check SQLite database health"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(db_path, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database health check failed for {db_path}: {e}")
            return False

# Predefined retry configurations for common scenarios
REDIS_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay=0.5,
    backoff_multiplier=1.5,
    max_delay=10.0
)

HTTP_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    backoff_multiplier=2.0,
    max_delay=15.0
)

DATABASE_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=0.1,
    backoff_multiplier=1.5,
    max_delay=5.0
)