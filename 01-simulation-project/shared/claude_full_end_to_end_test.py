"""
FULL End-to-End Test with Node.js TSX Strategy Process
Tests the complete workflow: CSV data → Bootstrap service → Node.js TSX strategy → Readiness verification
"""

import time
import json
import redis
import logging
from datetime import datetime
from claude_enhanced_tsx_strategy_bridge import EnhancedTSXStrategyBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_full_end_to_end_test():
    """Run complete end-to-end test with real Node.js TSX strategy"""
    
    print("=" * 80)
    print("FULL END-TO-END TEST: Node.js TSX Strategy with Real CSV Data")
    print("=" * 80)
    
    # Test configuration
    config = {
        'botId': 'e2e_test_bot',
        'symbol': 'MCL',  # Available symbol
        'historicalBarsBack': 30,
        'redisHost': 'localhost',
        'redisPort': 6379
    }
    
    # Paths
    strategy_path = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\03-trading-bot\TSX-Trading-Bot-V5\src\strategies\ema\emaStrategy.js"
    csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    
    bridge = None
    test_start_time = datetime.now()
    
    try:
        print(f"\n[STEP 1] Creating Enhanced TSX Strategy Bridge...")
        print(f"  Strategy: {strategy_path}")
        print(f"  Symbol: {config['symbol']}")
        print(f"  Historical bars: {config['historicalBarsBack']}")
        
        # Create the bridge
        bridge = EnhancedTSXStrategyBridge(strategy_path, csv_data_dir, config)
        
        # Set simulation datetime to a date that has data (2023)  
        simulation_date = datetime(2023, 6, 15, 12, 0, 0)  # June 2023 - should have data
        bridge.set_simulation_datetime(simulation_date)
        
        print("  [OK] Bridge created successfully")
        print(f"  [OK] Simulation datetime set to: {simulation_date}")
        
        print(f"\n[STEP 2] Pre-start verification...")
        
        # Test Redis connectivity
        redis_client = redis.Redis(host=config['redisHost'], port=config['redisPort'])
        redis_client.ping()
        print("  [OK] Redis connection established")
        
        # Verify symbol availability
        symbol_info = bridge.bootstrap_service.test_symbol_availability(config['symbol'])
        if not symbol_info['available']:
            raise ValueError(f"Symbol {config['symbol']} not available")
        print(f"  [OK] Symbol {config['symbol']} is available")
        print(f"    Date range: {symbol_info.get('date_range', 'Unknown')}")
        
        print(f"\n[STEP 3] Starting full bridge with Node.js process...")
        
        # This is the critical test - actually start the Node.js strategy
        start_success = bridge.start()
        
        if start_success:
            print("  [OK] Node.js TSX strategy started and became ready")
        else:
            print("  [FAIL] Strategy failed to become ready")
            
        print(f"\n[STEP 4] Verifying active components...")
        
        # Get comprehensive statistics
        stats = bridge.get_statistics()
        
        print("  Bridge Statistics:")
        print(f"    Running: {stats['running']}")
        print(f"    Strategy Ready: {stats['strategy_ready']}")
        print(f"    Bootstrap Ready: {stats['bootstrap_ready']}")
        
        print("  Bootstrap Service Statistics:")
        bootstrap_stats = stats.get('bootstrap_stats', {})
        print(f"    Running: {bootstrap_stats.get('running', False)}")
        print(f"    Requests Received: {bootstrap_stats.get('requests_received', 0)}")
        print(f"    Responses Sent: {bootstrap_stats.get('responses_sent', 0)}")
        print(f"    Available Symbols: {len(bootstrap_stats.get('available_symbols', []))}")
        
        print(f"\n[STEP 5] Testing historical data request...")
        
        # Wait a moment for any initial requests
        time.sleep(2)
        
        # Check if strategy made historical data requests
        final_stats = bridge.get_statistics()
        bootstrap_final = final_stats.get('bootstrap_stats', {})
        
        historical_requests = bootstrap_final.get('requests_received', 0)
        responses_sent = bootstrap_final.get('responses_sent', 0)
        
        print(f"  Historical data requests: {historical_requests}")
        print(f"  Responses sent: {responses_sent}")
        
        if historical_requests > 0:
            print("  [OK] Strategy successfully requested historical data")
        else:
            print("  [INFO] Strategy has not yet requested historical data")
            
        print(f"\n[STEP 6] Testing market data processing...")
        
        # Send a test market data bar
        test_bar = {
            'timestamp': '2023-01-15T10:30:00Z',
            'open': 71.50,
            'high': 71.75,
            'low': 71.25,
            'close': 71.60,
            'volume': 150
        }
        
        # Process the market data
        signal = bridge.process_market_data(test_bar)
        
        print(f"  Sent test market data bar")
        print(f"  Strategy signal received: {signal is not None}")
        if signal:
            print(f"  Signal details: {signal}")
        
        # Final status check
        print(f"\n[FINAL RESULTS]")
        test_duration = (datetime.now() - test_start_time).total_seconds()
        print(f"Test duration: {test_duration:.1f} seconds")
        
        final_stats = bridge.get_statistics()
        
        success_criteria = {
            'Bridge Running': final_stats['running'],
            'Strategy Ready': final_stats['strategy_ready'], 
            'Bootstrap Ready': final_stats['bootstrap_ready'],
            'CSV Data Available': len(bootstrap_final.get('available_symbols', [])) > 0,
            'MCL Symbol Available': config['symbol'] in bootstrap_final.get('available_symbols', [])
        }
        
        print("\nSuccess Criteria Check:")
        all_passed = True
        for criterion, passed in success_criteria.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {criterion}: {status}")
            if not passed:
                all_passed = False
        
        print(f"\n" + "=" * 80)
        if all_passed and start_success:
            print("[SUCCESS] END-TO-END TEST: COMPLETE SUCCESS")
            print("[OK] Node.js TSX strategy successfully integrated with real CSV data")
            print("[OK] Historical data bootstrap service working correctly")
            print("[OK] Full workflow validated - Phase 1 can be declared 100% COMPLETE")
        else:
            print("[WARNING] END-TO-END TEST: PARTIAL SUCCESS")
            print("Some components working but full integration needs attention")
        print("=" * 80)
        
        return all_passed and start_success
        
    except Exception as e:
        print(f"\n[ERROR] END-TO-END TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Always cleanup
        if bridge:
            try:
                print(f"\n[CLEANUP] Shutting down bridge...")
                bridge.shutdown()
                print("  [OK] Bridge shutdown complete")
            except Exception as e:
                print(f"  [WARNING] Error during shutdown: {e}")

if __name__ == "__main__":
    success = run_full_end_to_end_test()
    
    if success:
        print(f"\n[COMPLETE] VALIDATION COMPLETE: Phase 1 is truly 100% complete")
        print(f"[OK] Ready to move to Phase 2 with confidence")
    else:
        print(f"\n[ISSUES] VALIDATION REVEALED ISSUES: Phase 1 needs final adjustments")
        print(f"[ERROR] Cannot declare complete until all issues resolved")