/**
 * Simple Node.js test to isolate the issue
 */

console.log('[NodeTest] Starting simple Node.js test...');

try {
    // Test 1: Basic Redis connection
    console.log('[NodeTest] Testing Redis connection...');
    
    const redis = require('redis');
    
    async function testRedis() {
        const client = redis.createClient({
            host: 'localhost',
            port: 6379
        });
        
        await client.connect();
        console.log('[NodeTest] Redis connected successfully');
        
        await client.quit();
        console.log('[NodeTest] Redis disconnected');
        
        // Test 2: Try to load the strategy
        console.log('[NodeTest] Testing strategy load...');
        
        const path = require('path');
        const strategyPath = 'C:\\Users\\salte\\ClaudeProjects\\github-repos\\00-trading-project\\03-trading-bot\\TSX-Trading-Bot-V5\\src\\strategies\\ema\\emaStrategy.js';
        
        console.log(`[NodeTest] Loading strategy: ${strategyPath}`);
        
        const StrategyClass = require(path.resolve(strategyPath));
        console.log('[NodeTest] Strategy class loaded successfully');
        
        // Test 3: Try to create strategy instance
        console.log('[NodeTest] Creating strategy instance...');
        
        const mockMainBot = {
            log: (msg) => console.log(`[MockBot] ${msg}`),
            logError: (msg) => console.error(`[MockBot] ${msg}`),
            getConfig: (key) => null,
            getCurrentPositions: () => [],
            getBalance: () => 100000
        };
        
        const strategy = new StrategyClass({}, mockMainBot);
        console.log('[NodeTest] Strategy instance created successfully');
        
        // Final success
        console.log('[NodeTest] ready: true');
        console.log('[NodeTest] All tests passed!');
        
        process.exit(0);
    }
    
    testRedis().catch(error => {
        console.error('[NodeTest] Error:', error);
        process.exit(1);
    });
    
} catch (error) {
    console.error('[NodeTest] Synchronous error:', error);
    process.exit(1);
}