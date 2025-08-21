"""
Position management system for PDH/PDL trading strategy.
"""

import logging
from datetime import datetime, time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from math import sqrt

from .base_strategy import Signal, SignalDirection

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Trading position container."""
    id: Optional[int]
    symbol: str
    direction: SignalDirection
    quantity: int
    entry_price: Decimal
    entry_timestamp: datetime
    stop_loss: Decimal
    target_price: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    strategy_type: Optional[str] = None
    
    @property
    def is_long(self) -> bool:
        return self.direction == SignalDirection.LONG
    
    @property
    def is_short(self) -> bool:
        return self.direction == SignalDirection.SHORT


@dataclass
class AccountInfo:
    """Account information container."""
    balance: Decimal
    buying_power: Decimal
    day_pnl: Decimal
    total_margin_used: Decimal
    available_margin: Decimal


class PositionSizer:
    """Calculate position sizes based on risk management rules."""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def calculate_position_size(self, signal: Signal, account: AccountInfo, 
                              symbol_specs: Dict) -> int:
        """
        Calculate position size based on risk management rules.
        
        Args:
            signal: Trading signal
            account: Account information
            symbol_specs: Symbol specifications (tick_value, margin, etc.)
            
        Returns:
            Number of contracts to trade
        """
        try:
            # Get basic parameters
            risk_amount = account.balance * Decimal(str(self.config.get('risk_percent', 0.01)))
            tick_value = Decimal(str(symbol_specs.get('tick_value', 1.0)))
            
            # Calculate risk per contract
            stop_distance = abs(signal.entry_price - signal.stop_loss)
            risk_per_contract = stop_distance * tick_value
            
            if risk_per_contract <= 0:
                logger.warning("Invalid risk per contract calculated")
                return 0
            
            # Base position size
            base_contracts = int(risk_amount / risk_per_contract)
            
            # Apply time decay factor
            time_factor = self._calculate_time_decay()
            adjusted_contracts = int(base_contracts * Decimal(str(time_factor)))
            
            # Apply account-based limits
            max_contracts = self._get_max_contracts_for_account(
                account.balance, 
                symbol_specs.get('is_micro', False)
            )
            
            # Apply margin constraints
            margin_per_contract = Decimal(str(symbol_specs.get('margin', 1000)))
            max_by_margin = int(account.available_margin / margin_per_contract)
            
            # Return minimum of all constraints
            final_size = min(adjusted_contracts, max_contracts, max_by_margin)
            
            logger.info(f"Position size calculation: base={base_contracts}, "
                       f"time_adjusted={adjusted_contracts}, max={max_contracts}, "
                       f"margin_max={max_by_margin}, final={final_size}")
            
            return max(0, final_size)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    def _calculate_time_decay(self) -> float:
        """Calculate time decay factor based on time until market close."""
        try:
            current_time = datetime.now().time()
            market_close = time(21, 0)  # 9 PM CT
            
            # Convert to minutes from market open (assume 8:30 AM start)
            market_open = time(8, 30)
            
            # Calculate minutes since open and until close
            now_minutes = current_time.hour * 60 + current_time.minute
            close_minutes = market_close.hour * 60 + market_close.minute
            open_minutes = market_open.hour * 60 + market_open.minute
            
            # Total trading minutes in a day
            total_minutes = close_minutes - open_minutes
            remaining_minutes = close_minutes - now_minutes
            
            if remaining_minutes <= 0:
                return 0.1  # Emergency only after close
            
            # Time decay factor using square root for gradual reduction
            time_factor = sqrt(remaining_minutes / total_minutes)
            
            # Apply specific thresholds
            if current_time < time(12, 0):  # Before noon
                return 1.0
            elif current_time < time(15, 0):  # Before 3 PM
                return 0.75
            elif current_time < time(18, 0):  # Before 6 PM
                return 0.5
            elif current_time < time(20, 0):  # Before 8 PM
                return 0.25
            else:
                return 0.1
                
        except Exception as e:
            logger.error(f"Error calculating time decay: {e}")
            return 0.5  # Default moderate factor
    
    def _get_max_contracts_for_account(self, balance: Decimal, is_micro: bool) -> int:
        """Get maximum contracts based on account size and contract type."""
        if is_micro:
            if balance >= 5000:
                return 5
            elif balance >= 2500:
                return 3
            elif balance >= 1000:
                return 2
            else:
                return 1
        else:  # Standard contracts
            if balance >= 100000:
                return 3
            elif balance >= 50000:
                return 2
            elif balance >= 25000:
                return 1
            else:
                return 0  # Insufficient capital


class PositionManager:
    """Manage trading positions and portfolio risk."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.positions: Dict[str, Position] = {}
        self.daily_pnl = Decimal(0)
        self.max_daily_loss = None
        self.position_sizer = PositionSizer(config)
        
    def set_account_limits(self, account_balance: Decimal):
        """Set daily loss limits based on account balance."""
        self.max_daily_loss = account_balance * Decimal(str(
            self.config.get('max_daily_loss_percent', 0.03)
        ))
        
    def can_open_position(self, signal: Signal, account: AccountInfo) -> Tuple[bool, str]:
        """
        Check if new position can be opened.
        
        Returns:
            (can_open, reason)
        """
        # Check daily loss limit
        if self.max_daily_loss and abs(self.daily_pnl) >= self.max_daily_loss:
            return False, "Daily loss limit exceeded"
        
        # Check time constraints (no new positions after 8 PM CT)
        current_time = datetime.now().time()
        if current_time > time(20, 0):
            return False, "Too close to market close"
        
        # Check maximum positions limit
        max_positions = self.config.get('max_positions', 3)
        if len(self.positions) >= max_positions:
            return False, f"Maximum positions ({max_positions}) reached"
        
        # Check if already have position in same symbol
        if signal.symbol in self.positions:
            return False, f"Already have position in {signal.symbol}"
        
        # Check available margin
        if account.available_margin <= 0:
            return False, "Insufficient margin available"
        
        return True, "Position can be opened"
    
    def calculate_position_size(self, signal: Signal, account: AccountInfo, 
                              symbol_specs: Dict) -> int:
        """Calculate position size for new position."""
        return self.position_sizer.calculate_position_size(signal, account, symbol_specs)
    
    def open_position(self, signal: Signal, quantity: int) -> Optional[Position]:
        """
        Open new position based on signal.
        
        Args:
            signal: Trading signal
            quantity: Number of contracts
            
        Returns:
            Position object if successful, None otherwise
        """
        try:
            position = Position(
                id=None,  # Will be set after database insertion
                symbol=signal.symbol,
                direction=signal.direction,
                quantity=quantity,
                entry_price=signal.entry_price,
                entry_timestamp=datetime.now(),
                stop_loss=signal.stop_loss,
                target_price=signal.target_price,
                strategy_type=signal.strategy_type.value if signal.strategy_type else None
            )
            
            self.positions[signal.symbol] = position
            
            logger.info(f"Opened position: {signal.direction.value} {quantity} {signal.symbol} @ {signal.entry_price}")
            return position
            
        except Exception as e:
            logger.error(f"Error opening position: {e}")
            return None
    
    def close_position(self, symbol: str, exit_price: Decimal, 
                      tick_value: Decimal) -> Optional[Position]:
        """
        Close position and calculate P&L.
        
        Args:
            symbol: Symbol to close
            exit_price: Exit price
            tick_value: Tick value for P&L calculation
            
        Returns:
            Closed position with P&L calculated
        """
        try:
            if symbol not in self.positions:
                logger.warning(f"No position found for {symbol}")
                return None
            
            position = self.positions[symbol]
            
            # Calculate P&L
            if position.is_long:
                price_diff = exit_price - position.entry_price
            else:
                price_diff = position.entry_price - exit_price
            
            gross_pnl = price_diff * position.quantity * tick_value
            commission = Decimal(str(self.config.get('commission_per_contract', 0)))
            net_pnl = gross_pnl - (commission * position.quantity)
            
            position.unrealized_pnl = net_pnl
            self.daily_pnl += net_pnl
            
            # Remove from active positions
            del self.positions[symbol]
            
            logger.info(f"Closed position: {symbol} P&L: {net_pnl}")
            return position
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return None
    
    def update_positions(self, market_data: Dict[str, Decimal]):
        """Update all positions with current market prices."""
        for symbol, position in self.positions.items():
            if symbol in market_data:
                position.current_price = market_data[symbol]
                # Update unrealized P&L logic can be added here
    
    def get_positions_summary(self) -> Dict:
        """Get summary of all positions."""
        return {
            'total_positions': len(self.positions),
            'symbols': list(self.positions.keys()),
            'daily_pnl': float(self.daily_pnl),
            'max_daily_loss': float(self.max_daily_loss) if self.max_daily_loss else None
        }
    
    def force_close_all_positions(self, market_data: Dict[str, Decimal], 
                                 symbol_specs: Dict[str, Dict]) -> List[Position]:
        """Force close all positions (for emergency or end of day)."""
        closed_positions = []
        
        for symbol in list(self.positions.keys()):
            if symbol in market_data:
                tick_value = Decimal(str(symbol_specs.get(symbol, {}).get('tick_value', 1.0)))
                position = self.close_position(symbol, market_data[symbol], tick_value)
                if position:
                    closed_positions.append(position)
        
        logger.info(f"Force closed {len(closed_positions)} positions")
        return closed_positions