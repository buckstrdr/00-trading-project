# Streamlit Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Core Concepts](#core-concepts)
5. [Display Elements](#display-elements)
6. [Input Widgets](#input-widgets)
7. [Layout & Containers](#layout--containers)
8. [Data Display](#data-display)
9. [Charts & Visualization](#charts--visualization)
10. [Media Elements](#media-elements)
11. [Control Flow](#control-flow)
12. [Session State](#session-state)
13. [Caching & Performance](#caching--performance)
14. [File Handling](#file-handling)
15. [Multipage Apps](#multipage-apps)
16. [Custom Components](#custom-components)
17. [Theming & Styling](#theming--styling)
18. [Configuration](#configuration)
19. [Deployment](#deployment)
20. [Best Practices](#best-practices)

## Introduction

Streamlit is an open-source Python framework that makes it easy to create and share beautiful, custom web apps for machine learning and data science. With just a few lines of Python code, you can build interactive dashboards, data exploration tools, and machine learning demos.

### Key Features
- **Pure Python**: Write in Python, no need for HTML/CSS/JavaScript
- **Interactive Widgets**: Built-in widgets for user input
- **Live Reload**: See changes instantly as you code
- **Data Caching**: Smart caching for expensive computations
- **Easy Deployment**: Deploy to Streamlit Community Cloud or your own servers
- **Custom Components**: Extend with React components

## Installation

### Basic Installation
```bash
# Install via pip
pip install streamlit

# Verify installation
streamlit --version

# Run hello world app
streamlit hello
```

### Installation in Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install streamlit

# Using uv (modern Python package manager)
uv venv --python 3.12
source .venv/bin/activate
uv pip install streamlit
```

### Development Installation
```bash
# Clone repository
git clone https://github.com/streamlit/streamlit.git
cd streamlit

# Setup development environment
cd lib
python -m venv venv
source ./venv/bin/activate
make all-dev
```

### Additional Dependencies
```python
# For data science
pip install pandas numpy matplotlib plotly altair

# For machine learning
pip install scikit-learn tensorflow torch

# For databases
pip install sqlalchemy psycopg2

# For cloud services
pip install boto3 google-cloud-storage azure-storage-blob
```

## Getting Started

### Your First Streamlit App
```python
# app.py
import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="My First App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("Hello Streamlit! 🎈")
st.write("This is my first Streamlit application")

# Interactive elements
name = st.text_input("What's your name?")
if name:
    st.write(f"Hello, {name}!")

# Data display
df = pd.DataFrame({
    'Column A': np.random.randn(10),
    'Column B': np.random.randn(10)
})
st.dataframe(df)

# Chart
st.line_chart(df)
```

### Running Your App
```bash
# Basic run
streamlit run app.py

# With custom port
streamlit run app.py --server.port 8080

# With custom address
streamlit run app.py --server.address 0.0.0.0

# Development mode
streamlit run app.py --server.runOnSave true
```

## Core Concepts

### Streamlit Flow
```python
import streamlit as st

# Streamlit runs your script from top to bottom
# Every interaction causes a rerun

# Static elements (run once per session)
st.title("My App")

# Dynamic elements (re-evaluated on each run)
counter = st.button("Click me")
if counter:
    st.write("Button clicked!")

# Widget state persists across reruns
text = st.text_input("Enter text")
st.write(f"You entered: {text}")
```

### Magic Commands
```python
import streamlit as st
import pandas as pd

# Magic: Variables and literals are automatically displayed
"# This is a header"
"This is text"

df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
df  # Automatically displayed as a table

x = 10
y = 20
x + y  # Displays 30

# Equivalent to st.write()
st.write("# This is a header")
st.write("This is text")
st.write(df)
st.write(x + y)
```

### Write and Markdown
```python
import streamlit as st

# st.write - Universal display function
st.write("Hello **world**!")  # Markdown
st.write(1234)  # Numbers
st.write(df)  # DataFrames
st.write({"key": "value"})  # Dicts
st.write(my_function)  # Functions

# Markdown
st.markdown("# Header 1")
st.markdown("## Header 2")
st.markdown("**Bold** and *italic* text")
st.markdown("[Link](https://streamlit.io)")
st.markdown("- Item 1\n- Item 2")

# LaTeX
st.latex(r'''
    a^2 + b^2 = c^2
''')

# Code blocks
code = '''
def hello():
    print("Hello, World!")
'''
st.code(code, language='python')
```

## Display Elements

### Text Elements
```python
import streamlit as st

# Title
st.title("Main Title")

# Header
st.header("Section Header")

# Subheader
st.subheader("Subsection")

# Text
st.text("Plain text display")

# Caption
st.caption("This is a caption")

# Preformatted text
st.text("""
    Preformatted text
    Preserves    spacing
    And line breaks
""")

# Success, info, warning, error messages
st.success("Success message ✅")
st.info("Info message ℹ️")
st.warning("Warning message ⚠️")
st.error("Error message ❌")

# Exception display
try:
    1 / 0
except Exception as e:
    st.exception(e)
```

### Metric Display
```python
import streamlit as st

# Single metric
st.metric(
    label="Temperature",
    value="70 °F",
    delta="1.2 °F",
    delta_color="normal"  # or "inverse" or "off"
)

# Multiple metrics in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Revenue", "$1M", "+10%")
with col2:
    st.metric("Users", "1.2K", "-3%", delta_color="inverse")
with col3:
    st.metric("Performance", "98%", "5%")

# Metric with custom formatting
value = 1234567.89
st.metric(
    "Sales",
    f"${value:,.2f}",
    f"{(value * 0.1):+,.0f}"
)
```

### JSON Display
```python
import streamlit as st

# Display JSON data
data = {
    "name": "John Doe",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "New York"
    },
    "hobbies": ["reading", "coding", "hiking"]
}

st.json(data, expanded=True)  # expanded=False to collapse initially
```

## Input Widgets

### Text Inputs
```python
import streamlit as st

# Text input
name = st.text_input(
    "Enter your name",
    value="",
    max_chars=50,
    key="name_input",
    placeholder="Type here...",
    disabled=False,
    label_visibility="visible"  # or "hidden" or "collapsed"
)

# Password input
password = st.text_input("Password", type="password")

# Text area
text = st.text_area(
    "Enter long text",
    value="",
    height=150,
    max_chars=500,
    placeholder="Start typing..."
)

# Number input
age = st.number_input(
    "Enter your age",
    min_value=0,
    max_value=120,
    value=25,
    step=1,
    format="%d"
)

# With validation
email = st.text_input("Email")
if email and "@" not in email:
    st.error("Please enter a valid email")
```

### Selection Widgets
```python
import streamlit as st

# Selectbox
option = st.selectbox(
    "Choose an option",
    ["Option 1", "Option 2", "Option 3"],
    index=0,
    format_func=lambda x: x.upper(),
    placeholder="Select...",
    disabled=False
)

# Multiselect
options = st.multiselect(
    "Choose multiple options",
    ["Red", "Green", "Blue", "Yellow"],
    default=["Red"],
    max_selections=3
)

# Radio buttons
choice = st.radio(
    "Pick one",
    ["Option A", "Option B", "Option C"],
    index=0,
    horizontal=True,
    captions=["First", "Second", "Third"]
)

# Checkbox
agree = st.checkbox("I agree", value=False)

# Toggle
on = st.toggle("Enable feature", value=False)

# Select slider
value = st.select_slider(
    "Select a value",
    options=["Bad", "Good", "Excellent"],
    value="Good"
)
```

### Numeric Inputs
```python
import streamlit as st
from datetime import datetime, date, time

# Slider
value = st.slider(
    "Select a value",
    min_value=0,
    max_value=100,
    value=50,
    step=1,
    format="%d",
    key="slider"
)

# Range slider
start, end = st.slider(
    "Select range",
    0, 100, (25, 75)
)

# Date input
d = st.date_input(
    "Pick a date",
    value=date.today(),
    min_value=date(2020, 1, 1),
    max_value=date(2030, 12, 31),
    format="YYYY/MM/DD"
)

# Time input
t = st.time_input(
    "Pick a time",
    value=time(8, 45),
    step=900  # 15 minutes
)

# Date range
start_date, end_date = st.date_input(
    "Select date range",
    value=(date.today(), date.today()),
    key="date_range"
)
```

### Buttons and Actions
```python
import streamlit as st

# Button
if st.button("Click me", type="primary", use_container_width=True):
    st.write("Button clicked!")

# Download button
csv = df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="data.csv",
    mime="text/csv",
    key="download-csv"
)

# Link button
st.link_button("Go to Google", "https://google.com")

# Form
with st.form("my_form", clear_on_submit=True):
    st.write("Inside the form")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0)
    
    # Form submit button
    submitted = st.form_submit_button("Submit", type="primary")
    if submitted:
        st.write(f"Name: {name}, Age: {age}")

# Feedback widgets
sentiment = st.feedback("thumbs")  # or "faces" or "stars"
if sentiment is not None:
    st.write(f"Feedback: {sentiment}")
```

### Color and File Inputs
```python
import streamlit as st

# Color picker
color = st.color_picker(
    "Pick a color",
    value="#00f900"
)
st.write(f"Selected color: {color}")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "txt", "xlsx"],
    accept_multiple_files=False,
    key="file_uploader"
)

if uploaded_file is not None:
    # Read file
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)

# Multiple files
files = st.file_uploader(
    "Upload files",
    accept_multiple_files=True
)
for file in files:
    st.write(f"File: {file.name}")

# Camera input
picture = st.camera_input("Take a picture")
if picture:
    st.image(picture)
```

## Layout & Containers

### Columns
```python
import streamlit as st

# Equal columns
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Column 1")
    st.write("Content in column 1")

with col2:
    st.header("Column 2")
    st.write("Content in column 2")

with col3:
    st.header("Column 3")
    st.write("Content in column 3")

# Unequal columns
col1, col2 = st.columns([2, 1])  # 2:1 ratio

# With gap
col1, col2 = st.columns(2, gap="large")  # "small", "medium", "large"

# Nested columns
col1, col2 = st.columns(2)
with col1:
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.write("Nested 1")
    with sub_col2:
        st.write("Nested 2")
```

### Tabs
```python
import streamlit as st

# Create tabs
tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Data", "🔧 Settings"])

with tab1:
    st.header("Chart View")
    st.line_chart(df)

with tab2:
    st.header("Data View")
    st.dataframe(df)

with tab3:
    st.header("Settings")
    st.slider("Adjust value", 0, 100)

# Dynamic tabs
tab_names = ["Tab 1", "Tab 2", "Tab 3"]
tabs = st.tabs(tab_names)
for i, tab in enumerate(tabs):
    with tab:
        st.write(f"Content for {tab_names[i]}")
```

### Expander
```python
import streamlit as st

# Basic expander
with st.expander("See details", expanded=False):
    st.write("Hidden content")
    st.image("https://via.placeholder.com/150")
    
# Multiple expanders
for i in range(3):
    with st.expander(f"Section {i+1}"):
        st.write(f"Content for section {i+1}")

# Expander with state
expander_state = st.expander("Advanced", expanded=True)
with expander_state:
    option = st.selectbox("Choose", ["A", "B", "C"])
    if st.button("Apply"):
        st.success(f"Applied: {option}")
```

### Container
```python
import streamlit as st

# Basic container
with st.container():
    st.write("This is inside a container")
    st.button("Button in container")

# Container with border
with st.container(border=True):
    st.write("Container with border")
    
# Dynamic container
container = st.container()
container.write("Content 1")
# Other code...
container.write("Content 2")  # Added to same container

# Empty container for updates
placeholder = st.empty()
for i in range(10):
    placeholder.write(f"Count: {i}")
    time.sleep(0.1)
placeholder.empty()  # Clear content
```

### Sidebar
```python
import streamlit as st

# Sidebar elements
with st.sidebar:
    st.title("Sidebar")
    
    # Sidebar-specific elements
    option = st.selectbox("Choose", ["A", "B", "C"])
    
    # Sidebar navigation
    page = st.radio("Navigation", ["Home", "About", "Contact"])
    
    # Sidebar form
    with st.form("sidebar_form"):
        name = st.text_input("Name")
        submit = st.form_submit_button("Submit")

# Direct sidebar access
st.sidebar.write("Direct sidebar write")
st.sidebar.button("Sidebar button")

# Sidebar with sections
st.sidebar.header("Settings")
theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date range")
```

### Popover and Dialog
```python
import streamlit as st

# Popover
with st.popover("Open popover"):
    st.markdown("This is popover content")
    name = st.text_input("Enter name")
    if st.button("Submit"):
        st.write(f"Hello {name}")

# Dialog (modal)
@st.dialog("My Dialog")
def show_dialog():
    st.write("Dialog content")
    name = st.text_input("Name")
    if st.button("Submit"):
        st.rerun()

if st.button("Open Dialog"):
    show_dialog()
```

## Data Display

### DataFrames
```python
import streamlit as st
import pandas as pd
import numpy as np

# Create sample dataframe
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Salary': [50000, 60000, 70000],
    'Department': ['IT', 'HR', 'Finance']
})

# Basic dataframe display
st.dataframe(df)

# Styled dataframe
st.dataframe(
    df,
    use_container_width=True,
    hide_index=False,
    column_order=["Name", "Department", "Age", "Salary"],
    column_config={
        "Name": st.column_config.TextColumn(
            "Employee Name",
            help="The name of the employee",
            max_chars=50,
        ),
        "Age": st.column_config.NumberColumn(
            "Age (years)",
            min_value=0,
            max_value=120,
            step=1,
            format="%d years",
        ),
        "Salary": st.column_config.NumberColumn(
            "Annual Salary",
            format="$%d",
        ),
        "Department": st.column_config.SelectboxColumn(
            "Department",
            options=["IT", "HR", "Finance", "Marketing"],
        ),
    }
)

# Editable dataframe
edited_df = st.data_editor(
    df,
    num_rows="dynamic",  # Allow adding/deleting rows
    disabled=["Name"],  # Disable editing for specific columns
    key="data_editor"
)

# Display changes
if st.button("Show changes"):
    st.write("Edited data:", edited_df)
```

### Column Configuration
```python
import streamlit as st
import pandas as pd
from datetime import datetime, date

# Advanced column configurations
df = pd.DataFrame({
    'text': ['Item 1', 'Item 2'],
    'number': [100, 200],
    'float': [1.5, 2.5],
    'date': [date(2024, 1, 1), date(2024, 2, 1)],
    'datetime': [datetime.now(), datetime.now()],
    'bool': [True, False],
    'category': ['A', 'B'],
    'link': ['https://google.com', 'https://github.com'],
    'progress': [0.3, 0.7],
    'rating': [3, 5],
    'image': ['https://via.placeholder.com/50', 'https://via.placeholder.com/50'],
})

st.dataframe(
    df,
    column_config={
        "text": st.column_config.TextColumn("Text", max_chars=100),
        "number": st.column_config.NumberColumn("Number", format="%d"),
        "float": st.column_config.NumberColumn("Float", format="%.2f"),
        "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
        "datetime": st.column_config.DatetimeColumn("DateTime", format="YYYY-MM-DD HH:mm"),
        "bool": st.column_config.CheckboxColumn("Boolean", default=False),
        "category": st.column_config.SelectboxColumn(
            "Category",
            options=["A", "B", "C"],
            required=True
        ),
        "link": st.column_config.LinkColumn("Link", display_text="Open"),
        "progress": st.column_config.ProgressColumn("Progress", min_value=0, max_value=1),
        "rating": st.column_config.NumberColumn("Rating", min_value=1, max_value=5, step=1),
        "image": st.column_config.ImageColumn("Image", width="medium"),
    }
)

# List and chart columns
data_with_lists = pd.DataFrame({
    'Name': ['Product A', 'Product B'],
    'Tags': [['tag1', 'tag2'], ['tag3', 'tag4']],
    'Sales': [[10, 20, 30, 40], [15, 25, 35, 45]],
})

st.dataframe(
    data_with_lists,
    column_config={
        "Tags": st.column_config.ListColumn("Tags"),
        "Sales": st.column_config.BarChartColumn(
            "Sales Trend",
            y_min=0,
            y_max=50,
        ),
    }
)
```

### Static Tables
```python
import streamlit as st
import pandas as pd

# Static table (not interactive)
st.table(df)

# Metric table
metrics_df = pd.DataFrame({
    'Metric': ['Revenue', 'Users', 'Growth'],
    'Value': ['$1M', '10K', '25%'],
    'Change': ['+10%', '+500', '+5%']
})
st.table(metrics_df)
```

## Charts & Visualization

### Built-in Charts
```python
import streamlit as st
import pandas as pd
import numpy as np

# Generate sample data
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
)

# Line chart
st.line_chart(chart_data)

# Area chart
st.area_chart(chart_data)

# Bar chart
st.bar_chart(chart_data)

# Scatter chart
scatter_data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100),
    'size': np.random.randint(10, 100, 100),
    'color': np.random.choice(['red', 'blue', 'green'], 100)
})
st.scatter_chart(
    scatter_data,
    x='x',
    y='y',
    color='color',
    size='size'
)
```

### Map Visualization
```python
import streamlit as st
import pandas as pd
import numpy as np

# Map data
map_data = pd.DataFrame(
    np.random.randn(100, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon']
)

# Simple map
st.map(map_data)

# Advanced map with pydeck
import pydeck as pdk

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=37.76,
        longitude=-122.4,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=map_data,
            get_position='[lon, lat]',
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
    ],
))
```

### Plotly Charts
```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Plotly Express
df = px.data.iris()
fig = px.scatter(
    df, 
    x="sepal_width", 
    y="sepal_length", 
    color="species",
    size="petal_length",
    hover_data=["petal_width"]
)
st.plotly_chart(fig, use_container_width=True)

# Plotly Graph Objects
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4],
    y=[10, 11, 12, 13],
    mode='lines+markers',
    name='Trace 1'
))
fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4],
    y=[16, 15, 14, 13],
    mode='lines+markers',
    name='Trace 2'
))
fig.update_layout(
    title="Interactive Plot",
    xaxis_title="X Axis",
    yaxis_title="Y Axis",
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True, key="plotly_chart")

