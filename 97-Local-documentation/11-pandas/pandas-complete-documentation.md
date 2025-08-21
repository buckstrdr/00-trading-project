# Pandas Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Data Structures](#data-structures)
4. [Data Import/Export](#data-importexport)
5. [Data Selection and Indexing](#data-selection-and-indexing)
6. [Data Manipulation](#data-manipulation)
7. [GroupBy Operations](#groupby-operations)
8. [Merging and Joining](#merging-and-joining)
9. [Reshaping and Pivoting](#reshaping-and-pivoting)
10. [Time Series Analysis](#time-series-analysis)
11. [Visualization](#visualization)
12. [Statistical Functions](#statistical-functions)
13. [Window Functions](#window-functions)
14. [String Operations](#string-operations)
15. [Categorical Data](#categorical-data)
16. [MultiIndex Operations](#multiindex-operations)
17. [Performance Optimization](#performance-optimization)
18. [Best Practices](#best-practices)
19. [Common Patterns](#common-patterns)
20. [Troubleshooting](#troubleshooting)

## Introduction

Pandas is a powerful, flexible, and easy-to-use open-source data analysis and manipulation library for Python. It provides data structures and operations for manipulating numerical tables and time series data.

### Key Features
- Fast and efficient DataFrame object for data manipulation
- Tools for reading and writing data between in-memory data structures and various formats
- Intelligent data alignment and integrated handling of missing data
- Flexible reshaping and pivoting of datasets
- Intelligent label-based slicing, fancy indexing, and subsetting of large datasets
- Columns can be inserted and deleted from data structures
- Aggregating or transforming data with a powerful group by engine
- High performance merging and joining of datasets
- Hierarchical axis indexing
- Time series functionality

## Installation and Setup

### Basic Installation
```bash
# Install pandas
pip install pandas

# Install with optional dependencies
pip install pandas[all]

# Install specific version
pip install pandas==2.0.0

# Install from conda
conda install pandas
```

### Importing Pandas
```python
import pandas as pd
import numpy as np

# Check version
print(pd.__version__)

# Configure display options
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1000)
pd.set_option('display.precision', 3)
```

## Data Structures

### Series
A one-dimensional labeled array capable of holding any data type.

```python
# Creating Series
s = pd.Series([1, 3, 5, np.nan, 6, 8])
print(s)

# Series with custom index
s = pd.Series([1, 3, 5, 6, 8], index=['a', 'b', 'c', 'd', 'e'])
print(s)

# Series from dictionary
d = {'a': 1, 'b': 2, 'c': 3}
s = pd.Series(d)
print(s)

# Series with datetime index
dates = pd.date_range('20230101', periods=6)
s = pd.Series(np.random.randn(6), index=dates)
print(s)

# Accessing elements
print(s[0])  # By position
print(s['a'])  # By label
print(s[1:3])  # Slicing

# Series operations
s + s  # Element-wise addition
s * 2  # Scalar multiplication
np.exp(s)  # Apply NumPy functions
```

### DataFrame
A two-dimensional labeled data structure with columns of potentially different types.

```python
# Creating DataFrames
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': pd.date_range('20230101', periods=4),
    'C': pd.Series(1, index=list(range(4)), dtype='float32'),
    'D': np.array([3] * 4, dtype='int32'),
    'E': pd.Categorical(['test', 'train', 'test', 'train']),
    'F': 'foo'
})
print(df)

# DataFrame from NumPy array
df = pd.DataFrame(np.random.randn(6, 4), 
                  index=dates, 
                  columns=list('ABCD'))

# DataFrame from dictionary of Series
d = {
    'one': pd.Series([1.0, 2.0, 3.0], index=['a', 'b', 'c']),
    'two': pd.Series([1.0, 2.0, 3.0, 4.0], index=['a', 'b', 'c', 'd'])
}
df = pd.DataFrame(d)

# Basic operations
df.head()  # First 5 rows
df.tail(3)  # Last 3 rows
df.info()  # Concise summary
df.describe()  # Statistical summary
df.dtypes  # Data types
df.shape  # Dimensions
df.columns  # Column names
df.index  # Index
```

## Data Import/Export

### CSV Files
```python
# Reading CSV
df = pd.read_csv('file.csv')
df = pd.read_csv('file.csv', sep=';', encoding='utf-8')
df = pd.read_csv('file.csv', index_col=0, parse_dates=True)
df = pd.read_csv('file.csv', header=0, names=['col1', 'col2'])
df = pd.read_csv('file.csv', skiprows=2, nrows=1000)

# Writing CSV
df.to_csv('output.csv')
df.to_csv('output.csv', index=False)
df.to_csv('output.csv', sep='\t', encoding='utf-8')
```

### Excel Files
```python
# Reading Excel
df = pd.read_excel('file.xlsx')
df = pd.read_excel('file.xlsx', sheet_name='Sheet1')
df = pd.read_excel('file.xlsx', sheet_name=0)

# Reading multiple sheets
xlsx = pd.ExcelFile('file.xlsx')
df1 = pd.read_excel(xlsx, 'Sheet1')
df2 = pd.read_excel(xlsx, 'Sheet2')

# Writing Excel
df.to_excel('output.xlsx')
df.to_excel('output.xlsx', sheet_name='Sheet1', index=False)

# Writing multiple sheets
with pd.ExcelWriter('output.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1')
    df2.to_excel(writer, sheet_name='Sheet2')
```

### JSON Files
```python
# Reading JSON
df = pd.read_json('file.json')
df = pd.read_json('file.json', orient='records')

# Writing JSON
df.to_json('output.json')
df.to_json('output.json', orient='records', lines=True)
```

### SQL Databases
```python
import sqlite3

# Reading from SQL
conn = sqlite3.connect('database.db')
df = pd.read_sql_query('SELECT * FROM table', conn)
df = pd.read_sql_table('table_name', conn)

# Writing to SQL
df.to_sql('table_name', conn, if_exists='replace', index=False)
```

## Data Selection and Indexing

### Basic Selection
```python
# Column selection
df['A']  # Single column (returns Series)
df[['A', 'B']]  # Multiple columns (returns DataFrame)

# Row selection by label
df.loc['2023-01-01']  # Single row
df.loc['2023-01-01':'2023-01-03']  # Range of rows

# Row selection by position
df.iloc[0]  # First row
df.iloc[0:3]  # First 3 rows
df.iloc[-1]  # Last row

# Combined selection
df.loc['2023-01-01', 'A']  # Specific value
df.iloc[0, 0]  # By position
df.at['2023-01-01', 'A']  # Fast scalar access
df.iat[0, 0]  # Fast scalar access by position
```

### Boolean Indexing
```python
# Filtering rows
df[df['A'] > 0]  # Rows where column A > 0
df[df['B'].isin(['value1', 'value2'])]  # Rows where B is in list
df[(df['A'] > 0) & (df['B'] < 5)]  # Multiple conditions
df[df['C'].str.contains('pattern')]  # String pattern matching

# Using query method
df.query('A > 0 and B < 5')
df.query('C in ["value1", "value2"]')
```

### Advanced Indexing
```python
# Setting values
df.loc[df['A'] > 0, 'B'] = 0  # Set B to 0 where A > 0
df.iloc[0:3, 1] = 1  # Set specific positions

# Index alignment
s1 = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
s2 = pd.Series([4, 5, 6], index=['b', 'c', 'd'])
s1 + s2  # Aligned by index

# MultiIndex selection
df.loc[('level1', 'level2')]  # For MultiIndex DataFrames
```

## Data Manipulation

### Adding and Removing Columns
```python
# Adding columns
df['G'] = df['A'] + df['B']  # From existing columns
df['H'] = pd.Series(np.random.randn(len(df)))  # From Series
df['I'] = 5  # Constant value

# Using assign method
df = df.assign(J=lambda x: x['A'] * 2)

# Removing columns
df = df.drop('G', axis=1)  # Drop single column
df = df.drop(['H', 'I'], axis=1)  # Drop multiple columns
del df['J']  # In-place deletion
df.pop('K')  # Remove and return column
```

### Sorting
```python
# Sort by values
df.sort_values('A')  # Sort by single column
df.sort_values(['A', 'B'], ascending=[True, False])  # Multiple columns
df.sort_values('A', inplace=True)  # In-place sorting

# Sort by index
df.sort_index()  # Sort by index
df.sort_index(axis=1)  # Sort columns alphabetically
```

### Handling Missing Data
```python
# Detecting missing data
df.isna()  # Boolean mask of missing values
df.notna()  # Boolean mask of non-missing values
df.isna().sum()  # Count missing values per column

# Dropping missing data
df.dropna()  # Drop rows with any missing values
df.dropna(axis=1)  # Drop columns with any missing values
df.dropna(how='all')  # Drop rows where all values are missing
df.dropna(thresh=2)  # Keep rows with at least 2 non-NA values

# Filling missing data
df.fillna(0)  # Fill with constant
df.fillna(method='ffill')  # Forward fill
df.fillna(method='bfill')  # Backward fill
df.fillna(df.mean())  # Fill with mean
df.interpolate()  # Interpolate missing values
```

### Data Transformation
```python
# Apply functions
df.apply(np.sum)  # Apply to each column
df.apply(np.sum, axis=1)  # Apply to each row
df.apply(lambda x: x.max() - x.min())  # Custom function

# Applymap (element-wise)
df.applymap(lambda x: len(str(x)))

# Transform
df.transform(np.sqrt)  # Transform all values
df['A'].transform([np.sqrt, np.exp])  # Multiple transformations

# Replace values
df.replace(0, np.nan)  # Replace specific value
df.replace([0, 1], [np.nan, 100])  # Multiple replacements
df.replace({'A': 0, 'B': 1}, np.nan)  # Column-specific
```

## GroupBy Operations

### Basic GroupBy
```python
# Simple groupby
grouped = df.groupby('A')
grouped.sum()  # Sum by group
grouped.mean()  # Mean by group
grouped.size()  # Group sizes

# Multiple grouping columns
grouped = df.groupby(['A', 'B'])
grouped.sum()

# Custom aggregation
grouped.agg({'C': 'sum', 'D': 'mean'})
grouped.agg(['sum', 'mean', 'std'])

# Named aggregations
grouped.agg(
    total=('C', 'sum'),
    average=('D', 'mean')
)
```

### Advanced GroupBy Operations
```python
# Transform within groups
df['normalized'] = df.groupby('category')['value'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Filter groups
df.groupby('category').filter(lambda x: len(x) > 3)

# Apply custom function
def custom_func(group):
    return pd.Series({
        'mean': group.mean(),
        'std': group.std(),
        'count': len(group)
    })

df.groupby('category')['value'].apply(custom_func)

# Groupby with MultiIndex
df.groupby(level=0).sum()  # Group by first level
df.groupby(level=['level1', 'level2']).mean()

# Window operations within groups
df.groupby('category')['value'].rolling(window=3).mean()
df.groupby('category')['value'].expanding().sum()
```

### GroupBy Examples
```python
# Compute multiple statistics
df.groupby('category').agg({
    'price': ['mean', 'min', 'max'],
    'quantity': 'sum',
    'id': 'count'
})

# Top N per group
df.groupby('category').apply(lambda x: x.nlargest(3, 'value'))

# Percentage of total per group
df['pct'] = df.groupby('category')['value'].transform(
    lambda x: x / x.sum() * 100
)

# Cumulative operations within groups
df['cumsum'] = df.groupby('category')['value'].cumsum()
df['cummax'] = df.groupby('category')['value'].cummax()
```

## Merging and Joining

### Concatenation
```python
# Concatenate DataFrames
df1 = pd.DataFrame({'A': ['A0', 'A1'], 'B': ['B0', 'B1']})
df2 = pd.DataFrame({'A': ['A2', 'A3'], 'B': ['B2', 'B3']})
df3 = pd.DataFrame({'A': ['A4', 'A5'], 'B': ['B4', 'B5']})

# Vertical concatenation
result = pd.concat([df1, df2, df3])
result = pd.concat([df1, df2, df3], ignore_index=True)

# Horizontal concatenation
result = pd.concat([df1, df2], axis=1)

# With keys (hierarchical index)
result = pd.concat([df1, df2], keys=['x', 'y'])

# Concatenate Series
s1 = pd.Series(['X0', 'X1'], name='X')
result = pd.concat([df1, s1], axis=1)
```

### Merge Operations
```python
# Basic merge (SQL-style join)
left = pd.DataFrame({'key': ['A', 'B', 'C'], 'value': [1, 2, 3]})
right = pd.DataFrame({'key': ['A', 'B', 'D'], 'value': [4, 5, 6]})

# Inner join (default)
pd.merge(left, right, on='key')

# Left join
pd.merge(left, right, on='key', how='left')

# Right join
pd.merge(left, right, on='key', how='right')

# Outer join
pd.merge(left, right, on='key', how='outer')

# Merge on multiple columns
pd.merge(left, right, on=['key1', 'key2'])

# Merge with different column names
pd.merge(left, right, left_on='lkey', right_on='rkey')

# Merge on index
pd.merge(left, right, left_index=True, right_index=True)

# Merge with suffixes for overlapping columns
pd.merge(left, right, on='key', suffixes=('_left', '_right'))
```

### Join Operations
```python
# DataFrame.join (always joins on index)
df1.join(df2)
df1.join(df2, how='outer')
df1.join(df2, lsuffix='_left', rsuffix='_right')

# Join on specific column
df1.join(df2, on='key')

# Join multiple DataFrames
df1.join([df2, df3])
```

## Reshaping and Pivoting

### Pivot Tables
```python
# Basic pivot table
df.pivot_table(values='value', index='row', columns='col')

# With aggregation function
df.pivot_table(values='value', index='row', columns='col', aggfunc='mean')

# Multiple aggregations
df.pivot_table(values='value', index='row', columns='col', 
               aggfunc=['mean', 'sum', 'count'])

# Multiple values
df.pivot_table(values=['val1', 'val2'], index='row', columns='col')

# With margins (totals)
df.pivot_table(values='value', index='row', columns='col', margins=True)

# Fill missing values
df.pivot_table(values='value', index='row', columns='col', fill_value=0)
```

### Stack and Unstack
```python
# Stack: pivot columns to rows
stacked = df.stack()

# Unstack: pivot rows to columns
unstacked = stacked.unstack()
unstacked = stacked.unstack(level=-1)  # Specify level

# Multiple levels
df.unstack(level=[0, 1])
```

### Melt (Unpivot)
```python
# Basic melt
df_melted = pd.melt(df, id_vars=['id'], value_vars=['A', 'B'])

# With custom names
df_melted = pd.melt(df, id_vars=['id'], value_vars=['A', 'B'],
                    var_name='variable', value_name='value')

# Melt all columns except id_vars
df_melted = pd.melt(df, id_vars=['id'])
```

### Crosstab
```python
# Basic crosstab
pd.crosstab(df['row'], df['col'])

# With values and aggregation
pd.crosstab(df['row'], df['col'], values=df['value'], aggfunc='sum')

# Normalized (percentages)
pd.crosstab(df['row'], df['col'], normalize=True)
pd.crosstab(df['row'], df['col'], normalize='columns')

# With margins
pd.crosstab(df['row'], df['col'], margins=True)
```

### Explode
```python
# Explode list-like columns into separate rows
df = pd.DataFrame({'A': [[1, 2], [3, 4]], 'B': ['x', 'y']})
df.explode('A')
```

## Time Series Analysis

### Date Range Creation
```python
# Create date ranges
dates = pd.date_range('2023-01-01', periods=365)
dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
dates = pd.date_range('2023-01-01', periods=12, freq='M')

# Business days only
dates = pd.bdate_range('2023-01-01', periods=20)

# Custom frequency
dates = pd.date_range('2023-01-01', periods=10, freq='2H30min')
```

### DateTime Indexing
```python
# Create time series
ts = pd.Series(np.random.randn(1000), 
               index=pd.date_range('1/1/2000', periods=1000))

# DateTime indexing
ts['2000']  # Select year 2000
ts['2000-05']  # Select May 2000
ts['2000-05-01':'2000-05-15']  # Date range

# Partial string indexing
df.loc['2000']
df.loc['2000-Q1']  # First quarter
```

### Resampling
```python
# Downsampling (higher to lower frequency)
ts.resample('M').mean()  # Monthly mean
ts.resample('Q').sum()  # Quarterly sum
ts.resample('A').apply(lambda x: x.max() - x.min())  # Annual range

# Upsampling (lower to higher frequency)
ts.resample('12H').ffill()  # Forward fill
ts.resample('12H').interpolate()  # Interpolate

# OHLC resampling
ts.resample('W').ohlc()  # Open, High, Low, Close

# Custom resampling
ts.resample('M', label='right', closed='right').mean()
```

### Time Shifting
```python
# Shift values
ts.shift(1)  # Shift forward by 1 period
ts.shift(-1)  # Shift backward by 1 period
ts.shift(1, freq='D')  # Shift by 1 day

# Percentage change
ts.pct_change()  # Percentage change from previous period
ts.pct_change(periods=12)  # Year-over-year percentage change

# Difference
ts.diff()  # First difference
ts.diff(periods=12)  # Seasonal difference
```

### Rolling Windows
```python
# Rolling statistics
ts.rolling(window=30).mean()  # 30-day moving average
ts.rolling(window=30).std()  # 30-day moving standard deviation
ts.rolling(window=30).apply(lambda x: x.max() - x.min())

# Centered window
ts.rolling(window=30, center=True).mean()

# Exponentially weighted
ts.ewm(span=30).mean()  # Exponential moving average
ts.ewm(alpha=0.1).mean()  # With decay factor
```

## Visualization

### Basic Plotting
```python
import matplotlib.pyplot as plt

# Line plot
df.plot()
df['A'].plot()
df.plot(y=['A', 'B'])

# Specific plot types
df.plot.line()
df.plot.bar()
df.plot.barh()
df.plot.hist()
df.plot.box()
df.plot.kde()
df.plot.area()
df.plot.scatter(x='A', y='B')
df.plot.hexbin(x='A', y='B')
df.plot.pie(y='A')

# Subplots
df.plot(subplots=True, figsize=(12, 8))
df.plot(subplots=True, layout=(2, 2), figsize=(10, 8))
```

### Advanced Plotting
```python
# Customizing plots
df.plot(
    title='My Plot',
    xlabel='X Axis',
    ylabel='Y Axis',
    legend=True,
    grid=True,
    figsize=(10, 6),
    style='.-',
    color=['red', 'blue', 'green'],
    alpha=0.7
)

# Secondary y-axis
ax = df['A'].plot()
df['B'].plot(secondary_y=True, ax=ax)

# Plotting with colormaps
df.plot(colormap='viridis')
df.plot.bar(colormap='coolwarm')

# Scatter matrix
from pandas.plotting import scatter_matrix
scatter_matrix(df, alpha=0.2, figsize=(10, 10), diagonal='kde')

# Parallel coordinates
from pandas.plotting import parallel_coordinates
parallel_coordinates(df, 'category_column')

# Andrews curves
from pandas.plotting import andrews_curves
andrews_curves(df, 'category_column')

# Lag plot
from pandas.plotting import lag_plot
lag_plot(df['A'])

# Autocorrelation plot
from pandas.plotting import autocorrelation_plot
autocorrelation_plot(df['A'])

# Bootstrap plot
from pandas.plotting import bootstrap_plot
bootstrap_plot(df['A'], size=50, samples=500)
```

### Saving Plots
```python
# Save figure
ax = df.plot()
fig = ax.get_figure()
fig.savefig('plot.png')
fig.savefig('plot.pdf', dpi=300, bbox_inches='tight')
```

## Statistical Functions

### Descriptive Statistics
```python
# Basic statistics
df.mean()  # Mean
df.median()  # Median
df.mode()  # Mode
df.std()  # Standard deviation
df.var()  # Variance
df.min()  # Minimum
df.max()  # Maximum
df.sum()  # Sum
df.prod()  # Product
df.count()  # Count non-null values

# Quantiles
df.quantile(0.25)  # 25th percentile
df.quantile([0.25, 0.5, 0.75])  # Multiple quantiles

# Summary statistics
df.describe()  # Statistical summary
df.describe(include='all')  # Include non-numeric columns
df.describe(percentiles=[0.1, 0.5, 0.9])  # Custom percentiles
```

### Correlation and Covariance
```python
# Correlation
df.corr()  # Pearson correlation
df.corr(method='spearman')  # Spearman correlation
df.corr(method='kendall')  # Kendall correlation

# Covariance
df.cov()  # Covariance matrix

# Correlation with specific column
df.corrwith(df['A'])
```

### Other Statistical Functions
```python
# Cumulative statistics
df.cumsum()  # Cumulative sum
df.cumprod()  # Cumulative product
df.cummax()  # Cumulative maximum
df.cummin()  # Cumulative minimum

# Ranking
df.rank()  # Rank values
df.rank(method='dense')  # Dense ranking
df.rank(pct=True)  # Percentile rank

# Unique values
df['A'].unique()  # Unique values
df['A'].nunique()  # Number of unique values
df['A'].value_counts()  # Frequency counts

# Other functions
df.mad()  # Mean absolute deviation
df.skew()  # Skewness
df.kurt()  # Kurtosis
df.sem()  # Standard error of mean
```

## Window Functions

### Rolling Windows
```python
# Basic rolling
df.rolling(window=7).mean()  # 7-period moving average
df.rolling(window=7).sum()  # 7-period rolling sum
df.rolling(window=7).std()  # 7-period rolling standard deviation

# Custom aggregation
df.rolling(window=7).apply(lambda x: x.max() - x.min())

# Min periods
df.rolling(window=7, min_periods=1).mean()

# Centered window
df.rolling(window=7, center=True).mean()

# Window types
df.rolling(window=7, win_type='triang').mean()
```

### Expanding Windows
```python
# Expanding statistics
df.expanding().mean()  # Expanding mean
df.expanding().sum()  # Expanding sum
df.expanding().std()  # Expanding standard deviation
df.expanding(min_periods=3).mean()  # With minimum periods
```

### Exponentially Weighted Windows
```python
# Exponential moving average
df.ewm(span=20).mean()  # With span
df.ewm(alpha=0.1).mean()  # With alpha
df.ewm(halflife=10).mean()  # With half-life

# Other EWM statistics
df.ewm(span=20).std()
df.ewm(span=20).corr()
```

## String Operations

### String Methods
```python
# Basic string operations
df['text'].str.lower()  # Convert to lowercase
df['text'].str.upper()  # Convert to uppercase
df['text'].str.title()  # Title case
df['text'].str.capitalize()  # Capitalize first letter

# String manipulation
df['text'].str.strip()  # Remove leading/trailing whitespace
df['text'].str.lstrip()  # Remove leading whitespace
df['text'].str.rstrip()  # Remove trailing whitespace
df['text'].str.replace('old', 'new')  # Replace substring

# String information
df['text'].str.len()  # String length
df['text'].str.contains('pattern')  # Contains pattern
df['text'].str.startswith('prefix')  # Starts with
df['text'].str.endswith('suffix')  # Ends with

# Pattern matching
df['text'].str.match('pattern')  # Match pattern
df['text'].str.extract('(\\d+)')  # Extract pattern
df['text'].str.extractall('(\\d+)')  # Extract all occurrences
df['text'].str.findall('pattern')  # Find all patterns

# String splitting and joining
df['text'].str.split(' ')  # Split by delimiter
df['text'].str.split(' ', expand=True)  # Split into columns
df['text'].str.join(' ')  # Join list elements
df['text'].str.cat(sep=', ')  # Concatenate strings
```

### Text Processing
```python
# Padding
df['text'].str.pad(10, side='left', fillchar='0')
df['text'].str.center(10, fillchar='*')

# Slicing
df['text'].str[0:5]  # Substring
df['text'].str[-3:]  # Last 3 characters

# Regular expressions
df['text'].str.replace(r'\\d+', 'NUM', regex=True)
df['text'].str.split(r'\\s+', regex=True)

# Case conversion
df['text'].str.swapcase()  # Swap case
df['text'].str.normalize('NFKD')  # Unicode normalization
```

## Categorical Data

### Creating Categoricals
```python
# Create categorical
cat = pd.Categorical(['a', 'b', 'c', 'a', 'b', 'c'])
s = pd.Series(cat)

# From DataFrame column
df['category'] = df['category'].astype('category')

# With custom categories
cat = pd.Categorical(['a', 'b', 'c'], categories=['c', 'b', 'a', 'd'])

# Ordered categorical
cat = pd.Categorical(['low', 'medium', 'high'], 
                     categories=['low', 'medium', 'high'], 
                     ordered=True)
```

### Working with Categoricals
```python
# Access properties
s.cat.categories  # Get categories
s.cat.codes  # Get category codes
s.cat.ordered  # Check if ordered

# Modify categories
s.cat.add_categories(['d'])  # Add new category
s.cat.remove_categories(['a'])  # Remove category
s.cat.rename_categories({'a': 'A', 'b': 'B'})  # Rename
s.cat.reorder_categories(['c', 'b', 'a'])  # Reorder
s.cat.as_ordered()  # Make ordered
s.cat.as_unordered()  # Make unordered

# Operations
s.cat.remove_unused_categories()  # Remove unused
```

## MultiIndex Operations

### Creating MultiIndex
```python
# From tuples
index = pd.MultiIndex.from_tuples([('A', 1), ('A', 2), ('B', 1), ('B', 2)])
df = pd.DataFrame(np.random.randn(4, 2), index=index)

# From arrays
arrays = [['A', 'A', 'B', 'B'], [1, 2, 1, 2]]
index = pd.MultiIndex.from_arrays(arrays, names=['first', 'second'])

# From product
index = pd.MultiIndex.from_product([['A', 'B'], [1, 2]], 
                                   names=['first', 'second'])

# Set MultiIndex from columns
df = df.set_index(['col1', 'col2'])
```

### Working with MultiIndex
```python
# Selection
df.loc[('A', 1)]  # Select specific index
df.loc['A']  # Select first level
df.loc[('A', slice(None))]  # All second level for 'A'

# Cross-section
df.xs('A', level='first')  # Cross-section at level
df.xs(1, level='second')

# Swapping levels
df.swaplevel()
df.swaplevel('first', 'second')

# Sorting
df.sort_index(level=0)
df.sort_index(level=['first', 'second'])

# Reset index
df.reset_index()  # Move index to columns
df.reset_index(level='first')  # Reset specific level
```

## Performance Optimization

### Memory Usage
```python
# Check memory usage
df.memory_usage()
df.memory_usage(deep=True)  # Include object dtype memory
df.info(memory_usage='deep')

# Optimize dtypes
df['int_col'] = df['int_col'].astype('int32')  # Downcast integer
df['float_col'] = df['float_col'].astype('float32')  # Downcast float
df['cat_col'] = df['cat_col'].astype('category')  # Convert to categorical

# Read with optimized dtypes
dtypes = {'col1': 'int32', 'col2': 'float32', 'col3': 'category'}
df = pd.read_csv('file.csv', dtype=dtypes)
```

### Query Optimization
```python
# Use query for complex filtering
df.query('A > 0 and B < 5')  # Faster than boolean indexing

# Use eval for complex calculations
df.eval('C = A + B')  # Faster than df['C'] = df['A'] + df['B']

# Numexpr backend
pd.set_option('compute.use_numexpr', True)
```

### Vectorization
```python
# Avoid loops, use vectorized operations
# Bad
result = []
for i in range(len(df)):
    result.append(df.iloc[i]['A'] * 2)

# Good
result = df['A'] * 2

# Use NumPy functions
df['B'] = np.where(df['A'] > 0, 1, 0)  # Conditional assignment
```

### Chunking Large Data
```python
# Read in chunks
chunk_size = 10000
chunks = []
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    # Process chunk
    processed = chunk.groupby('category').sum()
    chunks.append(processed)

result = pd.concat(chunks)

# Use iterators
reader = pd.read_csv('large_file.csv', iterator=True)
df = reader.get_chunk(1000)
```

## Best Practices

### Data Validation
```python
# Check for duplicates
df.duplicated()  # Boolean mask
df.drop_duplicates()  # Remove duplicates
df.drop_duplicates(subset=['col1', 'col2'])  # Based on columns

# Validate data types
assert df['numeric_col'].dtype in ['int64', 'float64']
assert df['date_col'].dtype == 'datetime64[ns]'

# Check for missing values
assert df['required_col'].notna().all()

# Validate ranges
assert df['percentage'].between(0, 100).all()
assert df['positive_col'].ge(0).all()
```

### Method Chaining
```python
# Clean method chaining
result = (df
    .dropna()
    .assign(new_col=lambda x: x['A'] * 2)
    .query('B > 0')
    .groupby('category')
    .agg({'C': 'sum', 'D': 'mean'})
    .sort_values('C', ascending=False)
    .head(10)
)
```

### Avoiding Common Pitfalls
```python
# Copy vs View
df_copy = df.copy()  # Explicit copy
df_view = df[:]  # May be a view

# SettingWithCopyWarning
# Bad
df[df['A'] > 0]['B'] = 0

# Good
df.loc[df['A'] > 0, 'B'] = 0

# Chained indexing
# Bad
df['A'][0] = 10

# Good
df.loc[0, 'A'] = 10

# In operator with Series
# Check index membership
'a' in s  # Checks if 'a' is in index

# Check value membership
2 in s.values  # Checks if 2 is in values
s.isin([2]).any()  # Alternative
```

## Common Patterns

### Data Cleaning Pipeline
```python
def clean_data(df):
    """Complete data cleaning pipeline"""
    return (df
        .drop_duplicates()
        .dropna(subset=['critical_col'])
        .fillna({'col1': 0, 'col2': 'unknown'})
        .astype({'int_col': 'int32', 'cat_col': 'category'})
        .assign(
            date_col=lambda x: pd.to_datetime(x['date_col']),
            price_clean=lambda x: x['price'].str.replace('$', '').astype(float)
        )
        .query('price_clean > 0')
        .reset_index(drop=True)
    )

cleaned_df = clean_data(raw_df)
```

### Time Series Analysis Pattern
```python
def analyze_time_series(df, date_col, value_col):
    """Complete time series analysis"""
    # Prepare data
    ts = df.set_index(pd.to_datetime(df[date_col]))[value_col].sort_index()
    
    # Resample to daily frequency
    daily = ts.resample('D').mean()
    
    # Calculate rolling statistics
    rolling_mean = daily.rolling(window=7).mean()
    rolling_std = daily.rolling(window=7).std()
    
    # Calculate trend
    trend = daily.rolling(window=30).mean()
    
    # Seasonal decomposition
    from statsmodels.tsa.seasonal import seasonal_decompose
    decomposition = seasonal_decompose(daily.dropna(), model='additive', period=7)
    
    return {
        'daily': daily,
        'rolling_mean': rolling_mean,
        'rolling_std': rolling_std,
        'trend': trend,
        'seasonal': decomposition.seasonal,
        'residual': decomposition.resid
    }
```

### Feature Engineering Pattern
```python
def engineer_features(df):
    """Create new features from existing data"""
    return df.assign(
        # Date features
        year=lambda x: x['date'].dt.year,
        month=lambda x: x['date'].dt.month,
        day_of_week=lambda x: x['date'].dt.dayofweek,
        is_weekend=lambda x: x['date'].dt.dayofweek.isin([5, 6]),
        
        # Numerical features
        log_value=lambda x: np.log1p(x['value']),
        value_squared=lambda x: x['value'] ** 2,
        value_pct_change=lambda x: x['value'].pct_change(),
        
        # Categorical features
        category_encoded=lambda x: x['category'].astype('category').cat.codes,
        
        # Interaction features
        value_category_interaction=lambda x: x['value'] * x['category_encoded'],
        
        # Window features
        value_rolling_mean=lambda x: x['value'].rolling(window=7, min_periods=1).mean(),
        value_rolling_std=lambda x: x['value'].rolling(window=7, min_periods=1).std()
    )
```

## Troubleshooting

### Common Errors and Solutions

#### SettingWithCopyWarning
```python
# Problem
df[df['A'] > 0]['B'] = 10  # Warning!

# Solution
df.loc[df['A'] > 0, 'B'] = 10  # Use .loc for setting values
```

#### Memory Errors
```python
# Problem: Out of memory when reading large file
# Solution: Read in chunks
for chunk in pd.read_csv('large_file.csv', chunksize=10000):
    process(chunk)

# Or use dask for larger-than-memory datasets
import dask.dataframe as dd
df = dd.read_csv('large_file.csv')
```

#### Slow Operations
```python
# Problem: Slow iteration
# Bad
for idx, row in df.iterrows():
    df.loc[idx, 'new'] = row['A'] * 2

# Solution: Vectorize
df['new'] = df['A'] * 2

# For complex operations use apply or vectorized NumPy
df['new'] = df.apply(lambda row: complex_function(row), axis=1)
```

#### Index Alignment Issues
```python
# Problem: Unexpected NaN values after operation
s1 = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
s2 = pd.Series([4, 5, 6], index=['b', 'c', 'd'])
result = s1 + s2  # NaN for 'a' and 'd'

# Solution: Explicitly handle alignment
result = s1.add(s2, fill_value=0)  # Fill missing with 0
```

### Performance Profiling
```python
# Time operations
%timeit df.groupby('category').sum()

# Profile memory usage
from memory_profiler import profile

@profile
def process_data(df):
    return df.groupby('category').agg({'value': 'sum'})

# Line profiling
%lprun -f process_data process_data(df)
```

### Debugging Tips
```python
# Set display options for debugging
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Check data types
df.dtypes
df.info()

# Inspect specific values
df.iloc[0]  # First row
df.iloc[-1]  # Last row
df.sample(5)  # Random sample

# Check for issues
df.isna().sum()  # Missing values per column
df.duplicated().sum()  # Number of duplicates
df.describe()  # Statistical summary
```

## Conclusion

Pandas is an essential tool for data analysis in Python, providing powerful and flexible data structures along with a vast array of functions for data manipulation, analysis, and visualization. Key takeaways:

- Use vectorized operations instead of loops for better performance
- Leverage method chaining for cleaner code
- Understand the difference between views and copies
- Use appropriate data types to optimize memory usage
- Take advantage of pandas' integration with the Python ecosystem
- Profile and optimize performance-critical code
- Follow best practices to avoid common pitfalls

The library continues to evolve with new features and optimizations, making it increasingly powerful for handling everything from small datasets to large-scale data analysis tasks.