# Repository Core

A powerful and flexible base repository and service utilities package for SQLAlchemy-backed FastAPI applications.

## Overview

Repository Core provides a set of base classes and utilities to help you implement clean and maintainable repository and service patterns in your FastAPI applications. It's designed to work seamlessly with SQLAlchemy and follows best practices for database operations and business logic separation.

## Features

- Base repository classes for common CRUD operations
- Service layer abstractions for business logic
- SQLAlchemy model utilities
- Exceptions
- Schema validation
- Utility functions for common operations

## Installation

```bash
pip install repository-core
```

## Requirements

- Python >= 3.13
- FastAPI >= 0.115.2
- SQLAlchemy >= 2.0.40

## Usage Guide

### 1. Setting Up Base Models

```python
from repository_core.models import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
```

### 2. Creating a Repository

```python
from repository_core.repository import BaseRepository
from repository_core.models import BaseModel

class UserRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, User) #Access all the methods of base-repository
    
    # Add custom repository methods here
    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_one(User.email == email)
```

### 3. Implementing a Service

```python
from repository_core.services import BaseService

class UserService(BaseService):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
    
    # Add custom service methods here
    async def create_user(self, data: UserCreate) -> User:
        return await self.create(data)
```

## Project Structure

```
repository_core/
├── models/         # Base model classes
├── repository/     # Base repository implementations
├── services/       # Base service implementations
├── schemas/        # Pydantic schemas
├── exceptions/     # Custom exceptions
└── utils/          # Utility functions
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.