# 3D Plot
fig = px.scatter_3d(
    df, x='sepal_length', y='sepal_width', z='petal_width',
    color='species'
)
st.plotly_chart(fig)
```

### Altair Charts
```python
import streamlit as st
import altair as alt
import pandas as pd

# Basic Altair chart
source = pd.DataFrame({
    'a': ['A', 'B', 'C', 'D', 'E'],
    'b': [28, 55, 43, 91, 81]
})

chart = alt.Chart(source).mark_bar().encode(
    x='a',
    y='b',
    color=alt.Color('a', legend=None),
    tooltip=['a', 'b']
)
st.altair_chart(chart, use_container_width=True)

# Interactive Altair chart
source = pd.DataFrame(
    np.random.randn(100, 3),
    columns=['a', 'b', 'c']
)

base = alt.Chart(source).encode(
    x='a:Q',
    y='b:Q',
    color='c:Q'
)

chart = base.mark_circle(size=60).interactive()
st.altair_chart(chart, use_container_width=True)

# Layered chart
line = alt.Chart(source).mark_line().encode(
    x='a',
    y='b'
)
point = alt.Chart(source).mark_point().encode(
    x='a',
    y='b'
)
chart = line + point
st.altair_chart(chart, use_container_width=True)
```

### Matplotlib & Seaborn
```python
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Matplotlib
fig, ax = plt.subplots()
x = np.linspace(0, 2 * np.pi, 100)
ax.plot(x, np.sin(x), label='sin(x)')
ax.plot(x, np.cos(x), label='cos(x)')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Trigonometric Functions')
ax.legend()
st.pyplot(fig)

