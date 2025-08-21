const fs = require('fs').promises;
const path = require('path');

/**
 * The Crazy Horse Strategy
 * 
 * A 15-minute opening range breakout strategy that trades the NY session opening.
 * Enters positions when price breaks out of the first 15-minute range after 9:30 AM EST.
 * Uses the "shelf method" for trailing profits and optional position scaling.
 * 
 * @version 1.0
 */
class CrazyHorseStrategy {
    constructor(config = {}, mainBot = null) {
        this.name = 'CRAZY_HORSE';
        this.version = '1.0';
        this.mainBot = mainBot;
        
        // Strategy parameters with defaults
        this.params = {
            // Risk management (required)
            dollarRiskPerTrade: config.dollarRiskPerTrade || 100,
            dollarPerPoint: config.dollarPerPoint || 10,
            maxRiskPoints: config.maxRiskPoints || 3.0,
            riskRewardRatio: config.riskRewardRatio || 2,
            
            // Opening Range specific parameters
            sessionStartHour: config.sessionStartHour || 9,  // 9:30 AM EST
            sessionStartMinute: config.sessionStartMinute || 30,
            rangeMinutes: config.rangeMinutes || 15,  // 15-minute range
            
            // Position management
            enableAddToPosition: config.enableAddToPosition !== false,  // Optional adding at centerline
            enableDeleveraging: config.enableDeleveraging !== false,  // Optional deleveraging
            moveToBreakEven: config.moveToBreakEven !== false,  // Move stop to BE after first shelf
            
            // Shelf method parameters
            shelfMinPoints: config.shelfMinPoints || 1.0,  // Minimum shelf size
            shelfConsolidationBars: config.shelfConsolidationBars || 3,  // Bars to confirm shelf
            
            // Risk limits
            maxDollarLoss: config.maxDollarLoss || 100,  // Maximum dollar loss per trade
            accountSize: config.accountSize || 1000,  // Account size for risk calculation
            
            // Candle parameters
            candlePeriodMinutes: config.candlePeriodMinutes || 5,  // 5-minute candles for breakout
            maxCandleHistory: config.maxCandleHistory || 200,
            
            // Debug settings
            enableDebugLogging: config.enableDebugLogging || false,
            verboseLogging: config.verboseLogging || false
        };
        
        // State tracking
        this.state = {
            // Range tracking
            rangeHigh: null,
            rangeLow: null,
            rangeMidpoint: null,
            rangeFormed: false,
            rangeFormationTime: null,
            
            // Position tracking
            currentPosition: null,  // 'LONG', 'SHORT', or null
            positionOpenTime: null,
            entryPrice: null,
            stopLoss: null,
            takeProfit: null,
            positionSize: 1,
            
            // Position additions
            hasAddedPosition: false,
            addedPositionPrice: null,
            hasDeleveraged: false,
            
            // Shelf tracking
            currentShelf: null,
            shelfCount: 0,
            stopMovedToBreakEven: false,
            lastHighWaterMark: null,
            lastLowWaterMark: null,
            
            // General state
            isReady: false,
            lastSignalTime: null,
            bootstrapped: false
        };
        
        // Market data tracking
        this.candles = [];
        this.currentCandle = null;
        this.lastCandleTime = null;
        this.fiveMinCandles = [];  // Track 5-minute candles for breakout detection
        
        // Position state file path
        this.stateFilePath = path.join(__dirname, '..', '..', '..', 
            'data', 'strategy-state', `${this.name}_state.json`);
        
        // Initialize with historical data
        this.initializeWithHistoricalData();
        
        console.log(`🐎 ${this.name} v${this.version} initialized`);
        console.log(`💰 Risk per trade: $${this.params.dollarRiskPerTrade}`);
        console.log(`📊 Session start: ${this.params.sessionStartHour}:${this.params.sessionStartMinute.toString().padStart(2, '0')} EST`);
        console.log(`📏 Range period: ${this.params.rangeMinutes} minutes`);
    }
    
