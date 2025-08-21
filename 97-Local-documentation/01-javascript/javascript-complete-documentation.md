# JavaScript Complete Documentation

## Table of Contents
1. [Variables and Data Types](#variables-and-data-types)
2. [Operators](#operators)
3. [Functions](#functions)
4. [Objects](#objects)
5. [Arrays](#arrays)
6. [Control Flow](#control-flow)
7. [Classes](#classes)
8. [Modules](#modules)
9. [Asynchronous Programming](#asynchronous-programming)
10. [Promises](#promises)
11. [Error Handling](#error-handling)
12. [DOM Manipulation](#dom-manipulation)
13. [Events](#events)
14. [Regular Expressions](#regular-expressions)
15. [ES6+ Features](#es6-features)
16. [Built-in Objects](#built-in-objects)
17. [Web APIs](#web-apis)
18. [Best Practices](#best-practices)

## Variables and Data Types

### Variable Declarations

```javascript
// var - function scoped, hoisted
var name = 'John';
var age; // undefined

// let - block scoped, not hoisted
let count = 0;
let message = 'Hello';

// const - block scoped, immutable reference
const PI = 3.14159;
const config = { api: 'https://api.example.com' };
```

### Primitive Data Types

```javascript
// Number
let integer = 42;
let float = 3.14;
let negative = -10;
let exponential = 1.5e3; // 1500
let binary = 0b1010; // 10
let octal = 0o12; // 10
let hex = 0xA; // 10

// String
let single = 'single quotes';
let double = "double quotes";
let template = `template literal ${integer}`;
let multiline = `
  Line 1
  Line 2
`;

// Boolean
let isTrue = true;
let isFalse = false;

// Null and Undefined
let empty = null;
let notDefined = undefined;

// Symbol
let sym1 = Symbol('id');
let sym2 = Symbol('id');
console.log(sym1 === sym2); // false

// BigInt
let bigNumber = 9007199254740991n;
let bigInt = BigInt(9007199254740991);
```

### Type Checking and Conversion

```javascript
// Type checking
typeof 42; // "number"
typeof 'hello'; // "string"
typeof true; // "boolean"
typeof undefined; // "undefined"
typeof null; // "object" (legacy bug)
typeof {}; // "object"
typeof []; // "object"
typeof function(){}; // "function"

// Type conversion
String(42); // "42"
Number("42"); // 42
Boolean(0); // false
Boolean(1); // true
parseInt("42px"); // 42
parseFloat("3.14"); // 3.14

// Implicit conversion
"5" + 3; // "53" (string concatenation)
"5" - 3; // 2 (numeric subtraction)
"5" * "2"; // 10
true + 1; // 2
false + 1; // 1
```

## Operators

### Arithmetic Operators

```javascript
let a = 10, b = 3;

// Basic arithmetic
a + b; // 13
a - b; // 7
a * b; // 30
a / b; // 3.333...
a % b; // 1 (remainder)
a ** b; // 1000 (exponentiation)

// Increment/Decrement
let x = 5;
x++; // post-increment, returns 5, x becomes 6
++x; // pre-increment, returns 7, x becomes 7
x--; // post-decrement
--x; // pre-decrement
```

### Assignment Operators

```javascript
let x = 10;
x += 5; // x = x + 5
x -= 3; // x = x - 3
x *= 2; // x = x * 2
x /= 4; // x = x / 4
x %= 3; // x = x % 3
x **= 2; // x = x ** 2

// Logical assignment operators (ES2021)
x ||= 5; // x = x || 5
x &&= 3; // x = x && 3
x ??= 2; // x = x ?? 2 (nullish coalescing)
```

### Comparison Operators

```javascript
// Equality
5 == "5"; // true (loose equality)
5 === "5"; // false (strict equality)
5 != "5"; // false
5 !== "5"; // true

// Relational
5 > 3; // true
5 < 3; // false
5 >= 5; // true
5 <= 4; // false

// Object.is() for special cases
Object.is(NaN, NaN); // true
Object.is(0, -0); // false
```

### Logical Operators

```javascript
// AND, OR, NOT
true && false; // false
true || false; // true
!true; // false

// Short-circuit evaluation
let result = value1 && value2; // returns value2 if value1 is truthy
let result = value1 || value2; // returns value1 if truthy, else value2

// Nullish coalescing
let value = null ?? 'default'; // 'default'
let value = 0 ?? 'default'; // 0
let value = '' ?? 'default'; // ''
```

## Functions

### Function Declarations and Expressions

```javascript
// Function declaration (hoisted)
function greet(name) {
  return `Hello, ${name}!`;
}

// Function expression
const greet = function(name) {
  return `Hello, ${name}!`;
};

// Arrow function
const greet = (name) => `Hello, ${name}!`;
const add = (a, b) => a + b;
const log = message => console.log(message);
const doSomething = () => {
  console.log('Doing something');
  return 42;
};

// IIFE (Immediately Invoked Function Expression)
(function() {
  console.log('IIFE executed');
})();

(() => console.log('Arrow IIFE'))();
```

### Function Parameters

```javascript
// Default parameters
function greet(name = 'Guest', greeting = 'Hello') {
  return `${greeting}, ${name}!`;
}

// Rest parameters
function sum(...numbers) {
  return numbers.reduce((a, b) => a + b, 0);
}
sum(1, 2, 3, 4); // 10

// Destructuring parameters
function createUser({ name, age, email = 'not@provided.com' }) {
  return { name, age, email };
}

// Arguments object (not in arrow functions)
function oldStyle() {
  console.log(arguments); // array-like object
}
```

### Higher-Order Functions

```javascript
// Function returning function
function createMultiplier(factor) {
  return function(number) {
    return number * factor;
  };
}
const double = createMultiplier(2);
double(5); // 10

// Function accepting function
function processArray(array, callback) {
  const result = [];
  for (let item of array) {
    result.push(callback(item));
  }
  return result;
}

// Currying
const curry = (fn) => {
  return function curried(...args) {
    if (args.length >= fn.length) {
      return fn.apply(this, args);
    }
    return function(...args2) {
      return curried.apply(this, args.concat(args2));
    };
  };
};

const add = (a, b, c) => a + b + c;
const curriedAdd = curry(add);
curriedAdd(1)(2)(3); // 6
curriedAdd(1, 2)(3); // 6
```

## Objects

### Object Creation and Properties

```javascript
// Object literal
const person = {
  name: 'John',
  age: 30,
  'special-key': 'value',
  greet() {
    return `Hi, I'm ${this.name}`;
  }
};

// Accessing properties
person.name; // 'John'
person['age']; // 30
person['special-key']; // 'value'

// Dynamic property names
const propName = 'email';
const user = {
  [propName]: 'john@example.com',
  [`${propName}_verified`]: true
};

// Property descriptors
Object.defineProperty(person, 'id', {
  value: 123,
  writable: false,
  enumerable: true,
  configurable: false
});
```

### Object Methods

```javascript
const obj = { a: 1, b: 2, c: 3 };

// Object.keys, values, entries
Object.keys(obj); // ['a', 'b', 'c']
Object.values(obj); // [1, 2, 3]
Object.entries(obj); // [['a', 1], ['b', 2], ['c', 3]]

// Object.assign
const target = { a: 1 };
const source = { b: 2, c: 3 };
Object.assign(target, source); // { a: 1, b: 2, c: 3 }

// Object spread
const merged = { ...target, ...source };

// Object.freeze, seal
Object.freeze(obj); // can't add/remove/modify properties
Object.seal(obj); // can't add/remove properties, can modify

// Object.create
const proto = { greet() { return 'Hello'; } };
const instance = Object.create(proto);
```

### Prototypes and Inheritance

```javascript
// Constructor function
function Person(name, age) {
  this.name = name;
  this.age = age;
}

Person.prototype.greet = function() {
  return `Hello, I'm ${this.name}`;
};

const john = new Person('John', 30);

// Prototype chain
Object.getPrototypeOf(john) === Person.prototype; // true
john instanceof Person; // true

// Object.setPrototypeOf
const animal = { type: 'animal' };
const dog = { breed: 'Labrador' };
Object.setPrototypeOf(dog, animal);
```

## Arrays

### Array Creation and Basic Methods

```javascript
// Array creation
const arr1 = [1, 2, 3];
const arr2 = new Array(5); // [empty × 5]
const arr3 = Array.of(1, 2, 3);
const arr4 = Array.from('hello'); // ['h', 'e', 'l', 'l', 'o']
const arr5 = Array.from({ length: 3 }, (_, i) => i * 2); // [0, 2, 4]

// Basic methods
const fruits = ['apple', 'banana', 'orange'];
fruits.push('grape'); // add to end
fruits.pop(); // remove from end
fruits.unshift('strawberry'); // add to beginning
fruits.shift(); // remove from beginning

// Accessing elements
fruits[0]; // first element
fruits.at(-1); // last element (ES2022)
fruits.slice(1, 3); // ['banana', 'orange']
fruits.splice(1, 1, 'kiwi'); // remove 1 at index 1, add 'kiwi'
```

### Array Iteration Methods

```javascript
const numbers = [1, 2, 3, 4, 5];

// forEach
numbers.forEach((num, index, array) => {
  console.log(`${index}: ${num}`);
});

// map - transform elements
const doubled = numbers.map(n => n * 2); // [2, 4, 6, 8, 10]

// filter - select elements
const evens = numbers.filter(n => n % 2 === 0); // [2, 4]

// reduce - aggregate values
const sum = numbers.reduce((acc, curr) => acc + curr, 0); // 15
const grouped = numbers.reduce((acc, num) => {
  const key = num % 2 === 0 ? 'even' : 'odd';
  (acc[key] = acc[key] || []).push(num);
  return acc;
}, {}); // { odd: [1, 3, 5], even: [2, 4] }

// find and findIndex
const found = numbers.find(n => n > 3); // 4
const index = numbers.findIndex(n => n > 3); // 3

// some and every
numbers.some(n => n > 3); // true
numbers.every(n => n > 0); // true

// flat and flatMap
const nested = [1, [2, 3], [[4]]];
nested.flat(); // [1, 2, 3, [4]]
nested.flat(2); // [1, 2, 3, 4]
numbers.flatMap(n => [n, n * 2]); // [1, 2, 2, 4, 3, 6, 4, 8, 5, 10]
```

### Array Sorting and Searching

```javascript
// Sort
const nums = [3, 1, 4, 1, 5, 9];
nums.sort(); // [1, 1, 3, 4, 5, 9] (modifies original)
nums.sort((a, b) => b - a); // [9, 5, 4, 3, 1, 1] (descending)

// Complex sorting
const users = [
  { name: 'John', age: 30 },
  { name: 'Alice', age: 25 },
  { name: 'Bob', age: 35 }
];
users.sort((a, b) => a.age - b.age);

// toSorted (ES2023 - doesn't modify original)
const sorted = nums.toSorted();

// Searching
const arr = [1, 2, 3, 4, 5];
arr.includes(3); // true
arr.indexOf(3); // 2
arr.lastIndexOf(3); // 2

// Binary search (array must be sorted)
function binarySearch(arr, target) {
  let left = 0, right = arr.length - 1;
  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    if (arr[mid] === target) return mid;
    if (arr[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return -1;
}
```

### Array Destructuring

```javascript
// Basic destructuring
const [first, second] = [1, 2, 3];
const [head, ...tail] = [1, 2, 3, 4]; // head: 1, tail: [2, 3, 4]

// Skipping elements
const [, , third] = [1, 2, 3]; // third: 3

// Default values
const [a = 10, b = 20] = [1]; // a: 1, b: 20

// Swapping variables
let x = 1, y = 2;
[x, y] = [y, x]; // x: 2, y: 1

// Nested destructuring
const [[a1, a2], [b1, b2]] = [[1, 2], [3, 4]];
```

## Control Flow

### Conditional Statements

```javascript
// if...else
if (condition) {
  // code
} else if (anotherCondition) {
  // code
} else {
  // code
}

// Ternary operator
const result = condition ? valueIfTrue : valueIfFalse;

// Multiple ternary
const grade = score >= 90 ? 'A' :
              score >= 80 ? 'B' :
              score >= 70 ? 'C' :
              score >= 60 ? 'D' : 'F';

// Switch statement
switch (expression) {
  case value1:
    // code
    break;
  case value2:
  case value3:
    // code for both value2 and value3
    break;
  default:
    // default code
}

// Switch with block scope
switch (action) {
  case 'increment': {
    let count = 0;
    count++;
    break;
  }
  case 'decrement': {
    let count = 10;
    count--;
    break;
  }
}
```

### Loops

```javascript
// for loop
for (let i = 0; i < 5; i++) {
  console.log(i);
}

// for...of (iterables)
const array = [1, 2, 3];
for (const value of array) {
  console.log(value);
}

// for...in (object properties)
const obj = { a: 1, b: 2, c: 3 };
for (const key in obj) {
  console.log(key, obj[key]);
}

// while loop
let i = 0;
while (i < 5) {
  console.log(i);
  i++;
}

// do...while
let j = 0;
do {
  console.log(j);
  j++;
} while (j < 5);

// Loop control
for (let i = 0; i < 10; i++) {
  if (i === 3) continue; // skip to next iteration
  if (i === 7) break; // exit loop
  console.log(i);
}

// Labeled statements
outer: for (let i = 0; i < 3; i++) {
  for (let j = 0; j < 3; j++) {
    if (i === 1 && j === 1) {
      break outer; // breaks out of outer loop
    }
    console.log(i, j);
  }
}
```

## Classes

### Class Declaration and Constructor

```javascript
class Person {
  // Constructor
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }
  
  // Instance method
  greet() {
    return `Hello, I'm ${this.name}`;
  }
  
  // Getter
  get info() {
    return `${this.name} is ${this.age} years old`;
  }
  
  // Setter
  set info(value) {
    const [name, age] = value.split(',');
    this.name = name;
    this.age = parseInt(age);
  }
  
  // Static method
  static species() {
    return 'Homo sapiens';
  }
  
  // Static property
  static classification = 'Mammal';
}

const john = new Person('John', 30);
john.greet(); // "Hello, I'm John"
Person.species(); // "Homo sapiens"
```

### Class Inheritance

```javascript
class Employee extends Person {
  constructor(name, age, position) {
    super(name, age); // call parent constructor
    this.position = position;
  }
  
  greet() {
    return `${super.greet()}, I work as ${this.position}`;
  }
  
  work() {
    return `${this.name} is working`;
  }
}

const emp = new Employee('Alice', 25, 'Developer');
emp.greet(); // "Hello, I'm Alice, I work as Developer"
emp instanceof Employee; // true
emp instanceof Person; // true
```

### Private Fields and Methods

```javascript
class BankAccount {
  #balance = 0; // private field
  
  constructor(initialBalance) {
    this.#balance = initialBalance;
  }
  
  // Private method
  #validateAmount(amount) {
    if (amount <= 0) {
      throw new Error('Amount must be positive');
    }
  }
  
  deposit(amount) {
    this.#validateAmount(amount);
    this.#balance += amount;
    return this.#balance;
  }
  
  getBalance() {
    return this.#balance;
  }
}

const account = new BankAccount(100);
account.deposit(50); // 150
// account.#balance; // SyntaxError: Private field '#balance' must be declared in an enclosing class
```

## Modules

### ES6 Modules

```javascript
// math.js - Named exports
export const PI = 3.14159;
export function add(a, b) {
  return a + b;
}
export class Calculator {
  // class implementation
}

// Default export
export default function subtract(a, b) {
  return a - b;
}

// main.js - Importing
import subtract from './math.js'; // default import
import { PI, add, Calculator } from './math.js'; // named imports
import * as math from './math.js'; // import all
import subtract, { PI as piValue } from './math.js'; // combined

// Dynamic imports
async function loadModule() {
  const module = await import('./math.js');
  console.log(module.PI);
}

// Re-exporting
export { add, Calculator } from './math.js';
export { default as subtract } from './math.js';
```

### CommonJS Modules (Node.js)

```javascript
// math.js - Exporting
const PI = 3.14159;
function add(a, b) {
  return a + b;
}

module.exports = {
  PI,
  add,
  subtract: (a, b) => a - b
};

// Or single export
module.exports = function mainFunction() {
  // implementation
};

// main.js - Importing
const math = require('./math');
const { PI, add } = require('./math');

// Conditional imports
if (condition) {
  const optionalModule = require('./optional');
}
```

## Asynchronous Programming

### Callbacks

```javascript
// Basic callback
function fetchData(callback) {
  setTimeout(() => {
    callback('Data loaded');
  }, 1000);
}

fetchData((data) => {
  console.log(data);
});

// Error-first callback pattern
function readFile(filename, callback) {
  setTimeout(() => {
    if (filename === 'invalid.txt') {
      callback(new Error('File not found'), null);
    } else {
      callback(null, 'File contents');
    }
  }, 100);
}

readFile('data.txt', (err, data) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log(data);
});

// Callback hell
getData((data) => {
  processData(data, (processed) => {
    saveData(processed, (result) => {
      console.log('Done');
    });
  });
});
```

### Promises

```javascript
// Creating a promise
const promise = new Promise((resolve, reject) => {
  setTimeout(() => {
    const success = true;
    if (success) {
      resolve('Operation successful');
    } else {
      reject(new Error('Operation failed'));
    }
  }, 1000);
});

// Using promises
promise
  .then(result => {
    console.log(result);
    return 'Next value';
  })
  .then(value => console.log(value))
  .catch(error => console.error(error))
  .finally(() => console.log('Cleanup'));

// Promise methods
Promise.all([promise1, promise2, promise3])
  .then(results => console.log(results));

Promise.race([promise1, promise2])
  .then(firstResult => console.log(firstResult));

Promise.allSettled([promise1, promise2])
  .then(results => {
    results.forEach(result => {
      if (result.status === 'fulfilled') {
        console.log(result.value);
      } else {
        console.error(result.reason);
      }
    });
  });

Promise.any([promise1, promise2])
  .then(firstSuccess => console.log(firstSuccess))
  .catch(aggregateError => console.error(aggregateError));

// Promisifying callbacks
function promisify(fn) {
  return function(...args) {
    return new Promise((resolve, reject) => {
      fn(...args, (err, result) => {
        if (err) reject(err);
        else resolve(result);
      });
    });
  };
}
```

### Async/Await

```javascript
// Basic async/await
async function fetchData() {
  try {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

// Sequential vs Parallel
async function sequential() {
  const result1 = await operation1();
  const result2 = await operation2();
  return [result1, result2];
}

async function parallel() {
  const [result1, result2] = await Promise.all([
    operation1(),
    operation2()
  ]);
  return [result1, result2];
}

// Async iteration
async function* asyncGenerator() {
  yield await Promise.resolve(1);
  yield await Promise.resolve(2);
  yield await Promise.resolve(3);
}

async function iterateAsync() {
  for await (const value of asyncGenerator()) {
    console.log(value);
  }
}

// Top-level await (ES2022)
const data = await fetchData();
console.log(data);
```

## Error Handling

### Try-Catch-Finally

```javascript
try {
  // Code that might throw an error
  const result = riskyOperation();
  console.log(result);
} catch (error) {
  // Handle the error
  console.error('Error occurred:', error.message);
  
  // Re-throw if needed
  if (error.code === 'CRITICAL') {
    throw error;
  }
} finally {
  // Always executed
  console.log('Cleanup operations');
}

// Catching specific error types
try {
  operation();
} catch (error) {
  if (error instanceof TypeError) {
    console.error('Type error:', error);
  } else if (error instanceof ReferenceError) {
    console.error('Reference error:', error);
  } else {
    console.error('Unknown error:', error);
  }
}
```

### Custom Errors

```javascript
// Custom error class
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
    Error.captureStackTrace(this, ValidationError);
  }
}

class NetworkError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.name = 'NetworkError';
    this.statusCode = statusCode;
  }
}

// Using custom errors
function validateEmail(email) {
  if (!email.includes('@')) {
    throw new ValidationError('Invalid email format', 'email');
  }
}

try {
  validateEmail('invalid-email');
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`Validation failed for ${error.field}: ${error.message}`);
  }
}
```

### Error Handling in Async Code

```javascript
// Promise error handling
promise
  .then(result => processResult(result))
  .catch(error => {
    console.error('Promise rejected:', error);
    return defaultValue; // Recovery
  });

// Async/await error handling
async function safeOperation() {
  try {
    const result = await riskyAsyncOperation();
    return result;
  } catch (error) {
    console.error('Async operation failed:', error);
    return null;
  }
}

// Global error handlers
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  event.preventDefault();
});

// Node.js error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection at:', promise, 'reason:', reason);
});
```

## DOM Manipulation

### Selecting Elements

```javascript
// Single element selectors
const element = document.getElementById('myId');
const element = document.querySelector('.myClass');
const element = document.querySelector('[data-id="123"]');
const element = document.querySelector('div > p:first-child');

// Multiple element selectors
const elements = document.getElementsByClassName('myClass');
const elements = document.getElementsByTagName('div');
const elements = document.querySelectorAll('.myClass');
const elements = document.querySelectorAll('[data-active="true"]');

// Convert NodeList to Array
const elementsArray = Array.from(document.querySelectorAll('.item'));
const elementsArray = [...document.querySelectorAll('.item')];

// Traversing the DOM
const parent = element.parentNode;
const parent = element.parentElement;
const children = element.children; // HTMLCollection
const children = element.childNodes; // NodeList (includes text nodes)
const firstChild = element.firstElementChild;
const lastChild = element.lastElementChild;
const nextSibling = element.nextElementSibling;
const prevSibling = element.previousElementSibling;

// Finding elements
const closest = element.closest('.container');
const contains = element.contains(childElement);
const matches = element.matches('.active');
```

### Creating and Modifying Elements

```javascript
// Creating elements
const div = document.createElement('div');
const text = document.createTextNode('Hello World');
const fragment = document.createDocumentFragment();

// Setting content
element.textContent = 'Plain text';
element.innerHTML = '<strong>HTML content</strong>';
element.innerText = 'Visible text'; // respects styling

// Attributes
element.setAttribute('id', 'myId');
element.getAttribute('id');
element.removeAttribute('id');
element.hasAttribute('id');

// Data attributes
element.dataset.userId = '123';
const userId = element.dataset.userId;

// Classes
element.classList.add('active', 'highlight');
element.classList.remove('active');
element.classList.toggle('visible');
element.classList.contains('active');
element.classList.replace('old', 'new');
element.className = 'class1 class2';

// Styles
element.style.color = 'red';
element.style.backgroundColor = '#fff';
element.style.cssText = 'color: red; background: white;';
const computedStyle = window.getComputedStyle(element);
const color = computedStyle.color;
```

### Inserting and Removing Elements

```javascript
// Inserting elements
parent.appendChild(child);
parent.insertBefore(newChild, referenceChild);
element.append(child1, child2, 'text');
element.prepend(child);

// Modern insertion methods
element.insertAdjacentHTML('beforebegin', '<div>Before</div>');
element.insertAdjacentHTML('afterbegin', '<div>First child</div>');
element.insertAdjacentHTML('beforeend', '<div>Last child</div>');
element.insertAdjacentHTML('afterend', '<div>After</div>');

element.insertAdjacentElement('beforebegin', newElement);
element.insertAdjacentText('beforeend', 'text');

// Replacing elements
parent.replaceChild(newChild, oldChild);
element.replaceWith(newElement);

// Removing elements
parent.removeChild(child);
element.remove();

// Cloning elements
const clone = element.cloneNode(true); // deep clone
const shallowClone = element.cloneNode(false);
```

## Events

### Event Listeners

```javascript
// Adding event listeners
element.addEventListener('click', handleClick);
element.addEventListener('click', handleClick, { once: true });
element.addEventListener('click', handleClick, { passive: true });
element.addEventListener('click', handleClick, { capture: true });

// Removing event listeners
element.removeEventListener('click', handleClick);

// Event handler function
function handleClick(event) {
  console.log('Clicked:', event.target);
  console.log('Current target:', event.currentTarget);
  console.log('Event type:', event.type);
  console.log('Timestamp:', event.timeStamp);
}

// Inline event handlers (not recommended)
element.onclick = function(event) {
  console.log('Clicked');
};

// Multiple listeners
element.addEventListener('click', handler1);
element.addEventListener('click', handler2);
```

### Event Object

```javascript
element.addEventListener('click', (event) => {
  // Event properties
  event.type; // 'click'
  event.target; // element that triggered the event
  event.currentTarget; // element that listener is attached to
  event.timeStamp; // when event occurred
  event.bubbles; // whether event bubbles
  event.cancelable; // whether event can be canceled
  
  // Event methods
  event.preventDefault(); // prevent default action
  event.stopPropagation(); // stop event bubbling
  event.stopImmediatePropagation(); // stop other listeners
  
  // Mouse event properties
  event.clientX; // X coordinate relative to viewport
  event.clientY; // Y coordinate relative to viewport
  event.pageX; // X coordinate relative to page
  event.pageY; // Y coordinate relative to page
  event.screenX; // X coordinate relative to screen
  event.screenY; // Y coordinate relative to screen
  event.button; // which mouse button was pressed
  event.buttons; // which buttons are currently pressed
  event.altKey; // whether Alt key was pressed
  event.ctrlKey; // whether Ctrl key was pressed
  event.shiftKey; // whether Shift key was pressed
  event.metaKey; // whether Meta key was pressed
});
```

### Event Delegation

```javascript
// Instead of adding listeners to each item
document.querySelectorAll('.item').forEach(item => {
  item.addEventListener('click', handleClick);
});

// Use event delegation
document.querySelector('.container').addEventListener('click', (event) => {
  if (event.target.matches('.item')) {
    handleClick(event);
  }
});

// Complex delegation
document.addEventListener('click', (event) => {
  const button = event.target.closest('.btn');
  if (button) {
    const action = button.dataset.action;
    switch (action) {
      case 'delete':
        handleDelete(button);
        break;
      case 'edit':
        handleEdit(button);
        break;
      case 'save':
        handleSave(button);
        break;
    }
  }
});
```

### Custom Events

```javascript
// Creating custom events
const event = new Event('build');
const customEvent = new CustomEvent('userLogin', {
  detail: {
    username: 'john',
    timestamp: Date.now()
  },
  bubbles: true,
  cancelable: true
});

// Dispatching events
element.dispatchEvent(event);
element.dispatchEvent(customEvent);

// Listening to custom events
element.addEventListener('userLogin', (event) => {
  console.log('User logged in:', event.detail.username);
});

// Legacy way (for older browsers)
const event = document.createEvent('CustomEvent');
event.initCustomEvent('myEvent', true, true, { data: 'value' });
```

### Common Events

```javascript
// Mouse events
element.addEventListener('click', handler);
element.addEventListener('dblclick', handler);
element.addEventListener('mousedown', handler);
element.addEventListener('mouseup', handler);
element.addEventListener('mousemove', handler);
element.addEventListener('mouseenter', handler); // doesn't bubble
element.addEventListener('mouseleave', handler); // doesn't bubble
element.addEventListener('mouseover', handler); // bubbles
element.addEventListener('mouseout', handler); // bubbles
element.addEventListener('contextmenu', handler); // right-click

// Keyboard events
document.addEventListener('keydown', (event) => {
  console.log('Key:', event.key);
  console.log('Code:', event.code);
  console.log('Which:', event.which); // deprecated
});
document.addEventListener('keyup', handler);
document.addEventListener('keypress', handler); // deprecated

// Form events
form.addEventListener('submit', (event) => {
  event.preventDefault();
  // Handle form submission
});
input.addEventListener('change', handler);
input.addEventListener('input', handler);
input.addEventListener('focus', handler);
input.addEventListener('blur', handler);
select.addEventListener('change', handler);

// Window events
window.addEventListener('load', handler);
window.addEventListener('DOMContentLoaded', handler);
window.addEventListener('resize', handler);
window.addEventListener('scroll', handler);
window.addEventListener('beforeunload', (event) => {
  event.preventDefault();
  event.returnValue = ''; // Chrome requires this
});

// Touch events
element.addEventListener('touchstart', handler);
element.addEventListener('touchmove', handler);
element.addEventListener('touchend', handler);
element.addEventListener('touchcancel', handler);

// Drag events
element.addEventListener('dragstart', handler);
element.addEventListener('drag', handler);
element.addEventListener('dragend', handler);
element.addEventListener('dragenter', handler);
element.addEventListener('dragover', handler);
element.addEventListener('dragleave', handler);
element.addEventListener('drop', handler);
```

## Regular Expressions

### Creating Regular Expressions

```javascript
// Literal notation
const regex1 = /pattern/flags;
const regex2 = /hello/gi; // global, case-insensitive

// Constructor notation
const regex3 = new RegExp('pattern', 'flags');
const regex4 = new RegExp('hello', 'gi');

// Dynamic patterns
const searchTerm = 'world';
const regex5 = new RegExp(searchTerm, 'i');
```

### Pattern Syntax

```javascript
// Character classes
/\d/; // digit [0-9]
/\D/; // non-digit
/\w/; // word character [a-zA-Z0-9_]
/\W/; // non-word character
/\s/; // whitespace
/\S/; // non-whitespace
/./; // any character except newline
/[abc]/; // any of a, b, or c
/[^abc]/; // not a, b, or c
/[a-z]/; // any lowercase letter
/[A-Z]/; // any uppercase letter
/[0-9]/; // any digit

// Quantifiers
/a*/; // 0 or more
/a+/; // 1 or more
/a?/; // 0 or 1
/a{3}/; // exactly 3
/a{3,}/; // 3 or more
/a{3,5}/; // between 3 and 5

// Anchors
/^start/; // beginning of string
/end$/; // end of string
/\bhello\b/; // word boundary

// Groups and alternation
/(abc)/; // capturing group
/(?:abc)/; // non-capturing group
/(?<name>abc)/; // named group
/a|b/; // a or b
/(cats?|dogs?)/; // cat, cats, dog, or dogs

// Lookahead and lookbehind
/a(?=b)/; // positive lookahead
/a(?!b)/; // negative lookahead
/(?<=a)b/; // positive lookbehind
/(?<!a)b/; // negative lookbehind
```

### Using Regular Expressions

```javascript
const text = 'The quick brown fox jumps over the lazy dog';
const regex = /quick.*fox/;

// test() - returns boolean
regex.test(text); // true

// exec() - returns match array or null
const match = regex.exec(text);
// match[0]: matched string
// match.index: position of match
// match.input: original string

// String methods with regex
text.match(/o/g); // ['o', 'o', 'o']
text.search(/fox/); // 16 (index)
text.replace(/the/gi, 'a'); // replace all 'the' with 'a'
text.split(/\s+/); // split by whitespace

// Advanced replace with function
text.replace(/(\w+)/g, (match, word) => {
  return word.toUpperCase();
});

// Named groups
const dateRegex = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/;
const dateMatch = '2024-03-15'.match(dateRegex);
console.log(dateMatch.groups.year); // '2024'
console.log(dateMatch.groups.month); // '03'
console.log(dateMatch.groups.day); // '15'
```

### Common Patterns

```javascript
// Email validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// URL validation
const urlRegex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;

// Phone number (US format)
const phoneRegex = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;

// Password (min 8 chars, at least one letter and one number)
const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;

// Extract all emails from text
const extractEmails = (text) => {
  const regex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
  return text.match(regex) || [];
};

// Remove HTML tags
const stripHtml = (html) => {
  return html.replace(/<[^>]*>/g, '');
};

// Format phone number
const formatPhone = (phone) => {
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return '(' + match[1] + ') ' + match[2] + '-' + match[3];
  }
  return null;
};
```

## ES6+ Features

### Template Literals

```javascript
// Basic template literal
const name = 'John';
const greeting = `Hello, ${name}!`;

// Multi-line strings
const multiline = `
  Line 1
  Line 2
  Line 3
`;

// Expression interpolation
const result = `The sum of 2 + 2 is ${2 + 2}`;
const upper = `Uppercase: ${name.toUpperCase()}`;

// Tagged templates
function myTag(strings, ...values) {
  console.log(strings); // array of string literals
  console.log(values); // array of interpolated values
  return strings.reduce((result, str, i) => {
    return result + str + (values[i] || '');
  }, '');
}

const tagged = myTag`Hello ${name}, you are ${age} years old`;

// Raw strings
String.raw`Line 1\nLine 2`; // 'Line 1\\nLine 2'
```

### Destructuring Advanced

```javascript
// Object destructuring with renaming
const { name: userName, age: userAge } = user;

// Nested destructuring
const user = {
  id: 1,
  profile: {
    name: 'John',
    address: {
      city: 'New York'
    }
  }
};

const { profile: { name, address: { city } } } = user;

// Mixed destructuring
const { name, skills: [firstSkill, ...otherSkills] } = {
  name: 'John',
  skills: ['JavaScript', 'React', 'Node']
};

// Function parameter destructuring with defaults
function createUser({
  name = 'Anonymous',
  age = 0,
  role = 'user',
  ...rest
} = {}) {
  return { name, age, role, ...rest };
}

// Dynamic property destructuring
const key = 'name';
const { [key]: value } = { name: 'John' };
```

### Spread and Rest

```javascript
// Array spread
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2];
const copy = [...arr1];

// Object spread
const obj1 = { a: 1, b: 2 };
const obj2 = { c: 3, d: 4 };
const merged = { ...obj1, ...obj2 };
const withOverride = { ...obj1, b: 10 };

// Function arguments spread
Math.max(...[1, 2, 3, 4, 5]);
const dateArgs = [2024, 2, 15];
new Date(...dateArgs);

// Rest parameters in functions
function sum(...numbers) {
  return numbers.reduce((a, b) => a + b, 0);
}

// Rest in destructuring
const [first, ...rest] = [1, 2, 3, 4];
const { a, ...others } = { a: 1, b: 2, c: 3 };

// Conditional spread
const conditionalSpread = {
  ...(condition && { key: 'value' }),
  ...(anotherCondition ? { another: 'value' } : {})
};
```

### Symbols

```javascript
// Creating symbols
const sym1 = Symbol();
const sym2 = Symbol('description');
const sym3 = Symbol.for('global.symbol'); // global registry

// Symbols are unique
Symbol('id') === Symbol('id'); // false
Symbol.for('id') === Symbol.for('id'); // true

// Using symbols as object keys
const id = Symbol('id');
const user = {
  name: 'John',
  [id]: 123
};

// Symbols are not enumerable
Object.keys(user); // ['name']
Object.getOwnPropertySymbols(user); // [Symbol(id)]

// Well-known symbols
const iterableObject = {
  data: [1, 2, 3],
  [Symbol.iterator]() {
    let index = 0;
    return {
      next: () => {
        if (index < this.data.length) {
          return { value: this.data[index++], done: false };
        }
        return { done: true };
      }
    };
  }
};

// Symbol.toStringTag
const myObject = {
  [Symbol.toStringTag]: 'MyCustomObject'
};
Object.prototype.toString.call(myObject); // '[object MyCustomObject]'
```

### Iterators and Generators

```javascript
// Custom iterator
const range = {
  from: 1,
  to: 5,
  [Symbol.iterator]() {
    let current = this.from;
    const last = this.to;
    return {
      next() {
        if (current <= last) {
          return { value: current++, done: false };
        }
        return { done: true };
      }
    };
  }
};

for (const num of range) {
  console.log(num); // 1, 2, 3, 4, 5
}

// Generator functions
function* generator() {
  yield 1;
  yield 2;
  yield 3;
}

const gen = generator();
gen.next(); // { value: 1, done: false }
gen.next(); // { value: 2, done: false }
gen.next(); // { value: 3, done: false }
gen.next(); // { value: undefined, done: true }

// Generator with parameters
function* fibonacci(n) {
  let a = 0, b = 1;
  for (let i = 0; i < n; i++) {
    yield a;
    [a, b] = [b, a + b];
  }
}

// Delegating generators
function* delegating() {
  yield 1;
  yield* [2, 3, 4];
  yield* generator();
}

// Async generators
async function* asyncGenerator() {
  for (let i = 0; i < 3; i++) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    yield i;
  }
}
```

### Proxy and Reflect

```javascript
// Basic proxy
const target = { name: 'John', age: 30 };
const handler = {
  get(target, property) {
    console.log(`Getting ${property}`);
    return target[property];
  },
  set(target, property, value) {
    console.log(`Setting ${property} to ${value}`);
    target[property] = value;
    return true;
  }
};

const proxy = new Proxy(target, handler);
proxy.name; // logs: Getting name
proxy.age = 31; // logs: Setting age to 31

// Validation proxy
const userValidator = {
  set(target, property, value) {
    if (property === 'age' && typeof value !== 'number') {
      throw new TypeError('Age must be a number');
    }
    if (property === 'email' && !value.includes('@')) {
      throw new Error('Invalid email');
    }
    return Reflect.set(target, property, value);
  }
};

const user = new Proxy({}, userValidator);

// Revocable proxy
const { proxy: revocableProxy, revoke } = Proxy.revocable(target, handler);
revoke(); // proxy becomes unusable

// Reflect API
Reflect.has(target, 'name'); // 'name' in target
Reflect.get(target, 'name'); // target.name
Reflect.set(target, 'name', 'Jane'); // target.name = 'Jane'
Reflect.deleteProperty(target, 'age'); // delete target.age
Reflect.ownKeys(target); // Object.keys(target)
```

## Built-in Objects

### Math Object

```javascript
// Constants
Math.PI; // 3.141592653589793
Math.E; // 2.718281828459045
Math.LN2; // Natural log of 2
Math.LN10; // Natural log of 10
Math.SQRT2; // Square root of 2

// Methods
Math.abs(-5); // 5
Math.ceil(4.3); // 5
Math.floor(4.7); // 4
Math.round(4.5); // 5
Math.trunc(4.9); // 4

Math.max(1, 2, 3); // 3
Math.min(1, 2, 3); // 1
Math.pow(2, 3); // 8
Math.sqrt(16); // 4
Math.cbrt(27); // 3

Math.random(); // 0 <= x < 1
Math.sign(-5); // -1
Math.sign(0); // 0
Math.sign(5); // 1

// Trigonometry
Math.sin(Math.PI / 2); // 1
Math.cos(Math.PI); // -1
Math.tan(0); // 0
Math.asin(1); // PI/2
Math.acos(0); // PI/2
Math.atan(1); // PI/4
Math.atan2(y, x); // angle in radians

// Logarithms
Math.log(Math.E); // 1
Math.log10(100); // 2
Math.log2(8); // 3

// Utility functions
const randomInt = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

const clamp = (value, min, max) => {
  return Math.min(Math.max(value, min), max);
};
```

### Date Object

```javascript
// Creating dates
const now = new Date();
const date1 = new Date('2024-03-15');
const date2 = new Date('March 15, 2024 10:30:00');
const date3 = new Date(2024, 2, 15); // March 15, 2024 (month is 0-indexed)
const date4 = new Date(1710504600000); // from timestamp

// Getting date components
date.getFullYear(); // 2024
date.getMonth(); // 0-11
date.getDate(); // 1-31
date.getDay(); // 0-6 (Sunday = 0)
date.getHours(); // 0-23
date.getMinutes(); // 0-59
date.getSeconds(); // 0-59
date.getMilliseconds(); // 0-999
date.getTime(); // timestamp
date.getTimezoneOffset(); // minutes from UTC

// Setting date components
date.setFullYear(2025);
date.setMonth(11); // December
date.setDate(25);
date.setHours(12, 30, 0, 0); // hours, minutes, seconds, ms

// Formatting dates
date.toString(); // full string representation
date.toISOString(); // '2024-03-15T10:30:00.000Z'
date.toLocaleDateString(); // locale date
date.toLocaleTimeString(); // locale time
date.toLocaleString('en-US', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric'
});

// Date calculations
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);

const daysBetween = (date1, date2) => {
  const diff = Math.abs(date2 - date1);
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
};
```

### JSON

```javascript
// JSON.stringify
const obj = { name: 'John', age: 30, city: 'New York' };
JSON.stringify(obj); // '{"name":"John","age":30,"city":"New York"}'

// With replacer function
JSON.stringify(obj, (key, value) => {
  if (typeof value === 'number') {
    return value * 2;
  }
  return value;
});

// With replacer array
JSON.stringify(obj, ['name', 'age']); // only include specified properties

// With spacing
JSON.stringify(obj, null, 2); // pretty print with 2 spaces

// JSON.parse
const jsonString = '{"name":"John","age":30}';
const parsed = JSON.parse(jsonString);

// With reviver function
JSON.parse(jsonString, (key, value) => {
  if (key === 'age') {
    return value + 1;
  }
  return value;
});

// Handling dates
const dateJSON = JSON.stringify({ date: new Date() });
const parsedDate = JSON.parse(dateJSON, (key, value) => {
  if (typeof value === 'string' && /\d{4}-\d{2}-\d{2}T/.test(value)) {
    return new Date(value);
  }
  return value;
});

// Error handling
try {
  JSON.parse('invalid json');
} catch (error) {
  console.error('Invalid JSON:', error.message);
}
```

### Map and Set

```javascript
// Map
const map = new Map();
map.set('key1', 'value1');
map.set(123, 'numeric key');
map.set(true, 'boolean key');

const objKey = { id: 1 };
map.set(objKey, 'object as key');

map.get('key1'); // 'value1'
map.has('key1'); // true
map.delete('key1'); // true
map.size; // 3
map.clear(); // remove all

// Map iteration
for (const [key, value] of map) {
  console.log(key, value);
}

map.forEach((value, key) => {
  console.log(key, value);
});

const keys = [...map.keys()];
const values = [...map.values()];
const entries = [...map.entries()];

// WeakMap (keys must be objects)
const weakMap = new WeakMap();
const obj = {};
weakMap.set(obj, 'value');

// Set
const set = new Set();
set.add(1);
set.add(2);
set.add(2); // ignored, already exists

set.has(1); // true
set.delete(1); // true
set.size; // 1
set.clear();

// Set from array (removes duplicates)
const uniqueArray = [...new Set([1, 2, 2, 3, 3, 4])]; // [1, 2, 3, 4]

// Set operations
const setA = new Set([1, 2, 3]);
const setB = new Set([2, 3, 4]);

// Union
const union = new Set([...setA, ...setB]);

// Intersection
const intersection = new Set([...setA].filter(x => setB.has(x)));

// Difference
const difference = new Set([...setA].filter(x => !setB.has(x)));

// WeakSet (values must be objects)
const weakSet = new WeakSet();
weakSet.add(obj);
```

## Web APIs

### Fetch API

```javascript
// Basic fetch
fetch('https://api.example.com/data')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

// Async/await
async function fetchData() {
  try {
    const response = await fetch('https://api.example.com/data');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

// POST request
fetch('https://api.example.com/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token'
  },
  body: JSON.stringify({
    name: 'John',
    email: 'john@example.com'
  })
});

// With abort controller
const controller = new AbortController();
const signal = controller.signal;

fetch('https://api.example.com/data', { signal })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => {
    if (error.name === 'AbortError') {
      console.log('Fetch aborted');
    }
  });

// Abort after timeout
setTimeout(() => controller.abort(), 5000);

// Handling different response types
const response = await fetch(url);
const text = await response.text();
const json = await response.json();
const blob = await response.blob();
const arrayBuffer = await response.arrayBuffer();
const formData = await response.formData();
```

### Local Storage and Session Storage

```javascript
// localStorage (persists after browser closes)
localStorage.setItem('username', 'John');
localStorage.getItem('username'); // 'John'
localStorage.removeItem('username');
localStorage.clear(); // remove all items

// Store objects (must serialize)
const user = { name: 'John', age: 30 };
localStorage.setItem('user', JSON.stringify(user));
const retrievedUser = JSON.parse(localStorage.getItem('user'));

// sessionStorage (cleared when tab closes)
sessionStorage.setItem('tempData', 'value');
sessionStorage.getItem('tempData');

// Storage event (for cross-tab communication)
window.addEventListener('storage', (event) => {
  console.log('Storage changed:', {
    key: event.key,
    oldValue: event.oldValue,
    newValue: event.newValue,
    url: event.url
  });
});

// Storage wrapper with expiry
class StorageWithExpiry {
  static set(key, value, ttl) {
    const now = new Date();
    const item = {
      value: value,
      expiry: now.getTime() + ttl
    };
    localStorage.setItem(key, JSON.stringify(item));
  }
  
  static get(key) {
    const itemStr = localStorage.getItem(key);
    if (!itemStr) return null;
    
    const item = JSON.parse(itemStr);
    const now = new Date();
    
    if (now.getTime() > item.expiry) {
      localStorage.removeItem(key);
      return null;
    }
    return item.value;
  }
}
```

### Web Workers

```javascript
// main.js
// Create worker
const worker = new Worker('worker.js');

// Send message to worker
worker.postMessage({ cmd: 'start', data: [1, 2, 3] });

// Receive message from worker
worker.onmessage = (event) => {
  console.log('Result from worker:', event.data);
};

// Handle errors
worker.onerror = (error) => {
  console.error('Worker error:', error);
};

// Terminate worker
worker.terminate();

// worker.js
// Listen for messages
self.onmessage = (event) => {
  const { cmd, data } = event.data;
  
  if (cmd === 'start') {
    const result = performHeavyComputation(data);
    self.postMessage(result);
  }
};

// Import scripts in worker
importScripts('utils.js', 'math.js');

// Shared Worker (for multiple tabs)
const sharedWorker = new SharedWorker('shared-worker.js');
sharedWorker.port.start();
sharedWorker.port.postMessage('Hello');
sharedWorker.port.onmessage = (event) => {
  console.log('From shared worker:', event.data);
};
```

### Intersection Observer

```javascript
// Basic intersection observer
const observer = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      console.log('Element is visible:', entry.target);
      // Optionally unobserve after first intersection
      observer.unobserve(entry.target);
    }
  });
}, {
  root: null, // viewport
  rootMargin: '0px',
  threshold: 0.5 // 50% visible
});