# Seaborn
fig, ax = plt.subplots(figsize=(10, 6))
tips = sns.load_dataset("tips")
sns.boxplot(x="day", y="total_bill", hue="smoker", data=tips, ax=ax)
st.pyplot(fig)

# Multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes[0, 0].hist(np.random.randn(100))
axes[0, 1].scatter(np.random.randn(100), np.random.randn(100))
axes[1, 0].plot(np.random.randn(100).cumsum())
axes[1, 1].bar(['A', 'B', 'C'], [1, 2, 3])
plt.tight_layout()
st.pyplot(fig)
```

### Bokeh Charts
```python
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool
import numpy as np

# Create Bokeh figure
x = np.linspace(0, 4*np.pi, 100)
y = np.sin(x)

p = figure(
    title="Sine Wave",
    x_axis_label='x',
    y_axis_label='sin(x)',
    width=700,
    height=400
)

# Add line renderer with hover tool
p.line(x, y, line_width=2, color='navy', alpha=0.5)

# Add hover tool
hover = HoverTool(tooltips=[("(x,y)", "($x, $y)")])
p.add_tools(hover)

# Display in Streamlit
st.bokeh_chart(p, use_container_width=True)
```

### Graphviz
```python
import streamlit as st

# Create a graphviz chart
st.graphviz_chart('''
    digraph {
        A -> B
        B -> C
        C -> D
        D -> A
        A -> C
        B -> D
    }
''')

