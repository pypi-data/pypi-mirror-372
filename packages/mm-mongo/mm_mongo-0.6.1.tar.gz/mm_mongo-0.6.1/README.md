# mm-mongo

Type-safe PyMongo wrapper with Pydantic integration.

## Quick Start

### Define Models

```python
from mm_mongo import MongoModel
from bson import ObjectId

class User(MongoModel[ObjectId]):
    __collection__ = "users"
    __indexes__ = ["email", "!username"]  # email ascending, username unique

    name: str
    email: str
    username: str
    age: int
```

### Sync Usage

```python
from mm_mongo import MongoConnection, MongoCollection

# Connect
connection = MongoConnection("mongodb://localhost/mydb")
users = MongoCollection.init(connection.database, User)

# CRUD operations
user = User(id=ObjectId(), name="John", email="john@example.com", username="john", age=30)
result = users.insert_one(user)

user = users.get(result.inserted_id)
users.update(user.id, {"$set": {"age": 31}})
users.delete(user.id)
```

### Async Usage

```python
from mm_mongo import AsyncMongoConnection, AsyncMongoCollection

# Connect
connection = AsyncMongoConnection("mongodb://localhost/mydb")
users = await AsyncMongoCollection.init(connection.database, User)

# CRUD operations
user = User(id=ObjectId(), name="John", email="john@example.com", username="john", age=30)
result = await users.insert_one(user)

user = await users.get(result.inserted_id)
await users.update(user.id, {"$set": {"age": 31}})
await users.delete(user.id)
```

## Features

- **Type Safety**: Full generic type support with mypy compatibility
- **Pydantic Integration**: Automatic validation and serialization
- **Sync & Async**: Both synchronous and asynchronous APIs
- **Schema Validation**: MongoDB schema validation support
- **Index Management**: Automatic index creation with string shortcuts
- **ObjectId Support**: Seamless BSON ObjectId integration

## Model Configuration

```python
class Product(MongoModel[str]):
    __collection__ = "products"

    # Index formats:
    # "field" - ascending, "-field" - descending, "!field" - unique
    # "!field1:-field2:field3" - compound index with colon separators
    __indexes__ = ["name", "!sku", "-created_at", "!category:-price:name"]

    # MongoDB schema validation
    __validator__ = {
        "$jsonSchema": {
            "required": ["name", "price"],
            "properties": {"price": {"minimum": 0}}
        }
    }

    name: str
    sku: str
    price: float
    category: str
```

## Index String Format

- `"field"` - ascending index
- `"-field"` - descending index
- `"!field"` - unique ascending index
- `"!field1:-field2:field3"` - unique compound index (colon separators only)

Example:
```python
__indexes__ = ["name", "!sku", "-created_at", "!category:-price:name"]
```
