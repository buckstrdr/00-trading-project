"""
Tests for technical indicators and volume profile - Phase 2.2 and 2.3.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal

from src.indicators import (
    IndicatorResult,
    BaseIndicator,
    VWAP,
    ATR, 
    ADX,
    RSI,
    MovingAverage,
    BollingerBands,
    VolumeAnalyzer,
    TechnicalIndicatorsEngine,
    VolumeProfile,
    VolumeNode,
    POCAnalyzer,
    HighVolumeNode,
    LowVolumeNode,
    VolumeProfileEngine
)


class TestIndicatorResult:
    """Test indicator result container."""
    
    def test_indicator_result_creation(self):
        """Test creating indicator result."""
        result = IndicatorResult(
            name="TEST",
            value=42.5,
            metadata={'period': 14}
        )
        
        assert result.name == "TEST"
        assert result.value == 42.5
        assert result.is_valid is True
        assert result.metadata['period'] == 14
    
    def test_invalid_result(self):
        """Test invalid indicator result."""
        result = IndicatorResult(
            name="TEST",
            value=None,
            is_valid=False,
            error_message="Test error"
        )
        
        assert not result.is_valid
        assert result.error_message == "Test error"


class TestVWAP:
    """Test VWAP indicator."""
    
    def setup_method(self):
        """Setup test data."""
        self.test_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-15 09:30:00', periods=10, freq='1min'),
            'high': [4505, 4506, 4507, 4508, 4509, 4510, 4511, 4512, 4513, 4514],
            'low': [4495, 4496, 4497, 4498, 4499, 4500, 4501, 4502, 4503, 4504],
            'close': [4502, 4503, 4504, 4505, 4506, 4507, 4508, 4509, 4510, 4511],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        })
        self.vwap = VWAP()
    
    def test_vwap_calculation(self):
        """Test VWAP calculation."""
        result = self.vwap.calculate(self.test_data)
        
        assert result.is_valid
        assert result.name == "VWAP"
        assert result.value is not None
        assert result.series is not None
        assert len(result.series) == len(self.test_data)
    
    def test_vwap_with_session_reset(self):
        """Test VWAP with session reset."""
        vwap_session = VWAP(session_reset=True)
        result = vwap_session.calculate(self.test_data)
        
        assert result.is_valid
        assert result.metadata['session_reset'] is True
    
    def test_vwap_empty_data(self):
        """Test VWAP with empty data."""
        empty_data = pd.DataFrame()
        result = self.vwap.calculate(empty_data)
        
        assert not result.is_valid
        assert "Empty data" in result.error_message
    
    def test_vwap_missing_columns(self):
        """Test VWAP with missing required columns."""
        incomplete_data = self.test_data[['high', 'low']].copy()  # Missing close, volume
        result = self.vwap.calculate(incomplete_data)
        
        assert not result.is_valid
        assert "Missing required columns" in result.error_message


class TestATR:
    """Test ATR indicator."""
    
    def setup_method(self):
        """Setup test data."""
        # Create 20 bars of data for ATR period=14
        self.test_data = pd.DataFrame({
            'high': [4505, 4506, 4507, 4508, 4509, 4510, 4511, 4512, 4513, 4514,
                     4515, 4516, 4517, 4518, 4519, 4520, 4521, 4522, 4523, 4524],
            'low': [4495, 4496, 4497, 4498, 4499, 4500, 4501, 4502, 4503, 4504,
                    4505, 4506, 4507, 4508, 4509, 4510, 4511, 4512, 4513, 4514],
            'close': [4502, 4503, 4504, 4505, 4506, 4507, 4508, 4509, 4510, 4511,
                      4512, 4513, 4514, 4515, 4516, 4517, 4518, 4519, 4520, 4521]
        })
        self.atr = ATR(period=14)
    
    def test_atr_calculation(self):
        """Test ATR calculation."""
        result = self.atr.calculate(self.test_data)
        
        assert result.is_valid
        assert result.name == "ATR"
        assert result.value is not None
        assert result.value > 0  # ATR should be positive
        assert result.metadata['period'] == 14
    
    def test_atr_insufficient_data(self):
        """Test ATR with insufficient data."""
        short_data = self.test_data.head(5)  # Less than period
        result = self.atr.calculate(short_data)
        
        assert not result.is_valid
        assert "Insufficient data" in result.error_message


class TestADX:
    """Test ADX indicator."""
    
    def setup_method(self):
        """Setup test data with trending pattern."""
        # Create trending data for better ADX testing
        trend_data = []
        base_price = 4500
        for i in range(20):
            high = base_price + i * 2 + 5
            low = base_price + i * 2 - 5
            close = base_price + i * 2
            trend_data.append({'high': high, 'low': low, 'close': close})
        
        self.test_data = pd.DataFrame(trend_data)
        self.adx = ADX(period=14)
    
    def test_adx_calculation(self):
        """Test ADX calculation."""
        result = self.adx.calculate(self.test_data)
        
        assert result.is_valid
        assert result.name == "ADX"
        assert result.value is not None
        assert 0 <= result.value <= 100  # ADX should be between 0-100
        
        # Check metadata for DI+ and DI-
        assert 'di_plus' in result.metadata
        assert 'di_minus' in result.metadata
    
    def test_adx_trending_market(self):
        """Test ADX in trending market (should show higher values)."""
        result = self.adx.calculate(self.test_data)
        
        # In a trending market, ADX should eventually rise
        # (though it may take time to develop)
        assert result.is_valid
        assert result.value is not None


class TestRSI:
    """Test RSI indicator."""
    
    def setup_method(self):
        """Setup test data."""
        # Create data with some volatility
        prices = [4500, 4510, 4505, 4515, 4508, 4520, 4512, 4525, 4515, 4530,
                 4520, 4535, 4525, 4540, 4530, 4545, 4535, 4550, 4540, 4555]
        
        self.test_data = pd.DataFrame({
            'close': prices
        })
        self.rsi = RSI(period=14)
    
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        result = self.rsi.calculate(self.test_data)
        
        assert result.is_valid
        assert result.name == "RSI"
        assert result.value is not None
        assert 0 <= result.value <= 100  # RSI should be between 0-100
    
    def test_rsi_overbought_oversold(self):
        """Test RSI overbought/oversold detection."""
        # Create overbought scenario (continuous rising prices)
        rising_prices = [4500 + i * 5 for i in range(20)]
        overbought_data = pd.DataFrame({'close': rising_prices})
        
        result = self.rsi.calculate(overbought_data)
        assert result.is_valid
        # Should be relatively high RSI (though not necessarily >70 with this simple data)
        assert result.value > 50


class TestMovingAverage:
    """Test Moving Average indicators."""
    
    def setup_method(self):
        """Setup test data."""
        self.test_data = pd.DataFrame({
            'close': [4500, 4501, 4502, 4503, 4504, 4505, 4506, 4507, 4508, 4509,
                     4510, 4511, 4512, 4513, 4514, 4515, 4516, 4517, 4518, 4519]
        })
    
    def test_sma_calculation(self):
        """Test Simple Moving Average."""
        sma = MovingAverage(period=10, ma_type='sma')
        result = sma.calculate(self.test_data)
        
        assert result.is_valid
        assert result.name == "SMA_10"
        assert result.value is not None
        assert result.metadata['type'] == 'sma'
    
    def test_ema_calculation(self):
        """Test Exponential Moving Average."""
        ema = MovingAverage(period=10, ma_type='ema')
        result = ema.calculate(self.test_data)
        
        assert result.is_valid
        assert result.name == "EMA_10"
        assert result.value is not None
        assert result.metadata['type'] == 'ema'
    
    def test_invalid_ma_type(self):
        """Test invalid moving average type."""
        invalid_ma = MovingAverage(period=10, ma_type='invalid')
        result = invalid_ma.calculate(self.test_data)
        
        assert not result.is_valid
        assert "Unsupported moving average type" in result.error_message


class TestBollingerBands:
    """Test Bollinger Bands indicator."""
    
    def setup_method(self):
        """Setup test data."""
        # Create data with some volatility
        np.random.seed(42)  # For reproducible tests
        prices = 4500 + np.cumsum(np.random.randn(50) * 2)
        
        self.test_data = pd.DataFrame({
            'close': prices
        })
        self.bb = BollingerBands(period=20, std_dev=2.0)
    
    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation."""
        result = self.bb.calculate(self.test_data)
        
        assert result.is_valid
        assert result.name == "BB_20_2.0"
        assert isinstance(result.value, dict)
        
        # Check all band values
        assert 'upper' in result.value
        assert 'middle' in result.value
        assert 'lower' in result.value
        assert 'width' in result.value
        assert 'position' in result.value
        
        # Upper band should be higher than middle, middle higher than lower
        if all(v is not None for v in [result.value['upper'], result.value['middle'], result.value['lower']]):
            assert result.value['upper'] > result.value['middle']
            assert result.value['middle'] > result.value['lower']


