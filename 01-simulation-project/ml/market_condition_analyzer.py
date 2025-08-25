#!/usr/bin/env python3
"""
Market Condition Analyzer - Phase 4A Implementation
TSX Strategy Bridge ML Optimization Framework

Purpose: Advanced market regime detection and condition analysis
- Multi-timeframe trend analysis
- Volatility regime classification
- Volume pattern recognition
- Seasonal component analysis
- Market correlation analysis
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import json

# Statistical and ML imports
try:
    from scipy import stats
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False
    print("Warning: ML libraries not available. Using simplified analysis.")

# Add project paths
project_root = Path(__file__).parent.parent


class TrendRegime(Enum):
    """Trend regime classifications"""
    STRONG_UPTREND = "strong_uptrend"
    WEAK_UPTREND = "weak_uptrend"  
    SIDEWAYS = "sideways"
    WEAK_DOWNTREND = "weak_downtrend"
    STRONG_DOWNTREND = "strong_downtrend"
    UNKNOWN = "unknown"


class VolatilityRegime(Enum):
    """Volatility regime classifications"""
    VERY_LOW = "very_low"      # < 10th percentile
    LOW = "low"                # 10-30th percentile
    NORMAL = "normal"          # 30-70th percentile
    HIGH = "high"              # 70-90th percentile
    VERY_HIGH = "very_high"    # > 90th percentile
    UNKNOWN = "unknown"


class VolumeRegime(Enum):
    """Volume regime classifications"""
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"
    UNKNOWN = "unknown"


@dataclass
class MarketCondition:
    """Comprehensive market condition analysis"""
    symbol: str
    period: str
    timestamp: datetime.datetime
    
    # Trend analysis
    trend_regime: TrendRegime
    trend_strength: float  # 0-1, strength of trend
    trend_direction: str   # 'bullish', 'bearish', 'neutral'
    
    # Volatility analysis
    volatility_regime: VolatilityRegime
    volatility_value: float  # Annualized volatility
    volatility_percentile: float  # Historical percentile
    
    # Volume analysis
    volume_regime: VolumeRegime
    volume_trend: str  # 'increasing', 'decreasing', 'stable'
    
    # Price patterns
    price_range_pct: float  # High-low range as % of close
    momentum_score: float   # Price momentum indicator
    
    # Statistical measures
    autocorrelation: float  # Price autocorrelation
    mean_reversion_score: float  # Mean reversion tendency
    
    # Market microstructure  
    bid_ask_spread_proxy: float  # Estimated from OHLC
    market_efficiency_score: float  # Price efficiency measure
    
    # Additional features
    total_bars: int
    data_quality_score: float  # 0-1, quality of underlying data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ML processing"""
        return {
            'symbol': self.symbol,
            'period': self.period,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'trend_regime': self.trend_regime.value,
            'trend_strength': self.trend_strength,
            'trend_direction': self.trend_direction,
            'volatility_regime': self.volatility_regime.value,
            'volatility_value': self.volatility_value,
            'volatility_percentile': self.volatility_percentile,
            'volume_regime': self.volume_regime.value,
            'volume_trend': self.volume_trend,
            'price_range_pct': self.price_range_pct,
            'momentum_score': self.momentum_score,
            'autocorrelation': self.autocorrelation,
            'mean_reversion_score': self.mean_reversion_score,
            'bid_ask_spread_proxy': self.bid_ask_spread_proxy,
            'market_efficiency_score': self.market_efficiency_score,
            'total_bars': self.total_bars,
            'data_quality_score': self.data_quality_score
        }