    /**
     * Process incoming market data
     */
    processMarketData(price, volume = 1000, timestamp = null) {
        if (!timestamp) timestamp = new Date();
        
        try {
            // Validate inputs
            if (price === null || price === undefined || isNaN(price)) {
                return {
                    ready: false,
                    signal: null,
                    debug: { reason: 'Invalid price data' }
                };
            }
            
            // Update candle data
            const candleChanged = this.updateCandle(price, volume, timestamp);
            
            // Update 5-minute candles for breakout detection
            if (candleChanged) {
                this.update5MinCandles(price, volume, timestamp);
            }
            
            // Check and form the opening range
            this.checkAndFormRange(timestamp);
            
            // Check if ready
            if (!this.isStrategyReady()) {
                return {
                    ready: false,
                    signal: null,
                    debug: { reason: this.getNotReadyReason() }
                };
            }
            
            // Generate trading signals
            const signal = this.generateSignal(price, timestamp);
            
            // Update shelf tracking if in position
            if (this.state.currentPosition) {
                this.updateShelfTracking(price);
            }
            
            return {
                ready: true,
                signal: signal,
                environment: this.analyzeMarketEnvironment(price),
                debug: this.getDebugInfo()
            };
            
        } catch (error) {
            console.log(`❌ Error in processMarketData: ${error.message}`);
            return {
                ready: false,
                signal: null,
                debug: { 
                    reason: 'Processing error',
                    error: error.message 
                }
            };
        }
    }    
    /**
     * Check and form the 15-minute opening range
     */
    checkAndFormRange(timestamp) {
        const currentTime = new Date(timestamp);
        const hour = currentTime.getHours();
        const minute = currentTime.getMinutes();
        
        // Check if we're at the session start time
        if (hour === this.params.sessionStartHour && minute === this.params.sessionStartMinute) {
            if (!this.state.rangeFormed || this.isDifferentTradingDay(this.state.rangeFormationTime, currentTime)) {
                // Start tracking new range
                this.state.rangeHigh = null;
                this.state.rangeLow = null;
                this.state.rangeFormed = false;
                this.state.rangeFormationTime = new Date(currentTime);
                
                console.log(`🕐 Starting new ${this.params.rangeMinutes}-minute range formation at ${hour}:${minute.toString().padStart(2, '0')}`);
            }
        }
        
        // Check if we're within the range formation period
        if (this.state.rangeFormationTime && !this.state.rangeFormed) {
            const elapsedMinutes = (currentTime - this.state.rangeFormationTime) / 60000;
            
            // Update range high and low
            const recentCandles = this.fiveMinCandles.slice(-Math.ceil(this.params.rangeMinutes / 5));
            if (recentCandles.length > 0) {                for (const candle of recentCandles) {
                    if (this.state.rangeHigh === null || candle.high > this.state.rangeHigh) {
                        this.state.rangeHigh = candle.high;
                    }
                    if (this.state.rangeLow === null || candle.low < this.state.rangeLow) {
                        this.state.rangeLow = candle.low;
                    }
                }
            }
            
            // Check if range formation period is complete
            if (elapsedMinutes >= this.params.rangeMinutes) {
                if (this.state.rangeHigh !== null && this.state.rangeLow !== null) {
                    this.state.rangeFormed = true;
                    this.state.rangeMidpoint = (this.state.rangeHigh + this.state.rangeLow) / 2;
                    
                    const rangeSize = this.state.rangeHigh - this.state.rangeLow;
                    console.log(`✅ ${this.params.rangeMinutes}-minute range formed:`);
                    console.log(`   High: ${this.state.rangeHigh.toFixed(2)}`);
                    console.log(`   Low: ${this.state.rangeLow.toFixed(2)}`);
                    console.log(`   Midpoint: ${this.state.rangeMidpoint.toFixed(2)}`);
                    console.log(`   Range size: ${rangeSize.toFixed(2)} points`);
                }
            }
        }
    }    
    /**
     * Generate trading signals based on range breakout
     */
    generateSignal(price, timestamp) {
        // Check for existing positions
        if (this.mainBot && this.mainBot.modules && this.mainBot.modules.positionManagement) {
            const positions = this.mainBot.modules.positionManagement.getAllPositions();
            if (positions && positions.length > 0 && !this.state.currentPosition) {
                return null;
            }
        }
        
        // If no range formed yet, no signal
        if (!this.state.rangeFormed) {
            return null;
        }
        
        // Check if we're already in a position
        if (this.state.currentPosition) {
            // Check for position addition opportunity (optional)
            if (this.params.enableAddToPosition && !this.state.hasAddedPosition) {
                return this.checkForPositionAddition(price);
            }
            
            // Check for deleveraging opportunity (optional)
            if (this.params.enableDeleveraging && this.state.hasAddedPosition && !this.state.hasDeleveraged) {
                return this.checkForDeleveraging(price);
            }
            
            // Check for exit conditions
            return this.checkForExit(price, timestamp);
        }        
        // Check for breakout from range (using 5-minute candle close)
        const lastCompleteCandle = this.getLastComplete5MinCandle();
        if (!lastCompleteCandle) {
            return null;
        }
        
        // Long signal - 5-minute candle closed above range high
        if (lastCompleteCandle.close > this.state.rangeHigh) {
            const signal = this.createLongSignal(price);
            if (signal) {
                this.state.currentPosition = 'LONG';
                this.state.positionOpenTime = timestamp;
                this.state.entryPrice = price;
                this.state.lastSignalTime = timestamp;
                this.savePositionState();
            }
            return signal;
        }
        
        // Short signal - 5-minute candle closed below range low
        if (lastCompleteCandle.close < this.state.rangeLow) {
            const signal = this.createShortSignal(price);
            if (signal) {
                this.state.currentPosition = 'SHORT';
                this.state.positionOpenTime = timestamp;
                this.state.entryPrice = price;
                this.state.lastSignalTime = timestamp;
                this.savePositionState();
            }
            return signal;
        }
        
        return null;
    }    
    /**
     * Create a LONG signal
     */
    createLongSignal(price) {
        // Calculate stop loss and take profit
        const stopLoss = this.state.rangeLow;  // Stop at range low
        const riskPoints = Math.abs(price - stopLoss);
        
        // Check if risk is within limits
        if (riskPoints > this.params.maxRiskPoints) {
            console.log(`🚫 Risk too high: ${riskPoints.toFixed(2)} pts > ${this.params.maxRiskPoints} pts max`);
            return null;
        }
        
        const takeProfit = price + (riskPoints * this.params.riskRewardRatio);
        
        // Calculate position sizing
        const positionSizing = this.calculatePositionSize(riskPoints, 'LONG');
        
        const signal = {
            // Core signal properties
            direction: 'LONG',
            confidence: 'HIGH',
            entryPrice: price,
            stopLoss: stopLoss,
            takeProfit: takeProfit,
            instrument: 'MGC',
            
            // Risk metrics
            riskPoints: riskPoints,
            rewardPoints: takeProfit - price,            riskRewardRatio: this.params.riskRewardRatio,
            
            // Position sizing
            positionSize: positionSizing.positionSize,
            dollarRisk: positionSizing.actualDollarRisk,
            dollarReward: positionSizing.actualDollarReward,
            
            // Metadata
            timestamp: Date.now(),
            reason: 'Range breakout - 5min candle closed above range high',
            strategyName: this.name,
            strategyVersion: this.version,
            signalStrength: 1.0,
            
            // Strategy-specific data
            indicators: {
                rangeHigh: this.state.rangeHigh,
                rangeLow: this.state.rangeLow,
                rangeMidpoint: this.state.rangeMidpoint,
                breakoutLevel: this.state.rangeHigh
            }
        };
        
        console.log(`🐎 ${this.name} LONG signal generated`);
        console.log(`   Entry: ${price.toFixed(2)}`);
        console.log(`   Stop: ${stopLoss.toFixed(2)}`);
        console.log(`   Target: ${takeProfit.toFixed(2)}`);
        console.log(`   Risk: ${riskPoints.toFixed(2)} pts`);
        console.log(`   Position: ${positionSizing.positionSize} contracts`);
        
        // Store position details        this.state.stopLoss = stopLoss;
        this.state.takeProfit = takeProfit;
        this.state.positionSize = positionSizing.positionSize;
        
        return signal;
    }
    