# More complex graph
graph = """
    digraph G {
        rankdir=LR
        node [shape=box]
        
        Start -> Process1
        Process1 -> Decision [label="Complete"]
        Decision -> Process2 [label="Yes"]
        Decision -> End [label="No"]
        Process2 -> End
        
        Start [shape=ellipse, style=filled, fillcolor=green]
        End [shape=ellipse, style=filled, fillcolor=red]
        Decision [shape=diamond, style=filled, fillcolor=yellow]
    }
"""
st.graphviz_chart(graph)
```

## Media Elements

### Images
```python
import streamlit as st
from PIL import Image
import numpy as np

# Display image from file
st.image('path/to/image.jpg', caption='Image caption', use_container_width=True)

# Display image from URL
st.image('https://via.placeholder.com/300', caption='Placeholder image')

# Display PIL image
image = Image.open('image.jpg')
st.image(image, caption='PIL Image')

# Display numpy array
arr = np.random.randint(0, 255, size=(100, 100, 3), dtype=np.uint8)
st.image(arr, caption='Random pixels')

# Multiple images
images = ['image1.jpg', 'image2.jpg', 'image3.jpg']
st.image(images, width=200, caption=['Image 1', 'Image 2', 'Image 3'])

# Image in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.image('image1.jpg')
with col2:
    st.image('image2.jpg')
with col3:
    st.image('image3.jpg')
