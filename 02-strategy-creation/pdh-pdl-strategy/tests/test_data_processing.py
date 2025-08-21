"""
Tests for data processing components - Phase 2.1 Market Data Handler.
"""

import pytest
import pandas as pd
import tempfile
import os
from datetime import datetime, date, time, timedelta
from decimal import Decimal

from src.data import (
    MarketDataHandler,
    DataFeedConfig,
    SimulationDataFeed,
    CSVDataFeed,
    MarketDataValidator,
    RTHSessionFilter,
    PDHPDLCalculator,
    PDHPDLLevels,
    PDHPDLManager
)

from src.database import init_database, close_database, DatabaseManager


class TestMarketDataValidator:
    """Test market data validation functionality."""
    
    def test_valid_ohlcv_bar(self):
        """Test validation of valid OHLCV bar."""
        valid_bar = {
            'open': 4500.0,
            'high': 4505.0,
            'low': 4495.0,
            'close': 4502.0,
            'volume': 1000
        }
        
        is_valid, message = MarketDataValidator.validate_ohlcv_bar(valid_bar)
        assert is_valid
        assert message == "Valid bar"
    
    def test_invalid_high_low(self):
        """Test validation with invalid high/low relationship."""
        invalid_bar = {
            'open': 4500.0,
            'high': 4490.0,  # High less than open
            'low': 4495.0,
            'close': 4502.0,
            'volume': 1000
        }
        
        is_valid, message = MarketDataValidator.validate_ohlcv_bar(invalid_bar)
        assert not is_valid
        assert "High" in message
    
    def test_missing_fields(self):
        """Test validation with missing required fields."""
        incomplete_bar = {
            'open': 4500.0,
            'high': 4505.0,
            # Missing 'low', 'close', 'volume'
        }
        
        is_valid, message = MarketDataValidator.validate_ohlcv_bar(incomplete_bar)
        assert not is_valid
        assert "Missing required field" in message
    
    def test_negative_volume(self):
        """Test validation with negative volume."""
        invalid_bar = {
            'open': 4500.0,
            'high': 4505.0,
            'low': 4495.0,
            'close': 4502.0,
            'volume': -100
        }
        
        is_valid, message = MarketDataValidator.validate_ohlcv_bar(invalid_bar)
        assert not is_valid
        assert "Negative volume" in message
    
    def test_clean_data(self):
        """Test data cleaning functionality."""
        dirty_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=10, freq='1min'),
            'open': [4500.0, 4501.0, None, 4503.0, 4504.0, 4505.0, 4506.0, 4507.0, 4508.0, 4509.0],
            'high': [4505.0, 4506.0, 4507.0, 4508.0, 4509.0, 4510.0, 4511.0, 4512.0, 4513.0, 4514.0],
            'low': [4495.0, 4496.0, 4497.0, 4498.0, 4499.0, 4500.0, 4501.0, 4502.0, 4503.0, 4504.0],
            'close': [4502.0, 4503.0, 4504.0, 4505.0, 4506.0, 4507.0, 4508.0, 4509.0, 4510.0, 4511.0],
            'volume': [1000, 1100, None, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        })
        
        cleaned = MarketDataValidator.clean_data(dirty_data)
        
        # Should remove row with None in OHLC
        assert len(cleaned) == 9
        
        # Should fill None volume with 0
        assert cleaned['volume'].isna().sum() == 0


