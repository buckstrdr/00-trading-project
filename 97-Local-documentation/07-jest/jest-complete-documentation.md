# Jest Complete Documentation

This comprehensive documentation covers all Jest features, patterns, and best practices for JavaScript testing.

## Table of Contents

1. [Getting Started & Configuration](#getting-started--configuration)
2. [Jest CLI Options](#jest-cli-options)
3. [Expect API & Matchers](#expect-api--matchers)
4. [Mocking & Spies](#mocking--spies)
5. [Asynchronous Testing](#asynchronous-testing)
6. [Snapshot Testing](#snapshot-testing)
7. [Coverage & Watch Mode](#coverage--watch-mode)
8. [Setup & Teardown](#setup--teardown)
9. [Custom Matchers](#custom-matchers)
10. [Custom Reporters](#custom-reporters)
11. [Transformers](#transformers)
12. [Best Practices](#best-practices)

---

## Getting Started & Configuration

### Installation

Install Jest as a development dependency:

```bash
# npm
npm install --save-dev jest

# Yarn
yarn add --dev jest

# pnpm
pnpm add --save-dev jest
```

### Basic Setup

Add a test script to your `package.json`:

```json
{
  "scripts": {
    "test": "jest"
  }
}
```

### Configuration Generation

Generate a basic Jest configuration interactively:

```bash
# npm
npm init jest@latest

# Yarn
yarn create jest

# pnpm
pnpm create jest
```

### Babel Configuration

For modern JavaScript features, configure Babel:

```javascript
// babel.config.js
module.exports = {
  presets: [['@babel/preset-env', {targets: {node: 'current'}}]],
};
```

Install Babel dependencies:

```bash
npm install --save-dev babel-jest @babel/core @babel/preset-env
```

For TypeScript support:

```bash
npm install --save-dev @babel/preset-typescript
```

```javascript
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {targets: {node: 'current'}}],
    '@babel/preset-typescript',
  ],
};
```

### Environment-aware Babel Configuration

```javascript
// babel.config.js
module.exports = api => {
  const isTest = api.env('test');
  // You can use isTest to determine what presets and plugins to use.

  return {
    // ...
  };
};
```

### ESLint Configuration

Configure ESLint for Jest globals:

```json
{
  "overrides": [
    {
      "files": ["tests/**/*"],
      "env": {
        "jest": true
      }
    }
  ]
}
```

Or with eslint-plugin-jest:

```json
{
  "overrides": [
    {
      "files": ["tests/**/*"],
      "plugins": ["jest"],
      "env": {
        "jest/globals": true
      }
    }
  ]
}
```

Using globals package:

```javascript
import {defineConfig} from 'eslint/config';
import globals from 'globals';

export default defineConfig([
  {
    files: ['**/*.js'],
    languageOptions: {
      globals: {
        ...globals.jest,
      },
    },
    rules: {
      'no-unused-vars': 'warn',
      'no-undef': 'warn',
    },
  },
]);
```

### TypeScript Setup

Install type definitions:

```bash
# Jest globals (preferred)
npm install --save-dev @jest/globals

# Alternative (third-party)
npm install --save-dev @types/jest
```

Using explicit imports:

```typescript
import {describe, expect, test} from '@jest/globals';
import {sum} from './sum';

describe('sum module', () => {
  test('adds 1 + 2 to equal 3', () => {
    expect(sum(1, 2)).toBe(3);
  });
});
```

### Configuration File Options

#### Basic Jest Configuration

```javascript
/** @type {import('jest').Config} */
const config = {
  // Basic options
  testEnvironment: 'node', // or 'jsdom' for browser-like environment
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  
  // Coverage
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  
  // Setup
  setupFilesAfterEnv: ['<rootDir>/setup-jest.js'],
  
  // Module resolution
  moduleDirectories: ['node_modules', '<rootDir>/src'],
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'json'],
};

module.exports = config;
```

#### TypeScript Configuration

```typescript
import type {Config} from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
};

export default config;
```

### Disabling Babel Transform

If you don't want Babel transformation:

```javascript
// jest.config.js
module.exports = {
  transform: {},
};
```

---

## Jest CLI Options

### Core Commands

```bash
# Run all tests
jest

# Run tests in watch mode
jest --watch

# Run all tests in watch mode
jest --watchAll

# Run tests with coverage
jest --coverage

# Update snapshots
jest --updateSnapshot

# Run specific test
jest my-test.js

# Run tests matching pattern
jest --testNamePattern="sum"

# Run tests from specific directory
jest tests/
```

### Complete CLI Reference

#### Basic Options

```bash
# Display help
jest --help

# Show version
jest --version

# Display configuration
jest --showConfig

# Generate configuration
jest --init
```

#### Test Execution

```bash
# Run tests in serial (no parallel)
jest --runInBand

# Limit worker processes
jest --maxWorkers=4
jest --maxWorkers=50%

# Force exit after tests
jest --forceExit

# Set test timeout
jest --testTimeout=10000
```

#### Test Selection

```bash
# Run only changed files
jest --onlyChanged

# Run tests related to changed files since last commit
jest --lastCommit

# Run tests related to specific files
jest --findRelatedTests src/sum.js src/multiply.js

# Run tests matching name pattern
jest --testNamePattern="should add"

# Run tests in specific projects
jest --selectProjects unit integration

# Ignore specific projects
jest --ignoreProjects e2e
```

#### Coverage Options

```bash
# Enable coverage collection
jest --coverage

# Specify coverage directory
jest --coverageDirectory=reports

# Set coverage provider
jest --coverageProvider=v8
jest --coverageProvider=babel

# Collect coverage from specific files
jest --collectCoverageFrom="src/**/*.js"
```

#### Output and Reporting

```bash
# Silent mode (no console output)
jest --silent

# Verbose output (show individual tests)
jest --verbose

# Expand error diffs
jest --expand

# Disable stack traces
jest --noStackTrace

# JSON output
jest --json

# Output to file
jest --outputFile=results.json

# Enable OS notifications
jest --notify

# Use specific reporters
jest --reporters="default" --reporters="jest-junit"
```

#### Watch Mode Options

```bash
# Watch files for changes
jest --watch

# Watch all files
jest --watchAll

# Disable watchman
jest --no-watchman
```

#### Environment and Setup

```bash
# Set test environment
jest --env=jsdom
jest --env=node

# Pass options to test environment
jest --testEnvironmentOptions='{"url": "http://localhost"}'

# Use custom config file
jest --config=custom-jest.config.js

# Set root directory
jest --rootDir=src
```

#### Advanced Options

```bash
# CI mode (fail on new snapshots)
jest --ci

# Clear cache
jest --clearCache

# Detect open handles
jest --detectOpenHandles

# Enable debugging
jest --debug

# List all tests without running
jest --listTests

# Randomize test order
jest --randomize

# Use specific seed for randomization
jest --seed=12345

# Show seed used for randomization
jest --showSeed

# Shard tests across multiple machines
jest --shard=1/3
jest --shard=2/3
jest --shard=3/3
```

#### Passing Arguments Through Package Managers

```bash
# npm
npm test -- --coverage --verbose

# Yarn
yarn test --coverage --verbose

# pnpm
pnpm test -- --coverage --verbose
```

---

## Expect API & Matchers

### Core Expect Function

```javascript
// Basic usage
expect(value).toBe(expected);

// With modifiers
expect(value).not.toBe(unexpected);
expect(promise).resolves.toBe(expected);
expect(promise).rejects.toThrow(error);
```

### Modifiers

#### `.not`
Negates the assertion:

```javascript
test('the best flavor is not coconut', () => {
  expect(bestLaCroixFlavor()).not.toBe('coconut');
});
```

#### `.resolves`
Unwraps fulfilled promises:

```javascript
test('resolves to lemon', () => {
  return expect(Promise.resolve('lemon')).resolves.toBe('lemon');
});

test('resolves to lemon', async () => {
  await expect(Promise.resolve('lemon')).resolves.toBe('lemon');
  await expect(Promise.resolve('lemon')).resolves.not.toBe('octopus');
});
```

#### `.rejects`
Unwraps rejected promises:

```javascript
test('rejects to octopus', () => {
  return expect(Promise.reject(new Error('octopus'))).rejects.toThrow('octopus');
});

test('rejects to octopus', async () => {
  await expect(Promise.reject(new Error('octopus'))).rejects.toThrow('octopus');
});
```

### Equality Matchers

#### `.toBe(value)`
Strict equality (`Object.is`):

```javascript
test('the best flavor is grapefruit', () => {
  expect(bestLaCroixFlavor()).toBe('grapefruit');
});
```

#### `.toEqual(value)`
Deep equality:

```javascript
test('object assignment', () => {
  const data = {one: 1};
  data['two'] = 2;
  expect(data).toEqual({one: 1, two: 2});
});
```

#### `.toStrictEqual(value)`
Strict deep equality (checks types):

```javascript
test('strict equality', () => {
  expect({a: 1}).toStrictEqual({a: 1});
  // This would fail: expect({a: 1, b: undefined}).toStrictEqual({a: 1});
});
```

### Truthiness Matchers

```javascript
// Truthy/Falsy
expect(value).toBeTruthy();
expect(value).toBeFalsy();

// Specific values
expect(value).toBeUndefined();
expect(value).toBeDefined();
expect(value).toBeNull();
expect(value).toBeNaN();
```

### Number Matchers

```javascript
// Comparisons
expect(2 + 2).toBeGreaterThan(3);
expect(2 + 2).toBeGreaterThanOrEqual(4);
expect(2 + 2).toBeLessThan(5);
expect(2 + 2).toBeLessThanOrEqual(4);

// Floating point
expect(0.1 + 0.2).toBeCloseTo(0.3);
expect(0.1 + 0.2).toBeCloseTo(0.3, 5); // 5 decimal places
```

### String Matchers

```javascript
// Substring/regex matching
expect('team').not.toMatch(/I/);
expect('Christoph').toMatch(/stop/);
expect('hello world').toMatch('world');

// String containing
expect('hello world').toEqual(expect.stringContaining('world'));
expect('hello world').toEqual(expect.not.stringContaining('goodbye'));

// String matching regex
expect('hello world').toEqual(expect.stringMatching(/world/));
expect('hello world').toEqual(expect.not.stringMatching(/goodbye/));
```

### Array and Iterable Matchers

```javascript
// Length
expect(['Alice', 'Bob', 'Eve']).toHaveLength(3);
expect('abc').toHaveLength(3);

// Contains item
expect(['Alice', 'Bob', 'Eve']).toContain('Alice');

// Contains equal item (deep equality)
expect([{name: 'Alice'}, {name: 'Bob'}]).toContainEqual({name: 'Alice'});

// Array containing subset
expect(['Alice', 'Bob', 'Eve']).toEqual(
  expect.arrayContaining(['Alice', 'Bob'])
);

// All items match
expect(['apple', 'banana', 'cherry']).toEqual(
  expect.arrayOf(expect.any(String))
);
```

### Object Matchers

```javascript
// Has property
expect({name: 'Alice', age: 30}).toHaveProperty('name');
expect({name: 'Alice', age: 30}).toHaveProperty('name', 'Alice');
expect({user: {name: 'Alice'}}).toHaveProperty('user.name', 'Alice');

// Object containing subset
expect({name: 'Alice', age: 30, city: 'NY'}).toEqual(
  expect.objectContaining({
    name: 'Alice',
    age: 30
  })
);

// Partial object matching
expect({name: 'Alice', age: 30}).toMatchObject({name: 'Alice'});
```

### Instance and Type Matchers

```javascript
class Cat {}
const cat = new Cat();

expect(cat).toBeInstanceOf(Cat);
expect(new Date()).toBeInstanceOf(Date);

// Type checking with any()
expect(mockFunction).toHaveBeenCalledWith(expect.any(Number));
expect({name: 'Alice'}).toEqual({
  name: expect.any(String)
});
```

### Exception Matchers

```javascript
// Basic throw assertion
expect(() => {
  throw new Error('Wrong!');
}).toThrow();

// Specific error message
expect(() => {
  throw new Error('Wrong!');
}).toThrow('Wrong!');

// Error message matching regex
expect(() => {
  throw new Error('Wrong!');
}).toThrow(/Wrong/);

// Specific error class
expect(() => {
  throw new CustomError('Something');
}).toThrow(CustomError);

// Exact error object
expect(() => {
  throw new Error('Exact message');
}).toThrow(new Error('Exact message'));
```

### Mock Function Matchers

```javascript
const mockFn = jest.fn();

// Called assertions
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith(arg1, arg2);
expect(mockFn).toHaveBeenLastCalledWith(arg1, arg2);
expect(mockFn).toHaveBeenNthCalledWith(1, arg1, arg2);

// Return value assertions
expect(mockFn).toHaveReturned();
expect(mockFn).toHaveReturnedTimes(2);
expect(mockFn).toHaveReturnedWith(value);
expect(mockFn).toHaveLastReturnedWith(value);
expect(mockFn).toHaveNthReturnedWith(1, value);
```

### Asymmetric Matchers

```javascript
// Anything except null/undefined
expect(mockFn).toHaveBeenCalledWith(expect.anything());

// Any instance of constructor
expect(mockFn).toHaveBeenCalledWith(expect.any(Number));
expect(mockFn).toHaveBeenCalledWith(expect.any(String));

// Array containing elements
expect(['Alice', 'Bob', 'Eve']).toEqual(
  expect.arrayContaining(['Alice', 'Bob'])
);

// Object containing properties
expect({name: 'Alice', age: 30}).toEqual(
  expect.objectContaining({name: 'Alice'})
);

// String patterns
expect('hello world').toEqual(expect.stringContaining('world'));
expect('hello world').toEqual(expect.stringMatching(/world/));

// Close to number
expect(0.1 + 0.2).toEqual(expect.closeTo(0.3));
```

### Snapshot Matchers

```javascript
// Basic snapshot
expect(tree).toMatchSnapshot();

// Snapshot with hint
expect(tree).toMatchSnapshot('tree component');

// Inline snapshot
expect(tree).toMatchInlineSnapshot(`
  <div>
    Hello World
  </div>
`);

// Property matchers
expect(user).toMatchSnapshot({
  createdAt: expect.any(Date),
  id: expect.any(Number),
});
```

### Assertion Count

```javascript
// Verify exact number of assertions
test('doAsync calls both callbacks', () => {
  expect.assertions(2);
  function callback1(data) {
    expect(data).toBeTruthy();
  }
  function callback2(data) {
    expect(data).toBeTruthy();
  }
  doAsync(callback1, callback2);
});

// Verify at least one assertion
test('prepareState prepares a valid state', () => {
  expect.hasAssertions();
  prepareState(state => {
    expect(validateState(state)).toBeTruthy();
  });
  return waitOnState();
});
```

---

## Mocking & Spies

### Jest Mock Functions

#### Creating Mock Functions

```javascript
// Basic mock function
const mockFn = jest.fn();

// Mock with return value
const mockFn = jest.fn(() => 42);

// Mock with implementation
const mockFn = jest.fn((x, y) => x + y);

// Mock with name (for debugging)
const mockFn = jest.fn().mockName('myMockFunction');
```

#### Mock Return Values

```javascript
const mockFn = jest.fn();

// Single return value
mockFn.mockReturnValue(42);

// Return value once
mockFn.mockReturnValueOnce(10);
mockFn.mockReturnValueOnce(20);

// Resolved promise
mockFn.mockResolvedValue('resolved');
mockFn.mockResolvedValueOnce('resolved once');

// Rejected promise
mockFn.mockRejectedValue(new Error('rejected'));
mockFn.mockRejectedValueOnce(new Error('rejected once'));
```

#### Mock Implementation

```javascript
const mockFn = jest.fn();

// Set implementation
mockFn.mockImplementation((a, b) => a + b);

// Implementation once
mockFn.mockImplementationOnce((a, b) => a * b);

// Clear implementation
mockFn.mockRestore(); // Only for jest.spyOn
mockFn.mockReset(); // Clear calls and return values
mockFn.mockClear(); // Clear calls only
```

#### Accessing Mock Data

```javascript
const mockFn = jest.fn();

// Call information
mockFn.mock.calls; // Array of call arguments
mockFn.mock.results; // Array of return values
mockFn.mock.instances; // Array of `this` values

// Example usage
mockFn('arg1', 'arg2');
mockFn('arg3', 'arg4');

console.log(mockFn.mock.calls);
// [['arg1', 'arg2'], ['arg3', 'arg4']]

console.log(mockFn.mock.calls.length); // 2
console.log(mockFn.mock.calls[0][0]); // 'arg1'
```

### Module Mocking

#### Automatic Mocking

```javascript
// Mock entire module
jest.mock('./path/to/module');

// Mock with factory function
jest.mock('./path/to/module', () => ({
  default: jest.fn(() => 'mocked'),
  namedExport: jest.fn(),
}));

// Partial mocking
jest.mock('./path/to/module', () => ({
  ...jest.requireActual('./path/to/module'),
  specificFunction: jest.fn(),
}));
```

#### Manual Mocks

Create `__mocks__` directory:

```
project/
├── __mocks__/
│   ├── fs.js
│   └── lodash.js
├── src/
└── package.json
```

Example manual mock for Node.js `fs` module:

```javascript
// __mocks__/fs.js
'use strict';

const path = require('path');
const fs = jest.createMockFromModule('fs');

// Custom function for tests to set mock files
let mockFiles = Object.create(null);
function __setMockFiles(newMockFiles) {
  mockFiles = Object.create(null);
  for (const file in newMockFiles) {
    const dir = path.dirname(file);
    if (!mockFiles[dir]) {
      mockFiles[dir] = [];
    }
    mockFiles[dir].push(path.basename(file));
  }
}

// Mock implementation of readdirSync
function readdirSync(directoryPath) {
  return mockFiles[directoryPath] || [];
}

fs.__setMockFiles = __setMockFiles;
fs.readdirSync = readdirSync;

module.exports = fs;
```

#### ES Module Mocking

```javascript
// Mock ES module
jest.mock('./esModule', () => ({
  __esModule: true,
  default: jest.fn(),
  namedExport: jest.fn(),
}));

// Using dynamic imports
const mockModule = await import('./esModule');
mockModule.default.mockReturnValue('mocked');
```

### Spying on Methods

#### Object Method Spies

```javascript
const myObject = {
  method: (a, b) => a + b,
};

// Spy on method
const spy = jest.spyOn(myObject, 'method');

// Test usage
myObject.method(1, 2);
expect(spy).toHaveBeenCalledWith(1, 2);

// Restore original implementation
spy.mockRestore();
```

#### Property Spies

```javascript
const myObject = {
  get value() {
    return 42;
  },
  set value(val) {
    // setter logic
  }
};

// Spy on getter
const getSpy = jest.spyOn(myObject, 'value', 'get');
getSpy.mockReturnValue(100);

// Spy on setter
const setSpy = jest.spyOn(myObject, 'value', 'set');
```

#### Global Function Spies

```javascript
// Spy on global functions
const consoleSpy = jest.spyOn(console, 'log');
console.log('test');
expect(consoleSpy).toHaveBeenCalledWith('test');

// Spy on Date constructor
const dateSpy = jest.spyOn(global, 'Date');
dateSpy.mockImplementation(() => new Date('2020-01-01'));
```

### Timer Mocking

#### Fake Timers

```javascript
// Enable fake timers
jest.useFakeTimers();

// Test setTimeout
test('should call callback after timeout', () => {
  const callback = jest.fn();
  setTimeout(callback, 1000);

  // Fast-forward time
  jest.advanceTimersByTime(1000);
  expect(callback).toHaveBeenCalled();
});

// Test setInterval
test('should call callback multiple times', () => {
  const callback = jest.fn();
  setInterval(callback, 1000);

  jest.advanceTimersByTime(3000);
  expect(callback).toHaveBeenCalledTimes(3);
});

// Run all timers
jest.runAllTimers();

// Run only pending timers
jest.runOnlyPendingTimers();

// Restore real timers
jest.useRealTimers();
```

#### Modern Timer API

```javascript
// Use modern fake timers (Jest 27+)
jest.useFakeTimers({
  advanceTimers: true,
  doNotFake: ['nextTick'],
});

// Legacy timer API
jest.useFakeTimers('legacy');
```

### Advanced Mocking Patterns

#### Mocking Classes

```javascript
// Mock class constructor
jest.mock('./SomeClass');
const SomeClass = require('./SomeClass');

// Mock specific methods
SomeClass.mockImplementation(() => ({
  method: jest.fn(() => 'mocked result'),
}));

// Mock static methods
SomeClass.staticMethod = jest.fn();
```

#### Mocking Modules with Hoisting

```javascript
// Variables are hoisted above imports
const mockFunction = jest.fn();
jest.mock('./module', () => ({
  someFunction: mockFunction,
}));

// Now imports will use the mock
const { someFunction } = require('./module');
```

#### Conditional Mocking

```javascript
// Mock only in test environment
if (process.env.NODE_ENV === 'test') {
  jest.mock('./expensiveModule', () => ({
    expensiveFunction: jest.fn(() => 'mocked'),
  }));
}
```

#### Clearing and Resetting Mocks

```javascript
// Clear all mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
});

// Reset all mocks
beforeEach(() => {
  jest.resetAllMocks();
});

// Restore all mocks
afterEach(() => {
  jest.restoreAllMocks();
});
```

---

## Asynchronous Testing

### Testing Promises

#### Using async/await

```javascript
test('async data fetch', async () => {
  const data = await fetchData();
  expect(data).toBe('peanut butter');
});

test('async error handling', async () => {
  await expect(fetchData()).rejects.toThrow('error');
});
```

#### Using return

```javascript
test('promise resolves', () => {
  return fetchData().then(data => {
    expect(data).toBe('peanut butter');
  });
});

test('promise rejects', () => {
  return fetchData().catch(error => {
    expect(error.message).toMatch('error');
  });
});
```

#### Using resolves/rejects

```javascript
test('resolves to peanut butter', () => {
  return expect(fetchData()).resolves.toBe('peanut butter');
});

test('rejects with error', () => {
  return expect(fetchData()).rejects.toThrow('error');
});

// With async/await
test('resolves to peanut butter', async () => {
  await expect(fetchData()).resolves.toBe('peanut butter');
});
```

### Callback Testing

```javascript
// DON'T do this - test will pass before callback
test('callback data', () => {
  function callback(data) {
    expect(data).toBe('peanut butter');
  }
  fetchData(callback);
});

// DO this - use done callback
test('callback data', done => {
  function callback(data) {
    try {
      expect(data).toBe('peanut butter');
      done();
    } catch (error) {
      done(error);
    }
  }
  fetchData(callback);
});

// Better - promisify or use async/await
```

### Testing Multiple Async Operations

```javascript
test('multiple promises', async () => {
  const [result1, result2] = await Promise.all([
    fetchData('user1'),
    fetchData('user2'),
  ]);
  
  expect(result1).toBe('user1 data');
  expect(result2).toBe('user2 data');
});

test('sequential async operations', async () => {
  const user = await fetchUser('123');
  const posts = await fetchUserPosts(user.id);
  
  expect(posts).toHaveLength(5);
});
```

### Testing with Fake Timers

```javascript
test('async operation with timeout', async () => {
  jest.useFakeTimers();
  
  const promise = new Promise(resolve => {
    setTimeout(() => resolve('done'), 1000);
  });
  
  // Advance timers before awaiting
  jest.advanceTimersByTime(1000);
  
  const result = await promise;
  expect(result).toBe('done');
  
  jest.useRealTimers();
});
```

### Testing API Calls

```javascript
// Mock fetch
global.fetch = jest.fn();

test('api call success', async () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ id: 1, name: 'John' }),
  });

  const user = await fetchUser(1);
  
  expect(fetch).toHaveBeenCalledWith('/api/users/1');
  expect(user).toEqual({ id: 1, name: 'John' });
});

test('api call failure', async () => {
  fetch.mockRejectedValueOnce(new Error('Network error'));

  await expect(fetchUser(1)).rejects.toThrow('Network error');
});
```

### Testing Observables (RxJS)

```javascript
import { of, throwError } from 'rxjs';
import { marbles } from 'rxjs-marbles/jest';

test('observable success', marbles(m => {
  const source = m.cold('--a--b--c--|', { a: 1, b: 2, c: 3 });
  const expected = m.cold('--a--b--c--|', { a: 2, b: 4, c: 6 });
  
  const result = source.pipe(map(x => x * 2));
  
  m.expect(result).toBeObservable(expected);
}));
```

---

## Snapshot Testing

### Basic Snapshot Testing

#### Creating Snapshots

```javascript
import renderer from 'react-test-renderer';
import Link from '../Link';

test('Link renders correctly', () => {
  const tree = renderer
    .create(<Link page="http://www.facebook.com">Facebook</Link>)
    .toJSON();
  expect(tree).toMatchSnapshot();
});
```

Generated snapshot file (`.snap`):

```javascript
exports[`Link renders correctly 1`] = `
<a
  className="normal"
  href="http://www.facebook.com"
  onMouseEnter={[Function]}
  onMouseLeave={[Function]}
>
  Facebook
</a>
`;
```

#### Updating Snapshots

```bash
# Update all snapshots
jest --updateSnapshot

# Update specific test snapshots
jest --updateSnapshot --testNamePattern="Link"
```

### Inline Snapshots

#### Basic Inline Snapshots

```javascript
test('inline snapshot', () => {
  const tree = renderer.create(<Component />).toJSON();
  expect(tree).toMatchInlineSnapshot(`
    <div>
      <h1>Hello World</h1>
    </div>
  `);
});
```

#### Before/After Inline Snapshot Creation

Before first run:
```javascript
test('renders correctly', () => {
  const tree = renderer.create(<Link page="https://example.com">Example</Link>).toJSON();
  expect(tree).toMatchInlineSnapshot();
});
```

After first run:
```javascript
test('renders correctly', () => {
  const tree = renderer.create(<Link page="https://example.com">Example</Link>).toJSON();
  expect(tree).toMatchInlineSnapshot(`
    <a
      className="normal"
      href="https://example.com"
      onMouseEnter={[Function]}
      onMouseLeave={[Function]}
    >
      Example
    </a>
  `);
});
```

### Property Matchers

#### Handling Dynamic Values

```javascript
// This will fail due to dynamic data
test('user snapshot with dynamic data', () => {
  const user = {
    createdAt: new Date(),
    id: Math.floor(Math.random() * 20),
    name: 'LeBron James',
  };

  expect(user).toMatchSnapshot(); // ❌ Will fail every time
});

// Use property matchers for dynamic values
test('user snapshot with property matchers', () => {
  const user = {
    createdAt: new Date(),
    id: Math.floor(Math.random() * 20),
    name: 'LeBron James',
  };

  expect(user).toMatchSnapshot({
    createdAt: expect.any(Date),
    id: expect.any(Number),
  }); // ✅ Will pass consistently
});
```

Generated snapshot with property matchers:
```javascript
exports[`user snapshot with property matchers 1`] = `
{
  "createdAt": Any<Date>,
  "id": Any<Number>,
  "name": "LeBron James",
}
`;
```

#### Mixed Property Matching

```javascript
test('mixed property matching', () => {
  const user = {
    createdAt: new Date(),
    name: 'Bond... James Bond',
  };

  expect(user).toMatchSnapshot({
    createdAt: expect.any(Date),
    name: 'Bond... James Bond', // Exact match
  });
});
```

### Snapshot Best Practices

#### Descriptive Snapshot Names

```javascript
// ❌ Poor naming
exports[`<UserName /> should handle some test case`] = `null`;

// ✅ Good naming
exports[`<UserName /> should render null when no user provided`] = `null`;
exports[`<UserName /> should render user name when user provided`] = `
<div>
  John Doe
</div>
`;
```

#### Multiple Snapshots with Hints

```javascript
test('component states', () => {
  expect(getInitialState()).toMatchSnapshot('initial state');
  expect(getLoadingState()).toMatchSnapshot('loading state');
  expect(getErrorState()).toMatchSnapshot('error state');
});
```

#### Preprocessing Dynamic Data

```javascript
test('component with random data', () => {
  const randomNumber = Math.round(Math.random() * 100);
  const html = `<div id="${randomNumber}">Content</div>`;
  
  // Normalize random data before snapshot
  const normalizedHtml = html.replace(/id="\d+"/, 'id="123"');
  expect(normalizedHtml).toMatchSnapshot();
});
```

#### Mocking Non-Deterministic Values

```javascript
// Mock Date.now for consistent snapshots
Date.now = jest.fn(() => 1482363367071);

test('component with timestamp', () => {
  const component = <TimestampComponent />;
  expect(renderer.create(component).toJSON()).toMatchSnapshot();
});
```

### Interactive Testing

#### Testing Component State Changes

```javascript
import renderer from 'react-test-renderer';

test('Link changes class when hovered', () => {
  const component = renderer.create(
    <Link page="http://www.facebook.com">Facebook</Link>
  );
  
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot('normal state');

  // Trigger hover
  renderer.act(() => {
    tree.props.onMouseEnter();
  });
  
  tree = component.toJSON();
  expect(tree).toMatchSnapshot('hovered state');

  // Trigger mouse leave
  renderer.act(() => {
    tree.props.onMouseLeave();
  });
  
  tree = component.toJSON();
  expect(tree).toMatchSnapshot('normal state again');
});
```

### Error Snapshots

```javascript
function drinkFlavor(flavor) {
  if (flavor === 'octopus') {
    throw new DisgustingFlavorError('yuck, octopus flavor');
  }
}

test('throws on octopus', () => {
  function drinkOctopus() {
    drinkFlavor('octopus');
  }

  expect(drinkOctopus).toThrowErrorMatchingSnapshot();
});

test('throws on octopus with inline snapshot', () => {
  function drinkOctopus() {
    drinkFlavor('octopus');
  }

  expect(drinkOctopus).toThrowErrorMatchingInlineSnapshot(
    `"yuck, octopus flavor"`
  );
});
```

### Custom Snapshot Serializers

#### Built-in Serializers

Jest includes serializers for common types:
- React elements
- React test instances
- Immutable data structures

#### Adding Custom Serializers

```javascript
// Add serializer per test file
import serializer from 'my-serializer';
expect.addSnapshotSerializer(serializer);

// Global configuration
module.exports = {
  snapshotSerializers: ['my-serializer'],
};
```

#### Creating Custom Serializers

```javascript
// custom-serializer.js
module.exports = {
  serialize(val, config, indentation, depth, refs, printer) {
    return `Pretty ${val.constructor.name}: ${printer(val.value)}`;
  },
  
  test(val) {
    return val && val.constructor && val.constructor.name === 'MyClass';
  },
};
```

---

## Coverage & Watch Mode

### Code Coverage

#### Enabling Coverage

```bash
# Command line
jest --coverage

# Configuration
jest --coverage --coverageDirectory=reports

# Package.json script
{
  "scripts": {
    "test:coverage": "jest --coverage"
  }
}
```

#### Coverage Configuration

```javascript
// jest.config.js
module.exports = {
  // Enable coverage collection
  collectCoverage: true,
  
  // Coverage directory
  coverageDirectory: 'coverage',
  
  // Coverage reporters
  coverageReporters: ['text', 'lcov', 'html', 'json'],
  
  // Files to collect coverage from
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!src/index.js',
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
    './src/components/': {
      branches: 90,
      statements: 90,
    },
  },
  
  // Coverage provider
  coverageProvider: 'v8', // or 'babel'
  
  // Ignore patterns
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/coverage/',
    '/.next/',
  ],
};
```

#### Coverage Reporters

```javascript
module.exports = {
  coverageReporters: [
    'text',           // Console output
    'text-summary',   // Summary in console
    'html',          // HTML report
    'lcov',          // LCOV format
    'json',          // JSON format
    'clover',        // Clover XML
    'cobertura',     // Cobertura XML
    ['text', { skipFull: true }], // Text without fully covered files
  ],
};
```

#### Force Coverage Matching

```javascript
module.exports = {
  // Force coverage collection for these files even if not imported
  forceCoverageMatch: [
    '**/src/**/*.js',
    '!**/node_modules/**',
  ],
};
```

### Watch Mode

#### Basic Watch Commands

```bash
# Watch related files only
jest --watch

# Watch all files
jest --watchAll

# Disable watch mode
jest --no-watch
```

#### Watch Mode Interface

When in watch mode, Jest provides an interactive interface:

```
Watch Usage
 › Press f to run only failed tests.
 › Press o to only run tests related to changed files.
 › Press p to filter by a filename regex pattern.
 › Press t to filter by a test name regex pattern.
 › Press u to update failing snapshots.
 › Press i to update failing snapshots interactively.
 › Press q to quit watch mode.
 › Press Enter to trigger a test run.
```

#### Watch Configuration

```javascript
module.exports = {
  // Watch mode options
  watchman: true,                    // Use Watchman if available
  watchPathIgnorePatterns: [        // Ignore these paths
    '/node_modules/',
    '/coverage/',
    '/.git/',
  ],
  
  // Watch plugins
  watchPlugins: [
    'jest-watch-node-modules',
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],
};
```

#### Custom Watch Plugins

```javascript
// my-watch-plugin.js
class MyWatchPlugin {
  constructor({ config }) {
    this.config = config;
  }

  apply(jestHooks) {
    jestHooks.onFileChange(({ projects }) => {
      console.log('Files changed:', projects);
    });

    jestHooks.onTestRunComplete((results) => {
      if (results.snapshot.failure) {
        console.log('Snapshot tests failed!');
      }
    });

    jestHooks.shouldRunTestSuite((testSuiteInfo) => {
      return testSuiteInfo.testPath.includes('important');
    });
  }

  getUsageInfo() {
    return {
      key: 'm',
      prompt: 'show module dependencies',
    };
  }

  run(globalConfig, updateConfigAndRun) {
    console.log('Running custom watch command...');
    return Promise.resolve(false); // Don't trigger test run
  }
}

module.exports = MyWatchPlugin;
```

### Performance and Optimization

#### Running Tests in Parallel

```bash
# Control worker processes
jest --maxWorkers=4
jest --maxWorkers=50%

# Run tests serially
jest --runInBand
```

#### Cache Configuration

```javascript
module.exports = {
  // Cache directory
  cacheDirectory: '/tmp/jest-cache',
  
  // Clear cache
  clearMocks: true,
};
```

```bash
# Clear cache manually
jest --clearCache
```

#### Test Selection Optimization

```bash
# Run only changed files
jest --onlyChanged

# Run related tests
jest --findRelatedTests src/modified-file.js

# Run tests matching pattern
jest --testPathPattern=components

# Run specific test names
jest --testNamePattern="should render"
```

---

## Setup & Teardown

### Lifecycle Hooks

#### Global Hooks

```javascript
// Run once before all tests
beforeAll(() => {
  return initializeDatabase();
});

// Run once after all tests
afterAll(() => {
  return clearDatabase();
});
```

#### Per-Test Hooks

```javascript
// Run before each test
beforeEach(() => {
  initializeCity();
});

// Run after each test
afterEach(() => {
  clearCity();
});
```

#### Async Hooks

```javascript
// With promises
beforeEach(() => {
  return initializeCityDatabase();
});

// With async/await
beforeEach(async () => {
  await initializeCityDatabase();
});

// With done callback
beforeEach(done => {
  initializeCityDatabase(() => {
    done();
  });
});
```

### Hook Scoping

#### File-Level vs Describe-Level

```javascript
// Applies to all tests in the file
beforeEach(() => {
  return initializeCityDatabase();
});

test('city database has Vienna', () => {
  expect(isCity('Vienna')).toBeTruthy();
});

describe('matching cities to foods', () => {
  // Applies only to tests in this describe block
  beforeEach(() => {
    return initializeFoodDatabase();
  });

  test('Vienna <3 veal', () => {
    expect(isValidCityFoodPair('Vienna', 'Wiener Schnitzel')).toBe(true);
  });
});
```

#### Hook Execution Order

```javascript
beforeAll(() => console.log('1 - beforeAll'));
afterAll(() => console.log('1 - afterAll'));
beforeEach(() => console.log('1 - beforeEach'));
afterEach(() => console.log('1 - afterEach'));

test('', () => console.log('1 - test'));

describe('Scoped / Nested block', () => {
  beforeAll(() => console.log('2 - beforeAll'));
  afterAll(() => console.log('2 - afterAll'));
  beforeEach(() => console.log('2 - beforeEach'));
  afterEach(() => console.log('2 - afterEach'));

  test('', () => console.log('2 - test'));
});

// Output:
// 1 - beforeAll
// 1 - beforeEach
// 1 - test
// 1 - afterEach
// 2 - beforeAll
// 1 - beforeEach
// 2 - beforeEach
// 2 - test
// 2 - afterEach
// 1 - afterEach
// 2 - afterAll
// 1 - afterAll
```

### Dependent Resource Management

```javascript
// Setup in order
beforeEach(() => console.log('connection setup'));
beforeEach(() => console.log('database setup'));

// Teardown in reverse order
afterEach(() => console.log('database teardown'));
afterEach(() => console.log('connection teardown'));

test('test 1', () => console.log('test 1'));

describe('extra', () => {
  beforeEach(() => console.log('extra database setup'));
  afterEach(() => console.log('extra database teardown'));

  test('test 2', () => console.log('test 2'));
});

// Output for test 1:
// connection setup
// database setup
// test 1
// database teardown
// connection teardown

// Output for test 2:
// connection setup
// database setup
// extra database setup
// test 2
// extra database teardown
// database teardown
// connection teardown
```

### Global Setup and Teardown

#### Configuration Files

```javascript
// jest.config.js
module.exports = {
  globalSetup: '<rootDir>/setup.js',
  globalTeardown: '<rootDir>/teardown.js',
};
```

#### Global Setup Example

```javascript
// setup.js
module.exports = async function() {
  console.log('Setting up global test environment...');
  
  // Start test database
  await startTestDatabase();
  
  // Set global variables
  global.__DATABASE_URL__ = 'test-database-url';
  
  // Start test server
  const server = await startTestServer();
  global.__SERVER_PORT__ = server.port;
};
```

#### Global Teardown Example

```javascript
// teardown.js
module.exports = async function() {
  console.log('Tearing down global test environment...');
  
  // Stop test database
  await stopTestDatabase();
  
  // Stop test server
  await stopTestServer();
  
  // Clean up files
  await cleanupTempFiles();
};
```

### Setup Files

#### setupFiles vs setupFilesAfterEnv

```javascript
// jest.config.js
module.exports = {
  // Run before test framework is installed
  setupFiles: ['<rootDir>/setup-before.js'],
  
  // Run after test framework is installed
  setupFilesAfterEnv: ['<rootDir>/setup-after.js'],
};
```

#### setupFiles Example

```javascript
// setup-before.js
// Configure environment variables
process.env.NODE_ENV = 'test';
process.env.API_URL = 'http://localhost:3001';

// Polyfills
require('whatwg-fetch');

// Global mocks
global.fetch = jest.fn();
```

#### setupFilesAfterEnv Example

```javascript
// setup-after.js
import 'jest-extended'; // Additional matchers

// Custom matchers
expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;
    return {
      message: () => 
        `expected ${received} ${pass ? 'not ' : ''}to be within range ${floor} - ${ceiling}`,
      pass,
    };
  },
});

// Global test helpers
global.testHelper = {
  createUser: (overrides = {}) => ({
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    ...overrides,
  }),
};

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
  jest.useRealTimers();
});
```

### Describe Block Execution

```javascript
describe('describe outer', () => {
  console.log('describe outer-a');

  describe('describe inner 1', () => {
    console.log('describe inner 1');
    test('test 1', () => console.log('test 1'));
  });

  console.log('describe outer-b');
  test('test 2', () => console.log('test 2'));

  describe('describe inner 2', () => {
    console.log('describe inner 2');
    test('test 3', () => console.log('test 3'));
  });

  console.log('describe outer-c');
});

// Output:
// describe outer-a
// describe inner 1
// describe outer-b
// describe inner 2
// describe outer-c
// test 1
// test 2
// test 3
```

### Test Isolation

#### Cleaning State Between Tests

```javascript
// Clear all mocks
beforeEach(() => {
  jest.clearAllMocks();
});

// Reset modules
beforeEach(() => {
  jest.resetModules();
});

// Restore spies
afterEach(() => {
  jest.restoreAllMocks();
});
```

#### Database Cleanup

```javascript
const db = require('./database');

beforeEach(async () => {
  await db.clean();
  await db.seed();
});

afterEach(async () => {
  await db.clean();
});
```

#### DOM Cleanup

```javascript
// Clean up DOM after each test
afterEach(() => {
  document.body.innerHTML = '';
  
  // Clean up event listeners
  window.removeAllListeners?.();
});
```

### Test Organization

#### Using describe.skip and test.skip

```javascript
describe('feature tests', () => {
  test('working test', () => {
    expect(true).toBe(true);
  });

  test.skip('broken test', () => {
    // This test will be skipped
    expect(true).toBe(false);
  });
});

describe.skip('entire suite to skip', () => {
  // All tests in this suite will be skipped
  test('skipped test', () => {
    expect(true).toBe(true);
  });
});
```

#### Using test.only

```javascript
describe('debugging tests', () => {
  test.only('only this test will run', () => {
    expect(true).toBe(true);
  });

  test('this test will be skipped', () => {
    expect(true).toBe(true);
  });
});
```

---

## Custom Matchers

### Creating Custom Matchers

#### Basic Custom Matcher Structure

```javascript
expect.extend({
  yourMatcher(received, expected) {
    const pass = /* your assertion logic */;
    
    return {
      pass,
      message: () => 
        pass 
          ? `expected ${received} not to match ${expected}`
          : `expected ${received} to match ${expected}`,
    };
  },
});
```

#### Example: toBeWithinRange Matcher

```javascript
// toBeWithinRange.js
import { expect } from '@jest/globals';

function toBeWithinRange(actual, floor, ceiling) {
  if (
    typeof actual !== 'number' ||
    typeof floor !== 'number' ||
    typeof ceiling !== 'number'
  ) {
    throw new TypeError('These must be of type number!');
  }

  const pass = actual >= floor && actual <= ceiling;
  
  if (pass) {
    return {
      message: () =>
        `expected ${this.utils.printReceived(actual)} not to be within range ${this.utils.printExpected(`${floor} - ${ceiling}`)}`,
      pass: true,
    };
  } else {
    return {
      message: () =>
        `expected ${this.utils.printReceived(actual)} to be within range ${this.utils.printExpected(`${floor} - ${ceiling}`)}`,
      pass: false,
    };
  }
}

expect.extend({
  toBeWithinRange,
});

export { toBeWithinRange };
```

#### Using Custom Matchers

```javascript
import { expect, test } from '@jest/globals';
import './toBeWithinRange';

test('is within range', () => expect(100).toBeWithinRange(90, 110));
test('is NOT within range', () => expect(101).not.toBeWithinRange(0, 100));

// As asymmetric matcher
test('asymmetric ranges', () => {
  expect({ apples: 6, bananas: 3 }).toEqual({
    apples: expect.toBeWithinRange(1, 10),
    bananas: expect.not.toBeWithinRange(11, 20),
  });
});
```

### TypeScript Custom Matchers

#### Matcher with TypeScript

```typescript
import { expect } from '@jest/globals';
import type { MatcherFunction } from 'expect';

const toBeWithinRange: MatcherFunction<[floor: unknown, ceiling: unknown]> =
  function (actual, floor, ceiling) {
    if (
      typeof actual !== 'number' ||
      typeof floor !== 'number' ||
      typeof ceiling !== 'number'
    ) {
      throw new TypeError('These must be of type number!');
    }

    const pass = actual >= floor && actual <= ceiling;
    
    if (pass) {
      return {
        message: () =>
          `expected ${this.utils.printReceived(actual)} not to be within range ${this.utils.printExpected(`${floor} - ${ceiling}`)}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected ${this.utils.printReceived(actual)} to be within range ${this.utils.printExpected(`${floor} - ${ceiling}`)}`,
        pass: false,
      };
    }
  };

expect.extend({
  toBeWithinRange,
});

// Type declarations
declare module 'expect' {
  interface AsymmetricMatchers {
    toBeWithinRange(floor: number, ceiling: number): void;
  }
  interface Matchers<R> {
    toBeWithinRange(floor: number, ceiling: number): R;
  }
}
```

### Advanced Custom Matchers

#### Async Custom Matcher

```javascript
expect.extend({
  async toBeDivisibleByExternalValue(received) {
    const externalValue = await getExternalValueFromRemoteSource();
    const pass = received % externalValue === 0;
    
    if (pass) {
      return {
        message: () =>
          `expected ${received} not to be divisible by ${externalValue}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected ${received} to be divisible by ${externalValue}`,
        pass: false,
      };
    }
  },
});

test('is divisible by external value', async () => {
  await expect(100).toBeDivisibleByExternalValue();
  await expect(101).not.toBeDivisibleByExternalValue();
});
```

#### Custom Matcher with Utilities

```javascript
const { diff } = require('jest-diff');

expect.extend({
  toBe(received, expected) {
    const options = {
      comment: 'Object.is equality',
      isNot: this.isNot,
      promise: this.promise,
    };

    const pass = Object.is(received, expected);

    const message = pass
      ? () =>
          this.utils.matcherHint('toBe', undefined, undefined, options) +
          '\n\n' +
          `Expected: not ${this.utils.printExpected(expected)}\n` +
          `Received: ${this.utils.printReceived(received)}`
      : () => {
          const diffString = diff(expected, received, {
            expand: this.expand,
          });
          return (
            this.utils.matcherHint('toBe', undefined, undefined, options) +
            '\n\n' +
            (diffString && diffString.includes('- Expect')
              ? `Difference:\n\n${diffString}`
              : `Expected: ${this.utils.printExpected(expected)}\n` +
                `Received: ${this.utils.printReceived(received)}`)
          );
        };

    return { actual: received, message, pass };
  },
});
```

### Snapshot Matchers

#### Custom Snapshot Matcher

```javascript
const { toMatchSnapshot } = require('jest-snapshot');

expect.extend({
  toMatchTrimmedSnapshot(received, length) {
    return toMatchSnapshot.call(
      this,
      received.slice(0, length),
      'toMatchTrimmedSnapshot',
    );
  },
});

test('stores only 10 characters', () => {
  expect('extra long string oh my gerd').toMatchTrimmedSnapshot(10);
});

// Snapshot will be:
// exports[`stores only 10 characters: toMatchTrimmedSnapshot 1`] = `"extra long"`;
```

#### Custom Inline Snapshot Matcher

```javascript
const { toMatchInlineSnapshot } = require('jest-snapshot');

expect.extend({
  toMatchTrimmedInlineSnapshot(received, ...rest) {
    return toMatchInlineSnapshot.call(this, received.slice(0, 10), ...rest);
  },
});

test('stores only 10 characters', () => {
  expect('extra long string oh my gerd').toMatchTrimmedInlineSnapshot();
  // Will become:
  // expect('extra long string oh my gerd').toMatchTrimmedInlineSnapshot(`"extra long"`);
});
```

#### Async Inline Snapshot Matcher

```javascript
const { toMatchInlineSnapshot } = require('jest-snapshot');

expect.extend({
  async toMatchObservationInlineSnapshot(fn, ...rest) {
    // Error must be created before any await
    this.error = new Error();

    const observation = await observe(async () => {
      await fn();
    });

    return toMatchInlineSnapshot.call(this, observation, ...rest);
  },
});

test('observes something', async () => {
  await expect(async () => {
    return 'async action';
  }).toMatchObservationInlineSnapshot();
});
```

### Global Matcher Setup

#### Via setupFilesAfterEnv

```javascript
// setup-jest.js
import { expect } from '@jest/globals';
import { toBeWithinRange } from './matchers/toBeWithinRange';

expect.extend({
  toBeWithinRange,
});
```

```javascript
// jest.config.js
module.exports = {
  setupFilesAfterEnv: ['<rootDir>/setup-jest.js'],
};
```

### Matcher Context API

```javascript
expect.extend({
  customMatcher(received, expected) {
    // Available context properties:
    
    // this.isNot - boolean indicating .not was used
    // this.promise - string: 'rejects', 'resolves', or ''
    // this.expand - boolean for --expand flag
    // this.equals(a, b, customTesters) - deep equality function
    // this.utils - jest-matcher-utils functions
    // this.customTesters - array of custom equality testers
    
    const pass = this.equals(received, expected, this.customTesters);
    
    return {
      pass,
      message: () => 
        this.utils.matcherHint('customMatcher', 'received', 'expected', {
          isNot: this.isNot,
          promise: this.promise,
        }) + '\n\n' +
        `Expected: ${this.utils.printExpected(expected)}\n` +
        `Received: ${this.utils.printReceived(received)}`,
    };
  },
});
```

---

## Custom Reporters

### Basic Reporter Structure

```javascript
// custom-reporter.js
class CustomReporter {
  constructor(globalConfig, reporterOptions, reporterContext) {
    this._globalConfig = globalConfig;
    this._options = reporterOptions;
    this._context = reporterContext;
  }

  onRunComplete(testContexts, results) {
    console.log('Custom reporter output:');
    console.log('Global config:', this._globalConfig);
    console.log('Reporter options:', this._options);
    console.log('Test results:', results);
  }

  // Optional: Force Jest to exit with non-zero code
  getLastError() {
    if (this._shouldFail) {
      return new Error('Custom error reported!');
    }
  }
}

module.exports = CustomReporter;
```

### Reporter Configuration

```javascript
// jest.config.js
module.exports = {
  reporters: [
    'default', // Keep default reporter
    ['<rootDir>/custom-reporter.js', { 
      outputFile: 'test-results.json',
      includeConsoleOutput: true 
    }],
    ['jest-junit', { 
      outputDirectory: 'reports', 
      outputName: 'junit.xml' 
    }],
  ],
};
```

### Comprehensive Reporter Example

```javascript
// comprehensive-reporter.js
const fs = require('fs');
const path = require('path');

class ComprehensiveReporter {
  constructor(globalConfig, options = {}) {
    this._globalConfig = globalConfig;
    this._options = {
      outputFile: 'test-results.json',
      includeConsoleOutput: false,
      includeCoverage: true,
      ...options,
    };
    this._results = [];
  }

  onRunStart(aggregatedResult, options) {
    console.log('Starting test run...');
    this._startTime = Date.now();
  }

  onTestFileStart(test) {
    console.log(`Running ${test.path}`);
  }

  onTestFileResult(test, testResult, aggregatedResult) {
    this._results.push({
      testFilePath: testResult.testFilePath,
      numFailingTests: testResult.numFailingTests,
      numPassingTests: testResult.numPassingTests,
      numPendingTests: testResult.numPendingTests,
      testResults: testResult.testResults.map(result => ({
        ancestorTitles: result.ancestorTitles,
        title: result.title,
        status: result.status,
        duration: result.duration,
        failureMessages: result.failureMessages,
      })),
      coverage: testResult.coverage,
    });
  }

  onRunComplete(contexts, results) {
    const endTime = Date.now();
    const duration = endTime - this._startTime;

    const report = {
      success: results.success,
      startTime: this._startTime,
      endTime,
      duration,
      numTotalTestSuites: results.numTotalTestSuites,
      numPassedTestSuites: results.numPassedTestSuites,
      numFailedTestSuites: results.numFailedTestSuites,
      numTotalTests: results.numTotalTests,
      numPassedTests: results.numPassedTests,
      numFailedTests: results.numFailedTests,
      numPendingTests: results.numPendingTests,
      testResults: this._results,
    };

    if (this._options.includeCoverage && results.coverageMap) {
      report.coverage = results.coverageMap.toJSON();
    }

    // Write to file
    if (this._options.outputFile) {
      const outputPath = path.resolve(this._options.outputFile);
      fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
      console.log(`Report written to ${outputPath}`);
    }

    // Console summary
    console.log('\n' + '='.repeat(50));
    console.log('TEST SUMMARY');
    console.log('='.repeat(50));
    console.log(`Tests:       ${results.numPassedTests} passed, ${results.numFailedTests} failed, ${results.numTotalTests} total`);
    console.log(`Time:        ${duration}ms`);
    console.log(`Ran all test suites.`);
    
    if (results.numFailedTests > 0) {
      console.log('\nFailed tests:');
      this._results.forEach(fileResult => {
        fileResult.testResults
          .filter(test => test.status === 'failed')
          .forEach(test => {
            console.log(`  ● ${test.ancestorTitles.join(' › ')} › ${test.title}`);
            test.failureMessages.forEach(message => {
              console.log(`    ${message.split('\n')[0]}`);
            });
          });
      });
    }
  }

  getLastError() {
    return this._lastError;
  }
}

module.exports = ComprehensiveReporter;
```

### Specialized Reporters

#### Coverage Reporter

```javascript
// coverage-reporter.js
class CoverageReporter {
  onRunComplete(contexts, results) {
    if (!results.coverageMap) {
      console.log('No coverage data available');
      return;
    }

    const coverage = results.coverageMap.toJSON();
    const summary = results.coverageMap.getCoverageSummary();

    console.log('\nCoverage Summary:');
    console.log(`Lines:      ${summary.lines.pct}% (${summary.lines.covered}/${summary.lines.total})`);
    console.log(`Functions:  ${summary.functions.pct}% (${summary.functions.covered}/${summary.functions.total})`);
    console.log(`Branches:   ${summary.branches.pct}% (${summary.branches.covered}/${summary.branches.total})`);
    console.log(`Statements: ${summary.statements.pct}% (${summary.statements.covered}/${summary.statements.total})`);

    // Find files with low coverage
    const lowCoverageFiles = Object.entries(coverage)
      .filter(([, fileCoverage]) => fileCoverage.lines.pct < 80)
      .map(([filepath, fileCoverage]) => ({
        filepath: filepath.replace(process.cwd(), '.'),
        coverage: fileCoverage.lines.pct,
      }));

    if (lowCoverageFiles.length > 0) {
      console.log('\nFiles with low coverage:');
      lowCoverageFiles.forEach(file => {
        console.log(`  ${file.filepath}: ${file.coverage}%`);
      });
    }
  }
}

module.exports = CoverageReporter;
```

#### Performance Reporter

```javascript
// performance-reporter.js
class PerformanceReporter {
  constructor(globalConfig, options = {}) {
    this._options = {
      slowTestThreshold: 1000, // ms
      ...options,
    };
    this._slowTests = [];
  }

  onTestFileResult(test, testResult) {
    testResult.testResults.forEach(result => {
      if (result.duration > this._options.slowTestThreshold) {
        this._slowTests.push({
          testPath: testResult.testFilePath,
          testName: `${result.ancestorTitles.join(' › ')} › ${result.title}`,
          duration: result.duration,
        });
      }
    });
  }

  onRunComplete(contexts, results) {
    if (this._slowTests.length === 0) {
      console.log('\n✅ No slow tests detected');
      return;
    }

    console.log(`\n⚠️  Slow tests (>${this._options.slowTestThreshold}ms):`);
    this._slowTests
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 10) // Top 10 slowest
      .forEach(test => {
        console.log(`  ${test.duration}ms - ${test.testName}`);
        console.log(`    ${test.testPath.replace(process.cwd(), '.')}`);
      });
  }
}

module.exports = PerformanceReporter;
```

#### GitHub Actions Reporter

```javascript
// github-actions-reporter.js
class GitHubActionsReporter {
  onTestFileResult(test, testResult) {
    testResult.testResults.forEach(result => {
      if (result.status === 'failed') {
        const testPath = testResult.testFilePath.replace(process.cwd() + '/', '');
        const testName = `${result.ancestorTitles.join(' › ')} › ${result.title}`;
        
        result.failureMessages.forEach(message => {
          // GitHub Actions annotation format
          console.log(`::error file=${testPath}::${testName}: ${message.split('\n')[0]}`);
        });
      }
    });
  }

  onRunComplete(contexts, results) {
    if (results.success) {
      console.log('::notice::All tests passed! 🎉');
    } else {
      console.log(`::error::${results.numFailedTests} test(s) failed`);
    }

    // Set GitHub Actions outputs
    console.log(`::set-output name=tests-passed::${results.numPassedTests}`);
    console.log(`::set-output name=tests-failed::${results.numFailedTests}`);
    console.log(`::set-output name=tests-total::${results.numTotalTests}`);
  }
}

module.exports = GitHubActionsReporter;
```

### Reporter Lifecycle Methods

```javascript
class FullLifecycleReporter {
  // Called once before all tests
  onRunStart(aggregatedResult, options) {
    console.log('Test run started');
  }

  // Called before each test file
  onTestFileStart(test) {
    console.log(`Starting ${test.path}`);
  }

  // Called after each test file
  onTestFileResult(test, testResult, aggregatedResult) {
    console.log(`Finished ${test.path}`);
  }

  // Called when a test starts (Jest 28+)
  onTestCaseStart(test, testCaseStartInfo) {
    console.log(`Test case started: ${testCaseStartInfo.title}`);
  }

  // Called when a test finishes (Jest 28+)
  onTestCaseResult(test, testCaseResult) {
    console.log(`Test case finished: ${testCaseResult.title} - ${testCaseResult.status}`);
  }

  // Called once after all tests
  onRunComplete(testContexts, results) {
    console.log('Test run completed');
  }

  // Optional: return error to make Jest exit with non-zero code
  getLastError() {
    return this._error;
  }
}
```

---

## Transformers

### Built-in Transformers

Jest includes several built-in transformers:

- `babel-jest` - Transforms JavaScript/TypeScript via Babel
- `@jest/transform` - Core transformation utilities

### Basic Transform Configuration

```javascript
// jest.config.js
module.exports = {
  transform: {
    // JavaScript/TypeScript files
    '\\.[jt]sx?$': 'babel-jest',
    
    // CSS files
    '\\.css$': 'jest-transform-css',
    
    // Image files
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/file-transformer.js',
  },
  
  // Files to ignore during transformation
  transformIgnorePatterns: [
    'node_modules/(?!(some-es6-package|another-package)/)',
  ],
};
```

### File Transformer Example

```javascript
// file-transformer.js
const path = require('path');

module.exports = {
  process(sourceText, sourcePath) {
    return {
      code: `module.exports = ${JSON.stringify(path.basename(sourcePath))};`,
    };
  },
};
```

This transforms:
```javascript
import image from './image.png';
```

Into:
```javascript
const image = 'image.png';
```

### CSS Transformer

```javascript
// css-transformer.js
module.exports = {
  process() {
    return {
      code: 'module.exports = {};',
    };
  },
};
```

### Advanced File Transformer

```javascript
// advanced-file-transformer.js
const path = require('path');

module.exports = {
  // Indicate if this transformer can instrument code for coverage
  canInstrument: false,

  // Generate cache key for this transformer
  getCacheKey(sourceText, sourcePath, options) {
    return JSON.stringify({
      sourceText,
      sourcePath,
      configString: options.configString,
      transformerConfig: options.transformerConfig,
    });
  },

  // Transform the file
  process(sourceText, sourcePath, options) {
    const filename = path.basename(sourcePath);
    
    // Return both code and source map
    return {
      code: `
        module.exports = {
          __filename: ${JSON.stringify(filename)},
          __filepath: ${JSON.stringify(sourcePath)},
          __contents: ${JSON.stringify(sourceText)},
        };
      `,
      map: null, // Optional source map
    };
  },
};
```

### Async Transformer

```javascript
// async-transformer.js
const fs = require('fs').promises;
const path = require('path');

module.exports = {
  // Async transformation
  async processAsync(sourceText, sourcePath, options) {
    // Read additional files if needed
    const packagePath = path.join(path.dirname(sourcePath), 'package.json');
    
    try {
      const packageJson = await fs.readFile(packagePath, 'utf8');
      const pkg = JSON.parse(packageJson);
      
      return {
        code: `
          module.exports = {
            filename: ${JSON.stringify(path.basename(sourcePath))},
            packageName: ${JSON.stringify(pkg.name)},
            packageVersion: ${JSON.stringify(pkg.version)},
          };
        `,
      };
    } catch (error) {
      return {
        code: `module.exports = ${JSON.stringify(path.basename(sourcePath))};`,
      };
    }
  },
};
```

### TypeScript Configuration

#### Using babel-jest with TypeScript

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  transform: {
    '^.+\\.tsx?$': ['babel-jest', {
      presets: [
        ['@babel/preset-env', { targets: { node: 'current' } }],
        '@babel/preset-typescript',
      ],
    }],
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
};
```

#### Using ts-jest

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.test.json',
    },
  },
};
```

### React Configuration

#### Basic React Setup

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/setup-tests.js'],
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
  },
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/file-mock.js',
  },
};
```

#### Setup file for React

```javascript
// setup-tests.js
import '@testing-library/jest-dom';

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};
```

### Webpack Integration

#### Module Name Mapping

```javascript
// jest.config.js
module.exports = {
  moduleNameMapper: {
    // Handle CSS modules
    '\\.module\\.(css|sass|scss)$': 'identity-obj-proxy',
    
    // Handle CSS imports
    '\\.(css|sass|scss)$': '<rootDir>/__mocks__/style-mock.js',
    
    // Handle image imports
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/file-mock.js',
    
    // Handle absolute imports
    '^@/(.*)$': '<rootDir>/src/$1',
    '^components/(.*)$': '<rootDir>/src/components/$1',
  },
};
```

#### Style and File Mocks

```javascript
// __mocks__/style-mock.js
module.exports = {};
```

```javascript
// __mocks__/file-mock.js
module.exports = 'test-file-stub';
```

### Complex Transform Pipeline

```javascript
// complex-transformer.js
const babel = require('@babel/core');
const postCSS = require('postcss');

module.exports = {
  canInstrument: true,

  getCacheKey(sourceText, sourcePath, options) {
    return JSON.stringify({
      sourceText,
      sourcePath,
      babelConfig: options.transformerConfig.babel,
      postcssConfig: options.transformerConfig.postcss,
    });
  },

  process(sourceText, sourcePath, options) {
    const { transformerConfig } = options;

    // Handle CSS files
    if (sourcePath.endsWith('.css')) {
      return this.processCSS(sourceText, sourcePath, transformerConfig.postcss);
    }

    // Handle JavaScript/TypeScript files
    if (/\.[jt]sx?$/.test(sourcePath)) {
      return this.processJS(sourceText, sourcePath, transformerConfig.babel);
    }

    // Handle other files as modules
    return this.processAsset(sourceText, sourcePath);
  },

  processCSS(sourceText, sourcePath, postcssConfig) {
    const result = postCSS(postcssConfig.plugins || [])
      .process(sourceText, { from: sourcePath });

    return {
      code: `module.exports = ${JSON.stringify(result.css)};`,
    };
  },

  processJS(sourceText, sourcePath, babelConfig) {
    const result = babel.transformSync(sourceText, {
      filename: sourcePath,
      ...babelConfig,
    });

    return {
      code: result.code,
      map: result.map,
    };
  },

  processAsset(sourceText, sourcePath) {
    const filename = path.basename(sourcePath);
    return {
      code: `module.exports = ${JSON.stringify(filename)};`,
    };
  },
};
```

### Transform Utilities

#### Creating Transformer Factory

```javascript
// transformer-factory.js
function createTransformer(options = {}) {
  return {
    canInstrument: options.canInstrument || false,
    
    getCacheKey(sourceText, sourcePath, jestOptions) {
      return JSON.stringify({
        sourceText,
        sourcePath,
        options,
        configString: jestOptions.configString,
      });
    },

    process(sourceText, sourcePath, jestOptions) {
      return options.transform(sourceText, sourcePath, {
        ...jestOptions,
        transformerOptions: options,
      });
    },
  };
}

module.exports = { createTransformer };
```

Usage:
```javascript
// jest.config.js
const { createTransformer } = require('./transformer-factory');

module.exports = {
  transform: {
    '\\.special$': createTransformer({
      canInstrument: true,
      transform: (sourceText, sourcePath) => ({
        code: `module.exports = "transformed: ${path.basename(sourcePath)}";`,
      }),
    }),
  },
};
```

---

## Best Practices

### Test Organization

#### File Structure

```
project/
├── src/
│   ├── components/
│   │   ├── Button/
│   │   │   ├── Button.js
│   │   │   ├── Button.test.js
│   │   │   └── Button.spec.js
│   │   └── utils/
│   │       ├── helpers.js
│   │       └── helpers.test.js
├── __tests__/
│   ├── integration/
│   ├── e2e/
│   └── setup/
└── jest.config.js
```

#### Naming Conventions

```javascript
// ✅ Good test names
describe('UserService', () => {
  describe('when creating a new user', () => {
    test('should create user with valid data', () => {});
    test('should throw ValidationError with invalid email', () => {});
    test('should hash password before saving', () => {});
  });

  describe('when updating existing user', () => {
    test('should update only provided fields', () => {});
    test('should not allow email updates', () => {});
  });
});

// ❌ Poor test names
describe('UserService', () => {
  test('test 1', () => {});
  test('should work', () => {});
  test('user stuff', () => {});
});
```

### Test Quality

#### AAA Pattern (Arrange, Act, Assert)

```javascript
test('should calculate total price with tax', () => {
  // Arrange
  const items = [
    { price: 10, quantity: 2 },
    { price: 5, quantity: 1 },
  ];
  const taxRate = 0.1;

  // Act
  const total = calculateTotal(items, taxRate);

  // Assert
  expect(total).toBe(27.5);
});
```

#### Single Responsibility

```javascript
// ✅ Good - tests one thing
test('should validate email format', () => {
  expect(isValidEmail('test@example.com')).toBe(true);
  expect(isValidEmail('invalid-email')).toBe(false);
});

test('should validate password strength', () => {
  expect(isStrongPassword('weak')).toBe(false);
  expect(isStrongPassword('StrongP@ssw0rd')).toBe(true);
});

// ❌ Poor - tests multiple things
test('should validate user input', () => {
  expect(isValidEmail('test@example.com')).toBe(true);
  expect(isStrongPassword('StrongP@ssw0rd')).toBe(true);
  expect(isValidPhoneNumber('+1234567890')).toBe(true);
});
```

#### Meaningful Assertions

```javascript
// ✅ Good - specific assertions
test('should return user data', async () => {
  const user = await fetchUser(123);
  
  expect(user).toMatchObject({
    id: 123,
    name: expect.any(String),
    email: expect.stringMatching(/^.+@.+\..+$/),
    createdAt: expect.any(Date),
  });
});

// ❌ Poor - vague assertions
test('should return user data', async () => {
  const user = await fetchUser(123);
  expect(user).toBeDefined();
  expect(user).toBeTruthy();
});
```

### Mocking Best Practices

#### Mock Only What You Need

```javascript
// ✅ Good - mock external dependencies
test('should send notification email', async () => {
  const mockEmailService = {
    send: jest.fn().mockResolvedValue({ success: true }),
  };

  const notificationService = new NotificationService(mockEmailService);
  await notificationService.sendWelcomeEmail('user@example.com');

  expect(mockEmailService.send).toHaveBeenCalledWith({
    to: 'user@example.com',
    subject: 'Welcome!',
    template: 'welcome',
  });
});

// ❌ Poor - mocking internal methods
test('should process user data', () => {
  const service = new UserService();
  service.validateUser = jest.fn().mockReturnValue(true);
  service.saveUser = jest.fn().mockResolvedValue({ id: 1 });

  // This tests the mock, not the actual implementation
});
```

#### Restore Mocks Between Tests

```javascript
// ✅ Good - clean slate for each test
beforeEach(() => {
  jest.clearAllMocks();
});

afterEach(() => {
  jest.restoreAllMocks();
});
```

#### Use Specific Mock Assertions

```javascript
// ✅ Good - specific mock assertions
expect(mockFunction).toHaveBeenCalledTimes(1);
expect(mockFunction).toHaveBeenCalledWith('expected', 'arguments');
expect(mockFunction).toHaveBeenLastCalledWith('last', 'call');

// ❌ Poor - vague mock assertions
expect(mockFunction).toHaveBeenCalled();
```

### Async Testing Best Practices

#### Always Handle Async Properly

```javascript
// ✅ Good - proper async handling
test('should fetch user data', async () => {
  const user = await fetchUser(123);
  expect(user.id).toBe(123);
});

test('should handle fetch error', async () => {
  await expect(fetchUser(-1)).rejects.toThrow('User not found');
});

// ❌ Poor - missing await
test('should fetch user data', () => {
  const user = fetchUser(123); // Returns a promise!
  expect(user.id).toBe(123); // This will fail
});
```

#### Test Both Success and Error Cases

```javascript
describe('UserAPI', () => {
  test('should fetch user successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, name: 'John' }),
    });

    const user = await fetchUser(1);
    expect(user).toEqual({ id: 1, name: 'John' });
  });

  test('should handle network error', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    await expect(fetchUser(1)).rejects.toThrow('Network error');
  });

  test('should handle HTTP error response', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
    });

    await expect(fetchUser(999)).rejects.toThrow('User not found');
  });
});
```

### Snapshot Testing Best Practices

#### Use Snapshots for UI Components

```javascript
// ✅ Good - UI component snapshots
test('Button renders correctly', () => {
  const tree = renderer.create(
    <Button variant="primary" onClick={jest.fn()}>
      Click me
    </Button>
  ).toJSON();
  
  expect(tree).toMatchSnapshot();
});
```

#### Avoid Snapshots for APIs/Objects

```javascript
// ❌ Poor - API response snapshots
test('should return user data', async () => {
  const response = await api.getUser(123);
  expect(response).toMatchSnapshot(); // Too brittle
});

// ✅ Good - specific assertions
test('should return user data', async () => {
  const response = await api.getUser(123);
  expect(response).toMatchObject({
    id: 123,
    name: expect.any(String),
    email: expect.stringMatching(/^.+@.+$/),
  });
});
```

#### Use Property Matchers for Dynamic Data

```javascript
// ✅ Good - handle dynamic values
test('should create user record', () => {
  const user = createUser({ name: 'John', email: 'john@example.com' });
  
  expect(user).toMatchSnapshot({
    id: expect.any(String),
    createdAt: expect.any(Date),
    updatedAt: expect.any(Date),
  });
});
```

### Performance Best Practices

#### Use `test.concurrent` for Independent Tests

```javascript
// ✅ Good - run independent tests concurrently
test.concurrent('should validate email format', async () => {
  const result = await validateEmail('test@example.com');
  expect(result.valid).toBe(true);
});

test.concurrent('should validate phone format', async () => {
  const result = await validatePhone('+1234567890');
  expect(result.valid).toBe(true);
});
```

#### Optimize Setup and Teardown

```javascript
// ✅ Good - reuse expensive setup
describe('DatabaseService', () => {
  let db;

  beforeAll(async () => {
    db = await createTestDatabase();
  });

  afterAll(async () => {
    await db.close();
  });

  beforeEach(async () => {
    await db.clear(); // Fast operation
  });

  // Tests here...
});

// ❌ Poor - expensive setup in each test
test('should create user', async () => {
  const db = await createTestDatabase(); // Slow!
  // Test logic...
  await db.close();
});
```

#### Use `--runInBand` for Debugging

```bash
# When debugging flaky tests
jest --runInBand --verbose
```

### Configuration Best Practices

#### Environment-Specific Configurations

```javascript
// jest.config.js
const isCI = process.env.CI === 'true';

module.exports = {
  testEnvironment: 'node',
  verbose: isCI,
  collectCoverage: isCI,
  coverageReporters: isCI ? ['lcov', 'text'] : ['text'],
  maxWorkers: isCI ? '50%' : '100%',
  
  // Timeouts
  testTimeout: isCI ? 30000 : 5000,
  
  // Watch mode (only in development)
  watchPlugins: isCI ? [] : [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],
};
```

#### Separate Configs for Different Test Types

```javascript
// jest.config.js (base config)
module.exports = {
  projects: [
    '<rootDir>/jest.unit.config.js',
    '<rootDir>/jest.integration.config.js',
    '<rootDir>/jest.e2e.config.js',
  ],
};

// jest.unit.config.js
module.exports = {
  displayName: 'unit',
  testMatch: ['**/__tests__/unit/**/*.test.js'],
  testEnvironment: 'node',
};

// jest.integration.config.js
module.exports = {
  displayName: 'integration',
  testMatch: ['**/__tests__/integration/**/*.test.js'],
  testEnvironment: 'node',
  setupFilesAfterEnv: ['<rootDir>/setup-integration.js'],
};
```

### Error Handling Best Practices

#### Test Error Boundaries

```javascript
// Error boundary component
test('should catch and display error', () => {
  const ThrowError = () => {
    throw new Error('Test error');
  };

  const { getByText } = render(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  );

  expect(getByText(/something went wrong/i)).toBeInTheDocument();
});
```

#### Test Validation Errors

```javascript
test('should validate required fields', async () => {
  const invalidUser = { name: '', email: 'invalid' };
  
  await expect(createUser(invalidUser)).rejects.toThrow(
    expect.objectContaining({
      name: 'ValidationError',
      errors: expect.arrayContaining([
        expect.objectContaining({
          field: 'name',
          message: 'Name is required',
        }),
        expect.objectContaining({
          field: 'email',
          message: 'Invalid email format',
        }),
      ]),
    })
  );
});
```

### Common Anti-Patterns to Avoid

#### Don't Test Implementation Details

```javascript
// ❌ Poor - testing implementation
test('should call validateEmail method', () => {
  const service = new UserService();
  const spy = jest.spyOn(service, 'validateEmail');
  
  service.createUser({ email: 'test@example.com' });
  
  expect(spy).toHaveBeenCalled(); // Testing implementation
});

// ✅ Good - testing behavior
test('should create user with valid email', () => {
  const service = new UserService();
  const user = service.createUser({ email: 'test@example.com' });
  
  expect(user.email).toBe('test@example.com'); // Testing behavior
});
```

#### Don't Over-Mock

```javascript
// ❌ Poor - mocking everything
test('should process payment', async () => {
  const mockValidator = jest.fn().mockReturnValue(true);
  const mockCalculator = jest.fn().mockReturnValue(100);
  const mockLogger = jest.fn();
  const mockPaymentGateway = jest.fn().mockResolvedValue({ success: true });
  
  const service = new PaymentService(
    mockValidator,
    mockCalculator,
    mockLogger,
    mockPaymentGateway
  );
  
  // This tests the mocks, not the real logic
});

// ✅ Good - mock only external dependencies
test('should process payment', async () => {
  const mockPaymentGateway = jest.fn().mockResolvedValue({ success: true });
  const service = new PaymentService({ paymentGateway: mockPaymentGateway });
  
  const result = await service.processPayment({ amount: 100 });
  
  expect(result.success).toBe(true);
  expect(mockPaymentGateway).toHaveBeenCalledWith({ amount: 100 });
});
```

#### Don't Write Tests That Don't Add Value

```javascript
// ❌ Poor - testing trivial code
test('should return true', () => {
  function alwaysTrue() {
    return true;
  }
  
  expect(alwaysTrue()).toBe(true);
});

// ❌ Poor - testing external libraries
test('should format date', () => {
  const formatted = moment('2023-01-01').format('YYYY-MM-DD');
  expect(formatted).toBe('2023-01-01');
});

// ✅ Good - testing business logic
test('should calculate order total with tax and discount', () => {
  const order = {
    items: [{ price: 100, quantity: 2 }],
    discountPercent: 10,
    taxRate: 0.08,
  };
  
  const total = calculateOrderTotal(order);
  
  expect(total).toBe(194.4); // (200 - 20) * 1.08
});
```

---

This comprehensive Jest documentation covers all major aspects of testing with Jest, from basic setup to advanced patterns and best practices. Use it as a reference for implementing robust testing strategies in your JavaScript projects.