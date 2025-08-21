"""
PDH/PDL calculation engine for trading strategy.
Calculates Previous Day High/Low levels from Regular Trading Hours data.
"""

import logging
import pandas as pd
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..database.models import ReferenceLevel
from ..database.connection import db_manager
from .market_data_handler import MarketDataHandler, RTHSessionFilter

logger = logging.getLogger(__name__)


@dataclass
class PDHPDLLevels:
    """Container for PDH/PDL reference levels."""
    symbol: str
    trade_date: date
    pdh: Decimal
    pdl: Decimal
    daily_range: Decimal
    midpoint: Decimal
    poc: Optional[Decimal] = None
    
    # Additional calculated levels
    pdh_breakout_level: Optional[Decimal] = None
    pdl_breakout_level: Optional[Decimal] = None
    range_25_percent: Optional[Decimal] = None
    range_75_percent: Optional[Decimal] = None
    
    def __post_init__(self):
        """Calculate additional levels after initialization."""
        # Breakout levels (typically 2-4 ticks beyond PDH/PDL)
        tick_size = Decimal('0.25')  # ES futures tick size
        self.pdh_breakout_level = self.pdh + (tick_size * 2)
        self.pdl_breakout_level = self.pdl - (tick_size * 2)
        
        # 25% and 75% range levels
        self.range_25_percent = self.pdl + (self.daily_range * Decimal('0.25'))
        self.range_75_percent = self.pdl + (self.daily_range * Decimal('0.75'))
    
    def get_all_levels(self) -> Dict[str, Decimal]:
        """Get all calculated levels as a dictionary."""
        return {
            'pdh': self.pdh,
            'pdl': self.pdl,
            'midpoint': self.midpoint,
            'range': self.daily_range,
            'pdh_breakout': self.pdh_breakout_level,
            'pdl_breakout': self.pdl_breakout_level,
            'range_25': self.range_25_percent,
            'range_75': self.range_75_percent,
            'poc': self.poc
        }
    
    def is_above_pdh(self, price: Decimal) -> bool:
        """Check if price is above PDH."""
        return price > self.pdh
    
    def is_below_pdl(self, price: Decimal) -> bool:
        """Check if price is below PDL."""
        return price < self.pdl
    
    def is_breakout_long(self, price: Decimal) -> bool:
        """Check if price represents PDH breakout for long entry."""
        return price > self.pdh_breakout_level
    
    def is_breakout_short(self, price: Decimal) -> bool:
        """Check if price represents PDL breakdown for short entry."""
        return price < self.pdl_breakout_level
    
    def distance_from_pdh(self, price: Decimal) -> Decimal:
        """Calculate distance from PDH (positive = above, negative = below)."""
        return price - self.pdh
    
    def distance_from_pdl(self, price: Decimal) -> Decimal:
        """Calculate distance from PDL (positive = above, negative = below)."""
        return price - self.pdl
    
    def get_range_position(self, price: Decimal) -> float:
        """Get price position within PDH/PDL range (0.0 = PDL, 1.0 = PDH)."""
        if self.daily_range == 0:
            return 0.5
        
        return float((price - self.pdl) / self.daily_range)


