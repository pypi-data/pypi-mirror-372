"""SQLObjects Objects Manager - Core-based Database Operations

This module provides Django-style objects manager for database operations
using SQLAlchemy Core, offering high-performance database access with
familiar ORM-like interface.
"""

from typing import Any, Generic, Literal

from sqlalchemy import bindparam, delete, insert, select, text, update

from .exceptions import DoesNotExist, MultipleObjectsReturned
from .queries import QuerySet, T
from .session import AsyncSession, SessionContextManager
from .signals import Operation, emit_signals


__all__ = ["ObjectsDescriptor", "ObjectsManager"]


class ObjectsDescriptor(Generic[T]):
    """Descriptor that provides Django-style objects attribute for model classes.

    This descriptor is automatically attached to model classes to provide the
    'objects' attribute that returns an ObjectsManager instance for database operations.
    It implements the descriptor protocol to ensure each model class gets its own
    manager instance.
    """

    def __init__(self, model_class: type[T]) -> None:
        """Initialize the descriptor with the model class.

        Args:
            model_class: The model class this descriptor is attached to
        """
        self._model_class = model_class

    def __get__(self, obj: Any, owner: type[T]) -> "ObjectsManager[T]":
        """Return an ObjectsManager instance for the model class.

        This method is called when accessing the 'objects' attribute on a model class.

        Args:
            obj: The instance accessing the attribute (None for class access)
            owner: The class that owns this descriptor

        Returns:
            ObjectsManager instance configured for the model class
        """
        return ObjectsManager(self._model_class)


