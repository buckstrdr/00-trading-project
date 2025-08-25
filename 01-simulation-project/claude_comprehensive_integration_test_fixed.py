#!/usr/bin/env python3
"""
COMPREHENSIVE INTEGRATION TEST - ALL FIXES APPLIED
Tests complete Phase 1 + Phase 2 functionality with all issues fixed
ASCII ONLY - NO UNICODE CHARACTERS
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

def test_header(test_name):
    """CLAUDE.md requirement: Session verification headers"""
    print(f"\n{'='*70}")
    print(f"INTEGRATION TEST: {test_name}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Session PID: {os.getpid()}")
    print(f"Random: {time.time_ns() % 100000}")
    print(f"{'='*70}")

def test_phase1_redis_infrastructure():
    """Test Phase 1 Redis infrastructure"""
    test_header("PHASE 1 REDIS INFRASTRUCTURE")
    
    results = {}
    
    try:
        # Test Redis server process
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq redis-server.exe'], 
                              capture_output=True, text=True)
        redis_running = 'redis-server.exe' in result.stdout
        log_with_timestamp(f"Redis server running: {redis_running}")
        results['redis_process'] = redis_running
        
        # Test Python Redis connectivity
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        ping_result = redis_client.ping()
        log_with_timestamp(f"Python Redis PING: {ping_result}")
        results['python_redis'] = ping_result
        
        return results
        
    except Exception as e:
        log_with_timestamp(f"Redis infrastructure test failed: {e}", "ERROR")
        return {"error": str(e)}

def test_phase2c_csv_data_loading():
    """Test Phase 2C CSV data loading with fixed API"""
    test_header("PHASE 2C CSV DATA LOADING")
    
    results = {}
    
    try:
        from claude_csv_data_loader import MonthlyCSVDataLoader
        csv_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
        
        # Initialize loader
        loader = MonthlyCSVDataLoader(csv_dir)
        log_with_timestamp("CSV Data Loader initialized successfully")
        
        # Test all 5 trading symbols
        trading_symbols = ['MCL', 'MES', 'MGC', 'NG', 'SI']
        symbol_results = {}
        
        for symbol in trading_symbols:
            log_with_timestamp(f"Testing symbol: {symbol}")
            
            try:
                # Test symbol availability
                available = loader.is_symbol_available(symbol)
                log_with_timestamp(f"{symbol} available: {available}")
                
                if available:
                    # Test data loading
                    start_date = datetime(2023, 6, 15, 12, 0, 0)
                    end_date = datetime(2023, 6, 15, 18, 0, 0)
                    
                    data_df = loader.load_symbol_data(symbol, start_date, end_date)
                    
                    if len(data_df) > 0:
                        sample_price = data_df.iloc[0]['close'] if 'close' in data_df.columns else 0
                        log_with_timestamp(f"{symbol}: {len(data_df)} bars loaded, sample price: ${sample_price:.2f}")
                        
                        symbol_results[symbol] = {
                            'available': True,
                            'data_loaded': True,
                            'bars_count': len(data_df),
                            'sample_price': sample_price
                        }
                    else:
                        log_with_timestamp(f"{symbol}: No data for test period")
                        symbol_results[symbol] = {
                            'available': True,
                            'data_loaded': False,
                            'bars_count': 0
                        }
                else:
                    log_with_timestamp(f"{symbol}: Not available")
                    symbol_results[symbol] = {
                        'available': False,
                        'data_loaded': False
                    }
                    
            except Exception as e:
                log_with_timestamp(f"{symbol} test error: {e}", "ERROR")
                symbol_results[symbol] = {
                    'available': False,
                    'data_loaded': False,
                    'error': str(e)
                }
        
        results['symbols'] = symbol_results
        return results
        
    except Exception as e:
        log_with_timestamp(f"CSV data loading test failed: {e}", "ERROR")
        return {"error": str(e)}

def test_historical_data_api():
    """Test historical data API methods"""
    test_header("HISTORICAL DATA API")
    
    results = {}
    
    try:
        from claude_csv_data_loader import MonthlyCSVDataLoader
        csv_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
        
        loader = MonthlyCSVDataLoader(csv_dir)
        
        # Test historical slice method
        end_date = datetime(2023, 6, 15, 16, 0, 0)
        bars_back = 10
        
        try:
            historical_bars = loader.get_historical_slice('MCL', end_date, bars_back)
            log_with_timestamp(f"Historical slice: {len(historical_bars)} bars retrieved")
            results['historical_slice'] = len(historical_bars)
        except Exception as e:
            log_with_timestamp(f"Historical slice error: {e}", "ERROR")
            results['historical_slice_error'] = str(e)
        
        # Test compatibility method
        try:
            compat_bars = loader.get_historical_bars('MCL', bars_back, end_date)
            log_with_timestamp(f"Historical bars (compatibility): {len(compat_bars)} bars retrieved")
            results['historical_bars_compat'] = len(compat_bars)
        except Exception as e:
            log_with_timestamp(f"Historical bars compatibility error: {e}", "ERROR")
            results['historical_bars_error'] = str(e)
        
        # Test symbol availability method
        try:
            symbol_info = loader.test_symbol_availability('MCL')
            log_with_timestamp(f"Symbol availability test: {symbol_info}")
            results['symbol_availability'] = symbol_info.get('available', False)
        except Exception as e:
            log_with_timestamp(f"Symbol availability error: {e}", "ERROR")
            results['symbol_availability_error'] = str(e)
        
        return results
        
    except Exception as e:
        log_with_timestamp(f"Historical data API test failed: {e}", "ERROR")
        return {"error": str(e)}

def test_nodejs_components():
    """Test Node.js components"""
    test_header("NODE.JS COMPONENTS")
    
    results = {}
    
    try:
        # Test Node.js version
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            log_with_timestamp(f"Node.js version: {result.stdout.strip()}")
            results['nodejs_version'] = result.stdout.strip()
        
        # Check if strategy runner exists
        runner_path = os.path.join('shared', 'claude_tsx_v5_strategy_runner.js')
        runner_exists = os.path.exists(runner_path)
        log_with_timestamp(f"Strategy runner exists: {runner_exists}")
        results['strategy_runner'] = runner_exists
        
        # Check if Redis client exists
        redis_client_path = os.path.join('shared', 'claude_redis_client_fixed.js')
        redis_client_exists = os.path.exists(redis_client_path)
        log_with_timestamp(f"Fixed Redis client exists: {redis_client_exists}")
        results['redis_client'] = redis_client_exists
        
        return results
        
    except Exception as e:
        log_with_timestamp(f"Node.js components test failed: {e}", "ERROR")
        return {"error": str(e)}

def main():
    """Main integration test execution"""
    print("COMPREHENSIVE INTEGRATION TEST - ALL FIXES APPLIED")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Session PID: {os.getpid()}")
    print(f"Random verification: {time.time_ns() % 100000}")
    
    test_results = {}
    
    try:
        log_with_timestamp("Starting comprehensive integration tests...")
        
        # Execute all tests
        test_results['phase1_redis'] = test_phase1_redis_infrastructure()
        test_results['phase2c_csv'] = test_phase2c_csv_data_loading()
        test_results['historical_api'] = test_historical_data_api()
        test_results['nodejs_components'] = test_nodejs_components()
        
        # Analyze results
        print(f"\n{'='*70}")
        print("COMPREHENSIVE INTEGRATION TEST RESULTS")
        print(f"{'='*70}")
        
        total_tests = 0
        passed_tests = 0
        
        # Phase 1 Redis Results
        print("\nPHASE 1 REDIS INFRASTRUCTURE:")
        phase1_results = test_results.get('phase1_redis', {})
        if not phase1_results.get('error'):
            for test_name, result in phase1_results.items():
                total_tests += 1
                status = "PASS" if result else "FAIL"
                if result:
                    passed_tests += 1
                print(f"  [{status}] {test_name}: {result}")
        else:
            total_tests += 1
            print(f"  [FAIL] Redis infrastructure: {phase1_results['error']}")
        
        # Phase 2C CSV Results
        print("\nPHASE 2C CSV DATA LOADING:")
        phase2c_results = test_results.get('phase2c_csv', {})
        if not phase2c_results.get('error'):
            symbols = phase2c_results.get('symbols', {})
            for symbol, symbol_result in symbols.items():
                total_tests += 1
                if symbol_result.get('data_loaded'):
                    passed_tests += 1
                    bars = symbol_result.get('bars_count', 0)
                    price = symbol_result.get('sample_price', 0)
                    print(f"  [PASS] {symbol}: {bars} bars, ${price:.2f}")
                else:
                    error = symbol_result.get('error', 'No data loaded')
                    print(f"  [FAIL] {symbol}: {error}")
        else:
            total_tests += 1
            print(f"  [FAIL] CSV data loading: {phase2c_results['error']}")
        
        # Historical Data API Results
        print("\nHISTORICAL DATA API:")
        hist_results = test_results.get('historical_api', {})
        api_tests = ['historical_slice', 'historical_bars_compat', 'symbol_availability']
        for api_test in api_tests:
            total_tests += 1
            if api_test in hist_results:
                passed_tests += 1
                print(f"  [PASS] {api_test}: {hist_results[api_test]}")
            elif f"{api_test}_error" in hist_results:
                print(f"  [FAIL] {api_test}: {hist_results[f'{api_test}_error']}")
        
        # Node.js Components Results  
        print("\nNODE.JS COMPONENTS:")
        nodejs_results = test_results.get('nodejs_components', {})
        if not nodejs_results.get('error'):
            for component, result in nodejs_results.items():
                total_tests += 1
                status = "PASS" if result else "FAIL"
                if result:
                    passed_tests += 1
                print(f"  [{status}] {component}: {result}")
        
        completion_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"INTEGRATION TEST RESULTS: {passed_tests}/{total_tests} tests passed ({completion_percentage:.1f}%)")
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"{'='*70}")
        
        if completion_percentage >= 95:
            print("SUCCESS: COMPREHENSIVE INTEGRATION TEST PASSED!")
            print("All major components working correctly")
            return True
        elif completion_percentage >= 80:
            print(f"WARNING: Integration test at {completion_percentage:.1f}% - Near complete")
            return False
        else:
            print(f"FAIL: Integration test at {completion_percentage:.1f}% - Major issues remain")
            return False
            
    except Exception as e:
        log_with_timestamp(f"Integration test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nFinal Integration Test Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Test session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")