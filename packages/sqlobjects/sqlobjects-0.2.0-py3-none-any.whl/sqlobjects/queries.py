"""
SQLObjects Queries Module - Component-based Architecture

This module provides the core query building system for SQLObjects, using
composition pattern for better maintainability and performance.
"""

import asyncio
import gc
import hashlib
from collections.abc import AsyncGenerator
from datetime import date, datetime
from typing import Any, Generic, Literal, TypeVar, Union

from sqlalchemy import (
    BinaryExpression,
    ClauseElement,
    ColumnElement,
    Table,
    and_,
    asc,
    delete,
    desc,
    exists,
    func,
    literal,
    not_,
    or_,
    select,
    text,
    update,
)

from .exceptions import DoesNotExist, MultipleObjectsReturned
from .expressions import SubqueryExpression
from .fields import get_column_from_field, is_field_definition
from .session import AsyncSession


# Export classes for use in other modules
__all__ = ["Q", "QuerySet", "QueryBuilder", "QueryCache", "QueryExecutor", "T"]

# Type variables for generic support
T = TypeVar("T")

# Supported expression types for Q object combinations
QueryType = Union[
    "Q",
    ColumnElement,
    BinaryExpression,
    ClauseElement,
    Any,  # For FunctionExpression and other SQLObjects expressions
]


class Q:
    """Q object for logical combination of SQLAlchemy expressions.

    Focuses on combining SQLAlchemy expressions using logical operators (AND, OR, NOT).
    Supports both single and multiple expressions with automatic AND combination.

    Examples:
        # Single expression
        Q(User.age >= 18)

        # Multiple expressions (AND combination)
        Q(User.age >= 18, User.is_active == True)

        # Logical combinations
        Q(User.name == "John") | Q(User.name == "Jane")
        Q(User.age >= 18) & Q(User.is_active == True)
        ~Q(User.is_deleted == True)

        # Mixed with SQLAlchemy expressions
        Q(User.name == "John") & (User.age > 25)
    """

    def __init__(self, *expressions: Any):
        """Initialize Q object with SQLAlchemy expressions.

        Args:
            *expressions: SQLAlchemy expressions to combine with AND logic
        """
        self.expressions = list(expressions)
        self.connector = "AND"
        self.negated = False
        self.children: list[Q] = []

    def __and__(self, other: QueryType) -> "Q":
        """Combine with another expression using AND logic.

        Args:
            other: Another Q object or SQLAlchemy expression

        Returns:
            New Q object representing the AND combination

        Raises:
            ArgumentError: If SQLAlchemy expression is on left side with Q object
        """
        new_q = Q()
        new_q.connector = "AND"

        if isinstance(other, Q):
            new_q.children = [self, other]
        else:
            # Q object must be on left side for SQLAlchemy expression combinations
            new_q.children = [self]
            new_q.expressions = [other]

        return new_q

    def __or__(self, other: QueryType) -> "Q":
        """Combine with another expression using OR logic.

        Args:
            other: Another Q object or SQLAlchemy expression

        Returns:
            New Q object representing the OR combination
        """
        new_q = Q()
        new_q.connector = "OR"

        if isinstance(other, Q):
            new_q.children = [self, other]
        else:
            new_q.children = [self]
            new_q.expressions = [other]

        return new_q

    def __invert__(self) -> "Q":
        """Negate this Q object using NOT logic.

        Returns:
            New Q object representing the negated condition
        """
        new_q = Q(*self.expressions)
        new_q.connector = self.connector
        new_q.negated = not self.negated
        new_q.children = self.children.copy()
        return new_q

    def _to_sqlalchemy(self, table: Table) -> Any:
        """Convert Q object to SQLAlchemy condition expression.

        Args:
            table: The table for expression resolution

        Returns:
            SQLAlchemy condition expression
        """
        conditions = []

        # Handle child Q objects
        if self.children:
            child_conditions = [child._to_sqlalchemy(table) for child in self.children]
            conditions.extend(child_conditions)

        # Handle direct expressions
        if self.expressions:
            for expr in self.expressions:
                if hasattr(expr, "resolve"):
                    # Resolve SQLObjects expressions
                    conditions.append(expr.resolve(table))
                else:
                    # Direct SQLAlchemy expressions
                    conditions.append(expr)

        # Combine conditions based on connector
        if len(conditions) == 0:
            # No conditions, return a true condition
            condition = literal(True)
        elif len(conditions) == 1:
            condition = conditions[0]
        else:
            if self.connector == "AND":
                condition = and_(*conditions)
            else:  # OR
                condition = or_(*conditions)

        return not_(condition) if self.negated else condition


