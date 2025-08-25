/**
 * MockTradingBot with REAL Redis Channels
 * 
 * Acts exactly like the real TradingBot:
 * - Strategies publish to bot: channels (using their own Redis clients)
 * - MockTradingBot forwards between bot: and aggregator: channels
 * - PyBroker bridge listens to aggregator: channels
 * 
 * This maintains the exact production communication architecture
 */

const EventEmitter = require('events');
const redis = require('redis');

class MockTradingBotRealRedis extends EventEmitter {
    constructor(config = {}) {
        super();
        
        this.config = {
            botId: config.botId || 'backtest_bot_1',
            symbol: config.symbol || 'NQ',
            redisHost: config.redisHost || 'localhost',
            redisPort: config.redisPort || 6379,
            backtesting: true,
            ...config
        };
        
        // Position state synced from PyBroker
        this.positions = [];
        
        // Track latest signal
        this.latestSignal = null;
        
        // Real Redis clients for pub/sub
        this.redisPub = null;
        this.redisSub = null;
        
        this._initializeModules();
        this._setupRedisConnections();
    }
    
    async _setupRedisConnections() {
        try {
            // Create Redis publisher client (redis@4.7.1 syntax with legacyMode)
            this.redisPub = redis.createClient({
                socket: {
                    host: this.config.redisHost,
                    port: this.config.redisPort
                },
                legacyMode: true  // CRITICAL: Required for callback-style pub/sub
            });
            
            // Create Redis subscriber client (separate connection required for sub)
            this.redisSub = redis.createClient({
                socket: {
                    host: this.config.redisHost,
                    port: this.config.redisPort
                },
                legacyMode: true  // CRITICAL: Required for callback-style pub/sub
            });
            
            // Handle Redis errors
            this.redisPub.on('error', (err) => {
                console.error('[MockTradingBot] Redis publisher error:', err);
            });
            
            this.redisSub.on('error', (err) => {
                console.error('[MockTradingBot] Redis subscriber error:', err);
            });
            
            // Connect to Redis
            await this.redisPub.connect();
            await this.redisSub.connect();
            
            console.error('[MockTradingBot] Connected to Redis on', `${this.config.redisHost}:${this.config.redisPort}`);
            
            // Set up channel forwarding (just like real TradingBot)
            await this._setupChannelForwarding();
            
        } catch (error) {
            console.error('[MockTradingBot] Failed to connect to Redis:', error);
            // In backtest mode, we might want to continue without Redis
            console.error('[MockTradingBot] Running in Redis-less mode for testing');
        }
    }
    
    async _setupChannelForwarding() {
        // Set up message handler for ALL channels
        this.redisSub.on('message', (channel, message) => {
            console.error(`[MockTradingBot] Received on ${channel}:`, message);
            
            // Handle bot: channels - forward to aggregator:
            if (channel.startsWith('bot:')) {
                const aggregatorChannel = channel.replace('bot:', 'aggregator:');
                
                // Add bot ID to message for aggregator
                let forwardMessage = message;
                try {
                    const parsed = JSON.parse(message);
                    parsed.botId = this.config.botId;
                    parsed.timestamp = Date.now();
                    forwardMessage = JSON.stringify(parsed);
                } catch (e) {
                    // If not JSON, forward as-is
                }
                
                this.redisPub.publish(aggregatorChannel, forwardMessage);
                console.error(`[MockTradingBot] Forwarded to ${aggregatorChannel}`);
                
                // Emit local event for monitoring
                this.emit('message-forwarded', {
                    from: channel,
                    to: aggregatorChannel,
                    message: forwardMessage
                });
            }
            
            // Handle aggregator: response channels - forward back to bot:
            if (channel.startsWith('aggregator:') && channel.includes(':response')) {
                const botChannel = channel.replace('aggregator:', 'bot:');
                
                this.redisPub.publish(botChannel, message);
                console.error(`[MockTradingBot] Forwarded to ${botChannel}`);
                
                // Special handling for position updates
                if (channel === 'aggregator:position:response') {
                    this._handlePositionUpdate(message);
                }
            }
        });
        
        // Subscribe to bot: channels that strategies use
        const botChannels = [
            'bot:signal',
            'bot:trade:request',
            'bot:position:update',
            'bot:historical-data:request',
            'bot:strategy:status',
            'bot:risk:check'
        ];
        
        // Subscribe to each channel
        for (const channel of botChannels) {
            await this.redisSub.subscribe(channel);
            console.error(`[MockTradingBot] Subscribed to ${channel}`);
        }
        
        // Subscribe to aggregator: response channels
        const aggregatorResponseChannels = [
            'aggregator:signal:response',
            'aggregator:trade:response',
            'aggregator:position:response',
            'aggregator:historical-data:response'
        ];
        
        // Subscribe to each aggregator response channel
        for (const channel of aggregatorResponseChannels) {
            await this.redisSub.subscribe(channel);
            console.error(`[MockTradingBot] Subscribed to ${channel}`);
        }
        
        console.error('[MockTradingBot] Channel forwarding established');
    }
    
