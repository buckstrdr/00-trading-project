/**
 * Strategy Runner with MockTradingBot
 * Hosts TSX strategies with full mainBot interface
 */

const MockTradingBot = require('./mock_trading_bot_real_redis');
const path = require('path');

class StrategyRunner {
    constructor(strategyPath, config = {}) {
        this.strategyPath = strategyPath;
        this.config = config;
        this.mockBot = null;
        this.strategy = null;
        this.ready = false;
        
        this.initialize();
    }
    
    async initialize() {
        try {
            // Create MockTradingBot instance
            this.mockBot = new MockTradingBot(this.config);
            
            // Wait a bit for Redis connections
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Load strategy class
            const StrategyClass = require(path.resolve(this.strategyPath));
            
            // Initialize strategy with config and mockBot (as mainBot)
            this.strategy = new StrategyClass(this.config, this.mockBot);
            
            console.error(`[StrategyRunner] Strategy loaded: ${path.basename(this.strategyPath)}`);
            
            // Set up communication with Python
            this.setupCommunication();
            
            this.ready = true;
            
            // Signal ready to Python
            this.sendMessage({
                type: 'READY',
                strategy: path.basename(this.strategyPath),
                hasProcessMarketData: !!this.strategy.processMarketData,
                hasAnalyze: !!this.strategy.analyze,
                pid: process.pid
            });
            
        } catch (error) {
            console.error('[StrategyRunner] Initialization error:', error);
            this.sendMessage({
                type: 'ERROR',
                error: error.message,
                stack: error.stack
            });
            process.exit(1);
        }
    }
    
    setupCommunication() {
        // Handle incoming messages from Python via stdin
        process.stdin.on('data', async (data) => {
            try {
                const messages = data.toString().trim().split('\n');
                for (const msgStr of messages) {
                    if (!msgStr) continue;
                    
                    const message = JSON.parse(msgStr);
                    await this.handleMessage(message);
                }
            } catch (error) {
                console.error('[StrategyRunner] Error handling message:', error);
                this.sendMessage({
                    type: 'ERROR',
                    error: error.message
                });
            }
        });
        
        // Handle process signals
        process.on('SIGTERM', () => this.shutdown());
        process.on('SIGINT', () => this.shutdown());
    }
    
    async handleMessage(message) {
        if (!this.ready && message.type !== 'INIT') {
            console.error('[StrategyRunner] Not ready, ignoring message');
            return;
        }
        
        switch(message.type) {
            case 'MARKET_DATA':
                await this.processMarketData(message.data);
                break;
                
            case 'POSITION_UPDATE':
                this.mockBot.updatePositions(message.data.positions || []);
                this.sendMessage({
                    type: 'ACK',
                    message: 'Positions updated'
                });
                break;
                
            case 'HISTORICAL_DATA':
                // Handle historical data response
                if (this.mockBot.redisPub) {
                    await this.mockBot.redisPub.publish(
                        'bot:historical-data:response',
                        JSON.stringify(message.data)
                    );
                }
                break;
                
            case 'SHUTDOWN':
                await this.shutdown();
                break;
                
            default:
                console.error(`[StrategyRunner] Unknown message type: ${message.type}`);
        }
    }
    
    async processMarketData(data) {
        try {
            // Send market data to strategy via Redis (strategies listen to bot:market-data)
            await this.mockBot.sendMarketData({
                price: data.close,
                volume: data.volume,
                timestamp: data.timestamp,
                open: data.open,
                high: data.high,
                low: data.low,
                close: data.close
            });
            
            // Call strategy's processMarketData method if it exists
            let signal = null;
            
            if (this.strategy.processMarketData) {
                // TSX V5 style
                signal = await this.strategy.processMarketData(
                    data.close,
                    data.volume,
                    data.timestamp
                );
            } else if (this.strategy.analyze) {
                // Alternative method name
                signal = await this.strategy.analyze({
                    open: data.open,
                    high: data.high,
                    low: data.low,
                    close: data.close,
                    volume: data.volume,
                    timestamp: data.timestamp
                });
            }
            
            // Send signal back to Python
            if (signal) {
                this.sendMessage({
                    type: 'SIGNAL',
                    data: signal,
                    timestamp: Date.now()
                });
            }
            
        } catch (error) {
            console.error('[StrategyRunner] Error processing market data:', error);
            this.sendMessage({
                type: 'ERROR',
                error: error.message,
                context: 'processMarketData'
            });
        }
    }
    
    sendMessage(message) {
        process.stdout.write(JSON.stringify(message) + '\n');
    }
    
    async shutdown() {
        console.error('[StrategyRunner] Shutting down...');
        
        try {
            // Clean up strategy
            if (this.strategy && this.strategy.cleanup) {
                await this.strategy.cleanup();
            }
            
            // Shutdown MockTradingBot
            if (this.mockBot) {
                await this.mockBot.shutdown();
            }
            
            this.sendMessage({
                type: 'SHUTDOWN_COMPLETE'
            });
            
            process.exit(0);
        } catch (error) {
            console.error('[StrategyRunner] Shutdown error:', error);
            process.exit(1);
        }
    }
}

// Start if run directly
if (require.main === module) {
    const strategyPath = process.argv[2];
    const configStr = process.argv[3];
    
    if (!strategyPath) {
        console.error('Usage: node strategy_runner_enhanced.js <strategy_path> [config_json]');
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
    
    new StrategyRunner(strategyPath, config);
}

module.exports = StrategyRunner;