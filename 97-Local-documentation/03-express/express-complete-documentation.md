# Express.js Complete Documentation

## Table of Contents
1. [Getting Started](#getting-started)
2. [Application](#application)
3. [Request Object](#request-object)
4. [Response Object](#response-object)
5. [Routing](#routing)
6. [Middleware](#middleware)
7. [Error Handling](#error-handling)
8. [Template Engines](#template-engines)
9. [Static Files](#static-files)
10. [Security](#security)
11. [Database Integration](#database-integration)
12. [Authentication](#authentication)
13. [Sessions and Cookies](#sessions-and-cookies)
14. [File Uploads](#file-uploads)
15. [WebSockets](#websockets)
16. [Testing](#testing)
17. [Performance](#performance)
18. [Deployment](#deployment)
19. [Best Practices](#best-practices)

## Getting Started

### Installation and Basic Setup

```javascript
// Install Express
// npm install express

const express = require('express');
const app = express();
const port = 3000;

// Basic route
app.get('/', (req, res) => {
  res.send('Hello World!');
});

// Start server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
```

### Express Application Generator

```bash
# Install generator globally
npm install -g express-generator

# Create app with view engine
express --view=ejs myapp

# Create API-only app
express --no-view --git myapi

# Install dependencies
cd myapp
npm install
npm start
```

### ES6 Modules Support

```javascript
// package.json
{
  "type": "module"
}

// app.mjs
import express from 'express';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
```

## Application

### Application Settings

```javascript
const app = express();

// Set application settings
app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.set('json spaces', 2); // Pretty JSON
app.set('case sensitive routing', true);
app.set('strict routing', true);
app.set('x-powered-by', false); // Security
app.set('trust proxy', true); // Behind proxy

// Get settings
const port = app.get('port');
const env = app.get('env'); // development/production

// Enable/disable settings
app.enable('trust proxy');
app.disable('x-powered-by');

// Check if enabled
if (app.enabled('trust proxy')) {
  console.log('Proxy trusted');
}
```

### Application Methods

```javascript
// Mount middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// HTTP methods
app.get('/', handler);
app.post('/', handler);
app.put('/', handler);
app.delete('/', handler);
app.patch('/', handler);
app.options('/', handler);
app.head('/', handler);

// All methods
app.all('*', handler);

// Route method
app.route('/users')
  .get((req, res) => res.send('GET users'))
  .post((req, res) => res.send('POST user'))
  .put((req, res) => res.send('PUT user'));

// Path patterns
app.get('/ab?cd', handler); // abcd, acd
app.get('/ab+cd', handler); // abcd, abbcd, abbbcd
app.get('/ab*cd', handler); // abcd, abxcd, abRANDOMcd
app.get('/ab(cd)?e', handler); // abe, abcde
app.get(/.*fly$/, handler); // butterfly, dragonfly

// Parameters
app.param('id', (req, res, next, id) => {
  // Parameter middleware
  User.findById(id, (err, user) => {
    if (err) return next(err);
    if (!user) return res.status(404).send('User not found');
    req.user = user;
    next();
  });
});

// Locals
app.locals.title = 'My App';
app.locals.email = 'admin@example.com';
app.locals.helpers = {
  formatDate: (date) => new Date(date).toLocaleDateString()
};
```

### Sub-applications

```javascript
// admin.js - sub-application
const admin = express();

admin.get('/', (req, res) => {
  res.send('Admin Homepage');
});

admin.get('/users', (req, res) => {
  res.send('Admin Users');
});

// Main app
const app = express();
app.use('/admin', admin);

// Multiple sub-apps
const api = express();
const blog = express();

app.use('/api', api);
app.use('/blog', blog);

// Sub-app events
admin.on('mount', (parent) => {
  console.log('Admin mounted on', admin.mountpath);
});
```

## Request Object

### Request Properties

```javascript
app.get('/users/:id', (req, res) => {
  // URL properties
  console.log(req.baseUrl);      // /users
  console.log(req.originalUrl);  // /users/123?sort=name
  console.log(req.url);          // /123?sort=name
  console.log(req.path);         // /123
  console.log(req.hostname);     // example.com
  console.log(req.protocol);     // http or https
  console.log(req.secure);       // true if https
  console.log(req.subdomains);   // ['api'] for api.example.com
  
  // Parameters
  console.log(req.params);       // { id: '123' }
  console.log(req.query);        // { sort: 'name' }
  console.log(req.body);         // POST data (needs body parser)
  
  // Headers
  console.log(req.headers);      // All headers
  console.log(req.get('Content-Type')); // Specific header
  console.log(req.accepts('html'));     // Content negotiation
  console.log(req.acceptsCharsets('utf-8'));
  console.log(req.acceptsEncodings('gzip'));
  console.log(req.acceptsLanguages('en'));
  
  // Request info
  console.log(req.method);       // GET, POST, etc.
  console.log(req.xhr);          // true if AJAX
  console.log(req.ip);           // Client IP
  console.log(req.ips);          // IP array (if trust proxy)
  console.log(req.fresh);        // Cache fresh
  console.log(req.stale);        // Cache stale
  
  // Cookies
  console.log(req.cookies);      // { name: 'value' }
  console.log(req.signedCookies); // Signed cookies
  
  // App reference
  console.log(req.app);          // Express app instance
});
```

### Request Methods

```javascript
// Get header value
const userAgent = req.get('User-Agent');
const contentType = req.header('Content-Type');

// Check content type
if (req.is('json')) {
  // Request has JSON content
}
if (req.is('html')) {
  // Request wants HTML
}

// Parameter helper
// Checks params, query, body in order
const id = req.param('id');

// Range header parsing
const range = req.range(1000); // File size
// Returns array of ranges or -1 (unsatisfiable) or -2 (malformed)

// Content negotiation
const type = req.accepts(['html', 'json']);
const charset = req.acceptsCharsets(['utf-8', 'iso-8859-1']);
const encoding = req.acceptsEncodings(['gzip', 'deflate']);
const language = req.acceptsLanguages(['en', 'es']);
```

## Response Object

### Response Methods

```javascript
// Sending responses
res.send('HTML string');
res.send({ user: 'john' }); // JSON
res.send(Buffer.from('buffer'));
res.send('<p>HTML</p>');
res.send(404, 'Not found'); // Deprecated
res.status(404).send('Not found'); // Preferred

// JSON responses
res.json({ user: 'john' });
res.status(201).json({ id: 123 });
res.jsonp({ user: 'john' }); // JSONP

// Send file
res.sendFile('/absolute/path/to/file.html');
res.sendFile('file.html', { root: __dirname });
res.sendFile('file.html', (err) => {
  if (err) next(err);
});

// Download file
res.download('/path/to/file.pdf');
res.download('/path/to/file.pdf', 'custom-name.pdf');
res.download('/path/to/file.pdf', 'custom.pdf', (err) => {
  if (err) {
    // Handle error
  }
});

// Streaming
const readStream = fs.createReadStream('large-file.zip');
readStream.pipe(res);

// Redirect
res.redirect('/new-location');
res.redirect(301, '/permanent-new-location');
res.redirect('back'); // Redirect to referrer
res.redirect('http://example.com');

// Render template
res.render('index', { title: 'Home' });
res.render('user', { user }, (err, html) => {
  if (err) return next(err);
  res.send(html);
});

// End response
res.end();
res.status(204).end();
```

### Response Headers

```javascript
// Set headers
res.set('Content-Type', 'text/html');
res.set({
  'Content-Type': 'text/plain',
  'Content-Length': '123',
  'ETag': '12345'
});

res.header('X-Custom', 'value'); // Alias for set

// Get header
const contentType = res.get('Content-Type');

// Type shorthand
res.type('html');        // Content-Type: text/html
res.type('json');        // Content-Type: application/json
res.type('application/xml');
res.type('.html');       // Content-Type: text/html
res.type('png');         // Content-Type: image/png

// Status
res.status(404);
res.sendStatus(200);     // res.status(200).send('OK')
res.sendStatus(404);     // res.status(404).send('Not Found')

// Links header
res.links({
  next: 'http://api.example.com/users?page=2',
  last: 'http://api.example.com/users?page=5'
});

// Location header
res.location('/new-path');

// Vary header
res.vary('Accept');
res.vary('Accept-Encoding');

// Attachment header
res.attachment(); // Content-Disposition: attachment
res.attachment('file.pdf'); // With filename

// Append header
res.append('Set-Cookie', 'foo=bar; Path=/');
res.append('Warning', '199 Miscellaneous warning');
```

### Cookies and Sessions

```javascript
// Set cookie
res.cookie('name', 'value');
res.cookie('name', 'value', { 
  domain: '.example.com',
  path: '/admin',
  secure: true,
  httpOnly: true,
  maxAge: 900000,
  expires: new Date(Date.now() + 900000),
  sameSite: 'strict'
});

// Signed cookie
res.cookie('name', 'value', { signed: true });

// JSON cookie
res.cookie('cart', { items: [1, 2, 3] });

// Clear cookie
res.clearCookie('name');
res.clearCookie('name', { path: '/admin' });

// Session usage (requires express-session)
const session = require('express-session');
app.use(session({
  secret: 'keyboard cat',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: true }
}));

app.get('/', (req, res) => {
  req.session.views = (req.session.views || 0) + 1;
  res.send(`Views: ${req.session.views}`);
});

// Destroy session
req.session.destroy((err) => {
  // Session destroyed
});
```

### Content Negotiation

```javascript
// Format response based on Accept header
res.format({
  'text/plain': () => {
    res.send('hey');
  },
  'text/html': () => {
    res.send('<p>hey</p>');
  },
  'application/json': () => {
    res.send({ message: 'hey' });
  },
  default: () => {
    res.status(406).send('Not Acceptable');
  }
});

// Simplified format
res.format({
  html: () => res.render('user', { user }),
  json: () => res.json(user),
  default: () => res.status(406).send('Not Acceptable')
});
```

## Routing

### Basic Routing

```javascript
// Simple routes
app.get('/', (req, res) => {
  res.send('GET request to homepage');
});

app.post('/users', (req, res) => {
  res.send('POST request to /users');
});

app.put('/users/:id', (req, res) => {
  res.send(`PUT request to /users/${req.params.id}`);
});

app.delete('/users/:id', (req, res) => {
  res.send(`DELETE request to /users/${req.params.id}`);
});

// Route parameters
app.get('/users/:userId/posts/:postId', (req, res) => {
  res.json({
    userId: req.params.userId,
    postId: req.params.postId
  });
});

// Optional parameters
app.get('/posts/:id?', (req, res) => {
  if (req.params.id) {
    res.send(`Post ${req.params.id}`);
  } else {
    res.send('All posts');
  }
});

// Wildcard
app.get('/files/*', (req, res) => {
  res.send(`File path: ${req.params[0]}`);
});

// Regular expressions
app.get(/.*fly$/, (req, res) => {
  res.send('Ends with fly');
});

app.get(/a/, (req, res) => {
  res.send('Contains letter a');
});

// Named regex groups
app.get(/^\/commits\/(\w+)(?:\.\.(\w+))?$/, (req, res) => {
  const from = req.params[0];
  const to = req.params[1] || 'HEAD';
  res.send(`Commits from ${from} to ${to}`);
});
```

### Express Router

```javascript
// routes/users.js
const express = require('express');
const router = express.Router();

// Middleware specific to this router
router.use((req, res, next) => {
  console.log('Time:', Date.now());
  next();
});

// Routes
router.get('/', (req, res) => {
  res.send('Users home');
});

router.get('/:id', (req, res) => {
  res.send(`User ${req.params.id}`);
});

router.post('/', (req, res) => {
  res.send('Create user');
});

// Export router
module.exports = router;

// main app.js
const usersRouter = require('./routes/users');
app.use('/users', usersRouter);

// Router with options
const router = express.Router({
  caseSensitive: true,  // /Foo and /foo are different
  mergeParams: true,     // Access params from parent router
  strict: true           // /foo and /foo/ are different
});

// Nested routers
const adminRouter = express.Router();
const userRouter = express.Router({ mergeParams: true });

adminRouter.use('/users/:userId', userRouter);
userRouter.get('/profile', (req, res) => {
  // Can access req.params.userId from parent
  res.send(`Admin viewing user ${req.params.userId} profile`);
});

app.use('/admin', adminRouter);
```

### Route Patterns and Groups

```javascript
// Route chaining
app.route('/users')
  .get((req, res) => {
    res.send('Get all users');
  })
  .post((req, res) => {
    res.send('Create user');
  })
  .put((req, res) => {
    res.send('Update all users');
  });

// Route group with common middleware
const authMiddleware = (req, res, next) => {
  // Check authentication
  next();
};

const adminRoutes = express.Router();
adminRoutes.use(authMiddleware);
adminRoutes.get('/dashboard', handler);
adminRoutes.get('/settings', handler);
adminRoutes.get('/users', handler);

app.use('/admin', adminRoutes);

// Dynamic route loading
const fs = require('fs');
const routesDir = './routes';

fs.readdirSync(routesDir).forEach(file => {
  if (file.endsWith('.js')) {
    const route = require(`${routesDir}/${file}`);
    const routeName = file.replace('.js', '');
    app.use(`/${routeName}`, route);
  }
});

// Versioned API routes
const v1Routes = require('./routes/v1');
const v2Routes = require('./routes/v2');

app.use('/api/v1', v1Routes);
app.use('/api/v2', v2Routes);
```

### Route Organization

```javascript
// Advanced route organization
class RouteManager {
  constructor(app) {
    this.app = app;
    this.routes = new Map();
  }
  
  register(method, path, ...handlers) {
    const key = `${method} ${path}`;
    this.routes.set(key, handlers);
    this.app[method.toLowerCase()](path, ...handlers);
  }
  
  group(prefix, callback) {
    const router = express.Router();
    const originalRegister = this.register.bind(this);
    
    this.register = (method, path, ...handlers) => {
      router[method.toLowerCase()](path, ...handlers);
      this.routes.set(`${method} ${prefix}${path}`, handlers);
    };
    
    callback();
    this.register = originalRegister;
    this.app.use(prefix, router);
  }
  
  middleware(middleware, routes) {
    routes.forEach(route => {
      const [method, path] = route.split(' ');
      const handlers = this.routes.get(route);
      if (handlers) {
        handlers.unshift(middleware);
      }
    });
  }
}

const routes = new RouteManager(app);

routes.register('GET', '/', homeController.index);
routes.register('GET', '/about', aboutController.index);

routes.group('/api', () => {
  routes.register('GET', '/users', userController.index);
  routes.register('POST', '/users', userController.create);
});
```

## Middleware

### Built-in Middleware

```javascript
// JSON body parser
app.use(express.json({
  limit: '10mb',
  strict: true,
  type: 'application/json'
}));

// URL-encoded body parser
app.use(express.urlencoded({
  extended: true,  // Use qs library
  limit: '10mb',
  parameterLimit: 10000,
  type: 'application/x-www-form-urlencoded'
}));

// Static files
app.use(express.static('public'));
app.use(express.static('public', {
  dotfiles: 'ignore',
  etag: true,
  extensions: ['htm', 'html'],
  index: 'index.html',
  maxAge: '1d',
  redirect: true,
  setHeaders: (res, path, stat) => {
    res.set('X-Timestamp', Date.now());
  }
}));

// Multiple static directories
app.use(express.static('public'));
app.use(express.static('uploads'));
app.use('/static', express.static('public'));

// Raw body
app.use(express.raw({
  type: 'application/octet-stream',
  limit: '10mb'
}));

// Text body
app.use(express.text({
  type: 'text/plain',
  limit: '10kb'
}));
```

### Custom Middleware

```javascript
// Simple middleware
const myMiddleware = (req, res, next) => {
  console.log('Middleware executed');
  req.customProperty = 'value';
  next(); // Pass control to next middleware
};

app.use(myMiddleware);

// Async middleware
const asyncMiddleware = async (req, res, next) => {
  try {
    const data = await someAsyncOperation();
    req.data = data;
    next();
  } catch (error) {
    next(error); // Pass error to error handler
  }
};

// Conditional middleware
const conditionalMiddleware = (req, res, next) => {
  if (req.headers['x-custom-header']) {
    // Do something
    next();
  } else {
    res.status(400).send('Missing header');
  }
};

// Middleware factory
const createLoggerMiddleware = (options = {}) => {
  const { prefix = 'LOG' } = options;
  
  return (req, res, next) => {
    console.log(`[${prefix}] ${req.method} ${req.path}`);
    next();
  };
};

app.use(createLoggerMiddleware({ prefix: 'API' }));

// Middleware with cleanup
const resourceMiddleware = (req, res, next) => {
  // Allocate resource
  const resource = allocateResource();
  req.resource = resource;
  
  // Cleanup on response finish
  res.on('finish', () => {
    resource.cleanup();
  });
  
  next();
};
```

### Third-party Middleware

```javascript
// Morgan - Logging
const morgan = require('morgan');
app.use(morgan('combined'));
app.use(morgan('dev'));
app.use(morgan(':method :url :status :response-time ms'));

// Custom morgan tokens
morgan.token('user', (req) => req.user?.id || 'anonymous');
app.use(morgan(':user :method :url :status'));

// Cors
const cors = require('cors');
app.use(cors());
app.use(cors({
  origin: 'https://example.com',
  credentials: true,
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Helmet - Security headers
const helmet = require('helmet');
app.use(helmet());
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"]
    }
  }
}));

// Compression
const compression = require('compression');
app.use(compression());
app.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  },
  level: 6
}));

// Cookie parser
const cookieParser = require('cookie-parser');
app.use(cookieParser()); // Unsigned cookies
app.use(cookieParser('secret')); // Signed cookies

// Method override
const methodOverride = require('method-override');
app.use(methodOverride('_method'));
app.use(methodOverride('X-HTTP-Method-Override'));
app.use(methodOverride((req, res) => {
  if (req.body && typeof req.body === 'object' && '_method' in req.body) {
    const method = req.body._method;
    delete req.body._method;
    return method;
  }
}));
```

### Middleware Patterns

```javascript
// Rate limiting
const rateLimit = require('express-rate-limit');
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests',
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api', limiter);

// Custom rate limiter
const customRateLimiter = (maxRequests = 100, windowMs = 60000) => {
  const requests = new Map();
  
  return (req, res, next) => {
    const key = req.ip;
    const now = Date.now();
    const windowStart = now - windowMs;
    
    if (!requests.has(key)) {
      requests.set(key, []);
    }
    
    const userRequests = requests.get(key).filter(time => time > windowStart);
    
    if (userRequests.length >= maxRequests) {
      return res.status(429).send('Too many requests');
    }
    
    userRequests.push(now);
    requests.set(key, userRequests);
    next();
  };
};

// Request ID middleware
const { v4: uuidv4 } = require('uuid');

const requestId = (req, res, next) => {
  req.id = req.headers['x-request-id'] || uuidv4();
  res.setHeader('X-Request-Id', req.id);
  next();
};

// Timing middleware
const timing = (req, res, next) => {
  const start = process.hrtime();
  
  res.on('finish', () => {
    const [seconds, nanoseconds] = process.hrtime(start);
    const duration = seconds * 1000 + nanoseconds / 1000000;
    console.log(`${req.method} ${req.path} - ${duration.toFixed(2)}ms`);
  });
  
  next();
};
```

## Error Handling

### Error Middleware

```javascript
// Basic error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// Detailed error handler
app.use((err, req, res, next) => {
  // Set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};
  
  // Render error page
  res.status(err.status || 500);
  res.render('error');
});

// Multiple error handlers
const logErrors = (err, req, res, next) => {
  console.error(err.stack);
  next(err);
};

const clientErrorHandler = (err, req, res, next) => {
  if (req.xhr) {
    res.status(500).send({ error: 'Something failed!' });
  } else {
    next(err);
  }
};

const errorHandler = (err, req, res, next) => {
  res.status(500);
  res.render('error', { error: err });
};

app.use(logErrors);
app.use(clientErrorHandler);
app.use(errorHandler);

// Custom error classes
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.status = 400;
    this.field = field;
  }
}

class AuthorizationError extends Error {
  constructor(message = 'Unauthorized') {
    super(message);
    this.name = 'AuthorizationError';
    this.status = 403;
  }
}

// Using custom errors
app.post('/users', async (req, res, next) => {
  try {
    if (!req.body.email) {
      throw new ValidationError('Email is required', 'email');
    }
    // Process request
  } catch (error) {
    next(error);
  }
});

// Error handler for custom errors
app.use((err, req, res, next) => {
  if (err instanceof ValidationError) {
    return res.status(err.status).json({
      error: err.message,
      field: err.field
    });
  }
  
  if (err instanceof AuthorizationError) {
    return res.status(err.status).json({
      error: err.message
    });
  }
  
  // Default error
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});
```

### Async Error Handling

```javascript
// Async route handler wrapper
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

app.get('/users', asyncHandler(async (req, res) => {
  const users = await User.findAll();
  res.json(users);
}));

// Express 5.x native async support
app.get('/users', async (req, res, next) => {
  try {
    const users = await User.findAll();
    res.json(users);
  } catch (error) {
    next(error);
  }
});

// Global async error handler
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Application specific logging, throwing an error, or other logic here
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  // Clean up and exit
  process.exit(1);
});

// Timeout handling
const timeout = (ms) => {
  return (req, res, next) => {
    const timer = setTimeout(() => {
      const err = new Error('Request timeout');
      err.status = 408;
      next(err);
    }, ms);
    
    res.on('finish', () => clearTimeout(timer));
    next();
  };
};

app.use(timeout(30000)); // 30 second timeout
```

## Template Engines

### EJS (Embedded JavaScript)

```javascript
// Setup EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Render EJS template
app.get('/', (req, res) => {
  res.render('index', {
    title: 'Home',
    user: { name: 'John', age: 30 },
    items: ['Apple', 'Banana', 'Orange']
  });
});

// views/index.ejs
`
<!DOCTYPE html>
<html>
<head>
  <title><%= title %></title>
</head>
<body>
  <h1>Welcome <%= user.name %></h1>
  <% if (user.age >= 18) { %>
    <p>You are an adult</p>
  <% } %>
  
  <ul>
    <% items.forEach(item => { %>
      <li><%= item %></li>
    <% }) %>
  </ul>
  
  <%- include('partials/footer') %>
</body>
</html>
`;
```

### Pug (formerly Jade)

```javascript
// Setup Pug
app.set('view engine', 'pug');
app.set('views', './views');

// Render Pug template
app.get('/', (req, res) => {
  res.render('index', {
    title: 'Home',
    message: 'Hello Pug!'
  });
});

// views/index.pug
`
doctype html
html
  head
    title= title
  body
    h1= message
    .container
      if user
        p Welcome #{user.name}
      else
        p Please log in
    
    ul
      each item in items
        li= item
    
    include partials/footer
`;
```

### Handlebars

```javascript
// Setup Handlebars
const exphbs = require('express-handlebars');

app.engine('handlebars', exphbs({
  defaultLayout: 'main',
  helpers: {
    formatDate: (date) => new Date(date).toLocaleDateString(),
    ifEquals: (a, b, options) => {
      return a === b ? options.fn(this) : options.inverse(this);
    }
  }
}));
app.set('view engine', 'handlebars');

// Render Handlebars template
app.get('/', (req, res) => {
  res.render('home', {
    title: 'Home',
    users: [
      { name: 'John', active: true },
      { name: 'Jane', active: false }
    ]
  });
});

// views/home.handlebars
`
<h1>{{title}}</h1>
<ul>
  {{#each users}}
    <li>
      {{name}}
      {{#if active}}
        <span>Active</span>
      {{else}}
        <span>Inactive</span>
      {{/if}}
    </li>
  {{/each}}
</ul>
`;
```

## Security

### Security Best Practices

```javascript
// Helmet for security headers
const helmet = require('helmet');
app.use(helmet());

// Custom security headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000');
  next();
});

// CSRF protection
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/form', csrfProtection, (req, res) => {
  res.send('Form processed');
});

// Input validation
const { body, validationResult } = require('express-validator');

app.post('/user',
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }),
  body('age').isInt({ min: 0, max: 120 }),
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    // Process valid input
  }
);

// SQL injection prevention
const mysql = require('mysql2');
const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  database: 'test'
});

// Safe query with placeholders
app.get('/user/:id', (req, res) => {
  const userId = req.params.id;
  connection.execute(
    'SELECT * FROM users WHERE id = ?',
    [userId],
    (err, results) => {
      if (err) return res.status(500).send(err);
      res.json(results);
    }
  );
});

// XSS prevention
const xss = require('xss');

app.post('/comment', (req, res) => {
  const sanitizedComment = xss(req.body.comment);
  // Save sanitized comment
});

// Rate limiting for brute force protection
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  skipSuccessfulRequests: true
});

app.post('/login', loginLimiter, (req, res) => {
  // Login logic
});
```

### Authentication

```javascript
// Basic authentication
const basicAuth = require('express-basic-auth');

app.use(basicAuth({
  users: { 'admin': 'supersecret' },
  challenge: true,
  unauthorizedResponse: 'Unauthorized'
}));

// JWT authentication
const jwt = require('jsonwebtoken');

// Generate token
app.post('/login', async (req, res) => {
  // Validate credentials
  const user = await validateUser(req.body.email, req.body.password);
  
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  const token = jwt.sign(
    { id: user.id, email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: '1h' }
  );
  
  res.json({ token });
});

// Verify token middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.sendStatus(401);
  }
  
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

app.get('/protected', authenticateToken, (req, res) => {
  res.json({ message: 'Access granted', user: req.user });
});

// Passport.js integration
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;

passport.use(new LocalStrategy(
  async (username, password, done) => {
    try {
      const user = await User.findOne({ username });
      if (!user) {
        return done(null, false, { message: 'Incorrect username.' });
      }
      if (!user.validPassword(password)) {
        return done(null, false, { message: 'Incorrect password.' });
      }
      return done(null, user);
    } catch (err) {
      return done(err);
    }
  }
));

passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser(async (id, done) => {
  try {
    const user = await User.findById(id);
    done(null, user);
  } catch (err) {
    done(err);
  }
});

app.use(passport.initialize());
app.use(passport.session());

app.post('/login',
  passport.authenticate('local', {
    successRedirect: '/dashboard',
    failureRedirect: '/login',
    failureFlash: true
  })
);
```

## Testing

### Unit Testing with Jest

```javascript
// app.js
const express = require('express');
const app = express();

app.get('/users', (req, res) => {
  res.json([{ id: 1, name: 'John' }]);
});

module.exports = app;

// app.test.js
const request = require('supertest');
const app = require('./app');

describe('GET /users', () => {
  test('responds with json', async () => {
    const response = await request(app)
      .get('/users')
      .expect('Content-Type', /json/)
      .expect(200);
    
    expect(response.body).toEqual([
      { id: 1, name: 'John' }
    ]);
  });
});

// Testing middleware
const authMiddleware = require('./authMiddleware');

describe('Auth Middleware', () => {
  test('allows authenticated requests', () => {
    const req = {
      headers: { authorization: 'Bearer valid-token' }
    };
    const res = {};
    const next = jest.fn();
    
    authMiddleware(req, res, next);
    expect(next).toHaveBeenCalled();
  });
  
  test('blocks unauthenticated requests', () => {
    const req = { headers: {} };
    const res = {
      status: jest.fn(() => res),
      send: jest.fn()
    };
    const next = jest.fn();
    
    authMiddleware(req, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });
});
```

### Integration Testing

```javascript
// Integration test setup
const request = require('supertest');
const app = require('../app');
const db = require('../db');

beforeAll(async () => {
  await db.connect();
});

afterAll(async () => {
  await db.disconnect();
});

beforeEach(async () => {
  await db.clear();
  await db.seed();
});

describe('User API', () => {
  test('GET /api/users returns all users', async () => {
    const res = await request(app)
      .get('/api/users')
      .expect(200);
    
    expect(res.body).toHaveLength(3);
    expect(res.body[0]).toHaveProperty('id');
    expect(res.body[0]).toHaveProperty('name');
  });
  
  test('POST /api/users creates new user', async () => {
    const newUser = { name: 'Jane', email: 'jane@example.com' };
    
    const res = await request(app)
      .post('/api/users')
      .send(newUser)
      .expect(201);
    
    expect(res.body).toMatchObject(newUser);
    expect(res.body).toHaveProperty('id');
  });
  
  test('PUT /api/users/:id updates user', async () => {
    const updates = { name: 'Updated Name' };
    
    const res = await request(app)
      .put('/api/users/1')
      .send(updates)
      .expect(200);
    
    expect(res.body.name).toBe('Updated Name');
  });
  
  test('DELETE /api/users/:id deletes user', async () => {
    await request(app)
      .delete('/api/users/1')
      .expect(204);
    
    const res = await request(app)
      .get('/api/users/1')
      .expect(404);
  });
});
```

## Best Practices

### Project Structure

```
express-app/
├── src/
│   ├── controllers/
│   │   ├── userController.js
│   │   └── authController.js
│   ├── models/
│   │   └── User.js
│   ├── routes/
│   │   ├── index.js
│   │   ├── users.js
│   │   └── auth.js
│   ├── middleware/
│   │   ├── auth.js
│   │   ├── errorHandler.js
│   │   └── validation.js
│   ├── services/
│   │   ├── userService.js
│   │   └── emailService.js
│   ├── utils/
│   │   ├── logger.js
│   │   └── database.js
│   └── app.js
├── config/
│   ├── default.json
│   ├── production.json
│   └── test.json
├── public/
│   ├── css/
│   ├── js/
│   └── images/
├── views/
│   ├── layouts/
│   ├── partials/
│   └── pages/
├── tests/
│   ├── unit/
│   └── integration/
├── .env
├── .gitignore
├── package.json
└── server.js
```

### Environment Configuration

```javascript
// Using dotenv
require('dotenv').config();

// config/index.js
module.exports = {
  port: process.env.PORT || 3000,
  database: {
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'myapp'
  },
  jwt: {
    secret: process.env.JWT_SECRET || 'default-secret',
    expiresIn: process.env.JWT_EXPIRES_IN || '1h'
  },
  email: {
    host: process.env.EMAIL_HOST,
    port: process.env.EMAIL_PORT,
    user: process.env.EMAIL_USER,
    password: process.env.EMAIL_PASSWORD
  }
};

// Using config package
const config = require('config');
const dbConfig = config.get('database');
const serverConfig = config.get('server');
```

### Performance Optimization

```javascript
// Caching
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 600 }); // 10 minutes

const cacheMiddleware = (duration) => {
  return (req, res, next) => {
    const key = req.originalUrl || req.url;
    const cached = cache.get(key);
    
    if (cached) {
      return res.json(cached);
    }
    
    res.sendResponse = res.json;
    res.json = (body) => {
      cache.set(key, body, duration);
      res.sendResponse(body);
    };
    next();
  };
};

app.get('/api/data', cacheMiddleware(300), (req, res) => {
  // Expensive operation
  const data = fetchExpensiveData();
  res.json(data);
});

// Connection pooling
const mysql = require('mysql2');
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  database: 'test',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// Async parallel processing
app.get('/dashboard', async (req, res) => {
  const [users, posts, comments] = await Promise.all([
    User.findAll(),
    Post.findRecent(),
    Comment.findPopular()
  ]);
  
  res.render('dashboard', { users, posts, comments });
});

// Response compression
const compression = require('compression');
app.use(compression({
  level: 6,
  threshold: 100 * 1000, // 100kb
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  }
}));
```

## Conclusion

This comprehensive Express.js documentation covers all essential aspects of building web applications with Express. From basic routing to advanced security implementations, from middleware patterns to performance optimization, these examples provide a complete reference for Express.js development. Remember to always consider security, follow best practices, and optimize for performance in production applications.