```

### Audio
```python
import streamlit as st
import numpy as np

# Audio from file
st.audio('audio.mp3', format='audio/mp3', start_time=0, sample_rate=None)

# Audio from URL
st.audio('https://example.com/audio.wav')

# Audio from bytes
with open('audio.wav', 'rb') as f:
    audio_bytes = f.read()
st.audio(audio_bytes, format='audio/wav')

# Generated audio
sample_rate = 44100
duration = 2  # seconds
frequency = 440  # Hz (A4 note)
t = np.linspace(0, duration, sample_rate * duration)
audio_data = np.sin(2 * np.pi * frequency * t)
st.audio(audio_data, sample_rate=sample_rate)
```

### Video
```python
import streamlit as st

# Video from file
st.video('video.mp4', format='video/mp4', start_time=0, subtitles=None)

# Video from URL
st.video('https://example.com/video.mp4')

# Video from bytes
with open('video.mp4', 'rb') as f:
    video_bytes = f.read()
st.video(video_bytes)

# YouTube video (using iframe)
st.markdown("""
<iframe width="700" height="400" 
src="https://www.youtube.com/embed/VIDEO_ID" 
frameborder="0" allowfullscreen></iframe>
""", unsafe_allow_html=True)
```

## Control Flow

### Conditional Display
```python
import streamlit as st

# Basic conditional
if st.checkbox("Show details"):
    st.write("Here are the details...")

# Multiple conditions
option = st.radio("Choose view", ["Simple", "Detailed", "Advanced"])
if option == "Simple":
    st.write("Simple view")
elif option == "Detailed":
    st.write("Detailed view with more info")
else:
    st.write("Advanced view with all features")

# Nested conditions
if st.button("Start"):
    with st.spinner("Processing..."):
        # Simulate processing
        time.sleep(2)
    
    success = np.random.choice([True, False])
    if success:
        st.success("Process completed successfully!")
    else:
        st.error("Process failed. Please try again.")
```

### Stop Execution
```python
import streamlit as st

# Stop execution
name = st.text_input("Enter your name")
if not name:
    st.warning("Please enter your name")
    st.stop()

st.success(f"Hello, {name}!")

# With exit code
try:
    value = st.number_input("Enter a positive number")
    if value <= 0:
        st.error("Number must be positive!")
        st.stop()
    result = np.sqrt(value)
    st.write(f"Square root: {result}")
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()
```

### Rerun
```python
import streamlit as st
import time

# Manual rerun
if st.button("Refresh data"):
    st.rerun()

# Automatic rerun with delay
if 'counter' not in st.session_state:
    st.session_state.counter = 0

placeholder = st.empty()
placeholder.write(f"Counter: {st.session_state.counter}")

if st.button("Start counting"):
    for i in range(10):
        st.session_state.counter += 1
        time.sleep(0.5)
        st.rerun()

# Conditional rerun
if st.button("Process"):
    with st.spinner("Processing..."):
        # Do some processing
        time.sleep(2)
    st.session_state.processed = True
    st.rerun()

if 'processed' in st.session_state and st.session_state.processed:
    st.success("Processing complete!")
    st.session_state.processed = False
```

### Progress and Status
```python
import streamlit as st
import time

# Progress bar
progress_bar = st.progress(0, text="Processing...")
for i in range(100):
    progress_bar.progress(i + 1, text=f"Processing... {i+1}%")
    time.sleep(0.01)
st.success("Complete!")

# Spinner
with st.spinner("Loading data..."):
    time.sleep(2)
st.success("Data loaded!")

# Status container
with st.status("Processing files...", expanded=True) as status:
    st.write("Scanning files...")
    time.sleep(1)
    st.write("Found 100 files")
    time.sleep(1)
    st.write("Processing files...")
    time.sleep(1)
    status.update(label="Complete!", state="complete", expanded=False)

# Multiple status indicators
col1, col2, col3 = st.columns(3)
with col1:
    with st.spinner("Task 1..."):
        time.sleep(1)
with col2:
    with st.spinner("Task 2..."):
        time.sleep(1)
with col3:
    with st.spinner("Task 3..."):
        time.sleep(1)
st.success("All tasks complete!")
```

### Toast Notifications
```python
import streamlit as st

# Basic toast
st.toast("Hello world!", icon="🎉")

# Toast with duration
st.toast("This will disappear", icon="⏰", duration=3000)

# Multiple toasts
if st.button("Show notifications"):
    st.toast("First notification", icon="1️⃣")
    time.sleep(1)
    st.toast("Second notification", icon="2️⃣")
    time.sleep(1)
    st.toast("Third notification", icon="3️⃣")

# Success/Error toasts
try:
    # Some operation
    result = 10 / 2
    st.toast(f"Success! Result: {result}", icon="✅")
except Exception as e:
    st.toast(f"Error: {e}", icon="❌")
```

## Session State

### Basic Session State
```python
import streamlit as st

# Initialize session state
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Access and modify
st.write(f"Counter: {st.session_state.counter}")

if st.button("Increment"):
    st.session_state.counter += 1

if st.button("Reset"):
    st.session_state.counter = 0

# Alternative syntax
st.session_state['my_key'] = 'my_value'
value = st.session_state.get('my_key', 'default')
```

### Advanced Session State
```python
import streamlit as st

# Complex state management
if 'user' not in st.session_state:
    st.session_state.user = {
        'name': '',
        'age': 0,
        'preferences': [],
        'logged_in': False
    }

# Login system
if not st.session_state.user['logged_in']:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if username == "admin" and password == "password":
                st.session_state.user['name'] = username
                st.session_state.user['logged_in'] = True
                st.rerun()
            else:
                st.error("Invalid credentials")
