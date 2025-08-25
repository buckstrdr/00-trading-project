#!/usr/bin/env python3
"""
Debug the numpy datetime conversion error
"""

import sys
sys.path.append('src')
from tsx_backtest_framework import TSXBacktestFramework

print("=== NUMPY DATETIME DEBUG TEST ===")

try:
    strategy_path = '../03-trading-bot/TSX-Trading-Bot-V5/src/strategies/test/testTimeStrategy.js'
    csv_directory = '../98-month-by-month-data-files'
    
    framework = TSXBacktestFramework(strategy_path, csv_directory)
    
    print("Framework initialized successfully")
    
    # Run with detailed error tracking
    result = framework.run_single_backtest(
        symbol='MCL',
        start_date='2023-06-01',
        end_date='2023-06-01',
        config={'botId': 'debug_test'}
    )
    
    print(f"Backtest result: {result}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print("Full traceback:")
    traceback.print_exc()