"""
Technical indicators engine for PDH/PDL trading strategy.
Implements VWAP, ATR, ADX, and other technical analysis indicators.
"""

import logging
import pandas as pd
import numpy as np
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class IndicatorResult:
    """Container for indicator calculation results."""
    name: str
    value: Optional[float]
    series: Optional[pd.Series] = None
    metadata: Optional[Dict] = None
    is_valid: bool = True
    error_message: Optional[str] = None


class BaseIndicator(ABC):
    """Abstract base class for technical indicators."""
    
    def __init__(self, period: int = 14):
        """Initialize indicator with period."""
        self.period = period
        self.name = self.__class__.__name__
        
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """Calculate indicator values."""
        pass
    
    def validate_data(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Validate input data for indicator calculation."""
        if data.empty:
            return False, "Empty data provided"
        
        required_columns = self.get_required_columns()
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {missing_columns}"
        
        if len(data) < self.period:
            return False, f"Insufficient data: need {self.period}, got {len(data)}"
        
        return True, "Data validation passed"
    
    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """Get list of required columns for this indicator."""
        pass


class VWAP(BaseIndicator):
    """Volume Weighted Average Price indicator."""
    
    def __init__(self, session_reset: bool = True):
        """
        Initialize VWAP indicator.
        
        Args:
            session_reset: Whether to reset VWAP at session boundaries
        """
        super().__init__(period=1)  # VWAP doesn't use period
        self.session_reset = session_reset
        self.name = "VWAP"
    
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """Calculate Volume Weighted Average Price."""
        try:
            is_valid, message = self.validate_data(data)
            if not is_valid:
                return IndicatorResult(
                    name=self.name,
                    value=None,
                    is_valid=False,
                    error_message=message
                )
            
            data_copy = data.copy()
            
            # Calculate typical price
            data_copy['typical_price'] = (data_copy['high'] + data_copy['low'] + data_copy['close']) / 3
            
            # Calculate volume * typical price
            data_copy['volume_price'] = data_copy['typical_price'] * data_copy['volume']
            
            if self.session_reset and 'timestamp' in data_copy.columns:
                # Reset VWAP at session boundaries (daily)
                data_copy['date'] = pd.to_datetime(data_copy['timestamp']).dt.date
                
                # Calculate cumulative sums by date
                data_copy['cum_volume_price'] = data_copy.groupby('date')['volume_price'].cumsum()
                data_copy['cum_volume'] = data_copy.groupby('date')['volume'].cumsum()
            else:
                # Running VWAP
                data_copy['cum_volume_price'] = data_copy['volume_price'].cumsum()
                data_copy['cum_volume'] = data_copy['volume'].cumsum()
            
            # Calculate VWAP
            data_copy['vwap'] = data_copy['cum_volume_price'] / data_copy['cum_volume']
            
            # Handle division by zero
            data_copy['vwap'] = data_copy['vwap'].replace([np.inf, -np.inf], np.nan)
            
            current_vwap = data_copy['vwap'].iloc[-1] if not data_copy['vwap'].empty else None
            
            return IndicatorResult(
                name=self.name,
                value=current_vwap,
                series=data_copy['vwap'],
                metadata={'session_reset': self.session_reset}
            )
            
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return IndicatorResult(
                name=self.name,
                value=None,
                is_valid=False,
                error_message=str(e)
            )
    
    def get_required_columns(self) -> List[str]:
        """Get required columns for VWAP calculation."""
        return ['high', 'low', 'close', 'volume']


class ATR(BaseIndicator):
    """Average True Range indicator."""
    
    def __init__(self, period: int = 14):
        """Initialize ATR indicator."""
        super().__init__(period)
        self.name = "ATR"
    
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """Calculate Average True Range."""
        try:
            is_valid, message = self.validate_data(data)
            if not is_valid:
                return IndicatorResult(
                    name=self.name,
                    value=None,
                    is_valid=False,
                    error_message=message
                )
            
            data_copy = data.copy()
            
            # Calculate True Range components
            data_copy['high_low'] = data_copy['high'] - data_copy['low']
            data_copy['high_close_prev'] = abs(data_copy['high'] - data_copy['close'].shift(1))
            data_copy['low_close_prev'] = abs(data_copy['low'] - data_copy['close'].shift(1))
            
            # True Range is the maximum of the three components
            data_copy['true_range'] = data_copy[['high_low', 'high_close_prev', 'low_close_prev']].max(axis=1)
            
            # Calculate ATR using exponential moving average
            data_copy['atr'] = data_copy['true_range'].ewm(span=self.period, adjust=False).mean()
            
            current_atr = data_copy['atr'].iloc[-1] if not data_copy['atr'].empty else None
            
            return IndicatorResult(
                name=self.name,
                value=current_atr,
                series=data_copy['atr'],
                metadata={'period': self.period}
            )
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return IndicatorResult(
                name=self.name,
                value=None,
                is_valid=False,
                error_message=str(e)
            )
    
    def get_required_columns(self) -> List[str]:
        """Get required columns for ATR calculation."""
        return ['high', 'low', 'close']


class ADX(BaseIndicator):
    """Average Directional Index - trend strength indicator."""
    
    def __init__(self, period: int = 14):
        """Initialize ADX indicator."""
        super().__init__(period)
        self.name = "ADX"
    
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """Calculate Average Directional Index."""
        try:
            is_valid, message = self.validate_data(data)
            if not is_valid:
                return IndicatorResult(
                    name=self.name,
                    value=None,
                    is_valid=False,
                    error_message=message
                )
            
            data_copy = data.copy()
            
            # Calculate True Range (reuse ATR calculation)
            atr_indicator = ATR(self.period)
            atr_result = atr_indicator.calculate(data_copy)
            
            if not atr_result.is_valid:
                return IndicatorResult(
                    name=self.name,
                    value=None,
                    is_valid=False,
                    error_message=f"ATR calculation failed: {atr_result.error_message}"
                )
            
            data_copy['true_range'] = atr_result.series
            
            # Calculate directional movement
            data_copy['high_diff'] = data_copy['high'] - data_copy['high'].shift(1)
            data_copy['low_diff'] = data_copy['low'].shift(1) - data_copy['low']
            
            # Positive and Negative Directional Movement
            data_copy['dm_plus'] = np.where(
                (data_copy['high_diff'] > data_copy['low_diff']) & (data_copy['high_diff'] > 0),
                data_copy['high_diff'],
                0
            )
            
            data_copy['dm_minus'] = np.where(
                (data_copy['low_diff'] > data_copy['high_diff']) & (data_copy['low_diff'] > 0),
                data_copy['low_diff'],
                0
            )
            
            # Smooth the directional movements and true range
            data_copy['dm_plus_smooth'] = data_copy['dm_plus'].ewm(span=self.period, adjust=False).mean()
            data_copy['dm_minus_smooth'] = data_copy['dm_minus'].ewm(span=self.period, adjust=False).mean()
            data_copy['true_range_smooth'] = data_copy['true_range'].ewm(span=self.period, adjust=False).mean()
            
            # Calculate Directional Indicators
            data_copy['di_plus'] = 100 * data_copy['dm_plus_smooth'] / data_copy['true_range_smooth']
            data_copy['di_minus'] = 100 * data_copy['dm_minus_smooth'] / data_copy['true_range_smooth']
            
            # Calculate DX (Directional Movement Index)
            data_copy['dx'] = 100 * abs(data_copy['di_plus'] - data_copy['di_minus']) / (data_copy['di_plus'] + data_copy['di_minus'])
            
            # Calculate ADX (Average Directional Index)
            data_copy['adx'] = data_copy['dx'].ewm(span=self.period, adjust=False).mean()
            
            # Handle division by zero and infinite values
            data_copy['adx'] = data_copy['adx'].replace([np.inf, -np.inf], np.nan)
            
            current_adx = data_copy['adx'].iloc[-1] if not data_copy['adx'].empty else None
            
            return IndicatorResult(
                name=self.name,
                value=current_adx,
                series=data_copy['adx'],
                metadata={
                    'period': self.period,
                    'di_plus': data_copy['di_plus'].iloc[-1] if not data_copy['di_plus'].empty else None,
                    'di_minus': data_copy['di_minus'].iloc[-1] if not data_copy['di_minus'].empty else None
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return IndicatorResult(
                name=self.name,
                value=None,
                is_valid=False,
                error_message=str(e)
            )
    
    def get_required_columns(self) -> List[str]:
        """Get required columns for ADX calculation."""
        return ['high', 'low', 'close']


class RSI(BaseIndicator):
    """Relative Strength Index indicator."""
    
    def __init__(self, period: int = 14):
        """Initialize RSI indicator."""
        super().__init__(period)
        self.name = "RSI"
    
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """Calculate Relative Strength Index."""
        try:
            is_valid, message = self.validate_data(data)
            if not is_valid:
                return IndicatorResult(
                    name=self.name,
                    value=None,
                    is_valid=False,
                    error_message=message
                )
            
            data_copy = data.copy()
            
            # Calculate price changes
            data_copy['price_change'] = data_copy['close'] - data_copy['close'].shift(1)
            
            # Separate gains and losses
            data_copy['gains'] = np.where(data_copy['price_change'] > 0, data_copy['price_change'], 0)
            data_copy['losses'] = np.where(data_copy['price_change'] < 0, abs(data_copy['price_change']), 0)
            
            # Calculate average gains and losses
            data_copy['avg_gains'] = data_copy['gains'].ewm(span=self.period, adjust=False).mean()
            data_copy['avg_losses'] = data_copy['losses'].ewm(span=self.period, adjust=False).mean()
            
            # Calculate RS and RSI
            data_copy['rs'] = data_copy['avg_gains'] / data_copy['avg_losses']
            data_copy['rsi'] = 100 - (100 / (1 + data_copy['rs']))
            
            # Handle division by zero
            data_copy['rsi'] = data_copy['rsi'].replace([np.inf, -np.inf], np.nan)
            
            current_rsi = data_copy['rsi'].iloc[-1] if not data_copy['rsi'].empty else None
            
            return IndicatorResult(
                name=self.name,
                value=current_rsi,
                series=data_copy['rsi'],
                metadata={'period': self.period}
            )
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return IndicatorResult(
                name=self.name,
                value=None,
                is_valid=False,
                error_message=str(e)
            )
    
    def get_required_columns(self) -> List[str]:
        """Get required columns for RSI calculation."""
        return ['close']


class MovingAverage(BaseIndicator):
    """Moving Average indicators (SMA, EMA)."""
    
    def __init__(self, period: int = 20, ma_type: str = 'sma'):
        """
        Initialize Moving Average indicator.
        
        Args:
            period: Period for moving average
            ma_type: Type of moving average ('sma' or 'ema')
        """
        super().__init__(period)
        self.ma_type = ma_type.lower()
        self.name = f"{ma_type.upper()}_{period}"
    
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """Calculate Moving Average."""
        try:
            is_valid, message = self.validate_data(data)
            if not is_valid:
                return IndicatorResult(
                    name=self.name,
                    value=None,
                    is_valid=False,
                    error_message=message
                )
            
            data_copy = data.copy()
            
            if self.ma_type == 'sma':
                # Simple Moving Average
                data_copy['ma'] = data_copy['close'].rolling(window=self.period).mean()
            elif self.ma_type == 'ema':
                # Exponential Moving Average
                data_copy['ma'] = data_copy['close'].ewm(span=self.period, adjust=False).mean()
            else:
                raise ValueError(f"Unsupported moving average type: {self.ma_type}")
            
            current_ma = data_copy['ma'].iloc[-1] if not data_copy['ma'].empty else None
            
            return IndicatorResult(
                name=self.name,
                value=current_ma,
                series=data_copy['ma'],
                metadata={'period': self.period, 'type': self.ma_type}
            )
            
        except Exception as e:
            logger.error(f"Error calculating {self.name}: {e}")
            return IndicatorResult(
                name=self.name,
                value=None,
                is_valid=False,
                error_message=str(e)
            )
    
    def get_required_columns(self) -> List[str]:
        """Get required columns for Moving Average calculation."""
        return ['close']


class BollingerBands(BaseIndicator):
    """Bollinger Bands indicator."""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        """
        Initialize Bollinger Bands indicator.
        
        Args:
            period: Period for moving average
            std_dev: Number of standard deviations for bands
        """
        super().__init__(period)
        self.std_dev = std_dev
        self.name = f"BB_{period}_{std_dev}"
    
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """Calculate Bollinger Bands."""
        try:
            is_valid, message = self.validate_data(data)
            if not is_valid:
                return IndicatorResult(
                    name=self.name,
                    value=None,
                    is_valid=False,
                    error_message=message
                )
            
            data_copy = data.copy()
            
            # Calculate middle band (SMA)
            data_copy['bb_middle'] = data_copy['close'].rolling(window=self.period).mean()
            
            # Calculate standard deviation
            data_copy['bb_std'] = data_copy['close'].rolling(window=self.period).std()
            
            # Calculate upper and lower bands
            data_copy['bb_upper'] = data_copy['bb_middle'] + (data_copy['bb_std'] * self.std_dev)
            data_copy['bb_lower'] = data_copy['bb_middle'] - (data_copy['bb_std'] * self.std_dev)
            
            # Calculate band width and position
            data_copy['bb_width'] = data_copy['bb_upper'] - data_copy['bb_lower']
            data_copy['bb_position'] = (data_copy['close'] - data_copy['bb_lower']) / data_copy['bb_width']
            
            current_values = {
                'upper': data_copy['bb_upper'].iloc[-1] if not data_copy['bb_upper'].empty else None,
                'middle': data_copy['bb_middle'].iloc[-1] if not data_copy['bb_middle'].empty else None,
                'lower': data_copy['bb_lower'].iloc[-1] if not data_copy['bb_lower'].empty else None,
                'width': data_copy['bb_width'].iloc[-1] if not data_copy['bb_width'].empty else None,
                'position': data_copy['bb_position'].iloc[-1] if not data_copy['bb_position'].empty else None
            }
            
            return IndicatorResult(
                name=self.name,
                value=current_values,
                series=data_copy[['bb_upper', 'bb_middle', 'bb_lower']],
                metadata={'period': self.period, 'std_dev': self.std_dev}
            )
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return IndicatorResult(
                name=self.name,
                value=None,
                is_valid=False,
                error_message=str(e)
            )
    
    def get_required_columns(self) -> List[str]:
        """Get required columns for Bollinger Bands calculation."""
        return ['close']


class VolumeAnalyzer:
    """Volume analysis tools for market data."""
    
    @staticmethod
    def volume_sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate volume Simple Moving Average."""
        return data['volume'].rolling(window=period).mean()
    
    @staticmethod
    def volume_ratio(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate current volume to average volume ratio."""
        vol_sma = VolumeAnalyzer.volume_sma(data, period)
        return data['volume'] / vol_sma
    
    @staticmethod
    def cumulative_delta(data: pd.DataFrame) -> pd.Series:
        """
        Calculate cumulative delta (simplified version).
        Note: Real cumulative delta requires tick data with bid/ask info.
        """
        # Simplified approach using price movement and volume
        price_change = data['close'] - data['close'].shift(1)
        volume_delta = np.where(price_change > 0, data['volume'], -data['volume'])
        return pd.Series(volume_delta, index=data.index).cumsum()
    
    @staticmethod
    def volume_weighted_price(data: pd.DataFrame) -> pd.Series:
        """Calculate volume weighted price for each bar."""
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        return typical_price * data['volume']
    
    @staticmethod
    def on_balance_volume(data: pd.DataFrame) -> pd.Series:
        """Calculate On Balance Volume (OBV)."""
        price_change = data['close'] - data['close'].shift(1)
        obv_change = np.where(price_change > 0, data['volume'], 
                             np.where(price_change < 0, -data['volume'], 0))
        return pd.Series(obv_change, index=data.index).cumsum()


class TechnicalIndicatorsEngine:
    """Main engine for calculating multiple technical indicators."""
    
    def __init__(self):
        """Initialize technical indicators engine."""
        self.indicators: Dict[str, BaseIndicator] = {}
        self.results: Dict[str, IndicatorResult] = {}
        
    def add_indicator(self, name: str, indicator: BaseIndicator):
        """Add indicator to the engine."""
        self.indicators[name] = indicator
        
    def remove_indicator(self, name: str):
        """Remove indicator from the engine."""
        if name in self.indicators:
            del self.indicators[name]
        if name in self.results:
            del self.results[name]
    
    def calculate_all(self, data: pd.DataFrame) -> Dict[str, IndicatorResult]:
        """Calculate all registered indicators."""
        self.results = {}
        
        for name, indicator in self.indicators.items():
            try:
                result = indicator.calculate(data)
                self.results[name] = result
                
                if result.is_valid:
                    logger.debug(f"Calculated {name}: {result.value}")
                else:
                    logger.warning(f"Failed to calculate {name}: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"Error calculating {name}: {e}")
                self.results[name] = IndicatorResult(
                    name=name,
                    value=None,
                    is_valid=False,
                    error_message=str(e)
                )
        
        return self.results
    
    def get_indicator_value(self, name: str) -> Optional[float]:
        """Get current value for specific indicator."""
        if name in self.results and self.results[name].is_valid:
            return self.results[name].value
        return None
    
    def get_indicator_series(self, name: str) -> Optional[pd.Series]:
        """Get time series for specific indicator."""
        if name in self.results and self.results[name].is_valid:
            return self.results[name].series
        return None
    
    def create_default_suite(self) -> 'TechnicalIndicatorsEngine':
        """Create engine with default indicator suite for PDH/PDL strategy."""
        # VWAP for trend alignment
        self.add_indicator('vwap', VWAP(session_reset=True))
        
        # ATR for volatility measurement
        self.add_indicator('atr_14', ATR(period=14))
        
        # ADX for trend strength
        self.add_indicator('adx_14', ADX(period=14))
        
        # RSI for momentum
        self.add_indicator('rsi_14', RSI(period=14))
        
        # Moving averages for trend identification
        self.add_indicator('sma_20', MovingAverage(period=20, ma_type='sma'))
        self.add_indicator('ema_9', MovingAverage(period=9, ma_type='ema'))
        
        # Bollinger Bands for volatility and mean reversion
        self.add_indicator('bb_20', BollingerBands(period=20, std_dev=2.0))
        
        return self
    
    def get_signal_context(self, current_price: float) -> Dict[str, any]:
        """
        Get indicator context for signal generation.
        
        Args:
            current_price: Current market price
            
        Returns:
            Dictionary with indicator context for decision making
        """
        context = {
            'price': current_price,
            'indicators': {},
            'signals': {}
        }
        
        # Extract indicator values
        for name, result in self.results.items():
            if result.is_valid:
                context['indicators'][name] = result.value
        
        # Generate basic signals
        if 'vwap' in context['indicators'] and context['indicators']['vwap']:
            context['signals']['above_vwap'] = current_price > context['indicators']['vwap']
        
        if 'rsi_14' in context['indicators'] and context['indicators']['rsi_14']:
            rsi_value = context['indicators']['rsi_14']
            context['signals']['rsi_overbought'] = rsi_value > 70
            context['signals']['rsi_oversold'] = rsi_value < 30
        
        if 'adx_14' in context['indicators'] and context['indicators']['adx_14']:
            adx_value = context['indicators']['adx_14']
            context['signals']['strong_trend'] = adx_value > 25
            context['signals']['weak_trend'] = adx_value < 20
        
        return context
    
    def get_summary(self) -> Dict[str, any]:
        """Get summary of all indicator calculations."""
        summary = {
            'total_indicators': len(self.indicators),
            'successful': sum(1 for r in self.results.values() if r.is_valid),
            'failed': sum(1 for r in self.results.values() if not r.is_valid),
            'indicators': {}
        }
        
        for name, result in self.results.items():
            summary['indicators'][name] = {
                'value': result.value,
                'valid': result.is_valid,
                'error': result.error_message if not result.is_valid else None
            }
        
        return summary