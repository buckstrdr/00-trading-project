"""
Strategy Interface for Futures Backtesting System
Compatible with TSX Trading Bot V5 Strategy Framework
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import pandas as pd

class StrategySignal(BaseModel):
    """Standard signal format compatible with TSX Bot V5"""
    # REQUIRED CORE PROPERTIES
    direction: str  # 'LONG' | 'SHORT' | 'CLOSE_POSITION'
    confidence: str  # 'LOW' | 'MEDIUM' | 'HIGH' | 'TEST'
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    instrument: str = 'ES'  # Default to ES futures
    
    # REQUIRED RISK METRICS
    risk_points: float
    reward_points: float
    risk_reward_ratio: float
    
    # REQUIRED POSITION SIZING
    position_size: int
    dollar_risk: float
    dollar_reward: float
    
    # REQUIRED METADATA
    timestamp: datetime
    reason: str
    strategy_name: str
    strategy_version: str
    signal_strength: float = 1.0  # 0.0 - 1.0
    
    # OPTIONAL EXTENSIONS
    sub_strategy: Optional[str] = None
    environment: Optional[Dict[str, Any]] = None
    indicators: Optional[Dict[str, Any]] = None
    test_data: Optional[Dict[str, Any]] = None
    close_type: Optional[str] = None  # For close signals: 'full' | 'partial'

class MarketData(BaseModel):
    """Market data tick"""
    price: float
    volume: int = 1000
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None

class Candle(BaseModel):
    """OHLCV candle data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class StrategyState(BaseModel):
    """Strategy state for persistence"""
    current_position: Optional[str] = None  # 'LONG' | 'SHORT' | None
    position_open_time: Optional[datetime] = None
    last_trade_time: Optional[datetime] = None
    last_signal_time: Optional[datetime] = None
    is_ready: bool = False
    saved_at: datetime
    version: str

class StrategyConfig(BaseModel):
    """Strategy configuration"""
    # Risk management (required)
    dollar_risk_per_trade: float = 100
    dollar_per_point: float = 10  # Default for ES futures, override per instrument
    max_risk_points: float = 3.0
    risk_reward_ratio: float = 2.0
    
    # Position management
    one_trade_at_time: bool = True
    max_trade_duration_minutes: int = 480  # 8 hours
    signal_cooldown_minutes: int = 5
    
    # Strategy-specific parameters (extend in subclasses)
    parameters: Dict[str, Any] = {}
    
    @classmethod
    def for_futures_contract(cls, instrument: str, **kwargs) -> 'StrategyConfig':
        """Create configuration optimized for specific futures contract"""
        # Contract specifications
        contract_specs = {
            'MCL': {'dollar_per_point': 10.0, 'tick_size': 0.01},  # Micro WTI Crude
            'MES': {'dollar_per_point': 1.25, 'tick_size': 0.25},  # Micro E-mini S&P 500
            'ES': {'dollar_per_point': 12.50, 'tick_size': 0.25},  # E-mini S&P 500
            'NQ': {'dollar_per_point': 5.00, 'tick_size': 0.25},   # E-mini NASDAQ
            'YM': {'dollar_per_point': 5.00, 'tick_size': 1.0}     # E-mini Dow
        }
        
        specs = contract_specs.get(instrument, {'dollar_per_point': 10.0, 'tick_size': 0.25})
        
        return cls(
            dollar_per_point=specs['dollar_per_point'],
            parameters={'instrument': instrument, **kwargs}
        )

