#!/usr/bin/env python3

import sys
sys.path.append('src')
from tsx_backtest_framework import TSXBacktestFramework

print("=== FINAL BACKTESTER TEST ===")
print("Testing all fixes applied:")
print("1. Fixed same-day data loading (1377 bars)")
print("2. Fixed signal extraction from TSX strategy")
print("3. Fixed numpy datetime conversion")
print("4. Fixed simulation datetime context")
print()

strategy_path = '../03-trading-bot/TSX-Trading-Bot-V5/src/strategies/test/testTimeStrategy.js'
csv_directory = '../98-month-by-month-data-files'

framework = TSXBacktestFramework(strategy_path, csv_directory)
result = framework.run_single_backtest(
    symbol='MCL',
    start_date='2023-06-01',
    end_date='2023-06-01',
    config={'botId': 'final_test'}
)

print("=== RESULTS ===")
print(f"Success: {result.get('success', False)}")
if result.get('execution_info'):
    exec_info = result['execution_info']
    print(f"Total Trades: {exec_info.get('trade_count', 0)}")
    print(f"Total Return: {exec_info.get('total_return', 0):.4f}")
else:
    print("No execution info - backtest may have failed")
    if 'error' in result:
        print(f"Error: {result['error']}")

print("\n=== VERIFICATION ===")
trade_count = result.get('execution_info', {}).get('trade_count', 0)
if trade_count > 0:
    print(f"✅ SUCCESS: Generated {trade_count} trades")
    print("✅ TEST_TIME_STRATEGY is working with PyBroker!")
else:
    print("❌ FAILED: No trades generated")