    /**
     * Create a SHORT signal
     */
    createShortSignal(price) {
        // Calculate stop loss and take profit
        const stopLoss = this.state.rangeHigh;  // Stop at range high
        const riskPoints = Math.abs(stopLoss - price);
        
        // Check if risk is within limits
        if (riskPoints > this.params.maxRiskPoints) {
            console.log(`🚫 Risk too high: ${riskPoints.toFixed(2)} pts > ${this.params.maxRiskPoints} pts max`);
            return null;
        }
        
        const takeProfit = price - (riskPoints * this.params.riskRewardRatio);
        
        // Calculate position sizing
        const positionSizing = this.calculatePositionSize(riskPoints, 'SHORT');
        
        const signal = {
            // Core signal properties
            direction: 'SHORT',
            confidence: 'HIGH',
            entryPrice: price,            stopLoss: stopLoss,
            takeProfit: takeProfit,
            instrument: 'MGC',
            
            // Risk metrics
            riskPoints: riskPoints,
            rewardPoints: price - takeProfit,
            riskRewardRatio: this.params.riskRewardRatio,
            
            // Position sizing
            positionSize: positionSizing.positionSize,
            dollarRisk: positionSizing.actualDollarRisk,
            dollarReward: positionSizing.actualDollarReward,
            
            // Metadata
            timestamp: Date.now(),
            reason: 'Range breakout - 5min candle closed below range low',
            strategyName: this.name,
            strategyVersion: this.version,
            signalStrength: 1.0,
            
            // Strategy-specific data
            indicators: {
                rangeHigh: this.state.rangeHigh,
                rangeLow: this.state.rangeLow,
                rangeMidpoint: this.state.rangeMidpoint,
                breakoutLevel: this.state.rangeLow
            }
        };
        
        console.log(`🐎 ${this.name} SHORT signal generated`);        console.log(`   Entry: ${price.toFixed(2)}`);
        console.log(`   Stop: ${stopLoss.toFixed(2)}`);
        console.log(`   Target: ${takeProfit.toFixed(2)}`);
        console.log(`   Risk: ${riskPoints.toFixed(2)} pts`);
        console.log(`   Position: ${positionSizing.positionSize} contracts`);
        
        // Store position details
        this.state.stopLoss = stopLoss;
        this.state.takeProfit = takeProfit;
        this.state.positionSize = positionSizing.positionSize;
        
        return signal;
    }
    