class QueryBuilder:
    """Immutable query builder for SQL construction and optimization.

    Handles all aspects of SQL query building through composition pattern.
    Each method returns a new QueryBuilder instance to maintain immutability.
    """

    def __init__(self, model_class):
        """Initialize QueryBuilder with model class.

        Args:
            model_class: The model class this builder operates on
        """
        self.model_class = model_class
        self.conditions: list[Any] = []  # SQLAlchemy expressions, Q objects, etc.
        self.ordering: list[Any] = []  # Strings or SQLAlchemy expressions
        self.limits: int | None = None
        self.offset_value: int | None = None
        self.relationships: set[str] = set()
        self.selected_fields: set[str] = set()
        self.deferred_fields: set[str] = set()
        self.distinct_fields: list[str] = []
        self.annotations: dict[str, Any] = {}
        self.group_clauses: list[Any] = []
        self.having_conditions: list[Any] = []
        self.joins: list[tuple[Table, Any, str]] = []  # (table, condition, join_type)
        self.lock_mode: str | None = None
        self.lock_options: dict[str, bool] = {}
        self.extra_columns: dict[str, str] = {}
        self.extra_where: list[str] = []
        self.extra_params: dict[str, Any] = {}
        self.is_none_query: bool = False
        self.is_reversed: bool = False
        self.prefetch_configs: dict[str, Any] = {}

    def add_filter(self, *conditions):
        """Add WHERE conditions to the query.

        Args:
            *conditions: SQLAlchemy expressions or Q objects

        Returns:
            New QueryBuilder instance with added conditions
        """
        new_builder = self.copy()
        new_builder.conditions.extend(conditions)
        return new_builder

    def add_ordering(self, *fields):
        """Add ORDER BY fields to the query.

        Args:
            *fields: Field names or SQLAlchemy ordering expressions

        Returns:
            New QueryBuilder instance with added ordering
        """
        new_builder = self.copy()
        new_builder.ordering.extend(fields)
        return new_builder

    def add_limit(self, count: int):
        """Add LIMIT clause to the query.

        Args:
            count: Maximum number of results to return

        Returns:
            New QueryBuilder instance with limit applied
        """
        new_builder = self.copy()
        new_builder.limits = count
        return new_builder

    def add_offset(self, count: int):
        """Add OFFSET clause to the query.

        Args:
            count: Number of results to skip

        Returns:
            New QueryBuilder instance with offset applied
        """
        new_builder = self.copy()
        new_builder.offset_value = count
        return new_builder

    def add_relationships(self, *fields):
        """Add relationship fields for select_related/prefetch_related.

        Args:
            *fields: Relationship field names as strings

        Returns:
            New QueryBuilder instance with relationship fields added
        """
        new_builder = self.copy()
        new_builder.relationships.update(fields)
        return new_builder

    def add_prefetch_configs(self, **configs):
        """Add prefetch configurations with custom QuerySets.

        Args:
            **configs: Mapping of field names to custom QuerySet configurations

        Returns:
            New QueryBuilder instance with prefetch configs added
        """
        new_builder = self.copy()
        new_builder.prefetch_configs = {**self.prefetch_configs, **configs}
        return new_builder

    def add_selected_fields(self, *fields):
        """Add fields to SELECT clause (only() method).

        Args:
            *fields: Field names to include in SELECT

        Returns:
            New QueryBuilder instance with selected fields added
        """
        new_builder = self.copy()
        new_builder.selected_fields.update(fields)
        return new_builder

    def add_deferred_fields(self, *fields):
        """Add fields to defer from SELECT clause (defer() method).

        Args:
            *fields: Field names to exclude from SELECT

        Returns:
            New QueryBuilder instance with deferred fields added
        """
        new_builder = self.copy()
        new_builder.deferred_fields.update(fields)
        return new_builder

    def add_distinct(self, *fields):
        """Add DISTINCT clause to the query.

        Args:
            *fields: Field names for DISTINCT, empty for all fields

        Returns:
            New QueryBuilder instance with DISTINCT applied
        """
        new_builder = self.copy()
        new_builder.distinct_fields = list(fields)
        return new_builder

    def add_annotations(self, **kwargs):
        """Add annotation expressions to SELECT clause.

        Args:
            **kwargs: Mapping of alias names to SQLAlchemy expressions

        Returns:
            New QueryBuilder instance with annotations added
        """
        new_builder = self.copy()
        new_builder.annotations.update(kwargs)
        return new_builder

    def add_group_by(self, *fields):
        """Add GROUP BY clauses to the query.

        Args:
            *fields: Field names or SQLAlchemy expressions for grouping

        Returns:
            New QueryBuilder instance with GROUP BY added
        """
        new_builder = self.copy()
        new_builder.group_clauses.extend(fields)
        return new_builder

    def add_having(self, *conditions):
        """Add HAVING conditions for grouped queries.

        Args:
            *conditions: SQLAlchemy expressions for HAVING clause

        Returns:
            New QueryBuilder instance with HAVING conditions added
        """
        new_builder = self.copy()
        new_builder.having_conditions.extend(conditions)
        return new_builder

    def add_join(self, table: Table, condition: Any, join_type: str = "inner"):
        """Add JOIN clause to the query.

        Args:
            table: Table to join with
            condition: JOIN condition expression
            join_type: Type of join ('inner', 'left', 'outer')

        Returns:
            New QueryBuilder instance with JOIN added
        """
        new_builder = self.copy()
        new_builder.joins.append((table, condition, join_type))
        return new_builder

    def add_lock(self, mode: str, **options):
        """Add row-level locking to the query.

        Args:
            mode: Lock mode ('update' or 'share')
            **options: Lock options (nowait, skip_locked)

        Returns:
            New QueryBuilder instance with locking applied
        """
        new_builder = self.copy()
        new_builder.lock_mode = mode
        new_builder.lock_options = options
        return new_builder

    def add_extra(
        self, columns: dict[str, str] | None = None, where: list[str] | None = None, params: dict | None = None
    ):
        """Add extra SQL fragments to the query.

        Args:
            columns: Extra columns to add to SELECT clause
            where: Extra WHERE conditions as raw SQL strings
            params: Parameters for extra SQL fragments

        Returns:
            New QueryBuilder instance with extra SQL added
        """
        new_builder = self.copy()
        if columns:
            new_builder.extra_columns.update(columns)
        if where:
            new_builder.extra_where.extend(where)
        if params:
            new_builder.extra_params.update(params)
        return new_builder

    def set_none(self):
        """Set query to return no results (none() method).

        Returns:
            New QueryBuilder instance that will return empty results
        """
        new_builder = self.copy()
        new_builder.is_none_query = True
        return new_builder

    def set_reversed(self):
        """Set query ordering to be reversed.

        Returns:
            New QueryBuilder instance with reversed ordering
        """
        new_builder = self.copy()
        new_builder.is_reversed = True
        return new_builder

    def build(self, table):
        """Build final SQLAlchemy query object from accumulated clauses.

        Args:
            table: SQLAlchemy Table object to query

        Returns:
            SQLAlchemy Select object ready for execution
        """
        # Handle none query - return query that matches nothing
        if self.is_none_query:
            return select(table).where(literal(False))

        # Get auto-deferred fields from model class
        auto_deferred_fields = set()
        if hasattr(self.model_class, "_get_field_cache"):
            try:
                field_cache = self.model_class._get_field_cache()  # noqa
                auto_deferred_fields = field_cache.get("deferred_fields", set())
            except Exception:  # noqa
                pass

        # Handle field selection (only() method)
        if self.selected_fields:
            columns = [table.c[field] for field in self.selected_fields if field in table.c]
            query = select(*columns) if columns else select(table)
        elif self.deferred_fields or auto_deferred_fields:
            # For defer() or auto-deferred fields, select all fields except deferred ones
            all_fields = set(table.columns.keys())
            combined_deferred = self.deferred_fields | auto_deferred_fields
            selected_fields = all_fields - combined_deferred
            columns = [table.c[field] for field in selected_fields if field in table.c]
            query = select(*columns) if columns else select(table)
        else:
            query = select(table)

        # Apply joins
        for join_table, join_condition, join_type in self.joins:
            if join_type == "left":
                query = query.outerjoin(join_table, join_condition)
            else:  # inner join
                query = query.join(join_table, join_condition)

        # Apply conditions
        if self.conditions:
            query = query.where(and_(*self.conditions))

        # Apply extra where clauses
        if self.extra_where:
            extra_conditions = []
            for clause in self.extra_where:
                if self.extra_params:
                    extra_conditions.append(text(clause).bindparams(**self.extra_params))
                else:
                    extra_conditions.append(text(clause))
            query = query.where(and_(*extra_conditions))

        # Apply distinct
        if self.distinct_fields:
            columns = [table.c[field] for field in self.distinct_fields if field in table.c]
            if columns:
                query = query.distinct(*columns)
            else:
                query = query.distinct()

        # Apply annotations
        if self.annotations:
            annotation_columns = []
            for alias, expr in self.annotations.items():
                if hasattr(expr, "resolve"):
                    annotation_columns.append(expr.resolve(table).label(alias))
                else:
                    annotation_columns.append(expr.label(alias))
            query = query.add_columns(*annotation_columns)

        # Apply extra columns
        if self.extra_columns:
            extra_cols = []
            for alias, sql in self.extra_columns.items():
                if self.extra_params:
                    extra_cols.append(text(sql).bindparams(**self.extra_params).label(alias))
                else:
                    extra_cols.append(text(sql).label(alias))
            query = query.add_columns(*extra_cols)

        # Apply group by
        if self.group_clauses:
            group_columns = []
            for field in self.group_clauses:
                if isinstance(field, str) and field in table.c:
                    group_columns.append(table.c[field])
                elif hasattr(field, "resolve") and not isinstance(field, str):
                    group_columns.append(field.resolve(table))
                else:
                    group_columns.append(field)
            query = query.group_by(*group_columns)

        # Apply having
        if self.having_conditions:
            having_exprs = []
            for condition in self.having_conditions:
                if hasattr(condition, "resolve"):
                    having_exprs.append(condition.resolve(table))
                else:
                    having_exprs.append(condition)
            query = query.having(and_(*having_exprs))

        # Apply ordering
        if self.ordering:
            order_clauses = []
            for field in self.ordering:
                if isinstance(field, str):
                    if field.startswith("-"):
                        field_name = field[1:]
                        if field_name in table.c:
                            order_clauses.append(desc(table.c[field_name]))
                    else:
                        if field in table.c:
                            order_clauses.append(asc(table.c[field]))
                elif hasattr(field, "resolve"):
                    order_clauses.append(field.resolve(table))
                else:
                    order_clauses.append(field)
            if order_clauses:
                if self.is_reversed:
                    reversed_clauses = []
                    for clause in order_clauses:
                        if hasattr(clause, "desc") and clause.desc:
                            reversed_clauses.append(asc(clause.element))
                        else:
                            reversed_clauses.append(desc(clause.element if hasattr(clause, "element") else clause))
                    query = query.order_by(*reversed_clauses)
                else:
                    query = query.order_by(*order_clauses)

        # Apply row locking
        if self.lock_mode:
            lock_kwargs = {k: v for k, v in self.lock_options.items() if k in ("nowait", "skip_locked")}
            if self.lock_mode == "update":
                query = query.with_for_update(**lock_kwargs)  # type: ignore[arg-type]
            elif self.lock_mode == "share":
                query = query.with_for_update(read=True, **lock_kwargs)  # type: ignore[arg-type]

        # Apply limit and offset
        if self.limits is not None:
            query = query.limit(self.limits)
        if self.offset_value is not None:
            query = query.offset(self.offset_value)

        return query

    def copy(self):
        """Create a deep copy of this QueryBuilder instance.

        Returns:
            New QueryBuilder instance with identical state
        """
        new_builder = QueryBuilder(self.model_class)
        new_builder.conditions = self.conditions.copy()
        new_builder.ordering = self.ordering.copy()
        new_builder.limits = self.limits
        new_builder.offset_value = self.offset_value
        new_builder.relationships = self.relationships.copy()
        new_builder.selected_fields = self.selected_fields.copy()
        new_builder.deferred_fields = self.deferred_fields.copy()
        new_builder.distinct_fields = self.distinct_fields.copy()
        new_builder.annotations = self.annotations.copy()
        new_builder.group_clauses = self.group_clauses.copy()
        new_builder.having_conditions = self.having_conditions.copy()
        new_builder.joins = self.joins.copy()
        new_builder.lock_mode = self.lock_mode
        new_builder.lock_options = self.lock_options.copy()
        new_builder.extra_columns = self.extra_columns.copy()
        new_builder.extra_where = self.extra_where.copy()
        new_builder.extra_params = self.extra_params.copy()
        new_builder.is_none_query = self.is_none_query
        new_builder.is_reversed = self.is_reversed
        new_builder.prefetch_configs = self.prefetch_configs.copy()
        return new_builder


