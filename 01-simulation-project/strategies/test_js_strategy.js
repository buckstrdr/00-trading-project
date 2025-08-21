/**
 * Simple test strategy for JS integration
 * Uses basic moving average crossover
 */

class TestJSStrategy {
    constructor(config = {}, mainBot = null) {
        this.config = config;
        this.mainBot = mainBot;
        this.prices = [];
        this.shortMA = [];
        this.longMA = [];
        this.shortPeriod = config.shortPeriod || 10;
        this.longPeriod = config.longPeriod || 20;
    }
    
    analyze(priceData) {
        // Add price to history
        this.prices.push(priceData.close);
        
        // Keep only needed history
        if (this.prices.length > this.longPeriod) {
            this.prices.shift();
        }
        
        // Not enough data yet
        if (this.prices.length < this.longPeriod) {
            return 'HOLD';
        }
        
        // Calculate moving averages
        const shortMA = this.calculateMA(this.shortPeriod);
        const longMA = this.calculateMA(this.longPeriod);
        
        // Track MA history
        this.shortMA.push(shortMA);
        this.longMA.push(longMA);
        
        if (this.shortMA.length > 2) {
            this.shortMA.shift();
            this.longMA.shift();
        }
        
        // Check for crossover
        if (this.shortMA.length >= 2 && this.longMA.length >= 2) {
            const prevShort = this.shortMA[0];
            const currShort = this.shortMA[1];
            const prevLong = this.longMA[0];
            const currLong = this.longMA[1];
            
            // Golden cross - short MA crosses above long MA
            if (prevShort <= prevLong && currShort > currLong) {
                return 'BUY';
            }
            
            // Death cross - short MA crosses below long MA
            if (prevShort >= prevLong && currShort < currLong) {
                return 'SELL';
            }
        }
        
        return 'HOLD';
    }
    
    calculateMA(period) {
        const slice = this.prices.slice(-period);
        return slice.reduce((a, b) => a + b, 0) / slice.length;
    }
    
    init(config) {
        // Reset state
        this.prices = [];
        this.shortMA = [];
        this.longMA = [];
        if (config.shortPeriod) this.shortPeriod = config.shortPeriod;
        if (config.longPeriod) this.longPeriod = config.longPeriod;
    }
    
    cleanup() {
        // Clean up resources if needed
        this.prices = [];
        this.shortMA = [];
        this.longMA = [];
    }
}

module.exports = TestJSStrategy;