    /**
     * Check for position addition at centerline (optional)
     */
    checkForPositionAddition(price) {
        if (!this.params.enableAddToPosition || this.state.hasAddedPosition) {
            return null;
        }
        
        // Check if price has retraced to the midpoint
        const tolerance = 0.5;  // Points tolerance
        
        if (this.state.currentPosition === 'LONG') {
            // For long positions, check if price retraced down to midpoint
            if (price <= this.state.rangeMidpoint + tolerance && price >= this.state.rangeMidpoint - tolerance) {
                console.log(`📈 Adding to LONG position at midpoint: ${price.toFixed(2)}`);
                this.state.hasAddedPosition = true;
                this.state.addedPositionPrice = price;                
                // Return signal to add to position
                return {
                    direction: 'ADD_POSITION',
                    confidence: 'MEDIUM',
                    entryPrice: price,
                    positionSize: this.state.positionSize,  // Add same size
                    instrument: 'MGC',
                    timestamp: Date.now(),
                    reason: 'Retrace to range midpoint - adding to position',
                    strategyName: this.name,
                    strategyVersion: this.version
                };
            }
        } else if (this.state.currentPosition === 'SHORT') {
            // For short positions, check if price retraced up to midpoint
            if (price >= this.state.rangeMidpoint - tolerance && price <= this.state.rangeMidpoint + tolerance) {
                console.log(`📉 Adding to SHORT position at midpoint: ${price.toFixed(2)}`);
                this.state.hasAddedPosition = true;
                this.state.addedPositionPrice = price;
                
                // Return signal to add to position
                return {
                    direction: 'ADD_POSITION',
                    confidence: 'MEDIUM',
                    entryPrice: price,
                    positionSize: this.state.positionSize,  // Add same size
                    instrument: 'MGC',
                    timestamp: Date.now(),
                    reason: 'Retrace to range midpoint - adding to position',
                    strategyName: this.name,                    strategyVersion: this.version
                };
            }
        }
        
        return null;
    }
    
    /**
     * Check for deleveraging opportunity (optional)
     */
    checkForDeleveraging(price) {
        if (!this.params.enableDeleveraging || !this.state.hasAddedPosition || this.state.hasDeleveraged) {
            return null;
        }
        
        // Check if position is back in profit after adding
        if (this.state.currentPosition === 'LONG') {
            // For long, check if price is above our average entry
            const avgEntry = (this.state.entryPrice + this.state.addedPositionPrice) / 2;
            if (price > avgEntry + 1.0) {  // 1 point profit
                console.log(`💰 Deleveraging LONG position at profit: ${price.toFixed(2)}`);
                this.state.hasDeleveraged = true;
                
                return {
                    direction: 'PARTIAL_CLOSE',
                    confidence: 'MEDIUM',
                    exitPrice: price,
                    positionSize: this.state.positionSize,  // Close added size
                    instrument: 'MGC',
                    timestamp: Date.now(),                    reason: 'Position back in profit - deleveraging',
                    strategyName: this.name,
                    strategyVersion: this.version
                };
            }
        } else if (this.state.currentPosition === 'SHORT') {
            // For short, check if price is below our average entry
            const avgEntry = (this.state.entryPrice + this.state.addedPositionPrice) / 2;
            if (price < avgEntry - 1.0) {  // 1 point profit
                console.log(`💰 Deleveraging SHORT position at profit: ${price.toFixed(2)}`);
                this.state.hasDeleveraged = true;
                
                return {
                    direction: 'PARTIAL_CLOSE',
                    confidence: 'MEDIUM',
                    exitPrice: price,
                    positionSize: this.state.positionSize,  // Close added size
                    instrument: 'MGC',
                    timestamp: Date.now(),
                    reason: 'Position back in profit - deleveraging',
                    strategyName: this.name,
                    strategyVersion: this.version
                };
            }
        }
        
        return null;
    }
    
    /**
     * Update shelf tracking for trailing profits     */
    updateShelfTracking(price) {
        if (!this.state.currentPosition) return;
        
        // Initialize watermarks if needed
        if (this.state.currentPosition === 'LONG') {
            if (this.state.lastHighWaterMark === null || price > this.state.lastHighWaterMark) {
                this.state.lastHighWaterMark = price;
            }
            
            // Check for shelf formation (consolidation after move up)
            const pullback = this.state.lastHighWaterMark - price;
            if (pullback >= this.params.shelfMinPoints) {
                // Potential shelf forming
                if (!this.state.currentShelf) {
                    this.state.currentShelf = {
                        level: this.state.lastHighWaterMark,
                        bars: 1
                    };
                } else {
                    this.state.currentShelf.bars++;
                    
                    // Confirm shelf after consolidation
                    if (this.state.currentShelf.bars >= this.params.shelfConsolidationBars) {
                        this.confirmShelf('LONG');
                    }
                }
            } else if (this.state.currentShelf && price > this.state.currentShelf.level) {
                // Price broke above shelf, reset
                this.state.currentShelf = null;
            }            
        } else if (this.state.currentPosition === 'SHORT') {
            if (this.state.lastLowWaterMark === null || price < this.state.lastLowWaterMark) {
                this.state.lastLowWaterMark = price;
            }
            
            // Check for shelf formation (consolidation after move down)
            const bounce = price - this.state.lastLowWaterMark;
            if (bounce >= this.params.shelfMinPoints) {
                // Potential shelf forming
                if (!this.state.currentShelf) {
                    this.state.currentShelf = {
                        level: this.state.lastLowWaterMark,
                        bars: 1
                    };
                } else {
                    this.state.currentShelf.bars++;
                    
                    // Confirm shelf after consolidation
                    if (this.state.currentShelf.bars >= this.params.shelfConsolidationBars) {
                        this.confirmShelf('SHORT');
                    }
                }
            } else if (this.state.currentShelf && price < this.state.currentShelf.level) {
                // Price broke below shelf, reset
                this.state.currentShelf = null;
            }
        }
    }
    
