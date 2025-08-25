/**
 * TSX V5 Compatible Strategy Runner for Enhanced Bridge (FIXED VERSION)
 * Runs TSX V5 strategies with proper mainBot interface and FIXED Redis communication
 */

const FixedRedisClient = require('./claude_redis_client_fixed');
const path = require('path');

class TSXv5StrategyRunner {
    constructor(strategyPath, config = {}) {
        this.strategyPath = path.resolve(strategyPath);
        this.config = config;
        this.strategy = null;
        this.ready = false;
        
        // BACKTESTER FIX: Track simulation datetime for historical data requests
        this.simulationDateTime = null;
        
        // Redis clients
        this.redisClient = null;
        this.redisPub = null;
        this.redisSub = null;
        
        // Mock mainBot interface for TSX V5 strategies
        this.mainBot = {
            // Strategy data access
            strategyState: {},
            positions: [],
            currentPrice: 0,
            
            // Historical data management  
            requestHistoricalData: this.requestHistoricalData.bind(this),
            
            // Signal generation
            generateSignal: this.generateSignal.bind(this),
            
            // Logging
            log: this.log.bind(this),
            logError: this.logError.bind(this),
            
            // Position management (mock)
            getCurrentPositions: () => this.mainBot.positions,
            getBalance: () => 100000, // Mock balance
            
            // Configuration access
            getConfig: (key) => this.config[key],
            
            // Redis access for strategies
            getRedisClient: () => this.redisClient,
            getRedisPublisher: () => this.redisPub
        };
        
        this.initialize();
    }
    
    async initialize() {
        try {
            console.log(`[TSXv5Runner] Initializing TSX V5 strategy runner...`);
            
            // Setup Redis connections
            await this.setupRedis();
            
            // Load the TSX V5 strategy
            await this.loadStrategy();
            
            // Setup Redis listeners
            await this.setupRedisListeners();
            
            // Request initial historical data
            await this.requestInitialHistoricalData();
            
            this.ready = true;
            console.log(`[TSXv5Runner] ready: true`);  // Format that bridge expects
            
            // PHASE 2A FIX: Also signal ready via Redis for reliable detection
            await this.redisPub.publish('aggregator:strategy-ready', JSON.stringify({
                botId: this.config.botId,
                ready: true,
                pid: process.pid,
                strategy: path.basename(this.strategyPath),
                timestamp: new Date().toISOString()
            }));
            console.log(`[TSXv5Runner] Ready signal sent via Redis channel`);  
            
        } catch (error) {
            console.error(`[TSXv5Runner] Initialization failed:`, error);
            process.exit(1);
        }
    }
    
    async setupRedis() {
        const redisConfig = {
            host: this.config.redisHost || 'localhost',
            port: this.config.redisPort || 6379
        };
        
        // Main Redis client (Fixed)
        this.redisClient = new FixedRedisClient(redisConfig);
        await this.redisClient.connect();
        
        // Publisher (Fixed)
        this.redisPub = new FixedRedisClient(redisConfig);
        await this.redisPub.connect();
        
        // Subscriber (Fixed)
        this.redisSub = new FixedRedisClient(redisConfig);
        await this.redisSub.connect();
        
        console.log(`[TSXv5Runner] Fixed Redis connections established`);
    }
    
    async loadStrategy() {
        try {
            // Load the strategy class
            const StrategyClass = require(this.strategyPath);
            
            // Initialize with params and mainBot
            this.strategy = new StrategyClass(this.config, this.mainBot);
            
            console.log(`[TSXv5Runner] Strategy loaded: ${path.basename(this.strategyPath)}`);
            
        } catch (error) {
            console.error(`[TSXv5Runner] Failed to load strategy:`, error);
            throw error;
        }
    }
    
    async setupRedisListeners() {
        // Listen for market data
        const marketDataChannel = `aggregator:market-data:${this.config.botId}`;
        
        await this.redisSub.subscribe(marketDataChannel, (message) => {
            try {
                this.handleMarketData(JSON.parse(message));
            } catch (error) {
                console.error(`[TSXv5Runner] Error handling market data:`, error);
            }
        });
        
        // BACKTESTER FIX: Listen for simulation datetime updates
        const simulationChannel = `aggregator:simulation:${this.config.botId}`;
        
        await this.redisSub.subscribe(simulationChannel, (message) => {
            try {
                const simData = JSON.parse(message);
                if (simData.type === 'SIMULATION_DATE' && simData.datetime) {
                    this.simulationDateTime = new Date(simData.datetime);
                    console.log(`[TSXv5Runner] Simulation datetime updated: ${this.simulationDateTime.toISOString()}`);
                }
            } catch (error) {
                console.error(`[TSXv5Runner] Error handling simulation data:`, error);
            }
        });
        
        console.log(`[TSXv5Runner] Listening for market data on: ${marketDataChannel}`);
        console.log(`[TSXv5Runner] Listening for simulation context on: ${simulationChannel}`);
    }
    