class QueryCache:
    """FIFO query result cache with performance monitoring.

    Provides automatic caching of query results with configurable size limits
    and comprehensive statistics tracking for performance optimization.
    """

    def __init__(self, maxsize: int = 1000):
        """Initialize cache with maximum size limit.

        Args:
            maxsize: Maximum number of cached results (FIFO eviction)
        """
        self.cache: dict[str, Any] = {}
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0

    def get(self, cache_key: str):
        """Retrieve cached query result by key.

        Args:
            cache_key: Unique identifier for the cached result

        Returns:
            Cached result if found, None otherwise
        """
        if cache_key in self.cache:
            self.hits += 1
            return self.cache[cache_key]
        self.misses += 1
        return None

    def set(self, cache_key: str, result: Any):
        """Store query result in cache with FIFO eviction.

        Args:
            cache_key: Unique identifier for the result
            result: Query result to cache
        """
        if len(self.cache) >= self.maxsize:
            # FIFO eviction - remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[cache_key] = result

    def clear(self):
        """Clear all cached results and reset statistics."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> dict[str, int | float]:
        """Get comprehensive cache performance statistics.

        Returns:
            Dictionary with hits, misses, hit_rate, and cache_size
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {"hits": self.hits, "misses": self.misses, "hit_rate": hit_rate, "cache_size": len(self.cache)}


