# NumPy Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Array Creation](#array-creation)
4. [Array Attributes and Methods](#array-attributes-and-methods)
5. [Indexing and Slicing](#indexing-and-slicing)
6. [Array Operations](#array-operations)
7. [Broadcasting](#broadcasting)
8. [Universal Functions (ufuncs)](#universal-functions-ufuncs)
9. [Mathematical Functions](#mathematical-functions)
10. [Linear Algebra](#linear-algebra)
11. [Random Number Generation](#random-number-generation)
12. [Array Manipulation](#array-manipulation)
13. [Input/Output](#inputoutput)
14. [Data Types](#data-types)
15. [Structured Arrays](#structured-arrays)
16. [Masked Arrays](#masked-arrays)
17. [FFT and Signal Processing](#fft-and-signal-processing)
18. [Polynomials](#polynomials)
19. [Performance Optimization](#performance-optimization)
20. [Best Practices](#best-practices)

## Introduction

NumPy (Numerical Python) is the fundamental package for scientific computing in Python. It provides a powerful N-dimensional array object, sophisticated broadcasting functions, tools for integrating C/C++ and Fortran code, and useful linear algebra, Fourier transform, and random number capabilities.

### Key Features
- Powerful N-dimensional array object (ndarray)
- Broadcasting functions for universal functions
- Tools for integrating C/C++ and Fortran code
- Linear algebra, Fourier transform, and random number capabilities
- Efficient multi-dimensional container for generic data
- Defined data types allowing integration with databases
- Foundation for the entire scientific Python ecosystem

## Installation and Setup

### Basic Installation
```bash
# Install NumPy
pip install numpy

# Install specific version
pip install numpy==1.24.0

# Install with conda
conda install numpy

# Install development version
pip install git+https://github.com/numpy/numpy.git
```

### Importing NumPy
```python
import numpy as np

# Check version
print(np.__version__)

# Show configuration
np.show_config()

# Set print options
np.set_printoptions(precision=3, suppress=True)
```

## Array Creation

### From Python Structures
```python
import numpy as np

# From list
arr = np.array([1, 2, 3, 4, 5])
print(arr)

# From nested lists (2D array)
arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
print(arr_2d)

# From tuple
arr_tuple = np.array((1, 2, 3))
print(arr_tuple)

# Specify dtype
arr_float = np.array([1, 2, 3], dtype=np.float32)
print(arr_float)

# From range
arr_range = np.array(range(10))
print(arr_range)
```

### Intrinsic NumPy Array Creation
```python
# Zeros
zeros_arr = np.zeros((3, 4))
print(zeros_arr)

# Ones
ones_arr = np.ones((2, 3), dtype=np.int32)
print(ones_arr)

# Empty (uninitialized)
empty_arr = np.empty((2, 2))
print(empty_arr)

# Full
full_arr = np.full((3, 3), 7)
print(full_arr)

# Identity matrix
identity = np.identity(4)
print(identity)

# Eye matrix
eye = np.eye(3, k=1)  # k=1 for upper diagonal
print(eye)

# Diagonal
diag = np.diag([1, 2, 3, 4])
print(diag)
```

### Numerical Ranges
```python
# Arange
arr = np.arange(0, 10, 2)  # Start, stop, step
print(arr)

# Linspace
arr = np.linspace(0, 1, 5)  # Start, stop, num points
print(arr)

# Logspace
arr = np.logspace(0, 2, 5)  # 10^0 to 10^2, 5 points
print(arr)

# Geomspace
arr = np.geomspace(1, 1000, 4)  # Geometric progression
print(arr)
```

### Random Arrays
```python
from numpy.random import default_rng

# Create random number generator
rng = default_rng(42)  # Seed for reproducibility

# Random floats [0, 1)
random_arr = rng.random((3, 3))
print(random_arr)

# Random integers
random_int = rng.integers(0, 10, size=(3, 3))
print(random_int)

# Normal distribution
normal_arr = rng.normal(0, 1, size=(3, 3))
print(normal_arr)

# Choice from array
choices = rng.choice([1, 2, 3, 4, 5], size=10, replace=True)
print(choices)
```

### Array Creation from Functions
```python
# From function
def func(i, j):
    return i + j

arr = np.fromfunction(func, (3, 3))
print(arr)

# From iterator
arr = np.fromiter(range(5), dtype=int)
print(arr)

# Using indices
indices = np.indices((3, 3))
print(indices)

# Using meshgrid
x = np.linspace(-1, 1, 3)
y = np.linspace(-1, 1, 3)
X, Y = np.meshgrid(x, y)
print(X)
print(Y)
```

## Array Attributes and Methods

### Basic Attributes
```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

# Shape
print(arr.shape)  # (2, 3)

# Number of dimensions
print(arr.ndim)  # 2

# Size (total elements)
print(arr.size)  # 6

# Data type
print(arr.dtype)  # int64

# Item size (bytes)
print(arr.itemsize)  # 8

# Total bytes
print(arr.nbytes)  # 48

# Memory layout
print(arr.flags)
```

### Array Methods
```python
arr = np.array([[3, 1, 2], [6, 4, 5]])

# Reshape
reshaped = arr.reshape(3, 2)
print(reshaped)

# Flatten
flattened = arr.flatten()
print(flattened)

# Ravel (view if possible)
raveled = arr.ravel()
print(raveled)

# Transpose
transposed = arr.T
print(transposed)

# Sort
arr.sort(axis=1)  # In-place sort
print(arr)

# Copy
arr_copy = arr.copy()
print(arr_copy)

# View
arr_view = arr.view()
print(arr_view)
```

## Indexing and Slicing

### Basic Indexing
```python
# 1D array
arr = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
print(arr[0])  # First element
print(arr[-1])  # Last element
print(arr[2:5])  # Slice

# 2D array
arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(arr_2d[0, 0])  # Element at (0, 0)
print(arr_2d[1])  # Second row
print(arr_2d[:, 1])  # Second column
print(arr_2d[0:2, 1:3])  # Subarray
```

### Advanced Indexing
```python
arr = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

# Integer array indexing
indices = [1, 3, 5]
print(arr[indices])  # Elements at indices 1, 3, 5

# Boolean indexing
mask = arr > 5
print(arr[mask])  # Elements greater than 5

# 2D advanced indexing
arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
rows = np.array([0, 2])
cols = np.array([0, 2])
print(arr_2d[rows, cols])  # Elements at (0,0) and (2,2)

# Using ix_ for cross product
rows = np.array([0, 2])
cols = np.array([0, 2])
print(arr_2d[np.ix_(rows, cols)])  # Subarray with rows 0,2 and cols 0,2
```

### Fancy Indexing
```python
# Setting values with indexing
arr = np.zeros(10)
arr[[1, 3, 5, 7]] = 1
print(arr)

# Using where
arr = np.array([1, 2, 3, 4, 5])
indices = np.where(arr > 2)
print(arr[indices])

# Conditional replacement
arr = np.array([1, 2, 3, 4, 5])
arr[arr > 3] = 0
print(arr)

# Multiple conditions
arr = np.array([1, 2, 3, 4, 5])
mask = (arr > 2) & (arr < 5)
print(arr[mask])
```

## Array Operations

### Arithmetic Operations
```python
a = np.array([1, 2, 3, 4])
b = np.array([5, 6, 7, 8])

# Element-wise operations
print(a + b)  # Addition
print(a - b)  # Subtraction
print(a * b)  # Multiplication
print(a / b)  # Division
print(a ** 2)  # Power
print(np.sqrt(a))  # Square root

# Scalar operations
print(a + 10)
print(a * 2)
```

### Comparison Operations
```python
a = np.array([1, 2, 3, 4])
b = np.array([4, 2, 2, 4])

print(a == b)  # Element-wise equality
print(a != b)  # Not equal
print(a > b)  # Greater than
print(a >= b)  # Greater than or equal
print(a < b)  # Less than
print(a <= b)  # Less than or equal

# Array comparisons
print(np.array_equal(a, b))  # Check if arrays are equal
print(np.allclose(a, b, rtol=1e-5))  # Check if arrays are close
```

### Aggregation Operations
```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

# Sum
print(np.sum(arr))  # Total sum
print(np.sum(arr, axis=0))  # Sum along columns
print(np.sum(arr, axis=1))  # Sum along rows

# Mean
print(np.mean(arr))
print(np.mean(arr, axis=0))

# Standard deviation
print(np.std(arr))

# Min/Max
print(np.min(arr))
print(np.max(arr))
print(np.argmin(arr))  # Index of minimum
print(np.argmax(arr))  # Index of maximum

# Cumulative sum
print(np.cumsum(arr))

# Product
print(np.prod(arr))
```

## Broadcasting

Broadcasting is NumPy's ability to perform operations on arrays of different shapes.

### Broadcasting Rules
```python
# Rule 1: Arrays with same shape
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(a + b)

# Rule 2: Scalar to array
a = np.array([1, 2, 3])
b = 2
print(a * b)

# Rule 3: Compatible shapes
a = np.array([[1, 2, 3],
              [4, 5, 6]])  # Shape (2, 3)
b = np.array([10, 20, 30])  # Shape (3,)
print(a + b)  # b is broadcast to (2, 3)

# Using newaxis for broadcasting
a = np.array([1, 2, 3])
b = np.array([4, 5])
# Add new axis to enable broadcasting
result = a[:, np.newaxis] + b
print(result)
```

### Advanced Broadcasting
```python
# Outer product using broadcasting
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
outer = a[:, np.newaxis] * b[np.newaxis, :]
print(outer)

# Distance matrix using broadcasting
points = np.array([[0, 0], [1, 1], [2, 2]])
# Calculate pairwise distances
diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
distances = np.sqrt(np.sum(diff**2, axis=2))
print(distances)

# Using broadcast_to
arr = np.array([1, 2, 3])
broadcasted = np.broadcast_to(arr, (3, 3))
print(broadcasted)
```

## Universal Functions (ufuncs)

Universal functions operate element-wise on arrays, supporting array broadcasting, type casting, and several other standard features.

### Basic ufuncs
```python
# Trigonometric functions
angles = np.array([0, np.pi/4, np.pi/2])
print(np.sin(angles))
print(np.cos(angles))
print(np.tan(angles))

# Exponential and logarithmic
arr = np.array([1, 2, 3])
print(np.exp(arr))
print(np.log(arr))
print(np.log10(arr))

# Rounding
arr = np.array([1.2, 2.5, 3.7])
print(np.round(arr))
print(np.floor(arr))
print(np.ceil(arr))
```

### ufunc Methods
```python
# Reduce
arr = np.array([1, 2, 3, 4])
print(np.add.reduce(arr))  # Sum
print(np.multiply.reduce(arr))  # Product

# Accumulate
print(np.add.accumulate(arr))  # Cumulative sum
print(np.multiply.accumulate(arr))  # Cumulative product

# Outer
a = np.array([1, 2, 3])
b = np.array([4, 5])
print(np.multiply.outer(a, b))  # Outer product

# At (in-place operation)
arr = np.array([0, 0, 0, 0])
indices = [0, 1, 2, 3]
values = [1, 2, 3, 4]
np.add.at(arr, indices, values)
print(arr)
```

### Custom ufuncs
```python
# Using vectorize
def my_func(a, b):
    if a > b:
        return a - b
    else:
        return a + b

vectorized_func = np.vectorize(my_func)
a = np.array([1, 2, 3, 4])
b = np.array([4, 2, 2, 4])
print(vectorized_func(a, b))

# Using frompyfunc
ufunc = np.frompyfunc(my_func, 2, 1)
print(ufunc(a, b))
```

## Mathematical Functions

### Trigonometric Functions
```python
# Basic trigonometric
angles = np.linspace(0, 2*np.pi, 4)
print(np.sin(angles))
print(np.cos(angles))
print(np.tan(angles))

# Inverse trigonometric
values = np.array([-1, 0, 1])
print(np.arcsin(values))
print(np.arccos(values))
print(np.arctan(values))

# Hyperbolic functions
x = np.array([0, 1, 2])
print(np.sinh(x))
print(np.cosh(x))
print(np.tanh(x))

# Degrees and radians conversion
degrees = np.array([0, 45, 90, 180])
radians = np.deg2rad(degrees)
print(radians)
print(np.rad2deg(radians))
```

### Special Functions
```python
# Gamma function
x = np.array([1, 2, 3, 4])
print(np.math.factorial(3))  # For comparison
from scipy import special  # NumPy doesn't have gamma directly
# print(special.gamma(x))

# Error function
# from scipy import special
# print(special.erf(x))

# Bessel functions
# print(special.jn(0, x))  # Bessel function of the first kind

# Sign function
arr = np.array([-2, -1, 0, 1, 2])
print(np.sign(arr))

# Absolute value
print(np.abs(arr))
```

### Complex Numbers
```python
# Creating complex arrays
z = np.array([1+2j, 3+4j, 5+6j])
print(z)

# Real and imaginary parts
print(np.real(z))
print(np.imag(z))

# Conjugate
print(np.conj(z))

# Absolute value (magnitude)
print(np.abs(z))

# Phase angle
print(np.angle(z))

# Complex exponential
print(np.exp(1j * np.pi))
```

## Linear Algebra

### Basic Operations
```python
# Matrix multiplication
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Dot product
print(np.dot(A, B))

# Matrix multiply (@)
print(A @ B)

# Element-wise multiplication
print(A * B)

# Transpose
print(A.T)

# Trace
print(np.trace(A))
```

### Matrix Decomposition
```python
# Eigenvalues and eigenvectors
A = np.array([[1, 2], [3, 4]])
eigenvalues, eigenvectors = np.linalg.eig(A)
print("Eigenvalues:", eigenvalues)
print("Eigenvectors:", eigenvectors)

# Singular Value Decomposition (SVD)
U, S, Vt = np.linalg.svd(A)
print("U:", U)
print("S:", S)
print("Vt:", Vt)

# QR decomposition
Q, R = np.linalg.qr(A)
print("Q:", Q)
print("R:", R)

# Cholesky decomposition (for positive definite matrices)
C = np.array([[4, 2], [2, 3]])
L = np.linalg.cholesky(C)
print("L:", L)
```

### Solving Linear Systems
```python
# Solve Ax = b
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = np.linalg.solve(A, b)
print("Solution:", x)

# Least squares solution
A = np.array([[0, 1], [1, 1], [2, 1], [3, 1]])
b = np.array([-1, 0.2, 0.9, 2.1])
x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
print("Least squares solution:", x)

# Matrix inverse
A = np.array([[1, 2], [3, 4]])
A_inv = np.linalg.inv(A)
print("Inverse:", A_inv)
print("Verification:", A @ A_inv)

# Pseudo-inverse
A = np.array([[1, 2], [3, 4], [5, 6]])
A_pinv = np.linalg.pinv(A)
print("Pseudo-inverse:", A_pinv)
```

### Matrix Properties
```python
A = np.array([[1, 2], [3, 4]])

# Determinant
det = np.linalg.det(A)
print("Determinant:", det)

# Rank
rank = np.linalg.matrix_rank(A)
print("Rank:", rank)

# Norm
norm = np.linalg.norm(A)
print("Frobenius norm:", norm)
print("1-norm:", np.linalg.norm(A, 1))
print("Infinity norm:", np.linalg.norm(A, np.inf))

# Condition number
cond = np.linalg.cond(A)
print("Condition number:", cond)
```

## Random Number Generation

### Random Number Generators
```python
from numpy.random import default_rng, Generator, PCG64

# Default random generator
rng = default_rng(seed=42)

# Custom bit generator
bit_generator = PCG64(seed=42)
rng = Generator(bit_generator)

# Legacy random (not recommended for new code)
np.random.seed(42)
```

### Distributions
```python
rng = default_rng(42)

# Uniform distribution
uniform = rng.uniform(low=0, high=1, size=(3, 3))
print("Uniform:", uniform)

# Normal distribution
normal = rng.normal(loc=0, scale=1, size=(3, 3))
print("Normal:", normal)

# Binomial distribution
binomial = rng.binomial(n=10, p=0.5, size=10)
print("Binomial:", binomial)

# Poisson distribution
poisson = rng.poisson(lam=3, size=10)
print("Poisson:", poisson)

# Exponential distribution
exponential = rng.exponential(scale=1, size=10)
print("Exponential:", exponential)

# Beta distribution
beta = rng.beta(a=2, b=5, size=10)
print("Beta:", beta)

# Gamma distribution
gamma = rng.gamma(shape=2, scale=1, size=10)
print("Gamma:", gamma)
```

### Random Sampling
```python
rng = default_rng(42)

# Random choice
arr = np.array([1, 2, 3, 4, 5])
choice = rng.choice(arr, size=3, replace=False)
print("Choice without replacement:", choice)

# Weighted choice
weights = [0.1, 0.1, 0.1, 0.1, 0.6]
weighted_choice = rng.choice(arr, size=10, p=weights)
print("Weighted choice:", weighted_choice)

# Shuffle
arr = np.arange(10)
rng.shuffle(arr)
print("Shuffled:", arr)

# Permutation
perm = rng.permutation(10)
print("Permutation:", perm)

# Random sample from range
sample = rng.integers(0, 100, size=10)
print("Random integers:", sample)
```

## Array Manipulation

### Reshaping Arrays
```python
# Reshape
arr = np.arange(12)
reshaped = arr.reshape(3, 4)
print("Reshaped:\n", reshaped)

# Resize (modifies size)
arr_copy = arr.copy()
resized = np.resize(arr_copy, (2, 8))
print("Resized:\n", resized)

# Flatten and ravel
arr_2d = np.array([[1, 2], [3, 4]])
flattened = arr_2d.flatten()  # Copy
raveled = arr_2d.ravel()  # View when possible
print("Flattened:", flattened)
print("Raveled:", raveled)

# Adding dimensions
arr = np.array([1, 2, 3])
expanded = arr[np.newaxis, :]  # Add row dimension
print("Expanded shape:", expanded.shape)
expanded = arr[:, np.newaxis]  # Add column dimension
print("Expanded shape:", expanded.shape)
```

### Joining Arrays
```python
# Concatenate
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

concat_axis0 = np.concatenate([a, b], axis=0)
print("Concatenate axis 0:\n", concat_axis0)

concat_axis1 = np.concatenate([a, b], axis=1)
print("Concatenate axis 1:\n", concat_axis1)

# Stack
stacked = np.stack([a, b])
print("Stacked shape:", stacked.shape)

# Vertical stack
vstacked = np.vstack([a, b])
print("Vstacked:\n", vstacked)

# Horizontal stack
hstacked = np.hstack([a, b])
print("Hstacked:\n", hstacked)

# Depth stack
dstacked = np.dstack([a, b])
print("Dstacked shape:", dstacked.shape)
```

### Splitting Arrays
```python
arr = np.arange(16).reshape(4, 4)

# Split
splits = np.split(arr, 2, axis=0)
print("Split into 2 along axis 0:")
for s in splits:
    print(s)

# Array split (unequal divisions)
splits = np.array_split(arr, 3, axis=0)
print("Array split into 3:")
for s in splits:
    print(s)

# Vertical and horizontal split
vsplit = np.vsplit(arr, 2)
hsplit = np.hsplit(arr, 2)
print("Vsplit:", len(vsplit))
print("Hsplit:", len(hsplit))
```

### Other Manipulations
```python
# Repeat
arr = np.array([1, 2, 3])
repeated = np.repeat(arr, 3)
print("Repeated:", repeated)

# Tile
tiled = np.tile(arr, (2, 3))
print("Tiled:\n", tiled)

# Roll
rolled = np.roll(arr, 1)
print("Rolled:", rolled)

# Flip
arr_2d = np.array([[1, 2], [3, 4]])
flipped_ud = np.flipud(arr_2d)  # Flip up-down
flipped_lr = np.fliplr(arr_2d)  # Flip left-right
print("Flipped up-down:\n", flipped_ud)
print("Flipped left-right:\n", flipped_lr)

# Rotate
rotated = np.rot90(arr_2d)
print("Rotated 90 degrees:\n", rotated)
```

## Input/Output

### Text Files
```python
# Save to text file
arr = np.array([[1, 2, 3], [4, 5, 6]])
np.savetxt('array.txt', arr, delimiter=',', fmt='%d')

# Load from text file
loaded = np.loadtxt('array.txt', delimiter=',')
print("Loaded from text:", loaded)

# Save with headers
np.savetxt('array_with_header.txt', arr, 
           delimiter=',', 
           header='Column1,Column2,Column3',
           comments='#')

# Save multiple arrays
np.savez('arrays.npz', arr1=arr, arr2=arr*2)
loaded_npz = np.load('arrays.npz')
print("Array 1:", loaded_npz['arr1'])
print("Array 2:", loaded_npz['arr2'])
```

### Binary Files
```python
# Save single array (binary)
arr = np.array([[1, 2, 3], [4, 5, 6]])
np.save('array.npy', arr)

# Load binary
loaded = np.load('array.npy')
print("Loaded from binary:", loaded)

# Save compressed
np.savez_compressed('arrays_compressed.npz', arr1=arr, arr2=arr*2)
loaded_compressed = np.load('arrays_compressed.npz')
print("Compressed array 1:", loaded_compressed['arr1'])

# Memory mapping
# Create memory-mapped array
mmap_arr = np.memmap('mmap.dat', dtype='float32', mode='w+', shape=(100, 100))
mmap_arr[:] = np.random.random((100, 100))
del mmap_arr  # Flush to disk

# Read memory-mapped array
mmap_read = np.memmap('mmap.dat', dtype='float32', mode='r', shape=(100, 100))
print("Memory-mapped shape:", mmap_read.shape)
```

### Structured Data
```python
# Using genfromtxt for CSV with mixed types
from io import StringIO

data = StringIO("""
Name,Age,Score
Alice,25,85.5
Bob,30,92.0
Charlie,35,78.5
""")

arr = np.genfromtxt(data, delimiter=',', names=True, dtype=None, encoding='utf-8')
print("Structured data:", arr)
print("Names:", arr['Name'])
print("Ages:", arr['Age'])
```

## Data Types

### Basic Data Types
```python
# Integer types
int8_arr = np.array([1, 2, 3], dtype=np.int8)
int16_arr = np.array([1, 2, 3], dtype=np.int16)
int32_arr = np.array([1, 2, 3], dtype=np.int32)
int64_arr = np.array([1, 2, 3], dtype=np.int64)

# Unsigned integer types
uint8_arr = np.array([1, 2, 3], dtype=np.uint8)
uint16_arr = np.array([1, 2, 3], dtype=np.uint16)

# Float types
float16_arr = np.array([1.0, 2.0, 3.0], dtype=np.float16)
float32_arr = np.array([1.0, 2.0, 3.0], dtype=np.float32)
float64_arr = np.array([1.0, 2.0, 3.0], dtype=np.float64)

# Complex types
complex64_arr = np.array([1+2j, 3+4j], dtype=np.complex64)
complex128_arr = np.array([1+2j, 3+4j], dtype=np.complex128)

# Boolean type
bool_arr = np.array([True, False, True], dtype=np.bool_)

# String type
str_arr = np.array(['hello', 'world'], dtype='U10')  # Unicode, max 10 chars
bytes_arr = np.array([b'hello', b'world'], dtype='S10')  # Bytes, max 10 chars
```

### Type Conversion
```python
# Astype
arr = np.array([1, 2, 3])
float_arr = arr.astype(np.float32)
print("Converted to float32:", float_arr)

# Automatic casting
arr1 = np.array([1, 2, 3], dtype=np.int32)
arr2 = np.array([1.5, 2.5, 3.5], dtype=np.float32)
result = arr1 + arr2  # Result is float32
print("Result dtype:", result.dtype)

# View casting (reinterpret bytes)
arr = np.array([1, 2, 3, 4], dtype=np.int32)
view = arr.view(np.int16)
print("View as int16:", view)

# Safe casting check
can_cast = np.can_cast(np.int32, np.int16, casting='safe')
print("Can safely cast int32 to int16:", can_cast)
```

### Custom Data Types
```python
# Structured dtype
dt = np.dtype([('name', 'U10'), ('age', 'i4'), ('weight', 'f4')])
arr = np.array([('Alice', 25, 55.0), ('Bob', 30, 70.0)], dtype=dt)
print("Structured array:", arr)
print("Names:", arr['name'])
print("Ages:", arr['age'])

# Nested dtype
dt_nested = np.dtype([
    ('id', 'i4'),
    ('data', [('x', 'f4'), ('y', 'f4')])
])
arr_nested = np.zeros(3, dtype=dt_nested)
arr_nested['id'] = [1, 2, 3]
arr_nested['data']['x'] = [1.0, 2.0, 3.0]
arr_nested['data']['y'] = [4.0, 5.0, 6.0]
print("Nested structure:", arr_nested)
```

## Structured Arrays

### Creating Structured Arrays
```python
# Define structured dtype
dtype = np.dtype([
    ('name', 'U20'),
    ('age', 'i4'),
    ('salary', 'f8'),
    ('department', 'U10')
])

# Create structured array
employees = np.array([
    ('Alice', 25, 50000.0, 'IT'),
    ('Bob', 30, 60000.0, 'HR'),
    ('Charlie', 35, 70000.0, 'Finance'),
    ('David', 28, 55000.0, 'IT')
], dtype=dtype)

print("Employees:", employees)
print("Names:", employees['name'])
print("Average salary:", employees['salary'].mean())
```

### Working with Structured Arrays
```python
# Filtering
it_employees = employees[employees['department'] == 'IT']
print("IT employees:", it_employees)

# Sorting
sorted_by_age = np.sort(employees, order='age')
print("Sorted by age:", sorted_by_age)

# Multiple sort keys
sorted_multi = np.sort(employees, order=['department', 'salary'])
print("Sorted by department then salary:", sorted_multi)

# Adding fields
from numpy.lib import recfunctions as rfn

# Add a bonus field
with_bonus = rfn.append_fields(employees, 'bonus', 
                               employees['salary'] * 0.1, 
                               usemask=False)
print("With bonus:", with_bonus)
```

### Record Arrays
```python
# Convert to record array for attribute access
rec_arr = np.rec.array(employees)
print("First employee name:", rec_arr[0].name)
print("All ages:", rec_arr.age)

# Create record array directly
rec_arr2 = np.rec.fromarrays(
    [['Alice', 'Bob'], [25, 30], [50000, 60000]],
    names='name,age,salary'
)
print("Record array 2:", rec_arr2)
```

## Masked Arrays

### Creating Masked Arrays
```python
import numpy.ma as ma

# Create masked array
data = np.array([1, 2, 3, -999, 5, 6])
mask = data == -999
masked_arr = ma.masked_array(data, mask=mask)
print("Masked array:", masked_arr)

# Using masked_where
arr = np.array([1, 2, 3, 4, 5])
masked = ma.masked_where(arr > 3, arr)
print("Masked where > 3:", masked)

# Using masked_invalid (masks NaN and inf)
arr_with_nan = np.array([1, 2, np.nan, 4, np.inf])
masked_invalid = ma.masked_invalid(arr_with_nan)
print("Masked invalid:", masked_invalid)
```

### Operations with Masked Arrays
```python
# Arithmetic operations ignore masked values
a = ma.array([1, 2, 3, 4, 5], mask=[0, 0, 1, 0, 0])
b = ma.array([10, 20, 30, 40, 50], mask=[0, 1, 0, 0, 0])

print("Sum:", a + b)
print("Product:", a * b)

# Statistical operations
print("Mean:", ma.mean(a))
print("Std:", ma.std(a))
print("Compressed (unmasked):", a.compressed())

# Fill masked values
filled = a.filled(fill_value=0)
print("Filled with 0:", filled)
```

## FFT and Signal Processing

### Fast Fourier Transform
```python
# 1D FFT
signal = np.sin(2 * np.pi * 5 * np.linspace(0, 1, 100))
fft = np.fft.fft(signal)
freq = np.fft.fftfreq(len(signal))
print("FFT shape:", fft.shape)
print("Frequencies shape:", freq.shape)

# Inverse FFT
ifft = np.fft.ifft(fft)
print("Reconstructed signal matches:", np.allclose(signal, ifft.real))

# 2D FFT (for images)
image = np.random.random((32, 32))
fft2d = np.fft.fft2(image)
ifft2d = np.fft.ifft2(fft2d)
print("2D FFT shape:", fft2d.shape)

# Real FFT (for real-valued inputs)
rfft = np.fft.rfft(signal)
print("Real FFT shape:", rfft.shape)
```

### Signal Processing
```python
# Convolution
signal = np.array([1, 2, 3, 4, 5])
kernel = np.array([0.25, 0.5, 0.25])
convolved = np.convolve(signal, kernel, mode='same')
print("Convolved:", convolved)

# Correlation
corr = np.correlate(signal, kernel, mode='same')
print("Correlation:", corr)

# Window functions
from numpy import hamming, hanning, blackman, bartlett

n = 51
hamming_window = hamming(n)
hanning_window = hanning(n)
blackman_window = blackman(n)
bartlett_window = bartlett(n)

print("Window shapes:", hamming_window.shape)
```

## Polynomials

### Polynomial Operations
```python
# Create polynomial from coefficients
# p(x) = 2x^3 + 3x^2 + 4x + 5
coeffs = [2, 3, 4, 5]  # Highest degree first
p = np.poly1d(coeffs)
print("Polynomial:", p)

# Evaluate polynomial
x = np.array([1, 2, 3])
values = p(x)
print("Values at x:", values)

# Polynomial arithmetic
p1 = np.poly1d([1, 2, 3])
p2 = np.poly1d([1, 1])
print("Addition:", p1 + p2)
print("Multiplication:", p1 * p2)

# Derivative and integral
p_deriv = np.polyder(p)
p_integ = np.polyint(p)
print("Derivative:", p_deriv)
print("Integral:", p_integ)
```

### Polynomial Fitting
```python
# Fit polynomial to data
x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 1, 4, 9, 16])  # y = x^2

# Fit 2nd degree polynomial
coeffs = np.polyfit(x, y, deg=2)
p_fit = np.poly1d(coeffs)
print("Fitted polynomial:", p_fit)

# Evaluate fit
y_fit = p_fit(x)
print("Fitted values:", y_fit)
print("Original values:", y)

# Polynomial roots
p = np.poly1d([1, -3, 2])  # x^2 - 3x + 2 = 0
roots = np.roots(p)
print("Roots:", roots)  # Should be 1 and 2
```

## Performance Optimization

### Vectorization
```python
# Avoid loops - use vectorization
# Bad: Using loops
def slow_operation(arr):
    result = np.empty_like(arr)
    for i in range(len(arr)):
        result[i] = arr[i] ** 2 + 2 * arr[i] + 1
    return result

# Good: Vectorized operation
def fast_operation(arr):
    return arr ** 2 + 2 * arr + 1

# Performance comparison
arr = np.random.random(1000000)
# %timeit slow_operation(arr)  # Slow
# %timeit fast_operation(arr)  # Fast
```

### Memory Views and Copies
```python
# Views vs copies
arr = np.arange(10)

# View (no copy)
view = arr[::2]
view[0] = 100
print("Original modified:", arr[0])  # Original is modified

# Copy
copy = arr[::2].copy()
copy[0] = 200
print("Original unchanged:", arr[0])  # Original unchanged

# Check if view or copy
print("Is view:", view.base is arr)
print("Is copy:", copy.base is arr)

# Contiguous arrays
arr = np.arange(16).reshape(4, 4)
print("C-contiguous:", arr.flags['C_CONTIGUOUS'])
print("F-contiguous:", arr.flags['F_CONTIGUOUS'])

# Make contiguous
c_cont = np.ascontiguousarray(arr)
f_cont = np.asfortranarray(arr)
```

### Using Numba for JIT Compilation
```python
# Requires: pip install numba
try:
    from numba import jit
    
    @jit
    def fast_function(arr):
        result = np.empty_like(arr)
        for i in range(len(arr)):
            result[i] = arr[i] ** 2 + 2 * arr[i] + 1
        return result
    
    # Now the loop is compiled and fast
    arr = np.random.random(1000000)
    # %timeit fast_function(arr)
except ImportError:
    print("Numba not installed")
```

### Memory Efficiency
```python
# Use appropriate dtypes
# Instead of default float64
arr_float64 = np.array([1.0, 2.0, 3.0])  # 8 bytes per element

# Use float32 if precision allows
arr_float32 = np.array([1.0, 2.0, 3.0], dtype=np.float32)  # 4 bytes per element

print("Float64 bytes:", arr_float64.nbytes)
print("Float32 bytes:", arr_float32.nbytes)

# In-place operations
arr = np.array([1, 2, 3, 4, 5], dtype=np.float32)

# Not in-place (creates new array)
result = arr * 2

# In-place (modifies existing array)
arr *= 2
print("In-place result:", arr)

# Use out parameter
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])
result = np.empty_like(arr1)
np.add(arr1, arr2, out=result)
print("Result with out:", result)
```

## Best Practices

### General Guidelines
```python
# 1. Use vectorization instead of loops
# Bad
result = []
for x in arr:
    result.append(x * 2)

# Good
result = arr * 2

# 2. Preallocate arrays
# Bad
arr = np.array([])
for i in range(1000):
    arr = np.append(arr, i)

# Good
arr = np.empty(1000)
for i in range(1000):
    arr[i] = i

# 3. Use appropriate data types
# For integers in range 0-255
arr = np.array([1, 2, 3], dtype=np.uint8)

# 4. Avoid unnecessary copies
# Use views when possible
view = arr[::2]  # View
copy = arr[::2].copy()  # Explicit copy when needed

# 5. Use broadcasting
# Instead of
result = np.zeros((3, 4))
for i in range(3):
    result[i] = arr

# Use
result = np.tile(arr, (3, 1))
# Or broadcasting
result = np.ones((3, 1)) * arr
```

### Error Handling
```python
# Check for valid input
def safe_divide(a, b):
    """Safely divide arrays handling division by zero"""
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.true_divide(a, b)
        result[~np.isfinite(result)] = 0  # Set inf/nan to 0
    return result

# Check array properties
def process_array(arr):
    """Process array with validation"""
    arr = np.asarray(arr)  # Ensure it's an array
    
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D array, got {arr.ndim}D")
    
    if arr.dtype != np.float64:
        arr = arr.astype(np.float64)
    
    return arr

# Handle NaN values
arr_with_nan = np.array([1, 2, np.nan, 4, 5])
# Remove NaN
clean_arr = arr_with_nan[~np.isnan(arr_with_nan)]
# Or replace NaN
arr_with_nan[np.isnan(arr_with_nan)] = 0
```

### Debugging Tips
```python
# Print array information
def debug_array(arr, name="Array"):
    """Print detailed array information for debugging"""
    print(f"\n{name} Debug Info:")
    print(f"  Shape: {arr.shape}")
    print(f"  Dtype: {arr.dtype}")
    print(f"  Size: {arr.size}")
    print(f"  Bytes: {arr.nbytes}")
    print(f"  Min: {np.min(arr)}")
    print(f"  Max: {np.max(arr)}")
    print(f"  Mean: {np.mean(arr)}")
    print(f"  Std: {np.std(arr)}")
    print(f"  Has NaN: {np.any(np.isnan(arr))}")
    print(f"  Has Inf: {np.any(np.isinf(arr))}")

# Set print options for better display
np.set_printoptions(
    precision=3,      # Decimal places
    suppress=True,    # Suppress scientific notation
    threshold=10,     # Max elements to print
    linewidth=75      # Characters per line
)

# Check memory usage
arr = np.random.random((1000, 1000))
print(f"Memory usage: {arr.nbytes / 1024 / 1024:.2f} MB")
```

## Conclusion

NumPy is the foundation of scientific computing in Python, providing:
- Efficient multi-dimensional arrays and operations
- Broadcasting for flexible array operations
- Comprehensive mathematical functions
- Linear algebra and FFT capabilities
- Random number generation
- Tools for integrating with C/C++ and Fortran

Key takeaways:
- Use vectorization for performance
- Understand broadcasting rules
- Choose appropriate data types
- Be aware of views vs copies
- Leverage NumPy's built-in functions
- Profile and optimize critical code sections

NumPy's efficiency and comprehensive functionality make it essential for data science, machine learning, scientific computing, and engineering applications in Python.