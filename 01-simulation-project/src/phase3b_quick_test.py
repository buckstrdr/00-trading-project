"""
Phase 3B Quick Test - Verify fixes work
"""

import logging
import time
from datetime import datetime
from tsx_pybroker_strategy import create_tsx_pybroker_strategy

logging.basicConfig(level=logging.WARNING)  # Reduce log noise
logger = logging.getLogger(__name__)


def quick_test_phase3b():
    """Quick test of Phase 3B fixes"""
    
    print("PHASE 3B QUICK TEST - Verifying fixes")
    print("=" * 50)
    
    try:
        tsx_strategy = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\03-trading-bot\TSX-Trading-Bot-V5\src\strategies\ema\emaStrategy.js"
        csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
        
        config = {
            'symbol': 'MCL',
            'historicalBarsBack': 20,
            'botId': 'quick_test'
        }
        
        print("Creating PyBroker Strategy...")
        
        # Create strategy with very small date range
        strategy = create_tsx_pybroker_strategy(
            tsx_strategy,
            csv_data_dir,
            'MCL',
            '2023-06-01',
            '2023-06-02',  # Just 1 day
            config
        )
        
        print("Running small backtest...")
        
        # Run backtest
        result = strategy.backtest()
        
        print(f"Backtest completed!")
        print(f"Portfolio value: ${result.portfolio_value:.2f}")
        print(f"Trades: {len(result.trades)}")
        
        # Get TSX stats
        tsx_stats = strategy._tsx_wrapper.get_performance_stats()
        print(f"Market bars processed: {tsx_stats['market_bars_processed']}")
        print(f"TSX signals: {tsx_stats['total_signals']}")
        
        # Success if backtest ran without crashes
        success = result.portfolio_value > 0
        print(f"Quick test: {'SUCCESS' if success else 'FAILED'}")
        
        strategy._tsx_wrapper.cleanup()
        return success
        
    except Exception as e:
        print(f"Quick test failed: {e}")
        return False


if __name__ == "__main__":
    quick_test_phase3b()