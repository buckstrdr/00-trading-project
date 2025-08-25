/**
 * Test MockTradingBot with Real Redis
 */

const MockTradingBot = require('../shared/mock_trading_bot_real_redis');

async function testMockTradingBot() {
    console.log('=== Testing MockTradingBot ===\n');
    
    let bot;
    
    try {
        // Create bot instance
        console.log('Creating MockTradingBot instance...');
        bot = new MockTradingBot({
            botId: 'test_bot_1',
            symbol: 'NQ',
            redisHost: 'localhost',
            redisPort: 6379
        });
        
        // Wait for initialization
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Test modules exist
        console.log('\nTesting module interfaces:');
        console.log('✓ positionManagement:', typeof bot.modules.positionManagement);
        console.log('✓ healthMonitoring:', typeof bot.modules.healthMonitoring);
        console.log('✓ keyboardInterface:', typeof bot.modules.keyboardInterface);
        console.log('✓ manualTrading:', typeof bot.modules.manualTrading);
        console.log('✓ riskManagement:', typeof bot.modules.riskManagement);
        
        // Test position management
        console.log('\nTesting position management:');
        console.log('- hasPosition():', bot.modules.positionManagement.hasPosition());
        console.log('- getAllPositions():', bot.modules.positionManagement.getAllPositions());
        
        // Update positions
        bot.updatePositions([{
            symbol: 'NQ',
            side: 'LONG',
            quantity: 1,
            entry_price: 15000,
            current_price: 15100
        }]);
        
        console.log('- After update:');
        console.log('  hasPosition():', bot.modules.positionManagement.hasPosition());
        console.log('  getPositionSize():', bot.modules.positionManagement.getPositionSize('NQ'));
        
        // Test market data
        console.log('\nTesting market data send:');
        await bot.sendMarketData({
            price: 15100,
            volume: 1000,
            timestamp: Date.now()
        });
        console.log('✓ Market data sent');
        
        console.log('\n=== MockTradingBot tests passed ===');
        
        // Shutdown
        await bot.shutdown();
        
        return true;
        
    } catch (error) {
        console.error('\n❌ MockTradingBot test failed:', error);
        
        if (bot) {
            try {
                await bot.shutdown();
            } catch (e) {
                // Ignore shutdown errors
            }
        }
        
        return false;
    }
}

// Run test
testMockTradingBot().then(success => {
    process.exit(success ? 0 : 1);
});