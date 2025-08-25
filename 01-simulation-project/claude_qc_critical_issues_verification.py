#!/usr/bin/env python3
"""
CLAUDE.md COMPLIANCE: Critical QC Issues Documentation
Documents ACTUAL vs CLAIMED status with execution proof
NO UNICODE CHARACTERS to avoid the encoding crashes we're documenting
"""

import sys
import os
import time
import subprocess
import json
import redis
from datetime import datetime

# Add path for local imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

def log_with_timestamp(message, level="INFO"):
    """CLAUDE.md requirement: All logs with timestamps"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f"[{level}] {timestamp} | {message}")

def critical_issue_header(issue_name):
    """Document critical issues with session proof"""
    print(f"\n{'='*70}")
    print(f"CRITICAL ISSUE VERIFICATION: {issue_name}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Session PID: {os.getpid()}")
    print(f"Random: {time.time_ns() % 100000}")
    print(f"{'='*70}")

def test_phase2a_unicode_crash():
    """Test if Phase 2A Unicode issue is actually fixed"""
    critical_issue_header("PHASE 2A UNICODE ENCODING")
    
    log_with_timestamp("Testing if Unicode crashes still occur...")
    
    # Test 1: Direct Unicode character output
    try:
        # This should crash if Phase 2A is not actually fixed
        test_char = '\u274c'  # X mark emoji used in phase2c test
        print(f"Testing Unicode character: {test_char}")
        log_with_timestamp("ERROR: Unicode character printed - this should have crashed", "ERROR")
        return {"unicode_crash": False, "issue": "Unicode should crash but didn't"}
    except UnicodeEncodeError as e:
        log_with_timestamp(f"CONFIRMED: Unicode crash still occurs - {e}", "CRITICAL")
        return {"unicode_crash": True, "error": str(e)}
    
    # Test 2: Subprocess Unicode handling
    try:
        result = subprocess.run([
            'python', '-c', 
            'print("Test with unicode: \\u274c")'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode != 0:
            log_with_timestamp(f"Subprocess Unicode test failed: {result.stderr}", "CRITICAL")
            return {"subprocess_unicode": False, "stderr": result.stderr}
        else:
            log_with_timestamp("Subprocess Unicode test passed", "INFO")
            return {"subprocess_unicode": True, "stdout": result.stdout}
            
    except Exception as e:
        log_with_timestamp(f"Subprocess test error: {e}", "ERROR")
        return {"subprocess_error": str(e)}

def test_csv_data_with_correct_api():
    """Test CSV data using correct API method names"""
    critical_issue_header("CSV DATA WITH CORRECT API")
    
    log_with_timestamp("Testing CSV data loader with correct method names...")
    
    try:
        from claude_csv_data_loader import MonthlyCSVDataLoader
        csv_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
        
        loader = MonthlyCSVDataLoader(csv_dir)
        log_with_timestamp("CSV Data Loader initialized successfully")
        
        # Test available symbols (correct method)
        symbols = loader.get_available_symbols()
        log_with_timestamp(f"Available symbols: {symbols}")
        
        # Test MCL symbol availability (correct method)
        mcl_available = loader.is_symbol_available('MCL')
        log_with_timestamp(f"MCL symbol available: {mcl_available}")
        
        if mcl_available:
            # Test date range
            try:
                date_range = loader.get_date_range_for_symbol('MCL')
                log_with_timestamp(f"MCL date range: {date_range}")
            except Exception as e:
                log_with_timestamp(f"Date range error: {e}", "ERROR")
        
        return {
            "csv_loader_working": True,
            "symbols_found": len(symbols),
            "symbols_list": symbols,
            "mcl_available": mcl_available
        }
        
    except Exception as e:
        log_with_timestamp(f"CSV loader test failed: {e}", "ERROR")
        return {"csv_loader_working": False, "error": str(e)}

def test_historical_data_slice():
    """Test historical data slice functionality"""
    critical_issue_header("HISTORICAL DATA SLICE TEST")
    
    log_with_timestamp("Testing historical data slice with correct API...")
    
    try:
        from claude_csv_data_loader import MonthlyCSVDataLoader
        csv_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
        
        loader = MonthlyCSVDataLoader(csv_dir)
        
        # Test historical data slice (correct method)
        test_date = datetime(2023, 6, 15, 12, 0, 0)
        end_date = datetime(2023, 6, 16, 12, 0, 0)
        
        try:
            data_slice = loader.get_historical_slice('MCL', test_date, end_date)
            if data_slice is not None and len(data_slice) > 0:
                sample_row = data_slice.iloc[0] if hasattr(data_slice, 'iloc') else data_slice[0]
                log_with_timestamp(f"Historical data loaded: {len(data_slice)} records")
                log_with_timestamp(f"Sample data point: {sample_row}")
                return {
                    "historical_data_working": True,
                    "records_loaded": len(data_slice),
                    "sample_data": str(sample_row)[:200]
                }
            else:
                log_with_timestamp("No historical data returned", "WARNING")
                return {"historical_data_working": False, "issue": "No data returned"}
                
        except Exception as e:
            log_with_timestamp(f"Historical data slice error: {e}", "ERROR")
            return {"historical_data_working": False, "error": str(e)}
        
    except Exception as e:
        log_with_timestamp(f"Historical data test setup failed: {e}", "ERROR")
        return {"test_setup_failed": True, "error": str(e)}

def main():
    """Main critical issues verification"""
    print("CRITICAL QC VERIFICATION: CLAIMS vs REALITY")
    print(f"Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Session PID: {os.getpid()}")
    print(f"Random verification: {time.time_ns() % 100000}")
    
    critical_results = {}
    
    try:
        log_with_timestamp("Starting critical issues verification...")
        
        # Test Phase 2A Unicode issue
        critical_results['phase2a_unicode'] = test_phase2a_unicode_crash()
        
        # Test CSV data with correct API
        critical_results['csv_correct_api'] = test_csv_data_with_correct_api()
        
        # Test historical data functionality  
        critical_results['historical_data'] = test_historical_data_slice()
        
        # Generate critical analysis
        print(f"\n{'='*70}")
        print("CRITICAL ANALYSIS: CLAIMS vs ACTUAL RESULTS")
        print(f"{'='*70}")
        
        # Analyze Phase 2A claims vs reality
        print("\nPHASE 2A ANALYSIS:")
        print("CLAIMED: 'Subprocess communication PROPERLY FIXED - Unicode encoding crashes resolved'")
        unicode_result = critical_results.get('phase2a_unicode', {})
        if unicode_result.get('unicode_crash'):
            print("REALITY: FAILED - Unicode crashes still occurring")
            print(f"         Error: {unicode_result.get('error', 'Unknown error')}")
        else:
            print("REALITY: May be working in this context")
            
        # Analyze CSV data claims vs reality
        print("\nCSV DATA ANALYSIS:")
        print("CLAIMED: '27,777 real MCL bars loaded successfully'")
        csv_result = critical_results.get('csv_correct_api', {})
        if csv_result.get('csv_loader_working'):
            symbols = csv_result.get('symbols_found', 0)
            print(f"REALITY: CSV loader works - {symbols} symbols found")
            print(f"         Symbols: {csv_result.get('symbols_list', [])}")
        else:
            print("REALITY: FAILED - CSV loader not working")
            
        # Analyze historical data claims vs reality
        print("\nHISTORICAL DATA ANALYSIS:")
        print("CLAIMED: 'Real CSV data integration with authentic historical data'")
        hist_result = critical_results.get('historical_data', {})
        if hist_result.get('historical_data_working'):
            records = hist_result.get('records_loaded', 0)
            print(f"REALITY: WORKING - {records} historical records loaded")
        else:
            print("REALITY: FAILED - Historical data not accessible")
            
        print(f"\n{'='*70}")
        print(f"CRITICAL VERIFICATION COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"{'='*70}")
        
        return critical_results
        
    except Exception as e:
        log_with_timestamp(f"Critical verification failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return {"verification_failed": True, "error": str(e)}

if __name__ == "__main__":
    results = main()
    print("\nCRITICAL ISSUES VERIFICATION COMPLETE")
    print(f"Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")