class ObjectsManager(Generic[T]):
    """Object manager providing Django ORM-like interface using SQLAlchemy Core.

    This manager provides a familiar Django-style API for database operations
    while leveraging SQLAlchemy Core for optimal performance. It supports
    session management, query building, and bulk operations.
    """

    def __init__(self, model_class: type[T], db_or_session: str | AsyncSession | None = None):
        """Initialize the objects manager.

        Args:
            model_class: The model class this manager operates on
            db_or_session: Optional database name or session to use
        """
        self._model_class = model_class
        self._table = model_class.get_table()  # type: ignore[reportAttributeAccessIssue]
        self._db_or_session = db_or_session

    # ========================================
    # 1. Internal Helper Methods
    # ========================================

    def _get_session(self, readonly: bool = True) -> AsyncSession:
        """Get database session with explicit readonly parameter.

        Args:
            readonly: Whether the session is for read-only operations

        Returns:
            AsyncSession instance
        """
        if self._db_or_session is None:
            return SessionContextManager.get_session(readonly=readonly)
        elif isinstance(self._db_or_session, str):
            return SessionContextManager.get_session(self._db_or_session, readonly=readonly)
        else:
            return self._db_or_session

    def _validate_field_names(self, **kwargs) -> None:
        """Validate that all field names exist on the model.

        Args:
            **kwargs: Field names to validate

        Raises:
            AttributeError: If any field name doesn't exist on the model
        """
        table_fields = set(self._table.columns.keys())
        for field_name in kwargs.keys():
            if field_name not in table_fields:
                raise AttributeError(f"'{self._model_class.__name__}' has no field '{field_name}'")

    # ========================================
    # 2. Session Management Methods
    # ========================================

    def using(self, db_or_session: str | AsyncSession) -> "ObjectsManager[T]":
        """Create a new manager instance using the specified database or session.

        Args:
            db_or_session: Database name or AsyncSession instance

        Returns:
            New ObjectsManager instance bound to the specified database/session
        """
        return ObjectsManager(self._model_class, db_or_session)

    # ========================================
    # 3. Query Building Methods - Return QuerySet
    # ========================================

    def filter(self, *args) -> QuerySet[T]:
        """Filter objects using Q objects SQLAlchemy expressions and keyword arguments.

        Args:
            *args: Q objects or SQLAlchemy expressions for complex conditions

        Returns:
            QuerySet with filter conditions applied
        """
        return QuerySet(self._table, self._model_class, db_or_session=self._db_or_session).filter(*args)

    def defer(self, *fields) -> QuerySet[T]:
        """Defer loading of specified fields until accessed.

        Args:
            *fields: Field names to defer (supports strings and field expressions)

        Returns:
            QuerySet with deferred fields
        """
        return QuerySet(self._table, self._model_class, db_or_session=self._db_or_session).defer(*fields)

    def annotate(self, *args, **kwargs) -> QuerySet[T]:
        """Add annotation fields to the query.

        Args:
            *args: Positional annotation expressions with auto-generated aliases
            **kwargs: Named annotation expressions with custom aliases

        Returns:
            QuerySet with annotation fields added
        """
        return self.filter().annotate(*args, **kwargs)

    def group_by(self, *fields) -> QuerySet[T]:
        """Add GROUP BY clause to the query.

        Args:
            *fields: Field names, field expressions, or SQLAlchemy expressions for grouping

        Returns:
            QuerySet with GROUP BY clause applied
        """
        return self.filter().group_by(*fields)

    def having(self, *conditions) -> QuerySet[T]:
        """Add HAVING clause for grouped queries.

        Args:
            *conditions: SQLAlchemy expressions for HAVING conditions

        Returns:
            QuerySet with HAVING conditions applied
        """
        return self.filter().having(*conditions)

    def join(self, target_table, on_condition, join_type: str = "inner") -> QuerySet[T]:
        """Perform manual JOIN with another table.

        Args:
            target_table: Table to join with
            on_condition: JOIN condition expression
            join_type: Type of join ('inner', 'left', 'outer')

        Returns:
            QuerySet with JOIN applied
        """
        return self.filter().join(target_table, on_condition, join_type)

    def leftjoin(self, target_table, on_condition) -> QuerySet[T]:
        """Perform LEFT JOIN with another table.

        Args:
            target_table: Table to join with
            on_condition: JOIN condition expression

        Returns:
            QuerySet with LEFT JOIN applied
        """
        return self.filter().leftjoin(target_table, on_condition)

    def outerjoin(self, target_table, on_condition) -> QuerySet[T]:
        """Perform OUTER JOIN with another table.

        Args:
            target_table: Table to join with
            on_condition: JOIN condition expression

        Returns:
            QuerySet with OUTER JOIN applied
        """
        return self.filter().outerjoin(target_table, on_condition)

    def select_for_update(self, nowait: bool = False, skip_locked: bool = False) -> QuerySet[T]:
        """Apply row-level locking using FOR UPDATE.

        Args:
            nowait: Don't wait if rows are locked by another transaction
            skip_locked: Skip locked rows instead of waiting

        Returns:
            QuerySet with FOR UPDATE locking applied
        """
        return self.filter().select_for_update(nowait, skip_locked)

    def select_for_share(self, nowait: bool = False, skip_locked: bool = False) -> QuerySet[T]:
        """Apply shared row-level locking using FOR SHARE.

        Args:
            nowait: Don't wait if rows are locked by another transaction
            skip_locked: Skip locked rows instead of waiting

        Returns:
            QuerySet with FOR SHARE locking applied
        """
        return self.filter().select_for_share(nowait, skip_locked)

    def extra(self, columns=None, where=None, params=None) -> QuerySet[T]:
        """Add extra SQL fragments to the query.

        Args:
            columns: Extra columns to add to SELECT clause
            where: Extra WHERE conditions as raw SQL strings
            params: Parameters for extra SQL fragments

        Returns:
            QuerySet with extra SQL fragments added
        """
        return self.filter().extra(columns, where, params)

    def no_cache(self) -> QuerySet[T]:
        """Return QuerySet that skips cache for this operation.

        Returns:
            QuerySet with caching disabled
        """
        return self.filter().no_cache()

    def skip_default_ordering(self) -> QuerySet[T]:
        """Return QuerySet that skips applying default ordering.

        Returns:
            QuerySet without default ordering applied
        """
        return self.filter().skip_default_ordering()

    def subquery(self, name: str | None = None, query_type: Literal["auto", "table", "scalar", "exists"] = "auto"):
        """Convert current QuerySet to subquery expression.

        Args:
            name: Optional name for the subquery
            query_type: Type of subquery ('auto', 'table', 'scalar', 'exists')

        Returns:
            SubqueryExpression that can be used in other queries
        """
        return self.filter().subquery(name, query_type)

    # ========================================
    # 4. Query Execution Methods - Execute queries and return results
    # ========================================

    # Basic execution methods

    async def all(self) -> list[T]:
        """Get all objects of this model.

        Returns:
            List of all model instances
        """
        return await self.filter().all()

    async def get(self, *args) -> T:
        """Get a single object matching the given conditions.

        Args:
            *args: Q objects or SQLAlchemy expressions for complex conditions

        Returns:
            Single model instance

        Raises:
            DoesNotExist: If no object matches the conditions
            MultipleObjectsReturned: If multiple objects match the conditions
            ValidationError: If field lookup conditions are invalid
            DatabaseError: If database connection or query execution fails
            AttributeError: If specified field names don't exist on the model

        Examples:
            # Basic usage with default session
            user = await User.objects.get(User.username=="john")

            # Using specific database session
            user = await User.objects.using(analytics_session).get(User.username=="john")

            # Complex query with session
            user = await User.objects.using(analytics_session).get(
                Q(User.username=="john", User.email=="john@example.com")
            )
        """
        results = await self.filter(*args).limit(2).all()
        if not results:
            raise DoesNotExist(f"{self._model_class.__name__} matching query does not exist")
        if len(results) > 1:
            raise MultipleObjectsReturned(f"Multiple {self._model_class.__name__} objects returned")
        return results[0]

    async def exists(self) -> bool:
        """Check if any objects exist in the database.

        Returns:
            True if any objects exist, False otherwise
        """
        return await self.filter().exists()

    async def raw(self, sql: str, params: dict | None = None) -> list[T]:
        """Execute raw SQL query and return model instances.

        Args:
            sql: Raw SQL query string
            params: Optional parameters for the SQL query

        Returns:
            List of model instances created from query results
        """
        return await self.filter().raw(sql, params)

    async def first(self) -> T | None:
        """Get the first object according to the default ordering.

        Returns:
            First model instance or None if no objects exist
        """
        return await self.filter().first()

    async def last(self) -> T | None:
        """Get the last object according to the default ordering.

        Returns:
            Last model instance or None if no objects exist
        """
        return await self.filter().last()

    # Ordering-related execution methods

    async def earliest(self, *fields) -> T | None:
        """Get the earliest object by specified fields.

        Args:
            *fields: Field names to order by (supports strings and field expressions)

        Returns:
            Earliest model instance or None if no objects exist
        """
        if not fields:
            fields = ["id"]
        return await self.filter().earliest(*fields)

    async def latest(self, *fields) -> T | None:
        """Get the latest object by specified fields.

        Args:
            *fields: Field names to order by (supports strings and field expressions)

        Returns:
            Latest model instance or None if no objects exist
        """
        if not fields:
            fields = ["id"]
        return await self.filter().latest(*fields)

    # Data extraction methods

    async def values(self, *fields) -> list[dict[str, Any]]:
        """Get dictionaries of field values.

        Args:
            *fields: Field names to include (supports strings and field expressions)

        Returns:
            List of dictionaries with field values
        """
        return await self.filter().values(*fields)

    async def values_list(self, *fields, flat: bool = False) -> list:
        """Get tuples or flat list of field values.

        Args:
            *fields: Field names to include (supports strings and field expressions)
            flat: If True and single field, return flat list

        Returns:
            List of tuples or flat list of values
        """
        return await self.filter().values_list(*fields, flat=flat)

    async def dates(self, field, kind: str, order: str = "ASC") -> list[Any]:
        """Get list of dates for a field.

        Args:
            field: Field name to extract dates from (supports strings and field expressions)
            kind: Date part to extract ('year', 'month', 'day')
            order: Sort order ('ASC' or 'DESC')

        Returns:
            List of date values
        """
        return await self.filter().dates(field, kind, order)

    async def datetimes(self, field, kind: str, order: str = "ASC") -> list[Any]:
        """Get list of datetimes for a field.

        Args:
            field: Field name to extract datetimes from (supports strings and field expressions)
            kind: Datetime part to extract ('year', 'month', 'day', 'hour')
            order: Sort order ('ASC' or 'DESC')

        Returns:
            List of datetime values
        """
        return await self.filter().datetimes(field, kind, order)

    # Advanced execution methods

    async def iterator(self, chunk_size: int = 1000):
        """Async iterator for large datasets.

        Args:
            chunk_size: Number of objects to fetch per chunk

        Yields:
            Model instances one by one
        """
        async for obj in self.filter().iterator(chunk_size):
            yield obj

    async def get_item(self, key) -> T | list[T]:
        """Get item by index or slice.

        Args:
            key: Integer index or slice object

        Returns:
            Single model instance for index, list for slice
        """
        return await self.filter().get_item(key)

    # ========================================
    # 5. Data Operations Methods - Create and modify data
    # ========================================

    # Creation operations

    async def get_or_create(
        self, defaults: dict[str, Any] | None = None, validate: bool = True, **lookup
    ) -> tuple[T, bool]:
        """Get an existing object or create a new one if it doesn't exist.

        Args:
            defaults: Additional values to use when creating a new object
            validate: Whether to validate when creating
            **lookup: Field lookup conditions (only equality supported)

        Returns:
            Tuple of (object, created) where created is True if object was created

        Raises:
            AttributeError: If specified field names don't exist on the model
            ValidationError: If validation fails during creation
            IntegrityError: If database constraints are violated

        Examples:
            # Simple field lookup
            user, created = await User.objects.get_or_create(
                username="john",
                defaults={"email": "john@example.com"}
            )

            # Multiple conditions
            user, created = await User.objects.get_or_create(
                username="john",
                is_active=True,
                defaults={"email": "john@example.com"}
            )

            # Using specific session
            user, created = await User.objects.using(session).get_or_create(
                username="john",
                defaults={"email": "john@example.com"}
            )
        """
        if not lookup:
            raise ValueError("get_or_create requires at least one lookup field")

        # Validate field names
        self._validate_field_names(**lookup)
        if defaults:
            self._validate_field_names(**defaults)

        try:
            # Try to get existing object
            conditions = [self._table.c[field] == value for field, value in lookup.items()]
            obj = await self.filter(*conditions).get()
            return obj, False
        except DoesNotExist:
            # Create new object with lookup fields + defaults
            create_data = lookup.copy()
            if defaults:
                # defaults override lookup values if there's conflict
                create_data.update(defaults)

            # Create instance and use save() method to trigger signals
            obj = self._model_class.from_dict(create_data, validate=False)  # type: ignore[reportAttributeAccessIssue]
            await obj.using(self._get_session(readonly=False)).save(validate=validate)
            return obj, True

    async def update_or_create(
        self, defaults: dict[str, Any] | None = None, validate: bool = True, **lookup
    ) -> tuple[T, bool]:
        """Update an existing object or create a new one if it doesn't exist.

        Args:
            defaults: Values to update/set when object exists or is created
            validate: Whether to validate when updating/creating
            **lookup: Field lookup conditions (only equality supported)

        Returns:
            Tuple of (object, created) where created is True if object was created

        Raises:
            AttributeError: If specified field names don't exist on the model
            ValidationError: If validation fails during update/creation
            IntegrityError: If database constraints are violated

        Examples:
            # Simple field lookup
            user, created = await User.objects.update_or_create(
                username="john",
                defaults={"last_login": datetime.now()}
            )

            # Multiple conditions
            user, created = await User.objects.update_or_create(
                username="john",
                is_active=True,
                defaults={"last_login": datetime.now()}
            )

            # Using specific session
            user, created = await User.objects.using(session).update_or_create(
                username="john",
                defaults={"last_login": datetime.now()}
            )
        """
        if not lookup:
            raise ValueError("update_or_create requires at least one lookup field")

        # Validate field names
        self._validate_field_names(**lookup)
        if defaults:
            self._validate_field_names(**defaults)

        try:
            # Try to get existing object
            conditions = [self._table.c[field] == value for field, value in lookup.items()]
            obj = await self.filter(*conditions).get()

            # Update existing object with defaults using save() method
            if defaults:
                for key, value in defaults.items():
                    setattr(obj, key, value)
                await obj.using(self._get_session(readonly=False)).save(validate=validate)  # type: ignore[reportAttributeAccessIssue]

            return obj, False
        except DoesNotExist:
            # Create new object with lookup fields + defaults
            create_data = lookup.copy()
            if defaults:
                # defaults override lookup values if there's conflict
                create_data.update(defaults)

            # Create instance and use save() method to trigger signals
            obj = self._model_class.from_dict(create_data, validate=False)  # type: ignore[reportAttributeAccessIssue]
            await obj.using(self._get_session(readonly=False)).save(validate=validate)
            return obj, True

    async def in_bulk(self, id_list: list[Any] | None = None, field_name: str = "pk") -> dict[Any, T]:
        """Get multiple objects as a dictionary mapping field values to objects.

        This method is useful for efficiently retrieving multiple objects when you
        have a list of identifiers and want to access them by their field values.

        Args:
            id_list: List of values to match against the specified field
            field_name: Name of the field to use as dictionary keys ('pk' for primary key)

        Returns:
            Dictionary mapping field values to model instances
        """
        if field_name == "pk":
            pk_columns = list(self._table.primary_key.columns)
            actual_field = pk_columns[0].name if pk_columns else "id"
        else:
            actual_field = field_name

        queryset = self.filter()
        if id_list is not None:
            field_column = self._table.c[actual_field]
            queryset = queryset.filter(field_column.in_(id_list))

        objects = await queryset.all()
        return {getattr(obj, actual_field): obj for obj in objects}

    # Update and delete operations

    @emit_signals(Operation.SAVE)
    async def create(self, validate: bool = True, **kwargs) -> T:
        """Create a new object with the given field values.

        Args:
            validate: Whether to execute all validation (both SQLObjects and SQLAlchemy validators)
            **kwargs: Field values for the new object

        Returns:
            Created model instance

        Raises:
            ValidationError: If validation fails during creation
            IntegrityError: If database constraints are violated (unique, foreign key, etc.)
            DatabaseError: If database connection or transaction fails
            TypeError: If invalid field names or values are provided
            AttributeError: If specified field names don't exist on the model
        """
        try:
            obj = self._model_class.from_dict(kwargs, validate=False)  # type: ignore[reportAttributeAccessIssue]
            # Execute database operation directly, don't call obj.save() to avoid duplicate signals
            if validate:
                obj.validate_all_fields()

            stmt = insert(self._table).values(**obj._get_all_data())  # noqa
            session = self._get_session(readonly=False)
            result = await session.execute(stmt)

            # Set primary key values from result
            if result.inserted_primary_key:
                obj._set_primary_key_values(result.inserted_primary_key)  # noqa

            # Session auto-commits with auto_commit=True
            return obj
        except Exception as e:
            raise RuntimeError(f"Failed to create {self._model_class.__name__}: {e}") from e

    @emit_signals(Operation.SAVE, is_bulk=True)
    async def bulk_create(self, objects: list[dict[str, Any]]) -> None:
        """Create multiple objects for better performance.

        Args:
            objects: List of dictionaries containing object data
        """
        if not objects:
            return

        stmt = insert(self._table).values(objects)
        session = self._get_session(readonly=False)
        await session.execute(stmt)

    # Aggregation and statistics

    @emit_signals(Operation.SAVE, is_bulk=True)
    async def bulk_update(
        self, mappings: list[dict[str, Any]], match_fields: list[str] | None = None, batch_size: int = 1000
    ) -> int:
        """Perform true bulk update operations for better performance.

        Args:
            mappings: List of dictionaries containing match fields and update values
            match_fields: Fields to use for matching records (defaults to ["id"])
            batch_size: Number of records to process in each batch

        Returns:
            Total number of affected rows

        Raises:
            ValidationError: If mappings is empty or invalid
            IntegrityError: If database constraints are violated during update
            DatabaseError: If database connection or transaction fails
        """
        if not mappings:
            raise ValueError("Bulk update requires non-empty mappings list")

        if match_fields is None:
            match_fields = ["id"]

        total_affected = 0

        # Process in batches using Core-level update
        for i in range(0, len(mappings), batch_size):
            batch = mappings[i : i + batch_size]

            # Build WHERE conditions using match_fields
            where_conditions = []
            for field in match_fields:
                where_conditions.append(self._table.c[field] == bindparam(f"match_{field}"))

            # Create Core-level update statement
            stmt = update(self._table).where(*where_conditions)

            # Add update values (exclude match fields from values)
            update_values = {}
            for key in batch[0].keys():
                if key not in match_fields:
                    update_values[key] = bindparam(f"update_{key}")

            if update_values:
                stmt = stmt.values(**update_values)

                # Prepare parameter mappings
                param_mappings = []
                for mapping in batch:
                    param_dict = {}
                    # Add match field parameters
                    for field in match_fields:
                        param_dict[f"match_{field}"] = mapping[field]
                    # Add update value parameters
                    for key, value in mapping.items():
                        if key not in match_fields:
                            param_dict[f"update_{key}"] = value
                    param_mappings.append(param_dict)

                # Execute bulk update directly with session
                session = self._get_session(readonly=False)
                result = await session.execute(stmt, param_mappings)
                total_affected += result.rowcount if result.rowcount is not None else 0

        # Session auto-commits with auto_commit=True
        return total_affected

    @emit_signals(Operation.DELETE, is_bulk=True)
    async def bulk_delete(self, ids: list[Any], id_field: str = "id", batch_size: int = 1000) -> int:
        """Perform true bulk delete operations for better performance.

        Args:
            ids: List of IDs to delete
            id_field: Field name to use for matching (defaults to "id")
            batch_size: Number of records to process in each batch

        Returns:
            Total number of deleted rows

        Raises:
            ValidationError: If ids list is empty
            IntegrityError: If foreign key constraints prevent deletion
            DatabaseError: If database connection or transaction fails
        """
        if not ids:
            raise ValueError("Bulk delete requires non-empty ids list")

        total_affected = 0

        # Process in batches using IN clause
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]

            # Create delete statement with IN clause
            stmt = delete(self._table).where(self._table.c[id_field].in_(batch_ids))
            session = self._get_session(readonly=False)
            result = await session.execute(stmt)
            total_affected += result.rowcount if result.rowcount is not None else 0

        # Session auto-commits with auto_commit=True
        return total_affected

    async def delete_all(self, fast: bool = False) -> int:
        """Delete all records from the table.

        Args:
            fast: Whether to use TRUNCATE for fast deletion
                 Note: TRUNCATE doesn't support transaction rollback and doesn't trigger signals
                 Use with caution in production environments

        Returns:
            Number of deleted rows (-1 for TRUNCATE as it cannot return accurate count)
        """
        if fast:
            # Use TRUNCATE for maximum performance on large tables
            # Warning: This bypasses transaction safety and signal triggering
            table_name = self._table.name
            session = self._get_session(readonly=False)
            await session.execute(text(f"TRUNCATE TABLE {table_name}"))
            return -1  # TRUNCATE cannot return accurate row count
        else:
            # Use QuerySet.delete() for transaction safety and signal support
            return await self.filter().delete()

    async def update_all(self, **values) -> int:
        """Update all records in the table with the given values.

        Args:
            **values: Field values to update

        Returns:
            Number of updated rows

        Examples:
            # Update all users' status
            affected = await User.objects.update_all(status="migrated")
        """
        return await self.filter().update(**values)

    # QuerySet shortcut methods

    async def count(self) -> int:
        """Count the total number of objects.

        Returns:
            Total number of objects
        """
        return await self.filter().count()

    async def aggregate(self, **kwargs) -> dict[str, Any]:
        """Perform aggregation operations on the queryset.

        Args:
            **kwargs: Aggregation expressions with their aliases

        Returns:
            Dictionary with aggregation results
        """
        aggregations = []
        labels = []

        for alias, expr in kwargs.items():
            if hasattr(expr, "resolve"):
                # SQLObjects function
                aggregations.append(expr.resolve(self._table).label(alias))
            else:
                aggregations.append(expr.label(alias))
            labels.append(alias)

        query = select(*aggregations).select_from(self._table)
        session = self._get_session(readonly=True)
        result = await session.execute(query)
        first_result = result.first()
        return dict(zip(labels, first_result, strict=False)) if first_result else {}

    def distinct(self, *fields) -> QuerySet[T]:
        """Apply DISTINCT clause to eliminate duplicate rows.

        Args:
            *fields: Field names, field expressions to apply DISTINCT on, if empty applies to all

        Returns:
            QuerySet with DISTINCT applied
        """
        return self.filter().distinct(*fields)

    def exclude(self, *args) -> QuerySet[T]:
        """Exclude objects matching the given conditions.

        Args:
            *args: Q objects or SQLAlchemy expressions for complex conditions

        Returns:
            QuerySet with exclusion conditions applied
        """
        return self.filter().exclude(*args)

    def order_by(self, *fields) -> QuerySet[T]:
        """Order results by the specified fields.

        Args:
            *fields: Field names, field expressions, or SQLAlchemy expressions
                    (prefix string fields with '-' for descending order)

        Returns:
            QuerySet with ordering applied
        """
        return self.filter().order_by(*fields)

    def limit(self, count: int) -> QuerySet[T]:
        """Limit the number of results.

        Args:
            count: Maximum number of results to return

        Returns:
            QuerySet with limit applied
        """
        return self.filter().limit(count)

    def offset(self, count: int) -> QuerySet[T]:
        """Skip the specified number of results.

        Args:
            count: Number of results to skip

        Returns:
            QuerySet with offset applied
        """
        return self.filter().offset(count)

    def only(self, *fields) -> QuerySet[T]:
        """Load only the specified fields from the database.

        Args:
            *fields: Field names to load (supports strings and field expressions)

        Returns:
            QuerySet that loads only the specified fields
        """
        return self.filter().only(*fields)

    def none(self) -> QuerySet[T]:
        """Return an empty queryset that will never match any objects.

        Returns:
            QuerySet that returns no results
        """
        return self.filter().none()

    def reverse(self) -> QuerySet[T]:
        """Reverse the ordering of the queryset.

        Returns:
            QuerySet with reversed ordering
        """
        return self.filter().reverse()

    def select_related(self, *fields) -> QuerySet[T]:
        """JOIN preload related objects.

        Args:
            *fields: Related field names to preload (supports strings, field expressions, and nested paths)

        Returns:
            QuerySet with related objects preloaded

        Examples:
            # String paths (Django style)
            posts = await Post.objects.select_related('author', 'category').all()
            comments = await Comment.objects.select_related('post__author').all()

            # Field expressions (single relationship)
            posts = await Post.objects.select_related(Post.author).all()

            # Field expressions (nested relationships - future feature)
            # comments = await Comment.objects.select_related(Comment.post.author).all()
        """
        return self.filter().select_related(*fields)

    def prefetch_related(self, *fields, **queryset_configs: "QuerySet[Any]") -> QuerySet[T]:
        """Separate query preload related objects with advanced configuration support.

        Args:
            *fields: Simple prefetch field names (supports strings, field expressions, and nested paths)
            **queryset_configs: Advanced prefetch with custom QuerySets for filtering/ordering

        Returns:
            QuerySet with related objects prefetched

        Examples:
            # String paths (Django style)
            users = await User.objects.prefetch_related('posts', 'profile').all()

            # Field expressions (single relationship)
            users = await User.objects.prefetch_related(User.posts).all()

            # Field expressions (nested relationships - future feature)
            # users = await User.objects.prefetch_related(User.posts.tags).all()

            # Advanced prefetch with filtering and ordering
            users = await User.objects.prefetch_related(
                published_posts=Post.objects.filter(Post.is_published == True)
                                           .order_by('-created_at')
                                           .limit(5)
            ).all()

            # Mixed usage
            users = await User.objects.prefetch_related(
                User.profile,  # Field expression
                recent_posts=Post.objects.filter(
                    Post.created_at >= datetime.now() - timedelta(days=30)
                ).order_by('-created_at')
            ).all()
        """
        return self.filter().prefetch_related(*fields, **queryset_configs)
