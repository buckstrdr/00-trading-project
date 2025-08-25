/**
 * Unit tests for MockTradingBot
 * Tests all modules and Redis channel isolation
 */

const assert = require('assert');
const MockTradingBot = require('./shared/mock_trading_bot');

console.log('=== MockTradingBot Unit Tests ===');
console.log(`Test Start: ${new Date().toISOString()}`);
console.log(`Process ID: ${process.pid}`);
console.log(`Random Verification: ${Math.random()}`);

let testsPassed = 0;
let testsFailed = 0;

function test(name, fn) {
    try {
        fn();
        console.log(`✓ ${name}`);
        testsPassed++;
    } catch (error) {
        console.error(`✗ ${name}`);
        console.error(`  Error: ${error.message}`);
        testsFailed++;
    }
}

// Test 1: Basic Instantiation
test('MockTradingBot instantiation', () => {
    const bot = new MockTradingBot();
    assert(bot instanceof MockTradingBot);
    assert.strictEqual(bot.config.botId, 'mock_bot_1');
    assert.strictEqual(bot.config.symbol, 'NQ');
});

// Test 2: Custom Configuration
test('MockTradingBot with custom config', () => {
    const bot = new MockTradingBot({
        botId: 'test_bot',
        symbol: 'ES'
    });
    assert.strictEqual(bot.config.botId, 'test_bot');
    assert.strictEqual(bot.config.symbol, 'ES');
});

// Test 3: Position Management Module
test('Position Management - No positions initially', () => {
    const bot = new MockTradingBot();
    assert.strictEqual(bot.modules.positionManagement.hasPosition(), false);
    assert.deepStrictEqual(bot.modules.positionManagement.getAllPositions(), []);
});

test('Position Management - Add positions', () => {
    const bot = new MockTradingBot();
    bot.updatePositions([{
        symbol: 'NQ',
        side: 'LONG',
        quantity: 2,
        entryPrice: 15000,
        currentPrice: 15050
    }]);
    
    assert.strictEqual(bot.modules.positionManagement.hasPosition(), true);
    assert.strictEqual(bot.modules.positionManagement.getAllPositions().length, 1);
    assert.strictEqual(bot.modules.positionManagement.isLongPosition(), true);
    assert.strictEqual(bot.modules.positionManagement.isShortPosition(), false);
});

// Test 4: Health Monitoring Module
test('Health Monitoring - Initial state', () => {
    const bot = new MockTradingBot();
    assert.strictEqual(bot.modules.healthMonitoring.isQuietMode(), false);
    
    const status = bot.modules.healthMonitoring.getQuietModeStatus();
    assert.strictEqual(status.enabled, false);
    assert.strictEqual(status.reason, null);
});

test('Health Monitoring - Set quiet mode', () => {
    const bot = new MockTradingBot();
    bot.modules.healthMonitoring.setQuietMode(true, 'Testing');
    
    assert.strictEqual(bot.modules.healthMonitoring.isQuietMode(), true);
    
    const status = bot.modules.healthMonitoring.getQuietModeStatus();
    assert.strictEqual(status.enabled, true);
    assert.strictEqual(status.reason, 'Testing');
});

// Test 5: Keyboard Interface Module
test('Keyboard Interface - Initial state', () => {
    const bot = new MockTradingBot();
    const state = bot.modules.keyboardInterface.getPromptState();
    assert.strictEqual(state.active, false);
    assert.strictEqual(state.type, null);
});

// Test 6: Manual Trading Module
test('Manual Trading - Initial state', () => {
    const bot = new MockTradingBot();
    assert.strictEqual(bot.modules.manualTrading.awaitingConfirmation, false);
    assert.strictEqual(bot.modules.manualTrading.getConfirmationState(), false);
});

// Test 7: Redis Channel Validation
test('Redis - Valid bot: channels', () => {
    const bot = new MockTradingBot();
    const redis = bot.getRedisClient();
    
    // Should not throw
    redis.publish('bot:test', 'message');
    redis.subscribe('bot:data', () => {});
    redis.unsubscribe('bot:data');
});

test('Redis - Invalid channels throw errors', () => {
    const bot = new MockTradingBot();
    const redis = bot.getRedisClient();
    
    assert.throws(() => {
        redis.publish('aggregator:test', 'message');
    }, /Channel violation/);
    
    assert.throws(() => {
        redis.subscribe('connection-manager:test', () => {});
    }, /Channel violation/);
});

// Test 8: Shutdown
test('Shutdown clears resources', () => {
    const bot = new MockTradingBot();
    const redis = bot.getRedisClient();
    
    redis.subscribe('bot:test', () => {});
    bot.on('test-event', () => {});
    
    bot.shutdown();
    
    assert.strictEqual(bot.messageHandlers.size, 0);
    assert.strictEqual(bot.redisChannels.size, 0);
});

console.log('\n=== Test Summary ===');
console.log(`Tests Passed: ${testsPassed}`);
console.log(`Tests Failed: ${testsFailed}`);
console.log(`Total Tests: ${testsPassed + testsFailed}`);
console.log(`Test End: ${new Date().toISOString()}`);
console.log(`Exit Code: ${testsFailed > 0 ? 1 : 0}`);

process.exit(testsFailed > 0 ? 1 : 0);
