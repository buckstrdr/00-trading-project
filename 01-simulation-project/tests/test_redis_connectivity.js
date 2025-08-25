/**
 * Test Redis Connectivity
 * Verifies that we can connect to Redis with redis@4.7.1
 */

const redis = require('redis');

async function testRedisConnection() {
    console.log('=== Redis Connectivity Test ===');
    console.log('Testing with redis@4.7.1 and legacyMode...\n');
    
    let client;
    
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
        
        // Test basic operations
        console.log('Testing basic operations:');
        
        // SET
        await client.set('test:key', 'test_value');
        console.log('✓ SET test:key = test_value');
        
        // GET
        const value = await client.get('test:key');
        console.log(`✓ GET test:key = ${value}`);
        
        // PUBLISH
        await client.publish('test:channel', 'test_message');
        console.log('✓ PUBLISH test:channel test_message');
        
        // Clean up
        await client.del('test:key');
        console.log('✓ DEL test:key\n');
        
        console.log('=== All Redis tests passed ===');
        
        // Disconnect
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