else:
    st.write(f"Welcome, {st.session_state.user['name']}!")
    if st.button("Logout"):
        st.session_state.user['logged_in'] = False
        st.rerun()

# Persist widget state
st.text_input("Name", key="name_input")
st.write(f"You entered: {st.session_state.name_input}")

# Callbacks with session state
def on_change():
    st.session_state.last_changed = st.session_state.my_slider

st.slider("Value", 0, 100, key="my_slider", on_change=on_change)
if 'last_changed' in st.session_state:
    st.write(f"Last value: {st.session_state.last_changed}")
```

### Session State Patterns
```python
import streamlit as st

# Page navigation with session state
def navigate_to(page):
    st.session_state.current_page = page

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Navigation buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Home"):
        navigate_to('home')
with col2:
    if st.button("About"):
        navigate_to('about')
with col3:
    if st.button("Contact"):
        navigate_to('contact')

# Display page based on state
if st.session_state.current_page == 'home':
    st.title("Home Page")
elif st.session_state.current_page == 'about':
    st.title("About Page")
else:
    st.title("Contact Page")

# Form data persistence
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

with st.form("data_form"):
    st.session_state.form_data['name'] = st.text_input(
        "Name", 
        value=st.session_state.form_data.get('name', '')
    )
    st.session_state.form_data['email'] = st.text_input(
        "Email",
        value=st.session_state.form_data.get('email', '')
    )
    if st.form_submit_button("Save"):
        st.success("Data saved!")
```

## Caching & Performance

### Cache Data
```python
import streamlit as st
import pandas as pd
import time

# Cache data loading
@st.cache_data
def load_data(file_path):
    time.sleep(2)  # Simulate slow loading
    return pd.read_csv(file_path)

# Cache with TTL
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data_from_api(endpoint):
    # Fetch data from API
    return requests.get(endpoint).json()

# Cache with parameters
@st.cache_data
def process_data(df, column, operation="mean"):
    if operation == "mean":
        return df[column].mean()
    elif operation == "sum":
        return df[column].sum()
    else:
        return df[column].std()

# Clear cache
if st.button("Clear cache"):
    st.cache_data.clear()
```

### Cache Resource
```python
import streamlit as st
from sqlalchemy import create_engine
import torch

# Cache database connection
@st.cache_resource
def init_connection():
    return create_engine("postgresql://user:pass@localhost/db")

# Cache ML model
@st.cache_resource
def load_model():
    model = torch.load("model.pt")
    model.eval()
    return model

# Cache expensive object
@st.cache_resource
def create_expensive_object():
    # Create object that should persist across reruns
    return ExpensiveClass()

# Use cached resources
conn = init_connection()
model = load_model()
obj = create_expensive_object()
```

### Performance Optimization
```python
import streamlit as st

# Fragment for partial reruns
@st.fragment
def show_filters():
    # This won't trigger full app rerun
    st.slider("Filter 1", 0, 100)
    st.selectbox("Filter 2", ["A", "B", "C"])

# Lazy loading
@st.cache_data
def load_large_dataset():
    # Load only when needed
    return pd.read_csv("large_file.csv")

if st.checkbox("Show large dataset"):
    df = load_large_dataset()
    st.dataframe(df)

# Batch operations
@st.cache_data
def batch_process(items):
    results = []
    for item in items:
        # Process item
        results.append(process(item))
    return results

# Use generators for large data
def data_generator():
    for chunk in pd.read_csv("huge_file.csv", chunksize=1000):
        yield chunk

# Process in chunks
for chunk in data_generator():
    st.write(f"Processing chunk with {len(chunk)} rows")
```

## File Handling

### File Upload
```python
import streamlit as st
import pandas as pd
import json

# Single file upload
uploaded_file = st.file_uploader(
    "Choose a file",
    type=['csv', 'txt', 'json', 'xlsx'],
    accept_multiple_files=False,
    help="Upload a data file"
)

if uploaded_file is not None:
    # Get file details
    file_details = {
        "filename": uploaded_file.name,
        "filetype": uploaded_file.type,
        "filesize": uploaded_file.size
    }
    st.write(file_details)
    
    # Read file based on type
    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)
    elif uploaded_file.type == "application/json":
        data = json.load(uploaded_file)
        st.json(data)
    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")
        st.text(text)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
        st.dataframe(df)

# Multiple file upload
uploaded_files = st.file_uploader(
    "Choose files",
    accept_multiple_files=True
)

for uploaded_file in uploaded_files:
    st.write(f"Processing {uploaded_file.name}")
    # Process each file
```

### File Download
```python
import streamlit as st
import pandas as pd
import json

# Download button for text
text_content = "Hello, World!"
st.download_button(
    label="Download text file",
    data=text_content,
    file_name="hello.txt",
    mime="text/plain"
)

# Download CSV
df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="data.csv",
    mime="text/csv"
)

# Download JSON
data = {"key": "value", "number": 123}
json_str = json.dumps(data, indent=2)
st.download_button(
    label="Download JSON",
    data=json_str,
    file_name="data.json",
    mime="application/json"
)

# Download Excel
import io
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
    