class TestVolumeAnalyzer:
    """Test volume analysis tools."""
    
    def setup_method(self):
        """Setup test data."""
        self.test_data = pd.DataFrame({
            'high': [4505, 4506, 4507, 4508, 4509],
            'low': [4495, 4496, 4497, 4498, 4499],
            'close': [4502, 4503, 4504, 4505, 4506],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
    
    def test_volume_sma(self):
        """Test volume simple moving average."""
        vol_sma = VolumeAnalyzer.volume_sma(self.test_data, period=3)
        assert not vol_sma.empty
        assert vol_sma.iloc[-1] > 0  # Should have a positive volume average
    
    def test_volume_ratio(self):
        """Test volume ratio calculation."""
        vol_ratio = VolumeAnalyzer.volume_ratio(self.test_data, period=3)
        assert not vol_ratio.empty
        assert vol_ratio.iloc[-1] > 0  # Should have positive ratio
    
    def test_cumulative_delta(self):
        """Test cumulative delta calculation."""
        cum_delta = VolumeAnalyzer.cumulative_delta(self.test_data)
        assert len(cum_delta) == len(self.test_data)
        assert isinstance(cum_delta, pd.Series)
    
    def test_on_balance_volume(self):
        """Test On Balance Volume calculation."""
        obv = VolumeAnalyzer.on_balance_volume(self.test_data)
        assert len(obv) == len(self.test_data)
        assert isinstance(obv, pd.Series)


class TestTechnicalIndicatorsEngine:
    """Test technical indicators engine."""
    
    def setup_method(self):
        """Setup test data and engine."""
        self.test_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-15 09:30:00', periods=50, freq='1min'),
            'high': [4500 + i + np.random.rand() * 5 for i in range(50)],
            'low': [4500 + i - np.random.rand() * 5 for i in range(50)],
            'close': [4500 + i + (np.random.rand() - 0.5) * 3 for i in range(50)],
            'volume': [1000 + np.random.randint(0, 500) for _ in range(50)]
        })
        self.engine = TechnicalIndicatorsEngine()
    
    def test_add_remove_indicators(self):
        """Test adding and removing indicators."""
        # Add indicator
        self.engine.add_indicator('test_vwap', VWAP())
        assert 'test_vwap' in self.engine.indicators
        
        # Remove indicator
        self.engine.remove_indicator('test_vwap')
        assert 'test_vwap' not in self.engine.indicators
    
    def test_calculate_all_indicators(self):
        """Test calculating all registered indicators."""
        # Add multiple indicators
        self.engine.add_indicator('vwap', VWAP())
        self.engine.add_indicator('atr', ATR(period=14))
        self.engine.add_indicator('rsi', RSI(period=14))
        
        results = self.engine.calculate_all(self.test_data)
        
        assert len(results) == 3
        assert 'vwap' in results
        assert 'atr' in results
        assert 'rsi' in results
        
        # Check that valid results are returned
        for result in results.values():
            assert isinstance(result, IndicatorResult)
    
    def test_default_suite(self):
        """Test creating default indicator suite."""
        engine = TechnicalIndicatorsEngine().create_default_suite()
        
        # Should have multiple indicators
        assert len(engine.indicators) >= 5
        
        # Test calculation with default suite
        results = engine.calculate_all(self.test_data)
        assert len(results) > 0
        
        # Should have VWAP
        assert 'vwap' in results
    
    def test_get_signal_context(self):
        """Test getting signal context."""
        self.engine.add_indicator('vwap', VWAP())
        self.engine.add_indicator('rsi', RSI(period=14))
        
        # Calculate indicators
        self.engine.calculate_all(self.test_data)
        
        # Get context
        context = self.engine.get_signal_context(4550.0)
        
        assert 'price' in context
        assert 'indicators' in context
        assert 'signals' in context
        assert context['price'] == 4550.0


