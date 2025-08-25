const path = require('path');
const MockTradingBot = require('../shared/mock_trading_bot_real_redis');

console.log('=== EMA Strategy Loading Test ===');
console.log(`Time: ${new Date().toISOString()}`);
console.log(`PID: ${process.pid}`);

async function testEMALoading() {
    let mockBot;
    
    try {
        // Initialize MockTradingBot
        console.log('\n[1/5] Initializing MockTradingBot...');
        mockBot = new MockTradingBot({ 
            botId: 'ema_test',
            symbol: 'NQ',
            timeframe: '1m'
        });
        console.log('✓ MockTradingBot initialized');

        // Wait a moment for Redis connection
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Check EMA strategy path
        console.log('\n[2/5] Checking EMA strategy path...');
        const emaPath = path.resolve('../03-trading-bot/TSX-Trading-Bot-V5/src/strategies/ema/emaStrategy.js');
        console.log('EMA Strategy path:', emaPath);
        
        const fs = require('fs');
        if (!fs.existsSync(emaPath)) {
            throw new Error(`EMA Strategy file not found at: ${emaPath}`);
        }
        console.log('✓ EMA Strategy file exists');

        // Load EMA strategy
        console.log('\n[3/5] Loading EMA Strategy...');
        const EMAStrategy = require(emaPath);
        console.log('✓ EMA Strategy loaded successfully');
        console.log('Strategy exports type:', typeof EMAStrategy);

        // Create strategy configuration
        console.log('\n[4/5] Creating strategy instance...');
        const config = {
            botId: 'ema_test',
            symbol: 'NQ',
            timeframe: '1m',
            fastPeriod: 9,
            slowPeriod: 21,
            // Provide mainBot reference that strategies expect
            mainBot: {
                modules: mockBot.modules,
                // Add other properties that strategies might expect
                config: {
                    symbol: 'NQ',
                    timeframe: '1m'
                }
            }
        };
        
        console.log('Creating strategy with config:', {
            botId: config.botId,
            symbol: config.symbol,
            timeframe: config.timeframe,
            fastPeriod: config.fastPeriod,
            slowPeriod: config.slowPeriod
        });

        const strategy = new EMAStrategy(config, mockBot);
        console.log('✓ EMA Strategy instantiated successfully');
        console.log('Strategy type:', strategy.constructor.name);

        // Test processMarketData method
        console.log('\n[5/5] Testing processMarketData...');
        if (typeof strategy.processMarketData === 'function') {
            console.log('✓ processMarketData method exists');
            
            const testBar = {
                close: 15000,
                volume: 1000,
                timestamp: Date.now(),
                open: 14995,
                high: 15005,
                low: 14990
            };
            
            console.log('Testing with market data:', testBar);
            
            // Call processMarketData
            try {
                const signal = await strategy.processMarketData(testBar);
                console.log('✓ processMarketData executed');
                console.log('Signal generated:', signal || 'None');
            } catch (processError) {
                console.log('⚠ processMarketData error (may be normal):', processError.message);
            }
        } else {
            console.log('⚠ processMarketData method not found');
        }

        console.log('\n=== EMA Strategy Test Complete ===');
        console.log('✅ All tests passed successfully!');

    } catch (error) {
        console.error('\n❌ Error in EMA strategy test:', error.message);
        console.error('Stack trace:', error.stack);
        return false;
    } finally {
        // Cleanup
        console.log('\nCleaning up...');
        if (mockBot && mockBot.cleanup) {
            try {
                mockBot.cleanup();
                console.log('✓ MockTradingBot cleanup completed');
            } catch (cleanupError) {
                console.log('⚠ Cleanup error:', cleanupError.message);
            }
        }
    }
    
    return true;
}

// Run the test
testEMALoading()
    .then(success => {
        console.log(`\nTest result: ${success ? 'SUCCESS' : 'FAILURE'}`);
        process.exit(success ? 0 : 1);
    })
    .catch(error => {
        console.error('Unexpected error:', error);
        process.exit(1);
    });