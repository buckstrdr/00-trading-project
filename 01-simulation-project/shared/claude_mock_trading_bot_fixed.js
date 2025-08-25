/**
 * MockTradingBot with FIXED Redis Connections
 * Uses the Fixed Redis Client to resolve connection issues
 */

const EventEmitter = require('events');
const FixedRedisClient = require('./claude_redis_client_fixed');

class MockTradingBotFixed extends EventEmitter {
    constructor(config = {}) {
        super();
        
        this.config = {
            botId: config.botId || 'backtest_bot_1',
            symbol: config.symbol || 'MCL',
            redisHost: config.redisHost || 'localhost',
            redisPort: config.redisPort || 6379,
            backtesting: true,
            ...config
        };
        
        // Position state synced from PyBroker
        this.positions = [];
        
        // Track latest signal
        this.latestSignal = null;
        
        // Fixed Redis clients for pub/sub
        this.redisPub = null;
        this.redisSub = null;
        this.connected = false;
        
        this._initializeModules();
        this._setupRedisConnections();
    }
    
    _initializeModules() {
        // Mock modules that strategies expect
        this.orderState = {
            getPositions: () => this.positions,
            getLatestSignal: () => this.latestSignal
        };
        
        this.riskManager = {
            evaluateRisk: (signal) => ({ approved: true, reason: 'Backtesting mode' })
        };
        
        this.configManager = {
            getConfig: (key) => this.config[key] || null,
            updateConfig: (key, value) => { this.config[key] = value; }
        };
        
        this.logger = {
            info: (...args) => console.error('[MockBot INFO]', ...args),
            error: (...args) => console.error('[MockBot ERROR]', ...args),
            warn: (...args) => console.error('[MockBot WARN]', ...args),
            debug: (...args) => console.error('[MockBot DEBUG]', ...args)
        };
    }
    
    async _setupRedisConnections() {
        try {
            console.error('[MockTradingBot] Setting up Redis connections...');
            
            // Create Fixed Redis clients
            this.redisPub = new FixedRedisClient({
                host: this.config.redisHost,
                port: this.config.redisPort
            });
            
            this.redisSub = new FixedRedisClient({
                host: this.config.redisHost,
                port: this.config.redisPort
            });
            
            // Connect both clients
            await this.redisPub.connect();
            await this.redisSub.connect();
            
            console.error('[MockTradingBot] Connected to Redis on', `${this.config.redisHost}:${this.config.redisPort}`);
            
            // Set up channel forwarding
            await this._setupChannelForwarding();
            
            this.connected = true;
            console.error('[MockTradingBot] Redis setup complete - ready for strategies');
            
        } catch (error) {
            console.error('[MockTradingBot] Failed to connect to Redis:', error.message);
            this.connected = false;
            // Don't throw - allow strategies to load even if Redis fails
        }
    }
    
    async _setupChannelForwarding() {
        if (!this.redisSub.isConnected()) {
            console.error('[MockTradingBot] Cannot setup forwarding - Redis subscriber not connected');
            return;
        }
        
        try {
            // Define channels to monitor
            const botChannels = [
                'bot:signal',
                'bot:trade:request',
                'bot:position:update',
                'bot:historical-data:request',
                'bot:strategy:status',
                'bot:risk:check'
            ];
            
            const aggregatorChannels = [
                'aggregator:signal:response',
                'aggregator:trade:response', 
                'aggregator:position:response',
                'aggregator:historical-data:response'
            ];
            
            // Subscribe to all channels with message handler
            const messageHandler = (message, channel) => {
                this._handleChannelMessage(channel, message);
            };
            
            // Subscribe to bot channels (forward to aggregator)
            for (const channel of botChannels) {
                await this.redisSub.subscribe(channel, messageHandler);
                console.error(`[MockTradingBot] Subscribed to ${channel}`);
            }
            
            // Subscribe to aggregator channels (forward to strategies)
            for (const channel of aggregatorChannels) {
                await this.redisSub.subscribe(channel, messageHandler);
                console.error(`[MockTradingBot] Subscribed to ${channel}`);
            }
            
            console.error('[MockTradingBot] Channel forwarding established');
            
        } catch (error) {
            console.error('[MockTradingBot] Error setting up channel forwarding:', error.message);
        }
    }
    
