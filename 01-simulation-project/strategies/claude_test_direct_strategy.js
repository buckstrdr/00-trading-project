
// Simple test strategy for verification
class TestStrategy {
    constructor(config, mainBot) {
        this.config = config || {};
        this.mainBot = mainBot || {};
        this.signalCount = 0;
        console.error('[TestStrategy] Initialized');
        
        // Send ready signal
        if (process.send) {
            process.send(JSON.stringify({
                type: 'READY',
                strategy: 'TestStrategy'
            }));
        }
    }
    
    async processMarketData(price, volume, timestamp) {
        console.error(`[TestStrategy] Processing: price=${price}, volume=${volume}`);
        
        this.signalCount++;
        
        // Generate signal every 3rd bar
        if (this.signalCount % 3 === 0) {
            const signal = {
                action: this.signalCount % 6 === 0 ? 'BUY' : 'SELL',
                symbol: this.config.symbol || 'NQ',
                price: price,
                timestamp: timestamp || Date.now(),
                reason: 'Test signal'
            };
            
            console.error('[TestStrategy] Generating signal:', JSON.stringify(signal));
            
            // Send via process.send if available
            if (process.send) {
                process.send(JSON.stringify({
                    type: 'SIGNAL',
                    data: signal
                }));
            }
            
            return signal;
        }
        
        return null;
    }
    
    updatePositions(positions) {
        console.error(`[TestStrategy] Positions updated: ${positions.length}`);
    }
}

module.exports = TestStrategy;