class QueryExecutor:
    """Unified query execution engine with caching and iterator support.

    Handles all types of query execution including regular queries, bulk operations,
    aggregations, and memory-efficient iteration for large datasets.
    """

    def __init__(self, session=None):
        """Initialize executor with optional session.

        Args:
            session: Database session for query execution
        """
        self.session = session

    async def execute(
        self,
        query,
        query_type: str = "all",
        cache: QueryCache | None = None,
        use_cache: bool = True,
        builder=None,
        model_class=None,
        **kwargs,
    ):
        """Unified query execution with caching.

        Args:
            query: SQLAlchemy query object
            query_type: Type of query execution
            cache: Cache instance to use
            use_cache: Whether to use cache for this operation
            builder: QueryBuilder instance for prefetch handling
            model_class: Model class for row conversion
            **kwargs: Additional parameters for query building
        """
        # Build the actual query based on type
        actual_query = self._build_query_by_type(query, query_type, **kwargs)

        # Handle caching (skip for update/delete operations or when use_cache=False)
        cache_key = None
        if cache and use_cache and query_type in ("all", "count", "exists"):
            cache_key = hashlib.md5(str(actual_query).encode()).hexdigest()
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        # Get deferred fields from builder or model class field definitions
        deferred_fields = builder.deferred_fields if builder else set()

        # Add auto-deferred fields from model field definitions
        if model_class:
            auto_deferred = self._get_auto_deferred_fields(model_class)
            deferred_fields = deferred_fields | auto_deferred

            # For only() queries, add fields not in selected_fields as deferred
            if builder and builder.selected_fields:
                all_fields = set(model_class._get_field_names())  # noqa
                deferred_fields = deferred_fields | (all_fields - builder.selected_fields)

        result = await self._execute_query(actual_query, query_type, model_class, deferred_fields)

        # Handle prefetch_related if builder has prefetch configs
        if query_type == "all" and builder and builder.prefetch_configs and result:
            result = await self._handle_prefetch(result, builder.prefetch_configs)

        # Cache result (only for read operations and when use_cache=True)
        if cache and use_cache and cache_key:
            cache.set(cache_key, result)

        return result

    async def iterator(self, query, chunk_size: int = 1000):
        """Async iterator for processing large datasets in chunks."""
        offset = 0
        processed_chunks = 0

        while True:
            chunk_query = query.offset(offset).limit(chunk_size)
            chunk = await self._execute_query(chunk_query, "all")

            if not chunk:
                break

            for item in chunk:
                yield item

            offset += len(chunk)
            processed_chunks += 1

            # Periodic memory cleanup
            if processed_chunks % 10 == 0:
                gc.collect()

    @staticmethod
    def _build_query_by_type(query, query_type: str, **kwargs):
        """Build query based on execution type."""
        if query_type == "count":
            return (
                select(func.count())
                .select_from(query.froms[0] if query.froms else query.table)
                .where(query.whereclause)
                if query.whereclause is not None
                else select(func.count()).select_from(query.froms[0] if query.froms else query.table)
            )
        elif query_type == "exists":
            return select(exists(query))
        elif query_type == "update":
            table = query.froms[0] if query.froms else query.table
            update_query = update(table).values(**kwargs.get("values", {}))
            if query.whereclause is not None:
                update_query = update_query.where(query.whereclause)
            return update_query
        elif query_type == "delete":
            table = query.froms[0] if query.froms else query.table
            delete_query = delete(table)
            if query.whereclause is not None:
                delete_query = delete_query.where(query.whereclause)
            return delete_query
        elif query_type in ("values", "values_list"):
            fields = kwargs.get("fields", [])
            if fields:
                table = query.froms[0] if query.froms else query.table
                columns = [table.c[field] for field in fields if field in table.c]
                new_query = select(*columns)
                if query.whereclause is not None:
                    new_query = new_query.where(query.whereclause)
                if hasattr(query, "_order_by") and query._order_by:  # noqa
                    new_query = new_query.order_by(*query._order_by)  # noqa
                return new_query
            return query
        elif query_type == "aggregate":
            aggregations = kwargs.get("aggregations", [])
            table = query.froms[0] if query.froms else query.table
            agg_query = select(*aggregations).select_from(table)
            if query.whereclause is not None:
                agg_query = agg_query.where(query.whereclause)
            return agg_query
        else:  # "all"
            return query

    async def _execute_query(self, query, query_type: str, model_class=None, deferred_fields=None):
        """Execute query and return appropriate result."""
        if not self.session:
            if query_type == "all":
                return []
            elif query_type in ("count", "update", "delete"):
                return 0
            elif query_type in ("values", "values_list", "aggregate"):
                return []
            else:  # exists
                return False

        result = await self.session.execute(query)

        if query_type == "all":
            rows = result.fetchall()
            if model_class:
                return [self._row_to_instance(row, model_class, deferred_fields) for row in rows]
            return rows
        elif query_type in ("count", "exists"):
            return result.scalar_one()
        elif query_type in ("update", "delete"):
            return result.rowcount
        elif query_type in ("values", "values_list", "aggregate"):
            return result.fetchall()
        else:
            return result.fetchall()

    @staticmethod
    def _get_auto_deferred_fields(model_class):
        """Get fields that are marked as deferred=True in field definitions."""
        auto_deferred = set()

        try:
            # Use field cache to get deferred fields
            field_cache = model_class._get_field_cache()  # noqa
            auto_deferred = field_cache.get("deferred_fields", set())
        except Exception:  # noqa
            # Fallback: manually check field definitions
            try:
                from .fields import get_column_from_field, is_field_definition

                for field_name in model_class._get_field_names():  # noqa
                    field_attr = getattr(model_class, field_name, None)
                    if field_attr is not None and is_field_definition(field_attr):
                        column = get_column_from_field(field_attr)
                        if column is not None and hasattr(column, "info") and column.info:
                            performance_params = column.info.get("_performance", {})
                            if performance_params.get("deferred", False):
                                auto_deferred.add(field_name)
            except Exception:  # noqa
                pass

        return auto_deferred

    @staticmethod
    def _row_to_instance(row, model_class, deferred_fields=None):
        """Convert SQLAlchemy Row to model instance with deferred field support."""
        # Convert Row to dictionary
        data = dict(row._mapping)  # noqa

        # Get all field names from model
        all_fields = set(model_class._get_field_names())  # noqa
        loaded_fields = set(data.keys())

        # Calculate actual deferred fields (fields not in loaded data)
        actual_deferred_fields = all_fields - loaded_fields

        # If explicit deferred_fields provided, use those instead
        if deferred_fields:
            actual_deferred_fields = set(deferred_fields)
            # Remove deferred fields from data
            for field in deferred_fields:
                data.pop(field, None)

        # Create model instance
        instance = model_class.from_dict(data, validate=False)

        # Set deferred field state if there are any deferred fields
        if actual_deferred_fields:
            instance._state_manager.set("deferred_fields", actual_deferred_fields)  # noqa
            instance._state_manager.set("is_from_db", True)  # noqa
            instance._state_manager.set("loaded_deferred_fields", set())  # noqa

        return instance

    async def _handle_prefetch(self, instances, prefetch_configs):
        """Handle prefetch_related with custom QuerySet configurations."""
        if not instances or not prefetch_configs:
            return instances

        instance_ids = [instance.id for instance in instances if hasattr(instance, "id")]
        if not instance_ids:
            return instances

        # Execute all prefetch queries concurrently
        tasks = [
            self._single_prefetch(field_name, queryset, instance_ids)
            for field_name, queryset in prefetch_configs.items()
        ]
        prefetch_results = await asyncio.gather(*tasks)

        # Associate results with instances
        for field_name, related_objects in prefetch_results:
            related_map = self._group_by_foreign_key(related_objects)
            for instance in instances:
                instance_id = getattr(instance, "id", None)
                setattr(instance, field_name, related_map.get(instance_id, []))

        return instances

    @staticmethod
    async def _single_prefetch(field_name, queryset, instance_ids):
        """Execute single prefetch query."""
        # Assume foreign key field follows pattern: {model_name}_id
        # This is a simplified implementation - in practice, you'd need relationship metadata
        foreign_key_field = f"{queryset._model_class.__name__.lower()}_id"  # noqa

        try:
            # Try to find the foreign key column
            if hasattr(queryset._table.c, foreign_key_field):  # noqa
                fk_column = getattr(queryset._table.c, foreign_key_field)  # noqa
            else:
                # Fallback to common patterns
                for col_name in queryset._table.c.keys():  # noqa
                    if col_name.endswith("_id"):
                        fk_column = queryset._table.c[col_name]  # noqa
                        break
                else:
                    return field_name, []

            related_objects = await queryset.filter(fk_column.in_(instance_ids)).all()
            return field_name, related_objects
        except Exception:  # noqa
            # If prefetch fails, return empty list
            return field_name, []

    @staticmethod
    def _group_by_foreign_key(related_objects):
        """Group related objects by foreign key."""
        grouped = {}
        for obj in related_objects:
            # Try to find the foreign key value
            fk_value = None
            for attr_name in dir(obj):
                if attr_name.endswith("_id") and not attr_name.startswith("_"):
                    fk_value = getattr(obj, attr_name, None)
                    break

            if fk_value is not None:
                if fk_value not in grouped:
                    grouped[fk_value] = []
                grouped[fk_value].append(obj)

        return grouped