    /**     * Confirm shelf formation and update stop loss
     */
    confirmShelf(direction) {
        this.state.shelfCount++;
        
        if (direction === 'LONG') {
            const newStop = this.state.currentShelf.level - this.params.shelfMinPoints;
            
            // Move stop to break-even after first shelf
            if (this.state.shelfCount === 1 && this.params.moveToBreakEven && !this.state.stopMovedToBreakEven) {
                this.state.stopLoss = Math.max(this.state.entryPrice, newStop);
                this.state.stopMovedToBreakEven = true;
                console.log(`🛡️ Stop moved to break-even: ${this.state.stopLoss.toFixed(2)}`);
            } else if (newStop > this.state.stopLoss) {
                this.state.stopLoss = newStop;
                console.log(`📊 Shelf ${this.state.shelfCount} formed - trailing stop to: ${this.state.stopLoss.toFixed(2)}`);
            }
        } else if (direction === 'SHORT') {
            const newStop = this.state.currentShelf.level + this.params.shelfMinPoints;
            
            // Move stop to break-even after first shelf
            if (this.state.shelfCount === 1 && this.params.moveToBreakEven && !this.state.stopMovedToBreakEven) {
                this.state.stopLoss = Math.min(this.state.entryPrice, newStop);
                this.state.stopMovedToBreakEven = true;
                console.log(`🛡️ Stop moved to break-even: ${this.state.stopLoss.toFixed(2)}`);
            } else if (newStop < this.state.stopLoss) {
                this.state.stopLoss = newStop;
                console.log(`📊 Shelf ${this.state.shelfCount} formed - trailing stop to: ${this.state.stopLoss.toFixed(2)}`);
            }        }
        
        // Reset current shelf tracking
        this.state.currentShelf = null;
    }
    
    /**
     * Check for exit conditions
     */
    checkForExit(price, timestamp) {
        if (!this.state.currentPosition) return null;
        
        let shouldExit = false;
        let exitReason = '';
        
        // Check stop loss
        if (this.state.currentPosition === 'LONG') {
            if (price <= this.state.stopLoss) {
                shouldExit = true;
                exitReason = 'Stop loss hit';
            } else if (price >= this.state.takeProfit) {
                shouldExit = true;
                exitReason = 'Take profit reached';
            }
        } else if (this.state.currentPosition === 'SHORT') {
            if (price >= this.state.stopLoss) {
                shouldExit = true;
                exitReason = 'Stop loss hit';
            } else if (price <= this.state.takeProfit) {
                shouldExit = true;                exitReason = 'Take profit reached';
            }
        }
        
        // Check maximum dollar loss
        const currentLoss = this.calculateCurrentPnL(price);
        if (currentLoss < -this.params.maxDollarLoss) {
            shouldExit = true;
            exitReason = `Maximum dollar loss reached: $${Math.abs(currentLoss).toFixed(2)}`;
        }
        
        if (shouldExit) {
            const signal = {
                direction: 'CLOSE_POSITION',
                confidence: 'HIGH',
                exitPrice: price,
                instrument: 'MGC',
                positionSize: this.state.positionSize,
                timestamp: Date.now(),
                reason: exitReason,
                strategyName: this.name,
                strategyVersion: this.version,
                closeType: 'full',
                pnl: currentLoss
            };
            
            console.log(`🏁 Closing ${this.state.currentPosition} position: ${exitReason}`);
            console.log(`   PnL: $${currentLoss.toFixed(2)}`);
            
            // Reset position state
            this.resetPositionState();            
            return signal;
        }
        
        return null;
    }
    
    /**
     * Calculate current P&L
     */
    calculateCurrentPnL(currentPrice) {
        if (!this.state.currentPosition || !this.state.entryPrice) return 0;
        
        let pnlPoints = 0;
        if (this.state.currentPosition === 'LONG') {
            pnlPoints = currentPrice - this.state.entryPrice;
        } else if (this.state.currentPosition === 'SHORT') {
            pnlPoints = this.state.entryPrice - currentPrice;
        }
        
        // Include added position if applicable
        if (this.state.hasAddedPosition && this.state.addedPositionPrice) {
            let addedPnlPoints = 0;
            if (this.state.currentPosition === 'LONG') {
                addedPnlPoints = currentPrice - this.state.addedPositionPrice;
            } else if (this.state.currentPosition === 'SHORT') {
                addedPnlPoints = this.state.addedPositionPrice - currentPrice;
            }
            
            // If not deleveraged, include full added position P&L
            if (!this.state.hasDeleveraged) {                pnlPoints += addedPnlPoints;
            }
        }
        
        return pnlPoints * this.state.positionSize * this.params.dollarPerPoint;
    }
    
