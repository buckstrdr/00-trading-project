#!/usr/bin/env python3
"""
Debug CSV Date Parsing Issue
"""

import csv
from datetime import datetime

def debug_csv_parsing():
    csv_file = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files\MCL\2023\01-January\MCL_2023_01_January.csv"
    
    print("=== Debug CSV Parsing ===")
    print(f"Testing file: {csv_file}")
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for i, row in enumerate(reader):
                if i >= 3:  # Test first 3 rows
                    break
                    
                print(f"\nRow {i+1}: {row}")
                
                # Extract values
                date_str = row['Date (D)'].strip()
                time_str = row['Time (T)'].strip()
                
                print(f"  Date string: '{date_str}' (type: {type(date_str)})")
                print(f"  Time string: '{time_str}' (type: {type(time_str)})")
                
                # Test datetime parsing
                try:
                    dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
                    print(f"  Parsed datetime: {dt}")
                    print(f"  Success!")
                except Exception as e:
                    print(f"  Parse error: {e}")
                    
                    # Try alternative formats
                    try:
                        dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M")
                        print(f"  Alternative format worked: {dt}")
                    except Exception as e2:
                        print(f"  Alternative format failed: {e2}")
    
    except Exception as e:
        print(f"File read error: {e}")

if __name__ == "__main__":
    debug_csv_parsing()