class QuerySet(Generic[T]):
    """
    Refactored QuerySet using composition pattern.

    This implementation uses independent components to handle different
    aspects of query processing, avoiding MRO issues and improving
    maintainability.
    """

    def __init__(
        self,
        table: Table,
        model_class: type[T],
        db_or_session: str | AsyncSession | None = None,
        default_ordering: bool = True,
        use_cache: bool = True,
    ) -> None:
        """Initialize QuerySet with component composition."""
        self._table = table
        self._model_class = model_class
        self._db_or_session = db_or_session
        self._default_ordering = default_ordering
        self._use_cache = use_cache

        # Initialize components using composition
        self._builder = QueryBuilder(model_class)
        self._cache = QueryCache()
        self._executor = QueryExecutor(db_or_session)

        # Apply default ordering if needed
        if default_ordering and self._has_default_ordering():
            ordering = getattr(self._model_class, "_default_ordering", [])
            self._builder = self._builder.add_ordering(*ordering)

    @staticmethod
    def _get_field_name(field) -> str:
        """Extract field name from various field types.

        Supports strings, field expressions, SQLAlchemy ordering expressions,
        and field definitions. Handles desc() and asc() wrapped fields.

        Args:
            field: Field to extract name from

        Returns:
            Field name as string

        Raises:
            ValueError: If field name cannot be resolved
        """
        if isinstance(field, str):
            return field
        elif hasattr(field, "name") and field.name:
            return field.name
        elif hasattr(field, "element") and hasattr(field.element, "name"):
            return field.element.name
        elif is_field_definition(field):
            column = get_column_from_field(field)
            return column.name if column is not None and column.name else str(field)
        else:
            raise ValueError(f"Cannot resolve field name from {field}")

    @staticmethod
    def _get_relationship_path(field) -> str:
        """Extract relationship path from field expressions and strings.

        Converts field expressions with path segments to Django-style
        relationship paths using double underscores.

        Args:
            field: Field expression or string path

        Returns:
            Relationship path as string (e.g., 'user__posts__tags')

        Raises:
            ValueError: If relationship path cannot be resolved
        """
        if isinstance(field, str):
            return field
        elif hasattr(field, "path_segments") and field.path_segments:
            # Field expression path: ['user', 'posts', 'tags'] -> 'user__posts__tags'
            return "__".join(field.path_segments)
        elif hasattr(field, "name") and field.name:
            # Single field expression: 'user' -> 'user'
            return field.name
        else:
            raise ValueError(f"Cannot resolve relationship path from {field}")

    def _has_default_ordering(self) -> bool:
        """Check if model class has default ordering configured.

        Returns:
            True if model has default ordering, False otherwise
        """
        return hasattr(self._model_class, "_default_ordering") and bool(
            getattr(self._model_class, "_default_ordering", [])
        )

    def _create_new_queryset(self, builder: QueryBuilder | None = None) -> "QuerySet[T]":
        """Create new QuerySet instance with shared components.

        Args:
            builder: Optional QueryBuilder to use, defaults to copy of current builder

        Returns:
            New QuerySet instance with shared cache and executor
        """
        new_qs = QuerySet(self._table, self._model_class, self._db_or_session, self._default_ordering, self._use_cache)
        new_qs._builder = builder or self._builder.copy()
        new_qs._cache = self._cache  # Shared cache for performance
        new_qs._executor = self._executor  # Shared executor
        return new_qs

    # ========================================
    # Query Building Methods - Return QuerySet
    # ========================================

    def using(self, db_or_session: str | AsyncSession) -> "QuerySet[T]":
        """Specify database name or session object."""
        new_qs = QuerySet(self._table, self._model_class, db_or_session, self._default_ordering, self._use_cache)
        new_qs._builder = self._builder.copy()
        new_qs._cache = self._cache
        new_qs._executor = QueryExecutor(db_or_session)  # New executor with different session
        return new_qs

    def skip_default_ordering(self) -> "QuerySet[T]":
        """Return QuerySet that skips applying default ordering."""
        new_qs = QuerySet(
            self._table, self._model_class, self._db_or_session, default_ordering=False, use_cache=self._use_cache
        )
        new_qs._builder = self._builder.copy()
        new_qs._cache = self._cache
        new_qs._executor = self._executor
        return new_qs

    def filter(self, *conditions) -> "QuerySet[T]":
        """Filter QuerySet to include only objects matching conditions."""
        new_builder = self._builder.add_filter(*conditions)
        return self._create_new_queryset(new_builder)

    def exclude(self, *conditions) -> "QuerySet[T]":
        """Exclude objects matching conditions from QuerySet."""
        # Convert conditions to negated conditions
        negated_conditions = [not_(cond) for cond in conditions]
        new_builder = self._builder.add_filter(*negated_conditions)
        return self._create_new_queryset(new_builder)

    def order_by(self, *fields) -> "QuerySet[T]":
        """Order QuerySet results by specified fields."""
        processed_fields = []
        for field in fields:
            if isinstance(field, str):
                processed_fields.append(field)
            elif hasattr(field, "desc") or hasattr(field, "asc"):  # SQLAlchemy ordering expressions
                processed_fields.append(field)
            else:  # Field expressions
                processed_fields.append(self._get_field_name(field))

        new_builder = self._builder.add_ordering(*processed_fields)
        return self._create_new_queryset(new_builder)

    def limit(self, count: int) -> "QuerySet[T]":
        """Limit number of results returned."""
        new_builder = self._builder.add_limit(count)
        return self._create_new_queryset(new_builder)

    def offset(self, count: int) -> "QuerySet[T]":
        """Skip specified number of results from beginning."""
        new_builder = self._builder.add_offset(count)
        return self._create_new_queryset(new_builder)

    def only(self, *fields) -> "QuerySet[T]":
        """Load only specified fields from database."""
        field_names = [self._get_field_name(f) for f in fields]
        new_builder = self._builder.add_selected_fields(*field_names)
        return self._create_new_queryset(new_builder)

    def defer(self, *fields) -> "QuerySet[T]":
        """Defer loading of specified fields until accessed."""
        field_names = [self._get_field_name(f) for f in fields]
        new_builder = self._builder.add_deferred_fields(*field_names)
        return self._create_new_queryset(new_builder)

    def select_related(self, *fields) -> "QuerySet[T]":
        """JOIN preload related objects.

        Args:
            *fields: Related field names to preload (supports strings, field expressions, and nested paths)

        Examples:
            # String paths (Django style)
            posts = await Post.objects.select_related('author', 'category').all()
            comments = await Comment.objects.select_related('post__author').all()

            # Field expressions (single relationship)
            posts = await Post.objects.select_related(Post.author).all()

            # Field expressions (nested relationships - future feature)
            # comments = await Comment.objects.select_related(Comment.post.author).all()
        """
        relationship_paths = [self._get_relationship_path(f) for f in fields]
        new_builder = self._builder.add_relationships(*relationship_paths)
        return self._create_new_queryset(new_builder)

    def prefetch_related(self, *fields, **queryset_configs) -> "QuerySet[T]":
        """Separate query preload related objects with advanced configuration support.

        Args:
            *fields: Simple prefetch field names (supports strings, field expressions, and nested paths)
            **queryset_configs: Advanced prefetch with custom QuerySets for filtering/ordering

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
        relationship_paths = [self._get_relationship_path(f) for f in fields]
        new_builder = self._builder.add_relationships(*relationship_paths)
        if queryset_configs:
            new_builder = new_builder.add_prefetch_configs(**queryset_configs)
        return self._create_new_queryset(new_builder)

    # Advanced query building

    def distinct(self, *fields) -> "QuerySet[T]":
        """Apply DISTINCT clause to eliminate duplicate rows."""
        if not fields:
            new_builder = self._builder.add_distinct()
        else:
            field_names = [self._get_field_name(f) for f in fields]
            new_builder = self._builder.add_distinct(*field_names)
        return self._create_new_queryset(new_builder)

    @staticmethod
    def _generate_auto_alias(expression) -> str:
        """Generate automatic alias for aggregation expressions"""
        # Get function name
        func_name = getattr(expression, "name", None)
        if not func_name:
            # Fallback: extract from string representation
            expr_str = str(expression).lower()
            if "(" in expr_str:
                func_name = expr_str.split("(")[0].strip()
            else:
                func_name = "expr"

        # Get field name from clauses
        field_name = None
        if hasattr(expression, "clauses"):
            try:
                clauses = list(expression.clauses)
                if clauses:
                    clause = clauses[0]
                    # Skip wildcard (*) clauses
                    if hasattr(clause, "name") and clause.name != "*":
                        field_name = clause.name
                    elif hasattr(clause, "element") and hasattr(clause.element, "name"):
                        field_name = clause.element.name
            except (TypeError, AttributeError):
                pass

        # Generate alias
        if field_name and field_name != "*":
            return f"{field_name}__{func_name}"
        else:
            return func_name

    def annotate(self, *args, **kwargs) -> "QuerySet[T]":
        """Add annotation fields with auto-alias support.

        Examples:
            # Manual aliases (existing functionality)
            User.objects.annotate(user_count=func.count())

            # Auto aliases (new functionality)
            User.objects.annotate(func.count())  # alias: count
            User.objects.annotate(func.avg(User.age))  # alias: age__avg

            # Mixed usage
            User.objects.annotate(
                func.count(),  # auto alias
                avg_salary=func.avg(User.salary)  # manual alias
            )
        """
        # Process positional arguments (auto aliases)
        auto_annotations = {}
        for expr in args:
            alias = self._generate_auto_alias(expr)
            auto_annotations[alias] = expr

        # Merge auto and manual aliases
        all_annotations = {**auto_annotations, **kwargs}

        new_builder = self._builder.add_annotations(**all_annotations)
        return self._create_new_queryset(new_builder)

    def group_by(self, *fields) -> "QuerySet[T]":
        """Add GROUP BY clause with field expression support.

        Args:
            *fields: Field names, field expressions, or SQLAlchemy expressions

        Examples:
            # String field names
            User.objects.group_by("department", "role")

            # Field expressions
            User.objects.group_by(User.department, User.role)

            # Mixed usage
            User.objects.group_by("department", User.role)

            # With aggregation
            User.objects.group_by(User.department).annotate(
                count=func.count(),
                avg_salary=func.avg(User.salary)
            )
        """
        processed_fields = []
        for field in fields:
            if isinstance(field, str):
                processed_fields.append(field)
            elif hasattr(field, "resolve"):  # SQLAlchemy expressions
                processed_fields.append(field)
            else:  # Field expressions
                processed_fields.append(self._get_field_name(field))

        new_builder = self._builder.add_group_by(*processed_fields)
        return self._create_new_queryset(new_builder)

    def having(self, *conditions) -> "QuerySet[T]":
        """Add HAVING clause for aggregated queries."""
        new_builder = self._builder.add_having(*conditions)
        return self._create_new_queryset(new_builder)

    def join(self, target_table: Table, on_condition: Any, join_type: str = "inner") -> "QuerySet[T]":
        """Perform manual JOIN with another table."""
        new_builder = self._builder.add_join(target_table, on_condition, join_type)
        return self._create_new_queryset(new_builder)

    def leftjoin(self, target_table: Table, on_condition: Any) -> "QuerySet[T]":
        """Perform LEFT JOIN with another table."""
        new_builder = self._builder.add_join(target_table, on_condition, "left")
        return self._create_new_queryset(new_builder)

    def outerjoin(self, target_table: Table, on_condition: Any) -> "QuerySet[T]":
        """Perform OUTER JOIN with another table."""
        new_builder = self._builder.add_join(target_table, on_condition, "left")
        return self._create_new_queryset(new_builder)

    def select_for_update(self, nowait: bool = False, skip_locked: bool = False) -> "QuerySet[T]":
        """Apply row-level locking using FOR UPDATE."""
        options = {}
        if nowait:
            options["nowait"] = True
        if skip_locked:
            options["skip_locked"] = True
        new_builder = self._builder.add_lock("update", **options)
        return self._create_new_queryset(new_builder)

    def select_for_share(self, nowait: bool = False, skip_locked: bool = False) -> "QuerySet[T]":
        """Apply shared row-level locking using FOR SHARE."""
        options = {}
        if nowait:
            options["nowait"] = True
        if skip_locked:
            options["skip_locked"] = True
        new_builder = self._builder.add_lock("share", **options)
        return self._create_new_queryset(new_builder)

    def extra(
        self, columns: dict[str, str] | None = None, where: list[str] | None = None, params: dict | None = None
    ) -> "QuerySet[T]":
        """Add extra SQL fragments to the query."""
        new_builder = self._builder.add_extra(columns, where, params)
        return self._create_new_queryset(new_builder)

    def none(self) -> "QuerySet[T]":
        """Return an empty queryset that will never match any objects."""
        new_builder = self._builder.set_none()
        return self._create_new_queryset(new_builder)

    def reverse(self) -> "QuerySet[T]":
        """Reverse the ordering of the queryset."""
        new_builder = self._builder.set_reversed()
        return self._create_new_queryset(new_builder)

    def no_cache(self) -> "QuerySet[T]":
        """Return QuerySet that skips cache for this operation."""
        new_qs = QuerySet(self._table, self._model_class, self._db_or_session, self._default_ordering, use_cache=False)
        new_qs._builder = self._builder.copy()
        new_qs._cache = self._cache
        new_qs._executor = self._executor
        return new_qs

    # ========================================
    # Query Execution Methods - Execute queries and return results
    # ========================================

    async def all(self) -> list[T]:
        """Execute query and return all matching objects."""
        query = self._builder.build(self._table)
        result = await self._executor.execute(
            query, "all", self._cache, self._use_cache, builder=self._builder, model_class=self._model_class
        )
        return result if isinstance(result, list) else []

    async def get(self, *conditions) -> T:
        """Get single object matching conditions."""
        if conditions:
            queryset = self.filter(*conditions)
        else:
            queryset = self

        results = await queryset.limit(2).all()
        if not results:
            raise DoesNotExist(f"{self._model_class.__name__} matching query does not exist")
        if len(results) > 1:
            raise MultipleObjectsReturned(f"Multiple {self._model_class.__name__} objects returned")
        return results[0]

    async def first(self) -> T | None:
        """Get first object matching conditions."""
        results = await self.limit(1).all()
        return results[0] if results else None

    async def count(self) -> int:
        """Count number of objects matching query conditions."""
        query = self._builder.build(self._table)
        result = await self._executor.execute(query, "count", self._cache, self._use_cache)
        return result if isinstance(result, int) else 0

    async def exists(self) -> bool:
        """Check if any objects match query conditions."""
        query = self._builder.build(self._table)
        result = await self._executor.execute(query, "exists", self._cache, self._use_cache)
        return bool(result)

    async def last(self) -> T | None:
        """Get the last object matching the QuerySet conditions."""
        reversed_qs = self.reverse()
        return await reversed_qs.first()

    async def earliest(self, *fields) -> T | None:
        """Get the earliest object based on the specified fields."""
        if not fields:
            fields = ["id"]
        field_names = [self._get_field_name(f) for f in fields]
        order_fields = [field.lstrip("-") for field in field_names]
        ordered_qs = self.order_by(*order_fields)
        return await ordered_qs.first()

    async def latest(self, *fields) -> T | None:
        """Get the latest object based on the specified fields."""
        if not fields:
            fields = ["id"]
        field_names = [self._get_field_name(f) for f in fields]
        order_fields = [f"-{field.lstrip('-')}" for field in field_names]
        ordered_qs = self.order_by(*order_fields)
        return await ordered_qs.first()

    async def values(self, *fields) -> list[dict[str, Any]]:
        """Get dictionaries containing only the specified field values."""
        if not fields:
            field_names = tuple(col.name for col in self._table.columns)  # noqa
        else:
            field_names = tuple(self._get_field_name(f) for f in fields)

        query = self._builder.build(self._table)
        result = await self._executor.execute(query, "values", self._cache, self._use_cache, fields=field_names)

        if isinstance(result, list):
            return [dict(zip(field_names, row, strict=False)) for row in result]
        return []

    async def values_list(self, *fields, flat: bool = False) -> list[Any] | list[tuple[Any, ...]]:
        """Get list of tuples or single values for the specified fields."""
        if not fields:
            raise ValueError("values_list() requires at least one field name")

        field_names = [self._get_field_name(f) for f in fields]

        query = self._builder.build(self._table)
        result = await self._executor.execute(query, "values_list", self._cache, self._use_cache, fields=field_names)

        if isinstance(result, list):
            if flat and len(field_names) == 1:
                return [row[0] for row in result]
            return [tuple(row) for row in result]
        return []

    async def aggregate(self, **kwargs) -> dict[str, Any]:
        """Perform aggregation operations on the QuerySet."""
        aggregations = []
        labels = []

        for alias, expr in kwargs.items():
            if hasattr(expr, "resolve"):
                aggregations.append(expr.resolve(self._table).label(alias))
            else:
                aggregations.append(expr.label(alias))
            labels.append(alias)

        query = self._builder.build(self._table)
        result = await self._executor.execute(
            query, "aggregate", self._cache, self._use_cache, aggregations=aggregations
        )

        if isinstance(result, list) and result:
            first_result = result[0]
            return dict(zip(labels, first_result, strict=False))
        return {}

    async def iterator(self, chunk_size: int = 1000) -> AsyncGenerator[T, None]:
        """Async iterator for processing large datasets in chunks."""
        query = self._builder.build(self._table)
        async for item in self._executor.iterator(query, chunk_size):
            yield item

    async def raw(self, sql: str, params: dict | None = None) -> list[T]:
        """Execute raw SQL query and return model instances."""
        if not self._executor.session:
            return []

        query = text(sql)
        result = await self._executor.session.execute(query, params or {})

        instances = []
        for row in result:
            if hasattr(row, "_mapping"):
                data = dict(row._mapping)  # noqa
            else:
                column_names = [col.name for col in self._table.columns]  # noqa
                data = dict(zip(column_names, row, strict=False))

            table_columns = {col.name for col in self._table.columns}  # noqa
            filtered_data = {k: v for k, v in data.items() if k in table_columns}

            if filtered_data:
                instances.append(self._model_class(**filtered_data))

        return instances

    async def dates(self, field, kind: str, order: str = "ASC") -> list[date]:
        """Get unique date list for the specified date field.

        Args:
            field: Date field name (supports strings and field expressions)
            kind: Date precision ('year', 'month', 'day')
            order: Sort order ('ASC' or 'DESC')

        Returns:
            List of unique date objects truncated to specified precision
        """
        field_name = self._get_field_name(field)
        if field_name not in self._table.c:
            raise ValueError(f"Field '{field_name}' does not exist in table")

        field_col = self._table.c[field_name]

        # Get database dialect
        dialect_name = "unknown"
        if hasattr(self._executor, "session") and self._executor.session and hasattr(self._executor.session, "bind"):
            dialect_name = self._executor.session.bind.dialect.name

        # Database-specific date expression
        if dialect_name == "postgresql":
            if kind == "year":
                date_expr = func.date_trunc("year", field_col)
            elif kind == "month":
                date_expr = func.date_trunc("month", field_col)
            elif kind == "day":
                date_expr = func.date_trunc("day", field_col)
            else:
                raise ValueError(f"Unsupported date kind: {kind}")
        elif dialect_name == "sqlite":
            if kind == "year":
                date_expr = func.strftime("%Y-01-01", field_col)
            elif kind == "month":
                date_expr = func.strftime("%Y-%m-01", field_col)
            elif kind == "day":
                date_expr = func.date(field_col)
            else:
                raise ValueError(f"Unsupported date kind: {kind}")
        elif dialect_name == "mysql":
            if kind == "year":
                date_expr = func.date_format(field_col, "%Y-01-01")
            elif kind == "month":
                date_expr = func.date_format(field_col, "%Y-%m-01")
            elif kind == "day":
                date_expr = func.date(field_col)
            else:
                raise ValueError(f"Unsupported date kind: {kind}")
        else:
            # Fallback using extract
            if kind == "year":
                date_expr = func.extract("year", field_col)
            elif kind == "month":
                date_expr = func.extract("month", field_col)
            elif kind == "day":
                date_expr = func.extract("day", field_col)
            else:
                raise ValueError(f"Unsupported date kind: {kind}")

        query = select(date_expr.distinct().label("date_value")).select_from(self._table)

        if self._builder.conditions:
            query = query.where(and_(*self._builder.conditions))

        if order.upper() == "DESC":
            query = query.order_by(desc("date_value"))
        else:
            query = query.order_by(asc("date_value"))

        result = await self._executor.execute(query, "all", self._cache, self._use_cache)

        # Convert results to date objects
        dates = []
        for row in result:  # type: ignore[reportGeneralTypeIssues]
            value = row[0]
            if isinstance(value, str):
                dates.append(datetime.strptime(value, "%Y-%m-%d").date())
            elif isinstance(value, datetime):
                dates.append(value.date())
            elif isinstance(value, date):
                dates.append(value)
            elif isinstance(value, int | float):
                if kind == "year":
                    dates.append(date(int(value), 1, 1))
                else:
                    dates.append(date(2000, int(value) if kind == "month" else 1, int(value) if kind == "day" else 1))
            else:
                dates.append(date.fromisoformat(str(value)))

        return dates

    async def datetimes(self, field, kind: str, order: str = "ASC") -> list[datetime]:
        """Get unique datetime list for the specified datetime field.

        Args:
            field: Datetime field name (supports strings and field expressions)
            kind: Time precision ('year', 'month', 'day', 'hour', 'minute', 'second')
            order: Sort order ('ASC' or 'DESC')

        Returns:
            List of unique datetime objects truncated to specified precision
        """
        field_name = self._get_field_name(field)
        if field_name not in self._table.c:
            raise ValueError(f"Field '{field_name}' does not exist in table")

        field_col = self._table.c[field_name]

        # Get database dialect
        dialect_name = "unknown"
        if hasattr(self._executor, "session") and self._executor.session and hasattr(self._executor.session, "bind"):
            dialect_name = self._executor.session.bind.dialect.name

        # Database-specific datetime expression
        if dialect_name == "postgresql":
            if kind in ("year", "month", "day", "hour", "minute", "second"):
                datetime_expr = func.date_trunc(kind, field_col)
            else:
                raise ValueError(f"Unsupported datetime kind: {kind}")
        elif dialect_name == "sqlite":
            format_map = {
                "year": "%Y-01-01 00:00:00",
                "month": "%Y-%m-01 00:00:00",
                "day": "%Y-%m-%d 00:00:00",
                "hour": "%Y-%m-%d %H:00:00",
                "minute": "%Y-%m-%d %H:%M:00",
                "second": "%Y-%m-%d %H:%M:%S",
            }
            if kind not in format_map:
                raise ValueError(f"Unsupported datetime kind: {kind}")
            datetime_expr = func.strftime(format_map[kind], field_col)
        elif dialect_name == "mysql":
            format_map = {
                "year": "%Y-01-01 00:00:00",
                "month": "%Y-%m-01 00:00:00",
                "day": "%Y-%m-%d 00:00:00",
                "hour": "%Y-%m-%d %H:00:00",
                "minute": "%Y-%m-%d %H:%i:00",
                "second": "%Y-%m-%d %H:%i:%s",
            }
            if kind not in format_map:
                raise ValueError(f"Unsupported datetime kind: {kind}")
            datetime_expr = func.date_format(field_col, format_map[kind])
        else:
            # Fallback using extract
            if kind in ("year", "month", "day", "hour", "minute", "second"):
                datetime_expr = func.extract(kind, field_col)
            else:
                raise ValueError(f"Unsupported datetime kind: {kind}")

        query = select(datetime_expr.distinct().label("datetime_value")).select_from(self._table)

        if self._builder.conditions:
            query = query.where(and_(*self._builder.conditions))

        if order.upper() == "DESC":
            query = query.order_by(desc("datetime_value"))
        else:
            query = query.order_by(asc("datetime_value"))

        result = await self._executor.execute(query, "all", self._cache, self._use_cache)

        # Convert results to datetime objects
        datetimes = []
        for row in result:  # type: ignore[reportGeneralTypeIssues]
            value = row[0]
            if isinstance(value, str):
                datetimes.append(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
            elif isinstance(value, datetime):
                datetimes.append(value)
            elif isinstance(value, date):
                datetimes.append(datetime.combine(value, datetime.min.time()))
            elif isinstance(value, int | float):
                if kind == "year":
                    datetimes.append(datetime(int(value), 1, 1))
                else:
                    datetimes.append(datetime(2000, 1, 1))
            else:
                datetimes.append(datetime.fromisoformat(str(value)))

        return datetimes

    async def get_item(self, key) -> T | list[T]:
        """Get item by index or slice.

        Args:
            key: Integer index or slice object

        Returns:
            Single model instance for index, list for slice
        """
        if isinstance(key, slice):
            # Handle slice
            start = key.start or 0
            stop = key.stop
            if stop is not None:
                results = await self.offset(start).limit(stop - start).all()
            else:
                results = await self.offset(start).all()
            return results
        elif isinstance(key, int):
            # Handle single index
            if key < 0:
                raise ValueError("Negative indexing is not supported")
            result = await self.offset(key).limit(1).first()
            if result is None:
                raise IndexError("Index out of range")
            return result
        else:
            raise TypeError("Invalid key type for indexing")

    # ========================================
    # Data Operations Methods - Create, update, and delete data
    # ========================================

    async def create(self, validate: bool = True, **kwargs) -> T:
        """Create new object with given field values."""
        # Create instance for validation
        instance = self._model_class(**kwargs)
        if validate and hasattr(instance, "validate_all"):
            validate_method = getattr(instance, "validate_all", None)
            if validate_method:
                validate_method()

        # Actual insertion would be implemented here
        # For now, return the created instance (simplified)
        return instance

    async def update(self, **values) -> int:
        """Perform bulk update on objects matching query conditions."""
        query = self._builder.build(self._table)
        result = await self._executor.execute(query, "update", values=values)
        return result if isinstance(result, int) else 0

    async def delete(self) -> int:
        """Perform bulk delete on objects matching query conditions."""
        query = self._builder.build(self._table)
        result = await self._executor.execute(query, "delete")
        return result if isinstance(result, int) else 0

    # ========================================
    # Subquery Methods - Convert QuerySet to subquery expressions
    # ========================================

    def subquery(
        self, name: str | None = None, query_type: Literal["auto", "table", "scalar", "exists"] = "auto"
    ) -> SubqueryExpression:
        """Convert current QuerySet to subquery expression."""
        # Convert to SQLAlchemy query for SubqueryExpression
        # This would need integration with existing SubqueryExpression
        sqlalchemy_query = select(self._table)  # Simplified
        return SubqueryExpression(sqlalchemy_query, name, query_type)

    # ========================================
    # Utility Methods - Cache management and statistics
    # ========================================

    def get_instance_cache_stats(self) -> dict[str, Any]:
        """Get instance cache statistics."""
        return self._cache.get_stats()

    def clear_instance_cache(self) -> None:
        """Clear instance query cache."""
        self._cache.clear()

    @classmethod
    def get_cache_stats(cls) -> dict[str, Any]:
        """Get query cache statistics."""
        return {"hits": 0, "misses": 0, "hit_rate": 0, "cache_size": 0}

    @classmethod
    def clear_query_cache(cls) -> None:
        """Clear the query cache."""
        pass

    # ========================================
    # Magic Methods - Python protocol support
    # ========================================

    def __getitem__(self, key) -> "QuerySet[T]":
        """Support slice syntax access."""
        if isinstance(key, slice):
            start = key.start or 0
            stop = key.stop
            if stop is not None:
                return self.offset(start).limit(stop - start)
            else:
                return self.offset(start)
        elif isinstance(key, int):
            if key < 0:
                raise ValueError("Negative indexing is not supported")
            return self.offset(key).limit(1)
        else:
            raise TypeError("Invalid key type for indexing")

    def __aiter__(self) -> AsyncGenerator[T, None]:
        """Async iterator support."""
        return self.iterator()

    def __repr__(self) -> str:
        """String representation."""
        return f"<QuerySet: {self._model_class.__name__}>"
