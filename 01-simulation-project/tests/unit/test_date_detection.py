#!/usr/bin/env python3
"""
Test the improved date detection logic
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "scripts"))

from data_importer import CSVDataImporter

def test_date_detection():
    """Test date format detection on actual CSV files"""
    
    importer = CSVDataImporter()
    
    # Test files we know have different formats
    test_files = [
        Path(r"C:\Users\salte\ClaudeProjects\github-repos\month by month data files\MCL\2024\01-January\MCL_2024_01_January.csv"),
        Path(r"C:\Users\salte\ClaudeProjects\github-repos\month by month data files\MCL\2024\04-April\MCL_2024_04_April.csv"),
        Path(r"C:\Users\salte\ClaudeProjects\github-repos\month by month data files\MCL\2024\07-July\MCL_2024_07_July.csv"),
    ]
    
    for test_file in test_files:
        if test_file.exists():
            print(f"\n=== Testing {test_file.name} ===")
            
            # Parse just to get the date detection
            df = importer.parse_csv_file(test_file)
            if not df.empty:
                print(f"[OK] Successfully parsed {len(df)} records")
                print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            else:
                print(f"[ERROR] Failed to parse file")
        else:
            print(f"[ERROR] File not found: {test_file}")

if __name__ == "__main__":
    test_date_detection()