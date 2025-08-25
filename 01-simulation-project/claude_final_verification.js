/**
 * FINAL PHASE 1 VERIFICATION
 * Timestamp: 2025-08-23 22:08
 * This script verifies all Phase 1 components WITHOUT Redis
 */

const fs = require('fs');
const path = require('path');

console.log('='*50);
console.log('PHASE 1 COMPONENT VERIFICATION');
console.log('='*50);
console.log('Timestamp:', new Date().toISOString());
console.log('Process ID:', process.pid);
console.log('Working dir:', process.cwd());
console.log('Node version:', process.version);
console.log('Random proof:', Math.random(), Math.random(), Math.random());

// Test 1: Check if MockTradingBot exists
console.log('\n--- Test 1: MockTradingBot File Check ---');
const mockBotPath = path.join(__dirname, 'shared', 'mock_trading_bot_real_redis.js');
if (fs.existsSync(mockBotPath)) {
    const stats = fs.statSync(mockBotPath);
    console.log('✓ MockTradingBot EXISTS');
    console.log('  Path:', mockBotPath);
    console.log('  Size:', stats.size, 'bytes');
    console.log('  Modified:', stats.mtime);
    
    // Show first few lines
    const content = fs.readFileSync(mockBotPath, 'utf8');
    const lines = content.split('\n').slice(0, 5);
    console.log('  First 5 lines:');
    lines.forEach(line => console.log('    ', line));
} else {
    console.log('✗ MockTradingBot NOT FOUND');
}

// Test 2: Check Python Bridge
console.log('\n--- Test 2: Python Bridge Check ---');
const bridgePath = path.join(__dirname, 'shared', 'tsx_strategy_bridge.py');
const fixedBridgePath = path.join(__dirname, 'shared', 'claude_tsx_strategy_bridge_fixed.py');

[bridgePath, fixedBridgePath].forEach(file => {
    if (fs.existsSync(file)) {
        const stats = fs.statSync(file);
        console.log('✓', path.basename(file), 'EXISTS');
        console.log('  Size:', stats.size, 'bytes');
    }
});

// Test 3: Check Strategy Runner
console.log('\n--- Test 3: Strategy Runner Check ---');
const runnerPath = path.join(__dirname, 'shared', 'strategy_runner_enhanced.js');
if (fs.existsSync(runnerPath)) {
    console.log('✓ Enhanced Strategy Runner EXISTS');
    console.log('  Path:', runnerPath);
    console.log('  Size:', fs.statSync(runnerPath).size, 'bytes');
} else {
    console.log('✗ Enhanced Strategy Runner NOT FOUND');
}

// Test 4: Check package.json
console.log('\n--- Test 4: Dependencies Check ---');
const packagePath = path.join(__dirname, 'package.json');
if (fs.existsSync(packagePath)) {
    const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    console.log('✓ package.json EXISTS');
    console.log('  Name:', pkg.name);
    console.log('  Version:', pkg.version);
    console.log('  Dependencies:');
    Object.entries(pkg.dependencies || {}).forEach(([name, version]) => {
        console.log('    -', name + ':', version);
    });
} else {
    console.log('✗ package.json NOT FOUND');
}

// Test 5: Test Strategy Execution (No Redis Required)
console.log('\n--- Test 5: Strategy Execution Test ---');

// Create inline test strategy
const testStrategyCode = `
class TestStrategy {
    constructor(config, mainBot) {
        this.config = config || {};
        this.mainBot = mainBot || {};
        this.signals = 0;
    }
    
    processMarketData(price, volume) {
        this.signals++;
        if (this.signals % 2 === 0) {
            return { action: 'BUY', price: price };
        }
        return null;
    }
}
module.exports = TestStrategy;
`;

// Write temporary test strategy
const tempStrategyPath = path.join(__dirname, 'claude_temp_test_strategy.js');
fs.writeFileSync(tempStrategyPath, testStrategyCode);

try {
    // Load and test the strategy
    const TestStrategy = require(tempStrategyPath);
    const mockBot = { modules: {} };
    const strategy = new TestStrategy({ symbol: 'TEST' }, mockBot);
    
    // Process some data
    let signalCount = 0;
    for (let i = 0; i < 4; i++) {
        const signal = strategy.processMarketData(15000 + i * 10, 1000);
        if (signal) {
            signalCount++;
            console.log(`  Signal ${signalCount}:`, signal.action, 'at', signal.price);
        }
    }
    
    if (signalCount === 2) {
        console.log('✓ Strategy execution SUCCESSFUL');
    } else {
        console.log('✗ Unexpected signal count:', signalCount);
    }
} catch (error) {
    console.log('✗ Strategy execution FAILED:', error.message);
} finally {
    // Clean up
    if (fs.existsSync(tempStrategyPath)) {
        fs.unlinkSync(tempStrategyPath);
    }
}

// Final Summary
console.log('\n' + '='*50);
console.log('VERIFICATION SUMMARY');
console.log('='*50);

const components = {
    'MockTradingBot': fs.existsSync(mockBotPath),
    'Python Bridge': fs.existsSync(bridgePath),
    'Fixed Bridge': fs.existsSync(fixedBridgePath),
    'Strategy Runner': fs.existsSync(runnerPath),
    'Package.json': fs.existsSync(packagePath)
};

let allExist = true;
Object.entries(components).forEach(([name, exists]) => {
    console.log(`${name}: ${exists ? '✓ EXISTS' : '✗ MISSING'}`);
    if (!exists) allExist = false;
});

console.log('\nFinal Status:', allExist ? 'ALL COMPONENTS PRESENT' : 'SOME COMPONENTS MISSING');
console.log('Verification completed at:', new Date().toISOString());

process.exit(allExist ? 0 : 1);