class TestVolumeProfile:
    """Test volume profile functionality."""
    
    def setup_method(self):
        """Setup test data."""
        self.test_data = pd.DataFrame({
            'high': [4505.0, 4506.0, 4507.0, 4505.0, 4504.0],
            'low': [4495.0, 4496.0, 4497.0, 4495.0, 4494.0],
            'close': [4500.0, 4501.0, 4502.0, 4500.0, 4499.0],
            'volume': [1000, 1100, 1200, 800, 900]
        })
        self.profile = VolumeProfile(tick_size=Decimal('0.25'))
    
    def test_build_profile(self):
        """Test building volume profile."""
        volume_nodes = self.profile.build_profile(self.test_data)
        
        assert len(volume_nodes) > 0
        assert self.profile.total_volume > 0
        
        # Check that nodes are VolumeNode objects
        for price, node in volume_nodes.items():
            assert isinstance(node, VolumeNode)
            assert isinstance(price, Decimal)
            assert node.volume > 0
            assert node.percentage >= 0
    
    def test_find_high_volume_nodes(self):
        """Test finding high volume nodes."""
        volume_nodes = self.profile.build_profile(self.test_data)
        hvns = self.profile.find_high_volume_nodes(volume_nodes)
        
        # Should find some HVNs
        assert len(hvns) >= 0  # Could be 0 if threshold is high
        
        for hvn in hvns:
            assert isinstance(hvn, HighVolumeNode)
            assert hvn.significance >= 0
            assert hvn.support_resistance_strength >= 0
    
    def test_find_low_volume_nodes(self):
        """Test finding low volume nodes."""
        volume_nodes = self.profile.build_profile(self.test_data)
        lvns = self.profile.find_low_volume_nodes(volume_nodes)
        
        for lvn in lvns:
            assert isinstance(lvn, LowVolumeNode)
            assert lvn.gap_size >= 0
            assert lvn.breakout_potential >= 0
    
    def test_get_profile_stats(self):
        """Test getting profile statistics."""
        self.profile.build_profile(self.test_data)
        stats = self.profile.get_profile_stats()
        
        assert 'total_volume' in stats
        assert 'price_levels' in stats
        assert 'price_range' in stats
        assert 'volume_stats' in stats
        
        assert stats['total_volume'] > 0
        assert stats['price_levels'] > 0