class TestRTHSessionFilter:
    """Test RTH session filtering."""
    
    def setup_method(self):
        """Setup RTH filter for testing."""
        self.rth_filter = RTHSessionFilter()
    
    def test_filter_rth_data(self):
        """Test filtering for RTH hours."""
        # Create test data with both RTH and non-RTH times
        timestamps = [
            datetime(2024, 1, 15, 7, 30),   # Pre-market
            datetime(2024, 1, 15, 9, 30),   # RTH
            datetime(2024, 1, 15, 14, 30),  # RTH
            datetime(2024, 1, 15, 16, 30),  # After-hours
            datetime(2024, 1, 13, 10, 30),  # Saturday (should be excluded)
        ]
        
        test_data = pd.DataFrame({
            'timestamp': timestamps,
            'open': [4500, 4501, 4502, 4503, 4504],
            'high': [4505, 4506, 4507, 4508, 4509],
            'low': [4495, 4496, 4497, 4498, 4499],
            'close': [4502, 4503, 4504, 4505, 4506],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        rth_data = self.rth_filter.filter_rth_data(test_data)
        
        # Should only have 2 RTH bars (weekday RTH hours)
        assert len(rth_data) == 2
        
        # Check times are within RTH
        for timestamp in rth_data['timestamp']:
            time_part = timestamp.time()
            assert self.rth_filter.rth_start <= time_part <= self.rth_filter.rth_end
            assert timestamp.weekday() < 5  # Weekday
    
    def test_get_previous_trading_day(self):
        """Test getting previous trading day."""
        # Test Monday (should get Friday)
        monday = date(2024, 1, 15)  # Monday
        previous = self.rth_filter.get_previous_trading_day(monday)
        assert previous == date(2024, 1, 12)  # Friday
        
        # Test Tuesday (should get Monday)
        tuesday = date(2024, 1, 16)  # Tuesday
        previous = self.rth_filter.get_previous_trading_day(tuesday)
        assert previous == date(2024, 1, 15)  # Monday


class TestSimulationDataFeed:
    """Test simulation data feed."""
    
    def setup_method(self):
        """Setup simulation data feed."""
        config = DataFeedConfig(feed_type='simulation')
        self.feed = SimulationDataFeed(config)
    
    def test_connect_disconnect(self):
        """Test connection management."""
        assert not self.feed.is_connected()
        
        success = self.feed.connect()
        assert success
        assert self.feed.is_connected()
        
        self.feed.disconnect()
        assert not self.feed.is_connected()
    
    def test_get_current_bar(self):
        """Test getting current market data bar."""
        self.feed.connect()
        
        bar = self.feed.get_current_bar("ES")
        assert bar is not None
        assert bar.symbol == "ES"
        assert isinstance(bar.close_price, Decimal)
        assert bar.volume > 0
    
    def test_get_historical_data(self):
        """Test getting historical data."""
        self.feed.connect()
        
        start_date = date.today() - timedelta(days=2)
        end_date = date.today()
        
        data = self.feed.get_historical_data("ES", start_date, end_date)
        assert not data.empty
        assert 'timestamp' in data.columns
        assert 'close' in data.columns


class TestCSVDataFeed:
    """Test CSV data feed."""
    
    def setup_method(self):
        """Setup CSV data feed with temporary file."""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, 'test_data.csv')
        
        # Create test CSV data
        test_data = pd.DataFrame({
            'Date': ['2024-01-15', '2024-01-15', '2024-01-15'],
            'Time': ['09:30:00', '09:31:00', '09:32:00'],
            'Open': [4500.0, 4501.0, 4502.0],
            'High': [4505.0, 4506.0, 4507.0],
            'Low': [4495.0, 4496.0, 4497.0],
            'Close': [4502.0, 4503.0, 4504.0],
            'Volume': [1000, 1100, 1200]
        })
        test_data.to_csv(self.csv_file, index=False)
        
        config = DataFeedConfig(feed_type='csv', source_path=self.csv_file)
        self.feed = CSVDataFeed(config)
    
    def teardown_method(self):
        """Cleanup temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_connect_and_load(self):
        """Test connecting and loading CSV data."""
        assert not self.feed.is_connected()
        
        success = self.feed.connect()
        assert success
        assert self.feed.is_connected()
        assert self.feed.data is not None
        assert len(self.feed.data) == 3
    
    def test_get_current_bar(self):
        """Test getting current bar from CSV."""
        self.feed.connect()
        
        bar = self.feed.get_current_bar("ES")
        assert bar is not None
        assert bar.symbol == "ES"
        assert bar.close_price == Decimal('4504.0')  # Last row
    
    def test_get_historical_data(self):
        """Test getting historical data from CSV."""
        self.feed.connect()
        
        data = self.feed.get_historical_data("ES", date(2024, 1, 15), date(2024, 1, 15))
        assert not data.empty
        assert len(data) == 3


class TestMarketDataHandler:
    """Test main market data handler."""
    
    def setup_method(self):
        """Setup market data handler."""
        config = DataFeedConfig(feed_type='simulation')
        self.handler = MarketDataHandler(config)
        
        # Setup temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_url = f"sqlite:///{self.temp_dir}/test.db"
        self.db_manager = DatabaseManager(self.db_url)
        self.db_manager.initialize()
        self.db_manager.create_tables()
    
    def teardown_method(self):
        """Cleanup."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_connect_disconnect(self):
        """Test handler connection management."""
        assert not self.handler.is_connected()
        
        success = self.handler.connect()
        assert success
        assert self.handler.is_connected()
        
        self.handler.disconnect()
        assert not self.handler.is_connected()
    
    def test_get_current_data(self):
        """Test getting current market data with validation."""
        self.handler.connect()
        
        data = self.handler.get_current_data("ES")
        assert data is not None
        assert data.symbol == "ES"
        assert isinstance(data.close_price, Decimal)
    
    def test_get_historical_data(self):
        """Test getting historical data."""
        self.handler.connect()
        
        start_date = date.today() - timedelta(days=2)
        end_date = date.today()
        
        data = self.handler.get_historical_data("ES", start_date, end_date, rth_only=True)
        assert not data.empty
        
        # Test without RTH filter
        all_data = self.handler.get_historical_data("ES", start_date, end_date, rth_only=False)
        assert len(all_data) >= len(data)  # Should have more or equal data


class TestPDHPDLLevels:
    """Test PDH/PDL levels container."""
    
    def test_levels_creation(self):
        """Test creating PDH/PDL levels."""
        levels = PDHPDLLevels(
            symbol="ES",
            trade_date=date(2024, 1, 15),
            pdh=Decimal('4520.0'),
            pdl=Decimal('4480.0'),
            daily_range=Decimal('40.0'),
            midpoint=Decimal('4500.0')
        )
        
        assert levels.symbol == "ES"
        assert levels.pdh == Decimal('4520.0')
        assert levels.pdl == Decimal('4480.0')
        
        # Test calculated breakout levels
        assert levels.pdh_breakout_level == Decimal('4520.5')  # PDH + 2 ticks
        assert levels.pdl_breakout_level == Decimal('4479.5')  # PDL - 2 ticks
    
    def test_price_analysis_methods(self):
        """Test price analysis methods."""
        levels = PDHPDLLevels(
            symbol="ES",
            trade_date=date(2024, 1, 15),
            pdh=Decimal('4520.0'),
            pdl=Decimal('4480.0'),
            daily_range=Decimal('40.0'),
            midpoint=Decimal('4500.0')
        )
        
        # Test PDH analysis
        assert levels.is_above_pdh(Decimal('4525.0'))
        assert not levels.is_above_pdh(Decimal('4515.0'))
        
        # Test PDL analysis
        assert levels.is_below_pdl(Decimal('4475.0'))
        assert not levels.is_below_pdl(Decimal('4485.0'))
        
        # Test breakout analysis
        assert levels.is_breakout_long(Decimal('4525.0'))
        assert levels.is_breakout_short(Decimal('4475.0'))
        
        # Test range position
        range_pos = levels.get_range_position(Decimal('4500.0'))
        assert range_pos == 0.5  # Midpoint


class TestPDHPDLCalculator:
    """Test PDH/PDL calculator."""
    
    def setup_method(self):
        """Setup calculator and test data."""
        self.calculator = PDHPDLCalculator("ES")
        
        # Setup data handler
        config = DataFeedConfig(feed_type='simulation')
        self.data_handler = MarketDataHandler(config)
        self.data_handler.connect()
        
        # Setup database
        self.temp_dir = tempfile.mkdtemp()
        self.db_manager = DatabaseManager(f"sqlite:///{self.temp_dir}/test.db")
        self.db_manager.initialize()
        self.db_manager.create_tables()
    
    def teardown_method(self):
        """Cleanup."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_calculate_levels(self):
        """Test calculating PDH/PDL levels."""
        target_date = date.today()
        
        levels = self.calculator.calculate_levels(target_date, self.data_handler)
        assert levels is not None
        assert levels.symbol == "ES"
        assert levels.trade_date == target_date
        assert levels.pdh > levels.pdl
        assert levels.daily_range > 0
    
    def test_validate_levels(self):
        """Test level validation."""
        valid_levels = PDHPDLLevels(
            symbol="ES",
            trade_date=date(2024, 1, 15),
            pdh=Decimal('4520.0'),
            pdl=Decimal('4480.0'),
            daily_range=Decimal('40.0'),
            midpoint=Decimal('4500.0')
        )
        
        is_valid, message = self.calculator.validate_levels(valid_levels)
        assert is_valid
        assert message == "Valid levels"
        
        # Test invalid levels (PDH <= PDL)
        invalid_levels = PDHPDLLevels(
            symbol="ES",
            trade_date=date(2024, 1, 15),
            pdh=Decimal('4480.0'),
            pdl=Decimal('4520.0'),  # PDL > PDH
            daily_range=Decimal('40.0'),
            midpoint=Decimal('4500.0')
        )
        
        is_valid, message = self.calculator.validate_levels(invalid_levels)
        assert not is_valid
        assert "must be greater than" in message


class TestPDHPDLManager:
    """Test PDH/PDL manager for multiple symbols."""
    
    def setup_method(self):
        """Setup manager."""
        self.symbols = ["ES", "NQ"]
        self.manager = PDHPDLManager(self.symbols)
        
        # Setup data handler
        config = DataFeedConfig(feed_type='simulation')
        self.data_handler = MarketDataHandler(config)
        self.data_handler.connect()
    
    def test_calculate_all_levels(self):
        """Test calculating levels for all symbols."""
        target_date = date.today()
        
        results = self.manager.calculate_all_levels(target_date, self.data_handler)
        
        assert len(results) == 2
        assert "ES" in results
        assert "NQ" in results
        
        # Should have levels for both symbols
        for symbol in self.symbols:
            levels = results[symbol]
            if levels:  # May be None if calculation fails
                assert levels.symbol == symbol
                assert levels.trade_date == target_date


class TestPhase2Integration:
    """Integration tests for Phase 2.1 components."""
    
    def setup_method(self):
        """Setup integration test environment."""
        # Setup database
        self.temp_dir = tempfile.mkdtemp()
        self.db_manager = DatabaseManager(f"sqlite:///{self.temp_dir}/test.db")
        self.db_manager.initialize()
        self.db_manager.create_tables()
        
        # Setup data handler
        config = DataFeedConfig(feed_type='simulation')
        self.handler = MarketDataHandler(config)
        self.handler.connect()
        
        # Setup calculator
        self.calculator = PDHPDLCalculator("ES")
    
    def teardown_method(self):
        """Cleanup integration test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test complete data processing workflow."""
        # 1. Get historical data
        start_date = date.today() - timedelta(days=2)
        end_date = date.today()
        
        historical_data = self.handler.get_historical_data("ES", start_date, end_date)
        assert not historical_data.empty
        
        # 2. Calculate PDH/PDL levels
        levels = self.calculator.calculate_levels(date.today(), self.handler)
        assert levels is not None
        
        # 3. Validate levels
        is_valid, message = self.calculator.validate_levels(levels)
        assert is_valid
        
        # 4. Get current market data
        current_data = self.handler.get_current_data("ES")
        assert current_data is not None
        
        # 5. Test price analysis with current data
        if levels.is_above_pdh(current_data.close_price):
            assert current_data.close_price > levels.pdh
        
        if levels.is_below_pdl(current_data.close_price):
            assert current_data.close_price < levels.pdl


if __name__ == "__main__":
    pytest.main([__file__, "-v"])