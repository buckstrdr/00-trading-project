/**
 * Minimal Node.js runner for TSX Bot V5 strategies
 * Provides just enough mainBot structure for strategies to work
 */

const fs = require('fs');
const path = require('path');

// Get strategy path from command line
const strategyPath = process.argv[2];
if (!strategyPath) {
    console.error('Error: Strategy path required');
    process.exit(1);
}

// Load strategy
let StrategyClass;
try {
    StrategyClass = require(path.resolve(strategyPath));
} catch (error) {
    console.error(`Error loading strategy: ${error.message}`);
    process.exit(1);
}

// Create minimal mainBot proxy with only what strategies actually need
const mainBot = {
    modules: {
        positionManagement: {
            hasPosition: () => currentPosition !== null,
            getCurrentPosition: () => currentPosition,
            getPositionSize: () => currentPosition ? currentPosition.size : 0,
            getEntryPrice: () => currentPosition ? currentPosition.entryPrice : null
        },
        dataManager: {
            getCurrentPrice: () => lastPrice,
            getMarketData: () => marketData
        }
    },
    config: {
        symbol: 'BTC/USD',
        timeframe: '1m'
    }
};

// Track position state (managed by Python but needed for strategy logic)
let currentPosition = null;
let lastPrice = null;
let marketData = [];

// Initialize strategy with config and mainBot
const strategy = new StrategyClass({}, mainBot);

// Handle incoming messages from Python
process.stdin.on('data', (data) => {
    try {
        const message = JSON.parse(data.toString().trim());
        
        switch(message.type) {
            case 'PRICE_UPDATE':
                // Update price data
                lastPrice = message.data.close;
                marketData = message.data.candles || [];
                
                // Call strategy's analyze method with price data
                const signal = strategy.analyze({
                    open: message.data.open,
                    high: message.data.high,
                    low: message.data.low,
                    close: message.data.close,
                    volume: message.data.volume,
                    timestamp: message.data.timestamp
                });
                
                // Send signal back to Python
                process.stdout.write(JSON.stringify({
                    type: 'SIGNAL',
                    signal: signal || 'HOLD',
                    timestamp: new Date().toISOString(),
                    price: lastPrice
                }) + '\n');
                break;
                
            case 'POSITION_UPDATE':
                // Update position state from Python
                currentPosition = message.data.position;
                process.stdout.write(JSON.stringify({
                    type: 'ACK',
                    message: 'Position updated'
                }) + '\n');
                break;
                
            case 'INIT':
                // Initialize strategy with config
                if (strategy.init) {
                    strategy.init(message.data.config || {});
                }
                process.stdout.write(JSON.stringify({
                    type: 'READY',
                    strategy: path.basename(strategyPath),
                    hasInit: !!strategy.init,
                    hasAnalyze: !!strategy.analyze
                }) + '\n');
                break;
        }
        
    } catch (error) {
        process.stderr.write(`Error: ${error.message}\n`);
        process.stdout.write(JSON.stringify({
            type: 'ERROR',
            error: error.message
        }) + '\n');
    }
});

// Signal that runner is ready
process.stdout.write(JSON.stringify({
    type: 'READY',
    strategy: path.basename(strategyPath),
    pid: process.pid
}) + '\n');

// Handle shutdown
process.on('SIGTERM', () => {
    if (strategy.cleanup) {
        strategy.cleanup();
    }
    process.exit(0);
});
