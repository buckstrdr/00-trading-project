"""
Logging setup for PDH/PDL trading strategy.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class StrategyLogger:
    """Custom logger setup for trading strategy."""
    
    def __init__(self, name: str = "pdh_pdl_strategy"):
        """Initialize strategy logger."""
        self.name = name
        self.logger = logging.getLogger(name)
        self._is_configured = False
    
    def setup_logging(self, 
                     log_level: str = "INFO",
                     log_dir: Optional[str] = None,
                     console_output: bool = True,
                     file_output: bool = True) -> logging.Logger:
        """
        Setup comprehensive logging system.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            console_output: Enable console logging
            file_output: Enable file logging
            
        Returns:
            Configured logger instance
        """
        
        if self._is_configured:
            return self.logger
        
        # Set log level
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {log_level}')
        
        self.logger.setLevel(numeric_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Setup console handler
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
        
        # Setup file handlers
        if file_output:
            if log_dir is None:
                log_dir = self._get_default_log_dir()
            
            # Ensure log directory exists
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            # Main log file (rotating)
            main_log_file = os.path.join(log_dir, f"{self.name}.log")
            main_handler = logging.handlers.RotatingFileHandler(
                main_log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            main_handler.setLevel(numeric_level)
            main_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(main_handler)
            
            # Daily log file
            today = datetime.now().strftime("%Y-%m-%d")
            daily_log_file = os.path.join(log_dir, f"{self.name}_{today}.log")
            daily_handler = logging.FileHandler(daily_log_file)
            daily_handler.setLevel(numeric_level)
            daily_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(daily_handler)
            
            # Error-only log file
            error_log_file = os.path.join(log_dir, f"{self.name}_errors.log")
            error_handler = logging.FileHandler(error_log_file)
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(error_handler)
            
            # Trade log file (for trade-specific events)
            trade_log_file = os.path.join(log_dir, f"{self.name}_trades.log")
            trade_handler = logging.FileHandler(trade_log_file)
            trade_handler.setLevel(logging.INFO)
            trade_handler.setFormatter(detailed_formatter)
            trade_handler.addFilter(TradeLogFilter())
            self.logger.addHandler(trade_handler)
        
        self._is_configured = True
        self.logger.info(f"Logging configured - Level: {log_level}, Console: {console_output}, File: {file_output}")
        
        return self.logger
    
    def _get_default_log_dir(self) -> str:
        """Get default log directory."""
        base_dir = Path(__file__).parent.parent.parent
        return str(base_dir / "logs")
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger."""
        if not self._is_configured:
            self.setup_logging()
        return self.logger


class TradeLogFilter(logging.Filter):
    """Filter to capture only trade-related log messages."""
    
    def filter(self, record):
        """Filter trade-related messages."""
        trade_keywords = [
            'position', 'trade', 'order', 'fill', 'entry', 'exit',
            'profit', 'loss', 'pnl', 'signal', 'breakout', 'fade', 'flip'
        ]
        
        message = record.getMessage().lower()
        return any(keyword in message for keyword in trade_keywords)


class PerformanceLogger:
    """Performance-focused logger for system metrics."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize with main logger."""
        self.logger = logger
    
    def log_trade_performance(self, 
                            symbol: str,
                            strategy: str,
                            entry_price: float,
                            exit_price: Optional[float],
                            pnl: Optional[float],
                            duration_minutes: Optional[int]):
        """Log trade performance metrics."""
        if exit_price and pnl is not None:
            self.logger.info(
                f"TRADE_COMPLETED | {symbol} | {strategy} | "
                f"Entry: {entry_price} | Exit: {exit_price} | "
                f"PnL: {pnl:.2f} | Duration: {duration_minutes}min"
            )
        else:
            self.logger.info(
                f"TRADE_OPENED | {symbol} | {strategy} | Entry: {entry_price}"
            )
    
    def log_daily_performance(self,
                            total_trades: int,
                            winning_trades: int,
                            net_pnl: float,
                            max_drawdown: float):
        """Log daily performance summary."""
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        self.logger.info(
            f"DAILY_SUMMARY | Trades: {total_trades} | "
            f"Winners: {winning_trades} ({win_rate:.1f}%) | "
            f"Net PnL: {net_pnl:.2f} | Max DD: {max_drawdown:.2f}"
        )
    
    def log_system_metrics(self,
                          cpu_usage: float,
                          memory_usage: float,
                          active_positions: int,
                          pending_orders: int):
        """Log system performance metrics."""
        self.logger.debug(
            f"SYSTEM_METRICS | CPU: {cpu_usage:.1f}% | "
            f"Memory: {memory_usage:.1f}MB | "
            f"Positions: {active_positions} | Orders: {pending_orders}"
        )


# Global logger instance
strategy_logger = StrategyLogger()


def setup_logging(log_level: str = "INFO", 
                 log_dir: Optional[str] = None,
                 console_output: bool = True,
                 file_output: bool = True) -> logging.Logger:
    """Setup logging for the trading strategy."""
    # Reset the logger to allow reconfiguration
    global strategy_logger
    strategy_logger = StrategyLogger()
    return strategy_logger.setup_logging(log_level, log_dir, console_output, file_output)


def get_logger(name: str = "pdh_pdl_strategy") -> logging.Logger:
    """Get logger instance."""
    if name == "pdh_pdl_strategy":
        return strategy_logger.get_logger()
    else:
        # Return child logger
        return strategy_logger.get_logger().getChild(name)


def get_performance_logger() -> PerformanceLogger:
    """Get performance logger instance."""
    return PerformanceLogger(strategy_logger.get_logger())


# Setup basic logging for immediate use
if not strategy_logger._is_configured:
    setup_logging()