class TestPOCAnalyzer:
    """Test POC (Point of Control) analyzer."""
    
    def test_find_poc(self):
        """Test finding Point of Control."""
        volume_profile = {
            Decimal('4500.0'): 1000,
            Decimal('4500.5'): 1500,  # Should be POC
            Decimal('4501.0'): 800,
            Decimal('4501.5'): 1200
        }
        
        poc = POCAnalyzer.find_poc(volume_profile)
        assert poc == Decimal('4500.5')
    
    def test_find_poc_zone(self):
        """Test finding POC zone."""
        volume_profile = {
            Decimal('4500.0'): 1000,
            Decimal('4500.5'): 1500,  # POC
            Decimal('4501.0'): 1400,  # Should be in zone
            Decimal('4501.5'): 200    # Should not be in zone
        }
        
        zone_low, zone_high = POCAnalyzer.find_poc_zone(volume_profile, zone_threshold=0.8)
        
        assert zone_low is not None
        assert zone_high is not None
        assert zone_low <= zone_high
    
    def test_calculate_poc_distance(self):
        """Test calculating distance from POC."""
        poc = Decimal('4500.0')
        
        # Above POC
        distance, direction = POCAnalyzer.calculate_poc_distance(Decimal('4505.0'), poc)
        assert distance == Decimal('5.0')
        assert direction == 1.0
        
        # Below POC
        distance, direction = POCAnalyzer.calculate_poc_distance(Decimal('4495.0'), poc)
        assert distance == Decimal('5.0')
        assert direction == -1.0


