# Node.js Complete Documentation

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [File System (fs)](#file-system-fs)
3. [Path Module](#path-module)
4. [Process and Child Processes](#process-and-child-processes)
5. [Streams](#streams)
6. [Buffers](#buffers)
7. [Events](#events)
8. [HTTP/HTTPS](#httphttps)
9. [Networking](#networking)
10. [Crypto](#crypto)
11. [OS Module](#os-module)
12. [Cluster](#cluster)
13. [Worker Threads](#worker-threads)
14. [Timers](#timers)
15. [URL Module](#url-module)
16. [Query String](#query-string)
17. [Utilities](#utilities)
18. [Debugging](#debugging)
19. [Error Handling](#error-handling)
20. [NPM and Package Management](#npm-and-package-management)
21. [Performance](#performance)
22. [Best Practices](#best-practices)

## Core Concepts

### Node.js Architecture

```javascript
// Node.js is built on V8 JavaScript engine
// Single-threaded event loop architecture
// Non-blocking I/O operations

// Event-driven programming
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}
const myEmitter = new MyEmitter();

myEmitter.on('event', () => {
  console.log('An event occurred!');
});

myEmitter.emit('event');
```

### Module System

```javascript
// CommonJS modules (traditional Node.js)
// math.js
function add(a, b) {
  return a + b;
}

function subtract(a, b) {
  return a - b;
}

module.exports = {
  add,
  subtract
};

// main.js
const math = require('./math');
console.log(math.add(5, 3)); // 8

// ES Modules (modern Node.js)
// math.mjs
export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

// main.mjs
import { add, subtract } from './math.mjs';
console.log(add(5, 3)); // 8
```

### Global Objects

```javascript
// Global objects available without require
console.log(__dirname);  // Directory of current module
console.log(__filename); // Filename of current module
console.log(process.cwd()); // Current working directory

// Global timer functions
setTimeout(() => console.log('Timeout'), 1000);
setInterval(() => console.log('Interval'), 1000);
setImmediate(() => console.log('Immediate'));

// Process object
console.log(process.version); // Node.js version
console.log(process.platform); // Operating system
console.log(process.argv); // Command line arguments
console.log(process.env); // Environment variables
```

## File System (fs)

### Reading Files

```javascript
const fs = require('fs');
const fsPromises = require('fs').promises;

// Synchronous read
try {
  const data = fs.readFileSync('file.txt', 'utf8');
  console.log(data);
} catch (err) {
  console.error(err);
}

// Asynchronous read with callback
fs.readFile('file.txt', 'utf8', (err, data) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log(data);
});

// Promise-based read
async function readFile() {
  try {
    const data = await fsPromises.readFile('file.txt', 'utf8');
    console.log(data);
  } catch (err) {
    console.error(err);
  }
}

// Reading with streams (for large files)
const readStream = fs.createReadStream('large-file.txt', {
  encoding: 'utf8',
  highWaterMark: 16 * 1024 // 16KB chunks
});

readStream.on('data', (chunk) => {
  console.log('Received chunk:', chunk.length);
});

readStream.on('end', () => {
  console.log('Finished reading');
});

readStream.on('error', (err) => {
  console.error('Error:', err);
});
```

### Writing Files

```javascript
// Synchronous write
try {
  fs.writeFileSync('output.txt', 'Hello World');
  console.log('File written');
} catch (err) {
  console.error(err);
}

// Asynchronous write
fs.writeFile('output.txt', 'Hello World', (err) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log('File written');
});

// Append to file
fs.appendFile('log.txt', 'New log entry\n', (err) => {
  if (err) console.error(err);
});

// Writing with streams
const writeStream = fs.createWriteStream('output.txt');
writeStream.write('First line\n');
writeStream.write('Second line\n');
writeStream.end('Last line');

writeStream.on('finish', () => {
  console.log('Write completed');
});

// Copying files
fs.copyFile('source.txt', 'destination.txt', (err) => {
  if (err) console.error(err);
});

// Using pipeline for efficient copying
const { pipeline } = require('stream');

pipeline(
  fs.createReadStream('source.txt'),
  fs.createWriteStream('destination.txt'),
  (err) => {
    if (err) console.error('Pipeline failed:', err);
    else console.log('Pipeline succeeded');
  }
);
```

### Directory Operations

```javascript
// Create directory
fs.mkdir('new-directory', { recursive: true }, (err) => {
  if (err) console.error(err);
});

// Read directory
fs.readdir('.', { withFileTypes: true }, (err, files) => {
  if (err) {
    console.error(err);
    return;
  }
  
  files.forEach(file => {
    if (file.isDirectory()) {
      console.log('Directory:', file.name);
    } else {
      console.log('File:', file.name);
    }
  });
});

// Remove directory
fs.rmdir('directory', { recursive: true }, (err) => {
  if (err) console.error(err);
});

// Watch directory for changes
const watcher = fs.watch('directory', (eventType, filename) => {
  console.log(`Event: ${eventType}`);
  if (filename) {
    console.log(`File: ${filename}`);
  }
});

// Stop watching
setTimeout(() => {
  watcher.close();
}, 10000);
```

### File Stats and Permissions

```javascript
// Get file stats
fs.stat('file.txt', (err, stats) => {
  if (err) {
    console.error(err);
    return;
  }
  
  console.log('File size:', stats.size);
  console.log('Is file:', stats.isFile());
  console.log('Is directory:', stats.isDirectory());
  console.log('Created:', stats.birthtime);
  console.log('Modified:', stats.mtime);
});

// Check file existence
fs.access('file.txt', fs.constants.F_OK, (err) => {
  if (err) {
    console.log('File does not exist');
  } else {
    console.log('File exists');
  }
});

// Change permissions
fs.chmod('file.txt', 0o644, (err) => {
  if (err) console.error(err);
});

// Change ownership
fs.chown('file.txt', 1000, 1000, (err) => {
  if (err) console.error(err);
});

// Create symbolic link
fs.symlink('target.txt', 'link.txt', (err) => {
  if (err) console.error(err);
});
```

## Path Module

```javascript
const path = require('path');

// Path manipulation
console.log(path.basename('/users/admin/file.txt')); // file.txt
console.log(path.dirname('/users/admin/file.txt')); // /users/admin
console.log(path.extname('/users/admin/file.txt')); // .txt

// Join paths
const fullPath = path.join('/users', 'admin', 'documents', 'file.txt');
console.log(fullPath); // /users/admin/documents/file.txt

// Resolve absolute path
const absolutePath = path.resolve('file.txt');
console.log(absolutePath); // /current/working/directory/file.txt

// Parse path
const pathInfo = path.parse('/users/admin/file.txt');
console.log(pathInfo);
// {
//   root: '/',
//   dir: '/users/admin',
//   base: 'file.txt',
//   ext: '.txt',
//   name: 'file'
// }

// Format path
const formatted = path.format({
  root: '/',
  dir: '/users/admin',
  base: 'file.txt'
});
console.log(formatted); // /users/admin/file.txt

// Normalize path
console.log(path.normalize('/users//admin/../admin/file.txt'));
// /users/admin/file.txt

// Relative path
console.log(path.relative('/users/admin', '/users/admin/documents'));
// documents

// Platform-specific separators
console.log(path.sep); // '/' on Unix, '\' on Windows
console.log(path.delimiter); // ':' on Unix, ';' on Windows
```

## Process and Child Processes

### Process Object

```javascript
// Process information
console.log('PID:', process.pid);
console.log('Platform:', process.platform);
console.log('Architecture:', process.arch);
console.log('Node version:', process.version);
console.log('V8 version:', process.versions.v8);

// Command line arguments
process.argv.forEach((arg, index) => {
  console.log(`Argument ${index}: ${arg}`);
});

// Environment variables
console.log('HOME:', process.env.HOME);
console.log('PATH:', process.env.PATH);

// Set environment variable
process.env.MY_VARIABLE = 'value';

// Exit process
process.on('exit', (code) => {
  console.log(`Process exiting with code: ${code}`);
});

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection at:', promise, 'reason:', reason);
});

// Process signals
process.on('SIGINT', () => {
  console.log('Received SIGINT');
  process.exit(0);
});

// Memory usage
console.log(process.memoryUsage());
// {
//   rss: 4935680,
//   heapTotal: 1826816,
//   heapUsed: 650472,
//   external: 49879,
//   arrayBuffers: 9386
// }

// CPU usage
console.log(process.cpuUsage());
```

### Child Processes

```javascript
const { spawn, exec, execFile, fork } = require('child_process');

// Spawn - streaming interface
const ls = spawn('ls', ['-lh', '/usr']);

ls.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

ls.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

ls.on('close', (code) => {
  console.log(`child process exited with code ${code}`);
});

// Exec - buffered output
exec('ls -lh /usr', (error, stdout, stderr) => {
  if (error) {
    console.error(`exec error: ${error}`);
    return;
  }
  console.log(`stdout: ${stdout}`);
  console.error(`stderr: ${stderr}`);
});

// ExecFile - execute file directly
execFile('node', ['--version'], (error, stdout, stderr) => {
  if (error) {
    console.error(`execFile error: ${error}`);
    return;
  }
  console.log(`Node version: ${stdout}`);
});

// Fork - spawn Node.js process
const child = fork('child.js');

child.on('message', (msg) => {
  console.log('Message from child:', msg);
});

child.send({ hello: 'world' });

// Advanced spawn options
const subprocess = spawn('node', ['script.js'], {
  cwd: '/path/to/directory',
  env: { ...process.env, CUSTOM_VAR: 'value' },
  stdio: ['pipe', 'pipe', 'pipe', 'ipc'],
  detached: true,
  shell: true
});

// Detached process
subprocess.unref();

// Piping between processes
const grep = spawn('grep', ['test']);
const ps = spawn('ps', ['aux']);

ps.stdout.pipe(grep.stdin);
grep.stdout.on('data', (data) => {
  console.log(`grep result: ${data}`);
});

// Handle process errors
subprocess.on('error', (err) => {
  console.error('Failed to start subprocess:', err);
});
```

### Inter-Process Communication (IPC)

```javascript
// parent.js
const { fork } = require('child_process');
const child = fork('child.js');

// Send message to child
child.send({ type: 'start', data: 'Hello child' });

// Receive message from child
child.on('message', (msg) => {
  console.log('Parent received:', msg);
});

// child.js
process.on('message', (msg) => {
  console.log('Child received:', msg);
  
  // Send response back to parent
  process.send({ type: 'response', data: 'Hello parent' });
});

// Advanced IPC with handles
const net = require('net');
const child = fork('child.js');

const server = net.createServer();
server.listen(1337, () => {
  child.send('server', server);
});
```

## Streams

### Readable Streams

```javascript
const { Readable, Writable, Transform, pipeline } = require('stream');

// Create readable stream
class MyReadable extends Readable {
  constructor(options) {
    super(options);
    this.current = 0;
  }
  
  _read() {
    if (this.current < 5) {
      this.push(`Data ${this.current}\n`);
      this.current++;
    } else {
      this.push(null); // End stream
    }
  }
}

const readable = new MyReadable();
readable.on('data', (chunk) => {
  console.log('Received:', chunk.toString());
});

readable.on('end', () => {
  console.log('Stream ended');
});

// Reading modes
readable.pause(); // Pause reading
readable.resume(); // Resume reading

// Readable from iterable
const readableFromArray = Readable.from(['a', 'b', 'c']);

// Async iterator
async function readStream() {
  for await (const chunk of readable) {
    console.log('Chunk:', chunk);
  }
}
```

### Writable Streams

```javascript
// Create writable stream
class MyWritable extends Writable {
  _write(chunk, encoding, callback) {
    console.log('Writing:', chunk.toString());
    callback(); // Signal completion
  }
  
  _final(callback) {
    console.log('Finalizing stream');
    callback();
  }
}

const writable = new MyWritable();
writable.write('Hello ');
writable.write('World');
writable.end();

// Handle back-pressure
const writeStream = fs.createWriteStream('output.txt');
let canWrite = true;

function write() {
  let i = 0;
  while (i < 1000000 && canWrite) {
    canWrite = writeStream.write(`Line ${i}\n`);
    i++;
  }
  
  if (i < 1000000) {
    // Wait for drain event
    writeStream.once('drain', write);
  }
}

write();
```

### Transform Streams

```javascript
// Create transform stream
class UpperCaseTransform extends Transform {
  _transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback();
  }
}

const upperCase = new UpperCaseTransform();

// Pipe streams
process.stdin
  .pipe(upperCase)
  .pipe(process.stdout);

// Built-in transform streams
const zlib = require('zlib');
const gzip = zlib.createGzip();

fs.createReadStream('input.txt')
  .pipe(gzip)
  .pipe(fs.createWriteStream('output.txt.gz'));

// Pipeline with error handling
const { pipeline } = require('stream');

pipeline(
  fs.createReadStream('input.txt'),
  zlib.createGzip(),
  fs.createWriteStream('output.txt.gz'),
  (err) => {
    if (err) {
      console.error('Pipeline failed:', err);
    } else {
      console.log('Pipeline succeeded');
    }
  }
);
```

### Duplex Streams

```javascript
const { Duplex } = require('stream');

class MyDuplex extends Duplex {
  constructor(options) {
    super(options);
    this.data = [];
  }
  
  _read(size) {
    if (this.data.length) {
      this.push(this.data.shift());
    } else {
      this.push(null);
    }
  }
  
  _write(chunk, encoding, callback) {
    console.log('Received:', chunk.toString());
    this.data.push(chunk);
    callback();
  }
}

const duplex = new MyDuplex();
duplex.write('Hello');
duplex.on('data', (chunk) => {
  console.log('Read:', chunk.toString());
});
```

## Buffers

### Creating and Using Buffers

```javascript
// Create buffers
const buf1 = Buffer.alloc(10); // 10 bytes, initialized to 0
const buf2 = Buffer.allocUnsafe(10); // 10 bytes, not initialized
const buf3 = Buffer.from('Hello World'); // From string
const buf4 = Buffer.from([1, 2, 3, 4, 5]); // From array
const buf5 = Buffer.from('48656c6c6f', 'hex'); // From hex string

// Buffer operations
console.log(buf3.toString()); // Hello World
console.log(buf3.toString('hex')); // 48656c6c6f20576f726c64
console.log(buf3.toString('base64')); // SGVsbG8gV29ybGQ=

// Access buffer bytes
console.log(buf3[0]); // 72 (H)
buf3[0] = 74; // Change to J
console.log(buf3.toString()); // Jello World

// Buffer length
console.log(buf3.length); // 11
console.log(Buffer.byteLength('Hello')); // 5

// Copy buffers
const target = Buffer.alloc(5);
buf3.copy(target, 0, 0, 5);
console.log(target.toString()); // Jello

// Slice buffer (creates view, not copy)
const slice = buf3.slice(0, 5);
console.log(slice.toString()); // Jello

// Compare buffers
const buf6 = Buffer.from('Hello');
const buf7 = Buffer.from('Hello');
console.log(buf6.equals(buf7)); // true
console.log(buf6.compare(buf7)); // 0

// Concatenate buffers
const combined = Buffer.concat([buf6, buf7]);
console.log(combined.toString()); // HelloHello
```

### Buffer Encoding

```javascript
// Supported encodings
const encodings = [
  'ascii',
  'utf8',
  'utf16le',
  'ucs2',
  'base64',
  'base64url',
  'latin1',
  'binary',
  'hex'
];

const text = 'Hello World';
encodings.forEach(encoding => {
  const encoded = Buffer.from(text, 'utf8').toString(encoding);
  console.log(`${encoding}: ${encoded}`);
});

// Working with binary data
const binary = Buffer.alloc(4);
binary.writeInt32BE(1234567890, 0);
console.log(binary.readInt32BE(0)); // 1234567890

binary.writeFloatLE(3.14159, 0);
console.log(binary.readFloatLE(0)); // 3.14159

// BigInt support
const bigintBuf = Buffer.alloc(8);
bigintBuf.writeBigInt64BE(123456789012345n, 0);
console.log(bigintBuf.readBigInt64BE(0)); // 123456789012345n
```

## Events

### EventEmitter

```javascript
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}
const myEmitter = new MyEmitter();

// Add event listener
myEmitter.on('event', (arg1, arg2) => {
  console.log('Event triggered:', arg1, arg2);
});

// Add one-time listener
myEmitter.once('once-event', () => {
  console.log('This will only fire once');
});

// Emit events
myEmitter.emit('event', 'arg1', 'arg2');
myEmitter.emit('once-event');
myEmitter.emit('once-event'); // Won't fire

// Remove listener
const callback = () => console.log('Callback');
myEmitter.on('removable', callback);
myEmitter.removeListener('removable', callback);

// Remove all listeners
myEmitter.removeAllListeners('event');
myEmitter.removeAllListeners(); // Remove all

// Get listener count
console.log(myEmitter.listenerCount('event'));

// Get listeners
console.log(myEmitter.listeners('event'));

// Set max listeners
myEmitter.setMaxListeners(20);
console.log(myEmitter.getMaxListeners());

// Error handling
myEmitter.on('error', (err) => {
  console.error('Error occurred:', err);
});

// Prepend listener
myEmitter.prependListener('event', () => {
  console.log('This runs first');
});

// Async events
myEmitter.on('async-event', async () => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  console.log('Async operation completed');
});
```

### Event-Driven Architecture

```javascript
// Custom event-driven class
class DataProcessor extends EventEmitter {
  processData(data) {
    this.emit('start', data);
    
    try {
      // Simulate processing
      const result = data.toUpperCase();
      this.emit('data', result);
      this.emit('end', result);
    } catch (error) {
      this.emit('error', error);
    }
  }
}

const processor = new DataProcessor();

processor.on('start', (data) => {
  console.log('Processing started:', data);
});

processor.on('data', (data) => {
  console.log('Data processed:', data);
});

processor.on('end', (result) => {
  console.log('Processing complete:', result);
});

processor.on('error', (error) => {
  console.error('Processing error:', error);
});

processor.processData('hello world');
```

## HTTP/HTTPS

### HTTP Server

```javascript
const http = require('http');
const url = require('url');
const querystring = require('querystring');

// Basic HTTP server
const server = http.createServer((req, res) => {
  // Parse URL
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.query;
  
  // Routing
  if (pathname === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('<h1>Home Page</h1>');
  } else if (pathname === '/api/data') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ message: 'API response' }));
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});

// Handle POST requests
const postServer = http.createServer((req, res) => {
  if (req.method === 'POST') {
    let body = '';
    
    req.on('data', (chunk) => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      const parsed = querystring.parse(body);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(parsed));
    });
  }
});

// Advanced server with routing
class Router {
  constructor() {
    this.routes = {
      GET: {},
      POST: {},
      PUT: {},
      DELETE: {}
    };
  }
  
  get(path, handler) {
    this.routes.GET[path] = handler;
  }
  
  post(path, handler) {
    this.routes.POST[path] = handler;
  }
  
  handle(req, res) {
    const { pathname } = url.parse(req.url);
    const handler = this.routes[req.method][pathname];
    
    if (handler) {
      handler(req, res);
    } else {
      res.writeHead(404);
      res.end('Not Found');
    }
  }
}

const router = new Router();
router.get('/users', (req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify([{ id: 1, name: 'John' }]));
});

const routedServer = http.createServer((req, res) => {
  router.handle(req, res);
});
```

### HTTP Client

```javascript
// Making HTTP requests
const options = {
  hostname: 'api.example.com',
  port: 443,
  path: '/users',
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
};

const req = https.request(options, (res) => {
  let data = '';
  
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log(JSON.parse(data));
  });
});

req.on('error', (error) => {
  console.error(error);
});

req.end();

// POST request
const postData = JSON.stringify({ name: 'John', age: 30 });

const postOptions = {
  hostname: 'api.example.com',
  path: '/users',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

const postReq = https.request(postOptions, (res) => {
  res.on('data', (chunk) => {
    console.log(chunk.toString());
  });
});

postReq.write(postData);
postReq.end();

// Using http.get shorthand
http.get('http://api.example.com/data', (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => console.log(data));
}).on('error', console.error);
```

### HTTPS Server

```javascript
const https = require('https');
const fs = require('fs');

// HTTPS server with SSL certificates
const options = {
  key: fs.readFileSync('private-key.pem'),
  cert: fs.readFileSync('certificate.pem')
};

const httpsServer = https.createServer(options, (req, res) => {
  res.writeHead(200);
  res.end('Secure connection\n');
});

httpsServer.listen(443, () => {
  console.log('HTTPS Server running on port 443');
});

// HTTP/2 support
const http2 = require('http2');

const server = http2.createSecureServer({
  key: fs.readFileSync('private-key.pem'),
  cert: fs.readFileSync('certificate.pem')
});

server.on('error', (err) => console.error(err));

server.on('stream', (stream, headers) => {
  stream.respond({
    'content-type': 'text/html; charset=utf-8',
    ':status': 200
  });
  stream.end('<h1>Hello HTTP/2</h1>');
});

server.listen(8443);
```

## Networking

### TCP Server and Client

```javascript
const net = require('net');

// TCP Server
const server = net.createServer((socket) => {
  console.log('Client connected');
  
  socket.on('data', (data) => {
    console.log('Received:', data.toString());
    socket.write(`Echo: ${data}`);
  });
  
  socket.on('end', () => {
    console.log('Client disconnected');
  });
  
  socket.on('error', (err) => {
    console.error('Socket error:', err);
  });
});

server.listen(8080, () => {
  console.log('TCP Server listening on port 8080');
});

// TCP Client
const client = net.createConnection({ port: 8080 }, () => {
  console.log('Connected to server');
  client.write('Hello Server');
});

client.on('data', (data) => {
  console.log('Received:', data.toString());
  client.end();
});

client.on('end', () => {
  console.log('Disconnected from server');
});

// Advanced TCP options
const advancedServer = net.createServer({
  allowHalfOpen: true,
  pauseOnConnect: false
});

advancedServer.on('connection', (socket) => {
  socket.setEncoding('utf8');
  socket.setTimeout(30000); // 30 seconds timeout
  socket.setKeepAlive(true, 1000);
  socket.setNoDelay(true);
  
  socket.on('timeout', () => {
    console.log('Socket timeout');
    socket.end();
  });
});
```

### UDP (Datagram) Sockets

```javascript
const dgram = require('dgram');

// UDP Server
const udpServer = dgram.createSocket('udp4');

udpServer.on('error', (err) => {
  console.error('Server error:', err);
  udpServer.close();
});

udpServer.on('message', (msg, rinfo) => {
  console.log(`Server got: ${msg} from ${rinfo.address}:${rinfo.port}`);
  
  // Send response
  const response = Buffer.from('Message received');
  udpServer.send(response, rinfo.port, rinfo.address);
});

udpServer.on('listening', () => {
  const address = udpServer.address();
  console.log(`UDP Server listening ${address.address}:${address.port}`);
});

udpServer.bind(41234);

// UDP Client
const udpClient = dgram.createSocket('udp4');
const message = Buffer.from('Hello UDP Server');

udpClient.send(message, 41234, 'localhost', (err) => {
  if (err) console.error(err);
  udpClient.close();
});

// Multicast
const multicastServer = dgram.createSocket({ type: 'udp4', reuseAddr: true });
const MULTICAST_ADDR = '230.185.192.108';

multicastServer.bind(41234, () => {
  multicastServer.addMembership(MULTICAST_ADDR);
});

multicastServer.on('message', (msg, rinfo) => {
  console.log(`Multicast message: ${msg} from ${rinfo.address}`);
});
```

### DNS

```javascript
const dns = require('dns');
const { promisify } = require('util');

// DNS lookups
dns.lookup('example.com', (err, address, family) => {
  if (err) console.error(err);
  console.log('Address:', address);
  console.log('Family:', family);
});

// Resolve DNS records
dns.resolve4('example.com', (err, addresses) => {
  if (err) console.error(err);
  console.log('IPv4 addresses:', addresses);
});

dns.resolveMx('example.com', (err, addresses) => {
  if (err) console.error(err);
  console.log('MX records:', addresses);
});

// Promise-based DNS
const lookupAsync = promisify(dns.lookup);
const resolve4Async = promisify(dns.resolve4);

async function dnsOperations() {
  try {
    const address = await lookupAsync('example.com');
    console.log('Address:', address);
    
    const addresses = await resolve4Async('example.com');
    console.log('IPv4 addresses:', addresses);
  } catch (err) {
    console.error(err);
  }
}

// DNS Promises API
const dnsPromises = require('dns').promises;

async function modernDns() {
  try {
    const result = await dnsPromises.lookup('example.com');
    console.log(result);
    
    const records = await dnsPromises.resolveTxt('example.com');
    console.log('TXT records:', records);
  } catch (err) {
    console.error(err);
  }
}
```

## Crypto

### Hashing

```javascript
const crypto = require('crypto');

// Create hash
const hash = crypto.createHash('sha256');
hash.update('Hello World');
console.log(hash.digest('hex'));

// Hash file
const fs = require('fs');
const fileHash = crypto.createHash('sha256');
const stream = fs.createReadStream('file.txt');

stream.on('data', (data) => {
  fileHash.update(data);
});

stream.on('end', () => {
  console.log('File hash:', fileHash.digest('hex'));
});

// HMAC
const hmac = crypto.createHmac('sha256', 'secret-key');
hmac.update('Message to authenticate');
console.log('HMAC:', hmac.digest('hex'));

// Password hashing with salt
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return { salt, hash };
}

function verifyPassword(password, salt, hash) {
  const verifyHash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return hash === verifyHash;
}

// Scrypt (more secure for passwords)
crypto.scrypt('password', 'salt', 64, (err, derivedKey) => {
  if (err) throw err;
  console.log(derivedKey.toString('hex'));
});
```

### Encryption and Decryption

```javascript
// Symmetric encryption
const algorithm = 'aes-256-cbc';
const key = crypto.randomBytes(32);
const iv = crypto.randomBytes(16);

function encrypt(text) {
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

function decrypt(encrypted) {
  const decipher = crypto.createDecipheriv(algorithm, key, iv);
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

const encrypted = encrypt('Secret message');
console.log('Encrypted:', encrypted);
console.log('Decrypted:', decrypt(encrypted));

// Asymmetric encryption
const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: {
    type: 'spki',
    format: 'pem'
  },
  privateKeyEncoding: {
    type: 'pkcs8',
    format: 'pem'
  }
});

// Encrypt with public key
const encryptedData = crypto.publicEncrypt(
  publicKey,
  Buffer.from('Secret data')
);

// Decrypt with private key
const decryptedData = crypto.privateDecrypt(
  privateKey,
  encryptedData
);

console.log('Decrypted:', decryptedData.toString());

// Digital signatures
const sign = crypto.createSign('SHA256');
sign.update('Message to sign');
sign.end();
const signature = sign.sign(privateKey, 'hex');

const verify = crypto.createVerify('SHA256');
verify.update('Message to sign');
verify.end();
const isValid = verify.verify(publicKey, signature, 'hex');
console.log('Signature valid:', isValid);
```

### Random Data

```javascript
// Generate random bytes
crypto.randomBytes(32, (err, buffer) => {
  if (err) throw err;
  console.log('Random bytes:', buffer.toString('hex'));
});

// Synchronous random bytes
const randomBytes = crypto.randomBytes(16);
console.log(randomBytes.toString('hex'));

// Random integers
crypto.randomInt(0, 100, (err, n) => {
  if (err) throw err;
  console.log('Random integer:', n);
});

// UUID generation
const uuid = crypto.randomUUID();
console.log('UUID:', uuid);

// Secure random values
const array = new Uint32Array(10);
crypto.getRandomValues(array);
console.log('Random values:', array);
```

## OS Module

```javascript
const os = require('os');

// System information
console.log('Platform:', os.platform());
console.log('Architecture:', os.arch());
console.log('Hostname:', os.hostname());
console.log('OS Type:', os.type());
console.log('OS Release:', os.release());
console.log('OS Version:', os.version());

// User information
console.log('Home directory:', os.homedir());
console.log('Temp directory:', os.tmpdir());
console.log('User info:', os.userInfo());

// Memory information
console.log('Total memory:', os.totalmem() / 1024 / 1024 / 1024, 'GB');
console.log('Free memory:', os.freemem() / 1024 / 1024 / 1024, 'GB');

// CPU information
console.log('CPU cores:', os.cpus().length);
console.log('CPU info:', os.cpus()[0]);

// Network interfaces
console.log('Network interfaces:', os.networkInterfaces());

// System uptime
console.log('Uptime:', os.uptime(), 'seconds');

// Load average (Unix only)
console.log('Load average:', os.loadavg());

// End of line marker
console.log('EOL:', JSON.stringify(os.EOL));

// Get system constants
console.log('Constants:', os.constants);
```

## Cluster

```javascript
const cluster = require('cluster');
const http = require('http');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  console.log(`Master ${process.pid} is running`);
  
  // Fork workers
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  // Handle worker events
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died`);
    // Restart worker
    cluster.fork();
  });
  
  cluster.on('online', (worker) => {
    console.log(`Worker ${worker.process.pid} is online`);
  });
  
  // Send message to workers
  for (const id in cluster.workers) {
    cluster.workers[id].send('Hello from master');
  }
  
} else {
  // Worker process
  http.createServer((req, res) => {
    res.writeHead(200);
    res.end(`Worker ${process.pid} responded\n`);
  }).listen(8000);
  
  console.log(`Worker ${process.pid} started`);
  
  // Receive messages from master
  process.on('message', (msg) => {
    console.log(`Worker received: ${msg}`);
  });
}

// Advanced cluster configuration
if (cluster.isMaster) {
  // Cluster settings
  cluster.setupMaster({
    exec: 'worker.js',
    args: ['--use', 'https'],
    silent: true
  });
  
  // Custom scheduling policy
  cluster.schedulingPolicy = cluster.SCHED_RR; // Round-robin
  
  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('Master shutting down');
    for (const id in cluster.workers) {
      cluster.workers[id].disconnect();
    }
  });
}
```

## Worker Threads

```javascript
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

if (isMainThread) {
  // Main thread
  const worker = new Worker(__filename, {
    workerData: { num: 5 }
  });
  
  worker.on('message', (result) => {
    console.log('Result from worker:', result);
  });
  
  worker.on('error', (err) => {
    console.error('Worker error:', err);
  });
  
  worker.on('exit', (code) => {
    if (code !== 0) {
      console.error(`Worker stopped with exit code ${code}`);
    }
  });
  
  // Send message to worker
  worker.postMessage({ cmd: 'start' });
  
} else {
  // Worker thread
  parentPort.on('message', (msg) => {
    if (msg.cmd === 'start') {
      // Perform CPU-intensive operation
      const result = fibonacci(workerData.num);
      parentPort.postMessage(result);
    }
  });
  
  function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
  }
}

// Worker pool
class WorkerPool {
  constructor(workerScript, poolSize) {
    this.workerScript = workerScript;
    this.poolSize = poolSize;
    this.workers = [];
    this.queue = [];
    
    for (let i = 0; i < poolSize; i++) {
      this.createWorker();
    }
  }
  
  createWorker() {
    const worker = new Worker(this.workerScript);
    
    worker.on('message', (result) => {
      worker.currentResolve(result);
      worker.isBusy = false;
      this.processQueue();
    });
    
    worker.on('error', (err) => {
      worker.currentReject(err);
      worker.isBusy = false;
      this.processQueue();
    });
    
    worker.isBusy = false;
    this.workers.push(worker);
  }
  
  processQueue() {
    if (this.queue.length === 0) return;
    
    const worker = this.workers.find(w => !w.isBusy);
    if (!worker) return;
    
    const { data, resolve, reject } = this.queue.shift();
    worker.isBusy = true;
    worker.currentResolve = resolve;
    worker.currentReject = reject;
    worker.postMessage(data);
  }
  
  execute(data) {
    return new Promise((resolve, reject) => {
      this.queue.push({ data, resolve, reject });
      this.processQueue();
    });
  }
  
  terminate() {
    this.workers.forEach(worker => worker.terminate());
  }
}
```

## Timers

```javascript
// setTimeout
const timeoutId = setTimeout(() => {
  console.log('Timeout executed');
}, 1000);

// Clear timeout
clearTimeout(timeoutId);

// setInterval
const intervalId = setInterval(() => {
  console.log('Interval executed');
}, 1000);

// Clear interval after 5 seconds
setTimeout(() => {
  clearInterval(intervalId);
}, 5000);

// setImmediate
setImmediate(() => {
  console.log('Immediate executed');
});

// Process.nextTick
process.nextTick(() => {
  console.log('Next tick executed');
});

// Execution order
console.log('1. Synchronous');

process.nextTick(() => console.log('2. Next tick'));

setImmediate(() => console.log('4. Immediate'));

setTimeout(() => console.log('5. Timeout'), 0);

Promise.resolve().then(() => console.log('3. Promise'));

// Timer with ref/unref
const timer = setTimeout(() => {
  console.log('Timer executed');
}, 1000);

timer.unref(); // Allow process to exit if this is the only timer
timer.ref(); // Prevent process from exiting

// Promisified timers
const { promisify } = require('util');
const sleep = promisify(setTimeout);

async function delayedOperation() {
  console.log('Starting...');
  await sleep(2000);
  console.log('Finished after 2 seconds');
}

// Timer promises (Node.js 15+)
const timersPromises = require('timers/promises');

async function modernTimers() {
  await timersPromises.setTimeout(1000);
  console.log('After 1 second');
  
  for await (const _ of timersPromises.setInterval(1000)) {
    console.log('Every second');
    break; // Exit after first iteration
  }
}
```

## Performance

### Performance Hooks

```javascript
const { performance, PerformanceObserver } = require('perf_hooks');

// Measure execution time
const start = performance.now();
// ... some operation
const end = performance.now();
console.log(`Operation took ${end - start} milliseconds`);

// Performance marks
performance.mark('start');
// ... some operation
performance.mark('end');
performance.measure('My Operation', 'start', 'end');

const measure = performance.getEntriesByName('My Operation')[0];
console.log(`Duration: ${measure.duration}`);

// Performance observer
const obs = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  entries.forEach((entry) => {
    console.log(`${entry.name}: ${entry.duration}`);
  });
});

obs.observe({ entryTypes: ['measure'] });

// Resource timing
const resourceObs = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  entries.forEach((entry) => {
    console.log(`Resource: ${entry.name}, Duration: ${entry.duration}`);
  });
});

resourceObs.observe({ entryTypes: ['function', 'gc'] });
```

### Memory Management

```javascript
// Memory usage
const used = process.memoryUsage();
console.log('Memory usage:');
for (let key in used) {
  console.log(`${key}: ${Math.round(used[key] / 1024 / 1024 * 100) / 100} MB`);
}

// Garbage collection (requires --expose-gc flag)
if (global.gc) {
  global.gc();
  console.log('Garbage collection triggered');
}

// Monitor memory usage
setInterval(() => {
  const usage = process.memoryUsage();
  console.log(`Heap used: ${Math.round(usage.heapUsed / 1024 / 1024)} MB`);
}, 1000);

// Memory leak detection
class MemoryMonitor {
  constructor(threshold = 100) {
    this.threshold = threshold * 1024 * 1024; // Convert to bytes
    this.baseline = process.memoryUsage().heapUsed;
  }
  
  check() {
    const current = process.memoryUsage().heapUsed;
    const diff = current - this.baseline;
    
    if (diff > this.threshold) {
      console.warn(`Memory increased by ${Math.round(diff / 1024 / 1024)} MB`);
      this.baseline = current;
    }
  }
}

const monitor = new MemoryMonitor(50); // Alert on 50MB increase
setInterval(() => monitor.check(), 5000);
```

## Best Practices

### Error Handling

```javascript
// Async error handling
async function riskyOperation() {
  try {
    const result = await someAsyncOperation();
    return result;
  } catch (error) {
    console.error('Operation failed:', error);
    throw error; // Re-throw if needed
  }
}

// Promise error handling
somePromise()
  .then(result => processResult(result))
  .catch(error => handleError(error))
  .finally(() => cleanup());

// Event emitter error handling
emitter.on('error', (error) => {
  console.error('Emitter error:', error);
});

// Domain (deprecated but useful pattern)
class ErrorHandler {
  static wrap(fn) {
    return async (...args) => {
      try {
        return await fn(...args);
      } catch (error) {
        this.handleError(error);
      }
    };
  }
  
  static handleError(error) {
    console.error('Error caught:', error);
    // Log to monitoring service
    // Send alert if critical
  }
}

// Custom error classes
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

class DatabaseError extends Error {
  constructor(message, query) {
    super(message);
    this.name = 'DatabaseError';
    this.query = query;
  }
}
```

### Security Best Practices

```javascript
// Input validation
const validator = require('validator');

function validateInput(input) {
  if (!validator.isEmail(input.email)) {
    throw new ValidationError('Invalid email', 'email');
  }
  
  if (!validator.isLength(input.password, { min: 8 })) {
    throw new ValidationError('Password too short', 'password');
  }
  
  // Sanitize input
  input.name = validator.escape(input.name);
  input.description = validator.stripLow(input.description);
  
  return input;
}

// Environment variables
require('dotenv').config();

const config = {
  port: process.env.PORT || 3000,
  dbUrl: process.env.DATABASE_URL,
  apiKey: process.env.API_KEY
};

// Rate limiting
const rateLimiter = new Map();

function rateLimit(ip, maxRequests = 100, windowMs = 60000) {
  const now = Date.now();
  const userLimits = rateLimiter.get(ip) || { count: 0, resetTime: now + windowMs };
  
  if (now > userLimits.resetTime) {
    userLimits.count = 0;
    userLimits.resetTime = now + windowMs;
  }
  
  userLimits.count++;
  rateLimiter.set(ip, userLimits);
  
  return userLimits.count <= maxRequests;
}

// Secure headers
function setSecurityHeaders(res) {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000');
}
```

### Testing

```javascript
// Unit testing with assert
const assert = require('assert');

function add(a, b) {
  return a + b;
}

// Test cases
assert.strictEqual(add(2, 3), 5);
assert.strictEqual(add(-1, 1), 0);
assert.throws(() => add('a', 'b'), TypeError);

console.log('All tests passed');

// Custom test runner
class TestRunner {
  constructor() {
    this.tests = [];
  }
  
  test(name, fn) {
    this.tests.push({ name, fn });
  }
  
  async run() {
    console.log('Running tests...\n');
    let passed = 0;
    let failed = 0;
    
    for (const test of this.tests) {
      try {
        await test.fn();
        console.log(`✓ ${test.name}`);
        passed++;
      } catch (error) {
        console.log(`✗ ${test.name}`);
        console.error(`  ${error.message}`);
        failed++;
      }
    }
    
    console.log(`\nPassed: ${passed}, Failed: ${failed}`);
  }
}

const runner = new TestRunner();
runner.test('should add numbers', () => {
  assert.strictEqual(add(2, 3), 5);
});
runner.run();
```

### Debugging

```javascript
// Debug module usage
const debug = require('debug')('app:main');

debug('Application starting');
debug('Config loaded: %O', config);

// Inspector API
const inspector = require('inspector');
inspector.open(9229, 'localhost', true);

// Console methods
console.time('operation');
// ... operation
console.timeEnd('operation');

console.trace('Trace message');
console.table([{ a: 1, b: 2 }, { a: 3, b: 4 }]);

// Conditional debugging
const DEBUG = process.env.NODE_ENV !== 'production';

function debugLog(...args) {
  if (DEBUG) {
    console.log('[DEBUG]', ...args);
  }
}

// Performance profiling
if (process.env.PROFILE) {
  const profiler = require('v8-profiler-next');
  profiler.startProfiling('app');
  
  process.on('SIGINT', () => {
    const profile = profiler.stopProfiling('app');
    profile.export((error, result) => {
      fs.writeFileSync('profile.cpuprofile', result);
      profile.delete();
      process.exit();
    });
  });
}
```

## Conclusion

This comprehensive Node.js documentation covers the essential modules, patterns, and best practices for building robust server-side applications. From file system operations to networking, from process management to performance optimization, these examples provide a solid foundation for Node.js development. Remember to always consider security, error handling, and performance in your applications, and stay updated with the latest Node.js features and best practices.