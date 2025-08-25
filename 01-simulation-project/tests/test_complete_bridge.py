#!/usr/bin/env python3
"""
Test Complete TSX Strategy Bridge
Tests the full integration: Python -> Node.js -> Strategy -> Redis -> Python
"""

import sys
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.tsx_strategy_bridge import TSXStrategyBridge


def test_complete_bridge():
    """Test the complete bridge with a simple strategy"""
    
    print("=== Testing Complete TSX Strategy Bridge ===\n")
    
    # Path to test strategy
    strategy_path = Path(__file__).parent.parent / "strategies" / "test_simple_strategy.js"
    
    if not strategy_path.exists():
        print(f"Error: Strategy not found at {strategy_path}")
        return False
    
    bridge = None
    
    try:
        # Create bridge
        print(f"Creating bridge for strategy: {strategy_path.name}")
        bridge = TSXStrategyBridge(
            str(strategy_path),
            config={
                'botId': 'test_bot_1',
                'symbol': 'NQ',
                'timeframe': '1m'
            }
        )
        
        # Wait for initialization
        print("Waiting for initialization...")
        time.sleep(3)
        
        # Test market data processing
        print("\n--- Testing Market Data Processing ---")
        
        signals_received = []
        
        for i in range(10):
            # Create test bar
            bar = {
                'open': 15000 + i * 10,
                'high': 15010 + i * 10,
                'low': 14990 + i * 10,
                'close': 15005 + i * 10,
                'volume': 1000 + i * 100,
                'timestamp': time.time()
            }
            
            print(f"\nBar {i+1}: Sending close={bar['close']}, volume={bar['volume']}")
            
            # Process bar
            signal = bridge.process_bar(bar)
            
            if signal:
                print(f"  ✓ Received signal: {signal}")
                signals_received.append(signal)
            else:
                print("  - No signal")
            
            # Every 3rd bar, update positions
            if i % 3 == 0:
                positions = [{
                    'symbol': 'NQ',
                    'side': 'LONG' if i % 6 == 0 else 'SHORT',
                    'quantity': 1,
                    'entry_price': bar['close'],
                    'current_price': bar['close'] + 10
                }] if i > 0 else []
                
                print(f"  Updating positions: {len(positions)} position(s)")
                bridge.update_positions(positions)
            
            time.sleep(0.5)
        
        # Results
        print("\n=== Test Results ===")
        print(f"Bars processed: 10")
        print(f"Signals received: {len(signals_received)}")
        
        if len(signals_received) > 0:
            print("\nSignal details:")
            for idx, signal in enumerate(signals_received, 1):
                print(f"  Signal {idx}: {signal}")
        
        # Test passed if we got at least one signal
        success = len(signals_received) > 0
        
        if success:
            print("\n✓✓✓ BRIDGE TEST PASSED ✓✓✓")
        else:
            print("\n❌ BRIDGE TEST FAILED - No signals received")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if bridge:
            print("\nShutting down bridge...")
            bridge.shutdown()
            time.sleep(1)


if __name__ == "__main__":
    success = test_complete_bridge()
    sys.exit(0 if success else 1)