    _handlePositionUpdate(message) {
        try {
            const data = JSON.parse(message);
            if (data.positions) {
                this.updatePositions(data.positions);
            }
        } catch (e) {
            console.error('[MockTradingBot] Error handling position update:', e);
        }
    }
    
    _initializeModules() {
        const self = this;
        
        this.modules = {
            // POSITION MANAGEMENT MODULE
            // This is NOT a position tracking system - PyBroker handles all position tracking
            // This module is ONLY an interface that:
            // 1. Receives position updates from PyBroker 
            // 2. Stores them in this.positions array
            // 3. Provides the mainBot.modules.positionManagement API that strategies expect
            // 
            // PyBroker → updatePositions() → this.positions → strategies can check hasPosition()
            positionManagement: {
                hasPosition: () => {
                    return self.positions.length > 0;
                },
                
                getAllPositions: () => {
                    return [...self.positions];
                },
                
                getPosition: (symbol) => {
                    return self.positions.find(p => p.symbol === symbol || p.symbol === self.config.symbol);
                },
                
                getPositionSize: (symbol) => {
                    const position = self.positions.find(p => p.symbol === symbol || p.symbol === self.config.symbol);
                    return position ? position.quantity : 0;
                },
                
                getTotalPositionValue: () => {
                    return self.positions.reduce((total, pos) => {
                        return total + (pos.quantity * (pos.currentPrice || pos.entryPrice));
                    }, 0);
                },
                
                isLongPosition: () => {
                    const position = self.positions[0];
                    return position && (position.side === 'LONG' || position.side === 'BUY');
                },
                
                isShortPosition: () => {
                    const position = self.positions[0];
                    return position && (position.side === 'SHORT' || position.side === 'SELL');
                },
                
                getOpenPnL: () => {
                    return self.positions.reduce((total, pos) => {
                        const currentPrice = pos.currentPrice || pos.entryPrice;
                        const pnl = pos.side === 'LONG' 
                            ? (currentPrice - pos.entryPrice) * pos.quantity
                            : (pos.entryPrice - currentPrice) * pos.quantity;
                        return total + pnl;
                    }, 0);
                }
            },
            
            // Health monitoring - always healthy in backtest
            healthMonitoring: {
                isQuietMode: () => false,
                getQuietModeStatus: () => ({ enabled: false, reason: null, healthy: true }),
                setQuietMode: (enabled, reason = null) => {
                    console.error(`[MockTradingBot] Quiet mode ignored in backtest`);
                },
                getHealthStatus: () => ({
                    healthy: true,
                    quietMode: false,
                    timestamp: new Date().toISOString()
                })
            },
            
            // Keyboard interface - never active in backtest
            keyboardInterface: {
                getPromptState: () => ({ active: false, type: null }),
                setPromptState: (active, type = null) => {
                    console.error(`[MockTradingBot] Prompt state ignored in backtest`);
                },
                isPromptActive: () => false
            },
            
            // Manual trading - never active in backtest
            manualTrading: {
                awaitingConfirmation: false,
                getConfirmationState: function() { return false; },
                setConfirmationState: function(awaiting, type = null) {
                    console.error(`[MockTradingBot] Manual confirmation ignored in backtest`);
                },
                isAwaitingConfirmation: function() { return false; }
            },
            
            // Risk management - forward to aggregator via Redis
            riskManagement: {
                checkRisk: async (signal) => {
                    const request = {
                        botId: self.config.botId,
                        signal: signal,
                        timestamp: Date.now()
                    };
                    
                    // Publish to Redis for aggregator
                    if (self.redisPub) {
                        await self.redisPub.publish('bot:risk:check', JSON.stringify(request));
                    }
                    
                    // In backtest, assume risk check passes
                    return { passed: true, reason: 'Backtest mode' };
                }
            }
        };
    }
    
