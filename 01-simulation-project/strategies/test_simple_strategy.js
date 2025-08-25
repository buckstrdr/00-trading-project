/**
 * Simple Test Strategy for Bridge Testing
 * Mimics TSX Trading Bot V5 strategy structure
 */

class SimpleTestStrategy {
    constructor(config = {}, mainBot = null) {
        this.config = config;
        this.mainBot = mainBot;
        this.name = 'SimpleTestStrategy';
        
        // Track state
        this.lastPrice = null;
        this.signalCount = 0;
        
        console.error(`[${this.name}] Initialized with config:`, config);
    }
    
    /**
     * Process market data and generate signals
     * TSX V5 standard interface
     */
    processMarketData(price, volume, timestamp) {
        console.error(`[${this.name}] Processing: price=${price}, volume=${volume}`);
        
        // Check position using mainBot modules
        const hasPosition = this.mainBot?.modules?.positionManagement?.hasPosition() || false;
        console.error(`[${this.name}] Has position: ${hasPosition}`);
        
        // Simple logic: generate signal every 5th bar
        this.signalCount++;
        
        if (this.signalCount % 5 === 0) {
            const signal = {
                direction: hasPosition ? 'CLOSE' : (this.signalCount % 10 === 0 ? 'SHORT' : 'LONG'),
                confidence: 0.75,
                entry_price: price,
                stop_loss: price * (this.signalCount % 10 === 0 ? 1.01 : 0.99),
                take_profit: price * (this.signalCount % 10 === 0 ? 0.98 : 1.02),
                timestamp: timestamp || Date.now(),
                source: this.name
            };
            
            console.error(`[${this.name}] Generated signal:`, signal);
            return signal;
        }
        
        this.lastPrice = price;
        return null;
    }
    
    /**
     * Alternative method name (some strategies use this)
     */
    analyze(candle) {
        return this.processMarketData(
            candle.close,
            candle.volume,
            candle.timestamp
        );
    }
    
    /**
     * Cleanup on shutdown
     */
    cleanup() {
        console.error(`[${this.name}] Cleanup called`);
    }
}

module.exports = SimpleTestStrategy;