    /**
     * Reset position state after exit
     */
    resetPositionState() {
        this.state.currentPosition = null;
        this.state.positionOpenTime = null;
        this.state.entryPrice = null;
        this.state.stopLoss = null;
        this.state.takeProfit = null;
        this.state.positionSize = 1;
        this.state.hasAddedPosition = false;
        this.state.addedPositionPrice = null;
        this.state.hasDeleveraged = false;
        this.state.currentShelf = null;
        this.state.shelfCount = 0;
        this.state.stopMovedToBreakEven = false;
        this.state.lastHighWaterMark = null;
        this.state.lastLowWaterMark = null;
        
        this.savePositionState();
    }
    
    /**
     * Update candle data     */
    updateCandle(price, volume, timestamp) {
        const candleTime = new Date(timestamp);
        candleTime.setMinutes(Math.floor(candleTime.getMinutes()), 0, 0);
        const candleTimeMs = candleTime.getTime();
        
        if (!this.lastCandleTime || candleTimeMs !== this.lastCandleTime) {
            if (this.currentCandle && this.currentCandle.close !== null) {
                this.candles.push({ ...this.currentCandle });
                if (this.candles.length > this.params.maxCandleHistory) {
                    this.candles = this.candles.slice(-this.params.maxCandleHistory);
                }
            }
            
            this.currentCandle = {
                timestamp: candleTimeMs,
                open: price,
                high: price,
                low: price,
                close: price,
                volume: volume
            };
            this.lastCandleTime = candleTimeMs;
            return true;
        } else {
            this.currentCandle.high = Math.max(this.currentCandle.high, price);
            this.currentCandle.low = Math.min(this.currentCandle.low, price);
            this.currentCandle.close = price;
            this.currentCandle.volume += volume;
            return false;
        }    }
    
    /**
     * Update 5-minute candles for breakout detection
     */
    update5MinCandles(price, volume, timestamp) {
        const candleTime = new Date(timestamp);
        const minutes = candleTime.getMinutes();
        const roundedMinutes = Math.floor(minutes / 5) * 5;
        candleTime.setMinutes(roundedMinutes, 0, 0);
        const candleTimeMs = candleTime.getTime();
        
        let currentFiveMinCandle = this.fiveMinCandles.find(c => c.timestamp === candleTimeMs);
        
        if (!currentFiveMinCandle) {
            currentFiveMinCandle = {
                timestamp: candleTimeMs,
                open: price,
                high: price,
                low: price,
                close: price,
                volume: volume,
                complete: false
            };
            this.fiveMinCandles.push(currentFiveMinCandle);
            
            // Mark previous candle as complete
            if (this.fiveMinCandles.length > 1) {
                this.fiveMinCandles[this.fiveMinCandles.length - 2].complete = true;
            }
                        // Keep only recent candles
            if (this.fiveMinCandles.length > 50) {
                this.fiveMinCandles = this.fiveMinCandles.slice(-50);
            }
        } else {
            currentFiveMinCandle.high = Math.max(currentFiveMinCandle.high, price);
            currentFiveMinCandle.low = Math.min(currentFiveMinCandle.low, price);
            currentFiveMinCandle.close = price;
            currentFiveMinCandle.volume += volume;
        }
    }
    
    /**
     * Get the last complete 5-minute candle
     */
    getLastComplete5MinCandle() {
        const completeCandles = this.fiveMinCandles.filter(c => c.complete);
        return completeCandles.length > 0 ? completeCandles[completeCandles.length - 1] : null;
    }
    
    /**
     * Calculate position size based on risk
     */
    calculatePositionSize(riskPoints, direction) {
        const dollarRisk = this.params.dollarRiskPerTrade;
        const pointValue = this.params.dollarPerPoint;
        
        if (!dollarRisk || dollarRisk <= 0) {
            throw new Error('Invalid risk configuration - dollarRiskPerTrade not set');
        }        
        if (!pointValue || pointValue <= 0) {
            throw new Error('Invalid contract configuration - dollarPerPoint not set');
        }
        
        // Calculate exact position size
        const exactPositionSize = dollarRisk / (Math.abs(riskPoints) * pointValue);
        
        // Smart rounding - up to 50% over budget allowed
        let positionSize = Math.ceil(exactPositionSize);
        
        // Check if rounding up would exceed 50% over budget
        const roundedUpRisk = positionSize * Math.abs(riskPoints) * pointValue;
        const overRiskPercent = ((roundedUpRisk / dollarRisk - 1) * 100);
        
        if (overRiskPercent > 50) {
            // Too much risk, round down instead
            positionSize = Math.floor(exactPositionSize);
        }
        
        positionSize = Math.max(1, positionSize); // Ensure at least 1 contract
        
        // Calculate actual dollar amounts
        const actualDollarRisk = positionSize * Math.abs(riskPoints) * pointValue;
        const rewardPoints = Math.abs(riskPoints) * this.params.riskRewardRatio;
        const actualDollarReward = positionSize * rewardPoints * pointValue;
        
        return {
            positionSize,
            actualDollarRisk,            actualDollarReward,
            exactPositionSize
        };
    }
    
