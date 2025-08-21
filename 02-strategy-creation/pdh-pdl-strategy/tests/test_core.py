"""
Test suite for core trading system components.
"""

import pytest
from datetime import datetime, time
from decimal import Decimal
from unittest.mock import Mock, patch

from src.core import (
    Signal, SignalDirection, StrategyType, MarketData, ReferenceLevel,
    PositionManager, PositionSizer, Position, AccountInfo,
    RiskController, RiskLevel
)


class TestSignalAndMarketData:
    """Test signal and market data structures."""
    
    def test_signal_creation(self):
        """Test signal creation and properties."""
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00"),
            target_price=Decimal("4515.00"),
            confidence=0.8
        )
        
        assert signal.direction == SignalDirection.LONG
        assert signal.symbol == "ES"
        assert signal.entry_price == Decimal("4502.00")
        assert signal.timestamp is not None
    
    def test_market_data_structure(self):
        """Test market data container."""
        market_data = MarketData(
            symbol="ES",
            timestamp=datetime.now(),
            open_price=Decimal("4500.00"),
            high_price=Decimal("4505.00"),
            low_price=Decimal("4495.00"),
            close_price=Decimal("4502.00"),
            volume=10000,
            vwap=Decimal("4501.00"),
            atr=Decimal("15.50")
        )
        
        assert market_data.symbol == "ES"
        assert market_data.volume == 10000
        assert market_data.vwap == Decimal("4501.00")


