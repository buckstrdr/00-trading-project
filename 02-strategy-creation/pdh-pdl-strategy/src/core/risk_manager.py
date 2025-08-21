"""
Risk management system for PDH/PDL trading strategy.
"""

import logging
from datetime import datetime, time, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .base_strategy import Signal
from .position_manager import Position, AccountInfo

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for position validation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskMetrics:
    """Container for risk metrics."""
    daily_pnl: Decimal
    daily_loss_limit: Decimal
    portfolio_heat: float  # Percentage of capital at risk
    position_count: int
    max_positions: int
    margin_usage: float
    time_risk_factor: float
    correlation_risk: float


class RiskController:
    """Core risk management controller."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.daily_pnl = Decimal(0)
        self.max_daily_loss = None
        self.account_balance = None
        self.emergency_shutdown = False
        
        # Risk thresholds
        self.risk_thresholds = {
            'max_daily_loss_percent': config.get('max_daily_loss_percent', 0.03),
            'max_portfolio_heat': config.get('max_portfolio_heat', 0.10),
            'max_positions': config.get('max_positions', 3),
            'max_margin_usage': config.get('max_margin_usage', 0.80),
            'correlation_limit': config.get('correlation_limit', 0.70)
        }
        
        # Position tracking
        self.open_positions: Dict[str, Position] = {}
        
    def set_account_info(self, account: AccountInfo):
        """Set account information for risk calculations."""
        self.account_balance = account.balance
        self.max_daily_loss = account.balance * Decimal(str(
            self.risk_thresholds['max_daily_loss_percent']
        ))
        
    def validate_new_position(self, signal: Signal, position_size: int,
                            account: AccountInfo, symbol_specs: Dict) -> Tuple[bool, str, RiskLevel]:
        """
        Validate if new position meets risk requirements.
        
        Returns:
            (is_valid, reason, risk_level)
        """
        try:
            # Emergency shutdown check
            if self.emergency_shutdown:
                return False, "Emergency shutdown active", RiskLevel.CRITICAL
            
            # Daily loss limit check
            if self.max_daily_loss and abs(self.daily_pnl) >= self.max_daily_loss:
                return False, "Daily loss limit exceeded", RiskLevel.CRITICAL
            
            # Time-based restrictions
            time_valid, time_reason, time_risk = self._check_time_restrictions()
            if not time_valid:
                return False, time_reason, time_risk
            
            # Position limits
            if len(self.open_positions) >= self.risk_thresholds['max_positions']:
                return False, f"Maximum positions ({self.risk_thresholds['max_positions']}) reached", RiskLevel.HIGH
            
            # Portfolio heat check
            portfolio_heat = self._calculate_portfolio_heat(signal, position_size, symbol_specs)
            if portfolio_heat > self.risk_thresholds['max_portfolio_heat']:
                return False, f"Portfolio heat ({portfolio_heat:.2%}) exceeds limit", RiskLevel.HIGH
            
            # Margin usage check
            margin_usage = self._calculate_margin_usage(signal, position_size, account, symbol_specs)
            if margin_usage > self.risk_thresholds['max_margin_usage']:
                return False, f"Margin usage ({margin_usage:.2%}) exceeds limit", RiskLevel.MEDIUM
            
            # Correlation check
            corr_valid, corr_reason = self._check_correlation_limits(signal.symbol)
            if not corr_valid:
                return False, corr_reason, RiskLevel.MEDIUM
            
            # Position size validation
            if position_size <= 0:
                return False, "Invalid position size", RiskLevel.LOW
            
            # All checks passed
            risk_level = self._assess_overall_risk_level(portfolio_heat, margin_usage, time_risk)
            return True, "Position passes risk validation", risk_level
            
        except Exception as e:
            logger.error(f"Error in risk validation: {e}")
            return False, f"Risk validation error: {e}", RiskLevel.CRITICAL
    
    def _check_time_restrictions(self) -> Tuple[bool, str, RiskLevel]:
        """Check time-based trading restrictions."""
        current_time = datetime.now().time()
        
        # No trading after 8 PM CT
        if current_time >= time(20, 0):
            return False, "No new positions after 8 PM CT", RiskLevel.CRITICAL
        
        # Increased risk after 6 PM CT
        if current_time >= time(18, 0):
            return True, "High risk time period", RiskLevel.HIGH
        
        # Moderate risk after 3 PM CT
        if current_time >= time(15, 0):
            return True, "Moderate risk time period", RiskLevel.MEDIUM
        
        return True, "Normal trading hours", RiskLevel.LOW
    
    def _calculate_portfolio_heat(self, signal: Signal, position_size: int,
                                symbol_specs: Dict) -> float:
        """Calculate portfolio heat (percentage of capital at risk)."""
        if not self.account_balance:
            return 1.0  # Maximum risk if no account info
        
        # Calculate risk for new position
        stop_distance = abs(signal.entry_price - signal.stop_loss)
        tick_value = Decimal(str(symbol_specs.get('tick_value', 1.0)))
        new_position_risk = stop_distance * position_size * tick_value
        
        # Calculate existing risk
        existing_risk = Decimal(0)
        for position in self.open_positions.values():
            pos_stop_distance = abs(position.entry_price - position.stop_loss)
            pos_tick_value = Decimal(str(symbol_specs.get('tick_value', 1.0)))
            existing_risk += pos_stop_distance * position.quantity * pos_tick_value
        
        total_risk = new_position_risk + existing_risk
        portfolio_heat = float(total_risk / self.account_balance)
        
        return portfolio_heat
    
    def _calculate_margin_usage(self, signal: Signal, position_size: int,
                              account: AccountInfo, symbol_specs: Dict) -> float:
        """Calculate margin usage percentage."""
        margin_per_contract = Decimal(str(symbol_specs.get('margin', 1000)))
        new_margin_required = margin_per_contract * position_size
        
        total_margin_used = account.total_margin_used + new_margin_required
        margin_usage = float(total_margin_used / account.buying_power)
        
        return margin_usage
    
    def _check_correlation_limits(self, symbol: str) -> Tuple[bool, str]:
        """Check correlation limits between positions."""
        # Simplified correlation check - in real implementation,
        # this would use correlation matrix
        correlated_symbols = {
            'ES': ['SPY', 'SPX'],
            'NQ': ['QQQ', 'NDX'],
            'MES': ['ES', 'SPY'],
            'MNQ': ['NQ', 'QQQ']
        }
        
        # Count positions in correlated instruments
        correlated_positions = 0
        for pos_symbol in self.open_positions.keys():
            if symbol in correlated_symbols.get(pos_symbol, []) or \
               pos_symbol in correlated_symbols.get(symbol, []):
                correlated_positions += 1
        
        # Allow maximum 2 correlated positions
        if correlated_positions >= 2:
            return False, f"Too many correlated positions with {symbol}"
        
        return True, "Correlation limits OK"
    
    def _assess_overall_risk_level(self, portfolio_heat: float, 
                                 margin_usage: float, time_risk: RiskLevel) -> RiskLevel:
        """Assess overall risk level for the position."""
        risk_score = 0
        
        # Portfolio heat scoring
        if portfolio_heat > 0.08:
            risk_score += 3
        elif portfolio_heat > 0.05:
            risk_score += 2
        elif portfolio_heat > 0.02:
            risk_score += 1
        
        # Margin usage scoring
        if margin_usage > 0.70:
            risk_score += 3
        elif margin_usage > 0.50:
            risk_score += 2
        elif margin_usage > 0.30:
            risk_score += 1
        
        # Time risk scoring
        if time_risk == RiskLevel.HIGH:
            risk_score += 2
        elif time_risk == RiskLevel.MEDIUM:
            risk_score += 1
        
        # Convert score to risk level
        if risk_score >= 6:
            return RiskLevel.CRITICAL
        elif risk_score >= 4:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def add_position(self, position: Position):
        """Add position to risk tracking."""
        self.open_positions[position.symbol] = position
        
    def remove_position(self, symbol: str) -> bool:
        """Remove position from risk tracking."""
        if symbol in self.open_positions:
            del self.open_positions[symbol]
            return True
        return False
    
    def update_daily_pnl(self, pnl_change: Decimal):
        """Update daily P&L for risk monitoring."""
        self.daily_pnl += pnl_change
        
        # Check if emergency shutdown is needed
        if self.max_daily_loss and abs(self.daily_pnl) >= (self.max_daily_loss * Decimal('0.95')):
            logger.warning(f"Approaching daily loss limit: {self.daily_pnl}")
            
        if self.max_daily_loss and abs(self.daily_pnl) >= self.max_daily_loss:
            self.trigger_emergency_shutdown("Daily loss limit reached")
    
    def trigger_emergency_shutdown(self, reason: str):
        """Trigger emergency shutdown of trading."""
        self.emergency_shutdown = True
        logger.critical(f"EMERGENCY SHUTDOWN TRIGGERED: {reason}")
        
    def get_risk_metrics(self, account: AccountInfo) -> RiskMetrics:
        """Get current risk metrics."""
        return RiskMetrics(
            daily_pnl=self.daily_pnl,
            daily_loss_limit=self.max_daily_loss or Decimal(0),
            portfolio_heat=self._calculate_current_portfolio_heat(),
            position_count=len(self.open_positions),
            max_positions=self.risk_thresholds['max_positions'],
            margin_usage=float(account.total_margin_used / account.buying_power) if account.buying_power > 0 else 0,
            time_risk_factor=self._get_time_risk_factor(),
            correlation_risk=self._calculate_correlation_risk()
        )
    
    def _calculate_current_portfolio_heat(self) -> float:
        """Calculate current portfolio heat from open positions."""
        if not self.account_balance:
            return 0.0
        
        total_risk = Decimal(0)
        for position in self.open_positions.values():
            stop_distance = abs(position.entry_price - position.stop_loss)
            # Using default tick value - should be passed from symbol specs
            tick_value = Decimal('1.0')  
            total_risk += stop_distance * position.quantity * tick_value
        
        return float(total_risk / self.account_balance)
    
    def _get_time_risk_factor(self) -> float:
        """Get time-based risk factor."""
        current_time = datetime.now().time()
        
        if current_time >= time(20, 0):
            return 1.0  # Maximum risk
        elif current_time >= time(18, 0):
            return 0.8
        elif current_time >= time(15, 0):
            return 0.5
        else:
            return 0.2  # Minimum risk
    
    def _calculate_correlation_risk(self) -> float:
        """Calculate correlation risk between positions."""
        # Simplified correlation risk calculation
        # In practice, this would use actual correlation coefficients
        if len(self.open_positions) <= 1:
            return 0.0
        
        # Basic correlation risk based on symbol similarity
        symbols = list(self.open_positions.keys())
        similar_count = 0
        
        for i, symbol1 in enumerate(symbols):
            for symbol2 in symbols[i+1:]:
                if self._symbols_correlated(symbol1, symbol2):
                    similar_count += 1
        
        return similar_count / max(1, len(symbols))
    
    def _symbols_correlated(self, symbol1: str, symbol2: str) -> bool:
        """Check if two symbols are correlated."""
        correlation_groups = [
            ['ES', 'MES', 'SPY'],
            ['NQ', 'MNQ', 'QQQ'],
            ['RTY', 'M2K', 'IWM']
        ]
        
        for group in correlation_groups:
            if symbol1 in group and symbol2 in group:
                return True
        
        return False
    
    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of each trading day)."""
        self.daily_pnl = Decimal(0)
        self.emergency_shutdown = False
        logger.info("Daily risk metrics reset")
    
    def is_emergency_shutdown_active(self) -> bool:
        """Check if emergency shutdown is active."""
        return self.emergency_shutdown