// Observe elements
const elements = document.querySelectorAll('.observe-me');
elements.forEach(el => observer.observe(el));

// Lazy loading images
const lazyImageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.add('loaded');
      lazyImageObserver.unobserve(img);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => {
  lazyImageObserver.observe(img);
});

// Infinite scroll
const lastItemObserver = new IntersectionObserver((entries) => {
  const lastItem = entries[0];
  if (lastItem.isIntersecting) {
    loadMoreItems();
  }
}, { threshold: 1 });

lastItemObserver.observe(document.querySelector('.last-item'));
```

## Best Practices

### Code Organization

```javascript
// Module pattern
const AppModule = (function() {
  // Private variables and functions
  let privateVar = 0;
  
  function privateMethod() {
    console.log('Private method');
  }
  
  // Public API
  return {
    publicMethod() {
      privateMethod();
      return ++privateVar;
    },
    
    getCount() {
      return privateVar;
    }
  };
})();

// Namespace pattern
const MyApp = MyApp || {};
MyApp.utils = {
  formatDate(date) {
    // implementation
  },
  
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
};

// Factory pattern
function createUser(name, role) {
  return {
    name,
    role,
    permissions: role === 'admin' ? ['read', 'write', 'delete'] : ['read'],
    
    hasPermission(permission) {
      return this.permissions.includes(permission);
    }
  };
}
```

### Performance Optimization

```javascript
// Debouncing
function debounce(func, delay) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