    /**
     * Initialize with historical data for immediate readiness
     */
    async initializeWithHistoricalData() {
        try {
            console.log(`🚀 [BOOTSTRAP] Starting historical data initialization for opening range...`);
            
            // Calculate time windows
            const now = new Date();
            const endTime = new Date(now);
            const startTime = new Date(now.getTime() - (48 * 60 * 60 * 1000)); // 48 hours
            
            // Prepare API request for historical bars
            const requestData = {
                contractId: "F.US.MGC",
                live: false,  // Always FALSE for historical bars
                startTime: startTime.toISOString(),
                endTime: endTime.toISOString(),
                unit: 2,  // Minute
                unitNumber: 5,  // 5-minute candles
                limit: 1000,
                includePartialBar: false
            };
            
            // Fetch historical data from Connection Manager
            const response = await this.fetchHistoricalData(requestData);            
            if (response && response.success && response.bars) {
                console.log(`✅ [BOOTSTRAP] Received ${response.bars.length} historical bars`);
                
                // Process historical data to find today's opening range
                this.processHistoricalDataForRange(response.bars);
                
                // Mark strategy as bootstrapped
                this.state.bootstrapped = true;
                this.state.isReady = true;
                
                console.log(`🐎 [BOOTSTRAP] Strategy ready with historical data`);
            }
        } catch (error) {
            console.log(`⚠️ [BOOTSTRAP] Failed: ${error.message}`);
            console.log(`⚠️ [BOOTSTRAP] Will form range from live feed`);
        }
    }
    
    /**
     * Process historical bars to form opening range
     */
    processHistoricalDataForRange(bars) {
        const today = new Date();
        today.setHours(this.params.sessionStartHour, this.params.sessionStartMinute, 0, 0);
        const rangeEndTime = new Date(today.getTime() + (this.params.rangeMinutes * 60000));
        
        // Find bars within today's opening range period
        const rangeBars = bars.filter(bar => {
            const barTime = new Date(bar.t);
            return barTime >= today && barTime <= rangeEndTime;        });
        
        if (rangeBars.length > 0) {
            // Calculate range from historical bars
            let rangeHigh = -Infinity;
            let rangeLow = Infinity;
            
            for (const bar of rangeBars) {
                rangeHigh = Math.max(rangeHigh, bar.h);
                rangeLow = Math.min(rangeLow, bar.l);
                
                // Also populate 5-minute candles
                this.fiveMinCandles.push({
                    timestamp: new Date(bar.t).getTime(),
                    open: bar.o,
                    high: bar.h,
                    low: bar.l,
                    close: bar.c,
                    volume: bar.v,
                    complete: true
                });
            }
            
            if (rangeHigh !== -Infinity && rangeLow !== Infinity) {
                this.state.rangeHigh = rangeHigh;
                this.state.rangeLow = rangeLow;
                this.state.rangeMidpoint = (rangeHigh + rangeLow) / 2;
                this.state.rangeFormed = true;
                this.state.rangeFormationTime = today;
                
                console.log(`📊 [BOOTSTRAP] Opening range loaded from historical data:`);                console.log(`   High: ${rangeHigh.toFixed(2)}`);
                console.log(`   Low: ${rangeLow.toFixed(2)}`);
                console.log(`   Midpoint: ${this.state.rangeMidpoint.toFixed(2)}`);
            }
        }
    }
    
