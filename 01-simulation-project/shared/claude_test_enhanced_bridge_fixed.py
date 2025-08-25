"""
Test Enhanced TSX Strategy Bridge with Proper Unicode Handling
"""

import time
import sys
from datetime import datetime
from claude_enhanced_tsx_strategy_bridge import EnhancedTSXStrategyBridge

def test_enhanced_bridge():
    """Test the fixed Enhanced TSX Strategy Bridge"""
    
    print("=" * 80)
    print("TESTING ENHANCED TSX STRATEGY BRIDGE - SUBPROCESS FIX")
    print("=" * 80)
    
    # Configuration
    test_config = {
        'botId': 'test_enhanced_fixed',
        'symbol': 'MCL',
        'historicalBarsBack': 20,
        'redisHost': 'localhost',
        'redisPort': 6379
    }
    
    strategy_path = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\03-trading-bot\TSX-Trading-Bot-V5\src\strategies\ema\emaStrategy.js"
    csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    
    try:
        print(f"\n[STEP 1] Creating Enhanced Bridge...")
        print(f"Strategy: emaStrategy.js")
        print(f"Symbol: {test_config['symbol']}")
        
        # Create enhanced bridge
        bridge = EnhancedTSXStrategyBridge(strategy_path, csv_data_dir, test_config)
        
        print(f"\n[STEP 2] Starting Enhanced Bridge (with subprocess fix)...")
        
        # Start the bridge - this should now work with Unicode fix
        ready = bridge.start()
        
        print(f"\n[STEP 3] Bridge startup results:")
        print(f"  Strategy ready: {ready}")
        
        # Get detailed statistics
        stats = bridge.get_statistics()
        print(f"  Bootstrap ready: {stats['bootstrap_ready']}")
        print(f"  Strategy signals: {stats['strategy_signals']}")
        print(f"  Historical requests: {stats['historical_requests']}")
        
        print(f"\n[STEP 4] Testing market data processing...")
        
        # Test market data
        test_bar = {
            'symbol': 'MCL',
            'close': 75.50,
            'open': 75.45,
            'high': 75.55,
            'low': 75.40,
            'volume': 1500,
            'timestamp': datetime(2023, 6, 15, 14, 30, 0)
        }
        
        signal = bridge.process_market_data(test_bar)
        print(f"  Signal generated: {signal is not None}")
        
        if signal:
            print(f"  Signal type: {signal.get('action', 'UNKNOWN')}")
        
        # Wait a moment for any delayed signals
        time.sleep(2)
        
        # Final statistics
        final_stats = bridge.get_statistics()
        print(f"\n[STEP 5] Final Results:")
        print(f"  Total market data bars processed: {final_stats['market_data_bars']}")
        print(f"  Total strategy signals: {final_stats['strategy_signals']}")
        print(f"  Strategy ready status: {final_stats['strategy_ready']}")
        
        print(f"\n" + "=" * 80)
        
        if ready and final_stats['strategy_ready']:
            print(f"[SUCCESS] ENHANCED BRIDGE SUBPROCESS COMMUNICATION FIXED")
            print(f"[OK] Unicode encoding issues resolved")
            print(f"[OK] Strategy startup detection working")
            return True
        else:
            print(f"[FAIL] Enhanced Bridge still has issues")
            print(f"  Ready on startup: {ready}")
            print(f"  Final ready status: {final_stats['strategy_ready']}")
            return False
        
    except Exception as e:
        print(f"[ERROR] Enhanced Bridge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if 'bridge' in locals():
            bridge.shutdown()

if __name__ == "__main__":
    # Set UTF-8 encoding for console output to handle any Unicode in results
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    
    success = test_enhanced_bridge()
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")