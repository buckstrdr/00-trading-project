#!/usr/bin/env python3
"""
CSV Data Importer - Import month-by-month futures data
Purpose: Import CSV files in the specific format used by the user's data files
"""

import sys
import os
from pathlib import Path
import pandas as pd
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import glob
import logging
from concurrent.futures import ThreadPoolExecutor
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from shared.utils import setup_logging, Timer
from config.settings import DATA_DIR, SERVICE_PORTS

# Set up logging
logger = setup_logging("DataImporter", "INFO")

class CSVDataImporter:
    """Import CSV data files into the Data Service"""
    
    def __init__(self, data_service_url: str = None):
        self.data_service_url = data_service_url or f"http://localhost:{SERVICE_PORTS['data']}"
        self.db_path = DATA_DIR / "futures.db"
        
        # CSV format mapping
        self.csv_columns = {
            'Date (D)': 'date',
            'Time (T)': 'time', 
            'Open (O)': 'open',
            'High (H)': 'high',
            'Low (L)': 'low',
            'Close (C)': 'close',
            'Volume (V)': 'volume'
        }
        
        logger.info("CSV Data Importer initialized")
    
    def detect_date_format(self, date_series: pd.Series) -> str:
        """Detect if dates are in MM/DD/YYYY or DD/MM/YYYY format"""
        try:
            # Sample first 1000 dates to detect format
            sample_dates = date_series.head(1000)
            
            dd_mm_strong_indicators = 0  # Definitive indicators
            mm_dd_strong_indicators = 0
            
            for date_str in sample_dates:
                try:
                    parts = date_str.split('/')
                    if len(parts) == 3:
                        first_part = int(parts[0])
                        second_part = int(parts[1])
                        
                        # Strong indicator: first part > 12 means it's definitely day (DD/MM/YYYY)
                        if first_part > 12:
                            dd_mm_strong_indicators += 10
                        # Strong indicator: second part > 12 but first <= 12 means MM/DD/YYYY
                        elif second_part > 12 and first_part <= 12:
                            mm_dd_strong_indicators += 10
                        
                        # Also check for impossible MM/DD combinations that would indicate DD/MM
                        # For example: if we see 15/02 (15th February) vs 02/15 (February 15th)
                        if first_part > 12 and second_part <= 12:
                            dd_mm_strong_indicators += 5
                        elif first_part <= 12 and second_part > 12:
                            mm_dd_strong_indicators += 5
                            
                except ValueError:
                    continue
            
            logger.info(f"Format detection - DD/MM indicators: {dd_mm_strong_indicators}, MM/DD indicators: {mm_dd_strong_indicators}")
            
            # Decide based on strong indicators
            if dd_mm_strong_indicators > mm_dd_strong_indicators:
                return 'DD/MM/YYYY'
            elif mm_dd_strong_indicators > dd_mm_strong_indicators:
                return 'MM/DD/YYYY'
            else:
                # If no clear indicators, default to MM/DD/YYYY (US format)
                logger.info("No clear format indicators found, defaulting to MM/DD/YYYY")
                return 'MM/DD/YYYY'
                
        except Exception as e:
            logger.warning(f"Date format detection failed: {e}, defaulting to MM/DD/YYYY")
            return 'MM/DD/YYYY'
    
    def parse_csv_file(self, csv_path: Path) -> pd.DataFrame:
        """Parse a single CSV file in the specific format"""
        try:
            logger.info(f"📂 Parsing CSV file: {csv_path.name}")
            
            # Read CSV with semicolon delimiter
            df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
            
            # Validate expected columns
            expected_cols = list(self.csv_columns.keys())
            if not all(col in df.columns for col in expected_cols):
                missing = [col for col in expected_cols if col not in df.columns]
                raise ValueError(f"Missing columns in {csv_path.name}: {missing}")
            
            # Rename columns to standard format
            df = df.rename(columns=self.csv_columns)
            
            # Combine date and time into timestamp
            # Smart date format detection to handle mixed MM/DD/YYYY and DD/MM/YYYY
            datetime_str = df['date'] + ' ' + df['time']
            
            # Detect the date format by analyzing the data
            date_format = self.detect_date_format(df['date'])
            logger.info(f"Detected date format: {date_format} for {csv_path.name}")
            
            try:
                if date_format == 'DD/MM/YYYY':
                    df['timestamp'] = pd.to_datetime(datetime_str, format='%d/%m/%Y %H:%M')
                else:  # MM/DD/YYYY
                    df['timestamp'] = pd.to_datetime(datetime_str, format='%m/%d/%Y %H:%M')
            except ValueError as e:
                logger.warning(f"Date parsing failed with detected format, trying fallback for {csv_path.name}")
                # Fallback to pandas auto-detection
                df['timestamp'] = pd.to_datetime(datetime_str, format='mixed', dayfirst=(date_format == 'DD/MM/YYYY'))
            
            # Drop original date/time columns
            df = df.drop(['date', 'time'], axis=1)
            
            # Ensure proper data types
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').astype('Int64')
            
            # Remove any rows with NaN values
            initial_count = len(df)
            df = df.dropna()
            final_count = len(df)
            
            if initial_count != final_count:
                logger.warning(f"⚠️ Dropped {initial_count - final_count} invalid rows from {csv_path.name}")
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            logger.info(f"✅ Parsed {len(df)} records from {csv_path.name}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error parsing {csv_path}: {e}")
            return pd.DataFrame()
    
    def extract_symbol_from_path(self, csv_path: Path) -> str:
        """Extract symbol from file path"""
        try:
            # Path format: ../SYMBOL/YEAR/MONTH/SYMBOL_YEAR_MONTH_MonthName.csv
            # Extract symbol from the parent directory structure or filename
            path_parts = csv_path.parts
            
            # Find symbol from path - it should be in the path structure
            for part in reversed(path_parts):
                if part in ['MCL', 'MES', 'MGC', 'NG', 'SI']:
                    return part
            
            # Fallback: extract from filename
            filename = csv_path.stem  # Remove .csv extension
            if filename.startswith(('MCL_', 'MES_', 'MGC_', 'NG_', 'SI_')):
                return filename.split('_')[0]
            
            # Last resort: guess from path
            for part in path_parts:
                if part.upper() in ['MCL', 'MES', 'MGC', 'NG', 'SI']:
                    return part.upper()
                    
            raise ValueError(f"Could not extract symbol from path: {csv_path}")
            
        except Exception as e:
            logger.error(f"❌ Symbol extraction failed for {csv_path}: {e}")
            return "UNKNOWN"
    
    def import_csv_file(self, csv_path: Path, symbol: str = None) -> int:
        """Import a single CSV file"""
        try:
            # Parse the CSV
            df = self.parse_csv_file(csv_path)
            if df.empty:
                logger.warning(f"⚠️ No data to import from {csv_path}")
                return 0
            
            # Extract symbol if not provided
            if not symbol:
                symbol = self.extract_symbol_from_path(csv_path)
            
            # Import via Data Service API
            imported_count = self.import_via_api(symbol, df)
            
            if imported_count > 0:
                logger.info(f"✅ Imported {imported_count} records for {symbol} from {csv_path.name}")
            else:
                logger.warning(f"⚠️ No records imported for {symbol} from {csv_path.name}")
                
            return imported_count
            
        except Exception as e:
            logger.error(f"❌ Import failed for {csv_path}: {e}")
            return 0
    
    def import_via_api(self, symbol: str, df: pd.DataFrame) -> int:
        """Import data via Data Service API"""
        try:
            # Convert DataFrame to API format
            records = []
            for _, row in df.iterrows():
                record = {
                    'timestamp': row['timestamp'].isoformat(),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume'])
                }
                records.append(record)
            
            # Send to Data Service
            url = f"{self.data_service_url}/api/data/import"
            params = {'symbol': symbol}
            
            response = requests.post(url, params=params, json=records, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('imported_records', 0)
            else:
                logger.error(f"❌ API import failed: {response.status_code} - {response.text}")
                return 0
                
        except requests.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            # Fallback to direct database import
            return self.import_direct_to_db(symbol, df)
        except Exception as e:
            logger.error(f"❌ API import error: {e}")
            return 0
    
    def import_direct_to_db(self, symbol: str, df: pd.DataFrame) -> int:
        """Direct database import as fallback"""
        try:
            logger.info(f"🔄 Falling back to direct database import for {symbol}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO market_data 
                        (symbol, timestamp, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        row['timestamp'].isoformat(),
                        float(row['open']),
                        float(row['high']),
                        float(row['low']),
                        float(row['close']),
                        int(row['volume'])
                    ))
                    imported_count += 1
                except Exception as e:
                    logger.debug(f"Failed to import record: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Direct import completed: {imported_count} records for {symbol}")
            return imported_count
            
        except Exception as e:
            logger.error(f"❌ Direct database import failed: {e}")
            return 0
    
    def find_csv_files(self, base_path: Path, symbol: str = None, year: str = None) -> List[Path]:
        """Find CSV files matching criteria"""
        try:
            csv_files = []
            
            if symbol and year:
                # Specific symbol and year
                pattern = base_path / symbol / year / "*" / f"{symbol}_{year}_*.csv"
                csv_files = list(glob.glob(str(pattern)))
            elif symbol:
                # All years for a symbol
                pattern = base_path / symbol / "*" / "*" / f"{symbol}_*.csv"
                csv_files = list(glob.glob(str(pattern)))
            else:
                # All CSV files
                for sym in ['MCL', 'MES', 'MGC', 'NG', 'SI']:
                    pattern = base_path / sym / "*" / "*" / f"{sym}_*.csv"
                    csv_files.extend(glob.glob(str(pattern)))
            
            # Convert to Path objects and sort
            csv_paths = [Path(f) for f in csv_files if Path(f).exists()]
            csv_paths.sort()
            
            logger.info(f"📂 Found {len(csv_paths)} CSV files")
            return csv_paths
            
        except Exception as e:
            logger.error(f"❌ Error finding CSV files: {e}")
            return []
    
    def import_batch(
        self, 
        base_path: Path, 
        symbol: str = None, 
        year: str = None,
        max_workers: int = 3
    ) -> Dict[str, int]:
        """Import multiple CSV files in batch"""
        try:
            logger.info(f"🚀 Starting batch import - Symbol: {symbol or 'ALL'}, Year: {year or 'ALL'}")
            
            # Find all matching CSV files
            csv_files = self.find_csv_files(base_path, symbol, year)
            
            if not csv_files:
                logger.warning("⚠️ No CSV files found matching criteria")
                return {}
            
            # Import statistics
            results = {}
            total_imported = 0
            start_time = time.time()
            
            # Process files (using ThreadPoolExecutor for I/O bound operations)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all import tasks
                future_to_file = {
                    executor.submit(self.import_csv_file, csv_file): csv_file 
                    for csv_file in csv_files
                }
                
                # Process completed tasks
                for i, future in enumerate(future_to_file, 1):
                    csv_file = future_to_file[future]
                    try:
                        imported_count = future.result(timeout=120)  # 2 minute timeout per file
                        
                        file_symbol = self.extract_symbol_from_path(csv_file)
                        if file_symbol not in results:
                            results[file_symbol] = 0
                        results[file_symbol] += imported_count
                        total_imported += imported_count
                        
                        # Progress logging
                        if i % 10 == 0 or i == len(csv_files):
                            elapsed = time.time() - start_time
                            logger.info(f"📈 Progress: {i}/{len(csv_files)} files ({i/len(csv_files)*100:.1f}%) - {total_imported:,} total records - {elapsed:.1f}s elapsed")
                            
                    except Exception as e:
                        logger.error(f"❌ Import failed for {csv_file}: {e}")
                        continue
            
            # Final summary
            elapsed_time = time.time() - start_time
            logger.info(f"🎯 Batch import completed in {elapsed_time:.1f}s")
            logger.info(f"📊 Total records imported: {total_imported:,}")
            
            for sym, count in results.items():
                logger.info(f"  • {sym}: {count:,} records")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch import failed: {e}")
            return {}

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import CSV data files')
    parser.add_argument('data_path', help='Path to data files directory')
    parser.add_argument('--symbol', choices=['MCL', 'MES', 'MGC', 'NG', 'SI'], help='Specific symbol to import')
    parser.add_argument('--year', help='Specific year to import (e.g., 2024)')
    parser.add_argument('--workers', type=int, default=3, help='Number of parallel workers')
    parser.add_argument('--data-service', help='Data service URL', default=None)
    
    args = parser.parse_args()
    
    # Initialize importer
    importer = CSVDataImporter(data_service_url=args.data_service)
    
    # Run batch import
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"❌ Data path does not exist: {data_path}")
        return 1
    
    results = importer.import_batch(
        base_path=data_path,
        symbol=args.symbol,
        year=args.year,
        max_workers=args.workers
    )
    
    if results:
        logger.info("✅ Import completed successfully")
        return 0
    else:
        logger.error("❌ Import failed")
        return 1

if __name__ == "__main__":
    exit(main())