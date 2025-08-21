# Redis Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Core Data Structures](#core-data-structures)
3. [Key Management](#key-management)
4. [Pub/Sub Messaging](#pubsub-messaging)
5. [Transactions](#transactions)
6. [Persistence](#persistence)
7. [Scripting](#scripting)
8. [Client Libraries](#client-libraries)
9. [Best Practices](#best-practices)
10. [Common Patterns](#common-patterns)
11. [Performance Optimization](#performance-optimization)
12. [Security](#security)
13. [Cluster Management](#cluster-management)
14. [Advanced Features](#advanced-features)

## Introduction

Redis is an open-source, in-memory data structure store used as a database, cache, and message broker. It supports various data structures and is often used for high-performance applications, including AI and real-time data processing.

### Key Features
- In-memory data store with optional persistence
- Support for multiple data structures
- Pub/Sub messaging system
- Transactions and atomic operations
- Lua scripting
- Master-slave replication
- Cluster support for horizontal scaling
- High availability with Redis Sentinel

## Core Data Structures

### Strings
The simplest Redis data type, representing sequences of bytes.

#### Basic String Commands
```redis
SET key value                  # Set key to hold the string value
GET key                        # Get the value of key
GETSET key value              # Set key to value and return the old value
MGET key1 key2 ...           # Get the values of all the given keys
MSET key1 value1 key2 value2  # Set multiple keys to multiple values
STRLEN key                    # Get the length of the value stored in a key
```

#### String Manipulation
```redis
APPEND key value              # Append value to key
GETRANGE key start end       # Get substring of the string stored at key
SETRANGE key offset value    # Overwrite part of string at key starting at offset
INCR key                     # Increment the integer value of key by one
INCRBY key increment         # Increment the integer value by given amount
INCRBYFLOAT key increment    # Increment the float value by given amount
DECR key                     # Decrement the integer value by one
DECRBY key decrement        # Decrement the integer value by given amount
```

#### Bit Operations
```redis
GETBIT key offset            # Get the bit value at offset in key
SETBIT key offset value     # Set or clear the bit at offset in key
BITCOUNT key                # Count set bits in a string
BITOP operation destkey key1 key2  # Perform bitwise operations
```

#### Example Usage
```javascript
// Node.js with node-redis
const redis = require('redis');
const client = redis.createClient();

async function stringOperations() {
    await client.connect();
    
    // Basic operations
    await client.set('user:name', 'Alice');
    const name = await client.get('user:name');
    console.log(name); // 'Alice'
    
    // Increment operations
    await client.set('counter', '0');
    await client.incr('counter');
    const count = await client.get('counter');
    console.log(count); // '1'
    
    // Multiple operations
    await client.mSet({
        'user:1:name': 'Bob',
        'user:1:email': 'bob@example.com'
    });
    
    await client.quit();
}
```

### Hashes
Maps between string fields and string values, perfect for representing objects.

#### Hash Commands
```redis
HSET key field value         # Set field in the hash stored at key
HGET key field              # Get value of hash field
HGETALL key                 # Get all fields and values in hash
HMGET key field1 field2     # Get values of multiple hash fields
HMSET key f1 v1 f2 v2       # Set multiple hash fields
HDEL key field1 field2      # Delete one or more hash fields
HEXISTS key field           # Check if hash field exists
HKEYS key                   # Get all field names in hash
HVALS key                   # Get all values in hash
HLEN key                    # Get number of fields in hash
HINCRBY key field increment # Increment hash field integer value
HINCRBYFLOAT key field inc  # Increment hash field float value
HSCAN key cursor            # Incrementally iterate hash fields
HSTRLEN key field           # Get string length of hash field value
```

#### Hash Expiration (Redis 7.4+)
```redis
HEXPIRE key seconds field    # Set expiration for hash field
HEXPIREAT key timestamp field # Set expiration timestamp for field
HPEXPIRE key milliseconds field # Set expiration in milliseconds
HPEXPIREAT key timestamp field # Set expiration timestamp in ms
HEXPIRETIME key field        # Get expiration time for field
HPEXPIRETIME key field       # Get expiration time in ms
HTTL key field              # Get TTL for hash field
HPTTL key field             # Get TTL in milliseconds
HPERSIST key field          # Remove expiration from field
```

#### Example Usage
```javascript
// Storing user information as a hash
async function hashOperations() {
    await client.connect();
    
    // Set user data
    await client.hSet('user:1000', {
        'name': 'Alice Smith',
        'email': 'alice@example.com',
        'age': '30',
        'created': Date.now().toString()
    });
    
    // Get specific field
    const email = await client.hGet('user:1000', 'email');
    console.log(email); // 'alice@example.com'
    
    // Get all fields
    const user = await client.hGetAll('user:1000');
    console.log(user);
    
    // Increment age
    await client.hIncrBy('user:1000', 'age', 1);
    
    // Check field existence
    const hasPhone = await client.hExists('user:1000', 'phone');
    console.log(hasPhone); // false
    
    await client.quit();
}
```

### Lists
Linked lists of string values, commonly used for queues and stacks.

#### List Commands
```redis
LPUSH key value1 value2      # Prepend values to list
RPUSH key value1 value2      # Append values to list
LPOP key                     # Remove and get first element
RPOP key                     # Remove and get last element
LRANGE key start stop        # Get range of elements from list
LLEN key                     # Get list length
LINDEX key index             # Get element at index
LSET key index value         # Set list element at index
LREM key count value         # Remove elements from list
LTRIM key start stop         # Trim list to specified range
LINSERT key BEFORE|AFTER pivot value # Insert element before/after
LMOVE source dest LEFT|RIGHT LEFT|RIGHT # Move element between lists
LMPOP numkeys key1 key2 LEFT|RIGHT [COUNT count] # Pop from multiple lists
LPOS key element             # Find position of element in list
```

#### Blocking List Operations
```redis
BLPOP key1 key2 timeout      # Blocking left pop
BRPOP key1 key2 timeout      # Blocking right pop
BRPOPLPUSH source dest timeout # Blocking pop and push
BLMOVE source dest LEFT|RIGHT LEFT|RIGHT timeout # Blocking move
```

#### Example Usage - Queue Implementation
```javascript
// Message queue implementation
async function queueOperations() {
    await client.connect();
    
    // Producer - add jobs to queue
    await client.lPush('job:queue', JSON.stringify({
        id: 1,
        type: 'email',
        data: { to: 'user@example.com', subject: 'Hello' }
    }));
    
    // Consumer - process jobs (blocking)
    const job = await client.brPop('job:queue', 0);
    if (job) {
        const jobData = JSON.parse(job.element);
        console.log('Processing job:', jobData);
    }
    
    // Get queue length
    const queueLength = await client.lLen('job:queue');
    console.log(`Queue has ${queueLength} jobs`);
    
    await client.quit();
}
```

### Sets
Unordered collections of unique strings.

#### Set Commands
```redis
SADD key member1 member2     # Add members to set
SREM key member1 member2     # Remove members from set
SMEMBERS key                 # Get all members in set
SISMEMBER key member         # Check if value is set member
SMISMEMBER key m1 m2         # Check multiple members
SCARD key                    # Get number of members in set
SPOP key [count]             # Remove and return random members
SRANDMEMBER key [count]      # Get random members from set
SMOVE source dest member     # Move member from one set to another
SSCAN key cursor             # Incrementally iterate set elements
```

#### Set Operations
```redis
SUNION key1 key2             # Union of multiple sets
SUNIONSTORE dest key1 key2   # Store union in destination
SINTER key1 key2             # Intersection of multiple sets
SINTERSTORE dest key1 key2   # Store intersection
SINTERCARD numkeys key1 key2 # Get intersection cardinality
SDIFF key1 key2              # Difference of sets
SDIFFSTORE dest key1 key2    # Store difference
```

#### Example Usage - Tags System
```javascript
// Tag system implementation
async function setOperations() {
    await client.connect();
    
    // Add tags to articles
    await client.sAdd('article:1:tags', ['redis', 'database', 'nosql']);
    await client.sAdd('article:2:tags', ['redis', 'cache', 'performance']);
    
    // Check if article has specific tag
    const hasRedisTag = await client.sIsMember('article:1:tags', 'redis');
    console.log(hasRedisTag); // true
    
    // Find articles with common tags
    const commonTags = await client.sInter(['article:1:tags', 'article:2:tags']);
    console.log(commonTags); // ['redis']
    
    // Get all unique tags across articles
    const allTags = await client.sUnion(['article:1:tags', 'article:2:tags']);
    console.log(allTags); // ['redis', 'database', 'nosql', 'cache', 'performance']
    
    // Count tags
    const tagCount = await client.sCard('article:1:tags');
    console.log(`Article 1 has ${tagCount} tags`);
    
    await client.quit();
}
```

### Sorted Sets
Sets where every member is associated with a score for ordering.

#### Sorted Set Commands
```redis
ZADD key score1 member1 score2 member2  # Add members with scores
ZREM key member1 member2                # Remove members
ZCARD key                               # Get number of members
ZCOUNT key min max                      # Count members in score range
ZSCORE key member                       # Get score of member
ZMSCORE key member1 member2             # Get multiple member scores
ZINCRBY key increment member            # Increment member score
ZRANK key member                        # Get rank of member (ascending)
ZREVRANK key member                     # Get rank (descending)
```

#### Sorted Set Range Operations
```redis
ZRANGE key start stop [WITHSCORES]      # Get range by rank
ZREVRANGE key start stop [WITHSCORES]   # Get reverse range by rank
ZRANGEBYSCORE key min max [WITHSCORES]  # Get range by score
ZREVRANGEBYSCORE key max min            # Get reverse range by score
ZRANGEBYLEX key min max                 # Get range by lex
ZRANGESTORE dest key min max            # Store range in destination
ZLEXCOUNT key min max                   # Count members in lex range
```

#### Sorted Set Pop Operations
```redis
ZPOPMIN key [count]                     # Remove members with lowest scores
ZPOPMAX key [count]                     # Remove members with highest scores
ZMPOP numkeys key1 key2 MIN|MAX [COUNT] # Pop from multiple sorted sets
ZRANDMEMBER key [count]                 # Get random members
```

#### Sorted Set Set Operations
```redis
ZUNION numkeys key1 key2                # Union of sorted sets
ZUNIONSTORE dest numkeys key1 key2      # Store union
ZINTER numkeys key1 key2                # Intersection
ZINTERSTORE dest numkeys key1 key2      # Store intersection
ZINTERCARD numkeys key1 key2            # Get intersection cardinality
ZDIFF numkeys key1 key2                 # Difference
ZDIFFSTORE dest numkeys key1 key2       # Store difference
```

#### Example Usage - Leaderboard
```javascript
// Gaming leaderboard implementation
async function leaderboardOperations() {
    await client.connect();
    
    // Add player scores
    await client.zAdd('leaderboard', [
        { score: 100, value: 'player1' },
        { score: 85, value: 'player2' },
        { score: 95, value: 'player3' },
        { score: 110, value: 'player4' }
    ]);
    
    // Get top 3 players
    const topPlayers = await client.zRevRange('leaderboard', 0, 2, {
        WITHSCORES: true
    });
    console.log('Top players:', topPlayers);
    
    // Get player rank
    const rank = await client.zRevRank('leaderboard', 'player2');
    console.log(`Player2 rank: ${rank + 1}`); // Add 1 for 1-based ranking
    
    // Increment player score
    await client.zIncrBy('leaderboard', 10, 'player2');
    
    // Get players with scores between 90 and 100
    const midRange = await client.zRangeByScore('leaderboard', 90, 100);
    console.log('Players with scores 90-100:', midRange);
    
    await client.quit();
}
```

### Streams
Append-only data structures for building event sourcing and messaging systems.

#### Stream Commands
```redis
XADD key ID field value                 # Append message to stream
XLEN key                                # Get stream length
XRANGE key start end                    # Get range of messages
XREVRANGE key end start                 # Get reverse range
XREAD [COUNT count] STREAMS key ID      # Read messages from streams
XDEL key ID1 ID2                        # Delete messages
XTRIM key MAXLEN count                  # Trim stream to max length
XSETID key ID                          # Set stream last delivered ID
```

#### Stream Consumer Groups
```redis
XGROUP CREATE key group ID              # Create consumer group
XREADGROUP GROUP group consumer STREAMS key ID # Read as consumer
XACK key group ID1 ID2                  # Acknowledge messages
XPENDING key group                      # Get pending messages info
XINFO STREAM key                        # Get stream info
XINFO GROUPS key                        # Get consumer groups info
XINFO HELP                              # Get help on XINFO commands
```

#### Example Usage - Event Stream
```javascript
// Event streaming implementation
async function streamOperations() {
    await client.connect();
    
    // Add events to stream
    const messageId = await client.xAdd('events:stream', '*', {
        type: 'user_login',
        user_id: '1000',
        timestamp: Date.now().toString()
    });
    console.log('Added message with ID:', messageId);
    
    // Read events from stream
    const messages = await client.xRead([
        { key: 'events:stream', id: '0' }
    ], { COUNT: 10 });
    
    if (messages) {
        for (const stream of messages) {
            for (const message of stream.messages) {
                console.log('Event:', message.id, message.message);
            }
        }
    }
    
    // Consumer group for processing
    await client.xGroupCreate('events:stream', 'processors', '0');
    
    // Read as consumer
    const groupMessages = await client.xReadGroup(
        'processors',
        'consumer1',
        [{ key: 'events:stream', id: '>' }],
        { COUNT: 1 }
    );
    
    // Acknowledge processed messages
    if (groupMessages && groupMessages[0].messages.length > 0) {
        const msgId = groupMessages[0].messages[0].id;
        await client.xAck('events:stream', 'processors', msgId);
    }
    
    await client.quit();
}
```

### HyperLogLog
Probabilistic data structure for counting unique items.

```redis
PFADD key element1 element2             # Add elements
PFCOUNT key1 key2                       # Count unique elements
PFMERGE destkey sourcekey1 sourcekey2   # Merge HyperLogLogs
```

#### Example Usage - Unique Visitors
```javascript
// Count unique visitors
async function hyperLogLogOperations() {
    await client.connect();
    
    // Track unique visitors
    await client.pfAdd('visitors:2024-01-01', ['user1', 'user2', 'user3']);
    await client.pfAdd('visitors:2024-01-01', ['user2', 'user4']); // user2 duplicate
    
    // Count unique visitors
    const uniqueCount = await client.pfCount('visitors:2024-01-01');
    console.log(`Unique visitors: ${uniqueCount}`); // 4
    
    // Merge multiple days
    await client.pfAdd('visitors:2024-01-02', ['user3', 'user5', 'user6']);
    await client.pfMerge('visitors:january', [
        'visitors:2024-01-01',
        'visitors:2024-01-02'
    ]);
    
    const monthlyUnique = await client.pfCount('visitors:january');
    console.log(`Monthly unique visitors: ${monthlyUnique}`);
    
    await client.quit();
}
```

## Key Management

### Basic Key Operations
```redis
DEL key1 key2                           # Delete keys
UNLINK key1 key2                        # Non-blocking delete
EXISTS key1 key2                        # Check if keys exist
TYPE key                                # Get key data type
RENAME key newkey                       # Rename key
RENAMENX key newkey                     # Rename if new key doesn't exist
COPY source destination                 # Copy key
MOVE key db                             # Move key to another database
```

### Key Expiration
```redis
EXPIRE key seconds                      # Set expiration in seconds
EXPIREAT key timestamp                  # Set expiration at Unix timestamp
PEXPIRE key milliseconds                # Set expiration in milliseconds
PEXPIREAT key timestamp                 # Set expiration at Unix timestamp (ms)
TTL key                                 # Get time to live in seconds
PTTL key                               # Get time to live in milliseconds
PERSIST key                            # Remove expiration
EXPIRETIME key                         # Get expiration Unix timestamp
PEXPIRETIME key                        # Get expiration Unix timestamp (ms)
```

### Key Scanning
```redis
KEYS pattern                            # Find all keys matching pattern
SCAN cursor [MATCH pattern] [COUNT count] # Incrementally iterate keys
RANDOMKEY                               # Return random key
TOUCH key1 key2                         # Update last access time
```

#### Example Usage - Key Management
```javascript
// Key management operations
async function keyManagement() {
    await client.connect();
    
    // Set key with expiration
    await client.set('session:abc123', 'user_data', {
        EX: 3600 // Expire in 1 hour
    });
    
    // Check TTL
    const ttl = await client.ttl('session:abc123');
    console.log(`Session expires in ${ttl} seconds`);
    
    // Check key existence
    const exists = await client.exists('session:abc123');
    console.log(`Session exists: ${exists}`);
    
    // Scan for keys (production-safe alternative to KEYS)
    const scanIterator = client.scanIterator({
        MATCH: 'session:*',
        COUNT: 100
    });
    
    for await (const key of scanIterator) {
        console.log('Found session:', key);
    }
    
    // Rename key
    await client.rename('session:abc123', 'session:old:abc123');
    
    // Delete multiple keys
    await client.del(['key1', 'key2', 'key3']);
    
    await client.quit();
}
```

## Pub/Sub Messaging

### Publishing and Subscribing
```redis
PUBLISH channel message                 # Publish message to channel
SUBSCRIBE channel1 channel2             # Subscribe to channels
UNSUBSCRIBE [channel1 channel2]         # Unsubscribe from channels
PSUBSCRIBE pattern1 pattern2            # Subscribe to patterns
PUNSUBSCRIBE [pattern1 pattern2]        # Unsubscribe from patterns
```

### Sharded Pub/Sub (Redis 7.0+)
```redis
SPUBLISH channel message                # Publish to sharded channel
SSUBSCRIBE channel1 channel2            # Subscribe to sharded channels
SUNSUBSCRIBE [channel1 channel2]        # Unsubscribe from sharded channels
```

### Pub/Sub Introspection
```redis
PUBSUB CHANNELS [pattern]               # List active channels
PUBSUB NUMSUB channel1 channel2         # Get subscriber count
PUBSUB NUMPAT                          # Get pattern subscriber count
PUBSUB SHARDCHANNELS [pattern]          # List sharded channels
PUBSUB SHARDNUMSUB channel1 channel2    # Get sharded subscriber count
```

#### Example Usage - Real-time Notifications
```javascript
// Publisher
async function publisher() {
    const pubClient = redis.createClient();
    await pubClient.connect();
    
    // Publish notification
    await pubClient.publish('notifications', JSON.stringify({
        type: 'new_message',
        user_id: '1000',
        message: 'You have a new message!'
    }));
    
    // Check subscriber count
    const subscribers = await pubClient.pubSubNumSub('notifications');
    console.log('Subscribers:', subscribers);
    
    await pubClient.quit();
}

// Subscriber
async function subscriber() {
    const subClient = redis.createClient();
    await subClient.connect();
    
    // Subscribe to channel
    await subClient.subscribe('notifications', (message) => {
        const notification = JSON.parse(message);
        console.log('Received notification:', notification);
    });
    
    // Pattern subscription
    await subClient.pSubscribe('user:*', (message, channel) => {
        console.log(`Message on ${channel}:`, message);
    });
}
```

### Pattern Matching Subscriptions
```javascript
// Subscribe to patterns
async function patternSubscription() {
    const subscriber = redis.createClient();
    await subscriber.connect();
    
    // Subscribe to all news channels
    await subscriber.pSubscribe('news.*', (message, channel) => {
        console.log(`News on ${channel}:`, message);
    });
    
    // Publisher can publish to specific channels
    const publisher = redis.createClient();
    await publisher.connect();
    
    await publisher.publish('news.sports', 'Sports update');
    await publisher.publish('news.tech', 'Tech news');
    
    await publisher.quit();
}
```

### Allowed Commands in RESP2 Subscribed Mode
When a RESP2 client is in subscribed mode, only these commands are allowed:
- PING
- PSUBSCRIBE
- PUNSUBSCRIBE
- QUIT
- RESET
- SSUBSCRIBE
- SUBSCRIBE
- SUNSUBSCRIBE
- UNSUBSCRIBE

## Transactions

Redis transactions allow you to execute multiple commands atomically.

```redis
MULTI                                   # Start transaction
EXEC                                    # Execute transaction
DISCARD                                # Discard transaction
WATCH key1 key2                         # Watch keys for changes
UNWATCH                                # Unwatch all keys
```

### Basic Transaction Example
```javascript
// Basic transaction
async function basicTransaction() {
    await client.connect();
    
    // Start transaction
    const multi = client.multi();
    
    // Queue commands
    multi.set('key1', 'value1');
    multi.set('key2', 'value2');
    multi.incr('counter');
    multi.hSet('user:1', 'name', 'Alice');
    
    // Execute transaction
    const results = await multi.exec();
    console.log('Transaction results:', results);
    
    await client.quit();
}
```

### Optimistic Locking with WATCH
```javascript
// Atomic increment with retry logic
async function atomicIncrement() {
    await client.connect();
    
    let retries = 5;
    while (retries > 0) {
        try {
            // Watch the key
            await client.watch('counter');
            
            // Get current value
            const value = await client.get('counter');
            const newValue = parseInt(value || '0') + 1;
            
            // Start transaction
            const multi = client.multi();
            multi.set('counter', newValue);
            
            // Execute transaction
            const result = await multi.exec();
            
            if (result === null) {
                // Transaction aborted due to watched key change
                console.log('Transaction aborted, retrying...');
                retries--;
                continue;
            }
            
            console.log('Counter incremented to:', newValue);
            break;
            
        } catch (error) {
            console.error('Transaction error:', error);
            retries--;
        }
    }
    
    await client.quit();
}
```

### Complex Transaction Example
```javascript
// Transfer funds between accounts
async function transferFunds(fromAccount, toAccount, amount) {
    await client.connect();
    
    try {
        // Watch both accounts
        await client.watch([`account:${fromAccount}`, `account:${toAccount}`]);
        
        // Get current balances
        const fromBalance = parseFloat(await client.get(`account:${fromAccount}`) || '0');
        const toBalance = parseFloat(await client.get(`account:${toAccount}`) || '0');
        
        // Check sufficient funds
        if (fromBalance < amount) {
            throw new Error('Insufficient funds');
        }
        
        // Prepare transaction
        const multi = client.multi();
        multi.set(`account:${fromAccount}`, fromBalance - amount);
        multi.set(`account:${toAccount}`, toBalance + amount);
        multi.lPush('transactions', JSON.stringify({
            from: fromAccount,
            to: toAccount,
            amount: amount,
            timestamp: Date.now()
        }));
        
        // Execute transaction
        const result = await multi.exec();
        
        if (result === null) {
            throw new Error('Transaction aborted - accounts were modified');
        }
        
        console.log('Transfer successful');
        
    } catch (error) {
        console.error('Transfer failed:', error);
    } finally {
        await client.quit();
    }
}
```

## Persistence

Redis offers two persistence mechanisms:

### RDB (Redis Database)
Point-in-time snapshots of your dataset.

```redis
SAVE                                   # Synchronous save
BGSAVE                                # Background save
LASTSAVE                              # Get last save timestamp
```

### AOF (Append Only File)
Logs every write operation received by the server.

```redis
BGREWRITEAOF                          # Background AOF rewrite
```

### Persistence Configuration
```javascript
// Configure persistence programmatically
async function configurePersistence() {
    await client.connect();
    
    // Configure RDB snapshots
    await client.configSet('save', '900 1 300 10 60 10000');
    // Save after 900 sec if at least 1 key changed
    // Save after 300 sec if at least 10 keys changed
    // Save after 60 sec if at least 10000 keys changed
    
    // Configure AOF
    await client.configSet('appendonly', 'yes');
    await client.configSet('appendfsync', 'everysec');
    
    // Check configuration
    const config = await client.configGet('save');
    console.log('Save configuration:', config);
    
    await client.quit();
}
```

### WAITAOF Command
Ensures data persistence to AOF:

```javascript
// Ensure persistence
async function ensurePersistence() {
    await client.connect();
    
    // Write critical data
    await client.set('critical:data', 'important_value');
    
    // Wait for AOF fsync (1 local, 5 second timeout)
    const synced = await client.sendCommand(['WAITAOF', '1', '5000']);
    console.log(`Data synced to ${synced} instances`);
    
    await client.quit();
}
```

## Scripting

### Lua Scripting
```redis
EVAL script numkeys key1 arg1           # Execute Lua script
EVALSHA sha1 numkeys key1 arg1          # Execute script by SHA1
SCRIPT LOAD script                      # Load script into cache
SCRIPT EXISTS sha1 sha2                 # Check if scripts exist
SCRIPT FLUSH                           # Remove all scripts
SCRIPT KILL                            # Kill running script
SCRIPT DEBUG YES|SYNC|NO                # Set script debugging mode
```

#### Lua Script Example
```javascript
// Atomic operations with Lua
async function luaScripting() {
    await client.connect();
    
    // Define a Lua script for atomic increment with max value
    const script = `
        local current = redis.call('GET', KEYS[1])
        if not current then
            current = 0
        else
            current = tonumber(current)
        end
        
        local increment = tonumber(ARGV[1])
        local max = tonumber(ARGV[2])
        
        if current + increment > max then
            return redis.error_reply("Would exceed maximum")
        end
        
        local new = current + increment
        redis.call('SET', KEYS[1], new)
        return new
    `;
    
    // Load script
    const sha = await client.scriptLoad(script);
    console.log('Script SHA:', sha);
    
    // Execute script
    try {
        const result = await client.evalSha(
            sha,
            {
                keys: ['counter'],
                arguments: ['10', '100'] // increment by 10, max 100
            }
        );
        console.log('New counter value:', result);
    } catch (error) {
        console.error('Script error:', error);
    }
    
    await client.quit();
}
```

### Functions (Redis 7.0+)
```redis
FUNCTION LOAD code                      # Load function library
FCALL function numkeys key1 arg1        # Call function
FCALL_RO function numkeys key1 arg1     # Call read-only function
```

## Client Libraries

### Node.js (node-redis)
```javascript
const redis = require('redis');

async function nodeRedisExample() {
    // Create client
    const client = redis.createClient({
        socket: {
            host: 'localhost',
            port: 6379
        },
        password: 'your_password' // if needed
    });
    
    // Error handling
    client.on('error', (err) => console.log('Redis Client Error', err));
    
    // Connect
    await client.connect();
    
    // Basic operations
    await client.set('key', 'value');
    const value = await client.get('key');
    
    // Pipelining
    const pipeline = client.pipeline();
    pipeline.set('key1', 'value1');
    pipeline.set('key2', 'value2');
    pipeline.get('key1');
    const results = await pipeline.exec();
    
    // Clean disconnect
    await client.quit();
}
```

### Python (redis-py)
```python
import redis

# Create connection
r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Basic operations
r.set('key', 'value')
value = r.get('key')
print(value)

# Pipelining
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.get('key1')
results = pipe.execute()

# Transaction
pipe = r.pipeline(transaction=True)
pipe.multi()
pipe.set('user:1:name', 'Alice')
pipe.set('user:1:email', 'alice@example.com')
pipe.get('user:1:name')
transaction_results = pipe.execute()
```

### Connection Management
```javascript
// Connection pool configuration
const client = redis.createClient({
    socket: {
        host: 'localhost',
        port: 6379,
        reconnectStrategy: (retries) => {
            if (retries > 10) {
                return new Error('Too many reconnection attempts');
            }
            return Math.min(retries * 100, 3000);
        }
    },
    // Connection pool settings
    isolationPoolOptions: {
        min: 0,
        max: 10
    }
});
```

## Best Practices

### Key Naming Conventions
- Use colons for namespacing: `user:1000:profile`
- Be consistent with naming patterns
- Keep keys short but descriptive
- Consider TTL requirements in naming

```javascript
// Good key naming examples
const keyPatterns = {
    user: (id) => `user:${id}`,
    userEmail: (id) => `user:${id}:email`,
    session: (token) => `session:${token}`,
    cache: (resource) => `cache:${resource}`,
    temp: (id) => `temp:${id}`,
    queue: (name) => `queue:${name}`,
    lock: (resource) => `lock:${resource}`
};
```

### Memory Optimization
- Use appropriate data structures
- Set expiration times when possible
- Use compression for large values
- Monitor memory usage regularly
- Consider using Redis Modules for specialized use cases

```javascript
// Memory optimization techniques
async function memoryOptimization() {
    await client.connect();
    
    // Use hashes for small objects (more memory efficient)
    // Instead of: user:1:name, user:1:email as separate keys
    // Use: user:1 as hash with name, email fields
    
    // Set expiration for cache
    await client.set('cache:data', JSON.stringify(data), {
        EX: 3600 // 1 hour expiration
    });
    
    // Use appropriate data types
    // For counters, use INCR instead of GET/SET
    await client.incr('page:views');
    
    // Compress large values before storing
    const zlib = require('zlib');
    const compressed = zlib.gzipSync(JSON.stringify(largeObject));
    await client.set('compressed:data', compressed);
    
    // Monitor memory usage
    const info = await client.info('memory');
    console.log('Memory info:', info);
    
    await client.quit();
}
```

### Performance Tips
- Use pipelining for batch operations
- Avoid large keys and values
- Use SCAN instead of KEYS in production
- Monitor slow queries with SLOWLOG
- Use read replicas for scaling reads

```javascript
// Performance optimization
async function performanceOptimization() {
    await client.connect();
    
    // Use pipelining for batch operations
    const pipeline = client.pipeline();
    for (let i = 0; i < 1000; i++) {
        pipeline.set(`key:${i}`, `value:${i}`);
    }
    await pipeline.exec();
    
    // Use SCAN instead of KEYS
    const scanIterator = client.scanIterator({
        MATCH: 'user:*',
        COUNT: 100
    });
    
    for await (const key of scanIterator) {
        // Process key
    }
    
    // Monitor slow queries
    const slowLog = await client.slowlogGet(10);
    console.log('Slow queries:', slowLog);
    
    await client.quit();
}
```

### Security
- Always use authentication (requirepass)
- Use ACLs for fine-grained access control
- Enable TLS for encrypted connections
- Bind to specific interfaces, not 0.0.0.0
- Regular security updates

```javascript
// Security configuration
const secureClient = redis.createClient({
    socket: {
        host: 'localhost',
        port: 6379,
        tls: true,
        cert: fs.readFileSync('client-cert.pem'),
        key: fs.readFileSync('client-key.pem'),
        ca: [fs.readFileSync('ca-cert.pem')]
    },
    username: 'myuser',
    password: 'mypassword'
});
```

## Common Patterns

### Caching
```javascript
// Cache-aside pattern
async function cacheAside(key, fetchFunction, ttl = 3600) {
    await client.connect();
    
    // Try to get from cache
    let data = await client.get(key);
    
    if (data) {
        console.log('Cache hit');
        return JSON.parse(data);
    }
    
    console.log('Cache miss');
    // Fetch from source
    data = await fetchFunction();
    
    // Store in cache
    await client.set(key, JSON.stringify(data), {
        EX: ttl
    });
    
    return data;
}

// Usage
const userData = await cacheAside(
    'user:1000',
    async () => await fetchUserFromDB(1000),
    3600
);
```

### Rate Limiting
```javascript
// Token bucket rate limiting
async function rateLimiter(userId, limit = 10, window = 60) {
    await client.connect();
    
    const key = `rate:${userId}`;
    const current = await client.incr(key);
    
    if (current === 1) {
        // First request in window
        await client.expire(key, window);
    }
    
    if (current > limit) {
        // Rate limit exceeded
        const ttl = await client.ttl(key);
        return {
            allowed: false,
            retryAfter: ttl
        };
    }
    
    return {
        allowed: true,
        remaining: limit - current
    };
}
```

### Session Storage
```javascript
// Session management
class SessionStore {
    constructor(client, ttl = 1800) {
        this.client = client;
        this.ttl = ttl;
    }
    
    async create(sessionId, data) {
        const key = `session:${sessionId}`;
        await this.client.hSet(key, data);
        await this.client.expire(key, this.ttl);
        return sessionId;
    }
    
    async get(sessionId) {
        const key = `session:${sessionId}`;
        const data = await this.client.hGetAll(key);
        
        if (Object.keys(data).length === 0) {
            return null;
        }
        
        // Refresh TTL on access
        await this.client.expire(key, this.ttl);
        return data;
    }
    
    async destroy(sessionId) {
        const key = `session:${sessionId}`;
        await this.client.del(key);
    }
    
    async update(sessionId, data) {
        const key = `session:${sessionId}`;
        await this.client.hSet(key, data);
        await this.client.expire(key, this.ttl);
    }
}

// Usage
const sessions = new SessionStore(client);
const sessionId = await sessions.create('abc123', {
    userId: '1000',
    username: 'alice',
    loginTime: Date.now()
});
```

### Message Queue
```javascript
// Reliable queue with processing
class ReliableQueue {
    constructor(client, queueName) {
        this.client = client;
        this.queueName = queueName;
        this.processingName = `${queueName}:processing`;
    }
    
    async push(message) {
        await this.client.lPush(this.queueName, JSON.stringify(message));
    }
    
    async pop(timeout = 0) {
        // Move from queue to processing list atomically
        const result = await this.client.brPopLPush(
            this.queueName,
            this.processingName,
            timeout
        );
        
        if (result) {
            return JSON.parse(result);
        }
        return null;
    }
    
    async complete(message) {
        // Remove from processing list
        await this.client.lRem(
            this.processingName,
            1,
            JSON.stringify(message)
        );
    }
    
    async retry(message) {
        // Move back to main queue
        await this.complete(message);
        await this.push(message);
    }
    
    async getStats() {
        const pending = await this.client.lLen(this.queueName);
        const processing = await this.client.lLen(this.processingName);
        return { pending, processing };
    }
}
```

### Distributed Locks
```javascript
// Redlock-style distributed lock
class DistributedLock {
    constructor(client, ttl = 30000) {
        this.client = client;
        this.ttl = ttl;
    }
    
    async acquire(resource, timeout = 5000) {
        const key = `lock:${resource}`;
        const value = crypto.randomUUID();
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const result = await this.client.set(key, value, {
                PX: this.ttl,
                NX: true
            });
            
            if (result === 'OK') {
                return {
                    resource,
                    value,
                    release: () => this.release(resource, value)
                };
            }
            
            // Wait before retry
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        throw new Error('Failed to acquire lock');
    }
    
    async release(resource, value) {
        const key = `lock:${resource}`;
        
        // Use Lua script for atomic check and delete
        const script = `
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
        `;
        
        return await this.client.eval(script, {
            keys: [key],
            arguments: [value]
        });
    }
}

// Usage
const locks = new DistributedLock(client);
const lock = await locks.acquire('resource:1');
try {
    // Critical section
    await doWork();
} finally {
    await lock.release();
}
```

## Performance Optimization

### Pipelining
Reduce network round trips by batching commands:

```javascript
// Without pipelining - multiple round trips
async function withoutPipelining() {
    const start = Date.now();
    for (let i = 0; i < 1000; i++) {
        await client.set(`key:${i}`, `value:${i}`);
    }
    console.log(`Without pipelining: ${Date.now() - start}ms`);
}

// With pipelining - single round trip
async function withPipelining() {
    const start = Date.now();
    const pipeline = client.pipeline();
    for (let i = 0; i < 1000; i++) {
        pipeline.set(`key:${i}`, `value:${i}`);
    }
    await pipeline.exec();
    console.log(`With pipelining: ${Date.now() - start}ms`);
}
```

### Connection Pooling
```javascript
// Connection pool for high concurrency
const { createPool } = require('generic-pool');

const redisPool = createPool({
    create: async () => {
        const client = redis.createClient();
        await client.connect();
        return client;
    },
    destroy: async (client) => {
        await client.quit();
    },
    validate: async (client) => {
        try {
            await client.ping();
            return true;
        } catch {
            return false;
        }
    }
}, {
    min: 2,
    max: 10,
    testOnBorrow: true
});

// Use pooled connection
async function usePooledConnection() {
    const client = await redisPool.acquire();
    try {
        await client.set('key', 'value');
        const value = await client.get('key');
        return value;
    } finally {
        await redisPool.release(client);
    }
}
```

### Memory Analysis
```javascript
// Analyze memory usage
async function memoryAnalysis() {
    await client.connect();
    
    // Get memory stats
    const memoryStats = await client.memoryStats();
    console.log('Memory statistics:', memoryStats);
    
    // Check memory usage of specific key
    const keyMemory = await client.memoryUsage('large:key');
    console.log(`Key memory usage: ${keyMemory} bytes`);
    
    // Memory doctor recommendations
    const doctor = await client.memoryDoctor();
    console.log('Memory doctor:', doctor);
    
    await client.quit();
}
```

## Security

### ACL Configuration
```javascript
// Configure ACLs
async function configureACL() {
    await client.connect();
    
    // Create new user with limited permissions
    await client.aclSetUser('app_user', [
        'on',                    // Enable user
        '>password123',          // Set password
        '~cache:*',             // Allow keys matching pattern
        '+get',                 // Allow GET command
        '+set',                 // Allow SET command
        '+del',                 // Allow DEL command
        '-@dangerous'           // Deny dangerous commands
    ]);
    
    // List users
    const users = await client.aclList();
    console.log('ACL Users:', users);
    
    // Get user details
    const userInfo = await client.aclGetUser('app_user');
    console.log('User info:', userInfo);
    
    await client.quit();
}
```

### TLS Configuration
```javascript
const fs = require('fs');

// Create TLS-enabled client
const tlsClient = redis.createClient({
    socket: {
        host: 'redis.example.com',
        port: 6379,
        tls: true,
        rejectUnauthorized: true,
        cert: fs.readFileSync('./client-cert.pem'),
        key: fs.readFileSync('./client-key.pem'),
        ca: [fs.readFileSync('./ca-cert.pem')]
    }
});
```

## Cluster Management

### Cluster Commands
```redis
CLUSTER NODES                         # Get cluster nodes information
CLUSTER INFO                          # Get cluster information
CLUSTER MEET ip port                  # Add node to cluster
CLUSTER REPLICATE node-id             # Configure node as replica
CLUSTER FAILOVER                     # Force failover
CLUSTER SLOTS                        # Get slot mapping
CLUSTER KEYSLOT key                  # Get key hash slot
```

### Cluster Client Configuration
```javascript
// Connect to Redis Cluster
const clusterClient = redis.createCluster({
    rootNodes: [
        {
            socket: {
                host: 'node1.example.com',
                port: 6379
            }
        },
        {
            socket: {
                host: 'node2.example.com',
                port: 6379
            }
        },
        {
            socket: {
                host: 'node3.example.com',
                port: 6379
            }
        }
    ],
    defaults: {
        socket: {
            reconnectStrategy: (retries) => Math.min(retries * 100, 3000)
        }
    }
});

// Use cluster client
await clusterClient.connect();
await clusterClient.set('key', 'value');
const value = await clusterClient.get('key');
await clusterClient.quit();
```

## Advanced Features

### JSON Support (RedisJSON Module)
```javascript
// Working with JSON documents
async function jsonOperations() {
    await client.connect();
    
    // Set JSON document
    await client.json.set('user:1001', '$', {
        name: 'Alice',
        age: 30,
        email: 'alice@example.com',
        address: {
            city: 'New York',
            country: 'USA'
        },
        hobbies: ['reading', 'hiking']
    });
    
    // Get entire document
    const user = await client.json.get('user:1001');
    console.log('User:', user);
    
    // Get specific path
    const city = await client.json.get('user:1001', {
        path: '$.address.city'
    });
    console.log('City:', city);
    
    // Update nested value
    await client.json.set('user:1001', '$.age', 31);
    
    // Append to array
    await client.json.arrAppend('user:1001', '$.hobbies', 'swimming');
    
    // Increment number
    await client.json.numIncrBy('user:1001', '$.age', 1);
    
    await client.quit();
}
```

### Time Series (RedisTimeSeries Module)
```javascript
// Time series data
async function timeSeriesOperations() {
    await client.connect();
    
    // Create time series
    await client.ts.create('temperature:sensor1', {
        RETENTION: 86400000, // 24 hours in milliseconds
        LABELS: {
            sensor: 'sensor1',
            location: 'room1'
        }
    });
    
    // Add samples
    const now = Date.now();
    await client.ts.add('temperature:sensor1', now, 22.5);
    await client.ts.add('temperature:sensor1', now + 60000, 22.7);
    await client.ts.add('temperature:sensor1', now + 120000, 22.6);
    
    // Get latest value
    const latest = await client.ts.get('temperature:sensor1');
    console.log('Latest temperature:', latest);
    
    // Get range
    const range = await client.ts.range(
        'temperature:sensor1',
        now - 3600000,
        now + 3600000
    );
    console.log('Temperature range:', range);
    
    // Create aggregation rule
    await client.ts.create('temperature:sensor1:avg_1h');
    await client.ts.createRule(
        'temperature:sensor1',
        'temperature:sensor1:avg_1h',
        'AVG',
        3600000 // 1 hour buckets
    );
    
    await client.quit();
}
```

### Search and Query (RediSearch Module)
```javascript
// Full-text search
async function searchOperations() {
    await client.connect();
    
    // Create index
    await client.ft.create('idx:products', {
        '$.name': {
            type: 'TEXT',
            AS: 'name'
        },
        '$.description': {
            type: 'TEXT',
            AS: 'description'
        },
        '$.price': {
            type: 'NUMERIC',
            AS: 'price'
        },
        '$.category': {
            type: 'TAG',
            AS: 'category'
        }
    }, {
        ON: 'JSON',
        PREFIX: 'product:'
    });
    
    // Add documents
    await client.json.set('product:1', '$', {
        name: 'Laptop',
        description: 'High-performance laptop for professionals',
        price: 1299.99,
        category: 'electronics'
    });
    
    await client.json.set('product:2', '$', {
        name: 'Smartphone',
        description: 'Latest smartphone with advanced features',
        price: 899.99,
        category: 'electronics'
    });
    
    // Search
    const results = await client.ft.search('idx:products', 'laptop', {
        LIMIT: {
            from: 0,
            size: 10
        }
    });
    console.log('Search results:', results);
    
    // Search with filters
    const filtered = await client.ft.search(
        'idx:products',
        '@category:{electronics} @price:[500 1500]'
    );
    console.log('Filtered results:', filtered);
    
    await client.quit();
}
```

## Server Management

### Configuration
```javascript
// Server configuration
async function serverConfiguration() {
    await client.connect();
    
    // Get configuration
    const maxMemory = await client.configGet('maxmemory');
    console.log('Max memory:', maxMemory);
    
    // Set configuration
    await client.configSet('maxmemory-policy', 'allkeys-lru');
    
    // Reset statistics
    await client.configResetStat();
    
    // Rewrite config file
    await client.configRewrite();
    
    await client.quit();
}
```

### Information and Monitoring
```javascript
// Server monitoring
async function serverMonitoring() {
    await client.connect();
    
    // Get server info
    const info = await client.info();
    console.log('Server info:', info);
    
    // Get specific section
    const memoryInfo = await client.info('memory');
    console.log('Memory info:', memoryInfo);
    
    // Monitor commands in real-time
    // Note: MONITOR blocks the client
    // Use a separate client for monitoring
    const monitorClient = redis.createClient();
    await monitorClient.connect();
    
    monitorClient.monitor((time, args, source, database) => {
        console.log(`${time}: ${args} from ${source} on db${database}`);
    });
    
    // Check slow log
    const slowLog = await client.slowlogGet(10);
    console.log('Recent slow queries:', slowLog);
    
    // Reset slow log
    await client.slowlogReset();
    
    await client.quit();
}
```

### Replication
```javascript
// Replication management
async function replicationManagement() {
    await client.connect();
    
    // Make server a replica
    await client.replicaOf('master.example.com', 6379);
    
    // Get replication role
    const role = await client.role();
    console.log('Replication role:', role);
    
    // Wait for replication
    const replicated = await client.wait(2, 1000); // 2 replicas, 1 second timeout
    console.log(`Replicated to ${replicated} replicas`);
    
    // Promote to master
    await client.replicaOf('NO', 'ONE');
    
    await client.quit();
}
```

## Debugging and Troubleshooting

### Debug Commands
```javascript
// Debugging utilities
async function debugging() {
    await client.connect();
    
    // Object encoding
    await client.set('mykey', '10');
    const encoding = await client.objectEncoding('mykey');
    console.log('Object encoding:', encoding); // 'int'
    
    // Object idle time
    const idleTime = await client.objectIdletime('mykey');
    console.log('Idle time:', idleTime);
    
    // Object frequency (LFU)
    const frequency = await client.objectFreq('mykey');
    console.log('Access frequency:', frequency);
    
    // Debug object
    const debug = await client.debugObject('mykey');
    console.log('Debug info:', debug);
    
    await client.quit();
}
```

### Latency Monitoring
```javascript
// Latency analysis
async function latencyMonitoring() {
    await client.connect();
    
    // Enable latency monitoring
    await client.configSet('latency-monitor-threshold', '100');
    
    // Get latency stats
    const latencyStats = await client.latencyLatest();
    console.log('Latency stats:', latencyStats);
    
    // Get latency history
    const history = await client.latencyHistory('command');
    console.log('Command latency history:', history);
    
    // Latency doctor
    const doctor = await client.latencyDoctor();
    console.log('Latency doctor:', doctor);
    
    // Reset latency data
    await client.latencyReset();
    
    await client.quit();
}
```

## Conclusion

Redis provides a rich set of data structures and commands for building high-performance applications. Understanding these core concepts and commands is essential for effectively using Redis as a database, cache, or message broker. Always consider your specific use case when choosing data structures and patterns to ensure optimal performance and resource utilization.

### Additional Resources
- Official Redis Documentation: https://redis.io/docs
- Redis Commands Reference: https://redis.io/commands
- Redis Best Practices: https://redis.io/docs/manual/patterns/
- Redis University: https://university.redis.com
- Community Support: https://redis.io/community

### Key Takeaways
1. Choose the right data structure for your use case
2. Use pipelining and transactions for atomic operations
3. Implement proper error handling and retry logic
4. Monitor performance and memory usage
5. Secure your Redis deployment with ACLs and TLS
6. Use persistence mechanisms appropriate for your data
7. Scale horizontally with Redis Cluster when needed
8. Leverage Redis modules for specialized functionality