#!/usr/bin/env python3
"""
Test Symbol Error Handling - NQ should return error, not substitute with MCL
"""

import sys
import os
from datetime import datetime

sys.path.append('shared')
from claude_csv_data_loader import MonthlyCSVDataLoader

def test_symbol_error_handling():
    print("=== Testing Symbol Error Handling ===")
    
    data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    loader = MonthlyCSVDataLoader(data_dir)
    
    # Test 1: Valid symbol (MCL)
    print("\n[TEST 1] Valid symbol - MCL:")
    try:
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        df = loader.load_symbol_data('MCL', start_date, end_date)
        print(f"SUCCESS: MCL loaded {len(df)} bars")
    except Exception as e:
        print(f"FAIL: MCL should be available: {e}")
    
    # Test 2: Invalid symbol (NQ) - Should error, not substitute
    print("\n[TEST 2] Invalid symbol - NQ (should error):")
    try:
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        df = loader.load_symbol_data('NQ', start_date, end_date)
        print(f"FAIL: NQ should have returned error, but got {len(df)} bars")
    except ValueError as e:
        print(f"SUCCESS: NQ correctly returned error: {e}")
    except Exception as e:
        print(f"UNEXPECTED: Unexpected error type: {e}")
    
    # Test 3: Historical slice with invalid symbol
    print("\n[TEST 3] Historical slice with invalid symbol - NQ:")
    try:
        end_date = datetime(2023, 1, 15)
        bars = loader.get_historical_slice('NQ', end_date, 50)
        print(f"FAIL: NQ historical slice should have errored, but got {len(bars)} bars")
    except ValueError as e:
        print(f"SUCCESS: NQ historical slice correctly returned error: {e}")
    except Exception as e:
        print(f"UNEXPECTED: Unexpected error type: {e}")
    
    # Test 4: Check available symbols
    print("\n[TEST 4] Available symbols:")
    available = loader.get_available_symbols()
    print(f"Available symbols: {available}")
    print(f"NQ in available: {'NQ' in available}")
    print(f"MCL in available: {'MCL' in available}")
    
    # Test 5: Symbol availability checks
    print("\n[TEST 5] Symbol availability checks:")
    print(f"is_symbol_available('NQ'): {loader.is_symbol_available('NQ')}")
    print(f"is_symbol_available('MCL'): {loader.is_symbol_available('MCL')}")
    print(f"is_symbol_available('MES'): {loader.is_symbol_available('MES')}")
    
    print("\n=== Symbol Error Handling Test Complete ===")

if __name__ == "__main__":
    test_symbol_error_handling()