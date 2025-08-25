#!/usr/bin/env python3
"""
QC Phase 2C: Multi-Symbol CSV Support Verification - UNICODE FIXED
Tests all 5 trading symbols (MCL, MES, MGC, NG, SI) with real CSV data
NO UNICODE CHARACTERS - ASCII ONLY
"""

import sys
import os
import time
from datetime import datetime

# Add path for local imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from claude_csv_data_loader import MonthlyCSVDataLoader

def qc_multisymbol_csv_support():
    """
    QC all 5 trading symbols with real CSV data integration
    """
    print("=== QC PHASE 2C: MULTI-SYMBOL CSV SUPPORT (FIXED) ===")
    print(f"QC Start Time: {datetime.now()}")
    print(f"QC Session PID: {os.getpid()}")
    
    csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    
    # Test all trading symbols
    trading_symbols = ['MCL', 'MES', 'MGC', 'NG', 'SI']
    
    symbol_results = {}
    
    try:
        print(f"\n[QC TEST] Initializing CSV Data Loader...")
        data_loader = MonthlyCSVDataLoader(csv_data_dir)
        
        available_symbols = data_loader.get_available_symbols()
        print(f"Available symbols: {available_symbols}")
        
        print(f"\n[QC TEST] Testing all 5 trading symbols...")
        
        for symbol in trading_symbols:
            print(f"\n--- Testing Symbol: {symbol} ---")
            
            try:
                # Test symbol availability (correct method)
                symbol_available = data_loader.is_symbol_available(symbol)
                
                if symbol_available:
                    print(f"[PASS] {symbol}: Available")
                    
                    # Get date range
                    try:
                        date_range = data_loader.get_date_range_for_symbol(symbol)
                        print(f"  Date range: {date_range}")
                    except Exception as e:
                        print(f"  Date range error: {e}")
                    
                    # Test data loading with historical date (June 2023) 
                    start_date = datetime(2023, 6, 15, 12, 0, 0)
                    end_date = datetime(2023, 6, 15, 18, 0, 0)
                    
                    try:
                        data_slice = data_loader.load_symbol_data(symbol, start_date, end_date)
                        
                        if data_slice is not None and len(data_slice) > 0:
                            # Get sample price from DataFrame
                            if hasattr(data_slice, 'iloc') and len(data_slice) > 0:
                                sample_row = data_slice.iloc[0]
                                # Try different column names for price
                                price = 0
                                for col in ['Close', 'C', 'close', 'c']:
                                    if col in sample_row:
                                        price = sample_row[col]
                                        break
                                
                                print(f"[PASS] {symbol}: Data loaded - {len(data_slice)} bars")
                                print(f"  Sample price: ${price:.2f}")
                                print(f"  Columns: {list(data_slice.columns)}")
                                
                                symbol_results[symbol] = {
                                    'available': True,
                                    'data_loaded': True,
                                    'bars_count': len(data_slice),
                                    'sample_price': price
                                }
                            else:
                                print(f"[WARN] {symbol}: Data structure unexpected")
                                symbol_results[symbol] = {
                                    'available': True,
                                    'data_loaded': False,
                                    'bars_count': 0,
                                    'sample_price': 0,
                                    'issue': 'Data structure unexpected'
                                }
                        else:
                            print(f"[WARN] {symbol}: No data for June 2023")
                            symbol_results[symbol] = {
                                'available': True,
                                'data_loaded': False,
                                'bars_count': 0,
                                'sample_price': 0,
                                'issue': 'No data for test period'
                            }
                    except Exception as e:
                        print(f"[FAIL] {symbol}: Data loading error - {e}")
                        symbol_results[symbol] = {
                            'available': True,
                            'data_loaded': False,
                            'error': str(e)
                        }
                else:
                    print(f"[FAIL] {symbol}: Not available")
                    symbol_results[symbol] = {
                        'available': False,
                        'data_loaded': False,
                        'bars_count': 0,
                        'sample_price': 0
                    }
                    
            except Exception as e:
                print(f"[FAIL] {symbol}: Error - {e}")
                symbol_results[symbol] = {
                    'available': False,
                    'data_loaded': False,
                    'error': str(e)
                }
        
        print(f"\n=== PHASE 2C MULTI-SYMBOL QC RESULTS ===")
        
        working_symbols = 0
        total_symbols = len(trading_symbols)
        
        for symbol, result in symbol_results.items():
            if result.get('available', False) and result.get('data_loaded', False):
                status = "PASS"
                working_symbols += 1
                price = result.get('sample_price', 0)
                bars = result.get('bars_count', 0)
                print(f"  [PASS] {symbol}: {bars} bars, ${price:.2f} sample price")
            else:
                status = "FAIL"
                error = result.get('error', result.get('issue', 'Data not loaded'))
                print(f"  [FAIL] {symbol}: {error}")
        
        completion_percentage = (working_symbols / total_symbols) * 100
        
        print(f"\nMulti-Symbol Support: {working_symbols}/{total_symbols} ({completion_percentage:.1f}%)")
        
        if completion_percentage >= 100:
            print("SUCCESS: PHASE 2C IS 100% COMPLETE!")
            print("All trading symbols available with real CSV data")
            return True
        elif completion_percentage >= 80:
            print(f"NEAR COMPLETE: Phase 2C at {completion_percentage:.1f}%")
            return False
        else:
            print(f"INCOMPLETE: Phase 2C at {completion_percentage:.1f}%")
            return False
            
    except Exception as e:
        print(f"Multi-symbol QC test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = qc_multisymbol_csv_support()
    print(f"\nPhase 2C QC Result: {'COMPLETE' if success else 'INCOMPLETE'}")
    print(f"QC completed at: {datetime.now()}")