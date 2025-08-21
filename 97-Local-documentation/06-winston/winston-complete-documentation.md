# Winston.js Complete Documentation

A comprehensive guide to Winston.js, the versatile logging library for Node.js applications. Winston is designed to be simple and universal with support for multiple transports and flexible log formatting.

## Table of Contents

1. [Installation and Basic Setup](#installation-and-basic-setup)
2. [Core Concepts](#core-concepts)
3. [Logger Configuration](#logger-configuration)
4. [Logging Levels](#logging-levels)
5. [Formats and Formatting](#formats-and-formatting)
6. [Core Transports](#core-transports)
7. [Cloud and Database Transports](#cloud-and-database-transports)
8. [Monitoring and Analytics Transports](#monitoring-and-analytics-transports)
9. [Communication Transports](#communication-transports)
10. [Specialized Transports](#specialized-transports)
11. [Exception and Rejection Handling](#exception-and-rejection-handling)
12. [Multiple Loggers and Containers](#multiple-loggers-and-containers)
13. [Child Loggers](#child-loggers)
14. [Profiling and Performance](#profiling-and-performance)
15. [Querying Logs](#querying-logs)
16. [Streaming Logs](#streaming-logs)
17. [Custom Formats](#custom-formats)
18. [Custom Transports](#custom-transports)
19. [Best Practices](#best-practices)
20. [Production Setup Examples](#production-setup-examples)
21. [Migration Guide (v2 to v3)](#migration-guide-v2-to-v3)
22. [Troubleshooting](#troubleshooting)

---

## Installation and Basic Setup

### Installation

Winston can be installed via npm or yarn:

```bash
# Using npm
npm install winston

# Using yarn
yarn add winston
```

### Quick Start

The simplest way to get started with Winston:

```javascript
const winston = require('winston');

// Create a basic logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Add console transport for non-production environments
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

// Use the logger
logger.info('Hello, Winston!');
logger.error('This is an error message');
```

### Using the Default Logger

Winston provides a default logger that can be used directly:

```javascript
const winston = require('winston');

// Log directly using the default logger
winston.log('info', 'Hello distributed log files!');
winston.info('Hello again distributed logs');

// Change the global log level
winston.level = 'debug';
winston.log('debug', 'Now my debug messages are written to console!');
```

---

## Core Concepts

### The Info Object

Every log message in Winston is represented as an `info` object:

```javascript
const info = {
  level: 'info',                 // Level of the logging message
  message: 'Hey! Log something?' // Descriptive message being logged.
};
```

You can destructure the info object to separate core properties from metadata:

```javascript
const { level, message, ...meta } = info;
```

### Triple-Beam Symbols

Winston uses Symbol properties from the `triple-beam` package to manage internal state:

```javascript
const { LEVEL, MESSAGE, SPLAT } = require('triple-beam');

console.log(LEVEL === Symbol.for('level'));   // true
console.log(MESSAGE === Symbol.for('message')); // true
console.log(SPLAT === Symbol.for('splat'));   // true
```

---

## Logger Configuration

### Configuration Parameters

When creating a logger with `winston.createLogger()`, you can specify these parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `level` | `'info'` | Log only if `info.level` is less than or equal to this level |
| `levels` | `winston.config.npm.levels` | Levels (and colors) representing log priorities |
| `format` | `winston.format.json` | Formatting for `info` messages |
| `transports` | `[]` | Set of logging targets for `info` messages |
| `exitOnError` | `true` | If false, handled exceptions will not cause `process.exit` |
| `silent` | `false` | If true, all logs are suppressed |

### Basic Logger Creation

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

### Reconfiguring Loggers

You can completely reconfigure an existing logger:

```javascript
const logger = winston.createLogger({
  level: 'info',
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Replaces the previous transports with those in the new configuration
const DailyRotateFile = require('winston-daily-rotate-file');
logger.configure({
  level: 'verbose',
  transports: [
    new DailyRotateFile(opts)
  ]
});
```

### Configuring the Default Logger

```javascript
winston.configure({
  transports: [
    new winston.transports.File({ filename: 'somefile.log' })
  ]
});
```

---

## Logging Levels

### Standard NPM Levels (Default)

Winston uses npm logging levels by default:

```javascript
{
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  verbose: 4,
  debug: 5,
  silly: 6
}
```

### Standard Syslog Levels

You can also use RFC5424 syslog levels:

```javascript
{
  emerg: 0,
  alert: 1,
  crit: 2,
  error: 3,
  warning: 4,
  notice: 5,
  info: 6,
  debug: 7
}
```

To use syslog levels:

```javascript
const logger = winston.createLogger({
  levels: winston.config.syslog.levels,
  transports: [
    new winston.transports.Console({ level: 'error' }),
    new winston.transports.File({
      filename: 'combined.log',
      level: 'info'
    })
  ]
});
```

### Custom Logging Levels

Define your own custom logging levels:

```javascript
const myCustomLevels = {
  levels: {
    foo: 0,
    bar: 1,
    baz: 2,
    foobar: 3
  },
  colors: {
    foo: 'blue',
    bar: 'green',
    baz: 'yellow',
    foobar: 'red'
  }
};

const customLevelLogger = winston.createLogger({
  levels: myCustomLevels.levels
});

// Register colors for custom levels
winston.addColors(myCustomLevels.colors);

customLevelLogger.foobar('some foobar level-ed message');
```

### Dynamic Level Changes

You can change logging levels at runtime:

```javascript
const transports = {
  console: new winston.transports.Console({ level: 'warn' }),
  file: new winston.transports.File({ filename: 'combined.log', level: 'error' })
};

const logger = winston.createLogger({
  transports: [transports.console, transports.file]
});

logger.info('Will not be logged in either transport!');

// Change levels at runtime
transports.console.level = 'info';
transports.file.level = 'info';

logger.info('Will be logged in both transports!');
```

### Logging Methods

Winston provides multiple ways to log messages:

```javascript
// Using the generic log method
logger.log('silly', "127.0.0.1 - there's no place like home");
logger.log('debug', "127.0.0.1 - there's no place like home");
logger.log('verbose', "127.0.0.1 - there's no place like home");
logger.log('info', "127.0.0.1 - there's no place like home");
logger.log('warn', "127.0.0.1 - there's no place like home");
logger.log('error', "127.0.0.1 - there's no place like home");

// Using convenience methods
logger.info("127.0.0.1 - there's no place like home");
logger.warn("127.0.0.1 - there's no place like home");
logger.error("127.0.0.1 - there's no place like home");

// Using object syntax
logger.log({
  level: 'info',
  message: 'Hello distributed log files!'
});

logger.info('Hello again distributed logs');
```

---

## Formats and Formatting

### Built-in Formats

Winston provides many built-in formats that can be combined:

```javascript
const { format } = winston;
const { combine, timestamp, label, printf, json, simple, colorize, prettyPrint } = format;

const logger = winston.createLogger({
  format: combine(
    timestamp(),
    errors({ stack: true }),
    json()
  ),
  transports: [
    new winston.transports.File({ filename: 'app.log' }),
    new winston.transports.Console({
      format: combine(
        colorize(),
        simple()
      )
    })
  ]
});
```

### Custom Printf Format

Create custom log formats using `printf`:

```javascript
const { createLogger, format, transports } = require('winston');
const { combine, timestamp, label, printf } = format;

const myFormat = printf(({ level, message, label, timestamp }) => {
  return `${timestamp} [${label}] ${level}: ${message}`;
});

const logger = createLogger({
  format: combine(
    label({ label: 'right meow!' }),
    timestamp(),
    myFormat
  ),
  transports: [new transports.Console()]
});
```

### String Interpolation

Enable string interpolation with `format.splat()`:

```javascript
const { createLogger, format, transports } = require('winston');

const logger = createLogger({
  format: format.combine(
    format.splat(),
    format.simple()
  ),
  transports: [new transports.Console()]
});

// info: test message my string {}
logger.log('info', 'test message %s', 'my string');

// info: test message 123 {}
logger.log('info', 'test message %d', 123);

// info: test message first second {number: 123}
logger.log('info', 'test message %s, %s', 'first', 'second', { number: 123 });
```

### Combining Multiple Formats

```javascript
const { createLogger, format, transports } = require('winston');
const { combine, timestamp, label, prettyPrint } = format;

const logger = createLogger({
  format: combine(
    label({ label: 'right meow!' }),
    timestamp(),
    prettyPrint()
  ),
  transports: [new transports.Console()]
})

logger.log({
  level: 'info',
  message: 'What time is the testing at?'
});
// Outputs:
// { level: 'info',
//   message: 'What time is the testing at?',
//   label: 'right meow!',
//   timestamp: '2017-09-30T03:57:26.875Z' }
```

### Colorization

Apply colors to log levels:

```javascript
// Colorize only the level
winston.format.combine(
  winston.format.colorize(),
  winston.format.simple()
);

// Colorize the entire log line
winston.format.combine(
  winston.format.json(),
  winston.format.colorize({ all: true })
);
```

### Transport-Specific Formats

Apply different formats to different transports:

```javascript
const logger = winston.createLogger({
  transports: [
    new winston.transports.File({
      filename: 'error.log',
      level: 'error',
      format: winston.format.json()
    }),
    new winston.transports.Http({
      level: 'warn',
      format: winston.format.json()
    }),
    new winston.transports.Console({
      level: 'info',
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ]
});
```

---

## Custom Formats

### Creating Custom Formats

Winston allows you to create custom format functions:

```javascript
const { format } = require('winston');

const volume = format((info, opts) => {
  if (opts.yell) {
    info.message = info.message.toUpperCase();
  } else if (opts.whisper) {
    info.message = info.message.toLowerCase();
  }
  return info;
});

// Use the custom format
const scream = volume({ yell: true });
const whisper = volume({ whisper: true });
```

### Format API Definition

Custom formats must implement the `transform` method:

```javascript
// Format class:
//   transform(info: object, opts: object) method:
//     info: object - An object representing the log message.
//     opts: object - Settings specific to the current instance of the format.
//     Returns:
//       object - The modified `info` object.
//       falsey value - Indicates that the `info` argument should be ignored.
```

### Filtering Log Messages

Filter out log messages by returning a falsey value:

```javascript
const { createLogger, format, transports } = require('winston');

// Ignore log messages if they have { private: true }
const ignorePrivate = format((info, opts) => {
  if (info.private) { return false; }
  return info;
});

const logger = createLogger({
  format: format.combine(
    ignorePrivate(),
    format.json()
  ),
  transports: [new transports.Console()]
});

// Outputs: {"level":"error","message":"Public error to share"}
logger.log({
  level: 'error',
  message: 'Public error to share'
});

// Messages with { private: true } will not be written when logged.
logger.log({
  private: true,
  level: 'error',
  message: 'This is super secret - hide it.'
});
```

### Format Combine Behavior

`format.combine` respects falsey return values:

```javascript
const { format } = require('winston');

const willNeverThrow = format.combine(
  format(info => { return false })(), // Ignores everything
  format(info => { throw new Error('Never reached') })()
);
```

### Message Concatenation

Winston concatenates messages when a `message` property is in metadata:

```javascript
logger.log('error', 'hello', { message: 'world' });
logger.info('hello', { message: 'world' });
// Both will log: "hello world"
```

---

## Core Transports

### Console Transport

The Console transport outputs logs to the console (stdout/stderr):

```javascript
logger.add(new winston.transports.Console({
  level: 'info',
  silent: false,
  eol: '\n',
  stderrLevels: ['error', 'debug'],
  consoleWarnLevels: ['warn'],
  forceConsole: false  // Force use of console.log() instead of stdout
}));
```

#### Console Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | level set on parent logger | Level of messages that this transport should log |
| `silent` | boolean | false | Boolean flag indicating whether to suppress output |
| `eol` | string | os.EOL | String indicating the end-of-line characters to use |
| `stderrLevels` | Array<string> | [] | Array of strings containing the levels to log to stderr instead of stdout |
| `consoleWarnLevels` | Array<string> | [] | Array of strings containing the levels to log using console.warn |
| `forceConsole` | boolean | false | Force use of console.log(), console.warn(), and console.error() |

#### Force Console Usage

Useful for specific environments like VSCode, AWS Lambda, or Jest tests:

```javascript
const logger = winston.createLogger({
  level: 'info',
  transports: [new winston.transports.Console({ forceConsole: true })]
});
```

### File Transport

The File transport writes logs to files:

```javascript
logger.add(new winston.transports.File({
  filename: 'app.log',
  level: 'info',
  silent: false,
  eol: '\n',
  lazy: false,
  maxsize: 5242880,  // 5MB
  maxFiles: 5,
  tailable: false,
  maxRetries: 2,
  zippedArchive: false,
  options: { flags: 'a' }
}));
```

#### File Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | level set on parent logger | Level of messages that this transport should log |
| `silent` | boolean | false | Boolean flag indicating whether to suppress output |
| `eol` | string | os.EOL | Line-ending character to use |
| `lazy` | boolean | false | If true, log files will be created on demand |
| `filename` | string | - | The filename of the logfile to write output to |
| `maxsize` | number | - | Max size in bytes of the logfile |
| `maxFiles` | number | - | Limit the number of files created when size is exceeded |
| `tailable` | boolean | false | If true, log files will be rolled in ascending order |
| `maxRetries` | number | 2 | Number of stream creation retry attempts |
| `zippedArchive` | boolean | false | If true, all log files but current will be zipped |
| `options` | object | {flags: 'a'} | Options passed to fs.createWriteStream |

#### Multiple File Transports

Configure multiple file transports for different log levels:

```javascript
const logger = winston.createLogger({
  transports: [
    new winston.transports.File({
      filename: 'combined.log',
      level: 'info'
    }),
    new winston.transports.File({
      filename: 'errors.log',
      level: 'error'
    })
  ]
});
```

### HTTP Transport

Send logs to remote HTTP endpoints:

```javascript
logger.add(new winston.transports.Http({
  host: 'localhost',
  port: 80,
  path: '/',
  auth: { username: 'user', password: 'pass' },
  ssl: false,
  batch: false,
  batchInterval: 5000,
  batchCount: 10
}));
```

#### HTTP Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | localhost | Remote host of the HTTP logging endpoint |
| `port` | number | 80 or 443 | Remote port of the HTTP logging endpoint |
| `path` | string | / | Remote URI of the HTTP logging endpoint |
| `auth` | object | None | Username and password for HTTP Basic Auth |
| `ssl` | boolean | false | Value indicating if HTTPS should be used |
| `batch` | boolean | false | Value indicating if batch mode should be used |
| `batchInterval` | number | 5000 | Milliseconds to wait before sending HTTP request |
| `batchCount` | number | 10 | Number of logs to cumulate before sending |

### Stream Transport

Direct logs to any Node.js WritableStream:

```javascript
logger.add(new winston.transports.Stream({
  stream: fs.createWriteStream('/dev/null'),
  level: 'info',
  silent: false,
  eol: '\n'
}));
```

#### Stream Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `stream` | WritableStream | - | Any Node.js stream. If objectMode, entire info object is written |
| `level` | string | level set on parent logger | Level of messages that this transport should log |
| `silent` | boolean | false | Boolean flag indicating whether to suppress output |
| `eol` | string | os.EOL | Line-ending character to use |

---

## Cloud and Database Transports

### MongoDB Transport

Store logs in MongoDB:

```javascript
const winston = require('winston');
require('winston-mongodb');

logger.add(new winston.transports.MongoDB({
  level: 'info',
  silent: false,
  db: 'mongodb://localhost:27017/logs',
  options: { poolSize: 2, autoReconnect: true },
  collection: 'log',
  storeHost: true,
  username: 'dbuser',
  password: 'dbpass',
  label: 'my-app',
  name: 'mongodb-transport',
  capped: false,
  cappedSize: 10000000,
  cappedMax: 1000,
  tryReconnect: false,
  expireAfterSeconds: 3600
}));
```

#### MongoDB Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | 'info' | Level of messages that this transport should log |
| `silent` | boolean | false | Boolean flag indicating whether to suppress output |
| `db` | string/object/Promise | - | MongoDB connection uri, pre-connected db object or promise |
| `options` | object | {poolSize: 2, autoReconnect: true} | MongoDB connection parameters |
| `collection` | string | 'log' | Name of the collection to store log messages |
| `storeHost` | boolean | false | Boolean indicating if machine hostname should be stored |
| `username` | string | - | Username for MongoDB authentication |
| `password` | string | - | Password for MongoDB authentication |
| `label` | string | - | Label stored with entry object |
| `name` | string | - | Transport instance identifier |
| `capped` | boolean | false | Try to create new log collection as capped |
| `cappedSize` | number | 10000000 | Size of logs capped collection in bytes |
| `cappedMax` | number | - | Size of logs capped collection in number of documents |
| `tryReconnect` | boolean | false | Try to reconnect to database in case of fail |
| `expireAfterSeconds` | number | - | Seconds before entry is removed (if not capped) |

### Amazon CloudWatch Transport

Send logs to AWS CloudWatch:

```javascript
const winston = require('winston');
const AwsCloudWatch = require('winston-aws-cloudwatch');

logger.add(new AwsCloudWatch({
  logGroupName: 'my-log-group',  // required
  logStreamName: 'my-log-stream', // required
  awsConfig: {
    accessKeyId: 'your-access-key-id',
    secretAccessKey: 'your-secret-access-key',
    region: 'us-east-1'
  }
}));
```

#### CloudWatch Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `logGroupName` | string | - | The name of the CloudWatch log group to log to [required] |
| `logStreamName` | string | - | The name of the CloudWatch log stream to log to [required] |
| `awsConfig` | object | - | AWS configuration containing accessKeyId, secretAccessKey, region |

### Google Stackdriver Transport

Send logs to Google Cloud Logging (Stackdriver):

```javascript
const winston = require('winston');
const { LoggingWinston } = require('@google-cloud/logging-winston');

logger.add(new LoggingWinston({
  projectId: 'your-project-id',
  keyFilename: '/path/to/keyfile.json'
}));
```

#### Stackdriver Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `projectId` | string | - | Your Google Cloud project ID |
| `keyFilename` | string | - | Path to your service account key file |

### Redis Transport

Store logs in Redis:

```javascript
const WinstonRedis = require('winston-redis');

logger.add(new WinstonRedis({
  host: 'localhost',
  port: 6379,
  auth: 'password',
  length: 200,
  container: 'winston',
  channel: 'log-channel'
}));
```

#### Redis Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | localhost | Remote host of the Redis server |
| `port` | number | 6379 | Port the Redis server is running on |
| `auth` | string | null | Password set on the Redis server |
| `length` | number | 200 | Number of log messages to store |
| `container` | string | winston | Name of the Redis container for logs |
| `channel` | string | null | Name of the Redis channel to stream logs from |

### MySQL Transport

Store logs in MySQL database:

```javascript
import MySQLTransport from 'winston-mysql';

// First create the table:
// CREATE TABLE `sys_logs_default` (
//   `id` INT NOT NULL AUTO_INCREMENT,
//   `level` VARCHAR(16) NOT NULL,
//   `message` VARCHAR(2048) NOT NULL,
//   `meta` VARCHAR(2048) NOT NULL,
//   `timestamp` DATETIME NOT NULL,
//   PRIMARY KEY (`id`)
// );

const options = {
  host: 'localhost',
  user: 'root',
  password: 'password',
  database: 'mydb',
  table: 'sys_logs_default'
};

const logger = winston.createLogger({
  level: 'debug',
  format: winston.format.json(),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.Console({
      format: winston.format.simple(),
    }),
    new MySQLTransport(options),
  ],
});

let msg = 'My Log';
logger.info(msg, { message: msg, type: 'demo' });
```

### CouchDB Transport

Store logs in CouchDB:

```javascript
const WinstonCouchDb = require('winston-couchdb');

logger.add(new WinstonCouchDb({
  host: 'localhost',
  port: 5984,
  db: 'winston',
  auth: { username: 'admin', password: 'pass' },
  ssl: false
}));
```

#### CouchDB Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | localhost | Remote host of the HTTP logging endpoint |
| `port` | number | 5984 | Remote port of the HTTP logging endpoint |
| `db` | string | winston | Remote URI of the HTTP logging endpoint |
| `auth` | object | null | Username and password for HTTP Basic Auth |
| `ssl` | boolean | false | Value indicating if HTTPS should be used |

### Cloudant Transport

Store logs in IBM Cloudant:

```javascript
const winston = require('winston');
const WinstonCloudant = require('winston-cloudant');

logger.add(new WinstonCloudant({
  url: 'https://user:pass@account.cloudant.com', // required
  username: 'username',
  password: 'password',
  host: 'account.cloudant.com',
  db: 'logs',
  logstash: true
}));
```

#### Cloudant Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | string | - | Access url including user and password [required] |
| `username` | string | - | Username for the Cloudant DB instance |
| `password` | string | - | Password for the Cloudant DB instance |
| `host` | string | - | Host for the Cloudant DB instance |
| `db` | string | - | Name of the database to put logs in |
| `logstash` | boolean | false | Write logs in logstash format |

### SQLite Transport

Store logs in SQLite database:

```javascript
const wbs = require('winston-better-sqlite3');

logger.add(new wbs({
  db: '/path/to/database.sqlite',  // path to sqlite3 database file
  params: ['level', 'message']     // list of parameters to log
}));
```

#### SQLite Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `db` | string | - | Path to the sqlite3 database file on disk |
| `params` | string[] | - | A list of parameters to log (e.g., ['level', 'message']) |

### Cassandra Transport

Store logs in Cassandra:

```javascript
const Cassandra = require('winston-cassandra').Cassandra;

logger.add(new Cassandra({
  level: 'info',
  table: 'logs',
  partitionBy: 'day',
  consistency: 'quorum',
  hosts: ['host1', 'host2'],      // required
  keyspace: 'winston'             // required
}));
```

#### Cassandra Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | 'info' | Level of messages that this transport should log |
| `table` | string | 'logs' | Name of the Cassandra column family for log messages |
| `partitionBy` | string | 'day' | How logs are partitioned ('hour' or 'day') |
| `consistency` | string | 'quorum' | The consistency of the insert query |
| `hosts` | string[] | - | Array of hosts (required) |
| `keyspace` | string | - | Name of keyspace containing the logs table (required) |

### Riak Transport

Store logs in Riak:

```javascript
const { Riak } = require('winston-riak');

logger.add(new Riak({
  level: 'info',
  bucket: 'logs'  // can also be a function for dynamic bucket names
}));

// Dynamic bucket based on date and level
logger.add(new Riak({
  bucket: function (level, msg, meta, now) {
    var d = new Date(now);
    return level + [d.getDate(), d.getMonth(), d.getFullYear()].join('-');
  }
}));
```

#### Riak Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | - | Level of messages that this transport should log |
| `bucket` | string/function | - | Riak bucket name or function to generate bucket names |

### Amazon DynamoDB Transport

Store logs in DynamoDB:

```javascript
const winston = require('winston');
const { DynamoDB } = require('winston-dynamodb');

logger.add(new DynamoDB({
  useEnvironment: true,  // Use AWS environment variables
  tableName: 'log',
  // OR specify credentials directly:
  accessKeyId: 'your-access-key',
  secretAccessKey: 'your-secret-key',
  region: 'us-east-1'
}));
```

#### DynamoDB Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `accessKeyId` | string | - | AWS access key id |
| `secretAccessKey` | string | - | AWS secret access key |
| `region` | string | - | The region where the domain is hosted |
| `useEnvironment` | boolean | false | Use process.env values for AWS credentials |
| `tableName` | string | - | DynamoDB table name |

### Amazon Kinesis Firehose Transport

Send logs to Kinesis Firehose:

```javascript
const winston = require('winston');
const WFirehose = require('winston-firehose');

logger.add(new WFirehose({
  streamName: 'my-stream',  // required
  firehoseOptions: {        // required - AWS Firehose client options
    accessKeyId: 'your-key',
    secretAccessKey: 'your-secret',
    region: 'us-east-1'
  }
}));
```

#### Kinesis Firehose Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `streamName` | string | - | Name of the Amazon Kinesis Firehose stream [required] |
| `firehoseOptions` | object | - | AWS Kinesis firehose client options [required] |

### Amazon SNS Transport

Send logs via Amazon SNS:

```javascript
const winston = require('winston');
const SnsTransport = require('winston-sns');

logger.add(new SnsTransport({
  subscriber: '123456789012',        // AWS Account ID [required]
  topic_arn: 'arn:aws:sns:us-east-1:123456789012:MyTopic', // [required]
  aws_key: 'your-access-key',
  aws_secret: 'your-secret-key',
  region: 'us-east-1',
  subject: 'Winston Error Report',
  message: "Level '%l' Error:\n%e\n\nMetadata:\n%m",
  level: 'info',
  json: false,
  handleExceptions: false
}));
```

#### SNS Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `subscriber` | string | - | AWS Account ID [required] |
| `topic_arn` | string | - | SNS Topic ARN [required] |
| `aws_key` | string | - | AWS access key |
| `aws_secret` | string | - | AWS secret key |
| `region` | string | us-east-1 | AWS region |
| `subject` | string | Winston Error Report | Subject for notifications |
| `message` | string | Level '%l' Error... | Message template with placeholders |
| `level` | string | info | Lowest level this transport will log |
| `json` | boolean | false | Use JSON instead of human-friendly string |
| `handleExceptions` | boolean | false | Handle exceptions with this transport |

### SimpleDB Transport

Store logs in Amazon SimpleDB:

```javascript
const SimpleDB = require('winston-simpledb').SimpleDB;

logger.add(new SimpleDB({
  awsAccessKey: 'your-access-key',     // required
  secretAccessKey: 'your-secret-key', // required
  awsAccountId: '123456789012',        // required
  domainName: 'logs',                  // required
  region: 'us-east-1',                 // required
  itemName: 'uuid'  // 'uuid', 'epoch', 'timestamp', or function
}));
```

#### SimpleDB Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `awsAccessKey` | string | - | AWS Access Key [required] |
| `secretAccessKey` | string | - | AWS Secret Access Key [required] |
| `awsAccountId` | string | - | AWS Account Id [required] |
| `domainName` | string/function | - | Domain name to log to [required] |
| `region` | string | - | Region your domain resides in [required] |
| `itemName` | string/function | - | Item name to log ('uuid', 'epoch', 'timestamp') |

### Azure Table Transport

Store logs in Azure Table Storage:

```javascript
const { AzureLogger } = require('winston-azuretable');

logger.add(new AzureLogger({
  useDevStorage: false,  // Use Azure Storage Emulator
  account: 'your-account',
  key: 'your-key',
  level: 'info',
  tableName: 'log',
  partitionKey: process.env.NODE_ENV,
  silent: false
}));
```

#### Azure Table Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `useDevStorage` | boolean | false | Use Azure Storage Emulator |
| `account` | string | - | Azure Storage Account Name |
| `key` | string | - | Azure Storage Account Key |
| `level` | string | info | Lowest logging level to log |
| `tableName` | string | log | Name of the table to log messages |
| `partitionKey` | string | process.env.NODE_ENV | Table partition key |
| `silent` | boolean | false | Boolean flag indicating whether to suppress output |

### Google BigQuery Transport

Store logs in Google BigQuery:

```javascript
import { WinstonBigQuery } from 'winston-bigquery';
import winston, { format } from 'winston';

const logger = winston.createLogger({
  transports: [
    new WinstonBigQuery({
      tableId: 'winston_logs',            // required
      datasetId: 'logs',                  // required
      applicationCredentials: '/path/to/service-worker.json' // optional
    })
  ]
});
```

#### BigQuery Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `datasetId` | string | - | Your dataset name [required] |
| `tableId` | string | - | Table name in the dataset [required] |
| `applicationCredentials` | string | - | Path to local service worker (optional) |

**Note:** BigQuery transport requires a pre-built schema in BigQuery.

---

## Monitoring and Analytics Transports

### Datadog Transport

Send logs to Datadog:

```javascript
const winston = require('winston');
const { DataDogTransport } = require('datadog-logger-integrations/winston');

const logger = winston.createLogger({
  transports: [
    new DataDogTransport({
      ddClientConfig: {
        authMethods: {
          apiKeyAuth: 'your-api-key'
        }
      },
      service: 'my-service',
      ddsource: 'nodejs',
      ddtags: 'env:production,version:1.0'
    })
  ]
});
```

#### Datadog Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ddClientConfig` | object | - | DataDog client config [required] |
| `service` | string | - | Name of the application or service |
| `ddsource` | string | - | Technology from which the logs originated |
| `ddtags` | string | - | Metadata associated with the logs |

### Sentry Transport

Send logs to Sentry for error tracking:

```javascript
const Sentry = require('winston-transport-sentry-node').default;

logger.add(new Sentry({
  sentry: {
    dsn: 'https://your-dsn@sentry.io/project-id',
    environment: process.env.NODE_ENV || 'production',
    serverName: 'my-server',
    debug: false,
    sampleRate: 1.0,
    maxBreadcrumbs: 100
  },
  level: 'error',
  silent: false
}));
```

#### Sentry Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sentry.dsn` | string | process.env.SENTRY_DSN | Sentry DSN [required] |
| `sentry.environment` | string | NODE_ENV or 'production' | Application environment |
| `sentry.serverName` | string | - | Application name |
| `sentry.debug` | boolean | false | Turn debug mode on or off |
| `sentry.sampleRate` | number | 1.0 | Sample rate (0.0 to 1.0) |
| `sentry.maxBreadcrumbs` | number | 100 | Total breadcrumbs to capture |
| `level` | string | - | Level of messages to log |
| `silent` | boolean | false | Suppress output |

### New Relic Transport

Forward logs to New Relic:

```javascript
import winston from 'winston';
import NewrelicTransport from 'winston-newrelic-agent-transport';

const logger = winston.createLogger();

logger.add(new NewrelicTransport({
  level: 'info',
  rejectCriteria: [/password/, /secret/]  // Regex patterns to reject
}));
```

#### New Relic Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | - | Maximum level of messages to log (optional) |
| `rejectCriteria` | RegExp[] | - | Array of regexes to match for rejection (optional) |

### Loggly Transport

Send logs to Loggly:

```javascript
const WinstonLoggly = require('winston-loggly');

logger.add(new winston.transports.Loggly({
  level: 'info',
  subdomain: 'your-subdomain',  // required
  auth: {                       // required with inputName
    username: 'your-username',
    password: 'your-password'
  },
  inputName: 'your-input-name',
  inputToken: 'your-input-token',
  json: true
}));
```

#### Loggly Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | - | Level of messages that this transport should log |
| `subdomain` | string | - | The subdomain of your Loggly account [required] |
| `auth` | object | - | Authentication information [required with inputName] |
| `inputName` | string | - | Name of the input this instance should log to |
| `inputToken` | string | - | Input token of the input this instance should log to |
| `json` | boolean | false | If true, messages will be sent to Loggly as JSON |

### LogDNA Transport

Forward logs to LogDNA:

```javascript
const logdnaWinston = require('logdna-winston');
const winston = require('winston');

const logger = winston.createLogger({});

const options = {
  key: 'your-api-key',        // required
  hostname: 'my-hostname',
  ip: '127.0.0.1',
  mac: '00:00:00:00:00:00',
  app: 'my-app',
  env: 'production',
  index_meta: true,           // Make meta object searchable
  handleExceptions: true      // Handle exceptions
};

logger.add(new logdnaWinston(options));

let meta = {
  data: 'Some information'
};
logger.log('info', 'Log from LogDNA Winston', meta);
```

### Logzio Transport

Send logs to Logz.io:

```javascript
const winston = require('winston');
const Logzio = require('winston-logzio');

logger.add(new Logzio({
  token: 'your-logzio-token'
}));
```

### Logsene Transport

Send logs to Logsene (Elasticsearch):

```javascript
const winston = require('winston');
const Logsene = require('winston-logsene');

logger.add(new Logsene({
  token: process.env.LOGSENE_TOKEN,
  source: 'main module'
}));
```

#### Logsene Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `token` | string | - | Logsene Application Token |
| `source` | string | main module | Source of the logs |

### Sumo Logic Transport

Send logs to Sumo Logic:

```javascript
const winston = require('winston');
const { SumoLogic } = require('winston-sumologic-transport');

logger.add(new SumoLogic({
  url: 'https://endpoint.collection.sumologic.com/receiver/...'
}));
```

#### Sumo Logic Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | string | - | The Sumo Logic HTTP collector URL |

### Seq Transport

Send structured logs to Seq:

```javascript
const { SeqTransport } = require('@datalust/winston-seq');

logger.add(new SeqTransport({
  serverUrl: "https://your-seq-server:5341",
  apiKey: "your-api-key",
  onError: (e => { console.error(e) })
}));
```

#### Seq Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `serverUrl` | string | - | URL for your Seq server's ingestion |
| `apiKey` | string | - | Seq API Key (optional) |
| `onError` | function | - | Callback for transport errors |

### Airbrake Transport

Send logs to Airbrake for error monitoring:

```javascript
const winston = require('winston');
const { Airbrake } = require('winston-airbrake2');

logger.add(new Airbrake({
  apiKey: 'your-api-key',        // required
  name: 'airbrake',
  level: 'error',
  host: 'http://' + require('os').hostname(),
  env: process.env.NODE_ENV,
  timeout: 30000,
  developmentEnvironments: ['development', 'test'],
  projectRoot: null,
  appVersion: null,
  consoleLogError: false
}));
```

#### Airbrake Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | - | The project API Key [required] |
| `name` | string | airbrake | Transport name |
| `level` | string | error | Level of message to send to Airbrake |
| `host` | string | http://hostname | Information displayed in Airbrake URL |
| `env` | string | NODE_ENV | Environment (affects whether errors are sent) |
| `timeout` | number | 30000 | Maximum time to send to Airbrake (ms) |
| `developmentEnvironments` | string[] | ['development', 'test'] | Environments that won't send to Airbrake |
| `projectRoot` | string | null | Extra string sent to Airbrake |
| `appVersion` | string/number | null | Extra string/number sent to Airbrake |
| `consoleLogError` | boolean | false | Log errors to console in dev environments |

### Graylog2 Transport

Send logs to Graylog2 over UDP:

```javascript
const winston = require('winston');
const Graylog2 = require('winston-graylog2');

logger.add(new Graylog2({
  name: 'Graylog2',
  level: 'info',
  silent: false,
  handleExceptions: false,
  graylog: {
    servers: [
      { host: 'localhost', port: 12201 }
    ],
    hostname: require('os').hostname(),
    facility: 'Node.js',
    bufferSize: 1400
  }
}));
```

#### Graylog2 Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | - | Transport name |
| `level` | string | info | Level of messages this transport should log |
| `silent` | boolean | false | Boolean flag indicating whether to suppress output |
| `handleExceptions` | boolean | false | Handle uncaught exceptions |
| `graylog.servers` | object[] | - | List of graylog2 servers |
| `graylog.hostname` | string | os.hostname() | Name of this host |
| `graylog.facility` | string | Node.js | Facility for these log messages |
| `graylog.bufferSize` | number | 1400 | Max UDP packet size |

### Humio Transport

Send logs to Humio:

```javascript
const winston = require('winston');
const HumioTransport = require('humio-winston');

const logger = winston.createLogger({
  transports: [
    new HumioTransport({
      ingestToken: 'your-humio-ingest-token'
    })
  ]
});
```

### Parseable Transport

Send logs to Parseable (open-source log analytics):

```javascript
const { ParseableTransport } = require('parseable-winston');
const winston = require('winston');

const parseable = new ParseableTransport({
  url: 'https://parsable.myserver.local/api/v1/logstream',
  username: process.env.PARSEABLE_LOGS_USERNAME,
  password: process.env.PARSEABLE_LOGS_PASSWORD,
  logstream: 'my-logstream',
  tags: { tag1: 'tagValue' }  // optional tags
});

const logger = winston.createLogger({
  levels: winston.config.syslog.levels,
  transports: [parseable],
  defaultMeta: { instance: 'app', hostname: 'app1' }
});

logger.info('User took the goggles', { userid: 1, user: { name: 'John Doe' } });
logger.warning('The goggles do nothing', { userid: 1 });
```

#### Parseable Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | string | - | URL for the Parseable log stream endpoint |
| `username` | string | - | Username for Parseable authentication |
| `password` | string | - | Password for Parseable authentication |
| `logstream` | string | - | Name of the logstream to send logs to |
| `tags` | object | - | Key-value pairs added as tags with each ingestion (optional) |

---

## Communication Transports

### Email (Mail) Transport

Send logs via email:

```javascript
const { Mail } = require('winston-mail');

logger.add(new Mail({
  to: 'admin@example.com',           // required
  from: 'winston@server.com',
  host: 'smtp.example.com',          // required
  port: 587,
  secure: false,
  username: 'smtp-user',
  password: 'smtp-pass',
  level: 'error',
  silent: false
}));
```

#### Mail Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `to` | string | - | Email address(es) to send to [required] |
| `from` | string | winston@[server-host-name] | Email address to send from |
| `host` | string | - | SMTP server hostname [required] |
| `port` | number | 587 or 25 | SMTP port |
| `secure` | boolean | - | Use secure connection |
| `username` | string | - | User for server auth |
| `password` | string | - | Password for server auth |
| `level` | string | - | Level of messages this transport should log |
| `silent` | boolean | false | Boolean flag indicating whether to suppress output |

**Note:** Metadata is stringified as JSON in email.

### Slack Transport

Send logs to Slack via webhooks:

```javascript
const winston = require('winston');
const SlackHook = require('winston-slack-webhook-transport');

const logger = winston.createLogger({
  level: 'info',
  transports: [
    new SlackHook({
      webhookUrl: 'https://hooks.slack.com/services/xxx/xxx/xxx',
      channel: '#logs',
      username: 'LogBot',
      iconEmoji: ':robot_face:',
      iconUrl: 'https://example.com/icon.png',
      level: 'error',
      unfurlLinks: false,
      unfurlMedia: false,
      mrkdwn: true,
      formatter: (info) => {
        return {
          text: `${info.level}: ${info.message}`,
          attachments: [
            {
              color: 'danger',
              fields: [{
                title: 'Error Details',
                value: JSON.stringify(info.meta, null, 2),
                short: false
              }]
            }
          ]
        };
      }
    })
  ]
});

logger.info('This should now appear on Slack');
```

#### Slack Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `webhookUrl` | string | - | Slack incoming webhook URL [required] |
| `channel` | string | - | Slack channel to post message to |
| `username` | string | - | Username to post message with |
| `iconEmoji` | string | - | Status icon to post message with |
| `iconUrl` | string | - | Status icon URL to post message with |
| `formatter` | function | - | Custom function to format messages |
| `level` | string | - | Level to log |
| `unfurlLinks` | boolean | false | Enable or disable link unfurling |
| `unfurlMedia` | boolean | false | Enable or disable media unfurling |
| `mrkdwn` | boolean | false | Enable mrkdwn formatting |

### Papertrail Transport

Send logs to Papertrail:

```javascript
const { Papertrail } = require('winston-papertrail');

logger.add(new Papertrail({
  level: 'info',
  host: 'logs.papertrailapp.com',
  port: 12345,
  hostname: require('os').hostname(),
  program: 'my-app',
  logFormat: function(level, message) {
    return `[${level}] ${message}`;
  }
}));
```

#### Papertrail Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | info | Level of messages this transport should log |
| `host` | string | - | FQDN or IP address of the Papertrail endpoint |
| `port` | number | - | Port for the Papertrail log destination |
| `hostname` | string | os.hostname() | Hostname associated with messages |
| `program` | string | default | Facility to send log messages |
| `logFormat` | function | - | Log formatting function with signature (level, message) |

**Note:** Metadata is logged as a native JSON object to the 'meta' attribute.

### Pusher Transport

Send logs to Pusher for real-time processing:

```javascript
const { PusherLogger } = require('winston-pusher');

logger.add(new PusherLogger({
  pusher: {
    appId: 'your-app-id',
    key: 'your-key',
    secret: 'your-secret',
    cluster: 'your-cluster',
    encrypted: true
  },
  channel: 'logs',
  event: 'log-event'
}));
```

#### Pusher Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `pusher.appId` | string | - | Application ID from dashboard |
| `pusher.key` | string | - | Application key from dashboard |
| `pusher.secret` | string | - | Application secret from dashboard |
| `pusher.cluster` | string | - | The cluster |
| `pusher.encrypted` | boolean | - | Whether data is sent through SSL |
| `channel` | string | default | Channel of the event |
| `event` | string | default | Event name |

### Cisco Spark Transport

Send logs to Cisco Spark (now Webex Teams):

```javascript
const winston = require('winston');
require('winston-spark');

const options = {
  accessToken: 'your-spark-access-token',  // required
  roomId: 'your-spark-room-id',           // required
  level: 'info',
  hideMeta: false
};

logger.add(new winston.transports.SparkLogger(options));
```

#### Cisco Spark Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `accessToken` | string | - | Your Spark Access Token [required] |
| `roomId` | string | - | Spark Room Id [required] |
| `level` | string | info | Log Level |
| `hideMeta` | boolean | false | Hide MetaData |

---

## Specialized Transports

### VS Code Extension Development

#### OutputChannel Transport

For standard VS Code output channels:

```javascript
const vscode = require('vscode');
const winston = require('winston');
const { OutputChannelTransport } = require('winston-transport-vscode');

const outputChannel = vscode.window.createOutputChannel('My Extension');

const logger = winston.createLogger({
  transports: [new OutputChannelTransport({ outputChannel })]
});
```

#### LogOutputChannel Transport

For VS Code's dedicated log output channels:

```javascript
const { LogOutputChannelTransport } = require('winston-transport-vscode');

const outputChannel = vscode.window.createOutputChannel('My Extension', {
  log: true,
});

const logger = winston.createLogger({
  levels: LogOutputChannelTransport.config.levels,
  format: LogOutputChannelTransport.format(),
  transports: [new LogOutputChannelTransport({ outputChannel })]
});
```

### Fast File Rotate Transport

High-performance daily log rotation:

```javascript
const FileRotateTransport = require('fast-file-rotate');
const winston = require('winston');

const logger = winston.createLogger({
  transports: [
    new FileRotateTransport({
      fileName: __dirname + '/logs/console%DATE%.log'
    })
  ]
});
```

### Windows Event Log Transport

Log to Windows Event Log:

```javascript
const winston = require('winston');
const Winlog2 = require('winston-winlog2');

logger.add(new Winlog2({
  name: 'my-transport',
  eventLog: 'APPLICATION',  // Log type
  source: 'my-app'          // Source name in Event Log
}));
```

#### Winlog2 Transport Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | - | Transport name |
| `eventLog` | string | APPLICATION | Log type |
| `source` | string | node | Name of application appearing in event log |

### Worker Thread Console Transport

Asynchronous console logging using worker threads:

```typescript
import * as winston from 'winston';
import { ConsoleTransportInWorker } from '@greeneyesai/winston-console-transport-in-worker';

export const logger: winston.Logger = winston.createLogger({
  format: winston.format.combine(winston.format.timestamp(), myFormat),
  level: 'info',
  transports: [new ConsoleTransportInWorker()],
});
```

---

## Exception and Rejection Handling

### Uncaught Exception Handling

Winston can catch and log uncaught exceptions to prevent your application from crashing:

#### During Logger Creation

```javascript
const { createLogger, transports } = require('winston');

// Enable exception handling when you create your logger
const logger = createLogger({
  transports: [
    new transports.File({ filename: 'combined.log' })
  ],
  exceptionHandlers: [
    new transports.File({ filename: 'exceptions.log' })
  ]
});
```

#### Dynamically Adding Exception Handling

```javascript
const logger = createLogger({
  transports: [
    new transports.File({ filename: 'combined.log' })
  ]
});

// Call exceptions.handle with a transport to handle exceptions
logger.exceptions.handle(
  new transports.File({ filename: 'exceptions.log' })
);
```

#### Global Exception Handling

```javascript
// You can add a separate exception logger by passing it to `.exceptions.handle`
winston.exceptions.handle(
  new winston.transports.File({ filename: 'path/to/exceptions.log' })
);

// Alternatively you can set `handleExceptions` to true when adding transports
winston.add(new winston.transports.File({
  filename: 'path/to/combined.log',
  handleExceptions: true
}));
```

#### Exception Handling on Console Transport

```javascript
const logger = winston.createLogger({
  transports: [
    new winston.transports.Console({
      handleExceptions: true
    })
  ],
  exitOnError: false
});
```

### Unhandled Promise Rejection Handling

Similarly, Winston can catch unhandled promise rejections:

#### During Logger Creation

```javascript
const { createLogger, transports } = require('winston');

// Enable rejection handling when you create your logger
const logger = createLogger({
  transports: [
    new transports.File({ filename: 'combined.log' })
  ],
  rejectionHandlers: [
    new transports.File({ filename: 'rejections.log' })
  ]
});
```

#### Dynamically Adding Rejection Handling

```javascript
const logger = createLogger({
  transports: [
    new transports.File({ filename: 'combined.log' })
  ]
});

// Call rejections.handle with a transport to handle rejections
logger.rejections.handle(
  new transports.File({ filename: 'rejections.log' })
);
```

#### Global Rejection Handling

```javascript
// Add a separate rejection logger
winston.rejections.handle(
  new winston.transports.File({ filename: 'path/to/rejections.log' })
);

// Alternatively set `handleRejections` to true when adding transports
winston.add(new winston.transports.File({
  filename: 'path/to/combined.log',
  handleRejections: true
}));
```

### Exit Behavior Control

Control whether the process exits after logging an exception:

#### Prevent Process Exit

```javascript
const logger = winston.createLogger({ exitOnError: false });

// or, like this:
logger.exitOnError = false;
```

#### Conditional Exit Prevention

```javascript
function ignoreEpipe(err) {
  return err.code !== 'EPIPE';
}

const logger = winston.createLogger({ exitOnError: ignoreEpipe });

// or, like this:
logger.exitOnError = ignoreEpipe;
```

### Complete Exception and Rejection Setup

```javascript
const logger = winston.createLogger({
  transports: [
    new winston.transports.File({ filename: 'path/to/combined.log' })
  ],
  exceptionHandlers: [
    new winston.transports.File({ filename: 'path/to/exceptions.log' })
  ],
  rejectionHandlers: [
    new winston.transports.File({ filename: 'path/to/rejections.log' })
  ],
  exitOnError: false
});
```

---

## Multiple Loggers and Containers

### Using winston.loggers

Winston provides a global container for managing multiple logger instances:

```javascript
const winston = require('winston');
const { format } = winston;
const { combine, label, json } = format;

// Configure the logger for `category1`
winston.loggers.add('category1', {
  format: combine(
    label({ label: 'category one' }),
    json()
  ),
  transports: [
    new winston.transports.Console({ level: 'silly' }),
    new winston.transports.File({ filename: 'somefile.log' })
  ]
});

// Configure the logger for `category2`
winston.loggers.add('category2', {
  format: combine(
    label({ label: 'category two' }),
    json()
  ),
  transports: [
    new winston.transports.Http({ host: 'localhost', port: 8080 })
  ]
});

// Grab your preconfigured loggers
const category1 = winston.loggers.get('category1');
const category2 = winston.loggers.get('category2');

category1.info('logging to file and console transports');
category2.info('logging to http transport');
```

### Manual Container Management

For more granular control, you can create your own containers:

```javascript
const winston = require('winston');
const { format } = winston;
const { combine, label, json } = format;

const container = new winston.Container();

container.add('category1', {
  format: combine(
    label({ label: 'category one' }),
    json()
  ),
  transports: [
    new winston.transports.Console({ level: 'silly' }),
    new winston.transports.File({ filename: 'somefile.log' })
  ]
});

const category1 = container.get('category1');
category1.info('logging to file and console transports');
```

### Transport Management

#### Dynamic Transport Addition/Removal

```javascript
const files = new winston.transports.File({ filename: 'combined.log' });
const console = new winston.transports.Console();

logger
  .clear()          // Remove all transports
  .add(console)     // Add console transport
  .add(files)       // Add file transport
  .remove(console); // Remove console transport
```

#### Default Logger Transport Management

```javascript
const files = new winston.transports.File({ filename: 'combined.log' });
const console = new winston.transports.Console();

winston.add(console);
winston.add(files);
winston.remove(console);
```

#### Finding and Removing Specific Transports

```javascript
const combinedLogs = logger.transports.find(transport => {
  return transport.filename === 'combined.log'
});

logger.remove(combinedLogs);
```

---

## Child Loggers

Child loggers inherit configuration from parent loggers but can include additional default metadata:

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  transports: [
    new winston.transports.Console(),
  ]
});

const childLogger = logger.child({ requestId: '451' });

// All logs from childLogger will include requestId: '451'
childLogger.info('This will include the requestId');
childLogger.error('So will this error');
```

Child loggers are useful for:
- Request-specific logging (adding request IDs)
- Module-specific logging (adding module names)
- User-specific logging (adding user IDs)
- Any scenario where you want consistent metadata

---

## Profiling and Performance

### Basic Profiling

Winston provides simple profiling capabilities:

```javascript
// Start profile of 'test'
logger.profile('test');

setTimeout(function () {
  // Stop profile of 'test'. Logging will now take place:
  //   '17 Jan 21:00:00 - info: test duration=1000ms'
  logger.profile('test');
}, 1000);
```

### Advanced Profiling

For more flexible profiling, use `startTimer()`:

```javascript
// Returns an object corresponding to a specific timing. When done
// is called the timer will finish and log the duration. e.g.:
const profiler = logger.startTimer();

setTimeout(function () {
  profiler.done({ message: 'Logging message' });
}, 1000);
```

### Custom Profile Log Level

Override the default log level for profile messages:

```javascript
logger.profile('test', { level: 'debug' });
```

---

## Querying Logs

Winston supports querying logs from transports that implement querying (File, Couchdb, Redis, Loggly, Nssocket, and Http):

```javascript
const options = {
  from: new Date() - (24 * 60 * 60 * 1000),  // Last 24 hours
  until: new Date(),
  limit: 10,
  start: 0,
  order: 'desc',
  fields: ['message']
};

// Find items logged between today and yesterday
logger.query(options, function (err, results) {
  if (err) {
    /* TODO: handle me */
    throw err;
  }

  console.log(results);
});
```

### Query Options

| Option | Type | Description |
|--------|------|-------------|
| `from` | Date | Start time for the query |
| `until` | Date | End time for the query |
| `limit` | number | Maximum number of results to return |
| `start` | number | Offset for the results |
| `order` | string | Sort order ('asc' or 'desc') |
| `fields` | string[] | Specific fields to retrieve |

---

## Streaming Logs

Stream logs back from your chosen transport:

```javascript
// Start at the end
winston.stream({ start: -1 }).on('log', function(log) {
  console.log(log);
});
```

This creates an event emitter that you can listen to for real-time log processing.

---

## Custom Transports

Create your own custom transports by inheriting from `winston-transport`:

```javascript
const Transport = require('winston-transport');
const util = require('util');

// Inherit from `winston-transport` so you can take advantage
// of the base functionality and `.exceptions.handle()`.
module.exports = class YourCustomTransport extends Transport {
  constructor(opts) {
    super(opts);
    //
    // Consume any custom options here. e.g.:
    // - Connection information for databases
    // - Authentication information for APIs (e.g. loggly, papertrail,
    //   logentries, etc.).
    //
  }

  log(info, callback) {
    setImmediate(() => {
      this.emit('logged', info);
    });

    // Perform the writing to the remote service
    callback();
  }
};
```

### Using Custom Transports

```javascript
const YourCustomTransport = require('./your-custom-transport');

const logger = winston.createLogger({
  transports: [
    new YourCustomTransport({
      // your custom options
    })
  ]
});
```

---

## Error Handling

### Logger Error Events

Handle errors that originate within the logger itself:

```javascript
logger.on('error', function (err) { 
  // Handle or suppress errors
  console.error('Logger error:', err);
});
```

### Asynchronous Logging Completion

Ensure all log messages are processed before exiting:

```javascript
logger.log('info', 'some message');
logger.on('finish', () => process.exit());
logger.end();
```

### Transport-specific Error Handling

```javascript
const transport = new winston.transports.Console();
const logger = winston.createLogger({
  transports: [transport]
});

logger.on('finish', function (info) {
  // All `info` log messages have now been logged
});

logger.info('CHILL WINSTON!', { seriously: true });
logger.end();
```

---

## Best Practices

### 1. Structured Logging

Use consistent structure in your logs:

```javascript
logger.info('User login', {
  userId: user.id,
  email: user.email,
  ip: req.ip,
  userAgent: req.get('User-Agent'),
  timestamp: new Date().toISOString()
});
```

### 2. Appropriate Log Levels

Use log levels appropriately:

- **error**: Actual errors that need immediate attention
- **warn**: Warning conditions that should be noted
- **info**: Important business logic events
- **http**: HTTP request logs
- **verbose**: Detailed operational messages
- **debug**: Debug information for development
- **silly**: Everything including very detailed debug info

### 3. Environment-specific Configuration

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { 
    service: 'my-service',
    environment: process.env.NODE_ENV 
  },
  transports: []
});

// Development
if (process.env.NODE_ENV === 'development') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    )
  }));
}

// Production
if (process.env.NODE_ENV === 'production') {
  logger.add(new winston.transports.File({
    filename: 'error.log',
    level: 'error'
  }));
  
  logger.add(new winston.transports.File({
    filename: 'combined.log'
  }));
}
```

### 4. Security Considerations

Never log sensitive information:

```javascript
// DON'T DO THIS
logger.info('User login attempt', {
  password: user.password,  // NEVER LOG PASSWORDS
  creditCard: user.cc,      // NEVER LOG SENSITIVE DATA
  ssn: user.ssn            // NEVER LOG PII
});

// DO THIS INSTEAD
logger.info('User login attempt', {
  userId: user.id,
  email: user.email.replace(/(.{2})(.*)(@.*)/, '$1***$3'), // Partially obscure email
  hasValidPassword: !!user.password  // Log boolean instead of actual password
});
```

### 5. Error Context

Always provide context with errors:

```javascript
try {
  await someAsyncOperation();
} catch (error) {
  logger.error('Failed to process user order', {
    error: error.message,
    stack: error.stack,
    userId: user.id,
    orderId: order.id,
    timestamp: new Date().toISOString()
  });
  throw error;
}
```

### 6. Performance Considerations

For high-throughput applications:

```javascript
// Use batch options for HTTP transports
logger.add(new winston.transports.Http({
  host: 'log-server.com',
  port: 443,
  batch: true,
  batchInterval: 5000,  // Send logs every 5 seconds
  batchCount: 50        // Or when 50 logs are accumulated
}));

// Use appropriate log levels to avoid excessive logging
logger.level = process.env.NODE_ENV === 'production' ? 'warn' : 'debug';
```

### 7. Log Rotation

Implement log rotation to manage disk space:

```javascript
const DailyRotateFile = require('winston-daily-rotate-file');

logger.add(new DailyRotateFile({
  filename: 'logs/application-%DATE%.log',
  datePattern: 'YYYY-MM-DD-HH',
  zippedArchive: true,
  maxSize: '20m',
  maxFiles: '14d'
}));
```

### 8. Centralized Configuration

Create a centralized logging module:

```javascript
// logger.js
const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { 
    service: process.env.SERVICE_NAME || 'unknown-service',
    version: process.env.SERVICE_VERSION || '1.0.0'
  },
  transports: [
    // Console for all environments
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    
    // File for errors
    new DailyRotateFile({
      filename: 'logs/error-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxSize: '20m',
      maxFiles: '30d',
      zippedArchive: true
    }),
    
    // File for all logs
    new DailyRotateFile({
      filename: 'logs/combined-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '30d',
      zippedArchive: true
    })
  ],
  exceptionHandlers: [
    new winston.transports.File({ filename: 'logs/exceptions.log' })
  ],
  rejectionHandlers: [
    new winston.transports.File({ filename: 'logs/rejections.log' })
  ]
});

module.exports = logger;
```

Then use it throughout your application:

```javascript
// app.js
const logger = require('./logger');

logger.info('Application started', { 
  nodeVersion: process.version,
  platform: process.platform 
});
```

---

## Production Setup Examples

### Basic Production Logger

```javascript
const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { 
    service: 'my-service',
    environment: process.env.NODE_ENV 
  },
  transports: [
    // Console for all environments
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    // Rotating file for errors
    new DailyRotateFile({
      filename: 'logs/error-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxSize: '20m',
      maxFiles: '14d'
    }),
    // Rotating file for all logs
    new DailyRotateFile({
      filename: 'logs/combined-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d'
    })
  ],
  exceptionHandlers: [
    new winston.transports.File({ filename: 'logs/exceptions.log' })
  ],
  rejectionHandlers: [
    new winston.transports.File({ filename: 'logs/rejections.log' })
  ]
});

module.exports = logger;
```

### Cloud-ready Production Logger

```javascript
const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

// Cloud transports (conditional)
let cloudTransports = [];

if (process.env.AWS_CLOUDWATCH_GROUP) {
  const AwsCloudWatch = require('winston-aws-cloudwatch');
  cloudTransports.push(
    new AwsCloudWatch({
      logGroupName: process.env.AWS_CLOUDWATCH_GROUP,
      logStreamName: `${process.env.SERVICE_NAME}-${Date.now()}`,
      awsConfig: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
        region: process.env.AWS_REGION
      }
    })
  );
}

if (process.env.DATADOG_API_KEY) {
  const { DataDogTransport } = require('datadog-logger-integrations/winston');
  cloudTransports.push(
    new DataDogTransport({
      ddClientConfig: {
        authMethods: {
          apiKeyAuth: process.env.DATADOG_API_KEY
        }
      },
      service: process.env.SERVICE_NAME,
      ddsource: 'nodejs',
      ddtags: `env:${process.env.NODE_ENV},version:${process.env.SERVICE_VERSION}`
    })
  );
}

if (process.env.SENTRY_DSN) {
  const Sentry = require('winston-transport-sentry-node').default;
  cloudTransports.push(
    new Sentry({
      sentry: {
        dsn: process.env.SENTRY_DSN,
        environment: process.env.NODE_ENV
      },
      level: 'error'
    })
  );
}

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { 
    service: process.env.SERVICE_NAME,
    version: process.env.SERVICE_VERSION,
    environment: process.env.NODE_ENV,
    instance: process.env.INSTANCE_ID || require('os').hostname()
  },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new DailyRotateFile({
      filename: 'logs/error-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxSize: '50m',
      maxFiles: '30d',
      zippedArchive: true
    }),
    new DailyRotateFile({
      filename: 'logs/combined-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      maxSize: '50m',
      maxFiles: '30d',
      zippedArchive: true
    }),
    ...cloudTransports
  ],
  exceptionHandlers: [
    new winston.transports.File({ filename: 'logs/exceptions.log' }),
    ...cloudTransports.filter(t => t.constructor.name === 'SentryTransport')
  ],
  rejectionHandlers: [
    new winston.transports.File({ filename: 'logs/rejections.log' })
  ]
});

module.exports = logger;
```

### Microservices Logger

```javascript
const winston = require('winston');

class MicroserviceLogger {
  constructor(serviceName, version = '1.0.0') {
    this.serviceName = serviceName;
    this.version = version;
    
    this.logger = winston.createLogger({
      level: process.env.LOG_LEVEL || 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: { 
        service: serviceName,
        version: version,
        environment: process.env.NODE_ENV || 'development',
        instance: process.env.HOSTNAME || require('os').hostname()
      },
      transports: this.createTransports()
    });
  }

  createTransports() {
    const transports = [
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.printf(({ timestamp, level, message, service, ...meta }) => {
            return `${timestamp} [${service}] ${level}: ${message} ${JSON.stringify(meta)}`;
          })
        )
      })
    ];

    // Add file transports in production
    if (process.env.NODE_ENV === 'production') {
      const DailyRotateFile = require('winston-daily-rotate-file');
      
      transports.push(
        new DailyRotateFile({
          filename: `logs/${this.serviceName}-error-%DATE%.log`,
          datePattern: 'YYYY-MM-DD',
          level: 'error',
          maxSize: '20m',
          maxFiles: '14d',
          zippedArchive: true
        }),
        new DailyRotateFile({
          filename: `logs/${this.serviceName}-combined-%DATE%.log`,
          datePattern: 'YYYY-MM-DD',
          maxSize: '20m',
          maxFiles: '14d',
          zippedArchive: true
        })
      );
    }

    // Add centralized logging if configured
    if (process.env.ELASTICSEARCH_URL) {
      const ElasticsearchTransport = require('winston-elasticsearch');
      transports.push(
        new ElasticsearchTransport({
          level: 'info',
          clientOpts: {
            host: process.env.ELASTICSEARCH_URL,
            log: 'error'
          },
          index: `${this.serviceName}-logs`,
          indexPrefix: 'winston-logs',
          indexSuffixPattern: 'YYYY.MM.DD'
        })
      );
    }

    return transports;
  }

  // Convenience methods
  info(message, meta = {}) {
    this.logger.info(message, meta);
  }

  error(message, error = null, meta = {}) {
    const errorMeta = error ? {
      error: error.message,
      stack: error.stack,
      ...meta
    } : meta;
    
    this.logger.error(message, errorMeta);
  }

  warn(message, meta = {}) {
    this.logger.warn(message, meta);
  }

  debug(message, meta = {}) {
    this.logger.debug(message, meta);
  }

  // Request logging
  logRequest(req, res, duration) {
    this.logger.http('HTTP Request', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: duration,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      userId: req.user ? req.user.id : null
    });
  }

  // Business logic logging
  logBusinessEvent(event, data = {}) {
    this.logger.info(`Business Event: ${event}`, {
      event: event,
      ...data
    });
  }

  // Child logger for request context
  child(meta) {
    return {
      logger: this.logger.child(meta),
      info: (message, additionalMeta = {}) => this.logger.child(meta).info(message, additionalMeta),
      error: (message, error = null, additionalMeta = {}) => {
        const errorMeta = error ? {
          error: error.message,
          stack: error.stack,
          ...additionalMeta
        } : additionalMeta;
        this.logger.child(meta).error(message, errorMeta);
      },
      warn: (message, additionalMeta = {}) => this.logger.child(meta).warn(message, additionalMeta),
      debug: (message, additionalMeta = {}) => this.logger.child(meta).debug(message, additionalMeta)
    };
  }
}

module.exports = MicroserviceLogger;
```

Usage:

```javascript
const MicroserviceLogger = require('./microservice-logger');
const logger = new MicroserviceLogger('user-service', '2.1.0');

// Basic logging
logger.info('Service started');
logger.error('Database connection failed', new Error('Connection timeout'));

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.logRequest(req, res, duration);
  });
  
  // Create child logger for request context
  req.logger = logger.child({ 
    requestId: req.headers['x-request-id'] || generateRequestId(),
    userId: req.user ? req.user.id : null 
  });
  
  next();
});

// Business logic logging
app.post('/orders', (req, res) => {
  try {
    const order = createOrder(req.body);
    req.logger.info('Order created successfully', { orderId: order.id });
    logger.logBusinessEvent('ORDER_CREATED', { orderId: order.id, userId: req.user.id });
    res.json(order);
  } catch (error) {
    req.logger.error('Failed to create order', error, { orderData: req.body });
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

---

## Migration Guide (v2 to v3)

### Key Changes

1. **No more callbacks in `logger.log()`**
2. **Filters and rewriters replaced with formats**
3. **Exception handling changes**
4. **Transport instantiation required**

### Logger Creation Changes

**Winston 2.x:**
```javascript
const winston = require('winston');
const logger = new winston.Logger({
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

**Winston 3.x:**
```javascript
const winston = require('winston');
const logger = winston.createLogger({
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

### Callback Handling

**Winston 2.x:**
```javascript
logger.log('info', 'some message', function(err) {
  // Log completed
});
```

**Winston 3.x:**
```javascript
logger.log('info', 'some message');
logger.on('finish', () => process.exit());
logger.end();
```

### Transport Addition

**Winston 2.x:**
```javascript
// This worked in v2 but NO LONGER WORKS in v3
logger.add(winston.transports.Console);
```

**Winston 3.x:**
```javascript
// Do this instead - instantiate the transport
logger.add(new winston.transports.Console());
```

### Filters Migration

**Winston 2.x:**
```javascript
const isSecret = /super secret/;
const logger = new winston.Logger(options);
logger.filters.push(function(level, msg, meta) {
  return msg.replace(isSecret, 'su*** se****');
});
```

**Winston 3.x:**
```javascript
const { createLogger, format, transports } = require('winston');

const isSecret = /super secret/;
const filterSecret = format((info, opts) => {
  info.message = info.message.replace(isSecret, 'su*** se****');
  return info;
});

const logger = createLogger({
  format: format.combine(
    filterSecret(),
    format.json()
  ),
  transports: [new transports.Console()]
});
```

### Rewriters Migration

**Winston 2.x:**
```javascript
const logger = new winston.Logger(options);
logger.rewriters.push(function(level, msg, meta) {
  if (meta.creditCard) {
    meta.creditCard = maskCardNumbers(meta.creditCard);
  }
  return meta;
});
```

**Winston 3.x:**
```javascript
const maskFormat = winston.format(info => {
  if (info.creditCard) {
    info.creditCard = maskCardNumbers(info.creditCard);
  }
  info.hasCreditCard = !!info.creditCard;
  return info;
});

const logger = winston.createLogger({
  format: winston.format.combine(
    maskFormat(),
    winston.format.json()
  )
});
```

### Exception Handling

**Winston 2.x:**
```javascript
winston.handleExceptions(new winston.transports.File({ filename: 'exceptions.log' }));
```

**Winston 3.x:**
```javascript
const exception = winston.ExceptionHandler();
// or use exceptionHandlers in logger configuration
```

### Formatting Options Removed

Many formatting options were removed from transports and replaced with the format system:

| Removed Option | Winston 3.x Equivalent |
|----------------|------------------------|
| `json: true` | `format.json()` |
| `timestamp: true` | `format.timestamp()` |
| `colorize: true` | `format.colorize()` |
| `prettyPrint: true` | `format.prettyPrint()` |
| `label: 'my-label'` | `format.label({ label: 'my-label' })` |
| `formatter: fn` | Custom format function |

---

## Troubleshooting

### Common Issues

#### 1. Transport Not Logging

**Problem:** Transport seems to be added but no logs appear.

**Solutions:**
- Check if the transport level allows the log level you're using
- Verify the transport is properly instantiated (not just the class)
- Ensure the transport isn't silenced

```javascript
// Wrong
logger.add(winston.transports.Console);

// Right
logger.add(new winston.transports.Console({ level: 'debug' }));
```

#### 2. File Transport Not Creating Files

**Problem:** File transport configured but no log files are created.

**Solutions:**
- Check file permissions
- Ensure the directory exists
- Verify the filename path is correct

```javascript
const path = require('path');
const fs = require('fs');

// Ensure log directory exists
const logDir = path.dirname('/path/to/logs/app.log');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

logger.add(new winston.transports.File({ 
  filename: '/path/to/logs/app.log' 
}));
```

#### 3. Colors Not Appearing

**Problem:** Console logs don't show colors.

**Solutions:**
- Ensure `colorize()` format is applied to console transport
- Check if running in environment that supports colors

```javascript
logger.add(new winston.transports.Console({
  format: winston.format.combine(
    winston.format.colorize(),
    winston.format.simple()
  )
}));
```

#### 4. Custom Formats Not Working

**Problem:** Custom format function isn't being called.

**Solutions:**
- Ensure you're calling the format function: `myFormat()` not `myFormat`
- Check that format function returns the info object
- Verify format is in the correct position in `format.combine()`

```javascript
const myFormat = winston.format(info => {
  // Make sure to return info
  return info;
});

// Call the format function
const logger = winston.createLogger({
  format: winston.format.combine(
    myFormat(),  // Note the () to call the function
    winston.format.json()
  )
});
```

#### 5. Memory Leaks with High-Volume Logging

**Problem:** Application memory usage grows over time with heavy logging.

**Solutions:**
- Implement proper log rotation
- Use batch options for HTTP transports
- Consider using separate processes for logging

```javascript
const DailyRotateFile = require('winston-daily-rotate-file');

// Use rotating files to prevent indefinite growth
logger.add(new DailyRotateFile({
  filename: 'logs/app-%DATE%.log',
  datePattern: 'YYYY-MM-DD',
  maxSize: '50m',
  maxFiles: '7d',
  zippedArchive: true
}));
```

#### 6. Metadata Not Appearing

**Problem:** Additional metadata isn't showing up in logs.

**Solutions:**
- Check format configuration
- Ensure metadata is passed correctly
- Verify transport supports metadata

```javascript
// Make sure format includes all fields
logger.add(new winston.transports.Console({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      return `${timestamp} ${level}: ${message} ${JSON.stringify(meta)}`;
    })
  )
}));
```

#### 7. Performance Issues

**Problem:** Logging is causing performance bottlenecks.

**Solutions:**
- Use appropriate log levels in production
- Implement async logging patterns
- Use batch options for network transports

```javascript
// Only log important messages in production
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'warn' : 'debug',
  // ... rest of config
});

// Use batch for network transports
logger.add(new winston.transports.Http({
  host: 'log-server.com',
  batch: true,
  batchInterval: 5000,
  batchCount: 100
}));
```

### Debugging Winston

Enable Winston's internal debugging:

```javascript
process.env.DEBUG = 'winston*';
// Then run your application
```

Or use the debug option:

```javascript
const winston = require('winston');

// Check winston version and configuration
console.log('Winston version:', winston.version);
console.log('Available transports:', Object.keys(winston.transports));
console.log('Default levels:', winston.config.npm.levels);
```

### Testing Log Configuration

Create a simple test to verify your logger configuration:

```javascript
const winston = require('winston');

// Your logger configuration
const logger = winston.createLogger({
  level: 'debug',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'test.log' })
  ]
});

// Test all log levels
console.log('Testing logger configuration...');

logger.error('Test error message', { error: new Error('Test error') });
logger.warn('Test warning message', { warning: true });
logger.info('Test info message', { info: 'test data' });
logger.http('Test http message', { method: 'GET', url: '/test' });
logger.verbose('Test verbose message', { verbose: true });
logger.debug('Test debug message', { debug: 'test debug' });
logger.silly('Test silly message', { silly: 'test silly' });

console.log('Logger test completed. Check console output and test.log file.');
```

---

## Conclusion

Winston.js is a powerful and flexible logging library that can handle virtually any logging requirement in Node.js applications. Its modular architecture allows you to:

- **Route logs to multiple destinations** simultaneously
- **Format logs** according to your specific needs  
- **Handle exceptions and rejections** gracefully
- **Query and stream logs** for analysis
- **Scale from simple console logging** to complex distributed logging systems
- **Integrate with cloud services** and monitoring platforms

### Key Takeaways

1. **Start Simple**: Begin with basic console and file logging, then add complexity as needed
2. **Use Appropriate Levels**: Structure your logging levels properly for effective filtering
3. **Plan for Production**: Consider log rotation, centralized logging, and monitoring from the start
4. **Security First**: Never log sensitive information
5. **Monitor Performance**: Be mindful of logging overhead in high-throughput applications
6. **Test Your Configuration**: Always test your logging setup in different environments

### Next Steps

- Choose appropriate transports for your infrastructure
- Set up proper log rotation and archival
- Implement centralized logging for distributed systems
- Configure monitoring and alerting based on log patterns
- Create standardized logging patterns across your organization

With Winston's extensive transport ecosystem and flexible formatting system, you can build a logging solution that grows with your application and provides the observability needed for modern software development.