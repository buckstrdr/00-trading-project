"""
Market data handler for PDH/PDL trading strategy.
Handles real-time data feeds, historical data loading, and data validation.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import io
import requests

from ..core.base_strategy import MarketData
from ..database.models import MarketData as MarketDataModel
from ..database.connection import db_manager

logger = logging.getLogger(__name__)


@dataclass
class DataFeedConfig:
    """Configuration for data feed connections."""
    feed_type: str  # 'simulation', 'csv', 'api'
    source_path: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    update_interval_ms: int = 1000
    reconnect_attempts: int = 5
    timeout_seconds: int = 30


class DataFeedInterface(ABC):
    """Abstract interface for data feed implementations."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to data feed."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from data feed."""
        pass
    
    @abstractmethod
    def get_current_bar(self, symbol: str) -> Optional[MarketData]:
        """Get current market data bar for symbol."""
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, start_date: date, 
                          end_date: date) -> pd.DataFrame:
        """Get historical data for symbol and date range."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if data feed is connected."""
        pass


class SimulationDataFeed(DataFeedInterface):
    """Simulation data feed for testing and backtesting."""
    
    def __init__(self, config: DataFeedConfig):
        self.config = config
        self.connected = False
        self.current_time = datetime.now()
        
        # Generate sample data for ES futures
        self.sample_data = self._generate_sample_data()
        self.data_index = 0
        
    def connect(self) -> bool:
        """Connect to simulation feed."""
        try:
            logger.info("Connecting to simulation data feed")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to simulation feed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from simulation feed."""
        self.connected = False
        logger.info("Disconnected from simulation feed")
    
    def get_current_bar(self, symbol: str) -> Optional[MarketData]:
        """Get current simulated market data."""
        if not self.connected or self.data_index >= len(self.sample_data):
            return None
        
        try:
            row = self.sample_data.iloc[self.data_index]
            self.data_index += 1
            
            return MarketData(
                symbol=symbol,
                timestamp=row['timestamp'],
                open_price=Decimal(str(row['open'])),
                high_price=Decimal(str(row['high'])),
                low_price=Decimal(str(row['low'])),
                close_price=Decimal(str(row['close'])),
                volume=int(row['volume'])
            )
        except Exception as e:
            logger.error(f"Error getting current bar: {e}")
            return None
    
    def get_historical_data(self, symbol: str, start_date: date, 
                          end_date: date) -> pd.DataFrame:
        """Get historical simulation data."""
        try:
            # Filter sample data by date range
            mask = (self.sample_data['timestamp'].dt.date >= start_date) & \
                   (self.sample_data['timestamp'].dt.date <= end_date)
            
            filtered_data = self.sample_data[mask].copy()
            filtered_data['symbol'] = symbol
            
            return filtered_data
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def is_connected(self) -> bool:
        """Check simulation connection status."""
        return self.connected
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample OHLCV data for testing."""
        # Generate 1000 bars of sample data
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(days=5),
            end=datetime.now(),
            freq='1min'
        )
        
        # Base price around ES futures level
        base_price = 4500.0
        data = []
        
        for i, timestamp in enumerate(timestamps):
            # Random walk with some trend
            price_change = np.random.normal(0, 2.5)
            if i > 0:
                base_price = data[-1]['close'] + price_change
            
            # Generate OHLC from base price
            high_offset = abs(np.random.normal(0, 3))
            low_offset = abs(np.random.normal(0, 3))
            
            open_price = base_price + np.random.normal(0, 1)
            close_price = base_price + np.random.normal(0, 1)
            high_price = max(open_price, close_price) + high_offset
            low_price = min(open_price, close_price) - low_offset
            
            volume = int(np.random.exponential(1000) + 100)
            
            data.append({
                'timestamp': timestamp,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        return pd.DataFrame(data)


class CSVDataFeed(DataFeedInterface):
    """CSV file data feed for historical data."""
    
    def __init__(self, config: DataFeedConfig):
        self.config = config
        self.connected = False
        self.data: Optional[pd.DataFrame] = None
        
    def connect(self) -> bool:
        """Connect by loading CSV file."""
        try:
            if not self.config.source_path:
                raise ValueError("CSV source path not provided")
            
            logger.info(f"Loading CSV data from: {self.config.source_path}")
            self.data = pd.read_csv(self.config.source_path)
            
            # Standardize column names
            column_mapping = {
                'Date': 'timestamp',
                'Time': 'time',
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }
            
            self.data.rename(columns=column_mapping, inplace=True, errors='ignore')
            
            # Parse timestamps
            if 'time' in self.data.columns:
                self.data['timestamp'] = pd.to_datetime(
                    self.data['timestamp'] + ' ' + self.data['time']
                )
            else:
                self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            
            # Sort by timestamp
            self.data.sort_values('timestamp', inplace=True)
            self.data.reset_index(drop=True, inplace=True)
            
            self.connected = True
            logger.info(f"Loaded {len(self.data)} bars from CSV")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load CSV data: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect CSV feed."""
        self.connected = False
        self.data = None
        logger.info("Disconnected CSV data feed")
    
    def get_current_bar(self, symbol: str) -> Optional[MarketData]:
        """Get latest bar from CSV data."""
        if not self.connected or self.data is None or len(self.data) == 0:
            return None
        
        try:
            row = self.data.iloc[-1]  # Get latest bar
            
            return MarketData(
                symbol=symbol,
                timestamp=row['timestamp'],
                open_price=Decimal(str(row['open'])),
                high_price=Decimal(str(row['high'])),
                low_price=Decimal(str(row['low'])),
                close_price=Decimal(str(row['close'])),
                volume=int(row['volume'])
            )
        except Exception as e:
            logger.error(f"Error getting current bar: {e}")
            return None
    
    def get_historical_data(self, symbol: str, start_date: date, 
                          end_date: date) -> pd.DataFrame:
        """Get historical data from CSV within date range."""
        if not self.connected or self.data is None:
            return pd.DataFrame()
        
        try:
            # Filter by date range
            mask = (self.data['timestamp'].dt.date >= start_date) & \
                   (self.data['timestamp'].dt.date <= end_date)
            
            filtered_data = self.data[mask].copy()
            filtered_data['symbol'] = symbol
            
            return filtered_data
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def is_connected(self) -> bool:
        """Check CSV connection status."""
        return self.connected


class MarketDataValidator:
    """Validates and cleans market data."""
    
    @staticmethod
    def validate_ohlcv_bar(bar: Dict) -> Tuple[bool, str]:
        """
        Validate OHLCV bar data.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Check required fields
            required_fields = ['open', 'high', 'low', 'close', 'volume']
            for field in required_fields:
                if field not in bar or bar[field] is None:
                    return False, f"Missing required field: {field}"
            
            # Convert to float for validation
            o, h, l, c, v = float(bar['open']), float(bar['high']), \
                           float(bar['low']), float(bar['close']), int(bar['volume'])
            
            # Basic OHLC validation
            if h < max(o, c) or h < min(o, c):
                return False, f"High ({h}) less than open/close"
            
            if l > min(o, c) or l > max(o, c):
                return False, f"Low ({l}) greater than open/close"
            
            # Volume validation
            if v < 0:
                return False, f"Negative volume: {v}"
            
            # Price validation (reasonable ranges for ES futures)
            if any(price <= 0 for price in [o, h, l, c]):
                return False, "Non-positive prices detected"
            
            if any(price > 10000 or price < 1000 for price in [o, h, l, c]):
                return False, "Prices outside reasonable range"
            
            return True, "Valid bar"
            
        except (ValueError, TypeError) as e:
            return False, f"Data type error: {e}"
    
    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize market data."""
        cleaned = data.copy()
        
        # Remove rows with missing critical data
        cleaned.dropna(subset=['open', 'high', 'low', 'close'], inplace=True)
        
        # Fill missing volume with 0
        cleaned = cleaned.fillna({'volume': 0})
        
        # Remove duplicate timestamps
        cleaned.drop_duplicates(subset=['timestamp'], keep='last', inplace=True)
        
        # Remove invalid bars (where high < low)
        invalid_mask = cleaned['high'] < cleaned['low']
        if invalid_mask.any():
            logger.warning(f"Removing {invalid_mask.sum()} bars with high < low")
            cleaned = cleaned[~invalid_mask]
        
        # Sort by timestamp
        cleaned.sort_values('timestamp', inplace=True)
        cleaned.reset_index(drop=True, inplace=True)
        
        return cleaned


class RTHSessionFilter:
    """Filters data for Regular Trading Hours (RTH) sessions."""
    
    def __init__(self, rth_start: time = time(8, 30), rth_end: time = time(15, 15)):
        """
        Initialize RTH filter.
        
        Args:
            rth_start: RTH start time (default 8:30 AM CT)
            rth_end: RTH end time (default 3:15 PM CT)
        """
        self.rth_start = rth_start
        self.rth_end = rth_end
        
    def filter_rth_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filter DataFrame for RTH sessions only."""
        if data.empty:
            return data
        
        try:
            # Convert to Central Time if needed (assuming data is in CT)
            data_copy = data.copy()
            
            # Extract time component
            data_copy['time'] = data_copy['timestamp'].dt.time
            
            # Filter for RTH hours
            rth_mask = (data_copy['time'] >= self.rth_start) & \
                      (data_copy['time'] <= self.rth_end)
            
            # Filter for weekdays only (Monday=0, Sunday=6)
            weekday_mask = data_copy['timestamp'].dt.dayofweek < 5
            
            # Combine filters
            combined_mask = rth_mask & weekday_mask
            
            rth_data = data_copy[combined_mask].copy()
            rth_data.drop('time', axis=1, inplace=True)
            
            logger.info(f"RTH filter: {len(data)} -> {len(rth_data)} bars")
            return rth_data
            
        except Exception as e:
            logger.error(f"Error filtering RTH data: {e}")
            return pd.DataFrame()
    
    def get_previous_trading_day(self, current_date: date) -> date:
        """Get the previous trading day (excluding weekends)."""
        previous_date = current_date - timedelta(days=1)
        
        # Skip weekends
        while previous_date.weekday() > 4:  # Monday=0, Sunday=6
            previous_date -= timedelta(days=1)
        
        return previous_date


class MarketDataHandler:
    """Main market data handler coordinating all data operations."""
    
    def __init__(self, config: DataFeedConfig):
        self.config = config
        self.data_feed: Optional[DataFeedInterface] = None
        self.validator = MarketDataValidator()
        self.rth_filter = RTHSessionFilter()
        self.connected = False
        
        # Initialize appropriate data feed
        self._initialize_data_feed()
        
    def _initialize_data_feed(self):
        """Initialize data feed based on configuration."""
        try:
            if self.config.feed_type == 'simulation':
                self.data_feed = SimulationDataFeed(self.config)
            elif self.config.feed_type == 'csv':
                self.data_feed = CSVDataFeed(self.config)
            else:
                raise ValueError(f"Unsupported feed type: {self.config.feed_type}")
            
            logger.info(f"Initialized {self.config.feed_type} data feed")
            
        except Exception as e:
            logger.error(f"Failed to initialize data feed: {e}")
            raise
    
    def connect(self) -> bool:
        """Connect to data feed."""
        if not self.data_feed:
            return False
        
        success = self.data_feed.connect()
        self.connected = success
        return success
    
    def disconnect(self):
        """Disconnect from data feed."""
        if self.data_feed:
            self.data_feed.disconnect()
        self.connected = False
    
    def get_current_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data with validation."""
        if not self.connected or not self.data_feed:
            return None
        
        try:
            current_bar = self.data_feed.get_current_bar(symbol)
            if not current_bar:
                return None
            
            # Validate the bar
            bar_dict = {
                'open': float(current_bar.open_price),
                'high': float(current_bar.high_price),
                'low': float(current_bar.low_price),
                'close': float(current_bar.close_price),
                'volume': current_bar.volume
            }
            
            is_valid, error_msg = self.validator.validate_ohlcv_bar(bar_dict)
            if not is_valid:
                logger.warning(f"Invalid bar for {symbol}: {error_msg}")
                return None
            
            return current_bar
            
        except Exception as e:
            logger.error(f"Error getting current data for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, start_date: date, 
                          end_date: date, rth_only: bool = True) -> pd.DataFrame:
        """Get historical data with optional RTH filtering."""
        if not self.connected or not self.data_feed:
            return pd.DataFrame()
        
        try:
            # Get raw historical data
            raw_data = self.data_feed.get_historical_data(symbol, start_date, end_date)
            
            if raw_data.empty:
                return raw_data
            
            # Clean the data
            cleaned_data = self.validator.clean_data(raw_data)
            
            # Apply RTH filter if requested
            if rth_only:
                filtered_data = self.rth_filter.filter_rth_data(cleaned_data)
                return filtered_data
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def save_to_database(self, symbol: str, data: pd.DataFrame) -> bool:
        """Save market data to database."""
        try:
            with db_manager.get_session() as session:
                saved_count = 0
                
                for _, row in data.iterrows():
                    # Check if record already exists
                    existing = session.query(MarketDataModel).filter(
                        MarketDataModel.symbol == symbol,
                        MarketDataModel.timestamp == row['timestamp']
                    ).first()
                    
                    if existing:
                        continue  # Skip duplicates
                    
                    # Create new record
                    market_data = MarketDataModel(
                        symbol=symbol,
                        timestamp=row['timestamp'],
                        open_price=Decimal(str(row['open'])),
                        high_price=Decimal(str(row['high'])),
                        low_price=Decimal(str(row['low'])),
                        close_price=Decimal(str(row['close'])),
                        volume=int(row['volume'])
                    )
                    
                    session.add(market_data)
                    saved_count += 1
                
                logger.info(f"Saved {saved_count} new bars for {symbol}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving data to database: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self.connected and self.data_feed and self.data_feed.is_connected()
    
    def get_data_feed_info(self) -> Dict:
        """Get information about current data feed."""
        return {
            'feed_type': self.config.feed_type,
            'connected': self.is_connected(),
            'source_path': self.config.source_path,
            'update_interval_ms': self.config.update_interval_ms
        }