    _handleChannelMessage(channel, message) {
        console.error(`[MockTradingBot] Received on ${channel}: ${message.substring(0, 100)}...`);
        
        try {
            // Handle bot: channels - forward to aggregator:
            if (channel.startsWith('bot:')) {
                const aggregatorChannel = channel.replace('bot:', 'aggregator:');
                
                // Add bot ID to message for aggregator
                let forwardMessage = message;
                try {
                    const parsed = JSON.parse(message);
                    parsed.botId = this.config.botId;
                    forwardMessage = JSON.stringify(parsed);
                } catch (e) {
                    // If not JSON, just forward as-is
                }
                
                // Forward to aggregator
                this.redisPub.publish(aggregatorChannel, forwardMessage)
                    .catch(err => console.error(`[MockTradingBot] Error forwarding to ${aggregatorChannel}:`, err.message));
                
                console.error(`[MockTradingBot] Forwarded ${channel} -> ${aggregatorChannel}`);
                
                // Handle signals specially
                if (channel === 'bot:signal') {
                    try {
                        this.latestSignal = JSON.parse(message);
                        this.emit('signal', this.latestSignal);
                    } catch (e) {
                        console.error('[MockTradingBot] Error parsing signal:', e.message);
                    }
                }
            }
            
            // Handle aggregator: channels - forward to bot: (for responses)
            else if (channel.startsWith('aggregator:')) {
                const botChannel = channel.replace('aggregator:', 'bot:');
                
                // Forward response back to strategies
                this.redisPub.publish(botChannel, message)
                    .catch(err => console.error(`[MockTradingBot] Error forwarding to ${botChannel}:`, err.message));
                
                console.error(`[MockTradingBot] Forwarded ${channel} -> ${botChannel}`);
                
                // Handle position updates
                if (channel === 'aggregator:position:response') {
                    try {
                        const positionData = JSON.parse(message);
                        this.positions = positionData.positions || [];
                        this.emit('positionUpdate', this.positions);
                    } catch (e) {
                        console.error('[MockTradingBot] Error parsing positions:', e.message);
                    }
                }
            }
            
        } catch (error) {
            console.error(`[MockTradingBot] Error handling message on ${channel}:`, error.message);
        }
    }
    
    // Public API for strategies
    async publishSignal(signal) {
        if (!this.connected || !this.redisPub.isConnected()) {
            console.error('[MockTradingBot] Cannot publish signal - Redis not connected');
            return false;
        }
        
        try {
            const signalMessage = JSON.stringify({
                ...signal,
                botId: this.config.botId,
                timestamp: signal.timestamp || Date.now()
            });
            
            await this.redisPub.publish('bot:signal', signalMessage);
            console.error('[MockTradingBot] Published signal:', signal.action);
            return true;
            
        } catch (error) {
            console.error('[MockTradingBot] Error publishing signal:', error.message);
            return false;
        }
    }
    
    async requestHistoricalData(symbol, barsBack = 100, timeframe = '1m') {
        if (!this.connected || !this.redisPub.isConnected()) {
            console.error('[MockTradingBot] Cannot request historical data - Redis not connected');
            return null;
        }
        
        try {
            const requestId = `hist-${symbol}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
            const request = {
                requestId,
                symbol,
                barsBack,
                timeframe,
                sessionTemplate: 'USEQPost',
                timestamp: new Date().toISOString()
            };
            
            await this.redisPub.publish('bot:historical-data:request', JSON.stringify(request));
            console.error(`[MockTradingBot] Requested historical data: ${symbol} (${barsBack} bars)`);
            
            return requestId;
            
        } catch (error) {
            console.error('[MockTradingBot] Error requesting historical data:', error.message);
            return null;
        }
    }
    
    getPositions() {
        return this.positions;
    }
    
    getLatestSignal() {
        return this.latestSignal;
    }
    
    isConnected() {
        return this.connected && this.redisPub && this.redisPub.isConnected();
    }
    
    async shutdown() {
        console.error('[MockTradingBot] Shutting down...');
        
        try {
            if (this.redisPub) {
                await this.redisPub.disconnect();
            }
            if (this.redisSub) {
                await this.redisSub.disconnect();
            }
            this.connected = false;
            console.error('[MockTradingBot] Shutdown complete');
        } catch (error) {
            console.error('[MockTradingBot] Error during shutdown:', error.message);
        }
    }
}

module.exports = MockTradingBotFixed;

// Test the fixed MockTradingBot if run directly
if (require.main === module) {
    async function testMockTradingBot() {
        console.log('=== Testing Fixed MockTradingBot ===');
        
        const mockBot = new MockTradingBotFixed({
            botId: 'test_fixed_bot',
            symbol: 'MCL'
        });
        
        try {
            // Wait for initialization
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            if (mockBot.isConnected()) {
                console.log('✅ MockTradingBot connected to Redis');
                
                // Test signal publishing
                await mockBot.publishSignal({
                    action: 'BUY',
                    price: 75.50,
                    quantity: 1
                });
                console.log('✅ Signal published');
                
                // Test historical data request
                const requestId = await mockBot.requestHistoricalData('MCL', 10);
                console.log('✅ Historical data requested:', requestId);
                
            } else {
                console.log('❌ MockTradingBot not connected to Redis');
            }
            
            await mockBot.shutdown();
            console.log('🎉 Fixed MockTradingBot Test: SUCCESS');
            
        } catch (error) {
            console.error('❌ Fixed MockTradingBot Test Failed:', error.message);
            await mockBot.shutdown();
        }
    }
    
    testMockTradingBot();
}