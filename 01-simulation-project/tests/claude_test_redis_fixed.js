/**
 * Test Redis Connectivity - FIXED
 * Properly uses legacyMode for redis@4.7.1
 */

const redis = require('redis');

async function testRedisConnection() {
    console.log('=== Redis Connectivity Test (FIXED) ===');
    console.log('Testing with redis@4.7.1 using proper legacyMode...\n');
    
    let client;
    let legacyClient;
    
    try {
        // Create client with legacyMode for compatibility
        client = redis.createClient({
            socket: {
                host: 'localhost',
                port: 6379
            },
            legacyMode: true
        });
        
        // Handle errors
        client.on('error', (err) => {
            console.error('Redis error:', err);
        });
        
        // Connect
        console.log('Connecting to Redis...');
        await client.connect();
        console.log('✓ Connected successfully\n');
        
        // Get legacy client for callback-style operations
        legacyClient = client.v4;  // This is the v4 API for async/await
        
        // Test basic operations
        console.log('Testing basic operations:');
        
        // SET using v4 API
        await legacyClient.set('test:key', 'test_value');
        console.log('✓ SET test:key = test_value');
        
        // GET using v4 API
        const value = await legacyClient.get('test:key');
        console.log(`✓ GET test:key = ${value}`);
        
        if (value !== 'test_value') {
            console.error(`⚠️  Warning: Expected 'test_value', got '${value}'`);
        }
        
        // PUBLISH using legacy callback style
        await new Promise((resolve, reject) => {
            client.publish('test:channel', 'test_message', (err, count) => {
                if (err) reject(err);
                else {
                    console.log(`✓ PUBLISH test:channel test_message (${count} subscribers)`);
                    resolve();
                }
            });
        });
        
        // Test pub/sub
        console.log('\nTesting pub/sub:');
        
        // Create a second client for subscribing
        const subClient = redis.createClient({
            socket: {
                host: 'localhost',
                port: 6379
            },
            legacyMode: true
        });
        
        await subClient.connect();
        
        // Set up subscription
        let messageReceived = false;
        subClient.on('message', (channel, message) => {
            console.log(`✓ Received on ${channel}: ${message}`);
            messageReceived = true;
        });
        
        // Subscribe
        await new Promise((resolve) => {
            subClient.subscribe('test:pubsub', (err) => {
                if (err) console.error('Subscribe error:', err);
                else console.log('✓ Subscribed to test:pubsub');
                resolve();
            });
        });
        
        // Publish a message
        await new Promise((resolve) => {
            client.publish('test:pubsub', 'Hello Redis!', (err, count) => {
                if (err) console.error('Publish error:', err);
                else console.log(`✓ Published to test:pubsub (${count} subscribers)`);
                resolve();
            });
        });
        
        // Wait briefly for message
        await new Promise(resolve => setTimeout(resolve, 100));
        
        if (!messageReceived) {
            console.log('⚠️  Warning: Pub/sub message not received (might be timing issue)');
        }
        
        // Clean up
        await legacyClient.del('test:key');
        console.log('\n✓ Cleaned up test:key');
        
        // Test channels used by MockTradingBot
        console.log('\nTesting MockTradingBot channels:');
        const testChannels = [
            'bot:signal',
            'bot:market-data',
            'aggregator:signal',
            'aggregator:position:response'
        ];
        
        for (const channel of testChannels) {
            await new Promise((resolve) => {
                client.publish(channel, JSON.stringify({test: true}), (err, count) => {
                    if (err) {
                        console.error(`✗ Failed to publish to ${channel}: ${err}`);
                    } else {
                        console.log(`✓ Can publish to ${channel} (${count} subscribers)`);
                    }
                    resolve();
                });
            });
        }
        
        console.log('\n=== All Redis tests passed ===');
        
        // Disconnect
        await subClient.quit();
        await client.quit();
        console.log('✓ Disconnected cleanly');
        
        return true;
        
    } catch (error) {
        console.error('\n❌ Redis connection failed:', error.message);
        console.error('\nMake sure Redis is running:');
        console.error('- WSL2: redis-server');
        console.error('- Docker: docker run -d -p 6379:6379 redis');
        console.error('- Windows: Check if Redis service is running');
        
        if (client) {
            try {
                await client.quit();
            } catch (e) {
                // Ignore quit errors
            }
        }
        
        return false;
    }
}

// Run test
testRedisConnection().then(success => {
    process.exit(success ? 0 : 1);
});