const debouncedSearch = debounce((query) => {
  console.log('Searching for:', query);
}, 300);

// Throttling
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

const throttledScroll = throttle(() => {
  console.log('Scroll event');
}, 100);

// Memoization
function memoize(fn) {
  const cache = new Map();
  return function(...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

const expensiveOperation = memoize((n) => {
  console.log('Computing...');
  return n * n;
});

// Request Animation Frame
function smoothScroll(target, duration) {
  const start = window.pageYOffset;
  const distance = target - start;
  let startTime = null;
  
  function animation(currentTime) {
    if (startTime === null) startTime = currentTime;
    const timeElapsed = currentTime - startTime;
    const progress = Math.min(timeElapsed / duration, 1);
    
    window.scrollTo(0, start + distance * easeInOutQuad(progress));
    
    if (timeElapsed < duration) {
      requestAnimationFrame(animation);
    }
  }
  
  function easeInOutQuad(t) {
    return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
  }
  
  requestAnimationFrame(animation);
}
```

### Security Best Practices

```javascript
// Input sanitization
function sanitizeHTML(str) {
  const temp = document.createElement('div');
  temp.textContent = str;
  return temp.innerHTML;
}

// Avoid eval
// Bad
eval('console.log("Hello")');

// Good
Function('"use strict"; console.log("Hello")')();

// Content Security Policy
// Set in HTML header or meta tag
// <meta http-equiv="Content-Security-Policy" content="default-src 'self'">

// XSS prevention
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// CSRF token
async function makeSecureRequest(url, data) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken
    },
    credentials: 'same-origin',
    body: JSON.stringify(data)
  });
}

