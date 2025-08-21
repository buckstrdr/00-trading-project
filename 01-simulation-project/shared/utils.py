"""
Common utility functions
"""
import logging
import uuid
import functools
from datetime import datetime, timedelta
from typing import Any, Dict, List, Callable, Optional
import pandas as pd

def setup_logging(service_name: str, level: str = "INFO") -> logging.Logger:
    """Set up logging for a service"""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'%(asctime)s - {service_name} - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def generate_id(prefix: str = "") -> str:
    """Generate unique ID"""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}" if prefix else unique_id

def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Validate date range"""
    return start_date < end_date and end_date <= datetime.now()

def calculate_business_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate business days between dates"""
    return pd.bdate_range(start_date, end_date).size

def format_currency(amount: float) -> str:
    """Format currency amount"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.2%}"

def safe_divide(numerator: float, denominator: float) -> float:
    """Safe division that handles division by zero"""
    return numerator / denominator if denominator != 0 else 0

def validate_symbol(symbol: str) -> bool:
    """Validate futures symbol format"""
    # Basic validation - can be expanded
    return len(symbol) >= 2 and symbol.isalpha()

class Timer:
    """Simple timer context manager"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime.now()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        print(f"{self.name} completed in {duration.total_seconds():.2f} seconds")

def handle_service_errors(logger: logging.Logger, default_return=None):
    """
    Decorator to handle service errors gracefully
    
    Args:
        logger: Logger instance to use for error reporting
        default_return: Default value to return on error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                if default_return is not None:
                    return default_return
                raise
        return wrapper
    return decorator

def validate_service_config(config: Dict[str, Any], required_keys: List[str]) -> bool:
    """Validate service configuration has required keys"""
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        logger = logging.getLogger(__name__)
        logger.error(f"Missing required configuration keys: {missing_keys}")
        return False
    return True

class ServiceHealthStatus:
    """Track service health status"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.last_health_check = None
        self.consecutive_failures = 0
        self.is_healthy = True
        self.error_history = []
    
    def record_success(self):
        """Record successful operation"""
        self.last_health_check = datetime.now()
        self.consecutive_failures = 0
        self.is_healthy = True
    
    def record_failure(self, error: str):
        """Record failed operation"""
        self.last_health_check = datetime.now()
        self.consecutive_failures += 1
        self.error_history.append({
            'timestamp': datetime.now(),
            'error': error
        })
        
        # Keep only last 10 errors
        self.error_history = self.error_history[-10:]
        
        # Mark as unhealthy after 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.is_healthy = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            'service': self.service_name,
            'is_healthy': self.is_healthy,
            'consecutive_failures': self.consecutive_failures,
            'last_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'recent_errors': self.error_history[-3:] if self.error_history else []
        }