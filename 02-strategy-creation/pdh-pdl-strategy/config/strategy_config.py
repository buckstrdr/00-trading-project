"""
Configuration management for PDH/PDL trading strategy.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "pdh_pdl_strategy"
    username: str = "postgres"
    password: str = "password"
    url: Optional[str] = None


@dataclass 
class RiskConfig:
    """Risk management configuration."""
    max_daily_loss_percent: float = 0.03
    max_portfolio_heat: float = 0.10
    max_positions: int = 3
    max_margin_usage: float = 0.80
    correlation_limit: float = 0.70
    risk_percent: float = 0.01
    commission_per_contract: float = 2.50


@dataclass
class SymbolConfig:
    """Symbol-specific configuration."""
    symbol: str
    tick_value: float
    tick_size: float
    margin_requirement: int
    is_micro: bool = False
    stop_ticks: Dict[str, int] = None
    
    def __post_init__(self):
        if self.stop_ticks is None:
            self.stop_ticks = {
                'breakout': 12 if not self.is_micro else 8,
                'fade': 8 if not self.is_micro else 6,
                'flip': 10 if not self.is_micro else 7
            }


@dataclass
class TradingConfig:
    """Trading system configuration."""
    # Market hours
    market_open_time: str = "08:30"  # CT
    market_close_time: str = "21:00"  # CT
    rth_start_time: str = "08:30"    # CT
    rth_end_time: str = "15:15"      # CT
    
    # Strategy parameters
    volume_multiplier: float = 1.5
    confidence_threshold: float = 0.7
    atr_period: int = 14
    
    # Exit management
    exit_schedule: Dict[str, float] = None
    
    def __post_init__(self):
        if self.exit_schedule is None:
            self.exit_schedule = {
                "20:30": 0.5,   # 8:30 PM - 50%
                "20:45": 0.75,  # 8:45 PM - 75% 
                "20:55": 1.0    # 8:55 PM - 100%
            }


@dataclass
class StrategyConfig:
    """Complete strategy configuration."""
    database: DatabaseConfig
    risk: RiskConfig
    trading: TradingConfig
    symbols: Dict[str, SymbolConfig]
    
    # Environment settings
    environment: str = "development"  # development, testing, production
    log_level: str = "INFO"
    data_feed_url: Optional[str] = None
    broker_config: Optional[Dict[str, Any]] = None


class ConfigManager:
    """Configuration management system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager."""
        self.config_path = config_path or self._get_default_config_path()
        self.config: Optional[StrategyConfig] = None
        
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        base_dir = Path(__file__).parent
        return str(base_dir / "strategy.json")
    
    def load_config(self) -> StrategyConfig:
        """Load configuration from file or environment."""
        try:
            # Try to load from file first
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    self.config = self._parse_config(config_data)
                    logger.info(f"Configuration loaded from {self.config_path}")
            else:
                # Create default configuration
                self.config = self._create_default_config()
                self.save_config()
                logger.info("Created default configuration")
            
            # Override with environment variables
            self._override_from_environment()
            
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Return minimal default config on error
            return self._create_minimal_config()
    
    def _parse_config(self, config_data: Dict[str, Any]) -> StrategyConfig:
        """Parse configuration data into StrategyConfig."""
        # Parse database config
        db_config = DatabaseConfig(**config_data.get('database', {}))
        
        # Parse risk config  
        risk_config = RiskConfig(**config_data.get('risk', {}))
        
        # Parse trading config
        trading_config = TradingConfig(**config_data.get('trading', {}))
        
        # Parse symbol configs
        symbols = {}
        for symbol, symbol_data in config_data.get('symbols', {}).items():
            symbols[symbol] = SymbolConfig(symbol=symbol, **symbol_data)
        
        return StrategyConfig(
            database=db_config,
            risk=risk_config,
            trading=trading_config,
            symbols=symbols,
            environment=config_data.get('environment', 'development'),
            log_level=config_data.get('log_level', 'INFO'),
            data_feed_url=config_data.get('data_feed_url'),
            broker_config=config_data.get('broker_config')
        )
    
    def _create_default_config(self) -> StrategyConfig:
        """Create default configuration."""
        # Default symbols
        symbols = {
            'ES': SymbolConfig(
                symbol='ES',
                tick_value=12.50,
                tick_size=0.25,
                margin_requirement=500,
                is_micro=False
            ),
            'MES': SymbolConfig(
                symbol='MES', 
                tick_value=1.25,
                tick_size=0.25,
                margin_requirement=50,
                is_micro=True
            ),
            'NQ': SymbolConfig(
                symbol='NQ',
                tick_value=5.00,
                tick_size=0.25, 
                margin_requirement=500,
                is_micro=False
            ),
            'MNQ': SymbolConfig(
                symbol='MNQ',
                tick_value=0.50,
                tick_size=0.25,
                margin_requirement=50,
                is_micro=True
            )
        }
        
        return StrategyConfig(
            database=DatabaseConfig(),
            risk=RiskConfig(),
            trading=TradingConfig(),
            symbols=symbols
        )
    
    def _create_minimal_config(self) -> StrategyConfig:
        """Create minimal configuration for emergency use."""
        return StrategyConfig(
            database=DatabaseConfig(),
            risk=RiskConfig(),
            trading=TradingConfig(),
            symbols={
                'ES': SymbolConfig(
                    symbol='ES',
                    tick_value=12.50,
                    tick_size=0.25,
                    margin_requirement=500
                )
            }
        )
    
    def _override_from_environment(self):
        """Override configuration with environment variables."""
        if not self.config:
            return
        
        # Database overrides
        if os.getenv('DATABASE_URL'):
            self.config.database.url = os.getenv('DATABASE_URL')
        if os.getenv('DB_HOST'):
            self.config.database.host = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            self.config.database.port = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            self.config.database.database = os.getenv('DB_NAME')
        if os.getenv('DB_USER'):
            self.config.database.username = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            self.config.database.password = os.getenv('DB_PASSWORD')
        
        # Environment and logging overrides
        if os.getenv('ENVIRONMENT'):
            self.config.environment = os.getenv('ENVIRONMENT')
        if os.getenv('LOG_LEVEL'):
            self.config.log_level = os.getenv('LOG_LEVEL')
        
        # Risk overrides
        if os.getenv('MAX_DAILY_LOSS_PERCENT'):
            self.config.risk.max_daily_loss_percent = float(os.getenv('MAX_DAILY_LOSS_PERCENT'))
        if os.getenv('RISK_PERCENT'):
            self.config.risk.risk_percent = float(os.getenv('RISK_PERCENT'))
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            if not self.config:
                return False
            
            config_data = {
                'database': asdict(self.config.database),
                'risk': asdict(self.config.risk),
                'trading': asdict(self.config.trading),
                'symbols': {k: asdict(v) for k, v in self.config.symbols.items()},
                'environment': self.config.environment,
                'log_level': self.config.log_level,
                'data_feed_url': self.config.data_feed_url,
                'broker_config': self.config.broker_config
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_symbol_config(self, symbol: str) -> Optional[SymbolConfig]:
        """Get configuration for specific symbol."""
        if self.config and symbol in self.config.symbols:
            return self.config.symbols[symbol]
        return None
    
    def validate_config(self) -> bool:
        """Validate configuration settings."""
        if not self.config:
            logger.error("No configuration loaded")
            return False
        
        try:
            # Validate risk settings
            assert 0 < self.config.risk.max_daily_loss_percent <= 0.10, "Daily loss % should be 0-10%"
            assert 0 < self.config.risk.risk_percent <= 0.05, "Risk per trade should be 0-5%"
            assert self.config.risk.max_positions > 0, "Max positions must be positive"
            
            # Validate symbols
            assert len(self.config.symbols) > 0, "At least one symbol must be configured"
            for symbol, config in self.config.symbols.items():
                assert config.tick_value > 0, f"Tick value for {symbol} must be positive"
                assert config.margin_requirement > 0, f"Margin for {symbol} must be positive"
            
            # Validate environment
            assert self.config.environment in ['development', 'testing', 'production'], \
                   "Environment must be development, testing, or production"
            
            logger.info("Configuration validation passed")
            return True
            
        except AssertionError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False


# Global configuration manager instance
config_manager = ConfigManager()


def load_config(config_path: Optional[str] = None) -> StrategyConfig:
    """Load strategy configuration."""
    if config_path:
        global config_manager
        config_manager = ConfigManager(config_path)
    
    return config_manager.load_config()


def get_config() -> Optional[StrategyConfig]:
    """Get current configuration."""
    return config_manager.config


def get_symbol_config(symbol: str) -> Optional[SymbolConfig]:
    """Get symbol-specific configuration."""
    return config_manager.get_symbol_config(symbol)