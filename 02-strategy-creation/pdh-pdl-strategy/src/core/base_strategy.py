"""
Base strategy interface for PDH/PDL trading system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum


class SignalDirection(Enum):
    """Trading signal directions."""
    LONG = "LONG"
    SHORT = "SHORT"
    HOLD = "HOLD"


class StrategyType(Enum):
    """Strategy types for PDH/PDL system."""
    BREAKOUT = "breakout"
    FADE = "fade"
    FLIP = "flip"


@dataclass
class MarketData:
    """Market data container."""
    symbol: str
    timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    vwap: Optional[Decimal] = None
    atr: Optional[Decimal] = None


@dataclass
class Signal:
    """Trading signal container."""
    direction: SignalDirection
    symbol: str
    strategy_type: StrategyType
    entry_price: Decimal
    stop_loss: Decimal
    target_price: Optional[Decimal] = None
    confidence: Optional[float] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ReferenceLevel:
    """PDH/PDL reference levels container."""
    symbol: str
    date: datetime
    pdh: Decimal
    pdl: Decimal
    daily_range: Decimal
    midpoint: Decimal
    poc: Optional[Decimal] = None


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize strategy with configuration."""
        self.config = config
        self.name = self.__class__.__name__
        
    @abstractmethod
    def generate_signal(self, market_data: MarketData, levels: ReferenceLevel) -> Signal:
        """
        Generate trading signal based on market data and reference levels.
        
        Args:
            market_data: Current market data
            levels: PDH/PDL reference levels
            
        Returns:
            Trading signal
        """
        pass
    
    @abstractmethod
    def validate_signal(self, signal: Signal, market_data: MarketData) -> bool:
        """
        Validate trading signal before execution.
        
        Args:
            signal: Trading signal to validate
            market_data: Current market data
            
        Returns:
            True if signal is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Signal, account_balance: Decimal, 
                              risk_percent: float) -> int:
        """
        Calculate position size for the signal.
        
        Args:
            signal: Trading signal
            account_balance: Current account balance
            risk_percent: Risk percentage per trade
            
        Returns:
            Number of contracts to trade
        """
        pass
    
    def get_strategy_params(self) -> Dict[str, Any]:
        """Get strategy parameters for logging/monitoring."""
        return {
            'name': self.name,
            'config': self.config
        }


class StrategyManager:
    """Manager for multiple trading strategies."""
    
    def __init__(self):
        """Initialize strategy manager."""
        self.strategies: Dict[str, BaseStrategy] = {}
        
    def register_strategy(self, name: str, strategy: BaseStrategy):
        """Register a trading strategy."""
        self.strategies[name] = strategy
        
    def unregister_strategy(self, name: str) -> bool:
        """Unregister a trading strategy."""
        if name in self.strategies:
            del self.strategies[name]
            return True
        return False
    
    def generate_signals(self, market_data: MarketData, 
                        levels: ReferenceLevel) -> List[Signal]:
        """Generate signals from all registered strategies."""
        signals = []
        
        for strategy_name, strategy in self.strategies.items():
            try:
                signal = strategy.generate_signal(market_data, levels)
                if signal.direction != SignalDirection.HOLD:
                    if strategy.validate_signal(signal, market_data):
                        signals.append(signal)
            except Exception as e:
                # Log error but continue with other strategies
                print(f"Error in strategy {strategy_name}: {e}")
                
        return signals
    
    def get_active_strategies(self) -> List[str]:
        """Get list of active strategy names."""
        return list(self.strategies.keys())