    async requestInitialHistoricalData() {
        // BACKTESTER FIX: Wait for simulation datetime context or use default historical date
        const barsBack = this.config.historicalBarsBack || 50;
        
        // For backtesting, use a reasonable historical date if no simulation context yet
        let requestDateTime = this.simulationDateTime;
        if (!requestDateTime) {
            // Default to June 1, 2023 for backtesting scenarios
            requestDateTime = new Date('2023-06-01T09:30:00.000Z');
            console.log(`[TSXv5Runner] Using default backtest date: ${requestDateTime.toISOString()}`);
        }
        
        // Store the datetime to use in requestHistoricalData
        this.historicalRequestDateTime = requestDateTime;
        
        await this.requestHistoricalData(this.config.symbol, barsBack);
        console.log(`[TSXv5Runner] Requested ${barsBack} historical bars for ${this.config.symbol} at ${requestDateTime.toISOString()}`);
    }
    
    async requestHistoricalData(symbol, barsBack) {
        const requestId = `hist_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // BACKTESTER FIX: Use stored historical request datetime, then simulation datetime, or current time
        const timestamp = this.historicalRequestDateTime || this.simulationDateTime || new Date();
        
        const request = {
            requestId: requestId,
            symbol: symbol,
            barsBack: barsBack,
            timestamp: timestamp.toISOString()
        };
        
        // Send request on aggregator channel
        await this.redisPub.publish('aggregator:historical-data:request', JSON.stringify(request));
        
        console.log(`[TSXv5Runner] Historical data request sent: ${requestId} (${timestamp.toISOString()})`);
    }
    
    async handleMarketData(marketData) {
        try {
            // Update current price
            this.mainBot.currentPrice = marketData.price || marketData.close;
            
            // Call strategy's processMarketData if it exists
            if (this.strategy && this.strategy.processMarketData) {
                const result = await this.strategy.processMarketData(
                    marketData.price || marketData.close,
                    marketData.volume || 0,
                    marketData.timestamp || new Date().toISOString()
                );
                
                // BACKTESTER FIX: Extract actual signal from TSX strategy result format
                if (result && result.signal) {
                    console.log(`[TSXv5Runner] Strategy generated signal: ${result.signal.direction} at ${marketData.price}`);
                    this.handleStrategySignal(result.signal);
                } else if (result && result.ready === false) {
                    console.log(`[TSXv5Runner] Strategy not ready: ${result.debug?.reason || 'Unknown'}`);
                }
            }
            
        } catch (error) {
            console.error(`[TSXv5Runner] Error processing market data:`, error);
        }
    }
    
    generateSignal(signalData) {
        // Called by strategy to generate signals
        this.handleStrategySignal(signalData);
    }
    
    async handleStrategySignal(signal) {
        try {
            // BACKTESTER FIX: Convert TSX signal format to PyBroker-compatible format
            const enhancedSignal = {
                // Convert direction to action for PyBroker compatibility
                action: signal.direction || signal.action,
                price: signal.entryPrice || signal.price,
                shares: 100,  // Convert to shares for PyBroker (can be overridden by signal.positionSize)
                stop_loss: signal.stopLoss,
                take_profit: signal.takeProfit,
                
                // Preserve original TSX signal data
                tsx_signal: signal,
                
                // Add metadata  
                botId: this.config.botId,
                timestamp: signal.timestamp || new Date().toISOString(),
                strategy: path.basename(this.strategyPath)
            };
            
            // Publish signal on aggregator channel
            const signalChannel = `aggregator:signal:${this.config.botId}`;
            await this.redisPub.publish(signalChannel, JSON.stringify(enhancedSignal));
            
            console.log(`[TSXv5Runner] Signal published: ${enhancedSignal.action} at ${enhancedSignal.price}`);
            
        } catch (error) {
            console.error(`[TSXv5Runner] Error handling signal:`, error);
        }
    }
    
    log(message, level = 'INFO') {
        console.log(`[Strategy-${level}] ${message}`);
    }
    
    logError(message, error = null) {
        console.error(`[Strategy-ERROR] ${message}`, error || '');
    }
    
    async shutdown() {
        console.log(`[TSXv5Runner] Shutting down...`);
        
        try {
            // Cleanup strategy
            if (this.strategy && this.strategy.cleanup) {
                await this.strategy.cleanup();
            }
            
            // Close Redis connections
            if (this.redisClient) await this.redisClient.disconnect();
            if (this.redisPub) await this.redisPub.disconnect();
            if (this.redisSub) await this.redisSub.disconnect();
            
            console.log(`[TSXv5Runner] Shutdown complete`);
            process.exit(0);
            
        } catch (error) {
            console.error(`[TSXv5Runner] Shutdown error:`, error);
            process.exit(1);
        }
    }
}

// Handle process signals
process.on('SIGTERM', () => {
    if (global.runner) {
        global.runner.shutdown();
    } else {
        process.exit(0);
    }
});

process.on('SIGINT', () => {
    if (global.runner) {
        global.runner.shutdown();
    } else {
        process.exit(0);
    }
});

// Start if run directly
if (require.main === module) {
    const strategyPath = process.argv[2];
    const configStr = process.argv[3];
    
    if (!strategyPath) {
        console.error('Usage: node claude_tsx_v5_strategy_runner.js <strategy_path> [config_json]');
        process.exit(1);
    }
    
    let config = {};
    if (configStr) {
        try {
            config = JSON.parse(configStr);
        } catch (e) {
            console.error('Invalid config JSON:', e.message);
        }
    }
    
    global.runner = new TSXv5StrategyRunner(strategyPath, config);
}

module.exports = TSXv5StrategyRunner;