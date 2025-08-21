#!/usr/bin/env python3
"""
Test the fixed SimpleMAStrategy to verify it generates valid signals
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from strategies.examples.simple_ma_strategy import SimpleMAStrategy, SimpleMAConfig
from shared.strategy_interface import MarketData
from datetime import datetime, timedelta
import statistics

# Create strategy with MCL configuration
config = SimpleMAConfig.for_futures_contract('MCL', fast_period=10, slow_period=20)
strategy = SimpleMAStrategy(config)

# Simulate some price data that should generate crossover signals
test_prices = [
    73.50, 73.45, 73.40, 73.35, 73.30,  # Downtrend  
    73.25, 73.20, 73.15, 73.10, 73.05,  # More down
    73.00, 72.95, 72.90, 72.85, 72.80,  # Fast MA goes below slow MA
    72.75, 72.70, 72.65, 72.60, 72.55,  # Continue down 
    72.50, 72.45, 72.40, 72.35, 72.30,  # Build history
    
    # Now start uptrend for crossover
    72.35, 72.40, 72.50, 72.60, 72.70,  # Fast MA starts rising
    72.80, 72.90, 73.00, 73.10, 73.20,  # Should cross above slow MA
    73.30, 73.40, 73.50, 73.60, 73.70   # Continue up
]

print(f"Testing {len(test_prices)} price points...")
signals_generated = 0

for i, price in enumerate(test_prices):
    # Create timestamps 1 minute apart to create separate candles
    timestamp = datetime(2024, 1, 1, 9, 0) + timedelta(minutes=i)
    market_data = MarketData(
        price=price, 
        volume=1000,
        timestamp=timestamp
    )
    
    result = strategy.process_market_data(market_data)
    
    if result.get('signal'):
        signal = result['signal']
        signals_generated += 1
        print(f"\n=== SIGNAL {signals_generated} ===")
        print(f"Price: {price}")
        print(f"Direction: {signal.direction}")
        print(f"Entry: ${signal.entry_price:.2f}")
        print(f"Stop: ${signal.stop_loss:.2f}" if signal.stop_loss else "Stop: None")
        print(f"Target: ${signal.take_profit:.2f}" if signal.take_profit else "Target: None")
        print(f"Risk Points: {signal.risk_points:.3f}")
        print(f"Position Size: {signal.position_size}")
        print(f"Dollar Risk: ${signal.dollar_risk:.2f}")
        print(f"Reason: {signal.reason}")
    
    elif i > 25:  # Only show debug after we have enough candles
        debug = result.get('debug', {})
        fast_ma = debug.get('fast_ma')
        slow_ma = debug.get('slow_ma')
        if fast_ma and slow_ma:
            print(f"Price: {price:.2f}, Fast MA: {fast_ma:.3f}, Slow MA: {slow_ma:.3f}")

print(f"\n=== SUMMARY ===")
print(f"Total signals generated: {signals_generated}")
print(f"Strategy ready: {strategy.is_strategy_ready()}")
print(f"Candles processed: {len(strategy.candles)}")