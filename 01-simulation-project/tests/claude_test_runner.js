
const path = require('path');
const strategyPath = process.argv[2];
const config = JSON.parse(process.argv[3] || '{}');

console.error('Loading strategy from:', strategyPath);
const StrategyClass = require(path.resolve(strategyPath));

const mockBot = {
    modules: {
        positionManagement: {
            hasPosition: () => false,
            getAllPositions: () => []
        }
    }
};

const strategy = new StrategyClass(config, mockBot);

// Test market data processing
async function test() {
    console.error('\nTesting market data processing:');
    
    for (let i = 0; i < 6; i++) {
        const price = 15000 + i * 10;
        const volume = 1000 + i * 100;
        const signal = await strategy.processMarketData(price, volume, Date.now());
        
        if (signal) {
            console.log('SIGNAL:', JSON.stringify(signal));
        }
    }
    
    console.error('\nTest complete');
}

test().then(() => process.exit(0));
