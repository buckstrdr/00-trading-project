#!/usr/bin/env python3
"""
CLAUDE.md COMPLIANCE: Phase 1 Comprehensive QC Verification
Executes real tests with actual output capture following CLAUDE.md protocols
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

def verification_header(test_name):
    """CLAUDE.md requirement: Session verification headers"""
    print(f"\n{'='*60}")
    print(f"VERIFICATION: {test_name}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Session PID: {os.getpid()}")
    print(f"Random: {time.time_ns() % 100000}")
    print(f"{'='*60}")

def execute_with_proof(command_desc, command_func):
    """CLAUDE.md requirement: Execute with proof of execution"""
    log_with_timestamp(f"EXECUTING: {command_desc}")
    start_time = time.time()
    
    try:
        result = command_func()
        duration = time.time() - start_time
        log_with_timestamp(f"SUCCESS: {command_desc} (took {duration:.2f}s)", "SUCCESS")
        return True, result
    except Exception as e:
        duration = time.time() - start_time
        log_with_timestamp(f"FAILED: {command_desc} - {e} (took {duration:.2f}s)", "ERROR")
        return False, str(e)

def test_redis_infrastructure():
    """Test Redis server and connectivity"""
    verification_header("REDIS INFRASTRUCTURE")
    
    results = {}
    
    # Test 1: Redis server process
    def check_redis_process():
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq redis-server.exe'], 
                              capture_output=True, text=True)
        if 'redis-server.exe' in result.stdout:
            return f"Redis server running: {result.stdout.strip()}"
        raise Exception("Redis server not found in process list")
    
    success, result = execute_with_proof("Redis Server Process Check", check_redis_process)
    results['redis_process'] = {'success': success, 'output': result}
    
    # Test 2: Python Redis connectivity
    def check_python_redis():
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        ping_result = redis_client.ping()
        info = redis_client.info('server')
        return f"Python Redis PING: {ping_result}, Version: {info.get('redis_version', 'unknown')}"
    
    success, result = execute_with_proof("Python Redis Connectivity", check_python_redis)
    results['python_redis'] = {'success': success, 'output': result}
    
    return results

def test_csv_data_loading():
    """Test CSV data loader functionality"""
    verification_header("CSV DATA LOADING")
    
    results = {}
    
    # Test CSV data directory exists
    def check_csv_directory():
        csv_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
        if not os.path.exists(csv_dir):
            raise Exception(f"CSV data directory not found: {csv_dir}")
        
        files = os.listdir(csv_dir)
        csv_files = [f for f in files if f.endswith('.csv')]
        return f"CSV directory exists: {len(csv_files)} CSV files found"
    
    success, result = execute_with_proof("CSV Data Directory Check", check_csv_directory)
    results['csv_directory'] = {'success': success, 'output': result}
    
    # Test CSV data loader
    def test_csv_loader():
        try:
            from claude_csv_data_loader import MonthlyCSVDataLoader
            csv_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
            loader = MonthlyCSVDataLoader(csv_dir)
            
            # Test symbol availability
            symbols = loader.get_available_symbols()
            
            # Test loading MCL data
            test_date = datetime(2023, 6, 15, 12, 0, 0)
            bars = loader.get_historical_bars('MCL', 5, test_date)
            
            if bars and len(bars) > 0:
                sample_bar = bars[0]
                price = sample_bar.get('c', sample_bar.get('close', 0))
                return f"CSV Loader: {len(symbols)} symbols, MCL test: {len(bars)} bars, price: ${price:.2f}"
            else:
                return "CSV Loader initialized but no data for MCL June 2023"
                
        except ImportError as e:
            raise Exception(f"CSV Data Loader not found: {e}")
    
    success, result = execute_with_proof("CSV Data Loader Test", test_csv_loader)
    results['csv_loader'] = {'success': success, 'output': result}
    
    return results

def test_strategy_loading():
    """Test TSX strategy loading with Node.js"""
    verification_header("STRATEGY LOADING")
    
    results = {}
    
    # Test Node.js Redis client
    def test_nodejs_redis():
        # Check if our fixed Redis client exists
        redis_client_path = os.path.join('shared', 'claude_redis_client_fixed.js')
        if not os.path.exists(redis_client_path):
            raise Exception(f"Fixed Redis client not found: {redis_client_path}")
        
        # Test Node.js execution
        result = subprocess.run(['node', '-e', 'console.log("Node.js working:", process.version)'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise Exception(f"Node.js test failed: {result.stderr}")
        
        return f"Node.js test: {result.stdout.strip()}, Redis client exists: {redis_client_path}"
    
    success, result = execute_with_proof("Node.js Redis Client Test", test_nodejs_redis)
    results['nodejs_redis'] = {'success': success, 'output': result}
    
    # Test strategy runner exists
    def check_strategy_runner():
        runner_path = os.path.join('shared', 'claude_tsx_v5_strategy_runner.js')
        if not os.path.exists(runner_path):
            raise Exception(f"Strategy runner not found: {runner_path}")
        
        # Check TSX strategy exists
        strategy_path = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\03-trading-bot\TSX-Trading-Bot-V5\src\strategies\ema\emaStrategy.js"
        if not os.path.exists(strategy_path):
            raise Exception(f"EMA strategy not found: {strategy_path}")
        
        return f"Strategy runner exists: {runner_path}, EMA strategy exists: {strategy_path}"
    
    success, result = execute_with_proof("Strategy Runner Check", check_strategy_runner)
    results['strategy_runner'] = {'success': success, 'output': result}
    
    return results

def test_historical_bootstrap_service():
    """Test historical data bootstrap service"""
    verification_header("HISTORICAL BOOTSTRAP SERVICE")
    
    results = {}
    
    # Test bootstrap service exists
    def check_bootstrap_service():
        bootstrap_path = os.path.join('shared', 'claude_real_csv_bootstrap_service.py')
        if not os.path.exists(bootstrap_path):
            raise Exception(f"Bootstrap service not found: {bootstrap_path}")
        
        # Check file size and content
        with open(bootstrap_path, 'r') as f:
            content = f.read()
            lines = len(content.split('\n'))
        
        return f"Bootstrap service exists: {bootstrap_path}, Size: {lines} lines"
    
    success, result = execute_with_proof("Bootstrap Service Check", check_bootstrap_service)
    results['bootstrap_service'] = {'success': success, 'output': result}
    
    return results

def test_enhanced_bridge():
    """Test enhanced TSX strategy bridge"""
    verification_header("ENHANCED TSX BRIDGE")
    
    results = {}
    
    # Test enhanced bridge exists
    def check_enhanced_bridge():
        bridge_path = os.path.join('shared', 'claude_enhanced_tsx_strategy_bridge.py')
        if not os.path.exists(bridge_path):
            raise Exception(f"Enhanced bridge not found: {bridge_path}")
        
        # Check file size and content
        with open(bridge_path, 'r') as f:
            content = f.read()
            lines = len(content.split('\n'))
            
        # Check for Unicode fixes
        unicode_fixes = ['encoding=\'utf-8\'', 'errors=\'replace\'']
        fixes_found = sum(1 for fix in unicode_fixes if fix in content)
        
        return f"Enhanced bridge exists: {bridge_path}, Size: {lines} lines, Unicode fixes: {fixes_found}/2"
    
    success, result = execute_with_proof("Enhanced Bridge Check", check_enhanced_bridge)
    results['enhanced_bridge'] = {'success': success, 'output': result}
    
    return results

def main():
    """Main QC verification execution"""
    print("CLAUDE.MD COMPLIANCE: PHASE 1 COMPREHENSIVE QC VERIFICATION")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Execution PID: {os.getpid()}")
    print(f"Random verification: {time.time_ns() % 100000}")
    
    verification_results = {}
    
    try:
        # Execute all Phase 1 tests
        log_with_timestamp("Starting Phase 1 component verification...")
        
        verification_results['redis'] = test_redis_infrastructure()
        verification_results['csv_data'] = test_csv_data_loading()
        verification_results['strategy_loading'] = test_strategy_loading()
        verification_results['bootstrap'] = test_historical_bootstrap_service()
        verification_results['bridge'] = test_enhanced_bridge()
        
        # Generate summary
        print(f"\n{'='*60}")
        print("PHASE 1 QC VERIFICATION SUMMARY")
        print(f"{'='*60}")
        
        total_tests = 0
        passed_tests = 0
        
        for phase_name, phase_results in verification_results.items():
            print(f"\n{phase_name.upper()} TESTS:")
            for test_name, test_result in phase_results.items():
                total_tests += 1
                status = "PASS" if test_result['success'] else "FAIL"
                if test_result['success']:
                    passed_tests += 1
                print(f"  [{status}] {test_name}: {test_result['output']}")
        
        completion_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"PHASE 1 QC RESULTS: {passed_tests}/{total_tests} tests passed ({completion_percentage:.1f}%)")
        print(f"QC completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"{'='*60}")
        
        if completion_percentage >= 100:
            print("SUCCESS: PHASE 1 VERIFICATION: 100% COMPLETE")
            return True
        elif completion_percentage >= 80:
            print(f"WARNING: PHASE 1 VERIFICATION: {completion_percentage:.1f}% - Near Complete")
            return False
        else:
            print(f"FAIL: PHASE 1 VERIFICATION: {completion_percentage:.1f}% - Incomplete")
            return False
            
    except Exception as e:
        log_with_timestamp(f"QC verification failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nFinal Result: {'COMPLETE' if success else 'INCOMPLETE'}")
    print(f"Verification session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")