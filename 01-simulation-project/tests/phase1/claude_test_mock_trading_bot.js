/**
 * Unit tests for MockTradingBot
 * Tests all modules and Redis channel isolation
 */

const assert = require('assert');
const MockTradingBot = require('../../shared/mock_trading_bot');

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

// Test 2: Position Management Module
test('Position Management - No positions initially', () => {
    const bot = new MockTradingBot();
    assert.strictEqual(bot.modules.positionManagement.hasPosition(), false);
    assert.deepStrictEqual(bot.modules.positionManagement.getAllPositions(), []);
});

// Test 3: Health Monitoring Module
test('Health Monitoring - Initial state', () => {
    const bot = new MockTradingBot();
    assert.strictEqual(bot.modules.healthMonitoring.isQuietMode(), false);
});

// Test 4: Redis Channel Validation
test('Redis - Valid bot: channels', () => {
    const bot = new MockTradingBot();
    const redis = bot.getRedisClient();
    
    // Should not throw
    redis.publish('bot:test', 'message');
});

test('Redis - Invalid channels throw errors', () => {
    const bot = new MockTradingBot();
    const redis = bot.getRedisClient();
    
    assert.throws(() => {
        redis.publish('aggregator:test', 'message');
    }, /Channel violation/);
});

console.log('\n=== Test Summary ===');
console.log(`Tests Passed: ${testsPassed}`);
console.log(`Tests Failed: ${testsFailed}`);
console.log(`Total Tests: ${testsPassed + testsFailed}`);
console.log(`Test End: ${new Date().toISOString()}`);
console.log(`Exit Code: ${testsFailed > 0 ? 1 : 0}`);

process.exit(testsFailed > 0 ? 1 : 0);