    /**
     * UPDATE POSITIONS FROM PYBROKER
     * 
     * This is the KEY METHOD that syncs PyBroker's position state to the MockTradingBot.
     * 
     * PyBroker tracks all actual positions, trades, P&L, etc.
     * This method just receives those positions and makes them available to strategies
     * through the positionManagement module interface.
     * 
     * Called by:
     * 1. Python bridge directly when PyBroker executes trades
     * 2. Via Redis message on 'aggregator:position:response' channel
     * 
     * @param {Array} positions - Array of position objects from PyBroker
     */
    updatePositions(positions) {
        // Convert PyBroker position format to TSX format that strategies expect
        this.positions = positions.map(pos => ({
            symbol: pos.symbol || this.config.symbol,
            side: pos.side || pos.direction || 'LONG',
            quantity: Math.abs(pos.quantity || pos.size || 0),
            entryPrice: pos.entry_price || pos.entryPrice || 0,
            currentPrice: pos.current_price || pos.currentPrice || pos.entry_price || 0,
            stopLoss: pos.stop_loss || pos.stopLoss || null,
            takeProfit: pos.take_profit || pos.takeProfit || null,
            timestamp: pos.timestamp || Date.now(),
            pnl: pos.pnl || 0,
            pnlPercent: pos.pnl_percent || 0
        }));
        
        console.error(`[MockTradingBot] Positions updated: ${this.positions.length} position(s)`);
        
        // Publish position update to Redis for strategies
        if (this.redisPub) {
            const update = {
                botId: this.config.botId,
                positions: this.positions,
                timestamp: Date.now()
            };
            this.redisPub.publish('bot:position:update', JSON.stringify(update));
        }
        
        // Emit local event
        this.emit('positions-updated', this.positions);
    }
    
    /**
     * Send market data to strategies via Redis
     * Called by PyBroker bridge
     */
    async sendMarketData(data) {
        if (this.redisPub) {
            const message = {
                botId: this.config.botId,
                symbol: data.symbol || this.config.symbol,
                price: data.price,
                volume: data.volume,
                timestamp: data.timestamp || Date.now(),
                ...data
            };
            
            await this.redisPub.publish('bot:market-data', JSON.stringify(message));
            console.error(`[MockTradingBot] Sent market data: ${data.price} @ ${data.volume}`);
        }
    }
    
    /**
     * Get current positions
     */
    getPositions() {
        return [...this.positions];
    }
    
    /**
     * Clean shutdown
     */
    async shutdown() {
        console.error('[MockTradingBot] Shutting down...');
        
        // Unsubscribe from all channels
        if (this.redisSub) {
            await this.redisSub.unsubscribe();
            await this.redisSub.quit();
        }
        
        if (this.redisPub) {
            await this.redisPub.quit();
        }
        
        this.removeAllListeners();
        console.error('[MockTradingBot] Shutdown complete');
    }
}

module.exports = MockTradingBotRealRedis;