#!/usr/bin/env python3
"""
CLAUDE.md Compliant Backtester Verification Test
Full end-to-end test with real execution and logging
"""

import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append('src')

# Import backtester
from tsx_backtest_framework import TSXBacktestFramework

def main():
    """Run comprehensive backtester verification test"""
    
    print(f"=== BACKTESTER VERIFICATION TEST START ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Session PID: {os.getpid()}")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Test configuration
        strategy_path = '../03-trading-bot/TSX-Trading-Bot-V5/src/strategies/test/testTimeStrategy.js'
        csv_directory = '../98-month-by-month-data-files'
        
        logger.info("=== VERIFICATION 1: Files and Paths ===")
        strategy_file = Path(strategy_path)
        csv_dir = Path(csv_directory)
        
        print(f"Strategy file exists: {strategy_file.exists()}")
        print(f"Strategy path: {strategy_file.absolute()}")
        print(f"CSV directory exists: {csv_dir.exists()}")
        print(f"CSV directory path: {csv_dir.absolute()}")
        
        if not strategy_file.exists():
            raise FileNotFoundError(f"Strategy file not found: {strategy_path}")
        if not csv_dir.exists():
            raise FileNotFoundError(f"CSV directory not found: {csv_directory}")
        
        logger.info("✅ File verification passed")
        
        logger.info("=== VERIFICATION 2: Framework Initialization ===")
        framework = TSXBacktestFramework(strategy_path, csv_directory)
        print(f"Framework initialized: {framework is not None}")
        logger.info("✅ Framework initialization passed")
        
        logger.info("=== VERIFICATION 3: Backtest Execution ===")
        print("Running backtest with TEST_TIME_STRATEGY...")
        print("Expected: Multiple trades every 5 minutes with 1377 bars of data")
        
        start_time = time.time()
        
        result = framework.run_single_backtest(
            symbol='MCL',
            start_date='2023-06-01',
            end_date='2023-06-01',  # Single day with 1377 1-minute bars
            config={
                'botId': 'verification_test_bot',
                'enableDetailedLogging': True
            }
        )
        
        execution_time = time.time() - start_time
        
        logger.info("=== VERIFICATION 4: Results Analysis ===")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('execution_info'):
            exec_info = result['execution_info']
            trade_count = exec_info.get('trade_count', 0)
            total_return = exec_info.get('total_return', 0)
            win_rate = exec_info.get('win_rate', 0)
            max_drawdown = exec_info.get('max_drawdown', 0)
            
            print(f"Total Trades: {trade_count}")
            print(f"Total Return: {total_return:.4f}")
            print(f"Win Rate: {win_rate:.1%}")
            print(f"Max Drawdown: {max_drawdown:.4f}")
            
            # Expected results validation
            expected_min_trades = 50  # Should have many trades with 5-minute intervals
            
            if trade_count >= expected_min_trades:
                logger.info(f"✅ Trade generation PASSED: {trade_count} >= {expected_min_trades}")
            else:
                logger.warning(f"⚠️ Trade generation LOW: {trade_count} < {expected_min_trades}")
                
        else:
            logger.error("❌ No execution info available")
            print(f"Available keys: {list(result.keys())}")
            if 'error' in result:
                print(f"Error: {result['error']}")
        
        logger.info("=== VERIFICATION 5: Performance Stats ===")
        
        # Get framework performance stats if available
        if hasattr(framework, 'get_performance_stats'):
            stats = framework.get_performance_stats()
            print(f"Framework stats: {stats}")
            
        logger.info("=== VERIFICATION COMPLETE ===")
        
        # Final validation
        success = result.get('success', False)
        has_trades = result.get('execution_info', {}).get('trade_count', 0) > 0
        
        if success and has_trades:
            print("🎯 BACKTESTER VERIFICATION: PASSED")
            logger.info("✅ All verifications passed")
            return True
        else:
            print("❌ BACKTESTER VERIFICATION: FAILED")
            logger.error("❌ Some verifications failed")
            return False
            
    except Exception as e:
        print(f"❌ VERIFICATION ERROR: {e}")
        logger.error(f"Verification failed with error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    import os
    success = main()
    print(f"=== FINAL RESULT: {'SUCCESS' if success else 'FAILED'} ===")
    exit(0 if success else 1)