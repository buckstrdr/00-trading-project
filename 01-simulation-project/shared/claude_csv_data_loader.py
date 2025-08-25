"""
CSV Data Loader for Monthly Historical Data Files
Loads real market data from monthly CSV files for backtesting
"""

import os
import csv
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MonthlyCSVDataLoader:
    """
    Loads historical market data from monthly CSV files
    Handles the specific format: Date (D);Time (T);Open (O);High (H);Low (L);Close (C);Volume (V)
    """
    
    def __init__(self, data_directory: str):
        """
        Initialize CSV data loader
        
        Args:
            data_directory: Path to 98-month-by-month-data-files directory
        """
        self.data_directory = data_directory
        self.loaded_data_cache = {}  # Cache loaded monthly files
        
        # Verify data directory exists
        if not os.path.exists(data_directory):
            raise FileNotFoundError(f"Data directory not found: {data_directory}")
        
        logger.info(f"CSV Data Loader initialized with directory: {data_directory}")
    
    def load_symbol_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Load data for a symbol within date range
        
        Args:
            symbol: Symbol to load (exact match required)
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            pandas DataFrame with OHLCV data
            
        Raises:
            ValueError: If symbol is not available
        """
        logger.info(f"Loading {symbol} data from {start_date} to {end_date}")
        
        # Check if symbol is available - NO SUBSTITUTION ALLOWED
        if not self.is_symbol_available(symbol):
            available_symbols = self.get_available_symbols()
            raise ValueError(f"Symbol '{symbol}' not available. Available symbols: {available_symbols}")
        
        # Get list of monthly CSV files needed for date range
        csv_files = self._get_csv_files_for_range(symbol, start_date, end_date)
        
        if not csv_files:
            logger.warning(f"No CSV files found for {symbol} in date range")
            return pd.DataFrame()
        
        # Load all monthly data
        all_bars = []
        for csv_file in csv_files:
            try:
                monthly_bars = self._load_monthly_csv(csv_file)
                all_bars.extend(monthly_bars)
                logger.info(f"Loaded {len(monthly_bars)} bars from {os.path.basename(csv_file)}")
            except Exception as e:
                logger.error(f"Error loading {csv_file}: {e}")
        
        if not all_bars:
            logger.warning(f"No data loaded for {symbol}")
            return pd.DataFrame()
        
        # Convert to DataFrame and filter by date range
        df = pd.DataFrame(all_bars)
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Filter by exact date range
        mask = (df['datetime'] >= start_date) & (df['datetime'] <= end_date)
        filtered_df = df[mask].copy()
        
        # Sort by datetime
        filtered_df = filtered_df.sort_values('datetime').reset_index(drop=True)
        
        logger.info(f"Loaded {len(filtered_df)} bars for {symbol} after filtering")
        
        return filtered_df
    
    def get_historical_slice(self, symbol: str, end_datetime: datetime, bars_back: int) -> List[Dict[str, Any]]:
        """
        Get historical data slice for TSX strategy bootstrap
        
        Args:
            symbol: Symbol to get data for (exact match required)
            end_datetime: End datetime for the slice
            bars_back: Number of bars to go back
            
        Returns:
            List of OHLCV bar dictionaries
            
        Raises:
            ValueError: If symbol is not available
        """
        # Check symbol availability first - NO SUBSTITUTION
        if not self.is_symbol_available(symbol):
            available_symbols = self.get_available_symbols()
            raise ValueError(f"Symbol '{symbol}' not available. Available symbols: {available_symbols}")
        
        # Calculate start datetime - FIXED: Use proper calculation
        # Estimate roughly 390 bars per trading day (6.5 hours * 60 minutes)
        days_needed = max(1, bars_back // 390 + 5)  # Add buffer days
        start_datetime = end_datetime - timedelta(days=days_needed)
        
        # Load data for the period
        df = self.load_symbol_data(symbol, start_datetime, end_datetime)
        
        if df.empty:
            return []
        
        # Get the last N bars up to end_datetime
        df_filtered = df[df['datetime'] <= end_datetime]
        
        if len(df_filtered) == 0:
            return []
        
        # Take last bars_back bars
        df_slice = df_filtered.tail(bars_back)
        
        # Convert to list of dictionaries
        bars = []
        for _, row in df_slice.iterrows():
            bar = {
                'datetime': row['datetime'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            }
            bars.append(bar)
        
        logger.info(f"Retrieved {len(bars)} historical bars for {symbol} ending at {end_datetime}")
        return bars
    
    def get_historical_bars(self, symbol: str, bars_back: int, end_datetime: datetime) -> List[Dict[str, Any]]:
        """
        COMPATIBILITY METHOD: Get historical bars (wrapper for get_historical_slice)
        
        Args:
            symbol: Symbol to get data for
            bars_back: Number of bars to retrieve 
            end_datetime: End datetime for the slice
            
        Returns:
            List of OHLCV bar dictionaries
        """
        return self.get_historical_slice(symbol, end_datetime, bars_back)
    
    def test_symbol_availability(self, symbol: str) -> Dict[str, Any]:
        """
        COMPATIBILITY METHOD: Test symbol availability with additional info
        
        Args:
            symbol: Symbol to test
            
        Returns:
            Dictionary with availability info
        """
        try:
            available = self.is_symbol_available(symbol)
            result = {
                'available': available,
                'symbol': symbol
            }
            
            if available:
                try:
                    date_range = self.get_date_range_for_symbol(symbol)
                    result['date_range'] = f"{date_range[0]} to {date_range[1]}"
                except Exception as e:
                    result['date_range'] = f"Error getting date range: {e}"
            
            return result
        except Exception as e:
            return {
                'available': False,
                'symbol': symbol,
                'error': str(e)
            }
    
    def _get_csv_files_for_range(self, symbol: str, start_date: datetime, end_date: datetime) -> List[str]:
        """Get list of CSV files needed for date range"""
        
        csv_files = []
        symbol_dir = os.path.join(self.data_directory, symbol.upper())
        
        if not os.path.exists(symbol_dir):
            logger.error(f"Symbol directory not found: {symbol_dir}")
            return []
        
        # Iterate through years and months in range
        current_date = datetime(start_date.year, start_date.month, 1)
        end_month = datetime(end_date.year, end_date.month, 1)
        
        while current_date <= end_month:
            year_dir = os.path.join(symbol_dir, str(current_date.year))
            month_name = current_date.strftime("%B")
            month_num = current_date.strftime("%m")
            
            # Try different month directory naming patterns
            possible_month_dirs = [
                f"{month_num}-{month_name}",  # 01-January (month_num is already zero-padded)
            ]
            
            for month_dir_name in possible_month_dirs:
                month_dir = os.path.join(year_dir, month_dir_name)
                
                if os.path.exists(month_dir):
                    # Look for CSV file in month directory
                    csv_filename = f"{symbol.upper()}_{current_date.year}_{month_num}_{month_name}.csv"
                    csv_path = os.path.join(month_dir, csv_filename)
                    
                    if os.path.exists(csv_path):
                        csv_files.append(csv_path)
                        break
                    else:
                        # Try alternative naming (month_num is already zero-padded string)
                        alt_csv_filename = f"{symbol.upper()}_{current_date.year}_{month_num}_{month_name}.csv"
                        alt_csv_path = os.path.join(month_dir, alt_csv_filename)
                        if os.path.exists(alt_csv_path):
                            csv_files.append(alt_csv_path)
                            break
            
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        logger.info(f"Found {len(csv_files)} CSV files for {symbol} in date range")
        return csv_files
    
    def _load_monthly_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Load and parse a single monthly CSV file"""
        
        # Check cache first
        if file_path in self.loaded_data_cache:
            return self.loaded_data_cache[file_path]
        
        bars = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read first line to detect header
                first_line = f.readline().strip()
                f.seek(0)
                
                if 'Date (D)' in first_line:
                    # Has header - skip it
                    reader = csv.DictReader(f, delimiter=';')
                    
                    for row in reader:
                        try:
                            bar = self._parse_csv_row(row)
                            if bar:
                                bars.append(bar)
                        except Exception as e:
                            logger.warning(f"Error parsing row in {file_path}: {e}")
                            continue
                else:
                    # No header - manual parsing
                    for line_num, line in enumerate(f, 1):
                        try:
                            parts = line.strip().split(';')
                            if len(parts) >= 7:
                                bar = self._parse_csv_parts(parts)
                                if bar:
                                    bars.append(bar)
                        except Exception as e:
                            logger.warning(f"Error parsing line {line_num} in {file_path}: {e}")
                            continue
            
            # Cache the loaded data
            self.loaded_data_cache[file_path] = bars
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
        
        return bars
    
    def _parse_csv_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Parse a CSV row with headers"""
        
        try:
            # Parse date and time
            date_str = row['Date (D)'].strip()
            time_str = row['Time (T)'].strip()
            
            # Handle different date formats
            if '/' in date_str:
                # DD/MM/YYYY format
                dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            else:
                # Try other formats
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            bar = {
                'datetime': dt,
                'open': float(row['Open (O)'].strip()),
                'high': float(row['High (H)'].strip()),
                'low': float(row['Low (L)'].strip()),
                'close': float(row['Close (C)'].strip()),
                'volume': int(float(row['Volume (V)'].strip()))
            }
            
            return bar
            
        except Exception as e:
            logger.warning(f"Error parsing CSV row: {e}")
            return None
    
    def _parse_csv_parts(self, parts: List[str]) -> Optional[Dict[str, Any]]:
        """Parse CSV parts without headers"""
        
        try:
            # Assuming format: Date;Time;Open;High;Low;Close;Volume
            date_str = parts[0].strip()
            time_str = parts[1].strip()
            
            # Parse datetime
            if '/' in date_str:
                dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            else:
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            bar = {
                'datetime': dt,
                'open': float(parts[2].strip()),
                'high': float(parts[3].strip()),
                'low': float(parts[4].strip()),
                'close': float(parts[5].strip()),
                'volume': int(float(parts[6].strip()))
            }
            
            return bar
            
        except Exception as e:
            logger.warning(f"Error parsing CSV parts: {e}")
            return None
    
    def convert_to_tsx_format(self, bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert bar data to TSX V5 format"""
        
        tsx_bars = []
        
        for bar in bars:
            tsx_bar = {
                't': bar['datetime'].isoformat() + 'Z',
                'o': round(float(bar['open']), 6),
                'h': round(float(bar['high']), 6),
                'l': round(float(bar['low']), 6),
                'c': round(float(bar['close']), 6),
                'v': int(bar['volume'])
            }
            tsx_bars.append(tsx_bar)
        
        return tsx_bars
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols"""
        
        symbols = []
        
        for item in os.listdir(self.data_directory):
            item_path = os.path.join(self.data_directory, item)
            if os.path.isdir(item_path):
                symbols.append(item.upper())
        
        return symbols
    
    def is_symbol_available(self, symbol: str) -> bool:
        """Check if symbol data is available"""
        symbol_dir = os.path.join(self.data_directory, symbol.upper())
        return os.path.exists(symbol_dir)
    
    def get_date_range_for_symbol(self, symbol: str) -> tuple:
        """Get available date range for a symbol"""
        
        symbol_dir = os.path.join(self.data_directory, symbol.upper())
        if not os.path.exists(symbol_dir):
            return None, None
        
        min_date = None
        max_date = None
        
        for year_dir in os.listdir(symbol_dir):
            year_path = os.path.join(symbol_dir, year_dir)
            if not os.path.isdir(year_path):
                continue
                
            try:
                year = int(year_dir)
            except ValueError:
                continue
            
            for month_dir in os.listdir(year_path):
                month_path = os.path.join(year_path, month_dir)
                if not os.path.isdir(month_path):
                    continue
                
                # Extract month number from directory name
                if '-' in month_dir:
                    month_str = month_dir.split('-')[0]
                    try:
                        month = int(month_str)
                        date = datetime(year, month, 1)
                        
                        if min_date is None or date < min_date:
                            min_date = date
                        if max_date is None or date > max_date:
                            max_date = date
                    except ValueError:
                        continue
        
        return min_date, max_date


# Test the loader if run directly
if __name__ == "__main__":
    print("=== Testing CSV Data Loader ===")
    
    data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    
    try:
        loader = MonthlyCSVDataLoader(data_dir)
        
        # Test 1: Get available symbols
        symbols = loader.get_available_symbols()
        print(f"Available symbols: {symbols}")
        
        # Test 2: Get date range for MCL
        if 'MCL' in symbols:
            min_date, max_date = loader.get_date_range_for_symbol('MCL')
            print(f"MCL date range: {min_date} to {max_date}")
            
            # Test 3: Load small sample of data
            if min_date:
                start_test = datetime(2023, 1, 1)
                end_test = datetime(2023, 1, 31)
                
                try:
                    df = loader.load_symbol_data('MCL', start_test, end_test)
                    print(f"Loaded {len(df)} bars for MCL Jan 2023")
                except Exception as e:
                    print(f"Error loading MCL data: {e}")
                    import traceback
                    traceback.print_exc()
                    df = None
                
                if df is not None and not df.empty:
                    print(f"Sample data:")
                    print(df.head())
                    
                    # Test 4: Historical slice
                    end_dt = df.iloc[-1]['datetime']
                    hist_bars = loader.get_historical_slice('MCL', end_dt, 10)
                    print(f"\nHistorical slice: {len(hist_bars)} bars")
                    
                    # Test 5: TSX format conversion
                    tsx_bars = loader.convert_to_tsx_format(hist_bars[-3:])
                    print(f"\nTSX format sample:")
                    for bar in tsx_bars:
                        print(f"  {bar}")
        
        print("\n=== CSV Data Loader Test Complete ===")
        
    except Exception as e:
        print(f"Test failed: {e}")