# FastAPI Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Basic Concepts](#basic-concepts)
4. [Path Operations](#path-operations)
5. [Request Handling](#request-handling)
6. [Response Models](#response-models)
7. [Data Validation](#data-validation)
8. [Dependency Injection](#dependency-injection)
9. [Security and Authentication](#security-and-authentication)
10. [Database Integration](#database-integration)
11. [Async Operations](#async-operations)
12. [Background Tasks](#background-tasks)
13. [WebSockets](#websockets)
14. [CORS](#cors)
15. [Testing](#testing)
16. [OpenAPI Documentation](#openapi-documentation)
17. [Deployment](#deployment)
18. [Advanced Features](#advanced-features)
19. [Best Practices](#best-practices)
20. [Common Patterns](#common-patterns)

## Introduction

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It's designed to be easy to use, fast to code, ready for production, and based on standards like OpenAPI and JSON Schema.

### Key Features
- Fast performance (on par with NodeJS and Go)
- Fast to code (increase development speed by 200-300%)
- Fewer bugs (reduce human errors by 40%)
- Intuitive editor support
- Easy to learn and use
- Short, minimized code duplication
- Robust, production-ready code
- Standards-based (OpenAPI and JSON Schema)
- Automatic interactive API documentation

## Installation and Setup

### Basic Installation
```bash
# Install FastAPI
pip install fastapi

# Install ASGI server
pip install "uvicorn[standard]"

# For all features including validation
pip install "fastapi[all]"
```

### Creating Your First Application
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

### Running the Application
```bash
# Development server with auto-reload
uvicorn main:app --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000

# With custom settings
uvicorn main:app --workers 4 --log-level info
```

## Basic Concepts

### Application Instance
```python
from fastapi import FastAPI

# Basic app instance
app = FastAPI()

# With configuration
app = FastAPI(
    title="My API",
    description="This is a very fancy project",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
```

### Path Operations
```python
from fastapi import FastAPI

app = FastAPI()

# GET operation
@app.get("/users")
async def get_users():
    return {"users": ["Alice", "Bob"]}

# POST operation
@app.post("/users")
async def create_user(name: str):
    return {"name": name}

# PUT operation
@app.put("/users/{user_id}")
async def update_user(user_id: int, name: str):
    return {"user_id": user_id, "name": name}

# DELETE operation
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return {"deleted": user_id}

# PATCH operation
@app.patch("/users/{user_id}")
async def patch_user(user_id: int, name: str = None):
    return {"user_id": user_id, "name": name}
```

## Path Operations

### Path Parameters
```python
from fastapi import FastAPI, Path
from typing import Optional

app = FastAPI()

# Basic path parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# With validation
@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., title="The ID of the item", ge=1, le=1000)
):
    return {"item_id": item_id}

# Multiple path parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item_id": item_id}

# Enum path parameters
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}
```

### Query Parameters
```python
from fastapi import FastAPI, Query
from typing import Optional, List

app = FastAPI()

# Basic query parameters
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Optional query parameters
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Optional[str] = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

# Query parameter validation
@app.get("/items/")
async def read_items(
    q: Optional[str] = Query(
        None,
        min_length=3,
        max_length=50,
        regex="^fixedquery$",
        title="Query string",
        description="Query string for searching items"
    )
):
    return {"q": q}

# List query parameters
@app.get("/items/")
async def read_items(q: List[str] = Query([])):
    return {"q": q}

# Required query parameters
@app.get("/items/")
async def read_items(q: str = Query(..., min_length=3)):
    return {"q": q}
```

## Request Handling

### Request Body
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Define Pydantic model
class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None

# Basic request body
@app.post("/items/")
async def create_item(item: Item):
    return item

# Request body with path parameters
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

# Multiple body parameters
class User(BaseModel):
    username: str
    full_name: Optional[str] = None

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    return {"item_id": item_id, "item": item, "user": user}

# Body with validation
from pydantic import Field

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    tax: Optional[float] = Field(None, ge=0)
```

### Request Forms and Files
```python
from fastapi import FastAPI, File, UploadFile, Form
from typing import List

app = FastAPI()

# Form data
@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

# File upload
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}

# Multiple files
@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile]):
    return {"filenames": [file.filename for file in files]}

# File with form data
@app.post("/create/")
async def create_file(
    file: UploadFile,
    name: str = Form(...),
    description: str = Form(...)
):
    return {
        "filename": file.filename,
        "name": name,
        "description": description
    }
```

### Headers and Cookies
```python
from fastapi import FastAPI, Header, Cookie
from typing import Optional

app = FastAPI()

# Request headers
@app.get("/items/")
async def read_items(
    user_agent: Optional[str] = Header(None),
    x_token: Optional[str] = Header(None)
):
    return {"User-Agent": user_agent, "X-Token": x_token}

# Custom header names
@app.get("/items/")
async def read_items(
    strange_header: Optional[str] = Header(None, convert_underscores=False)
):
    return {"strange_header": strange_header}

# Cookies
@app.get("/items/")
async def read_items(ads_id: Optional[str] = Cookie(None)):
    return {"ads_id": ads_id}
```

## Response Models

### Basic Response Models
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    tax: Optional[float] = None

# Response model
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item

# Response model with exclusion
class UserIn(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    username: str
    email: str

@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    return user

# List response
@app.get("/items/", response_model=List[Item])
async def read_items():
    return [
        {"name": "Item 1", "price": 10.5},
        {"name": "Item 2", "price": 20.0}
    ]
```

### Response Model Configuration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    tax: Optional[float] = None
    tags: List[str] = []

# Exclude unset values
@app.post("/items/", response_model=Item, response_model_exclude_unset=True)
async def create_item(item: Item):
    return item

# Include/exclude specific fields
@app.get(
    "/items/{item_id}",
    response_model=Item,
    response_model_include={"name", "price"},
    response_model_exclude={"tax"}
)
async def read_item(item_id: str):
    return {"name": "Foo", "price": 35.4, "tax": 3.2}

# Response with status code
from fastapi import status

@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item
```

### Additional Response Data
```python
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse

app = FastAPI()

# Custom headers
@app.get("/items/")
async def read_items(response: Response):
    response.headers["X-Custom-Header"] = "custom-value"
    return {"items": ["item1", "item2"]}

# JSON response with custom status
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id == "not-found":
        return JSONResponse(
            status_code=404,
            content={"message": "Item not found"}
        )
    return {"item_id": item_id}

# HTML response
@app.get("/html/", response_class=HTMLResponse)
async def get_html():
    return """
    <html>
        <head><title>FastAPI HTML</title></head>
        <body><h1>Hello FastAPI</h1></body>
    </html>
    """

# File response
@app.get("/download/")
async def download_file():
    return FileResponse("path/to/file.pdf", media_type="application/pdf")
```

## Data Validation

### Pydantic Models
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str = Field(..., regex="^\d{5}$")

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex="^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(..., gt=0, le=120)
    salary: Decimal = Field(..., decimal_places=2)
    is_active: bool = True
    created_at: datetime
    address: Optional[Address] = None
    tags: List[str] = []

    # Custom validator
    @validator("email")
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email")
        return v

    # Root validator
    @validator("*", pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "salary": 50000.00,
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "tags": ["python", "fastapi"]
            }
        }
```

### Advanced Validation
```python
from pydantic import BaseModel, validator, root_validator
from typing import Any, Dict

class Item(BaseModel):
    name: str
    price: float
    quantity: int

    @validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

    @root_validator
    def check_total_value(cls, values):
        price = values.get("price")
        quantity = values.get("quantity")
        if price and quantity:
            total = price * quantity
            if total > 10000:
                raise ValueError("Total value too high")
        return values

    @validator("name")
    def name_alphanumeric(cls, v):
        assert v.replace(" ", "").isalnum(), "Name must be alphanumeric"
        return v

# Custom field types
from pydantic import constr, conint, confloat

class Product(BaseModel):
    id: conint(gt=0, le=1000)
    name: constr(min_length=2, max_length=50)
    price: confloat(gt=0, le=1000000)
    code: constr(regex="^[A-Z]{3}-\d{3}$")
```

## Dependency Injection

### Basic Dependencies
```python
from fastapi import FastAPI, Depends
from typing import Optional

app = FastAPI()

# Simple dependency
def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons
```

### Class Dependencies
```python
from fastapi import Depends

class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends()):
    return {
        "q": commons.q,
        "skip": commons.skip,
        "limit": commons.limit
    }
```

### Nested Dependencies
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    return {"username": "user", "token": token}

def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return current_user
```

### Dependencies with Yield
```python
from contextlib import contextmanager

# Database dependency
def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
async def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

# Context manager dependency
@contextmanager
def get_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        release_resource(resource)

@app.get("/resource/")
async def use_resource(resource = Depends(get_resource)):
    return {"resource": resource}
```

## Security and Authentication

### OAuth2 with Password Flow
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

app = FastAPI()

# Security configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Endpoints
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### API Key Security
```python
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery, APIKeyCookie

app = FastAPI()

# API Key configurations
API_KEY = "your-api-key"
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)
api_key_cookie = APIKeyCookie(name="api_key", auto_error=False)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query),
    api_key_cookie: str = Security(api_key_cookie),
):
    if api_key_header == API_KEY:
        return api_key_header
    elif api_key_query == API_KEY:
        return api_key_query
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

@app.get("/protected")
async def protected_route(api_key: str = Security(get_api_key)):
    return {"message": "Access granted", "api_key": api_key}
```

### HTTP Basic Authentication
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}
```

## Database Integration

### SQLAlchemy Setup
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, Depends, HTTPException

# Database configuration
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
# For SQLite: "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    is_offer = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# CRUD operations
@app.post("/items/")
def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/")
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(ItemDB).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, db: Session = Depends(get_db)):
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"deleted": item_id}
```

### Async SQLAlchemy
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Async database configuration
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_async_db():
    async with async_session() as session:
        yield session

@app.get("/items/")
async def read_items_async(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(ItemDB))
    items = result.scalars().all()
    return items

@app.post("/items/")
async def create_item_async(item: Item, db: AsyncSession = Depends(get_async_db)):
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item
```

### MongoDB Integration
```python
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional, List

# MongoDB configuration
MONGODB_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGODB_URL)
database = client.myapp
collection = database.items

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class ItemModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    price: float
    
    class Config:
        json_encoders = {ObjectId: str}

@app.post("/items/")
async def create_item_mongo(item: ItemModel):
    item_dict = item.dict(by_alias=True)
    result = await collection.insert_one(item_dict)
    item_dict["_id"] = result.inserted_id
    return item_dict

@app.get("/items/")
async def read_items_mongo(skip: int = 0, limit: int = 10):
    cursor = collection.find().skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    return items

@app.get("/items/{item_id}")
async def read_item_mongo(item_id: str):
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## Async Operations

### Async Endpoints
```python
import asyncio
from fastapi import FastAPI
import httpx

app = FastAPI()

# Basic async endpoint
@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(1)
    return {"message": "Async response"}

# Async with external API calls
@app.get("/external")
async def call_external_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

# Multiple async operations
@app.get("/multiple")
async def multiple_async_ops():
    tasks = [
        fetch_data_1(),
        fetch_data_2(),
        fetch_data_3()
    ]
    results = await asyncio.gather(*tasks)
    return {"results": results}

async def fetch_data_1():
    await asyncio.sleep(1)
    return "Data 1"

async def fetch_data_2():
    await asyncio.sleep(2)
    return "Data 2"

async def fetch_data_3():
    await asyncio.sleep(0.5)
    return "Data 3"
```

### Async Context Managers
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    await setup_database()
    yield
    # Shutdown
    print("Shutting down...")
    await cleanup_database()

app = FastAPI(lifespan=lifespan)

async def setup_database():
    # Initialize database connections
    pass

async def cleanup_database():
    # Close database connections
    pass
```

## Background Tasks

### Basic Background Tasks
```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)

@app.post("/send-notification/{email}")
async def send_notification(
    email: str, 
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(write_log, f"Notification sent to {email}")
    return {"message": "Notification sent"}

# Multiple background tasks
def send_email(email: str, message: str):
    print(f"Sending email to {email}: {message}")

def log_activity(activity: str):
    print(f"Logging: {activity}")

@app.post("/process/")
async def process_data(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Processing complete")
    background_tasks.add_task(log_activity, f"Processed data for {email}")
    return {"message": "Processing started"}
```

### Advanced Background Tasks
```python
from typing import Any
import asyncio

class BackgroundTaskManager:
    def __init__(self):
        self.tasks = []

    async def process_item(self, item_id: int):
        await asyncio.sleep(5)  # Simulate processing
        print(f"Processed item {item_id}")

    def add_task(self, coro):
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return task

task_manager = BackgroundTaskManager()

@app.post("/items/{item_id}/process")
async def process_item(item_id: int):
    task = task_manager.add_task(
        task_manager.process_item(item_id)
    )
    return {
        "message": "Processing started",
        "task_id": id(task)
    }

@app.get("/tasks/status")
async def get_tasks_status():
    return {
        "total_tasks": len(task_manager.tasks),
        "completed": sum(1 for t in task_manager.tasks if t.done()),
        "pending": sum(1 for t in task_manager.tasks if not t.done())
    }
```

## WebSockets

### Basic WebSocket
```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head><title>WebSocket Test</title></head>
<body>
    <h1>WebSocket Test</h1>
    <form action="" onsubmit="sendMessage(event)">
        <input type="text" id="messageText" autocomplete="off"/>
        <button>Send</button>
    </form>
    <ul id='messages'></ul>
    <script>
        var ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = function(event) {
            var messages = document.getElementById('messages')
            var message = document.createElement('li')
            message.innerHTML = event.data
            messages.appendChild(message)
        };
        function sendMessage(event) {
            var input = document.getElementById("messageText")
            ws.send(input.value)
            input.value = ''
            event.preventDefault()
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

### WebSocket with Multiple Clients
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(
                f"You wrote: {data}", websocket
            )
            await manager.broadcast(
                f"Client #{client_id} says: {data}"
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
```

## CORS

### CORS Configuration
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Specific CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-Custom-Header"],
    max_age=3600,
)

# Dynamic CORS
def get_allowed_origins():
    # Load from database or config
    return ["https://app1.com", "https://app2.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing

### Unit Testing with pytest
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# Test file (test_main.py)
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_read_item():
    response = client.get("/items/42?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "test"}

def test_read_item_no_query():
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": None}

# Testing with authentication
def test_protected_route():
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer fake-token"}
    )
    assert response.status_code == 401
```

### Async Testing
```python
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

app = FastAPI()

@app.get("/async")
async def async_endpoint():
    return {"message": "async"}

# Async test
@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/async")
    assert response.status_code == 200
    assert response.json() == {"message": "async"}

# Testing with database
@pytest.fixture
async def test_db():
    # Setup test database
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    # Cleanup
    await test_engine.dispose()

@pytest.mark.asyncio
async def test_create_item(test_db):
    item_data = {"name": "Test", "price": 10.5}
    # Test with test_db session
    pass
```

### Testing WebSockets
```python
from fastapi.testclient import TestClient

def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert data == "Message: Hello"

def test_websocket_disconnect():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Hello")
        websocket.close()
    # Assert cleanup happened
```

## OpenAPI Documentation

### Customizing OpenAPI
```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom API",
        version="2.5.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Customizing documentation URLs
app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Disabling documentation
app = FastAPI(docs_url=None, redoc_url=None)
```

### API Metadata
```python
from fastapi import FastAPI

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users",
        "externalDocs": {
            "description": "External docs",
            "url": "https://example.com/docs/users",
        },
    },
    {
        "name": "items",
        "description": "Manage items",
    },
]

app = FastAPI(
    title="My API",
    description="API with metadata",
    version="1.0.0",
    openapi_tags=tags_metadata,
    servers=[
        {"url": "https://api.example.com", "description": "Production"},
        {"url": "https://staging-api.example.com", "description": "Staging"},
    ],
)

@app.get("/users/", tags=["users"])
async def get_users():
    return [{"username": "user1"}]

@app.get("/items/", tags=["items"])
async def get_items():
    return [{"name": "item1"}]
```

## Deployment

### Production Configuration
```python
# main.py
from fastapi import FastAPI
import uvicorn
from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"
    debug: bool = False
    database_url: str
    secret_key: str
    allowed_hosts: list = ["*"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

app = FastAPI(title=get_settings().app_name)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=get_settings().debug,
        workers=4,
        log_level="info"
    )
```

### Gunicorn Configuration
```python
# gunicorn_conf.py
import multiprocessing

# Gunicorn config
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Run with: gunicorn main:app -c gunicorn_conf.py
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Multi-stage build
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Advanced Features

### Middleware
```python
from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time

app = FastAPI()

# Built-in middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    print(f"Request: {request.method} {request.url}")
    print(f"Body: {body}")
    response = await call_next(request)
    return response
```

### Event Handlers
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    print("Starting up...")
    await setup_database()
    await load_ml_model()
    
    yield
    
    # Shutdown events
    print("Shutting down...")
    await close_database()
    await cleanup_resources()

app = FastAPI(lifespan=lifespan)

# Alternative syntax (deprecated but still supported)
@app.on_event("startup")
async def startup_event():
    print("Starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
```

### Sub Applications
```python
from fastapi import FastAPI

# Main application
app = FastAPI()

# Sub application
subapi = FastAPI()

@subapi.get("/sub/")
async def read_sub():
    return {"message": "Hello from sub API"}

# Mount sub application
app.mount("/subapi", subapi)

# Multiple sub applications
admin_api = FastAPI()
public_api = FastAPI()

app.mount("/admin", admin_api)
app.mount("/api", public_api)
```

### GraphQL Integration
```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def hello(self, name: str = "World") -> str:
        return f"Hello {name}"

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_user(self, name: str) -> str:
        # Add user logic
        return f"Added user: {name}"

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

## Best Practices

### Project Structure
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── crud/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── users.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   └── db/
│       ├── __init__.py
│       └── database.py
├── tests/
│   ├── __init__.py
│   └── test_users.py
├── alembic/
├── requirements.txt
├── .env
└── docker-compose.yml
```

### Error Handling
```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

# Custom exception
class CustomException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Error: {exc.name}"}
    )

# Override default handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "custom": "error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )
```

### Performance Optimization
```python
from fastapi import FastAPI
from functools import lru_cache
import aioredis
from typing import Optional

app = FastAPI()

# Caching
@lru_cache(maxsize=128)
def expensive_computation(param: str):
    # Expensive operation
    return result

# Redis caching
redis = None

@app.on_event("startup")
async def startup():
    global redis
    redis = await aioredis.create_redis_pool("redis://localhost")

async def get_cached_data(key: str) -> Optional[str]:
    if redis:
        return await redis.get(key)
    return None

async def set_cached_data(key: str, value: str, expire: int = 3600):
    if redis:
        await redis.setex(key, expire, value)

# Response caching
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/cached/")
@cache(expire=60)
async def get_cached_endpoint():
    return {"data": "This will be cached for 60 seconds"}
```

## Common Patterns

### Pagination
```python
from fastapi import FastAPI, Query
from typing import List, Optional

app = FastAPI()

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int

@app.get("/items/", response_model=PaginatedResponse)
async def get_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get items from database
    query = db.query(Item)
    if search:
        query = query.filter(Item.name.contains(search))
    
    total = query.count()
    items = query.offset(offset).limit(per_page).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )
```

### Rate Limiting
```python
from fastapi import FastAPI, Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/limited/")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "This endpoint is rate limited"}

# Custom rate limiting
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int, window: timedelta):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        now = datetime.now()
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window
        ]
        # Check limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        return False

rate_limiter = RateLimiter(max_requests=10, window=timedelta(minutes=1))

@app.get("/custom-limited/")
async def custom_limited(request: Request):
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return {"message": "Success"}
```

### File Handling
```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
import aiofiles
from typing import List
import os

app = FastAPI()

# File upload
@app.post("/upload/")
async def upload_file(file: UploadFile):
    # Save file
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    return {"filename": file.filename, "size": len(content)}

# Multiple file upload
@app.post("/upload-multiple/")
async def upload_multiple(files: List[UploadFile]):
    results = []
    for file in files:
        content = await file.read()
        # Process file
        results.append({"filename": file.filename, "size": len(content)})
    return results

# File download
@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = f"files/{file_name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type='application/octet-stream'
    )

# Streaming large files
@app.get("/stream/{file_name}")
async def stream_file(file_name: str):
    file_path = f"files/{file_name}"
    
    async def iterfile():
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(1024 * 1024):  # 1MB chunks
                yield chunk
    
    return StreamingResponse(
        iterfile(),
        media_type='application/octet-stream',
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )
```

### Health Checks
```python
from fastapi import FastAPI, status
from datetime import datetime
import psutil

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "my-api"
    }

@app.get("/health/detailed")
async def detailed_health():
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Check system resources
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": db_status,
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory.percent}%",
            "disk_usage": f"{psutil.disk_usage('/').percent}%"
        }
    }

@app.get("/ready")
async def readiness_check():
    # Check if service is ready to accept traffic
    if not app.state.ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
    return {"ready": True}
```

## Conclusion

FastAPI is a powerful, modern web framework that combines the best of Python's type hints with high performance and automatic documentation generation. Its intuitive design, comprehensive feature set, and excellent performance make it an ideal choice for building production-ready APIs.

Key takeaways:
- Leverage Python type hints for automatic validation and documentation
- Use async/await for high-performance concurrent operations
- Take advantage of automatic OpenAPI documentation
- Implement proper security and authentication mechanisms
- Follow best practices for project structure and error handling
- Optimize performance with caching and proper database usage
- Test thoroughly with FastAPI's excellent testing support

Whether you're building a simple REST API or a complex microservices architecture, FastAPI provides the tools and flexibility needed to create robust, scalable, and maintainable applications.