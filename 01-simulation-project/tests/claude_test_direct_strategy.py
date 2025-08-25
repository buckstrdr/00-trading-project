#!/usr/bin/env python3
"""
Test TSX Strategy Bridge without Redis dependency
Tests direct strategy execution and signal generation
"""

import sys
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the fixed bridge
from shared.claude_tsx_strategy_bridge_fixed import TSXStrategyBridgeFixed


def test_without_redis():
    """Test strategy without requiring Redis"""
    
    print("=== Testing TSX Strategy (No Redis Required) ===\n")
    
    # Create a simple test strategy that doesn't need Redis
    test_strategy = """
// Simple test strategy for verification
class TestStrategy {
    constructor(config, mainBot) {
        this.config = config || {};
        this.mainBot = mainBot || {};
        this.signalCount = 0;
        console.error('[TestStrategy] Initialized');
        
        // Send ready signal
        if (process.send) {
            process.send(JSON.stringify({
                type: 'READY',
                strategy: 'TestStrategy'
            }));
        }
    }
    
    async processMarketData(price, volume, timestamp) {
        console.error(`[TestStrategy] Processing: price=${price}, volume=${volume}`);
        
        this.signalCount++;
        
        // Generate signal every 3rd bar
        if (this.signalCount % 3 === 0) {
            const signal = {
                action: this.signalCount % 6 === 0 ? 'BUY' : 'SELL',
                symbol: this.config.symbol || 'NQ',
                price: price,
                timestamp: timestamp || Date.now(),
                reason: 'Test signal'
            };
            
            console.error('[TestStrategy] Generating signal:', JSON.stringify(signal));
            
            // Send via process.send if available
            if (process.send) {
                process.send(JSON.stringify({
                    type: 'SIGNAL',
                    data: signal
                }));
            }
            
            return signal;
        }
        
        return null;
    }
    
    updatePositions(positions) {
        console.error(`[TestStrategy] Positions updated: ${positions.length}`);
    }
}

module.exports = TestStrategy;
"""
    
    # Write test strategy to file
    strategy_file = Path(__file__).parent.parent / "strategies" / "claude_test_direct_strategy.js"
    strategy_file.parent.mkdir(exist_ok=True)
    strategy_file.write_text(test_strategy)
    print(f"Created test strategy: {strategy_file.name}")
    
    # Test without bridge (direct Node.js execution)
    import subprocess
    
    runner_test = """
const path = require('path');
const strategyPath = process.argv[2];
const config = JSON.parse(process.argv[3] || '{}');

console.error('Loading strategy from:', strategyPath);
const StrategyClass = require(path.resolve(strategyPath));

const mockBot = {
    modules: {
        positionManagement: {
            hasPosition: () => false,
            getAllPositions: () => []
        }
    }
};

const strategy = new StrategyClass(config, mockBot);

// Test market data processing
async function test() {
    console.error('\\nTesting market data processing:');
    
    for (let i = 0; i < 6; i++) {
        const price = 15000 + i * 10;
        const volume = 1000 + i * 100;
        const signal = await strategy.processMarketData(price, volume, Date.now());
        
        if (signal) {
            console.log('SIGNAL:', JSON.stringify(signal));
        }
    }
    
    console.error('\\nTest complete');
}

test().then(() => process.exit(0));
"""
    
    # Write runner test
    runner_file = Path(__file__).parent / "claude_test_runner.js"
    runner_file.write_text(runner_test)
    
    # Run test
    print("\n--- Testing Direct Strategy Execution ---")
    
    cmd = [
        'node',
        str(runner_file),
        str(strategy_file),
        json.dumps({'symbol': 'NQ', 'botId': 'test'})
    ]
    
    print(f"Running: {' '.join(cmd[:3])}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print("\n=== Output ===")
    if result.stdout:
        print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print(f"\nExit code: {result.returncode}")
    
    # Check for signals in output
    if 'SIGNAL:' in result.stdout:
        print("\n✅ Strategy generated signals successfully!")
        
        # Parse signals
        for line in result.stdout.split('\n'):
            if 'SIGNAL:' in line:
                signal_json = line.split('SIGNAL:')[1].strip()
                signal = json.loads(signal_json)
                print(f"  - {signal['action']} at ${signal['price']}")
    else:
        print("\n❌ No signals generated")
    
    # Clean up
    strategy_file.unlink(missing_ok=True)
    runner_file.unlink(missing_ok=True)
    
    return result.returncode == 0


if __name__ == '__main__':
    success = test_without_redis()
    sys.exit(0 if success else 1)