class StrategyInterface(ABC):
    """
    Base interface for all trading strategies
    Compatible with TSX Trading Bot V5 framework
    """
    
    def __init__(self, config: StrategyConfig, backtest_engine=None):
        self.name: str = self.__class__.__name__
        self.version: str = "1.0"
        self.config = config
        self.backtest_engine = backtest_engine  # Reference to backtest engine
        
        # Strategy state
        self.state = StrategyState(
            saved_at=datetime.now(),
            version=self.version
        )
        
        # Market data tracking
        self.candles: List[Candle] = []
        self.current_candle: Optional[Candle] = None
        self.last_candle_time: Optional[int] = None
        
        # Performance tracking
        self.signal_count = 0
        self.processing_times: List[float] = []
        self.initialization_time = datetime.now()
    
    @abstractmethod
    def process_market_data(self, market_data: MarketData) -> Dict[str, Any]:
        """
        Process real-time market data and generate signals
        
        Args:
            market_data: Current market data tick
            
        Returns:
            Dict with keys:
            - ready: bool - whether strategy is ready to trade
            - signal: Optional[StrategySignal] - trading signal if generated
            - environment: Optional[Dict] - market environment analysis
            - debug: Dict - debug information
        """
        pass
    
    @abstractmethod
    def is_strategy_ready(self) -> bool:
        """Check if strategy is ready to generate signals"""
        pass
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get strategy status for UI display"""
        return {
            "module": "Strategy",
            "status": "READY" if self.is_strategy_ready() else "INITIALIZING",
            "name": self.name,
            "version": self.version,
            "strategy_type": self.__class__.__name__,
            "is_ready": self.is_strategy_ready(),
            "debug": {
                "last_signal_time": self.state.last_signal_time,
                "candle_count": len(self.candles),
                "signal_count": self.signal_count,
                "position": self.state.current_position,
                "uptime_seconds": (datetime.now() - self.initialization_time).total_seconds()
            }
        }
    
    def reset(self):
        """Reset strategy state"""
        self.state = StrategyState(
            saved_at=datetime.now(),
            version=self.version
        )
        self.candles = []
        self.current_candle = None
        self.last_candle_time = None
        self.signal_count = 0
        print(f"RESET {self.name} strategy reset complete")
    
    # Optional methods that strategies can implement
    def on_position_closed(self, timestamp: datetime, was_profit: bool):
        """Called when backtester closes a position"""
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters for debugging"""
        # Serialize config with datetime conversion
        config_data = self.config.dict()
        for key, value in config_data.items():
            if hasattr(value, 'isoformat'):
                config_data[key] = value.isoformat()
        
        return {
            "config": config_data,
            "name": self.name,
            "version": self.version
        }
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get detailed debug information"""
        # Serialize state with datetime conversion
        state_data = self.state.dict()
        for key, value in state_data.items():
            if hasattr(value, 'isoformat'):
                state_data[key] = value.isoformat()
        
        return {
            "strategy": {
                "name": self.name,
                "version": self.version,
                "is_ready": self.is_strategy_ready(),
                "uptime": (datetime.now() - self.initialization_time).total_seconds()
            },
            "parameters": self.get_parameters(),
            "state": state_data,
            "performance": {
                "signals_generated": self.signal_count,
                "candles_processed": len(self.candles),
                "average_processing_time": (
                    sum(self.processing_times) / len(self.processing_times) 
                    if self.processing_times else 0
                )
            }
        }
    
    # Helper methods for strategy implementation
    def update_candle(self, price: float, volume: int, timestamp: datetime) -> bool:
        """
        Update candle data with new price/volume
        Returns True if a new candle was created
        """
        # Round timestamp to minute
        candle_time = timestamp.replace(second=0, microsecond=0)
        candle_time_ms = int(candle_time.timestamp() * 1000)
        
        # Start new candle if time changed
        if not self.last_candle_time or candle_time_ms != self.last_candle_time:
            # Close previous candle
            if self.current_candle:
                self.candles.append(self.current_candle)
                
                # Keep only last 200 candles for memory management
                if len(self.candles) > 200:
                    self.candles = self.candles[-200:]
            
            # Start new candle
            self.current_candle = Candle(
                timestamp=candle_time,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=volume
            )
            self.last_candle_time = candle_time_ms
            return True
        else:
            # Update current candle
            if self.current_candle:
                self.current_candle.high = max(self.current_candle.high, price)
                self.current_candle.low = min(self.current_candle.low, price)
                self.current_candle.close = price
                self.current_candle.volume += volume
            return False
    
    def calculate_position_size(self, risk_points: float) -> Dict[str, float]:
        """Calculate position size based on risk parameters"""
        dollar_risk = self.config.dollar_risk_per_trade
        point_value = self.config.dollar_per_point
        
        if dollar_risk <= 0:
            raise ValueError("Invalid risk configuration - dollar_risk_per_trade must be positive")
        
        if point_value <= 0:
            raise ValueError("Invalid contract configuration - dollar_per_point must be positive")
        
        # Calculate exact position size
        exact_position_size = dollar_risk / (abs(risk_points) * point_value)
        
        # Smart rounding - up to 50% over budget allowed
        position_size = max(1, round(exact_position_size))
        
        # Calculate actual dollar amounts
        actual_dollar_risk = position_size * abs(risk_points) * point_value
        reward_points = risk_points * self.config.risk_reward_ratio
        actual_dollar_reward = position_size * abs(reward_points) * point_value
        
        return {
            "position_size": position_size,
            "actual_dollar_risk": actual_dollar_risk,
            "actual_dollar_reward": actual_dollar_reward,
            "exact_position_size": exact_position_size,
            "reward_points": abs(reward_points)
        }
    
    def passes_risk_filter(self, risk_points: float, position_size: int) -> bool:
        """Check if trade passes risk management filters"""
        max_risk_points = self.config.max_risk_points
        
        # Futures-specific minimum risk points based on instrument
        instrument = self.config.parameters.get('instrument', 'ES')
        if instrument == 'MCL':
            min_risk_points = 0.005  # Half tick size for MCL (0.01)
        elif instrument == 'MES':
            min_risk_points = 0.125  # Half tick size for MES (0.25)
        elif instrument in ['ES', 'NQ', 'YM']:
            min_risk_points = 0.125  # Half tick size for standard futures
        else:
            min_risk_points = 0.005  # Default for smaller instruments
        
        # Check risk point limits
        if abs(risk_points) > max_risk_points:
            print(f"RISK FILTER: {abs(risk_points):.2f} pts > {max_risk_points} pts max")
            return False
        
        if abs(risk_points) < min_risk_points:
            print(f"RISK FILTER: {abs(risk_points):.2f} pts < {min_risk_points} pts minimum")
            return False
        
        # Check position size limits - adjust for futures contracts
        max_position_size = 100 if instrument in ['MCL', 'MES'] else 10
        if position_size > max_position_size:
            print(f"RISK FILTER: Position size {position_size} too large (max {max_position_size})")
            return False
        
        return True
    
    def create_signal(self, direction: str, entry_price: float, stop_loss: float, 
                     take_profit: float, reason: str, **kwargs) -> Optional[StrategySignal]:
        """Create a properly formatted trading signal"""
        try:
            # Calculate risk metrics
            risk_points = abs(entry_price - stop_loss)
            reward_points = abs(take_profit - entry_price)
            
            if risk_points == 0:
                print(f"INVALID SIGNAL: Risk points cannot be zero")
                return None
                
            risk_reward_ratio = reward_points / risk_points
            
            # Calculate position sizing
            position_data = self.calculate_position_size(risk_points)
            
            # Apply risk filter
            if not self.passes_risk_filter(risk_points, position_data["position_size"]):
                return None
            
            # Create signal
            signal = StrategySignal(
                direction=direction,
                confidence='HIGH',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                instrument=self.config.parameters.get('instrument', 'ES'),
                risk_points=risk_points,
                reward_points=reward_points,
                risk_reward_ratio=risk_reward_ratio,
                position_size=position_data["position_size"],
                dollar_risk=position_data["actual_dollar_risk"],
                dollar_reward=position_data["actual_dollar_reward"],
                timestamp=datetime.now(),
                reason=reason,
                strategy_name=self.name,
                strategy_version=self.version,
                **kwargs
            )
            
            # Log signal generation
            print(f"SIGNAL {self.name} {direction} signal generated")
            print(f"   Entry: {entry_price:.2f}")
            print(f"   Stop: {stop_loss:.2f}")
            print(f"   Target: {take_profit:.2f}")
            print(f"   Risk: {risk_points:.2f} pts")
            print(f"   Position: {position_data['position_size']} contracts")
            
            self.signal_count += 1
            self.state.last_signal_time = datetime.now()
            
            return signal
            
        except Exception as e:
            print(f"ERROR creating signal: {e}")
            return None
    
    def analyze_market_environment(self, price: float) -> Dict[str, Any]:
        """Analyze current market environment - override in subclasses"""
        return {
            "current_time": datetime.now(),
            "price": price,
            "trend": "NEUTRAL",  # Default trend analysis
            "volatility": "NORMAL",
            "candle_count": len(self.candles)
        }