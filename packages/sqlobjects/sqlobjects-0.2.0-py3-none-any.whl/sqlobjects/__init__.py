"""SQLObjects - Django-style async ORM library built on SQLAlchemy Core

A modern, async-first ORM library that provides Django-style APIs while leveraging
the power and performance of SQLAlchemy Core.

Core Features:
- Django-style chainable queries with Q objects
- Async-first design with SQLAlchemy Core
- Multi-database support with connection management
- Comprehensive validation system
- Signal system for model lifecycle events
- Type-safe field definitions with shortcuts

Examples:
    >>> from sqlobjects import ObjectModel
    >>> from sqlobjects.database import init_db, create_tables
    >>> from sqlobjects.fields import str_column, int_column
    >>> # Initialize database
    >>> db = await init_db("sqlite+aiosqlite:///test.db")
    >>> # Define model
    >>> class User(ObjectModel):
    ...     name: str = str_column(length=50)
    ...     age: int = int_column()
    >>> # Create tables
    >>> await db.create_tables(ObjectModel)
    >>> # Use the model
    >>> user = await User.objects.create(name="John", age=25)
"""

from .model import ObjectModel
from .queries import Q


__version__ = "2.0.0"
__all__ = [
    "ObjectModel",
    "Q",
]