class TestPositionSizer:
    """Test position sizing calculations."""
    
    def setup_method(self):
        """Setup for position sizer tests."""
        self.config = {
            'risk_percent': 0.01,
            'max_daily_loss_percent': 0.03
        }
        self.position_sizer = PositionSizer(self.config)
    
    def test_position_size_calculation(self):
        """Test basic position size calculation."""
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"),
            day_pnl=Decimal("0"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        
        symbol_specs = {
            'tick_value': 12.50,
            'margin': 500,
            'is_micro': False
        }
        
        size = self.position_sizer.calculate_position_size(signal, account, symbol_specs)
        
        # Should calculate reasonable position size
        assert size > 0
        assert size <= 2  # Max for 50k account
    
    @patch('src.core.position_manager.datetime')
    def test_time_decay_factor(self, mock_datetime):
        """Test time decay calculations."""
        # Mock morning time (10 AM)
        mock_datetime.now.return_value.time.return_value = time(10, 0)
        time_factor = self.position_sizer._calculate_time_decay()
        assert time_factor == 1.0
        
        # Mock afternoon time (4 PM)
        mock_datetime.now.return_value.time.return_value = time(16, 0)
        time_factor = self.position_sizer._calculate_time_decay()
        assert time_factor == 0.5
        
        # Mock late time (8:30 PM)
        mock_datetime.now.return_value.time.return_value = time(20, 30)
        time_factor = self.position_sizer._calculate_time_decay()
        assert time_factor == 0.1
    
    def test_account_limits(self):
        """Test account-based position limits."""
        # Test micro contracts
        max_micro = self.position_sizer._get_max_contracts_for_account(Decimal("2500"), True)
        assert max_micro == 3
        
        max_micro_small = self.position_sizer._get_max_contracts_for_account(Decimal("800"), True)
        assert max_micro_small == 1
        
        # Test standard contracts
        max_standard = self.position_sizer._get_max_contracts_for_account(Decimal("50000"), False)
        assert max_standard == 2
        
        max_standard_large = self.position_sizer._get_max_contracts_for_account(Decimal("100000"), False)
        assert max_standard_large == 3


class TestPositionManager:
    """Test position management functionality."""
    
    def setup_method(self):
        """Setup for position manager tests."""
        self.config = {
            'max_positions': 3,
            'max_daily_loss_percent': 0.03,
            'commission_per_contract': 2.50
        }
        self.position_manager = PositionManager(self.config)
        self.position_manager.set_account_limits(Decimal("50000"))
    
    def test_can_open_position_checks(self):
        """Test position opening validation."""
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"),
            day_pnl=Decimal("0"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        
        # Should allow position
        can_open, reason = self.position_manager.can_open_position(signal, account)
        assert can_open
        assert "can be opened" in reason
        
        # Test daily loss limit
        self.position_manager.daily_pnl = Decimal("-1500")  # Exceeds 3% of 50k
        can_open, reason = self.position_manager.can_open_position(signal, account)
        assert not can_open
        assert "Daily loss limit" in reason
    
    @patch('src.core.position_manager.datetime')
    def test_time_restrictions(self, mock_datetime):
        """Test time-based position restrictions."""
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"),
            day_pnl=Decimal("0"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        
        # Test late time restriction (after 8 PM)
        mock_datetime.now.return_value.time.return_value = time(20, 30)
        can_open, reason = self.position_manager.can_open_position(signal, account)
        assert not can_open
        assert "Too close to market close" in reason
    
    def test_position_operations(self):
        """Test opening and closing positions."""
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        # Open position
        position = self.position_manager.open_position(signal, 1)
        assert position is not None
        assert position.symbol == "ES"
        assert position.is_long
        
        # Close position
        closed_position = self.position_manager.close_position(
            "ES", Decimal("4510.00"), Decimal("12.50")
        )
        assert closed_position is not None
        assert closed_position.unrealized_pnl > 0


class TestRiskController:
    """Test risk management functionality."""
    
    def setup_method(self):
        """Setup for risk controller tests."""
        self.config = {
            'max_daily_loss_percent': 0.03,
            'max_portfolio_heat': 0.10,
            'max_positions': 3,
            'max_margin_usage': 0.80
        }
        self.risk_controller = RiskController(self.config)
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"),
            day_pnl=Decimal("0"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        self.risk_controller.set_account_info(account)
    
    def test_risk_validation(self):
        """Test position risk validation."""
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"),
            day_pnl=Decimal("0"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        
        symbol_specs = {
            'tick_value': 12.50,
            'margin': 500
        }
        
        is_valid, reason, risk_level = self.risk_controller.validate_new_position(
            signal, 1, account, symbol_specs
        )
        
        assert is_valid
        assert risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
    
    def test_daily_loss_limit(self):
        """Test daily loss limit enforcement."""
        # Set daily P&L to exceed limit
        self.risk_controller.daily_pnl = Decimal("-1600")  # Exceeds 3% of 50k
        
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"),
            day_pnl=Decimal("-1600"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        
        symbol_specs = {'tick_value': 12.50, 'margin': 500}
        
        is_valid, reason, risk_level = self.risk_controller.validate_new_position(
            signal, 1, account, symbol_specs
        )
        
        assert not is_valid
        assert "Daily loss limit" in reason
        assert risk_level == RiskLevel.CRITICAL
    
    def test_emergency_shutdown(self):
        """Test emergency shutdown functionality."""
        assert not self.risk_controller.is_emergency_shutdown_active()
        
        self.risk_controller.trigger_emergency_shutdown("Test shutdown")
        assert self.risk_controller.is_emergency_shutdown_active()
        
        # Should block all new positions
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4495.00")
        )
        
        account = AccountInfo(
            balance=Decimal("50000"),
            buying_power=Decimal("50000"),
            day_pnl=Decimal("0"),
            total_margin_used=Decimal("0"),
            available_margin=Decimal("50000")
        )
        
        symbol_specs = {'tick_value': 12.50, 'margin': 500}
        
        is_valid, reason, risk_level = self.risk_controller.validate_new_position(
            signal, 1, account, symbol_specs
        )
        
        assert not is_valid
        assert "Emergency shutdown" in reason
        assert risk_level == RiskLevel.CRITICAL
    
    def test_portfolio_heat_calculation(self):
        """Test portfolio heat calculation."""
        signal = Signal(
            direction=SignalDirection.LONG,
            symbol="ES",
            strategy_type=StrategyType.BREAKOUT,
            entry_price=Decimal("4502.00"),
            stop_loss=Decimal("4485.00")  # Large stop for high heat
        )
        
        symbol_specs = {'tick_value': 12.50}
        
        # Calculate portfolio heat for large position
        heat = self.risk_controller._calculate_portfolio_heat(signal, 5, symbol_specs)
        
        # Should be significant heat due to large stop and position size
        assert heat > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])