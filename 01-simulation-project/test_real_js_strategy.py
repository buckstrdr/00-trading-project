#!/usr/bin/env python3
"""
Real JavaScript Strategy Integration Test
Tests actual PDHPDLStrategy-Comprehensive.js with Python backtesting system
Per CLAUDE.md anti-bullshit rules: REAL testing with your actual strategy file
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time

# Add project path
sys.path.append(str(Path(__file__).parent))

from shared.js_strategy_adapter import JSStrategyAdapter, JSStrategyConfig
from shared.strategy_interface import MarketData

def test_real_js_strategy():
    """Test with the actual PDHPDLStrategy-Comprehensive.js file"""
    print("=" * 80)
    print("REAL JAVASCRIPT STRATEGY INTEGRATION TEST")
    print("Testing PDHPDLStrategy-Comprehensive.js with Python backtesting system")
    print("=" * 80)
    
    # Path to the real JavaScript strategy
    real_js_strategy_path = Path("C:/Users/salte/ClaudeProjects/github-repos/TSX-Trading-Bot-V5/src/strategies/PDHPDLStrategy-Comprehensive.js")
    
    if not real_js_strategy_path.exists():
        print(f"FAIL: Real JavaScript strategy not found at {real_js_strategy_path}")
        return False
    
    print(f"PASS Found real JavaScript strategy: {real_js_strategy_path}")
    print(f"   File size: {real_js_strategy_path.stat().st_size:,} bytes")
    
    try:
        # Create configuration for MCL futures (same as strategy uses)
        config = JSStrategyConfig.for_futures_contract(
            'MCL', 
            dollar_risk_per_trade=100,
            risk_reward_ratio=2.0,
            max_risk_points=0.50
        )
        
        print(f"PASS Created strategy configuration for MCL futures")
        print(f"   Risk per trade: ${config.dollar_risk_per_trade}")
        print(f"   Dollar per point: ${config.dollar_per_point}")
        
        # Initialize the adapter with real strategy
        print(f"\nInitializing JSStrategyAdapter with real PDHPDLStrategy...")
        start_time = time.time()
        
        adapter = JSStrategyAdapter(str(real_js_strategy_path), config)
        
        init_time = time.time() - start_time
        print(f"PASS JSStrategyAdapter initialized in {init_time:.3f} seconds")
        print(f"   Strategy name: {adapter.name}")
        
        # Test if strategy is ready
        if not adapter.is_strategy_ready():
            print("FAIL Strategy not ready - attempting to start Node.js process...")
            return False
        
        print("PASS Strategy ready for market data processing")
        
        # Test with realistic MCL price data
        test_prices = [
            67.45, 67.47, 67.52, 67.48, 67.55, 67.60, 67.58, 67.62, 67.65, 67.63,
            67.68, 67.72, 67.70, 67.75, 67.78, 67.82, 67.85, 67.88, 67.92, 67.95
        ]
        
        print(f"\nProcessing {len(test_prices)} market data points...")
        
        successful_ticks = 0
        signals_generated = 0
        processing_times = []
        
        for i, price in enumerate(test_prices):
            market_data = MarketData(
                price=price,
                volume=1000 + (i * 100),  # Varying volume
                timestamp=datetime.now() + timedelta(seconds=i * 60)  # 1-minute intervals
            )
            
            tick_start = time.time()
            result = adapter.process_market_data(market_data)
            tick_time = time.time() - tick_start
            processing_times.append(tick_time)
            
            if result and isinstance(result, dict):
                successful_ticks += 1
                
                if result.get('signal'):
                    signals_generated += 1
                    signal = result['signal']
                    print(f"   SIGNAL #{signals_generated}: {signal.direction} at ${price:.2f}")
                    print(f"      Stop: ${signal.stop_loss:.2f}, Target: ${signal.take_profit:.2f}")
                    print(f"      Risk: ${signal.dollar_risk:.2f}, Reward: ${signal.dollar_reward:.2f}")
                    print(f"      Position size: {signal.position_size} contracts")
                
                # Show environment data
                env = result.get('environment', {})
                if env:
                    print(f"   Environment: Balance=${env.get('accountBalance', 0):.2f}, "
                          f"Position={env.get('hasPosition', False)}")
            else:
                print(f"FAIL Invalid result at price ${price:.2f}")
        
        # Calculate performance metrics
        avg_processing_time = sum(processing_times) / len(processing_times)
        total_processing_time = sum(processing_times)
        
        print(f"\nPERFORMANCE RESULTS:")
        print(f"   Successful ticks: {successful_ticks}/{len(test_prices)}")
        print(f"   Signals generated: {signals_generated}")
        print(f"   Average processing time: {avg_processing_time:.4f} seconds per tick")
        print(f"   Total processing time: {total_processing_time:.3f} seconds")
        print(f"   Processing rate: {len(test_prices)/total_processing_time:.1f} ticks/second")
        
        # Check if strategy behaved realistically
        success_rate = successful_ticks / len(test_prices)
        if success_rate < 0.8:
            print(f"FAIL Low success rate: {success_rate:.1%}")
            return False
        
        if avg_processing_time > 1.0:
            print(f"FAIL Processing too slow: {avg_processing_time:.3f}s per tick")
            return False
        
        print(f"\nINTEGRATION TEST PASSED!")
        print(f"   Real JavaScript strategy successfully integrated with Python backtesting system")
        print(f"   Success rate: {success_rate:.1%}")
        print(f"   Performance: {avg_processing_time:.4f}s per tick")
        
        # Cleanup
        adapter._cleanup()
        
        return True
        
    except Exception as e:
        print(f"INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print(f"Test start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_real_js_strategy()
    
    print(f"\nTest end time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\nREAL JAVASCRIPT STRATEGY INTEGRATION: SUCCESS!")
        print("The refactor claim is VALIDATED - JavaScript strategies work in Python backtesting system")
        sys.exit(0)
    else:
        print("\nREAL JAVASCRIPT STRATEGY INTEGRATION: FAILED!")
        print("The refactor claim is INVALID - integration does not work as claimed")
        sys.exit(1)

if __name__ == "__main__":
    main()