class TechnicalIndicators:
    """Technical analysis indicators for market condition analysis"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
        
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
        
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
        
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
        
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram


class MarketConditionAnalyzer:
    """Advanced market regime detection and condition analysis"""
    
    def __init__(self, historical_lookback: int = 252):
        """
        Initialize analyzer
        
        Args:
            historical_lookback: Days of historical data for percentile calculations
        """
        self.historical_lookback = historical_lookback
        self.logger = self._setup_logging()
        self.indicators = TechnicalIndicators()
        
        # Historical data for regime classification
        self.historical_volatility = {}
        self.historical_volume = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for analyzer"""
        logger = logging.getLogger('MarketConditionAnalyzer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def analyze_comprehensive_conditions(self, 
                                       data: pd.DataFrame, 
                                       symbol: str, 
                                       period: str = None) -> MarketCondition:
        """
        Perform comprehensive market condition analysis
        
        Args:
            data: OHLCV DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
            symbol: Trading symbol
            period: Analysis period identifier
            
        Returns:
            MarketCondition object with comprehensive analysis
        """
        try:
            if data.empty or len(data) < 20:
                return self._default_market_condition(symbol, period)
                
            # Ensure required columns exist
            data = self._validate_and_clean_data(data)
            
            # Core analysis components
            trend_analysis = self._analyze_trend(data)
            volatility_analysis = self._analyze_volatility(data, symbol)
            volume_analysis = self._analyze_volume(data, symbol)
            pattern_analysis = self._analyze_price_patterns(data)
            microstructure_analysis = self._analyze_market_microstructure(data)
            
            # Create comprehensive market condition
            condition = MarketCondition(
                symbol=symbol,
                period=period or f"{len(data)}_bars",
                timestamp=datetime.datetime.now(),
                
                # Trend components
                trend_regime=trend_analysis['regime'],
                trend_strength=trend_analysis['strength'],
                trend_direction=trend_analysis['direction'],
                
                # Volatility components
                volatility_regime=volatility_analysis['regime'],
                volatility_value=volatility_analysis['value'],
                volatility_percentile=volatility_analysis['percentile'],
                
                # Volume components
                volume_regime=volume_analysis['regime'],
                volume_trend=volume_analysis['trend'],
                
                # Pattern components
                price_range_pct=pattern_analysis['range_pct'],
                momentum_score=pattern_analysis['momentum'],
                
                # Statistical components
                autocorrelation=pattern_analysis['autocorr'],
                mean_reversion_score=pattern_analysis['mean_reversion'],
                
                # Microstructure components
                bid_ask_spread_proxy=microstructure_analysis['spread_proxy'],
                market_efficiency_score=microstructure_analysis['efficiency'],
                
                # Metadata
                total_bars=len(data),
                data_quality_score=self._assess_data_quality(data)
            )
            
            self.logger.info(f"Analyzed market conditions for {symbol}: {condition.trend_regime.value}, Vol: {condition.volatility_regime.value}")
            
            return condition
            
        except Exception as e:
            self.logger.error(f"Error analyzing market conditions for {symbol}: {e}")
            return self._default_market_condition(symbol, period)
            
    def _validate_and_clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean OHLCV data"""
        # Required columns
        required_cols = ['open', 'high', 'low', 'close']
        
        # Add missing columns with defaults
        for col in required_cols:
            if col not in data.columns:
                if col == 'open':
                    data['open'] = data.get('close', 0)
                elif col == 'high':
                    data['high'] = data.get('close', 0)
                elif col == 'low':
                    data['low'] = data.get('close', 0)
                    
        # Add volume if missing
        if 'volume' not in data.columns:
            data['volume'] = 1000  # Default volume
            
        # Clean data
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.fillna(method='forward').fillna(method='backward')
        
        return data
        
    def _analyze_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trend regime and characteristics"""
        close = data['close']
        
        # Multiple timeframe moving averages
        sma_10 = self.indicators.sma(close, 10)
        sma_20 = self.indicators.sma(close, 20)
        sma_50 = self.indicators.sma(close, 50) if len(data) >= 50 else sma_20
        
        # MACD analysis
        macd_line, signal_line, histogram = self.indicators.macd(close)
        
        # Trend strength calculation
        try:
            # Price vs moving averages
            price_above_sma20 = (close.iloc[-1] > sma_20.iloc[-1]) if not sma_20.empty else False
            price_above_sma50 = (close.iloc[-1] > sma_50.iloc[-1]) if not sma_50.empty else False
            
            # Moving average alignment
            ma_alignment = 0
            if not sma_10.empty and not sma_20.empty:
                ma_alignment += 1 if sma_10.iloc[-1] > sma_20.iloc[-1] else -1
            if not sma_20.empty and not sma_50.empty:
                ma_alignment += 1 if sma_20.iloc[-1] > sma_50.iloc[-1] else -1
                
            # MACD confirmation
            macd_bullish = (macd_line.iloc[-1] > signal_line.iloc[-1]) if not macd_line.empty else False
            
            # Overall trend strength (0-1)
            strength_factors = []
            if price_above_sma20:
                strength_factors.append(0.3)
            if price_above_sma50:
                strength_factors.append(0.3)
            if ma_alignment > 0:
                strength_factors.append(0.2)
            if macd_bullish:
                strength_factors.append(0.2)
                
            trend_strength = sum(strength_factors)
            
            # Direction
            price_change = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20] if len(close) >= 20 else 0
            
            if price_change > 0.05 and trend_strength > 0.6:
                direction = 'bullish'
                regime = TrendRegime.STRONG_UPTREND
            elif price_change > 0.02 and trend_strength > 0.4:
                direction = 'bullish' 
                regime = TrendRegime.WEAK_UPTREND
            elif price_change < -0.05 and trend_strength > 0.6:
                direction = 'bearish'
                regime = TrendRegime.STRONG_DOWNTREND
            elif price_change < -0.02 and trend_strength > 0.4:
                direction = 'bearish'
                regime = TrendRegime.WEAK_DOWNTREND
            else:
                direction = 'neutral'
                regime = TrendRegime.SIDEWAYS
                
        except Exception as e:
            self.logger.warning(f"Error in trend analysis: {e}")
            trend_strength = 0.0
            direction = 'neutral'
            regime = TrendRegime.UNKNOWN
            
        return {
            'strength': trend_strength,
            'direction': direction,
            'regime': regime
        }
        
    def _analyze_volatility(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Analyze volatility regime"""
        close = data['close']
        
        try:
            # Calculate daily returns
            returns = close.pct_change().dropna()
            
            if len(returns) < 10:
                return {
                    'regime': VolatilityRegime.UNKNOWN,
                    'value': 0.0,
                    'percentile': 50.0
                }
                
            # Annualized volatility
            volatility = returns.std() * np.sqrt(252)  # Assuming daily data
            
            # Historical percentile (simplified)
            if symbol in self.historical_volatility:
                hist_vol = self.historical_volatility[symbol]
                percentile = stats.percentileofscore(hist_vol, volatility)
            else:
                # Use current dataset for percentile
                rolling_vol = returns.rolling(window=20).std() * np.sqrt(252)
                percentile = stats.percentileofscore(rolling_vol.dropna(), volatility)
                
            # Classify regime
            if percentile < 10:
                regime = VolatilityRegime.VERY_LOW
            elif percentile < 30:
                regime = VolatilityRegime.LOW
            elif percentile < 70:
                regime = VolatilityRegime.NORMAL
            elif percentile < 90:
                regime = VolatilityRegime.HIGH
            else:
                regime = VolatilityRegime.VERY_HIGH
                
        except Exception as e:
            self.logger.warning(f"Error in volatility analysis: {e}")
            volatility = 0.0
            percentile = 50.0
            regime = VolatilityRegime.UNKNOWN
            
        return {
            'regime': regime,
            'value': volatility,
            'percentile': percentile
        }
        
    def _analyze_volume(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Analyze volume patterns"""
        volume = data['volume']
        
        try:
            if len(volume) < 10:
                return {
                    'regime': VolumeRegime.UNKNOWN,
                    'trend': 'unknown'
                }
                
            # Volume moving averages
            volume_sma20 = volume.rolling(20).mean()
            current_volume = volume.iloc[-5:].mean()  # Recent average
            
            # Volume trend
            if not volume_sma20.empty:
                if current_volume > volume_sma20.iloc[-1] * 1.2:
                    volume_trend = 'increasing'
                elif current_volume < volume_sma20.iloc[-1] * 0.8:
                    volume_trend = 'decreasing'
                else:
                    volume_trend = 'stable'
            else:
                volume_trend = 'unknown'
                
            # Volume regime classification (simplified)
            avg_volume = volume.mean()
            
            if current_volume > avg_volume * 2:
                regime = VolumeRegime.VERY_HIGH
            elif current_volume > avg_volume * 1.5:
                regime = VolumeRegime.HIGH
            elif current_volume > avg_volume * 0.7:
                regime = VolumeRegime.NORMAL
            elif current_volume > avg_volume * 0.3:
                regime = VolumeRegime.LOW
            else:
                regime = VolumeRegime.VERY_LOW
                
        except Exception as e:
            self.logger.warning(f"Error in volume analysis: {e}")
            regime = VolumeRegime.UNKNOWN
            volume_trend = 'unknown'
            
        return {
            'regime': regime,
            'trend': volume_trend
        }
        
    def _analyze_price_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price patterns and statistical properties"""
        close = data['close']
        high = data['high']
        low = data['low']
        
        try:
            # Price range analysis
            price_range_pct = ((high.max() - low.min()) / close.mean()) * 100
            
            # Momentum score (simplified)
            if len(close) >= 10:
                momentum = (close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]
                momentum_score = max(-1, min(1, momentum * 10))  # Normalize to -1 to 1
            else:
                momentum_score = 0.0
                
            # Autocorrelation analysis
            returns = close.pct_change().dropna()
            if len(returns) >= 20:
                autocorr = returns.autocorr(lag=1)
                autocorr = autocorr if not np.isnan(autocorr) else 0.0
            else:
                autocorr = 0.0
                
            # Mean reversion score (using Bollinger Bands)
            if len(close) >= 20:
                upper, middle, lower = self.indicators.bollinger_bands(close, 20, 2)
                
                # Check how often price reverts from extreme levels
                upper_touches = (close > upper).sum()
                lower_touches = (close < lower).sum()
                total_touches = upper_touches + lower_touches
                
                if total_touches > 0:
                    # Simple mean reversion score
                    mean_reversion_score = min(1.0, total_touches / (len(close) * 0.1))
                else:
                    mean_reversion_score = 0.0
            else:
                mean_reversion_score = 0.0
                
        except Exception as e:
            self.logger.warning(f"Error in pattern analysis: {e}")
            price_range_pct = 0.0
            momentum_score = 0.0
            autocorr = 0.0
            mean_reversion_score = 0.0
            
        return {
            'range_pct': price_range_pct,
            'momentum': momentum_score,
            'autocorr': autocorr,
            'mean_reversion': mean_reversion_score
        }
        
    def _analyze_market_microstructure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market microstructure proxies"""
        try:
            high = data['high']
            low = data['low']
            close = data['close']
            
            # Bid-ask spread proxy using high-low spread
            hl_spread = (high - low).mean()
            spread_proxy = hl_spread / close.mean() if close.mean() > 0 else 0
            
            # Market efficiency proxy (price impact/randomness)
            returns = close.pct_change().dropna()
            if len(returns) >= 30:
                # Measure of price efficiency (lower = more efficient)
                efficiency_score = 1.0 - min(1.0, abs(returns.mean()) * 100)
            else:
                efficiency_score = 0.5  # Neutral
                
        except Exception as e:
            self.logger.warning(f"Error in microstructure analysis: {e}")
            spread_proxy = 0.0
            efficiency_score = 0.5
            
        return {
            'spread_proxy': spread_proxy,
            'efficiency': efficiency_score
        }
        
    def _assess_data_quality(self, data: pd.DataFrame) -> float:
        """Assess quality of underlying data"""
        try:
            quality_score = 1.0
            
            # Check for missing values
            missing_pct = data.isnull().sum().sum() / (len(data) * len(data.columns))
            quality_score -= missing_pct * 0.5
            
            # Check for zero values in price data
            price_cols = ['open', 'high', 'low', 'close']
            zero_prices = sum((data[col] == 0).sum() for col in price_cols if col in data.columns)
            if zero_prices > 0:
                quality_score -= 0.2
                
            # Check for consistent OHLC relationships
            if all(col in data.columns for col in price_cols):
                inconsistent = ((data['high'] < data['low']) | 
                               (data['high'] < data['close']) |
                               (data['low'] > data['close'])).sum()
                if inconsistent > 0:
                    quality_score -= 0.3
                    
            return max(0.0, min(1.0, quality_score))
            
        except Exception:
            return 0.5  # Neutral score on error
            
    def _default_market_condition(self, symbol: str, period: str = None) -> MarketCondition:
        """Return default market condition for error cases"""
        return MarketCondition(
            symbol=symbol,
            period=period or "unknown",
            timestamp=datetime.datetime.now(),
            trend_regime=TrendRegime.UNKNOWN,
            trend_strength=0.0,
            trend_direction='unknown',
            volatility_regime=VolatilityRegime.UNKNOWN,
            volatility_value=0.0,
            volatility_percentile=50.0,
            volume_regime=VolumeRegime.UNKNOWN,
            volume_trend='unknown',
            price_range_pct=0.0,
            momentum_score=0.0,
            autocorrelation=0.0,
            mean_reversion_score=0.0,
            bid_ask_spread_proxy=0.0,
            market_efficiency_score=0.5,
            total_bars=0,
            data_quality_score=0.0
        )
        
    def save_analysis(self, condition: MarketCondition, output_path: str = None):
        """Save market condition analysis to file"""
        if not output_path:
            output_path = project_root / "ml" / f"market_analysis_{condition.symbol}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(condition.to_dict(), f, indent=2)
                
            self.logger.info(f"Saved market analysis to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis: {e}")


def main():
    """Test market condition analyzer"""
    print("=== Market Condition Analyzer Test ===")
    
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-08-01', end='2023-08-31', freq='H')
    
    # Generate realistic price data
    base_price = 100.0
    prices = [base_price]
    
    for i in range(len(dates) - 1):
        # Random walk with slight trend
        change = np.random.normal(0.001, 0.02)
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
        
    sample_data = pd.DataFrame({
        'datetime': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': [1000 + np.random.randint(-200, 200) for _ in prices]
    })
    
    # Initialize analyzer
    analyzer = MarketConditionAnalyzer()
    
    # Analyze conditions
    condition = analyzer.analyze_comprehensive_conditions(sample_data, 'TEST', '2023-08-01_2023-08-31')
    
    print(f"\nMarket Condition Analysis Results:")
    print(f"Symbol: {condition.symbol}")
    print(f"Trend Regime: {condition.trend_regime.value}")
    print(f"Trend Strength: {condition.trend_strength:.3f}")
    print(f"Volatility Regime: {condition.volatility_regime.value}")
    print(f"Volatility Value: {condition.volatility_value:.3f}")
    print(f"Volume Regime: {condition.volume_regime.value}")
    print(f"Momentum Score: {condition.momentum_score:.3f}")
    print(f"Mean Reversion Score: {condition.mean_reversion_score:.3f}")
    print(f"Data Quality: {condition.data_quality_score:.3f}")
    
    # Save analysis
    analyzer.save_analysis(condition)
    
    print(f"\nAnalysis completed for {condition.total_bars} data points")


if __name__ == "__main__":
    main()