// Secure random values
const array = new Uint32Array(10);
crypto.getRandomValues(array);

// Password hashing (use server-side, this is for demo)
async function hashPassword(password) {
  const msgUint8 = new TextEncoder().encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
```

### Testing Patterns

```javascript
// Unit testing pattern
function add(a, b) {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new TypeError('Arguments must be numbers');
  }
  return a + b;
}

// Simple test framework
const assert = {
  equal(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(message || `Expected ${expected}, got ${actual}`);
    }
  },
  
  deepEqual(actual, expected, message) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      throw new Error(message || 'Objects are not equal');
    }
  },
  
  throws(fn, message) {
    try {
      fn();
      throw new Error(message || 'Expected function to throw');
    } catch (error) {
      // Expected
    }
  }
};

// Test suite
function runTests() {
  const tests = [
    {
      name: 'add should return sum of two numbers',
      test: () => {
        assert.equal(add(2, 3), 5);
        assert.equal(add(-1, 1), 0);
      }
    },
    {
      name: 'add should throw for non-numbers',
      test: () => {
        assert.throws(() => add('2', 3));
        assert.throws(() => add(2, null));
      }
    }
  ];
  
  tests.forEach(({ name, test }) => {
    try {
      test();
      console.log(`✓ ${name}`);
    } catch (error) {
      console.error(`✗ ${name}: ${error.message}`);
    }
  });
}

// Mocking
class MockAPI {
  constructor(responses) {
    this.responses = responses;
    this.calls = [];
  }
  
  fetch(url) {
    this.calls.push(url);
    return Promise.resolve(this.responses[url] || null);
  }
}
```

## Conclusion

This comprehensive JavaScript documentation covers the core concepts, modern features, and best practices of JavaScript development. From basic syntax to advanced patterns, these examples provide a solid foundation for building robust JavaScript applications.

Remember to:
- Always consider browser compatibility when using newer features
- Follow consistent coding standards
- Write testable and maintainable code
- Keep security in mind
- Optimize for performance when necessary
- Use appropriate error handling
- Document your code properly

JavaScript continues to evolve, so stay updated with the latest ECMAScript specifications and best practices in the JavaScript community.