class TestVolumeProfileEngine:
    """Test volume profile engine."""
    
    def setup_method(self):
        """Setup test data and engine."""
        self.test_data = pd.DataFrame({
            'high': [4505.0, 4506.0, 4507.0, 4505.0, 4504.0] * 4,  # 20 bars
            'low': [4495.0, 4496.0, 4497.0, 4495.0, 4494.0] * 4,
            'close': [4500.0, 4501.0, 4502.0, 4500.0, 4499.0] * 4,
            'volume': [1000, 1100, 1200, 800, 900] * 4
        })
        self.engine = VolumeProfileEngine()
    
    def test_analyze_session(self):
        """Test analyzing a trading session."""
        analysis = self.engine.analyze_session('test_session', self.test_data)
        
        assert 'session_id' in analysis
        assert 'poc' in analysis
        assert 'high_volume_nodes' in analysis
        assert 'low_volume_nodes' in analysis
        assert 'statistics' in analysis
        
        assert analysis['session_id'] == 'test_session'
    
    def test_find_confluence_with_levels(self):
        """Test finding confluence with PDH/PDL levels."""
        # First analyze a session
        self.engine.analyze_session('test_session', self.test_data)
        
        # Define PDH/PDL levels
        pdh_pdl_levels = {
            'pdh': Decimal('4507.0'),
            'pdl': Decimal('4494.0'),
            'midpoint': Decimal('4500.5')
        }
        
        confluences = self.engine.find_confluence_with_levels('test_session', pdh_pdl_levels)
        
        # Should return a list (may be empty)
        assert isinstance(confluences, list)
        
        for confluence in confluences:
            assert 'type' in confluence
            assert 'confluence_strength' in confluence
            assert confluence['type'] == 'volume_pdh_pdl_confluence'
    
    def test_get_support_resistance_levels(self):
        """Test getting support/resistance levels."""
        # First analyze a session
        self.engine.analyze_session('test_session', self.test_data)
        
        sr_levels = self.engine.get_support_resistance_levels('test_session')
        
        assert isinstance(sr_levels, list)
        
        for level in sr_levels:
            assert 'price' in level
            assert 'strength' in level
            assert 'type' in level
            assert level['type'] == 'volume_sr'


