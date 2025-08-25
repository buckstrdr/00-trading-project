/**
 * Direct test of strategy runner
 */

const StrategyRunner = require('../shared/strategy_runner_enhanced');

async function test() {
    console.error('=== Direct Strategy Runner Test ===\n');
    
    const runner = new StrategyRunner('./strategies/test_simple_strategy.js', {
        botId: 'test_bot_1',
        symbol: 'NQ'
    });
    
    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Send 10 bars of market data
    for (let i = 1; i <= 10; i++) {
        console.error(`\nSending bar ${i}...`);
        
        await runner.handleMessage({
            type: 'MARKET_DATA',
            data: {
                open: 100 + i,
                high: 101 + i,
                low: 99 + i,
                close: 100 + i,
                volume: 1000 + i * 10,
                timestamp: Date.now()
            }
        });
        
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    console.error('\n=== Test complete, shutting down ===');
    await runner.shutdown();
}

test().catch(console.error);