    /**
     * Fetch historical data from Connection Manager
     */
    async fetchHistoricalData(requestData) {
        try {
            const response = await fetch('http://localhost:7500/api/market-data/bars', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            return await response.json();
        } catch (error) {
            console.error(`❌ [BOOTSTRAP] HTTP request failed: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Check if two dates are on different trading days
     */
    isDifferentTradingDay(date1, date2) {
        if (!date1 || !date2) return true;
        const d1 = new Date(date1);
        const d2 = new Date(date2);        return d1.toDateString() !== d2.toDateString();
    }
    
    /**
     * Analyze market environment
     */
    analyzeMarketEnvironment(price) {
        return {
            currentTime: new Date(),
            price: price,
            rangeFormed: this.state.rangeFormed,
            rangeHigh: this.state.rangeHigh,
            rangeLow: this.state.rangeLow,
            rangeMidpoint: this.state.rangeMidpoint,
            position: this.state.currentPosition,
            shelfCount: this.state.shelfCount
        };
    }
    
    /**
     * Check if strategy is ready to trade
     */
    isStrategyReady() {
        return this.state.isReady && this.state.rangeFormed;
    }
    
    /**
     * Get reason why strategy is not ready
     */
    getNotReadyReason() {
        if (!this.state.isReady) {
            return 'Strategy initializing';        }
        if (!this.state.rangeFormed) {
            return 'Waiting for opening range to form';
        }
        return 'Unknown';
    }
    
    /**
     * Get status summary for UI
     */
    getStatusSummary() {
        return {
            module: 'Strategy',
            status: this.isStrategyReady() ? 'READY' : 'INITIALIZING',
            name: this.name,
            version: this.version,
            strategyType: 'Opening Range Breakout',
            isReady: this.isStrategyReady(),
            debug: {
                rangeFormed: this.state.rangeFormed,
                rangeHigh: this.state.rangeHigh,
                rangeLow: this.state.rangeLow,
                currentPosition: this.state.currentPosition,
                shelfCount: this.state.shelfCount,
                stopAtBreakEven: this.state.stopMovedToBreakEven,
                candleCount: this.candles.length,
                fiveMinCandleCount: this.fiveMinCandles.length
            }
        };
    }
    
    /**     * Get debug information
     */
    getDebugInfo() {
        return {
            rangeStatus: this.state.rangeFormed ? 'Formed' : 'Forming',
            position: this.state.currentPosition || 'None',
            entryPrice: this.state.entryPrice,
            currentStop: this.state.stopLoss,
            shelfCount: this.state.shelfCount,
            positionAdditions: this.state.hasAddedPosition,
            deleveraged: this.state.hasDeleveraged
        };
    }
    
    /**
     * Save position state to file
     */
    async savePositionState() {
        try {
            const dir = path.dirname(this.stateFilePath);
            await fs.mkdir(dir, { recursive: true });
            
            const stateData = {
                currentPosition: this.state.currentPosition,
                positionOpenTime: this.state.positionOpenTime ? 
                    this.state.positionOpenTime.toISOString() : null,
                entryPrice: this.state.entryPrice,
                stopLoss: this.state.stopLoss,
                takeProfit: this.state.takeProfit,
                positionSize: this.state.positionSize,
                hasAddedPosition: this.state.hasAddedPosition,                addedPositionPrice: this.state.addedPositionPrice,
                hasDeleveraged: this.state.hasDeleveraged,
                shelfCount: this.state.shelfCount,
                stopMovedToBreakEven: this.state.stopMovedToBreakEven,
                savedAt: new Date().toISOString(),
                version: this.version
            };
            
            await fs.writeFile(this.stateFilePath, JSON.stringify(stateData, null, 2), 'utf8');
        } catch (error) {
            console.log(`❌ Failed to save position state: ${error.message}`);
        }
    }
    
    /**
     * Load position state on startup
     */
    async loadPositionState() {
        try {
            const stateContent = await fs.readFile(this.stateFilePath, 'utf8');
            const stateData = JSON.parse(stateContent);
            
            if (stateData.currentPosition) {
                this.state.currentPosition = stateData.currentPosition;
                this.state.positionOpenTime = stateData.positionOpenTime ? 
                    new Date(stateData.positionOpenTime) : null;
                this.state.entryPrice = stateData.entryPrice;
                this.state.stopLoss = stateData.stopLoss;
                this.state.takeProfit = stateData.takeProfit;
                this.state.positionSize = stateData.positionSize;                this.state.hasAddedPosition = stateData.hasAddedPosition;
                this.state.addedPositionPrice = stateData.addedPositionPrice;
                this.state.hasDeleveraged = stateData.hasDeleveraged;
                this.state.shelfCount = stateData.shelfCount;
                this.state.stopMovedToBreakEven = stateData.stopMovedToBreakEven;
                
                console.log(`📂 Loaded saved position state: ${this.state.currentPosition}`);
            }
        } catch (error) {
            if (error.code === 'ENOENT') {
                console.log(`📂 No existing state file found, starting fresh`);
            } else {
                console.log(`❌ Failed to load position state: ${error.message}`);
            }
        }
    }
    
    /**
     * Reset strategy state
     */
    reset() {
        this.state = {
            rangeHigh: null,
            rangeLow: null,
            rangeMidpoint: null,
            rangeFormed: false,
            rangeFormationTime: null,
            currentPosition: null,
            positionOpenTime: null,
            entryPrice: null,
            stopLoss: null,            takeProfit: null,
            positionSize: 1,
            hasAddedPosition: false,
            addedPositionPrice: null,
            hasDeleveraged: false,
            currentShelf: null,
            shelfCount: 0,
            stopMovedToBreakEven: false,
            lastHighWaterMark: null,
            lastLowWaterMark: null,
            isReady: false,
            lastSignalTime: null,
            bootstrapped: false
        };
        
        this.candles = [];
        this.currentCandle = null;
        this.lastCandleTime = null;
        this.fiveMinCandles = [];
        
        console.log('🔄 Strategy reset complete');
    }
}

module.exports = CrazyHorseStrategy;