class PDHPDLCalculator:
    """Calculator for PDH/PDL levels from market data."""
    
    def __init__(self, symbol: str):
        """
        Initialize PDH/PDL calculator.
        
        Args:
            symbol: Trading symbol (e.g., 'ES', 'NQ')
        """
        self.symbol = symbol
        self.rth_filter = RTHSessionFilter()
        
        # RTH session times (Central Time)
        self.rth_start = time(8, 30)   # 8:30 AM CT
        self.rth_end = time(15, 15)    # 3:15 PM CT
        
        # Cache for calculated levels
        self._levels_cache: Dict[date, PDHPDLLevels] = {}
    
    def calculate_levels(self, target_date: date, 
                        data_handler: MarketDataHandler) -> Optional[PDHPDLLevels]:
        """
        Calculate PDH/PDL levels for a target trading date.
        
        Args:
            target_date: Date for which to calculate levels
            data_handler: Market data handler for historical data
            
        Returns:
            PDHPDLLevels object or None if calculation fails
        """
        try:
            # Check cache first
            if target_date in self._levels_cache:
                logger.info(f"Using cached levels for {target_date}")
                return self._levels_cache[target_date]
            
            # Get previous trading day
            previous_day = self.rth_filter.get_previous_trading_day(target_date)
            logger.info(f"Calculating PDH/PDL for {target_date} using data from {previous_day}")
            
            # Get RTH data from previous trading day
            rth_data = data_handler.get_historical_data(
                symbol=self.symbol,
                start_date=previous_day,
                end_date=previous_day,
                rth_only=True
            )
            
            if rth_data.empty:
                logger.warning(f"No RTH data available for {previous_day}")
                return None
            
            # Calculate PDH/PDL from RTH data
            pdh = Decimal(str(rth_data['high'].max()))
            pdl = Decimal(str(rth_data['low'].min()))
            daily_range = pdh - pdl
            midpoint = (pdh + pdl) / 2
            
            # Calculate Point of Control (POC) if volume data available
            poc = self._calculate_poc(rth_data)
            
            # Create levels object
            levels = PDHPDLLevels(
                symbol=self.symbol,
                trade_date=target_date,
                pdh=pdh,
                pdl=pdl,
                daily_range=daily_range,
                midpoint=midpoint,
                poc=poc
            )
            
            # Cache the result
            self._levels_cache[target_date] = levels
            
            logger.info(f"Calculated levels for {target_date}: PDH={pdh}, PDL={pdl}, Range={daily_range}")
            return levels
            
        except Exception as e:
            logger.error(f"Error calculating PDH/PDL levels: {e}")
            return None
    
    def _calculate_poc(self, rth_data: pd.DataFrame) -> Optional[Decimal]:
        """
        Calculate Point of Control (POC) from volume data.
        
        Args:
            rth_data: RTH market data with volume
            
        Returns:
            POC price level or None if calculation fails
        """
        try:
            if 'volume' not in rth_data.columns or rth_data['volume'].sum() == 0:
                return None
            
            # Simple POC calculation using volume-weighted average
            volume_weighted_price = (rth_data['close'] * rth_data['volume']).sum()
            total_volume = rth_data['volume'].sum()
            
            if total_volume > 0:
                poc = Decimal(str(volume_weighted_price / total_volume))
                return poc
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating POC: {e}")
            return None
    
    def calculate_levels_from_database(self, target_date: date) -> Optional[PDHPDLLevels]:
        """
        Calculate PDH/PDL levels using database data.
        
        Args:
            target_date: Date for which to calculate levels
            
        Returns:
            PDHPDLLevels object or None if calculation fails
        """
        try:
            # Check if levels already exist in database
            with db_manager.get_session() as session:
                existing_levels = session.query(ReferenceLevel).filter(
                    ReferenceLevel.symbol == self.symbol,
                    ReferenceLevel.trade_date == target_date
                ).first()
                
                if existing_levels:
                    logger.info(f"Found existing levels in database for {target_date}")
                    return PDHPDLLevels(
                        symbol=existing_levels.symbol,
                        trade_date=existing_levels.trade_date,
                        pdh=existing_levels.pdh,
                        pdl=existing_levels.pdl,
                        daily_range=existing_levels.daily_range,
                        midpoint=existing_levels.midpoint,
                        poc=existing_levels.poc
                    )
            
            # Get previous trading day
            previous_day = self.rth_filter.get_previous_trading_day(target_date)
            
            # Query database for previous day's RTH data
            with db_manager.get_session() as session:
                from ..database.models import MarketData
                
                # Get RTH data from database
                rth_query = session.query(MarketData).filter(
                    MarketData.symbol == self.symbol,
                    MarketData.timestamp >= datetime.combine(previous_day, self.rth_start),
                    MarketData.timestamp <= datetime.combine(previous_day, self.rth_end)
                ).all()
                
                if not rth_query:
                    logger.warning(f"No database data for {previous_day}")
                    return None
                
                # Convert to DataFrame for processing
                data_rows = []
                for record in rth_query:
                    data_rows.append({
                        'timestamp': record.timestamp,
                        'high': float(record.high_price),
                        'low': float(record.low_price),
                        'close': float(record.close_price),
                        'volume': record.volume
                    })
                
                rth_data = pd.DataFrame(data_rows)
                
                # Calculate levels
                pdh = Decimal(str(rth_data['high'].max()))
                pdl = Decimal(str(rth_data['low'].min()))
                daily_range = pdh - pdl
                midpoint = (pdh + pdl) / 2
                poc = self._calculate_poc(rth_data)
                
                # Save to database
                levels_record = ReferenceLevel(
                    symbol=self.symbol,
                    trade_date=target_date,
                    pdh=pdh,
                    pdl=pdl,
                    daily_range=daily_range,
                    poc=poc
                )
                
                session.add(levels_record)
                
                # Create levels object
                levels = PDHPDLLevels(
                    symbol=self.symbol,
                    trade_date=target_date,
                    pdh=pdh,
                    pdl=pdl,
                    daily_range=daily_range,
                    midpoint=midpoint,
                    poc=poc
                )
                
                logger.info(f"Calculated and saved levels: PDH={pdh}, PDL={pdl}")
                return levels
                
        except Exception as e:
            logger.error(f"Error calculating levels from database: {e}")
            return None
    
    def get_historical_levels(self, start_date: date, end_date: date) -> List[PDHPDLLevels]:
        """
        Get historical PDH/PDL levels for a date range.
        
        Args:
            start_date: Start date for range
            end_date: End date for range
            
        Returns:
            List of PDHPDLLevels objects
        """
        try:
            with db_manager.get_session() as session:
                levels_query = session.query(ReferenceLevel).filter(
                    ReferenceLevel.symbol == self.symbol,
                    ReferenceLevel.trade_date >= start_date,
                    ReferenceLevel.trade_date <= end_date
                ).order_by(ReferenceLevel.trade_date).all()
                
                historical_levels = []
                for record in levels_query:
                    levels = PDHPDLLevels(
                        symbol=record.symbol,
                        trade_date=record.trade_date,
                        pdh=record.pdh,
                        pdl=record.pdl,
                        daily_range=record.daily_range,
                        midpoint=record.midpoint,
                        poc=record.poc
                    )
                    historical_levels.append(levels)
                
                logger.info(f"Retrieved {len(historical_levels)} historical levels")
                return historical_levels
                
        except Exception as e:
            logger.error(f"Error getting historical levels: {e}")
            return []
    
    def update_levels_for_date(self, target_date: date, 
                              data_handler: MarketDataHandler) -> bool:
        """
        Update or create PDH/PDL levels for a specific date.
        
        Args:
            target_date: Date to update levels for
            data_handler: Market data handler
            
        Returns:
            True if successful, False otherwise
        """
        try:
            levels = self.calculate_levels(target_date, data_handler)
            if not levels:
                return False
            
            # Save to database
            with db_manager.get_session() as session:
                # Check for existing record
                existing = session.query(ReferenceLevel).filter(
                    ReferenceLevel.symbol == self.symbol,
                    ReferenceLevel.trade_date == target_date
                ).first()
                
                if existing:
                    # Update existing record
                    existing.pdh = levels.pdh
                    existing.pdl = levels.pdl
                    existing.daily_range = levels.daily_range
                    existing.poc = levels.poc
                    logger.info(f"Updated existing levels for {target_date}")
                else:
                    # Create new record
                    new_record = ReferenceLevel(
                        symbol=self.symbol,
                        trade_date=target_date,
                        pdh=levels.pdh,
                        pdl=levels.pdl,
                        daily_range=levels.daily_range,
                        poc=levels.poc
                    )
                    session.add(new_record)
                    logger.info(f"Created new levels for {target_date}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error updating levels for {target_date}: {e}")
            return False
    
    def clear_cache(self):
        """Clear the levels cache."""
        self._levels_cache.clear()
        logger.info("Cleared PDH/PDL levels cache")
    
    def validate_levels(self, levels: PDHPDLLevels) -> Tuple[bool, str]:
        """
        Validate PDH/PDL levels for reasonableness.
        
        Args:
            levels: PDHPDLLevels object to validate
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Check that PDH > PDL
            if levels.pdh <= levels.pdl:
                return False, f"PDH ({levels.pdh}) must be greater than PDL ({levels.pdl})"
            
            # Check reasonable range (for ES futures)
            min_price, max_price = Decimal('1000'), Decimal('10000')
            if not (min_price <= levels.pdh <= max_price):
                return False, f"PDH ({levels.pdh}) outside reasonable range"
            
            if not (min_price <= levels.pdl <= max_price):
                return False, f"PDL ({levels.pdl}) outside reasonable range"
            
            # Check reasonable daily range (should be > 0 and < 500 points for ES)
            if levels.daily_range <= 0:
                return False, f"Daily range ({levels.daily_range}) must be positive"
            
            if levels.daily_range > Decimal('500'):
                return False, f"Daily range ({levels.daily_range}) too large"
            
            return True, "Valid levels"
            
        except Exception as e:
            return False, f"Validation error: {e}"


class PDHPDLManager:
    """High-level manager for PDH/PDL operations across multiple symbols."""
    
    def __init__(self, symbols: List[str]):
        """Initialize manager with list of symbols."""
        self.symbols = symbols
        self.calculators = {symbol: PDHPDLCalculator(symbol) for symbol in symbols}
        
    def calculate_all_levels(self, target_date: date, 
                           data_handler: MarketDataHandler) -> Dict[str, Optional[PDHPDLLevels]]:
        """Calculate PDH/PDL levels for all symbols."""
        results = {}
        
        for symbol in self.symbols:
            try:
                levels = self.calculators[symbol].calculate_levels(target_date, data_handler)
                results[symbol] = levels
                
                if levels:
                    logger.info(f"Calculated levels for {symbol}")
                else:
                    logger.warning(f"Failed to calculate levels for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error calculating levels for {symbol}: {e}")
                results[symbol] = None
        
        return results
    
    def update_all_levels(self, target_date: date, 
                         data_handler: MarketDataHandler) -> Dict[str, bool]:
        """Update PDH/PDL levels for all symbols."""
        results = {}
        
        for symbol in self.symbols:
            try:
                success = self.calculators[symbol].update_levels_for_date(target_date, data_handler)
                results[symbol] = success
                
            except Exception as e:
                logger.error(f"Error updating levels for {symbol}: {e}")
                results[symbol] = False
        
        return results
    
    def get_current_levels(self, symbol: str, target_date: date = None) -> Optional[PDHPDLLevels]:
        """Get current PDH/PDL levels for a symbol."""
        if symbol not in self.calculators:
            return None
        
        if target_date is None:
            target_date = date.today()
        
        return self.calculators[symbol].calculate_levels_from_database(target_date)