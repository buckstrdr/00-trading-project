#!/usr/bin/env python3
"""
Data Import Convenience Script
Usage: python import_data.py [options]
"""

import sys
from pathlib import Path
import argparse

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts"))

from data_importer import CSVDataImporter
from shared.utils import setup_logging

def main():
    """Main entry point with user-friendly interface"""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Import month-by-month CSV futures data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python import_data.py                                    # Import all data
  python import_data.py --symbol MCL                       # Import only MCL data
  python import_data.py --symbol MCL --year 2024          # Import MCL 2024 data
  python import_data.py --data-path "C:/path/to/data"     # Custom data path
  python import_data.py --test-sample                     # Import small test sample

Symbols available: MCL, MES, MGC, NG, SI
        """
    )
    
    parser.add_argument(
        '--data-path', 
        default=r'C:\Users\salte\ClaudeProjects\github-repos\month by month data files',
        help='Path to month-by-month data files directory'
    )
    
    parser.add_argument(
        '--symbol', 
        choices=['MCL', 'MES', 'MGC', 'NG', 'SI'],
        help='Import specific symbol only'
    )
    
    parser.add_argument(
        '--year',
        help='Import specific year only (e.g., 2024)'
    )
    
    parser.add_argument(
        '--test-sample',
        action='store_true',
        help='Import small test sample (MCL 2024 January only)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='Number of parallel workers (default: 3)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be imported without actually importing'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging("ImportData", "INFO")
    
    # Validate data path
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"❌ Data path does not exist: {data_path}")
        logger.info("💡 Please check the path or use --data-path to specify correct location")
        return 1
    
    # Test sample override
    if args.test_sample:
        args.symbol = 'MCL'
        args.year = '2024'
        logger.info("🧪 Test sample mode: importing MCL 2024 data only")
    
    # Display import plan
    logger.info("📋 Import Plan:")
    logger.info(f"  • Data Path: {data_path}")
    logger.info(f"  • Symbol: {args.symbol or 'ALL'}")
    logger.info(f"  • Year: {args.year or 'ALL'}")
    logger.info(f"  • Workers: {args.workers}")
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No data will be imported")
        # Find files that would be processed
        importer = CSVDataImporter()
        csv_files = importer.find_csv_files(data_path, args.symbol, args.year)
        
        logger.info(f"📂 Found {len(csv_files)} CSV files that would be imported:")
        
        # Group by symbol for display
        by_symbol = {}
        for csv_file in csv_files[:20]:  # Show first 20
            symbol = importer.extract_symbol_from_path(csv_file)
            if symbol not in by_symbol:
                by_symbol[symbol] = []
            by_symbol[symbol].append(csv_file.name)
        
        for symbol, files in by_symbol.items():
            logger.info(f"  • {symbol}: {len(files)} files")
            for file in files[:3]:  # Show first 3 files per symbol
                logger.info(f"    - {file}")
            if len(files) > 3:
                logger.info(f"    ... and {len(files) - 3} more files")
        
        if len(csv_files) > 20:
            logger.info(f"    ... and {len(csv_files) - 20} more files total")
        
        logger.info("✅ Dry run completed")
        return 0
    
    # Confirm import if large operation
    if not args.symbol and not args.year:
        logger.warning("⚠️ This will import ALL available data - this may take significant time")
        response = input("Continue? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            logger.info("❌ Import cancelled by user")
            return 0
    
    # Initialize importer and run
    try:
        logger.info("🚀 Starting data import...")
        
        importer = CSVDataImporter()
        
        results = importer.import_batch(
            base_path=data_path,
            symbol=args.symbol,
            year=args.year,
            max_workers=args.workers
        )
        
        if results:
            logger.info("✅ Import completed successfully!")
            total_records = sum(results.values())
            logger.info(f"📊 Summary: {total_records:,} total records imported")
            
            for symbol, count in results.items():
                logger.info(f"  • {symbol}: {count:,} records")
            
            return 0
        else:
            logger.error("❌ Import failed - no data imported")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("⚠️ Import interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Import failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())