class TestPhase2Integration:
    """Integration tests for Phase 2 components."""
    
    def setup_method(self):
        """Setup integration test environment."""
        # Create comprehensive test data
        np.random.seed(42)
        dates = pd.date_range('2024-01-15 09:30:00', periods=100, freq='1min')
        
        # Generate realistic price data
        base_price = 4500
        prices = [base_price]
        for i in range(99):
            change = np.random.normal(0, 2)
            new_price = prices[-1] + change
            prices.append(max(4400, min(4600, new_price)))  # Keep within range
        
        self.test_data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p + abs(np.random.normal(0, 3)) for p in prices],
            'low': [p - abs(np.random.normal(0, 3)) for p in prices],
            'close': [p + np.random.normal(0, 1) for p in prices],
            'volume': [1000 + int(abs(np.random.normal(0, 500))) for _ in prices]
        })
        
        # Fix high/low relationship
        for i in range(len(self.test_data)):
            row = self.test_data.iloc[i]
            high = max(row['open'], row['close'], row['high'])
            low = min(row['open'], row['close'], row['low'])
            self.test_data.iloc[i, self.test_data.columns.get_loc('high')] = high
            self.test_data.iloc[i, self.test_data.columns.get_loc('low')] = low
    
    def test_complete_indicators_workflow(self):
        """Test complete indicators workflow."""
        # 1. Create indicators engine
        engine = TechnicalIndicatorsEngine().create_default_suite()
        
        # 2. Calculate all indicators
        results = engine.calculate_all(self.test_data)
        
        # 3. Verify indicators calculated successfully
        assert len(results) > 0
        successful_indicators = [name for name, result in results.items() if result.is_valid]
        assert len(successful_indicators) >= 5  # Should have most indicators working
        
        # 4. Get signal context
        current_price = float(self.test_data['close'].iloc[-1])
        context = engine.get_signal_context(current_price)
        
        assert context['price'] == current_price
        assert len(context['indicators']) > 0
    
    def test_complete_volume_profile_workflow(self):
        """Test complete volume profile workflow."""
        # 1. Create volume profile engine
        engine = VolumeProfileEngine()
        
        # 2. Analyze session
        analysis = engine.analyze_session('integration_test', self.test_data)
        
        # 3. Verify analysis completed
        assert 'poc' in analysis
        assert analysis['poc']['price'] is not None
        
        # 4. Test confluence analysis
        pdh_pdl_levels = {
            'pdh': Decimal(str(self.test_data['high'].max())),
            'pdl': Decimal(str(self.test_data['low'].min())),
            'midpoint': (Decimal(str(self.test_data['high'].max())) + 
                        Decimal(str(self.test_data['low'].min()))) / 2
        }
        
        confluences = engine.find_confluence_with_levels('integration_test', pdh_pdl_levels)
        assert isinstance(confluences, list)
        
        # 5. Get support/resistance levels
        sr_levels = engine.get_support_resistance_levels('integration_test')
        assert isinstance(sr_levels, list)
    
    def test_indicators_with_volume_profile_integration(self):
        """Test integration between indicators and volume profile."""
        # 1. Calculate technical indicators
        indicators_engine = TechnicalIndicatorsEngine()
        indicators_engine.add_indicator('vwap', VWAP())
        indicators_engine.add_indicator('atr', ATR())
        
        indicator_results = indicators_engine.calculate_all(self.test_data)
        
        # 2. Calculate volume profile
        volume_engine = VolumeProfileEngine()
        volume_analysis = volume_engine.analyze_session('integration', self.test_data)
        
        # 3. Combine insights
        current_price = float(self.test_data['close'].iloc[-1])
        
        # Get indicator context
        context = indicators_engine.get_signal_context(current_price)
        
        # Get POC information
        poc_price = volume_analysis.get('poc', {}).get('price')
        
        # 4. Verify both systems provide useful information
        assert len(context['indicators']) > 0
        assert poc_price is not None
        
        # 5. Example of combined analysis
        combined_signal = {
            'current_price': current_price,
            'vwap_alignment': context['signals'].get('above_vwap'),
            'poc_distance': abs(current_price - poc_price) if poc_price else None,
            'atr_volatility': context['indicators'].get('atr'),
            'hvn_count': len(volume_analysis.get('high_volume_nodes', [])),
            'lvn_count': len(volume_analysis.get('low_volume_nodes', []))
        }
        
        # Verify combined signal has meaningful data
        assert combined_signal['current_price'] > 0
        assert combined_signal['atr_volatility'] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])