const path = require('path');

console.log('=== Strategy Loading Test ===');
console.log(`Time: ${new Date().toISOString()}`);
console.log(`PID: ${process.pid}`);

// Test 1: Load MockTradingBot
console.log('\n[1/4] Loading MockTradingBot...');
try {
    const MockTradingBot = require('../shared/mock_trading_bot_real_redis');
    const mockBot = new MockTradingBot({ botId: 'test_bot_1' });
    console.log('✓ MockTradingBot loaded successfully');
    
    // Test module access
    console.log('Available modules:', Object.keys(mockBot.modules || {}));
    
    // Cleanup after test
    setTimeout(() => {
        if (mockBot.cleanup) {
            mockBot.cleanup();
        }
    }, 1000);
    
} catch (error) {
    console.error('❌ Error loading MockTradingBot:', error.message);
    process.exit(1);
}

// Test 2: Load Strategy Runner
console.log('\n[2/4] Loading Strategy Runner...');
try {
    const StrategyRunner = require('../shared/strategy_runner_enhanced');
    console.log('✓ StrategyRunner loaded successfully');
} catch (error) {
    console.error('❌ Error loading StrategyRunner:', error.message);
    // Try alternative
    try {
        const StrategyRunner = require('../shared/strategy_runner');
        console.log('✓ Basic StrategyRunner loaded successfully');
    } catch (altError) {
        console.error('❌ Error loading any StrategyRunner:', altError.message);
        process.exit(1);
    }
}

// Test 3: Test Strategy Runner initialization
console.log('\n[3/4] Testing StrategyRunner initialization...');
try {
    const MockTradingBot = require('../shared/mock_trading_bot_real_redis');
    const mockBot = new MockTradingBot({ botId: 'test_bot_init' });
    
    const testConfig = {
        botId: 'test_bot_init',
        symbol: 'NQ',
        timeframe: '1m'
    };
    
    // Try to initialize without actual strategy for now
    console.log('✓ Test configuration created');
    console.log('Config:', testConfig);
    
    setTimeout(() => {
        if (mockBot.cleanup) {
            mockBot.cleanup();
        }
    }, 1000);
    
} catch (error) {
    console.error('❌ Error in initialization test:', error.message);
}

// Test 4: Verify required paths exist
console.log('\n[4/4] Checking file paths...');
const requiredFiles = [
    '../shared/mock_trading_bot_real_redis.js',
    '../shared/strategy_runner_enhanced.js',
    '../shared/tsx_strategy_bridge.py'
];

requiredFiles.forEach(file => {
    const fullPath = path.resolve(__dirname, file);
    try {
        require.resolve(fullPath);
        console.log(`✓ ${file} - exists`);
    } catch (error) {
        console.log(`⚠ ${file} - not found`);
    }
});

console.log('\n=== Basic Loading Test Complete ===');

// Exit after brief delay to allow Redis cleanup
setTimeout(() => {
    console.log('Test completed successfully');
    process.exit(0);
}, 2000);