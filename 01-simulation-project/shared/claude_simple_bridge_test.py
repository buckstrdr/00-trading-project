"""
Simple test of Enhanced Bridge without UTF-8 console redirection
"""

import time
from datetime import datetime
from claude_enhanced_tsx_strategy_bridge import EnhancedTSXStrategyBridge

def simple_bridge_test():
    """Simple test without complex logging"""
    
    print("=== ENHANCED BRIDGE SUBPROCESS FIX TEST ===")
    
    # Configuration
    config = {
        'botId': 'simple_test',
        'symbol': 'MCL',
        'historicalBarsBack': 15,
        'redisHost': 'localhost',
        'redisPort': 6379
    }
    
    strategy_path = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\03-trading-bot\TSX-Trading-Bot-V5\src\strategies\ema\emaStrategy.js"
    csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    
    try:
        print("Creating Enhanced Bridge...")
        bridge = EnhancedTSXStrategyBridge(strategy_path, csv_data_dir, config)
        
        # Set historical simulation date to ensure CSV data is available
        historical_date = datetime(2023, 6, 15, 14, 30, 0)
        bridge.set_simulation_datetime(historical_date)
        print(f"Set simulation date to: {historical_date}")
        
        print("Starting Enhanced Bridge...")
        ready = bridge.start()
        
        print(f"Startup result: {ready}")
        
        # Wait a moment
        time.sleep(3)
        
        # Check final stats
        stats = bridge.get_statistics()
        print(f"Final strategy ready: {stats['strategy_ready']}")
        print(f"Bootstrap ready: {stats['bootstrap_ready']}")
        
        # Try sending one market data bar with historical date
        test_bar = {
            'close': 75.50,
            'open': 75.45, 
            'high': 75.55,
            'low': 75.40,
            'volume': 1000,
            'timestamp': datetime(2023, 6, 15, 14, 30, 0)  # Use historical date within CSV range
        }
        
        signal = bridge.process_market_data(test_bar)
        print(f"Market data processed, signal: {signal is not None}")
        
        # Final check
        final_stats = bridge.get_statistics()
        print(f"Market bars processed: {final_stats['market_data_bars']}")
        print(f"Signals generated: {final_stats['strategy_signals']}")
        
        success = final_stats['strategy_ready']
        print(f"SUBPROCESS FIX SUCCESS: {success}")
        
        return success
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
        
    finally:
        if 'bridge' in locals():
            bridge.shutdown()

if __name__ == "__main__":
    simple_bridge_test()