st.download_button(
    label="Download Excel",
    data=buffer.getvalue(),
    file_name="data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Download generated file
def generate_report():
    report = "# Report\n\nThis is a generated report."
    return report.encode('utf-8')

if st.button("Generate Report"):
    report_data = generate_report()
    st.download_button(
        label="Download Report",
        data=report_data,
        file_name="report.md",
        mime="text/markdown"
    )
```

## Multipage Apps

### Page Configuration
```python
# pages/1_📊_Dashboard.py
import streamlit as st

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Dashboard Page")
st.write("This is the dashboard")

# pages/2_📈_Analytics.py
import streamlit as st

st.set_page_config(
    page_title="Analytics",
    page_icon="📈"
)

st.title("Analytics Page")
st.write("This is the analytics page")
```

### Navigation Patterns
```python
import streamlit as st

# Method 1: Using st.navigation (new)
pages = {
    "Home": [
        st.Page("home.py", title="Home", icon="🏠"),
        st.Page("about.py", title="About", icon="ℹ️"),
    ],
    "Tools": [
        st.Page("calculator.py", title="Calculator", icon="🧮"),
        st.Page("converter.py", title="Converter", icon="🔄"),
    ],
}

pg = st.navigation(pages)
pg.run()

# Method 2: Manual navigation with session state
def navigate_to(page):
    st.session_state.page = page

pages = {
    "Home": home_page,
    "About": about_page,
    "Contact": contact_page
}

if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Sidebar navigation
with st.sidebar:
    for page_name in pages.keys():
        if st.button(page_name):
            navigate_to(page_name)

# Display selected page
pages[st.session_state.page]()
```

### Shared State Across Pages
```python
# utils/state.py
import streamlit as st

def init_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'data' not in st.session_state:
        st.session_state.data = None

# pages/login.py
import streamlit as st
from utils.state import init_state

init_state()

if st.session_state.user is None:
    username = st.text_input("Username")
    if st.button("Login"):
        st.session_state.user = username
        st.switch_page("pages/dashboard.py")
else:
    st.write(f"Already logged in as {st.session_state.user}")
    st.switch_page("pages/dashboard.py")

# pages/dashboard.py
import streamlit as st
from utils.state import init_state

init_state()

if st.session_state.user:
    st.write(f"Welcome, {st.session_state.user}!")
else:
    st.error("Please login first")
    st.switch_page("pages/login.py")
```

## Custom Components

### Using Custom Components
```python
import streamlit as st
import streamlit.components.v1 as components

# Embed HTML
components.html(
    """
    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px;">
        <h2>Custom HTML Component</h2>
        <p>This is embedded HTML content</p>
        <button onclick="alert('Hello!')">Click me</button>
    </div>
    """,
    height=200
)

# Embed iframe
components.iframe("https://example.com", height=500)

# Use third-party components
# pip install streamlit-aggrid
from st_aggrid import AgGrid, GridOptionsBuilder

df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination()
gb.configure_selection('multiple')
grid_options = gb.build()

AgGrid(df, gridOptions=grid_options)
```

### Creating Custom Components
```python
# my_component/__init__.py
import streamlit.components.v1 as components
import os

# Declare component
_component_func = components.declare_component(
    "my_component",
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
)

def my_component(name, key=None):
    return _component_func(name=name, key=key)

# frontend/index.html
"""
<!DOCTYPE html>
<html>
<body>
<script>
    // Receive data from Python
    function onDataFromPython(event) {
        const data = event.detail.args;
        document.getElementById("output").innerHTML = "Hello, " + data.name;
        
        // Send data back to Python
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:componentReady",
            apiVersion: 1
        }, "*");
    }
    
    // Register event listener
    window.addEventListener("streamlit:dataFromPython", onDataFromPython);
</script>
<div id="output"></div>
</body>
</html>
"""
```

## Theming & Styling

### Theme Configuration
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#1A6CE7"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#1A1D21"
font = "sans serif"  # "sans serif", "serif", or "monospace"
```

### Dark Theme
```toml
# .streamlit/config.toml - Dark theme
[theme]
primaryColor = "#1ED760"
backgroundColor = "#121212"
secondaryBackgroundColor = "#333333"
textColor = "#FFFFFF"
font = "sans serif"
```

### Custom CSS
```python
import streamlit as st

# Inject custom CSS
st.markdown("""
<style>
    /* Main content area */
    .main {
        padding-top: 2rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styles */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    
    /* Custom metrics */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #cccccc;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

st.title("Styled App")
```

### HTML Components
```python
import streamlit as st

# Custom HTML/CSS components
st.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 1rem;
    color: white;
    text-align: center;
">
    <h1 style="margin: 0;">Welcome to My App</h1>
    <p style="margin: 0.5rem 0 0 0;">Beautiful custom design</p>
</div>
""", unsafe_allow_html=True)

# Cards
def create_card(title, content, color="#f0f2f6"):
    return f"""
    <div style="
        background-color: {color};
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1A6CE7;
        margin: 1rem 0;
    ">
        <h3 style="margin: 0 0 0.5rem 0;">{title}</h3>
        <p style="margin: 0;">{content}</p>
    </div>
    """

st.markdown(create_card("Card Title", "Card content goes here"), unsafe_allow_html=True)
```

## Configuration

### Config File
```toml
# .streamlit/config.toml

[global]
dataFrameSerialization = "arrow"
showErrorDetails = true

[server]
port = 8501
address = "localhost"
baseUrlPath = ""
enableCORS = true
enableXsrfProtection = true
maxUploadSize = 200
maxMessageSize = 200
enableWebsocketCompression = false
enableStaticServing = false
headless = false
runOnSave = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#1A6CE7"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#262730"
font = "sans serif"

[runner]
magicEnabled = true
installTracer = false
fixMatplotlib = true
postScriptGC = true
fastReruns = true

[client]
caching = true
displayEnabled = true
showSidebarNavigation = true
```

### Secrets Management
```toml
# .streamlit/secrets.toml (DO NOT commit to version control)
[database]
host = "localhost"
port = 5432
database = "mydb"
user = "myuser"
password = "mypassword"

[api]
key = "your-api-key"
secret = "your-api-secret"

[general]
email = "admin@example.com"
```

```python
import streamlit as st

# Access secrets
db_host = st.secrets["database"]["host"]
db_port = st.secrets["database"]["port"]
api_key = st.secrets["api"]["key"]

# Use with connection
conn = st.connection("mydb", type="sql")

# Environment variables (alternative)
import os
api_key = os.environ.get("API_KEY")
```

## Deployment

### Streamlit Community Cloud
```yaml
# requirements.txt
streamlit==1.28.0
pandas==2.0.3
numpy==1.24.3
plotly==5.15.0

# Deploy steps:
# 1. Push code to GitHub
# 2. Sign in to share.streamlit.io
# 3. Deploy from GitHub repository
# 4. Configure secrets in dashboard
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Deployment Platforms
```bash
# Heroku
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Create setup.sh
mkdir -p ~/.streamlit/
echo "[server]\nheadless = true\nport = $PORT\nenableCORS = false\n" > ~/.streamlit/config.toml

# AWS EC2
sudo apt update
sudo apt install python3-pip
pip3 install streamlit
streamlit run app.py --server.port 80

# Google Cloud Run
gcloud run deploy --source . --port 8501

# Azure App Service
az webapp up --name myapp --resource-group mygroup
```

## Best Practices

### Performance Optimization
```python
import streamlit as st

# 1. Use caching effectively
@st.cache_data(ttl=3600)
def expensive_computation(param):
    # Cache results for 1 hour
    return compute(param)

# 2. Lazy loading
if st.checkbox("Show detailed analysis"):
    detailed_data = expensive_computation()
    st.write(detailed_data)

# 3. Use fragments for partial updates
@st.fragment
def filter_controls():
    filters = {}
    filters['category'] = st.selectbox("Category", ["A", "B", "C"])
    filters['date'] = st.date_input("Date")
    return filters

# 4. Optimize dataframe display
st.dataframe(df, use_container_width=True, height=400)

# 5. Use generators for large datasets
@st.cache_data
def load_data_generator():
    for chunk in pd.read_csv("large_file.csv", chunksize=1000):
        yield chunk
```

### Code Organization
```python
# project_structure/
# ├── app.py              # Main application
# ├── pages/              # Multipage apps
# │   ├── 1_📊_Dashboard.py
# │   └── 2_📈_Analytics.py
# ├── components/         # Reusable components
# │   ├── __init__.py
# │   ├── charts.py
# │   └── filters.py
# ├── utils/             # Utility functions
# │   ├── __init__.py
# │   ├── data.py
# │   └── auth.py
# ├── data/              # Data files
# ├── .streamlit/        # Configuration
# │   ├── config.toml
# │   └── secrets.toml
# └── requirements.txt

# components/charts.py
import streamlit as st
import plotly.express as px

def create_line_chart(df, x, y, title):
    fig = px.line(df, x=x, y=y, title=title)
    st.plotly_chart(fig, use_container_width=True)

# app.py
from components.charts import create_line_chart
from utils.data import load_data

df = load_data()
create_line_chart(df, 'date', 'value', 'Trend Analysis')
```

### Error Handling
```python
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Error handling patterns
try:
    data = load_data()
    st.success("Data loaded successfully!")
except FileNotFoundError:
    st.error("Data file not found. Please upload a file.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    logger.exception("Unexpected error")
    if st.checkbox("Show error details"):
        st.exception(e)

# Validation
def validate_input(value):
    if value < 0:
        st.error("Value must be positive")
        return False
    return True

# Graceful degradation
@st.cache_data
def fetch_data():
    try:
        return fetch_from_api()
    except:
        st.warning("Using cached data")
        return load_cached_data()
```

### Testing
```python
# test_app.py
import streamlit as st
from streamlit.testing.v1 import AppTest
import pytest

def test_app():
    at = AppTest.from_file("app.py")
    at.run()
    
    # Test initial state
    assert not at.exception
    assert at.title[0].value == "My App"
    
    # Test interaction
    at.text_input[0].input("Test User").run()
    assert "Hello, Test User" in at.markdown[0].value
    
    # Test button click
    at.button[0].click().run()
    assert at.success[0]

# Run tests
# pytest test_app.py
```

### Security Best Practices
```python
import streamlit as st
import hashlib
import secrets

# 1. Never hardcode secrets
API_KEY = st.secrets["api"]["key"]  # Use secrets.toml

# 2. Validate and sanitize input
def sanitize_input(text):
    # Remove potentially harmful characters
    return "".join(c for c in text if c.isalnum() or c.isspace())

user_input = st.text_input("Enter text")
clean_input = sanitize_input(user_input)

# 3. Use HTTPS in production
# Configure in deployment settings

# 4. Implement authentication
def check_password():
    def password_entered():
        if hmac.compare_digest(
            hashlib.sha256(st.session_state["password"].encode()).hexdigest(),
            st.secrets["password_hash"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    
    if not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    
    return True

if check_password():
    st.write("Welcome to the protected app!")

# 5. Rate limiting for API calls
from functools import wraps
import time

def rate_limit(max_calls=10, period=60):
    def decorator(func):
        calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            if len(calls) >= max_calls:
                st.error(f"Rate limit exceeded. Try again later.")
                return None
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=5, period=60)
def api_call():
    # Make API call
    pass
```

## Conclusion

Streamlit is a powerful framework for building data applications quickly and efficiently. Key features include:

1. **Simple API**: Write apps in pure Python
2. **Rich Widgets**: Comprehensive set of input and display widgets
3. **Automatic Reactivity**: UI updates automatically on interaction
4. **Built-in Caching**: Optimize performance with smart caching
5. **Easy Deployment**: Deploy to cloud with minimal configuration
6. **Extensible**: Create custom components when needed

For more information and updates, visit:
- [Official Documentation](https://docs.streamlit.io)
- [Community Forum](https://discuss.streamlit.io)
- [GitHub Repository](https://github.com/streamlit/streamlit)
- [Component Gallery](https://streamlit.io/components)