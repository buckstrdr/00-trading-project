"""
PDH/PDL Trading Strategy Package
"""

__version__ = "1.0.0"
__author__ = "Trading Strategy Development"
__description__ = "Automated PDH/PDL Daily Flip Trading Strategy"

from .core import *
from .database import *

__all__ = [
    # Core components
    'BaseStrategy',
    'StrategyManager',
    'Signal', 
    'SignalDirection',
    'StrategyType',
    'MarketData',
    'ReferenceLevel',
    'PositionManager',
    'PositionSizer',
    'Position',
    'AccountInfo',
    'RiskController',
    'RiskLevel',
    'RiskMetrics',
    
    # Database components
    'MarketData',
    'ReferenceLevel',
    'Trade',
    'PerformanceMetrics',
    'SystemLog',
    'DatabaseManager',
    'init_database',
    'close_database'
]