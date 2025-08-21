"""
Phase 1 integration tests - Foundation setup validation.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Test imports to verify all modules load correctly
from src.database import init_database, close_database, MarketData, ReferenceLevel
from src.core import (
    Signal, SignalDirection, StrategyType, 
    PositionManager, RiskController, AccountInfo
)
from src.utils import setup_logging, get_logger
from config.strategy_config import ConfigManager, load_config


class TestPhase1Integration:
    """Integration tests for Phase 1 foundation setup."""
    
    def setup_method(self):
        """Setup for each test."""
        # Use temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup after each test."""
        # Cleanup temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_all_modules_import(self):
        """Test that all modules can be imported without errors."""
        # This test verifies the basic module structure
        assert True  # If we get here, imports worked
    
    def test_database_system_integration(self):
        """Test database system integration."""
        # Test database initialization with SQLite
        db_url = f"sqlite:///{self.temp_dir}/test.db"
        
        # Test direct database manager usage
        from src.database import DatabaseManager, MarketData
        db_manager = DatabaseManager(db_url)
        
        success = db_manager.initialize()
        assert success
        
        tables_created = db_manager.create_tables()
        assert tables_created
        
        # Test that we can create and query data
        with db_manager.get_session() as session:
            # Create test market data
            market_data = MarketData(
                symbol="ES",
                timestamp=datetime.now(),
                open_price=Decimal("4500.00"),
                high_price=Decimal("4505.00"),
                low_price=Decimal("4495.00"), 
                close_price=Decimal("4502.00"),
                volume=10000
            )
            
            session.add(market_data)
            session.flush()
            
            # Verify data was saved
            count = session.query(MarketData).count()
            assert count == 1
        
        db_manager.close()
    
    def test_core_system_integration(self):
        """Test core trading system integration."""
        # Create test configuration
        config = {
            'risk_percent': 0.01,
            'max_daily_loss_percent': 0.03,
            'max_positions': 3,
            'commission_per_contract': 2.50
        }
        
        # Test position manager
        position_manager = PositionManager(config)
        position_manager.set_account_limits(Decimal("50000"))
        
        # Test risk controller
        risk_controller = RiskController(config)
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"),
            day_pnl=Decimal("0"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        risk_controller.set_account_info(account)
        
        # Create test signal
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        # Test that systems work together
        can_open, reason = position_manager.can_open_position(signal, account)
        assert can_open
        
        symbol_specs = {'tick_value': 12.50, 'margin': 500}
        is_valid, risk_reason, risk_level = risk_controller.validate_new_position(
            signal, 1, account, symbol_specs
        )
        assert is_valid
    
    def test_configuration_system(self):
        """Test configuration management system."""
        # Create config manager with temp path
        config_path = os.path.join(self.temp_dir, "test_config.json")
        config_manager = ConfigManager(config_path)
        
        # Test loading default config
        config = config_manager.load_config()
        assert config is not None
        assert config.environment == "development"
        assert len(config.symbols) > 0
        
        # Test validation
        assert config_manager.validate_config()
        
        # Test that config file was created
        assert os.path.exists(config_path)
        
        # Test symbol config retrieval
        es_config = config_manager.get_symbol_config("ES")
        assert es_config is not None
        assert es_config.tick_value == 12.50
    
    def test_logging_system(self):
        """Test logging system setup."""
        log_dir = os.path.join(self.temp_dir, "logs")
        
        # Setup logging
        logger = setup_logging(
            log_level="INFO",
            log_dir=log_dir,
            console_output=False,  # Disable for testing
            file_output=True
        )
        
        assert logger is not None
        
        # Test logging
        logger.info("Test message")
        logger.error("Test error message")
        
        # Verify log files were created
        log_files = list(Path(log_dir).glob("*.log"))
        assert len(log_files) > 0
    
    def test_complete_system_workflow(self):
        """Test complete system workflow integration."""
        # Setup database with direct manager
        db_url = f"sqlite:///{self.temp_dir}/workflow_test.db"
        from src.database import DatabaseManager
        db_manager = DatabaseManager(db_url)
        assert db_manager.initialize()
        assert db_manager.create_tables()
        
        # Setup logging
        logger = setup_logging(
            log_level="INFO",
            log_dir=os.path.join(self.temp_dir, "logs"),
            console_output=False,
            file_output=True
        )
        
        # Load configuration
        config_path = os.path.join(self.temp_dir, "workflow_config.json")
        config_manager = ConfigManager(config_path)
        config = config_manager.load_config()
        
        # Setup trading systems
        position_manager = PositionManager(config.risk.__dict__)
        position_manager.set_account_limits(Decimal("50000"))
        
        risk_controller = RiskController(config.risk.__dict__)
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"), 
            day_pnl=Decimal("0"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        risk_controller.set_account_info(account)
        
        # Create and validate a signal
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        # Test complete workflow
        can_open, reason = position_manager.can_open_position(signal, account)
        assert can_open, f"Position check failed: {reason}"
        
        symbol_config = config.symbols["ES"]
        symbol_specs = {
            'tick_value': symbol_config.tick_value,
            'margin': symbol_config.margin_requirement,
            'is_micro': symbol_config.is_micro
        }
        
        is_valid, risk_reason, risk_level = risk_controller.validate_new_position(
            signal, 1, account, symbol_specs
        )
        assert is_valid, f"Risk validation failed: {risk_reason}"
        
        # Calculate position size
        position_size = position_manager.calculate_position_size(signal, account, symbol_specs)
        assert position_size > 0, "Position size calculation failed"
        
        # Log successful workflow
        logger.info(f"Complete workflow test successful - Position size: {position_size}")
        
        # Cleanup
        db_manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])