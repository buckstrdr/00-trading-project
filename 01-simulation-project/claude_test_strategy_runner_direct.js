/**
 * Direct test of TSX V5 Strategy Runner to debug readiness issue
 */

const path = require('path');
const TSXv5StrategyRunner = require('./shared/claude_tsx_v5_strategy_runner');

console.log("=== DIRECT TSX STRATEGY RUNNER TEST ===");
console.log("Testing testTimeStrategy.js readiness...");

async function testDirectRunner() {
    try {
        const strategyPath = '../03-trading-bot/TSX-Trading-Bot-V5/src/strategies/test/testTimeStrategy.js';
        const config = {
            botId: 'direct_test',
            symbol: 'MCL',
            historicalBarsBack: 10,
            redisHost: 'localhost',
            redisPort: 6379
        };
        
        console.log(`[TEST] Creating TSX V5 Strategy Runner...`);
        console.log(`  Strategy: ${path.basename(strategyPath)}`);
        console.log(`  Config:`, config);
        
        // Create runner (should initialize automatically)
        const runner = new TSXv5StrategyRunner(strategyPath, config);
        
        // Wait for initialization
        console.log(`[TEST] Waiting for runner to become ready...`);
        
        let readyCheckCount = 0;
        const maxChecks = 60; // 60 seconds
        
        while (!runner.ready && readyCheckCount < maxChecks) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            readyCheckCount++;
            
            if (readyCheckCount % 5 === 0) {
                console.log(`[TEST] Still waiting... ${readyCheckCount}/${maxChecks} seconds`);
            }
        }
        
        console.log(`[TEST] Runner ready status: ${runner.ready}`);
        
        if (runner.ready) {
            console.log(`✅ SUCCESS: TSX Strategy Runner became ready in ${readyCheckCount} seconds`);
            
            // Test market data processing
            console.log(`[TEST] Sending test market data...`);
            const testMarketData = {
                symbol: 'MCL',
                price: 75.50,
                close: 75.50,
                volume: 1000,
                timestamp: '2023-06-01T10:00:00.000Z'
            };
            
            await runner.handleMarketData(testMarketData);
            console.log(`[TEST] Market data sent successfully`);
            
        } else {
            console.log(`❌ FAILED: TSX Strategy Runner did not become ready within ${maxChecks} seconds`);
            console.log(`[DEBUG] Runner state:`, {
                ready: runner.ready,
                strategy: runner.strategy ? 'loaded' : 'not loaded',
                redisClient: runner.redisClient ? 'connected' : 'not connected',
                simulationDateTime: runner.simulationDateTime
            });
        }
        
        // Cleanup
        console.log(`[TEST] Shutting down runner...`);
        await runner.shutdown();
        
    } catch (error) {
        console.error(`[ERROR] Test failed:`, error);
        process.exit(1);
    }
}

// Run the test
testDirectRunner();