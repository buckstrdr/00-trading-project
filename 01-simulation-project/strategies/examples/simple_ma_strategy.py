"""
Simple Moving Average Crossover Strategy
Example implementation of the Strategy Interface
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import statistics

from shared.strategy_interface import (
    StrategyInterface, StrategySignal, MarketData, 
    StrategyConfig
)
from shared.strategy_registry import register_strategy

class SimpleMAConfig(StrategyConfig):
    """Configuration for Simple MA Strategy"""
    fast_period: int = 10
    slow_period: int = 20
    min_candles_required: int = 25

@register_strategy
class SimpleMAStrategy(StrategyInterface):
    """
    Simple Moving Average Crossover Strategy
    
    Generates:
    - LONG signals when fast MA crosses above slow MA
    - SHORT signals when fast MA crosses below slow MA
    - CLOSE_POSITION signals based on stop loss/take profit
    """
    
    def __init__(self, config: SimpleMAConfig, backtest_engine=None):
        super().__init__(config, backtest_engine)
        self.name = "SIMPLE_MA"
        self.version = "1.0"
        
        # Strategy-specific configuration
        self.fast_period = config.parameters.get('fast_period', 10)
        self.slow_period = config.parameters.get('slow_period', 20)
        self.min_candles_required = config.parameters.get('min_candles_required', 25)
        
        # Strategy state
        self.last_signal_direction = None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        
        print(f"{self.name} v{self.version} initialized")
        print(f"   Fast MA: {self.fast_period}")
        print(f"   Slow MA: {self.slow_period}")
        print(f"   Min candles: {self.min_candles_required}")
    
    def process_market_data(self, market_data: MarketData) -> Dict[str, Any]:
        """Process market data and generate signals"""
        # Update candle data
        candle_changed = self.update_candle(
            market_data.price, 
            market_data.volume, 
            market_data.timestamp
        )
        
        # Check if strategy is ready
        if not self.is_strategy_ready():
            return {
                "ready": False,
                "signal": None,
                "environment": None,
                "debug": {"reason": "Not enough candles for analysis"}
            }
        
        # Only generate signals on candle close
        if not candle_changed:
            return {
                "ready": True,
                "signal": None,
                "environment": self.analyze_market_environment(market_data.price),
                "debug": {"reason": "Waiting for candle close"}
            }
        
        # Generate signal based on MA crossover
        signal = self.generate_signal(market_data.price, market_data.timestamp)
        
        return {
            "ready": True,
            "signal": signal,
            "environment": self.analyze_market_environment(market_data.price),
            "debug": {
                "reason": signal.reason if signal else "No signal conditions met",
                "fast_ma": self.get_fast_ma(),
                "slow_ma": self.get_slow_ma()
            }
        }
    
    def generate_signal(self, price: float, timestamp: datetime) -> Optional[StrategySignal]:
        """Generate trading signal based on moving average crossover"""
        
        # Calculate moving averages
        fast_ma = self.get_fast_ma()
        slow_ma = self.get_slow_ma()
        
        if fast_ma is None or slow_ma is None:
            return None
        
        # Check for existing position first
        if self.state.current_position:
            return self.check_exit_conditions(price, timestamp)
        
        # Check for crossover signals
        previous_fast = self.get_fast_ma(offset=1)
        previous_slow = self.get_slow_ma(offset=1)
        
        if previous_fast is None or previous_slow is None:
            return None
        
        # Detect bullish crossover (fast MA crosses above slow MA)
        if (previous_fast <= previous_slow and fast_ma > slow_ma and 
            self.last_signal_direction != "LONG"):
            
            return self.create_long_signal(price, fast_ma, slow_ma, timestamp)
        
        # Detect bearish crossover (fast MA crosses below slow MA)
        elif (previous_fast >= previous_slow and fast_ma < slow_ma and 
              self.last_signal_direction != "SHORT"):
              
            return self.create_short_signal(price, fast_ma, slow_ma, timestamp)
        
        return None
    
    def create_long_signal(self, price: float, fast_ma: float, slow_ma: float, 
                          timestamp: datetime) -> Optional[StrategySignal]:
        """Create LONG signal"""
        # Use fixed futures-appropriate stops (MCL tick = 0.01, reasonable stop = 0.15)
        instrument = self.config.parameters.get('instrument', 'MCL')
        if instrument == 'MCL':
            fixed_stop_distance = 0.15  # 15 ticks for MCL
        elif instrument == 'MES':
            fixed_stop_distance = 5.0   # 20 ticks for MES
        else:
            fixed_stop_distance = 0.50  # Default futures stop
            
        stop_loss = price - fixed_stop_distance
        take_profit = price + (fixed_stop_distance * self.config.risk_reward_ratio)
        
        signal = self.create_signal(
            direction="LONG",
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=f"Fast MA ({fast_ma:.2f}) crossed above Slow MA ({slow_ma:.2f})",
            sub_strategy="MA_CROSSOVER_BULL",
            indicators={
                "fast_ma": fast_ma,
                "slow_ma": slow_ma,
                "stop_distance": fixed_stop_distance,
                "instrument": instrument
            }
        )
        
        if signal:
            self.last_signal_direction = "LONG"
            self.state.current_position = "LONG"
            self.entry_price = price
            self.stop_loss = stop_loss
            self.take_profit = take_profit
        
        return signal
    
    def create_short_signal(self, price: float, fast_ma: float, slow_ma: float, 
                           timestamp: datetime) -> Optional[StrategySignal]:
        """Create SHORT signal"""
        # Use fixed futures-appropriate stops
        instrument = self.config.parameters.get('instrument', 'MCL')
        if instrument == 'MCL':
            fixed_stop_distance = 0.15  # 15 ticks for MCL
        elif instrument == 'MES':
            fixed_stop_distance = 5.0   # 20 ticks for MES
        else:
            fixed_stop_distance = 0.50  # Default futures stop
            
        stop_loss = price + fixed_stop_distance
        take_profit = price - (fixed_stop_distance * self.config.risk_reward_ratio)
        
        signal = self.create_signal(
            direction="SHORT",
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=f"Fast MA ({fast_ma:.2f}) crossed below Slow MA ({slow_ma:.2f})",
            sub_strategy="MA_CROSSOVER_BEAR",
            indicators={
                "fast_ma": fast_ma,
                "slow_ma": slow_ma,
                "stop_distance": fixed_stop_distance,
                "instrument": instrument
            }
        )
        
        if signal:
            self.last_signal_direction = "SHORT"
            self.state.current_position = "SHORT"
            self.entry_price = price
            self.stop_loss = stop_loss
            self.take_profit = take_profit
        
        return signal
    
    def check_exit_conditions(self, price: float, timestamp: datetime) -> Optional[StrategySignal]:
        """Check if position should be closed"""
        if not self.state.current_position:
            return None
        
        close_reason = None
        
        # Check stop loss
        if self.state.current_position == "LONG" and price <= self.stop_loss:
            close_reason = "STOP_LOSS"
        elif self.state.current_position == "SHORT" and price >= self.stop_loss:
            close_reason = "STOP_LOSS"
        
        # Check take profit
        elif self.state.current_position == "LONG" and price >= self.take_profit:
            close_reason = "TAKE_PROFIT"
        elif self.state.current_position == "SHORT" and price <= self.take_profit:
            close_reason = "TAKE_PROFIT"
        
        # Check time limit
        elif (self.state.position_open_time and 
              timestamp - self.state.position_open_time > 
              timedelta(minutes=self.config.max_trade_duration_minutes)):
            close_reason = "TIME_LIMIT"
        
        if close_reason:
            return self.create_close_signal(price, timestamp, close_reason)
        
        return None
    
    def create_close_signal(self, price: float, timestamp: datetime, 
                           reason: str) -> StrategySignal:
        """Create position close signal"""
        signal = StrategySignal(
            direction="CLOSE_POSITION",
            confidence="TEST",
            entry_price=price,
            instrument=self.config.parameters.get('instrument', 'ES'),
            risk_points=0,
            reward_points=0,
            risk_reward_ratio=0,
            position_size=1,
            dollar_risk=0,
            dollar_reward=0,
            timestamp=timestamp,
            reason=f"Closing position: {reason}",
            strategy_name=self.name,
            strategy_version=self.version,
            close_type="full",
            test_data={"close_reason": reason}
        )
        
        # Clear position state
        self.state.current_position = None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        
        print(f"{self.name} closing position: {reason}")
        
        return signal
    
    def get_fast_ma(self, offset: int = 0) -> Optional[float]:
        """Calculate fast moving average"""
        return self.calculate_ma(self.fast_period, offset)
    
    def get_slow_ma(self, offset: int = 0) -> Optional[float]:
        """Calculate slow moving average"""
        return self.calculate_ma(self.slow_period, offset)
    
    def calculate_ma(self, period: int, offset: int = 0) -> Optional[float]:
        """Calculate simple moving average"""
        if len(self.candles) < period + offset:
            return None
        
        end_idx = len(self.candles) - offset
        start_idx = end_idx - period
        
        if start_idx < 0:
            return None
        
        prices = [candle.close for candle in self.candles[start_idx:end_idx]]
        return statistics.mean(prices)
    
    def is_strategy_ready(self) -> bool:
        """Check if strategy has enough data to operate"""
        ready = len(self.candles) >= self.min_candles_required
        
        if ready and not self.state.is_ready:
            self.state.is_ready = True
            print(f"{self.name} now READY - {len(self.candles)} candles available")
        
        return ready
    
    def analyze_market_environment(self, price: float) -> Dict[str, Any]:
        """Analyze current market conditions"""
        fast_ma = self.get_fast_ma()
        slow_ma = self.get_slow_ma()
        
        trend = "NEUTRAL"
        if fast_ma and slow_ma:
            if fast_ma > slow_ma:
                trend = "BULLISH"
            elif fast_ma < slow_ma:
                trend = "BEARISH"
        
        return {
            "current_time": datetime.now(),
            "price": price,
            "trend": trend,
            "fast_ma": fast_ma,
            "slow_ma": slow_ma,
            "candle_count": len(self.candles),
            "is_ready": self.is_strategy_ready()
        }
    
    def on_position_closed(self, timestamp: datetime, was_profit: bool):
        """Called when backtester closes a position"""
        self.state.last_trade_time = timestamp
        result = "PROFIT" if was_profit else "LOSS"
        print(f"{self.name} position closed with {result}")
    
    def reset(self):
        """Reset strategy state"""
        super().reset()
        self.last_signal_direction = None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        print(f"{self.name} strategy reset complete")