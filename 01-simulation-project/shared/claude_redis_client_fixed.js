/**
 * Fixed Redis Client for Node.js with redis@4.7.1
 * Resolves connection and disconnect timing issues
 */

const redis = require('redis');
const { EventEmitter } = require('events');

class FixedRedisClient extends EventEmitter {
    constructor(config = {}) {
        super();
        
        this.config = {
            host: config.host || 'localhost',
            port: config.port || 6379,
            retryAttempts: config.retryAttempts || 3,
            ...config
        };
        
        this.client = null;
        this.connected = false;
        this.connecting = false;
    }
    
    async connect() {
        if (this.connected) {
            return true;
        }
        
        if (this.connecting) {
            // Wait for existing connection attempt
            return new Promise((resolve) => {
                const checkConnection = () => {
                    if (this.connected) {
                        resolve(true);
                    } else if (!this.connecting) {
                        resolve(false);
                    } else {
                        setTimeout(checkConnection, 100);
                    }
                };
                checkConnection();
            });
        }
        
        this.connecting = true;
        
        try {
            console.log(`[FixedRedisClient] Connecting to Redis at ${this.config.host}:${this.config.port}...`);
            
            this.client = redis.createClient({
                socket: {
                    host: this.config.host,
                    port: this.config.port,
                    reconnectStrategy: (retries) => {
                        if (retries >= this.config.retryAttempts) {
                            return new Error('Too many retry attempts');
                        }
                        return Math.min(retries * 50, 500);
                    }
                },
                legacyMode: false  // Use modern mode for better error handling
            });
            
            // Set up event handlers
            this.client.on('connect', () => {
                console.log('[FixedRedisClient] Redis client connected');
                this.connected = true;
                this.connecting = false;
                this.emit('connect');
            });
            
            this.client.on('error', (err) => {
                console.error('[FixedRedisClient] Redis client error:', err.message);
                this.connected = false;
                this.connecting = false;
                this.emit('error', err);
            });
            
            this.client.on('end', () => {
                console.log('[FixedRedisClient] Redis connection ended');
                this.connected = false;
                this.emit('end');
            });
            
            // Actually connect
            await this.client.connect();
            
            // Test the connection
            await this.client.ping();
            console.log('[FixedRedisClient] Redis connection verified with ping');
            
            return true;
            
        } catch (error) {
            console.error('[FixedRedisClient] Failed to connect to Redis:', error.message);
            this.connected = false;
            this.connecting = false;
            throw error;
        }
    }
    
    async disconnect() {
        if (!this.connected || !this.client) {
            return true;
        }
        
        try {
            console.log('[FixedRedisClient] Disconnecting from Redis...');
            await this.client.disconnect();
            this.connected = false;
            console.log('[FixedRedisClient] Disconnected successfully');
            return true;
        } catch (error) {
            console.error('[FixedRedisClient] Error during disconnect:', error.message);
            this.connected = false;
            return false;
        }
    }
    
    async publish(channel, message) {
        if (!this.connected) {
            throw new Error('Redis client not connected');
        }
        
        try {
            const result = await this.client.publish(channel, message);
            return result;
        } catch (error) {
            console.error(`[FixedRedisClient] Error publishing to ${channel}:`, error.message);
            throw error;
        }
    }
    
    async subscribe(channel, callback) {
        if (!this.connected) {
            throw new Error('Redis client not connected');
        }
        
        try {
            await this.client.subscribe(channel, (message) => {
                callback(message, channel);
            });
            console.log(`[FixedRedisClient] Subscribed to channel: ${channel}`);
        } catch (error) {
            console.error(`[FixedRedisClient] Error subscribing to ${channel}:`, error.message);
            throw error;
        }
    }
    
    async unsubscribe(channel) {
        if (!this.connected) {
            return true;
        }
        
        try {
            await this.client.unsubscribe(channel);
            console.log(`[FixedRedisClient] Unsubscribed from channel: ${channel}`);
            return true;
        } catch (error) {
            console.error(`[FixedRedisClient] Error unsubscribing from ${channel}:`, error.message);
            return false;
        }
    }
    
    async ping() {
        if (!this.connected) {
            throw new Error('Redis client not connected');
        }
        
        try {
            const result = await this.client.ping();
            return result === 'PONG';
        } catch (error) {
            console.error('[FixedRedisClient] Ping failed:', error.message);
            return false;
        }
    }
    
    isConnected() {
        return this.connected;
    }
}

module.exports = FixedRedisClient;

// Test the fixed client if run directly
if (require.main === module) {
    async function testFixedRedisClient() {
        console.log('=== Testing Fixed Redis Client ===');
        
        const client = new FixedRedisClient({
            host: 'localhost',
            port: 6379
        });
        
        try {
            await client.connect();
            console.log('✅ Connection successful');
            
            const pingResult = await client.ping();
            console.log('✅ Ping result:', pingResult);
            
            // Test publish
            await client.publish('test:channel', JSON.stringify({ test: 'message', timestamp: Date.now() }));
            console.log('✅ Publish successful');
            
            await client.disconnect();
            console.log('✅ Disconnect successful');
            
            console.log('\n🎉 Fixed Redis Client Test: SUCCESS');
            
        } catch (error) {
            console.error('❌ Fixed Redis Client Test Failed:', error.message);
            console.error('Stack:', error.stack);
        }
    }
    
    testFixedRedisClient();
}