# Python Complete Documentation

## Table of Contents
1. [Core Syntax and Data Types](#core-syntax-and-data-types)
2. [Variables and Type Annotations](#variables-and-type-annotations)
3. [Control Flow](#control-flow)
4. [Functions](#functions)
5. [Classes and OOP](#classes-and-oop)
6. [Error Handling](#error-handling)
7. [File I/O](#file-io)
8. [Standard Library Essentials](#standard-library-essentials)
9. [Async Programming](#async-programming)
10. [Context Variables](#context-variables)
11. [Type System and Generics](#type-system-and-generics)
12. [Advanced Features](#advanced-features)

---

## Core Syntax and Data Types

### Basic Data Types

#### Numeric Types
```python
# Integer
age = 25
big_number = 1_000_000  # Underscores for readability

# Float
price = 19.99
scientific = 1.5e10

# Complex
z = 3 + 4j
```

#### String Types
```python
# String literals
name = "Alice"
message = 'Hello World'
multiline = """
This is a
multiline string
"""

# String methods
text = "Hello, World!"
print(text.upper())        # HELLO, WORLD!
print(text.lower())        # hello, world!
print(text.replace("World", "Python"))  # Hello, Python!
print(text.split(","))     # ['Hello', ' World!']
```

#### Boolean Type
```python
is_active = True
is_complete = False

# Boolean operations
result = True and False  # False
result = True or False   # True
result = not True        # False
```

#### None Type
```python
data = None
if data is None:
    print("No data available")
```

### Collection Types

#### Lists (Mutable)
```python
# List creation
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]

# List operations
fruits.append("orange")
fruits.insert(1, "grape")
fruits.remove("banana")
popped = fruits.pop()

# List comprehensions
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
```

#### Tuples (Immutable)
```python
# Tuple creation
coordinates = (10, 20)
colors = ("red", "green", "blue")

# Named tuples
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(10, 20)
print(p.x, p.y)
```

#### Dictionaries
```python
# Dictionary creation
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}

# Dictionary operations
person["email"] = "alice@example.com"
age = person.get("age", 0)
keys = list(person.keys())
values = list(person.values())

# Dictionary comprehensions
squares_dict = {x: x**2 for x in range(5)}
```

#### Sets
```python
# Set creation
unique_numbers = {1, 2, 3, 4, 5}
fruits_set = set(["apple", "banana", "apple"])  # Duplicates removed

# Set operations
set1 = {1, 2, 3}
set2 = {3, 4, 5}
union = set1 | set2        # {1, 2, 3, 4, 5}
intersection = set1 & set2  # {3}
difference = set1 - set2    # {1, 2}
```

---

## Variables and Type Annotations

### Variable Declaration and Assignment
```python
# Simple assignment
x = 10
name = "Alice"

# Multiple assignment
a, b, c = 1, 2, 3
x = y = z = 0

# Swapping variables
a, b = b, a
```

### Type Annotations (PEP 526)
```python
# Basic type annotations
name: str = "Alice"
age: int = 30
height: float = 5.8
is_student: bool = True

# Collections with type hints
numbers: list[int] = [1, 2, 3, 4]
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
coordinates: tuple[float, float] = (10.5, 20.3)

# Optional types
from typing import Optional
middle_name: Optional[str] = None
data: int | None = None  # Python 3.10+ union syntax
```

### Advanced Type Annotations
```python
from typing import Union, List, Dict, Callable, TypeVar, Generic

# Union types
def process_id(user_id: Union[int, str]) -> str:
    return str(user_id)

# Modern union syntax (Python 3.10+)
def process_data(data: int | str | float) -> str:
    return str(data)

# Callable types
def apply_operation(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# Generic types
T = TypeVar('T')

def first_item(items: List[T]) -> T:
    return items[0]

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()
```

### Class Variables and Instance Variables
```python
from typing import ClassVar

class Counter:
    # Class variable
    total_instances: ClassVar[int] = 0
    
    def __init__(self, value: int) -> None:
        # Instance variable
        self.value: int = value
        Counter.total_instances += 1
```

---

## Control Flow

### Conditional Statements
```python
# Basic if-elif-else
age = 18
if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")

# Conditional expressions (ternary operator)
status = "Adult" if age >= 18 else "Minor"

# Match-case (Python 3.10+)
def handle_status_code(code: int) -> str:
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return "Unknown"
```

### Loops

#### For Loops
```python
# Iterating over sequences
for fruit in ["apple", "banana", "cherry"]:
    print(fruit)

# Range function
for i in range(5):          # 0 to 4
    print(i)

for i in range(1, 6):       # 1 to 5
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8
    print(i)

# Enumerate for index and value
for index, value in enumerate(["a", "b", "c"]):
    print(f"{index}: {value}")

# Dictionary iteration
person = {"name": "Alice", "age": 30}
for key, value in person.items():
    print(f"{key}: {value}")
```

#### While Loops
```python
# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1

# While with else
num = 5
while num > 0:
    print(num)
    num -= 1
else:
    print("Loop completed")
```

#### Loop Control
```python
# Break and continue
for i in range(10):
    if i == 3:
        continue  # Skip this iteration
    if i == 7:
        break     # Exit the loop
    print(i)

# Nested loops with labels (using functions)
def find_value(matrix, target):
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value == target:
                return i, j
    return None
```

---

## Functions

### Basic Function Definition
```python
def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# Function with default parameters
def greet_with_title(name: str, title: str = "Mr.") -> str:
    return f"Hello, {title} {name}!"

# Function with variable arguments
def sum_all(*args: int) -> int:
    return sum(args)

# Function with keyword arguments
def create_person(**kwargs: str) -> dict[str, str]:
    return kwargs

# Mixed parameters
def process_data(required: str, *args: int, default: str = "N/A", **kwargs: str) -> dict:
    return {
        "required": required,
        "args": args,
        "default": default,
        "kwargs": kwargs
    }
```

### Lambda Functions
```python
# Basic lambda
square = lambda x: x ** 2

# Lambda with multiple parameters
add = lambda x, y: x + y

# Using lambdas with built-in functions
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))

# Sorting with lambda
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
students.sort(key=lambda student: student[1])  # Sort by grade
```

### Decorators
```python
from functools import wraps
import time

# Simple decorator
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

# Decorator with parameters
def retry(max_attempts: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(1)
        return wrapper
    return decorator

@retry(3)
def unreliable_function():
    import random
    if random.random() < 0.7:
        raise ValueError("Random error")
    return "Success"
```

### Higher-Order Functions
```python
# Function that returns a function
def multiplier(factor: int):
    def multiply(number: int) -> int:
        return number * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)

# Function that takes functions as arguments
def apply_operation(numbers: list[int], operation):
    return [operation(num) for num in numbers]

numbers = [1, 2, 3, 4, 5]
doubled = apply_operation(numbers, lambda x: x * 2)
```

---

## Classes and OOP

### Basic Class Definition
```python
class Person:
    """A class representing a person."""
    
    # Class variable
    species = "Homo sapiens"
    
    def __init__(self, name: str, age: int) -> None:
        """Initialize a Person instance."""
        self.name = name
        self.age = age
    
    def greet(self) -> str:
        """Return a greeting."""
        return f"Hello, I'm {self.name}"
    
    def have_birthday(self) -> None:
        """Increment age by 1."""
        self.age += 1
    
    def __str__(self) -> str:
        """String representation."""
        return f"Person(name='{self.name}', age={self.age})"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"Person('{self.name}', {self.age})"

# Creating instances
person1 = Person("Alice", 30)
person2 = Person("Bob", 25)
```

### Inheritance
```python
class Animal:
    def __init__(self, name: str, species: str) -> None:
        self.name = name
        self.species = species
    
    def make_sound(self) -> str:
        return "Some generic animal sound"
    
    def info(self) -> str:
        return f"{self.name} is a {self.species}"

class Dog(Animal):
    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name, "Canine")
        self.breed = breed
    
    def make_sound(self) -> str:
        return "Woof!"
    
    def fetch(self) -> str:
        return f"{self.name} is fetching the ball"

class Cat(Animal):
    def __init__(self, name: str, indoor: bool = True) -> None:
        super().__init__(name, "Feline")
        self.indoor = indoor
    
    def make_sound(self) -> str:
        return "Meow!"
    
    def purr(self) -> str:
        return f"{self.name} is purring"

# Multiple inheritance
class FlyingMixin:
    def fly(self) -> str:
        return "Flying high!"

class Bird(Animal, FlyingMixin):
    def __init__(self, name: str, wingspan: float) -> None:
        super().__init__(name, "Avian")
        self.wingspan = wingspan
    
    def make_sound(self) -> str:
        return "Tweet!"
```

### Properties and Descriptors
```python
class Temperature:
    def __init__(self, celsius: float = 0) -> None:
        self._celsius = celsius
    
    @property
    def celsius(self) -> float:
        return self._celsius
    
    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero")
        self._celsius = value
    
    @property
    def fahrenheit(self) -> float:
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5/9
    
    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15

# Usage
temp = Temperature(25)
print(temp.fahrenheit)  # 77.0
temp.fahrenheit = 100
print(temp.celsius)     # 37.77777777777778
```

### Abstract Base Classes
```python
from abc import ABC, abstractmethod
from typing import Protocol

# Using ABC
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

# Using Protocol (Structural typing)
class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius
    
    def draw(self) -> str:
        return f"Drawing a circle with radius {self.radius}"

def render(drawable: Drawable) -> None:
    print(drawable.draw())
```

### Dataclasses
```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Point:
    x: float
    y: float
    
    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

@dataclass
class Person:
    name: str
    age: int
    hobbies: List[str] = field(default_factory=list)
    _private_id: str = field(default="", repr=False)
    
    def __post_init__(self) -> None:
        if self._private_id == "":
            self._private_id = f"user_{hash(self.name)}"

# Usage
point = Point(3, 4)
person = Person("Alice", 30, ["reading", "hiking"])
```

### Special Methods (Magic Methods)
```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    
    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector':
        return Vector(self.x * scalar, self.y * scalar)
    
    def __len__(self) -> int:
        return 2
    
    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Vector index out of range")
    
    def __str__(self) -> str:
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        return f"Vector({self.x!r}, {self.y!r})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False

# Usage
v1 = Vector(1, 2)
v2 = Vector(3, 4)
v3 = v1 + v2  # Vector(4, 6)
```

---

## Error Handling

### Basic Exception Handling
```python
# Try-except block
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")

# Multiple exceptions
try:
    value = int(input("Enter a number: "))
    result = 10 / value
except ValueError:
    print("Invalid number format")
except ZeroDivisionError:
    print("Cannot divide by zero")

# Catching multiple exception types
try:
    # Some risky operation
    pass
except (ValueError, TypeError) as e:
    print(f"Error occurred: {e}")

# Catch all exceptions (use sparingly)
try:
    # Some operation
    pass
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Exception Handling with Else and Finally
```python
try:
    file = open("data.txt", "r")
    data = file.read()
except FileNotFoundError:
    print("File not found")
except PermissionError:
    print("Permission denied")
else:
    # Executed if no exception occurred
    print("File read successfully")
    print(f"Data length: {len(data)}")
finally:
    # Always executed
    if 'file' in locals() and not file.closed:
        file.close()
        print("File closed")
```

### Custom Exceptions
```python
class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class EmailValidationError(ValidationError):
    """Raised when email validation fails."""
    def __init__(self, email: str, message: str = "Invalid email format"):
        self.email = email
        self.message = message
        super().__init__(self.message)

def validate_email(email: str) -> None:
    if "@" not in email:
        raise EmailValidationError(email, "Email must contain @ symbol")
    if not email.endswith(".com"):
        raise EmailValidationError(email, "Email must end with .com")

# Usage
try:
    validate_email("invalid_email")
except EmailValidationError as e:
    print(f"Validation failed for {e.email}: {e.message}")
```

### Context Managers
```python
# Using context managers for resource management
with open("data.txt", "r") as file:
    content = file.read()
# File is automatically closed

# Custom context manager
class Timer:
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        print(f"Elapsed time: {self.end - self.start:.4f} seconds")

with Timer():
    time.sleep(1)
    # Some operation

# Context manager using contextlib
from contextlib import contextmanager

@contextmanager
def database_transaction():
    print("Starting transaction")
    try:
        yield "connection"
    except Exception:
        print("Rolling back transaction")
        raise
    else:
        print("Committing transaction")

with database_transaction() as conn:
    print(f"Using {conn}")
    # Database operations
```

---

## File I/O

### Basic File Operations
```python
# Reading files
with open("example.txt", "r") as file:
    content = file.read()  # Read entire file
    
with open("example.txt", "r") as file:
    lines = file.readlines()  # Read all lines as list
    
with open("example.txt", "r") as file:
    for line in file:  # Iterate line by line
        print(line.strip())

# Writing files
with open("output.txt", "w") as file:
    file.write("Hello, World!\n")
    file.writelines(["Line 1\n", "Line 2\n"])

# Appending to files
with open("log.txt", "a") as file:
    file.write("New log entry\n")
```

### Working with Different Encodings
```python
# Reading with specific encoding
with open("data.txt", "r", encoding="utf-8") as file:
    content = file.read()

# Writing with specific encoding
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Unicode content: ñáéíóú")

# Binary file operations
with open("image.jpg", "rb") as file:
    binary_data = file.read()

with open("copy.jpg", "wb") as file:
    file.write(binary_data)
```

### Path Operations
```python
from pathlib import Path
import os

# Using pathlib (recommended)
path = Path("data/files/example.txt")
print(path.exists())
print(path.is_file())
print(path.parent)
print(path.suffix)
print(path.stem)

# Creating directories
Path("new_directory").mkdir(exist_ok=True)
Path("nested/directories").mkdir(parents=True, exist_ok=True)

# Iterating through directory
for file_path in Path(".").iterdir():
    if file_path.is_file():
        print(file_path.name)

# Finding files with patterns
for py_file in Path(".").glob("*.py"):
    print(py_file)

for py_file in Path(".").rglob("*.py"):  # Recursive
    print(py_file)

# Using os.path (legacy approach)
file_path = os.path.join("data", "files", "example.txt")
print(os.path.exists(file_path))
print(os.path.dirname(file_path))
print(os.path.basename(file_path))
```

### JSON and CSV Operations
```python
import json
import csv

# JSON operations
data = {"name": "Alice", "age": 30, "hobbies": ["reading", "hiking"]}

# Write JSON
with open("data.json", "w") as file:
    json.dump(data, file, indent=2)

# Read JSON
with open("data.json", "r") as file:
    loaded_data = json.load(file)

# CSV operations
# Write CSV
with open("people.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Age", "City"])
    writer.writerow(["Alice", 30, "New York"])
    writer.writerow(["Bob", 25, "Boston"])

# Read CSV
with open("people.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)

# CSV with dictionaries
with open("people.csv", "w", newline="") as file:
    fieldnames = ["name", "age", "city"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30, "city": "New York"})

with open("people.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row["name"], row["age"])
```

---

## Standard Library Essentials

### Collections Module
```python
from collections import defaultdict, Counter, deque, namedtuple, OrderedDict

# defaultdict
dd = defaultdict(list)
dd['key1'].append('value1')  # No KeyError

# Counter
text = "hello world"
counter = Counter(text)
print(counter.most_common(3))  # [('l', 3), ('o', 2), ('h', 1)]

# deque (double-ended queue)
dq = deque([1, 2, 3])
dq.appendleft(0)    # deque([0, 1, 2, 3])
dq.append(4)        # deque([0, 1, 2, 3, 4])
dq.popleft()        # Returns 0
dq.pop()           # Returns 4

# namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(p.x, p.y)
```

### itertools Module
```python
import itertools

# Infinite iterators
count = itertools.count(10, 2)  # 10, 12, 14, 16, ...
cycle = itertools.cycle(['A', 'B', 'C'])  # A, B, C, A, B, C, ...
repeat = itertools.repeat('hello', 3)  # hello, hello, hello

# Combinatorial functions
combinations = list(itertools.combinations('ABCD', 2))  # AB, AC, AD, BC, BD, CD
permutations = list(itertools.permutations('ABC', 2))   # AB, AC, BA, BC, CA, CB
product = list(itertools.product('AB', '12'))          # A1, A2, B1, B2

# Grouping
data = [1, 1, 2, 2, 2, 3, 3]
groups = itertools.groupby(data)
for key, group in groups:
    print(key, list(group))

# Chain and accumulate
chained = itertools.chain([1, 2], [3, 4], [5, 6])  # 1, 2, 3, 4, 5, 6
accumulated = list(itertools.accumulate([1, 2, 3, 4]))  # [1, 3, 6, 10]
```

### datetime Module
```python
from datetime import datetime, date, time, timedelta, timezone
import calendar

# Current date and time
now = datetime.now()
today = date.today()
current_time = datetime.now().time()

# Creating specific dates
birthday = date(1990, 5, 15)
meeting_time = datetime(2023, 12, 25, 14, 30, 0)

# Formatting dates
formatted = now.strftime("%Y-%m-%d %H:%M:%S")
parsed = datetime.strptime("2023-12-25", "%Y-%m-%d")

# Date arithmetic
tomorrow = today + timedelta(days=1)
next_week = now + timedelta(weeks=1)
past_hour = now - timedelta(hours=1)

# Timezone handling
utc_now = datetime.now(timezone.utc)
local_time = utc_now.astimezone()

# Working with timestamps
timestamp = now.timestamp()
from_timestamp = datetime.fromtimestamp(timestamp)
```

### math Module
```python
import math

# Basic functions
print(math.sqrt(16))        # 4.0
print(math.pow(2, 3))       # 8.0
print(math.ceil(4.3))       # 5
print(math.floor(4.7))      # 4
print(math.factorial(5))    # 120

# Trigonometric functions
print(math.sin(math.pi/2))  # 1.0
print(math.cos(0))          # 1.0
print(math.tan(math.pi/4))  # 1.0

# Logarithmic functions
print(math.log(math.e))     # 1.0
print(math.log10(100))      # 2.0
print(math.log2(8))         # 3.0

# Constants
print(math.pi)              # 3.141592653589793
print(math.e)               # 2.718281828459045
```

### random Module
```python
import random

# Basic random operations
print(random.random())              # Random float between 0 and 1
print(random.randint(1, 10))        # Random integer between 1 and 10
print(random.uniform(1.0, 10.0))    # Random float between 1.0 and 10.0

# Choosing from sequences
colors = ['red', 'green', 'blue', 'yellow']
print(random.choice(colors))        # Random choice
print(random.choices(colors, k=3))  # Random choices with replacement
print(random.sample(colors, 2))     # Random sample without replacement

# Shuffling
numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)             # Shuffle in place
print(numbers)

# Random with seed for reproducibility
random.seed(42)
print(random.randint(1, 100))       # Always same result with same seed
```

---

## Async Programming

### Basic Async/Await
```python
import asyncio
import aiohttp
import time

# Basic async function
async def say_hello(name: str, delay: float) -> str:
    print(f"Starting to greet {name}")
    await asyncio.sleep(delay)
    result = f"Hello, {name}!"
    print(f"Finished greeting {name}")
    return result

# Running async functions
async def main():
    # Sequential execution
    result1 = await say_hello("Alice", 1)
    result2 = await say_hello("Bob", 1)
    print(f"Results: {result1}, {result2}")
    
    # Concurrent execution
    task1 = say_hello("Charlie", 1)
    task2 = say_hello("Diana", 1)
    results = await asyncio.gather(task1, task2)
    print(f"Concurrent results: {results}")

# Run the main function
# asyncio.run(main())
```

### Async Context Managers
```python
class AsyncTimer:
    async def __aenter__(self):
        self.start = time.time()
        print("Timer started")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        print(f"Timer finished: {self.end - self.start:.2f} seconds")

async def timed_operation():
    async with AsyncTimer():
        await asyncio.sleep(2)
        print("Operation completed")
```

### Async Iterators and Generators
```python
class AsyncRange:
    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.start >= self.stop:
            raise StopAsyncIteration
        current = self.start
        self.start += 1
        await asyncio.sleep(0.1)  # Simulate async work
        return current

async def async_generator(n: int):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def use_async_iterators():
    # Using async iterator
    async for value in AsyncRange(0, 5):
        print(f"AsyncRange value: {value}")
    
    # Using async generator
    async for value in async_generator(3):
        print(f"AsyncGen value: {value}")
```

### Working with Tasks
```python
async def fetch_data(url: str, session_id: int) -> dict:
    print(f"Session {session_id}: Fetching {url}")
    await asyncio.sleep(1)  # Simulate network delay
    return {"url": url, "session_id": session_id, "status": "success"}

async def main_with_tasks():
    # Creating tasks
    task1 = asyncio.create_task(fetch_data("https://api1.com", 1))
    task2 = asyncio.create_task(fetch_data("https://api2.com", 2))
    task3 = asyncio.create_task(fetch_data("https://api3.com", 3))
    
    # Wait for all tasks
    results = await asyncio.gather(task1, task2, task3)
    print("All tasks completed:", results)
    
    # Wait for first completed task
    done, pending = await asyncio.wait(
        [task1, task2, task3], 
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # Cancel pending tasks
    for task in pending:
        task.cancel()
```

### Exception Handling in Async Code
```python
async def risky_operation(fail: bool = False) -> str:
    await asyncio.sleep(1)
    if fail:
        raise ValueError("Operation failed!")
    return "Success!"

async def handle_async_exceptions():
    try:
        result = await risky_operation(fail=True)
    except ValueError as e:
        print(f"Caught exception: {e}")
    
    # Handling exceptions in gather
    results = await asyncio.gather(
        risky_operation(fail=False),
        risky_operation(fail=True),
        return_exceptions=True
    )
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i} failed: {result}")
        else:
            print(f"Task {i} succeeded: {result}")
```

---

## Context Variables

### Basic Context Variables Usage
```python
from contextvars import ContextVar
import asyncio

# Create context variables
request_id: ContextVar[str] = ContextVar('request_id', default='no-request')
user_id: ContextVar[int] = ContextVar('user_id')

def log_message(message: str) -> None:
    req_id = request_id.get()
    try:
        uid = user_id.get()
        print(f"[{req_id}] [User: {uid}] {message}")
    except LookupError:
        print(f"[{req_id}] [No User] {message}")

async def process_request(req_id: str, uid: int) -> None:
    # Set context variables
    request_id.set(req_id)
    user_id.set(uid)
    
    log_message("Processing request")
    await asyncio.sleep(1)
    log_message("Request completed")

async def main_context():
    # Each task gets its own context
    await asyncio.gather(
        process_request("req-001", 123),
        process_request("req-002", 456),
        process_request("req-003", 789)
    )
```

### Context Variables with Tokens
```python
def update_context_temporarily():
    # Store original value
    original_req_id = request_id.get()
    print(f"Original request ID: {original_req_id}")
    
    # Set new value and get token
    token = request_id.set("temp-request")
    print(f"Temporary request ID: {request_id.get()}")
    
    try:
        # Do some work with new context
        log_message("Working with temporary context")
    finally:
        # Reset to original value
        request_id.reset(token)
        print(f"Restored request ID: {request_id.get()}")

# Context manager for automatic reset (Python 3.14+)
def with_context_value():
    with request_id.set("scoped-request"):
        log_message("Inside context manager")
        # Context automatically resets when exiting
    log_message("Outside context manager")
```

### Custom Context Management
```python
from contextvars import copy_context
import asyncio

class RequestContext:
    def __init__(self, request_id: str, user_id: int, trace_id: str = None):
        self.request_id = request_id
        self.user_id = user_id
        self.trace_id = trace_id or f"trace-{request_id}"
    
    def apply(self):
        request_id.set(self.request_id)
        user_id.set(self.user_id)
        # You could set more context variables here

async def run_with_context(context: RequestContext, coro):
    """Run a coroutine with a specific context."""
    ctx = copy_context()
    
    def setup_context():
        context.apply()
    
    ctx.run(setup_context)
    return await coro

# Usage
async def business_logic():
    log_message("Executing business logic")
    await asyncio.sleep(0.5)
    log_message("Business logic completed")

async def main_with_custom_context():
    context1 = RequestContext("req-A", 100)
    context2 = RequestContext("req-B", 200)
    
    await asyncio.gather(
        run_with_context(context1, business_logic()),
        run_with_context(context2, business_logic())
    )
```

---

## Type System and Generics

### Type Variables and Constraints
```python
from typing import TypeVar, Generic, Protocol, Union, List, Dict, Callable

# Basic type variable
T = TypeVar('T')

def first_item(items: List[T]) -> T:
    return items[0]

# Constrained type variable
AnyStr = TypeVar('AnyStr', str, bytes)

def concat(a: AnyStr, b: AnyStr) -> AnyStr:
    return a + b

# Bounded type variable
from collections.abc import Sized

Sized_T = TypeVar('Sized_T', bound=Sized)

def get_length(obj: Sized_T) -> int:
    return len(obj)
```

### Generic Classes
```python
from typing import Generic, TypeVar, Optional, List, Iterator

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def peek(self) -> Optional[T]:
        return self._items[-1] if self._items else None
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __iter__(self) -> Iterator[T]:
        return reversed(self._items)

# Usage
string_stack: Stack[str] = Stack()
string_stack.push("hello")
string_stack.push("world")

int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
```

### Generic with Multiple Type Parameters
```python
class Pair(Generic[K, V]):
    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value
    
    def get_key(self) -> K:
        return self.key
    
    def get_value(self) -> V:
        return self.value
    
    def __str__(self) -> str:
        return f"Pair({self.key}, {self.value})"

# Usage
name_age: Pair[str, int] = Pair("Alice", 30)
coordinates: Pair[float, float] = Pair(10.5, 20.3)
```

### Protocols for Structural Typing
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> str: ...

@runtime_checkable
class Comparable(Protocol):
    def __lt__(self, other) -> bool: ...

class Circle:
    def __init__(self, radius: float):
        self.radius = radius
    
    def draw(self) -> str:
        return f"Drawing circle with radius {self.radius}"
    
    def __lt__(self, other: 'Circle') -> bool:
        return self.radius < other.radius

def render_shape(shape: Drawable) -> None:
    print(shape.draw())

def sort_items(items: List[Comparable]) -> List[Comparable]:
    return sorted(items)

# Usage
circle = Circle(5.0)
render_shape(circle)  # Works because Circle implements Drawable protocol

circles = [Circle(3), Circle(1), Circle(5)]
sorted_circles = sort_items(circles)  # Works because Circle implements Comparable
```

### Type Aliases and NewType
```python
from typing import NewType, Union, List, Dict

# Type aliases
UserId = NewType('UserId', int)
UserName = NewType('UserName', str)

# Union types (modern syntax)
NumberLike = Union[int, float]  # Traditional syntax
NumberLike = int | float        # Python 3.10+ syntax

# Complex type aliases
UserData = Dict[str, Union[str, int, List[str]]]
ProcessingResult = Union[str, int, None]

def create_user(user_id: UserId, name: UserName) -> UserData:
    return {
        "id": user_id,
        "name": name,
        "roles": ["user"]
    }

def process_number(value: NumberLike) -> ProcessingResult:
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return int(value)
    return None

# Usage
user_id = UserId(123)  # Type-safe user ID
user_name = UserName("Alice")  # Type-safe user name
user = create_user(user_id, user_name)
```

### Advanced Generic Patterns
```python
from typing import TypeVar, Generic, Callable, ParamSpec, TypeVarTuple, Unpack

P = ParamSpec('P')
R = TypeVar('R')

def log_function_calls(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

@log_function_calls
def add_numbers(a: int, b: int) -> int:
    return a + b

@log_function_calls
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# Variadic generics (Python 3.11+)
Ts = TypeVarTuple('Ts')

class Array(Generic[Unpack[Ts]]):
    def __init__(self, *args: Unpack[Ts]) -> None:
        self.data = args
    
    def get(self) -> tuple[Unpack[Ts]]:
        return self.data

# Usage
arr = Array(1, "hello", 3.14)  # Array[int, str, float]
data = arr.get()  # Returns tuple[int, str, float]
```

---

## Advanced Features

### Descriptors
```python
class ValidatedAttribute:
    def __init__(self, name: str, validator: Callable[[any], bool] = None):
        self.name = name
        self.validator = validator or (lambda x: True)
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(f"Invalid value for {self.name}: {value}")
        obj.__dict__[self.name] = value
    
    def __delete__(self, obj):
        del obj.__dict__[self.name]

class Person:
    name = ValidatedAttribute('name', lambda x: isinstance(x, str) and len(x) > 0)
    age = ValidatedAttribute('age', lambda x: isinstance(x, int) and 0 <= x <= 150)
    
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

### Metaclasses
```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseConnection(metaclass=SingletonMeta):
    def __init__(self, host: str = "localhost"):
        self.host = host
        self.connected = False
    
    def connect(self):
        if not self.connected:
            print(f"Connecting to {self.host}")
            self.connected = True
        return self

# Usage
db1 = DatabaseConnection("server1")
db2 = DatabaseConnection("server2")
print(db1 is db2)  # True - same instance
```

### Coroutines and Async Generators
```python
import asyncio
from typing import AsyncGenerator, AsyncIterator

async def async_range(start: int, stop: int, step: int = 1) -> AsyncGenerator[int, None]:
    current = start
    while current < stop:
        await asyncio.sleep(0.01)  # Simulate async work
        yield current
        current += step

async def fetch_pages(urls: List[str]) -> AsyncGenerator[str, None]:
    for url in urls:
        await asyncio.sleep(0.1)  # Simulate network request
        yield f"Content from {url}"

async def consume_async_generator():
    async for number in async_range(0, 10, 2):
        print(f"Generated: {number}")
    
    urls = ["http://api1.com", "http://api2.com", "http://api3.com"]
    async for content in fetch_pages(urls):
        print(content)
```

### Advanced Decorators with Typing
```python
from functools import wraps
from typing import TypeVar, Callable, ParamSpec, Any, cast
import asyncio

P = ParamSpec('P')
T = TypeVar('T')

def rate_limit(calls_per_second: float):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        last_called = 0.0
        min_interval = 1.0 / calls_per_second
        
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            nonlocal last_called
            import time
            now = time.time()
            time_since_last = now - last_called
            
            if time_since_last < min_interval:
                time.sleep(min_interval - time_since_last)
            
            last_called = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def async_retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            raise last_exception
        
        return wrapper
    return decorator

@rate_limit(2.0)  # Max 2 calls per second
def api_call(endpoint: str) -> str:
    return f"Called {endpoint}"

@async_retry(max_attempts=3, delay=0.5)
async def unreliable_async_operation() -> str:
    import random
    if random.random() < 0.7:
        raise ConnectionError("Network error")
    return "Success"
```

---

## Best Practices and Tips

### Code Organization
```python
# Use type hints consistently
from typing import Optional, List, Dict, Protocol
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    host: str
    port: int
    debug: bool = False
    allowed_hosts: List[str] = None
    
    def __post_init__(self):
        if self.allowed_hosts is None:
            self.allowed_hosts = ["localhost"]

class DatabaseProtocol(Protocol):
    def connect(self) -> None: ...
    def execute(self, query: str) -> List[Dict[str, Any]]: ...
    def close(self) -> None: ...

def load_config(config_path: Path) -> Config:
    # Implementation here
    pass
```

### Error Handling Best Practices
```python
import logging
from typing import Union, Result  # Result type if using a library like returns

logger = logging.getLogger(__name__)

class ApplicationError(Exception):
    """Base exception for application errors."""
    pass

class ValidationError(ApplicationError):
    """Raised when data validation fails."""
    pass

class NetworkError(ApplicationError):
    """Raised when network operations fail."""
    pass

def validate_email(email: str) -> None:
    if not email or "@" not in email:
        raise ValidationError(f"Invalid email format: {email}")

def safe_divide(a: float, b: float) -> Union[float, None]:
    """Safely divide two numbers, returning None if division by zero."""
    try:
        return a / b
    except ZeroDivisionError:
        logger.warning(f"Division by zero attempted: {a} / {b}")
        return None

def robust_operation(data: Dict[str, Any]) -> Union[str, ApplicationError]:
    """Example of explicit error handling."""
    try:
        validate_email(data.get("email", ""))
        result = process_data(data)
        return result
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        return e
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return ApplicationError(f"Processing failed: {str(e)}")
```

### Performance Considerations
```python
# Use generators for large datasets
def process_large_file(filename: str):
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip().upper()

# Use slots for memory efficiency
class Point:
    __slots__ = ['x', 'y']
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> int:
    # Simulate expensive operation
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

# Use appropriate data structures
from collections import deque, defaultdict
from bisect import bisect_left

# Use deque for efficient append/pop operations at both ends
recent_items = deque(maxlen=100)

# Use defaultdict to avoid KeyError
grouped_data = defaultdict(list)
```

This documentation provides a comprehensive overview of Python's core features, from basic syntax to advanced concepts. Each section includes practical examples that demonstrate real-world usage patterns. The documentation is organized to serve as both a learning resource and a quick reference guide for Python development.