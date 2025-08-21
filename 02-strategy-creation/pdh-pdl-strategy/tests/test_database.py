"""
Test suite for database functionality.
"""

import pytest
import tempfile
import os
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import (
    DatabaseManager, MarketData, ReferenceLevel, Trade, 
    PerformanceMetrics, SystemLog, Base, init_database
)


class TestDatabaseManager:
    """Test database manager functionality."""
    
    def setup_method(self):
        """Setup test database for each test."""
        # Use in-memory SQLite for testing
        self.test_db_url = "sqlite:///:memory:"
        self.db_manager = DatabaseManager(self.test_db_url)
        assert self.db_manager.initialize()
        assert self.db_manager.create_tables()
    
    def teardown_method(self):
        """Cleanup after each test."""
        if self.db_manager.engine:
            self.db_manager.close()
    
    def test_database_initialization(self):
        """Test database initialization."""
        assert self.db_manager.engine is not None
        assert self.db_manager.SessionLocal is not None
        assert self.db_manager.health_check()
    
    def test_market_data_operations(self):
        """Test market data CRUD operations."""
        with self.db_manager.get_session() as session:
            # Create market data
            market_data = MarketData(
                symbol="ES",
                timestamp=datetime(2024, 1, 15, 10, 30),
                open_price=Decimal("4500.25"),
                high_price=Decimal("4505.75"),
                low_price=Decimal("4498.50"),
                close_price=Decimal("4502.00"),
                volume=12500
            )
            
            session.add(market_data)
            session.flush()
            
            # Verify data was saved
            assert market_data.id is not None
            
            # Query data
            queried = session.query(MarketData).filter(
                MarketData.symbol == "ES"
            ).first()
            
            assert queried is not None
            assert queried.symbol == "ES"
            assert queried.close_price == Decimal("4502.00")
    
    def test_reference_level_operations(self):
        """Test PDH/PDL reference level operations."""
        with self.db_manager.get_session() as session:
            # Create reference level
            ref_level = ReferenceLevel(
                symbol="ES",
                trade_date=date(2024, 1, 15),
                pdh=Decimal("4510.50"),
                pdl=Decimal("4485.25"),
                daily_range=Decimal("25.25"),
                poc=Decimal("4500.00")
            )
            
            session.add(ref_level)
            session.flush()
            
            # Test midpoint calculation
            assert ref_level.midpoint == Decimal("4497.875")
            
            # Query the saved data to verify it exists
            queried = session.query(ReferenceLevel).filter(
                ReferenceLevel.symbol == "ES",
                ReferenceLevel.trade_date == date(2024, 1, 15)
            ).first()
            
            assert queried is not None
            assert queried.pdh == Decimal("4510.50")
            assert queried.poc == Decimal("4500.00")
    
    def test_trade_operations(self):
        """Test trade logging operations."""
        with self.db_manager.get_session() as session:
            # Create trade
            trade = Trade(
                symbol="ES",
                strategy_type="breakout",
                direction="LONG",
                entry_timestamp=datetime(2024, 1, 15, 10, 30),
                entry_price=Decimal("4502.00"),
                quantity=1,
                stop_loss=Decimal("4495.00")
            )
            
            session.add(trade)
            session.flush()
            
            # Test trade properties
            assert trade.is_open
            assert trade.duration_minutes is None
            
            # Update trade with exit
            trade.exit_timestamp = datetime(2024, 1, 15, 11, 15)
            trade.exit_price = Decimal("4510.00")
            trade.status = "CLOSED"
            trade.pnl = trade.calculate_pnl(Decimal("12.50"))  # ES tick value
            
            session.flush()
            
            # Test updated properties
            assert not trade.is_open
            assert trade.duration_minutes == 45
            assert trade.is_winner
            assert trade.pnl > 0
    
    def test_performance_metrics(self):
        """Test performance metrics calculations."""
        with self.db_manager.get_session() as session:
            # Create performance metrics
            metrics = PerformanceMetrics(
                date=date(2024, 1, 15),
                symbol="ES",
                total_trades=10,
                winning_trades=6,
                losing_trades=4,
                gross_profit=Decimal("1500.00"),
                gross_loss=Decimal("800.00"),
                net_profit=Decimal("700.00")
            )
            
            session.add(metrics)
            session.flush()
            
            # Test calculated properties
            assert metrics.win_rate == 60.0
    
    def test_system_logging(self):
        """Test system logging functionality."""
        with self.db_manager.get_session() as session:
            # Create log entry
            log_entry = SystemLog(
                level="INFO",
                message="Test log message",
                module="test_module",
                function="test_function"
            )
            
            session.add(log_entry)
            session.flush()
            
            # Verify log was saved
            assert log_entry.id is not None
            assert log_entry.timestamp is not None


class TestDatabaseIntegration:
    """Integration tests for database functionality."""
    
    def test_init_database_function(self):
        """Test the init_database function."""
        # This will use the default database configuration
        # In a real test environment, you'd mock this
        pass  # Skip for now as it requires actual DB setup


if __name__ == "__main__":
    pytest.main([__file__, "-v"])