# Socket.IO Complete Documentation

## Table of Contents
1. [Getting Started](#getting-started)
2. [Server API](#server-api)
3. [Client API](#client-api)
4. [Events](#events)
5. [Namespaces](#namespaces)
6. [Rooms](#rooms)
7. [Broadcasting](#broadcasting)
8. [Middleware](#middleware)
9. [Error Handling](#error-handling)
10. [Authentication](#authentication)
11. [Acknowledgements](#acknowledgements)
12. [Binary Data](#binary-data)
13. [Adapters](#adapters)
14. [Scaling](#scaling)
15. [Connection State Recovery](#connection-state-recovery)
16. [Engine.IO](#engineio)
17. [Transport Options](#transport-options)
18. [Testing](#testing)
19. [Performance](#performance)
20. [Best Practices](#best-practices)

## Getting Started

### Installation

```bash
# Server
npm install socket.io

# Client
npm install socket.io-client

# Additional packages for scaling
npm install @socket.io/redis-adapter
npm install @socket.io/cluster-adapter
npm install @socket.io/sticky
```

### Basic Server Setup

```javascript
// With Express
const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "http://localhost:3001",
    methods: ["GET", "POST"]
  }
});

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

httpServer.listen(3000, () => {
  console.log('Server listening on port 3000');
});
```

### Basic Client Setup

```javascript
// Browser or Node.js
import { io } from 'socket.io-client';

const socket = io('http://localhost:3000', {
  transports: ['websocket', 'polling'],
  auth: {
    token: 'my-token'
  }
});

socket.on('connect', () => {
  console.log('Connected:', socket.id);
});

socket.on('disconnect', (reason) => {
  console.log('Disconnected:', reason);
});

// HTML with CDN
`
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
  const socket = io();
  socket.on('connect', () => {
    console.log('Connected');
  });
</script>
`;
```

## Server API

### Server Configuration

```javascript
const io = new Server(httpServer, {
  // Path configuration
  path: '/socket.io/',
  
  // Parser configuration
  parser: require('socket.io-msgpack-parser'),
  
  // Connection configuration
  connectTimeout: 5000,
  
  // Ping configuration
  pingInterval: 25000,
  pingTimeout: 20000,
  
  // Transport configuration
  transports: ['polling', 'websocket'],
  allowUpgrades: true,
  upgradeTimeout: 10000,
  
  // CORS configuration
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
    allowedHeaders: ['content-type'],
    credentials: true
  },
  
  // WebSocket configuration
  perMessageDeflate: {
    threshold: 1024
  },
  
  // HTTP compression
  httpCompression: {
    threshold: 1024
  },
  
  // Socket.IO specific
  serveClient: true,
  adapter: require('@socket.io/redis-adapter'),
  allowEIO3: false,
  maxHttpBufferSize: 1e6,
  
  // Connection state recovery
  connectionStateRecovery: {
    maxDisconnectionDuration: 2 * 60 * 1000,
    skipMiddlewares: true
  },
  
  // Cleanup empty namespaces
  cleanupEmptyChildNamespaces: true
});
```

### Server Methods

```javascript
// Get all connected sockets
const sockets = await io.fetchSockets();
sockets.forEach(socket => {
  console.log(socket.id);
  console.log(socket.handshake);
  console.log(socket.rooms);
  console.log(socket.data);
});

// Server-side events
io.on('connection', (socket) => {
  // Socket connected
});

io.on('new_namespace', (namespace) => {
  // New namespace created
});

// Engine.IO events
io.engine.on('connection_error', (err) => {
  console.log(err.req);
  console.log(err.code);
  console.log(err.message);
  console.log(err.context);
});

// Generate socket IDs
io.engine.generateId = (req) => {
  return 'custom-' + Math.random();
};

// Close server
io.close(() => {
  console.log('Server closed');
});
```

### Socket Object (Server)

```javascript
io.on('connection', (socket) => {
  // Socket properties
  console.log(socket.id);           // Socket ID
  console.log(socket.handshake);    // Handshake details
  console.log(socket.rooms);        // Set of rooms
  console.log(socket.data);         // Custom data
  console.log(socket.connected);    // Connection status
  console.log(socket.recovered);    // Recovery status
  
  // Handshake details
  const { 
    headers,
    query,
    auth,
    time,
    issued,
    url,
    address,
    xdomain,
    secure
  } = socket.handshake;
  
  // Join/leave rooms
  socket.join('room1');
  socket.join(['room1', 'room2']);
  socket.leave('room1');
  
  // Send events
  socket.emit('event', data);
  socket.send('message');
  
  // Broadcast (to everyone except sender)
  socket.broadcast.emit('event', data);
  
  // To specific room
  socket.to('room1').emit('event', data);
  socket.to(['room1', 'room2']).emit('event', data);
  
  // Volatile events (can be dropped)
  socket.volatile.emit('event', data);
  
  // Compress
  socket.compress(true).emit('event', data);
  
  // Timeout
  socket.timeout(5000).emit('event', data, (err, response) => {
    if (err) {
      // Timeout occurred
    } else {
      // Got response
    }
  });
  
  // Disconnect
  socket.disconnect();
  socket.disconnect(true); // Close underlying connection
});
```

## Client API

### Client Configuration

```javascript
const socket = io('http://localhost:3000', {
  // Connection options
  forceNew: false,
  multiplex: true,
  
  // Reconnection options
  reconnection: true,
  reconnectionAttempts: Infinity,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  randomizationFactor: 0.5,
  
  // Timeout options
  timeout: 20000,
  ackTimeout: 10000,
  
  // Auth options
  auth: {
    token: 'my-auth-token'
  },
  
  // Query options
  query: {
    userId: '123'
  },
  
  // Transport options
  transports: ['websocket', 'polling'],
  upgrade: true,
  rememberUpgrade: false,
  
  // Path
  path: '/socket.io/',
  
  // Parser
  parser: require('socket.io-msgpack-parser'),
  
  // Close on beforeunload
  closeOnBeforeunload: true,
  
  // Retry configuration
  retries: 3,
  
  // Extra headers (Node.js only)
  extraHeaders: {
    'X-Custom-Header': 'value'
  },
  
  // With credentials
  withCredentials: true,
  
  // Transport-specific options
  transportOptions: {
    polling: {
      extraHeaders: {
        'X-Custom-Header': 'value'
      }
    },
    websocket: {
      // WebSocket options
    }
  }
});
```

### Client Methods

```javascript
// Connection management
socket.connect();
socket.open(); // Alias for connect
socket.disconnect();
socket.close(); // Alias for disconnect

// Event emission
socket.emit('event', data);
socket.send('message'); // Shorthand for emit('message', ...)

// Volatile events
socket.volatile.emit('event', data);

// Compressed events
socket.compress(true).emit('event', data);

// Binary flag control
socket.binary(false).emit('plain-object', object);

// Event listeners
socket.on('event', callback);
socket.once('event', callback);
socket.off('event', callback);
socket.removeListener('event', callback);
socket.removeAllListeners('event');
socket.removeAllListeners();

// Any event listeners
socket.onAny((eventName, ...args) => {
  console.log(`Received ${eventName}`);
});

socket.prependAny((eventName, ...args) => {
  console.log(`Before ${eventName}`);
});

socket.offAny(listener);

// Outgoing event listeners
socket.onAnyOutgoing((eventName, ...args) => {
  console.log(`Sending ${eventName}`);
});

socket.prependAnyOutgoing((eventName, ...args) => {
  console.log(`Before sending ${eventName}`);
});

socket.offAnyOutgoing(listener);

// Get all listeners
const listeners = socket.listeners('event');
const count = socket.listenerCount('event');
```

### Client Properties

```javascript
// Connection state
console.log(socket.connected);    // Boolean
console.log(socket.disconnected); // Boolean
console.log(socket.id);          // Socket ID
console.log(socket.recovered);   // Recovery status

// Manager access
console.log(socket.io);          // Manager instance

// Access to underlying engine
socket.io.on('reconnect', (attempt) => {
  console.log(`Reconnected after ${attempt} attempts`);
});

socket.io.on('reconnect_attempt', (attempt) => {
  console.log(`Reconnection attempt ${attempt}`);
});

socket.io.on('reconnect_error', (error) => {
  console.log('Reconnection error:', error);
});

socket.io.on('reconnect_failed', () => {
  console.log('Reconnection failed');
});

socket.io.on('ping', () => {
  console.log('Ping sent');
});

socket.io.on('error', (error) => {
  console.log('Manager error:', error);
});
```

## Events

### System Events (Server)

```javascript
io.on('connection', (socket) => {
  // Client events
  socket.on('disconnect', (reason) => {
    // Reasons: 'transport error', 'transport close', 'ping timeout',
    // 'client namespace disconnect', 'server namespace disconnect'
    console.log('Disconnected:', reason);
  });
  
  socket.on('disconnecting', (reason) => {
    // Socket is disconnecting (rooms still accessible)
    console.log('Disconnecting from rooms:', socket.rooms);
  });
  
  socket.on('error', (error) => {
    console.error('Socket error:', error);
  });
});

// Namespace events
namespace.on('connection', (socket) => {
  // Socket connected to namespace
});

namespace.on('connect', (socket) => {
  // Alias for connection
});
```

### System Events (Client)

```javascript
// Connection events
socket.on('connect', () => {
  console.log('Connected with ID:', socket.id);
});

socket.on('disconnect', (reason, details) => {
  console.log('Disconnected:', reason);
  if (reason === 'transport error') {
    console.log('Error details:', details);
  }
});

socket.on('connect_error', (error) => {
  console.log('Connection error:', error.message);
  console.log('Error type:', error.type);
  console.log('Error context:', error.context);
});

// Manager events (via socket.io)
socket.io.on('reconnect', (attemptNumber) => {
  console.log('Reconnected after', attemptNumber, 'attempts');
});

socket.io.on('reconnect_attempt', (attemptNumber) => {
  console.log('Reconnection attempt', attemptNumber);
});

socket.io.on('reconnect_error', (error) => {
  console.log('Reconnection error:', error);
});

socket.io.on('reconnect_failed', () => {
  console.log('Failed to reconnect');
});

socket.io.on('ping', () => {
  console.log('Ping packet sent');
});

socket.io.on('error', (error) => {
  console.log('Manager error:', error);
});
```

### Custom Events

```javascript
// Server
io.on('connection', (socket) => {
  // Listen for custom events
  socket.on('chat message', (msg) => {
    console.log('Message:', msg);
    
    // Broadcast to all
    io.emit('chat message', msg);
    
    // Broadcast to all except sender
    socket.broadcast.emit('chat message', msg);
    
    // Send to specific socket
    io.to(socketId).emit('private message', msg);
  });
  
  // Catch-all listener
  socket.onAny((eventName, ...args) => {
    console.log(`Received ${eventName}:`, args);
  });
  
  // Prepend listener (runs first)
  socket.prependAny((eventName, ...args) => {
    console.log(`Before processing ${eventName}`);
  });
});

// Client
socket.emit('chat message', 'Hello World');

socket.on('chat message', (msg) => {
  console.log('Received:', msg);
});

// Any event listener
socket.onAny((eventName, ...args) => {
  console.log(`Event ${eventName} received:`, args);
});

// Monitor outgoing events
socket.onAnyOutgoing((eventName, ...args) => {
  console.log(`Sending ${eventName}:`, args);
});
```

## Namespaces

### Creating and Using Namespaces

```javascript
// Server - Create namespace
const adminNamespace = io.of('/admin');

adminNamespace.on('connection', (socket) => {
  console.log('Admin connected:', socket.id);
  
  socket.on('admin-event', (data) => {
    // Handle admin event
  });
});

// Dynamic namespaces with regex
io.of(/^\/dynamic-\d+$/).on('connection', (socket) => {
  const namespace = socket.nsp;
  console.log('Connected to:', namespace.name);
});

// Middleware for namespace
adminNamespace.use((socket, next) => {
  // Authentication for admin namespace
  if (isAdmin(socket.handshake.auth)) {
    next();
  } else {
    next(new Error('Not authorized'));
  }
});

// Client - Connect to namespace
const adminSocket = io('/admin');
const dynamicSocket = io('/dynamic-101');

adminSocket.on('connect', () => {
  console.log('Connected to admin namespace');
});
```

### Namespace Configuration

```javascript
// Get all namespaces
io._nsps.forEach((namespace, name) => {
  console.log('Namespace:', name);
});

// Namespace properties and methods
const namespace = io.of('/custom');

// Get all connected sockets in namespace
const sockets = await namespace.fetchSockets();

// Emit to all in namespace
namespace.emit('announcement', 'Hello everyone');

// Get rooms in namespace
const rooms = namespace.adapter.rooms;

// Disconnect all sockets in namespace
namespace.disconnectSockets();
namespace.disconnectSockets(true); // Close underlying connections

// Local flag (for multi-server setups)
namespace.local.emit('local-only-event');

// Get namespace by name
const ns = io.of('/admin');

// Server-side namespace events
namespace.on('connection', (socket) => {
  // Socket connected to this namespace
});

// Clean up empty child namespaces
const io = new Server({
  cleanupEmptyChildNamespaces: true
});
```

## Rooms

### Room Management

```javascript
io.on('connection', (socket) => {
  // Join room(s)
  socket.join('room1');
  socket.join(['room2', 'room3']);
  
  // Leave room
  socket.leave('room1');
  
  // Get rooms socket is in
  console.log(socket.rooms); // Set { socketId, 'room2', 'room3' }
  
  // Check if in room
  if (socket.rooms.has('room2')) {
    console.log('Socket is in room2');
  }
  
  // Emit to rooms
  socket.to('room1').emit('event', data);
  socket.to(['room1', 'room2']).emit('event', data);
  
  // Emit to room except sender
  socket.to('room1').emit('event'); // Doesn't include sender
  io.to('room1').emit('event');     // Includes all in room
  
  // Multiple rooms (union)
  io.to('room1').to('room2').emit('event');
  
  // Leave all rooms
  socket.rooms.clear();
  socket.rooms.add(socket.id); // Keep default room
  
  // Get sockets in room
  const socketsInRoom = await io.in('room1').fetchSockets();
  
  // Disconnect sockets in room
  io.in('room1').disconnectSockets();
  
  // Room size
  const rooms = io.sockets.adapter.rooms;
  const roomSize = rooms.get('room1')?.size || 0;
});
```

### Dynamic Rooms

```javascript
// Chat room example
io.on('connection', (socket) => {
  socket.on('join-room', (roomId, userId) => {
    socket.join(roomId);
    socket.data.userId = userId;
    
    // Notify others in room
    socket.to(roomId).emit('user-joined', {
      userId,
      socketId: socket.id
    });
    
    // Get all users in room
    const sockets = await io.in(roomId).fetchSockets();
    const users = sockets.map(s => ({
      socketId: s.id,
      userId: s.data.userId
    }));
    
    socket.emit('room-users', users);
  });
  
  socket.on('leave-room', (roomId) => {
    socket.leave(roomId);
    socket.to(roomId).emit('user-left', socket.data.userId);
  });
  
  socket.on('room-message', (roomId, message) => {
    io.to(roomId).emit('new-message', {
      userId: socket.data.userId,
      message,
      timestamp: Date.now()
    });
  });
  
  socket.on('disconnecting', () => {
    // Notify all rooms user is leaving
    socket.rooms.forEach(roomId => {
      if (roomId !== socket.id) {
        socket.to(roomId).emit('user-disconnected', socket.data.userId);
      }
    });
  });
});
```

## Broadcasting

### Broadcasting Patterns

```javascript
io.on('connection', (socket) => {
  // To all connected clients
  io.emit('broadcast', data);
  
  // To all except sender
  socket.broadcast.emit('broadcast', data);
  
  // To specific room(s)
  socket.to('room1').emit('room-event', data);
  socket.to(['room1', 'room2']).emit('multi-room', data);
  io.to('room1').emit('room-event', data);
  
  // To specific socket
  io.to(socketId).emit('private', data);
  socket.to(socketId).emit('private', data);
  
  // To namespace
  io.of('/admin').emit('admin-event', data);
  
  // Exclude rooms
  socket.broadcast.except('room1').emit('event', data);
  io.except('room1').emit('event', data);
  
  // Local emission (doesn't go through adapter)
  socket.local.emit('local-event', data);
  io.local.emit('local-event', data);
  
  // Volatile (can be dropped)
  socket.volatile.emit('volatile-event', data);
  io.volatile.emit('volatile-event', data);
  
  // Compressed
  socket.compress(true).emit('compressed', largeData);
  
  // Combined flags
  socket.volatile.compress(true).to('room1').emit('event', data);
  
  // Binary control
  socket.binary(false).emit('no-binary-scan', plainObject);
});
```

### Advanced Broadcasting

```javascript
// Broadcast with acknowledgment
io.timeout(5000).emit('event-with-ack', data, (err, responses) => {
  if (err) {
    // Some clients did not acknowledge in time
    console.error('Timeout on some clients');
  } else {
    // responses is an array of responses from each socket
    responses.forEach((response, index) => {
      console.log(`Response ${index}:`, response);
    });
  }
});

// Emit with acknowledgment (promise-based)
try {
  const responses = await io.timeout(1000).emitWithAck('event', data);
  console.log('All responses:', responses);
} catch (err) {
  console.error('Some clients did not respond in time');
}

// Socket-specific acknowledgment
socket.timeout(5000).emit('request', data, (err, response) => {
  if (err) {
    console.error('Client did not respond in time');
  } else {
    console.log('Client response:', response);
  }
});

// Server-side emit (between servers)
io.serverSideEmit('server-event', data);

// With acknowledgment
io.serverSideEmitWithAck('server-request', data).then(responses => {
  console.log('Server responses:', responses);
});
```

## Middleware

### Socket Middleware

```javascript
// Global middleware
io.use((socket, next) => {
  // Runs for every connection attempt
  const token = socket.handshake.auth.token;
  
  if (isValidToken(token)) {
    socket.data.user = getUserFromToken(token);
    next();
  } else {
    next(new Error('Authentication failed'));
  }
});

// Multiple middleware
io.use(middleware1);
io.use(middleware2);
io.use(middleware3);

// Namespace middleware
const adminNs = io.of('/admin');
adminNs.use((socket, next) => {
  if (socket.handshake.auth.role === 'admin') {
    next();
  } else {
    next(new Error('Admin access only'));
  }
});

// Async middleware
io.use(async (socket, next) => {
  try {
    const user = await authenticateUser(socket.handshake.auth);
    socket.data.user = user;
    next();
  } catch (err) {
    next(err);
  }
});

// Conditional middleware
io.use((socket, next) => {
  if (socket.handshake.headers['x-custom-header']) {
    // Apply special handling
    socket.data.special = true;
  }
  next();
});
```

### Engine.IO Middleware

```javascript
// Express-style middleware at Engine.IO level
io.engine.use((req, res, next) => {
  // Runs for every HTTP request (including upgrade)
  console.log('Engine.IO request:', req.url);
  next();
});

// Session middleware
const session = require('express-session');
const sessionMiddleware = session({
  secret: 'secret-key',
  resave: false,
  saveUninitialized: true
});

io.engine.use(sessionMiddleware);

// Only for handshake
function onlyForHandshake(middleware) {
  return (req, res, next) => {
    const isHandshake = req._query.sid === undefined;
    if (isHandshake) {
      middleware(req, res, next);
    } else {
      next();
    }
  };
}

io.engine.use(onlyForHandshake(sessionMiddleware));
io.engine.use(onlyForHandshake(passport.session()));

// Authentication check
io.engine.use(onlyForHandshake((req, res, next) => {
  if (req.user) {
    next();
  } else {
    res.writeHead(401);
    res.end();
  }
}));

// Helmet for security
const helmet = require('helmet');
io.engine.use(helmet());
```

### Event Middleware Pattern

```javascript
// Custom event middleware system
class SocketMiddleware {
  constructor() {
    this.middlewares = new Map();
  }
  
  use(event, ...handlers) {
    if (!this.middlewares.has(event)) {
      this.middlewares.set(event, []);
    }
    this.middlewares.get(event).push(...handlers);
  }
  
  async process(event, socket, ...args) {
    const handlers = this.middlewares.get(event) || [];
    
    for (const handler of handlers) {
      try {
        await handler(socket, ...args);
      } catch (err) {
        socket.emit('error', err.message);
        return false;
      }
    }
    return true;
  }
}

const eventMiddleware = new SocketMiddleware();

// Register middleware for specific events
eventMiddleware.use('chat-message', 
  async (socket, message) => {
    // Validate message
    if (!message || message.length > 1000) {
      throw new Error('Invalid message');
    }
  },
  async (socket, message) => {
    // Check rate limit
    if (isRateLimited(socket.id)) {
      throw new Error('Rate limit exceeded');
    }
  }
);

// Use in connection handler
io.on('connection', (socket) => {
  socket.on('chat-message', async (message) => {
    const success = await eventMiddleware.process('chat-message', socket, message);
    if (success) {
      io.emit('chat-message', {
        user: socket.data.user,
        message,
        timestamp: Date.now()
      });
    }
  });
});
```

## Error Handling

### Connection Errors

```javascript
// Server-side error handling
io.on('connection', (socket) => {
  socket.on('error', (error) => {
    console.error('Socket error:', error);
  });
});

// Middleware errors
io.use((socket, next) => {
  try {
    // Authentication logic
    if (!socket.handshake.auth.token) {
      throw new Error('No token provided');
    }
    next();
  } catch (err) {
    next(err); // Pass error to client
  }
});

// Client-side error handling
socket.on('connect_error', (error) => {
  console.error('Connection error:', error.message);
  
  if (error.type === 'TransportError') {
    console.error('Transport error details:', error.context);
  }
  
  // Retry with different options
  if (socket.io.opts.transports.includes('polling')) {
    socket.io.opts.transports = ['websocket'];
  }
});

// Engine.IO errors
io.engine.on('connection_error', (err) => {
  console.error('Engine.IO connection error:');
  console.error('Request:', err.req);
  console.error('Code:', err.code);
  console.error('Message:', err.message);
  console.error('Context:', err.context);
});
```

### Event Error Handling

```javascript
// Wrap handlers in try-catch
io.on('connection', (socket) => {
  socket.on('risky-operation', async (data) => {
    try {
      const result = await performRiskyOperation(data);
      socket.emit('operation-success', result);
    } catch (error) {
      console.error('Operation failed:', error);
      socket.emit('operation-error', {
        message: error.message,
        code: error.code
      });
    }
  });
});

// Global error handler
function withErrorHandler(handler) {
  return async (...args) => {
    try {
      await handler(...args);
    } catch (error) {
      const socket = args[0];
      socket.emit('error', {
        event: handler.name,
        message: error.message
      });
    }
  };
}

// Use error handler wrapper
io.on('connection', (socket) => {
  socket.on('event1', withErrorHandler(handleEvent1));
  socket.on('event2', withErrorHandler(handleEvent2));
});

// Error recovery
socket.on('connect_error', (error) => {
  // Implement exponential backoff
  const backoff = Math.min(1000 * Math.pow(2, reconnectAttempt), 30000);
  reconnectAttempt++;
  
  setTimeout(() => {
    socket.connect();
  }, backoff);
});
```

## Authentication

### Token-based Authentication

```javascript
// Server
const jwt = require('jsonwebtoken');

io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    socket.data.user = decoded;
    next();
  } catch (err) {
    next(new Error('Authentication error'));
  }
});

// Client
const socket = io({
  auth: {
    token: localStorage.getItem('token')
  }
});

// Dynamic authentication
socket.on('connect_error', (err) => {
  if (err.message === 'Authentication error') {
    // Refresh token
    refreshToken().then(newToken => {
      socket.auth.token = newToken;
      socket.connect();
    });
  }
});

// Update auth on reconnection
socket.auth = (cb) => {
  cb({
    token: getLatestToken()
  });
};
```

### Session-based Authentication

```javascript
// Server with Express session
const session = require('express-session');
const passport = require('passport');

const sessionMiddleware = session({
  secret: 'secret',
  resave: false,
  saveUninitialized: false
});

// Share session with Socket.IO
io.engine.use(sessionMiddleware);
io.engine.use(passport.initialize());
io.engine.use(passport.session());

io.use((socket, next) => {
  const session = socket.request.session;
  if (session && session.passport && session.passport.user) {
    socket.data.userId = session.passport.user;
    next();
  } else {
    next(new Error('Unauthorized'));
  }
});
```

### OAuth Authentication

```javascript
// Passport JWT strategy
const JwtStrategy = require('passport-jwt').Strategy;

passport.use(new JwtStrategy({
  jwtFromRequest: (req) => {
    // Extract token from handshake
    return req._query.token;
  },
  secretOrKey: process.env.JWT_SECRET
}, async (payload, done) => {
  try {
    const user = await User.findById(payload.id);
    if (user) {
      return done(null, user);
    }
    return done(null, false);
  } catch (error) {
    return done(error, false);
  }
}));

// Apply to Socket.IO
io.engine.use((req, res, next) => {
  const isHandshake = req._query.sid === undefined;
  if (isHandshake) {
    passport.authenticate('jwt', { session: false })(req, res, next);
  } else {
    next();
  }
});

io.use((socket, next) => {
  if (socket.request.user) {
    socket.data.user = socket.request.user;
    next();
  } else {
    next(new Error('Unauthorized'));
  }
});
```

## Acknowledgements

### Basic Acknowledgements

```javascript
// Server
io.on('connection', (socket) => {
  // With callback
  socket.on('request', (data, callback) => {
    // Process request
    const result = processRequest(data);
    
    // Send acknowledgement
    callback({
      status: 'success',
      result
    });
  });
  
  // Multiple arguments in callback
  socket.on('multi-ack', (data, callback) => {
    callback('arg1', 'arg2', 'arg3');
  });
});

// Client
// Callback style
socket.emit('request', { data: 'test' }, (response) => {
  console.log('Server acknowledged:', response);
});

// Promise style (client only)
const response = await socket.emitWithAck('request', { data: 'test' });
console.log('Server response:', response);

// With timeout
try {
  const response = await socket.timeout(5000).emitWithAck('request', data);
  console.log('Got response:', response);
} catch (err) {
  console.error('No response within 5 seconds');
}
```

### Broadcasting with Acknowledgements

```javascript
// Server - broadcast with ack
io.timeout(5000).emit('broadcast-with-ack', 'data', (err, responses) => {
  if (err) {
    console.log('Some clients did not ack');
  } else {
    console.log(`${responses.length} clients acknowledged`);
    responses.forEach((response, i) => {
      console.log(`Client ${i}:`, response);
    });
  }
});

// Promise-based
try {
  const responses = await io.timeout(5000).emitWithAck('event', data);
  console.log('All responses:', responses);
} catch (err) {
  console.error('Timeout reached');
}

// Room broadcast with ack
const responses = await io.to('room1').timeout(3000).emitWithAck('room-event', data);

// Server-to-server with ack
io.serverSideEmit('cluster-event', data, (err, responses) => {
  if (!err) {
    console.log('Other servers responded:', responses);
  }
});

// Promise version
const responses = await io.serverSideEmitWithAck('cluster-event', data);
```

### Retry Mechanism

```javascript
// Client with retry configuration
const socket = io({
  retries: 3,
  ackTimeout: 10000
});

// Manual retry implementation
async function emitWithRetry(event, data, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await socket.timeout(5000).emitWithAck(event, data);
      return response;
    } catch (err) {
      console.log(`Attempt ${i + 1} failed`);
      if (i === maxRetries - 1) throw err;
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
}
```

## Binary Data

### Sending Binary Data

```javascript
// Server
io.on('connection', (socket) => {
  // Send Buffer
  const buffer = Buffer.from('Hello World');
  socket.emit('buffer-data', buffer);
  
  // Send ArrayBuffer
  const arrayBuffer = new ArrayBuffer(10);
  socket.emit('arraybuffer-data', arrayBuffer);
  
  // Send Blob (browser)
  socket.on('image', (imageBlob) => {
    // Process blob
    socket.broadcast.emit('new-image', imageBlob);
  });
  
  // Mixed data
  socket.emit('mixed', {
    text: 'Hello',
    binary: Buffer.from([1, 2, 3, 4]),
    nested: {
      data: new Uint8Array([5, 6, 7, 8])
    }
  });
});

// Client
// Send file
const fileInput = document.getElementById('file');
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  socket.emit('file-upload', {
    name: file.name,
    size: file.size,
    type: file.type,
    data: file
  });
});

// Receive binary
socket.on('buffer-data', (buffer) => {
  // In browser, buffer is ArrayBuffer
  const view = new Uint8Array(buffer);
  console.log('Received buffer:', view);
});
```

### Binary Performance

```javascript
// Control binary scanning
io.on('connection', (socket) => {
  // Skip binary scanning for performance
  socket.binary(false).emit('large-json', {
    // Large JSON object without binary data
    // Skips recursive scanning
  });
  
  // Namespace level
  io.binary(false).emit('broadcast-json', plainObject);
});

// Compression with binary
socket.compress(true).emit('compressed-binary', largeBinaryData);

// Stream large files
const stream = ss.createStream();
ss(socket).emit('file-stream', stream, { name: 'file.pdf' });
fs.createReadStream('large-file.pdf').pipe(stream);

// Chunked transfer
function sendFileInChunks(socket, filePath, chunkSize = 64 * 1024) {
  const stream = fs.createReadStream(filePath, { highWaterMark: chunkSize });
  let chunk = 0;
  
  stream.on('data', (data) => {
    socket.emit('file-chunk', {
      chunk: chunk++,
      data: data
    });
  });
  
  stream.on('end', () => {
    socket.emit('file-complete', { chunks: chunk });
  });
}
```

## Scaling

### Redis Adapter

```javascript
const { createAdapter } = require('@socket.io/redis-adapter');
const { createClient } = require('redis');

const pubClient = createClient({ host: 'localhost', port: 6379 });
const subClient = pubClient.duplicate();

Promise.all([pubClient.connect(), subClient.connect()]).then(() => {
  io.adapter(createAdapter(pubClient, subClient));
});

// With Redis Streams
const { createAdapter } = require('@socket.io/redis-streams-adapter');

io.adapter(createAdapter(pubClient));

// Emit from external process
const { Emitter } = require('@socket.io/redis-emitter');

const emitter = new Emitter(pubClient);
emitter.to('room1').emit('external-event', 'data');
```

### Cluster Adapter

```javascript
const cluster = require('cluster');
const { setupPrimary, NodeClusterEngine } = require('@socket.io/cluster-engine');

if (cluster.isPrimary) {
  const numCPUs = require('os').cpus().length;
  
  // Setup primary
  setupPrimary();
  
  // Fork workers
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} died`);
    cluster.fork();
  });
} else {
  const engine = new NodeClusterEngine();
  
  engine.attach(httpServer, {
    path: '/socket.io/'
  });
  
  io.bind(engine);
  
  httpServer.listen(3000);
}
```

### Sticky Sessions

```javascript
const cluster = require('cluster');
const { setupMaster, setupWorker } = require('@socket.io/sticky');

if (cluster.isMaster) {
  const numWorkers = require('os').cpus().length;
  
  setupMaster(httpServer, {
    loadBalancingMethod: 'least-connection'
  });
  
  for (let i = 0; i < numWorkers; i++) {
    cluster.fork();
  }
} else {
  setupWorker(io);
  httpServer.listen(0, 'localhost');
}
```

## Connection State Recovery

### Basic Recovery

```javascript
// Server configuration
const io = new Server({
  connectionStateRecovery: {
    // Maximum disconnection duration
    maxDisconnectionDuration: 2 * 60 * 1000,
    // Skip middlewares on recovery
    skipMiddlewares: true
  }
});

io.on('connection', (socket) => {
  if (socket.recovered) {
    // Socket recovered successfully
    console.log('Socket recovered, missed events:', socket.missedEvents);
  } else {
    // New connection or recovery failed
    console.log('New connection');
  }
  
  // Access recovery info
  console.log('Recovery offset:', socket.handshake.auth.offset);
});

// Client
socket.on('connect', () => {
  if (socket.recovered) {
    console.log('Connection recovered');
    // Any missed events have been received
  } else {
    console.log('New connection');
    // Need to restore state manually
  }
});
```

### Custom Recovery Implementation

```javascript
// Server
const sessions = new Map();

io.on('connection', (socket) => {
  const sessionId = socket.handshake.auth.sessionId;
  
  if (sessionId && sessions.has(sessionId)) {
    // Restore session
    const session = sessions.get(sessionId);
    socket.data = session.data;
    socket.join(session.rooms);
    
    // Send missed messages
    session.missedMessages.forEach(msg => {
      socket.emit(...msg);
    });
    
    sessions.delete(sessionId);
  } else {
    // New session
    socket.data.sessionId = generateSessionId();
    socket.emit('session', socket.data.sessionId);
  }
  
  socket.on('disconnect', () => {
    // Store session for recovery
    sessions.set(socket.data.sessionId, {
      data: socket.data,
      rooms: [...socket.rooms].filter(r => r !== socket.id),
      missedMessages: [],
      disconnectedAt: Date.now()
    });
    
    // Clean up old sessions
    setTimeout(() => {
      sessions.delete(socket.data.sessionId);
    }, 60000);
  });
});

// Client
let sessionId = localStorage.getItem('sessionId');

const socket = io({
  auth: {
    sessionId
  }
});

socket.on('session', (id) => {
  sessionId = id;
  localStorage.setItem('sessionId', id);
});
```

## Testing

### Unit Testing

```javascript
const { createServer } = require('http');
const { Server } = require('socket.io');
const Client = require('socket.io-client');

describe('Socket.IO Server', () => {
  let io, serverSocket, clientSocket;
  
  beforeAll((done) => {
    const httpServer = createServer();
    io = new Server(httpServer);
    httpServer.listen(() => {
      const port = httpServer.address().port;
      clientSocket = new Client(`http://localhost:${port}`);
      io.on('connection', (socket) => {
        serverSocket = socket;
      });
      clientSocket.on('connect', done);
    });
  });
  
  afterAll(() => {
    io.close();
    clientSocket.close();
  });
  
  test('should communicate', (done) => {
    serverSocket.on('message', (arg) => {
      expect(arg).toBe('world');
      done();
    });
    clientSocket.emit('message', 'world');
  });
  
  test('should receive acknowledgement', (done) => {
    serverSocket.on('request', (data, callback) => {
      callback('response');
    });
    clientSocket.emit('request', 'data', (response) => {
      expect(response).toBe('response');
      done();
    });
  });
});
```

### Integration Testing

```javascript
// Test configuration
const io = new Server(3000, {
  pingInterval: 300,
  pingTimeout: 200,
  maxPayload: 1000000,
  connectTimeout: 1000,
  cors: {
    origin: '*'
  }
});

io.on('connection', (socket) => {
  socket.emit('auth', socket.handshake.auth);
  
  socket.on('message', (...args) => {
    socket.emit.apply(socket, ['message-back', ...args]);
  });
  
  socket.on('message-with-ack', (...args) => {
    const ack = args.pop();
    ack(...args);
  });
});

io.of('/custom').on('connection', (socket) => {
  socket.emit('auth', socket.handshake.auth);
});
```

## Best Practices

### Connection Management

```javascript
// Implement connection pooling
class SocketPool {
  constructor(maxConnections = 5) {
    this.connections = [];
    this.maxConnections = maxConnections;
  }
  
  connect(url, options) {
    if (this.connections.length >= this.maxConnections) {
      // Reuse existing connection
      return this.connections[0];
    }
    
    const socket = io(url, options);
    this.connections.push(socket);
    
    socket.on('disconnect', () => {
      const index = this.connections.indexOf(socket);
      if (index > -1) {
        this.connections.splice(index, 1);
      }
    });
    
    return socket;
  }
  
  closeAll() {
    this.connections.forEach(socket => socket.close());
    this.connections = [];
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing connections...');
  
  io.close(() => {
    console.log('All connections closed');
    process.exit(0);
  });
  
  // Force close after timeout
  setTimeout(() => {
    process.exit(1);
  }, 10000);
});
```

### Performance Optimization

```javascript
// Debounce expensive operations
const debounce = (func, wait) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

io.on('connection', (socket) => {
  const debouncedSave = debounce((data) => {
    saveToDatabase(data);
  }, 1000);
  
  socket.on('frequent-update', debouncedSave);
});

// Batch operations
class BatchEmitter {
  constructor(socket, event, interval = 100) {
    this.socket = socket;
    this.event = event;
    this.queue = [];
    
    setInterval(() => {
      if (this.queue.length > 0) {
        this.socket.emit(this.event, this.queue);
        this.queue = [];
      }
    }, interval);
  }
  
  add(data) {
    this.queue.push(data);
  }
}

// Use volatile for non-critical updates
setInterval(() => {
  io.volatile.emit('time-update', new Date());
}, 1000);
```

### Security Best Practices

```javascript
// Rate limiting
const rateLimiter = new Map();

io.on('connection', (socket) => {
  socket.use(([event, ...args], next) => {
    const key = `${socket.id}:${event}`;
    const now = Date.now();
    const limit = rateLimiter.get(key) || { count: 0, resetTime: now + 60000 };
    
    if (now > limit.resetTime) {
      limit.count = 0;
      limit.resetTime = now + 60000;
    }
    
    if (limit.count >= 100) { // 100 events per minute
      return next(new Error('Rate limit exceeded'));
    }
    
    limit.count++;
    rateLimiter.set(key, limit);
    next();
  });
});

// Input validation
const validator = require('validator');

socket.on('message', (message) => {
  if (!validator.isLength(message, { min: 1, max: 1000 })) {
    return socket.emit('error', 'Invalid message length');
  }
  
  const sanitized = validator.escape(message);
  io.emit('message', sanitized);
});

// Origin validation
const io = new Server({
  cors: {
    origin: (origin, callback) => {
      const allowedOrigins = ['https://example.com', 'https://app.example.com'];
      
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true
  }
});
```

## Conclusion

This comprehensive Socket.IO documentation covers all essential aspects of real-time bidirectional communication between web clients and servers. From basic event handling to advanced scaling strategies, from authentication to performance optimization, these examples provide a complete reference for Socket.IO development. Remember to consider security, implement proper error handling, and optimize for performance in production applications.