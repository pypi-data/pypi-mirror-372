"""SQLObjects Expression System - Type-Safe and Performance-Optimized

This module provides a simplified expression system that directly uses SQLAlchemy
native expressions, offering type safety, high performance, and modern database
expression support without unnecessary abstraction layers.

Key Design Principles:
- Direct SQLAlchemy integration for zero-overhead abstraction
- Type safety through native SQLAlchemy field references
- Intelligent subquery support with automatic type inference
- Full compatibility with SQLAlchemy ecosystem

Usage Examples:
    # Direct field references with type safety
    User.name.upper()                    # Chain methods on fields
    User.age >= 18                       # Direct comparisons

    # Database functions
    func.concat(User.first_name, ' ', User.last_name)
    func.extract('year', User.created_at)

    # Complex expressions
    condition = and_(
        User.age >= 18,
        or_(User.role == 'admin', User.is_staff == True)
    )

    # Subqueries with intelligent type inference
    avg_salary = User.objects.aggregate(
        avg_sal=func.avg(User.salary)
    ).subquery(query_type="scalar")
"""

from typing import Any, Literal

from sqlalchemy import ColumnElement, func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Select, and_, asc, desc, exists, literal, not_, nullsfirst, nullslast, or_, text
from sqlalchemy.types import Boolean, String

from .exceptions import ValidationError


__all__ = [
    # Core expression building
    "func",
    "and_",
    "or_",
    "not_",
    "exists",
    "text",
    "literal",
    # Query ordering
    "asc",
    "desc",
    "nullsfirst",
    "nullslast",
    # Subquery support
    "SubqueryExpression",
    # Function mixins and expression
    "FunctionMixin",
    "ColumnFunctionMixin",
    "ColumnAttributeFunctionMixin",
    "StringFunctionMixin",
    "NumericFunctionMixin",
    "DateTimeFunctionMixin",
    "FunctionExpression",
]


class SubqueryExpression(ColumnElement):
    """Intelligent subquery expression supporting multiple SQLAlchemy subquery types.

    This class provides a unified interface for creating and managing different types
    of subqueries including table subqueries, scalar subqueries, and existence subqueries.
    It automatically handles type conversion and provides operator overloading for
    seamless integration with other expressions.

    Examples:
        >>> # Table subquery for JOIN operations
        >>> subq = User.objects.filter(age__gte=18).subquery()
        >>> # Scalar subquery for comparisons
        >>> avg_age = User.objects.aggregate(avg_age=func.avg(User.age)).subquery("scalar")
        >>> # Existence subquery for boolean conditions
        >>> has_posts = Post.objects.filter(author_id=User.id).subquery("exists")
    """

    inherit_cache = True  # Support SQLAlchemy caching

    def __init__(
        self, query: Select, name: str | None = None, query_type: Literal["auto", "table", "scalar", "exists"] = "auto"
    ):
        """Initialize subquery expression with intelligent type inference.

        Args:
            query: SQLAlchemy Select query to convert to subquery
            name: Optional alias name for the subquery
            query_type: Type of subquery ('auto', 'table', 'scalar', 'exists')

        Raises:
            ValidationError: If query_type is invalid
        """
        super().__init__()
        valid_types = {"auto", "table", "scalar", "exists"}
        if query_type not in valid_types:
            raise ValidationError(f"Unknown query type: {query_type}. Available types: {', '.join(valid_types)}")

        self.query = query
        self.name = name
        self.query_type = self._infer_type() if query_type == "auto" else query_type
        self._subquery = None
        self._scalar_subquery = None
        self._exists_subquery = None

    # SQLAlchemy type obtained dynamically through type attribute
    def __getattribute__(self, name):
        if name == "type":
            return self._get_expression_type() or super().__getattribute__(name)
        return super().__getattribute__(name)

    def _infer_type(self) -> str:
        """Automatically infer the appropriate subquery type based on query structure.

        Analyzes query characteristics including column count, aggregate functions,
        and LIMIT clauses to determine the most suitable subquery type.

        Returns:
            Inferred subquery type ('scalar', 'table', or 'exists')
        """
        try:
            structure = self._analyze_query_structure()

            # Rule 1: Clear scalar query characteristics
            if (
                structure["has_single_column"]
                and structure["has_aggregates"]
                and (structure["has_limit_one"] or structure["is_count_query"])
            ):
                return "scalar"

            # Rule 2: Single column aggregate query (commonly used for comparisons)
            if structure["has_single_column"] and structure["has_aggregates"]:
                return "scalar"

            # Rule 3: Multi-column queries default to table subquery
            if structure["column_count"] > 1:
                return "table"

            # Rule 4: Single column non-aggregate query (e.g., ID lists)
            if structure["has_single_column"] and not structure["has_aggregates"]:
                return "table"  # For IN conditions

            # Default: table subquery
            return "table"

        except Exception:  # noqa
            # Default to table subquery when inference fails
            return "table"

    def _analyze_query_structure(self) -> dict:
        """Analyze query structure to extract inference criteria.

        Examines various aspects of the query including SELECT columns,
        aggregate functions, LIMIT clauses, and annotations to provide
        data for intelligent type inference.

        Returns:
            Dictionary containing query structure analysis results
        """
        analysis = {
            "select_columns": [],
            "has_aggregates": False,
            "has_single_column": False,
            "has_limit_one": False,
            "has_annotations": False,
            "column_count": 0,
            "is_count_query": False,
        }

        try:
            # Analyze SELECT columns
            if hasattr(self.query, "selected_columns"):
                analysis["select_columns"] = list(self.query.selected_columns)  # noqa
                analysis["column_count"] = len(analysis["select_columns"])
                analysis["has_single_column"] = analysis["column_count"] == 1

            # Analyze aggregate functions (simplified detection)
            query_str = str(self.query).lower()
            aggregate_keywords = ["count(", "sum(", "avg(", "max(", "min("]
            analysis["has_aggregates"] = any(keyword in query_str for keyword in aggregate_keywords)

            # Analyze LIMIT clause
            analysis["has_limit_one"] = (
                hasattr(self.query, "_limit") and self.query._limit is not None and self.query._limit == 1  # noqa
            )

            # Detect count queries
            analysis["is_count_query"] = "count(" in query_str

        except Exception:  # noqa
            # Return safe defaults when analysis fails
            pass

        return analysis

    def _get_expression_type(self):
        """Infer SQLAlchemy type based on subquery type

        Returns:
            SQLAlchemy type object or None for table subqueries
        """
        if self.query_type == "exists":
            return Boolean()
        elif self.query_type == "scalar":
            return self._infer_scalar_type()
        else:  # "table"
            return None

    def _infer_scalar_type(self):
        """Infer the return type of scalar subquery

        Returns:
            SQLAlchemy type object based on column analysis
        """
        try:
            columns = list(self.query.selected_columns)  # noqa

            if len(columns) == 1:
                # Single column query: use the column's type directly
                return columns[0].type
            elif len(columns) > 1:
                # Multi-column query: find aggregate column (usually the last one)
                return self._find_aggregate_column_type(columns)
            else:
                # No column info: use default type
                return String()

        except Exception:  # noqa
            return String()

    @staticmethod
    def _find_aggregate_column_type(columns):
        """Find aggregate column type from multiple columns

        Args:
            columns: List of column objects to analyze

        Returns:
            SQLAlchemy type object of the aggregate column
        """
        # Strategy 1: Find columns with aggregate function labels
        for col in reversed(columns):  # Search from back to front
            if hasattr(col, "name") and col.name:
                # Check if column is generated by aggregate function
                if any(agg in str(col).lower() for agg in ["count", "sum", "avg", "max", "min"]):
                    return col.type

        # Strategy 2: Find annotate-generated column (usually the last one)
        last_column = columns[-1]
        if hasattr(last_column, "type"):
            return last_column.type

        # Strategy 3: Default type
        return String()

    def get_children(self, **kwargs):
        """Return child expressions for SQLAlchemy visitor pattern

        Args:
            **kwargs: Additional keyword arguments

        Returns:
            List containing the query object
        """
        return [self.query]

    def resolve(self, table_or_model=None) -> Any:
        """Resolve to appropriate SQLAlchemy object based on subquery type.

        Args:
            table_or_model: Table object or model class for field resolution (unused for subqueries)

        Returns:
            SQLAlchemy subquery object (Subquery, ScalarSelect, or Exists)

        Raises:
            ValidationError: If subquery conversion fails
        """
        _ = table_or_model  # use it to avoid unused argument warning

        try:
            if self.query_type == "scalar":
                return self._get_scalar_subquery()
            elif self.query_type == "exists":
                return self._get_exists_subquery()
            else:  # 'table'
                return self._get_table_subquery()
        except Exception as e:
            raise ValidationError(f"Subquery conversion failed: {e}") from e

    def _get_table_subquery(self):
        """Get table subquery (equivalent to SQLAlchemy subquery()).

        Creates a table subquery that can be used in JOIN operations
        and other table-level operations.

        Returns:
            SQLAlchemy Subquery object

        Raises:
            ValidationError: If subquery creation fails
        """
        if self._subquery is None:
            try:
                self._subquery = self.query.subquery(name=self.name)
            except Exception as e:
                raise ValidationError(f"Subquery build failed: {e}") from e
        return self._subquery

    def _get_scalar_subquery(self):
        """Get scalar subquery (equivalent to SQLAlchemy scalar_subquery()).

        Creates a scalar subquery that returns a single value and can be used
        in comparisons and arithmetic operations.

        IMPORTANT: This method handles multi-column queries (like from annotate())
        by extracting only the aggregate column. This is necessary because:
        1. SQLAlchemy allows multi-column scalar_subquery() calls without error
        2. But databases reject multi-column scalar subqueries at runtime with "row value misused"
        3. We need to extract the intended aggregate column for proper SQL generation

        Example problematic case:
            User.objects.annotate(avg_sal=func.avg(User.salary)).subquery("scalar")
            Original: SELECT users.id, users.name, avg(salary) AS avg_sal FROM users
            Fixed:    SELECT avg(salary) AS avg_sal FROM users WHERE ...

        Returns:
            SQLAlchemy ScalarSelect object

        Raises:
            ValidationError: If scalar subquery creation fails
        """
        if self._scalar_subquery is None:
            try:
                # Handle multi-column queries (e.g., from annotate()) by extracting aggregate columns
                columns = list(self.query.selected_columns)  # noqa
                if len(columns) > 1:
                    # Multi-column query: extract the aggregate column (usually the last one)
                    # This prevents "row value misused" database errors
                    agg_column = columns[-1]
                    from sqlalchemy import select

                    # Create new query with only the aggregate column
                    scalar_query = select(agg_column)
                    # Copy WHERE clause if exists
                    if hasattr(self.query, "whereclause") and self.query.whereclause is not None:
                        scalar_query = scalar_query.where(self.query.whereclause)
                    # Copy FROM clause
                    if hasattr(self.query, "table") and self.query.table is not None:  # type: ignore[reportAttributeAccessIssue]
                        scalar_query = scalar_query.select_from(self.query.table)  # type: ignore[reportAttributeAccessIssue]
                    elif hasattr(self.query, "froms") and self.query.froms:
                        scalar_query = scalar_query.select_from(*self.query.froms)
                    self._scalar_subquery = scalar_query.scalar_subquery()
                else:
                    # Single column query: use as-is (safe for scalar subquery)
                    self._scalar_subquery = self.query.scalar_subquery()
            except Exception as e:
                raise ValidationError(f"Scalar subquery build failed: {e}") from e
        return self._scalar_subquery

    def _get_exists_subquery(self):
        """Get existence subquery (equivalent to SQLAlchemy exists()).

        Creates an existence subquery that returns a boolean value indicating
        whether any rows match the subquery conditions.

        Returns:
            SQLAlchemy Exists object

        Raises:
            ValidationError: If existence subquery creation fails
        """
        if self._exists_subquery is None:
            try:
                self._exists_subquery = exists(self.query)
            except Exception as e:
                raise ValidationError(f"Exists subquery build failed: {e}") from e
        return self._exists_subquery

    @property
    def c(self):
        """Access subquery columns (only applicable to table subqueries).

        Provides access to the columns of a table subquery, similar to
        SQLAlchemy's subquery.c attribute.

        Returns:
            Column collection for the table subquery

        Raises:
            ValidationError: If called on non-table subquery types
        """
        if self.query_type != "table":
            raise ValidationError(f"Column access not supported on {self.query_type} subquery")
        return self._get_table_subquery().c

    def alias(self, name: str) -> "SubqueryExpression":
        """Create an alias for the subquery.

        Args:
            name: Alias name for the subquery

        Returns:
            New SubqueryExpression with the specified alias
        """
        return SubqueryExpression(self.query, name, self.query_type)  # type: ignore[arg-type]

    def as_scalar(self) -> "SubqueryExpression":
        """Convert to scalar subquery type.

        Returns:
            New SubqueryExpression configured as scalar subquery
        """
        return SubqueryExpression(self.query, self.name, "scalar")

    def as_exists(self) -> "SubqueryExpression":
        """Convert to existence subquery type.

        Returns:
            New SubqueryExpression configured as existence subquery
        """
        return SubqueryExpression(self.query, self.name, "exists")

    def as_table(self) -> "SubqueryExpression":
        """Convert to table subquery type.

        Returns:
            New SubqueryExpression configured as table subquery
        """
        return SubqueryExpression(self.query, self.name, "table")


@compiles(SubqueryExpression)
def visit_subquery_expression(element, compiler, **kw):
    """SQLAlchemy compiler: compile SubqueryExpression to SQL

    Args:
        element: SubqueryExpression instance to compile
        compiler: SQLAlchemy compiler instance
        **kw: Additional compilation keywords

    Returns:
        Compiled SQL string
    """
    return compiler.process(element.resolve(), **kw)


# === Function Mixin System ===


class ColumnFunctionMixin:
    """Function mixin for Column descriptor fields"""

    def _get_expression(self):
        """Get expression from Column descriptor

        Returns:
            The column attribute from the descriptor
        """
        # New architecture: prioritize _column_attribute
        if hasattr(self, "_column_attribute") and self._column_attribute is not None:  # type: ignore[reportAttributeAccessIssue]
            return self._column_attribute  # type: ignore[reportAttributeAccessIssue]
        else:
            raise AttributeError("No expression available")


class ColumnAttributeFunctionMixin:
    """Function mixin for ColumnAttribute fields"""

    def _get_expression(self):
        """Get expression from ColumnAttribute

        Returns:
            The ColumnAttribute itself (inherits from CoreColumn)
        """
        return self


class FunctionMixin:
    """Function method mixin class to reduce code duplication

    Provides common database function methods that can be mixed into
    field classes and expression classes.
    """

    def _get_expression(self):
        """Abstract method - subclasses must implement this method

        Returns:
            The expression object to apply functions to

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement _get_expression()")

    def _create_result(self, func_call):  # noqa
        """Create FunctionExpression object

        Args:
            func_call: SQLAlchemy function call result

        Returns:
            FunctionExpression wrapping the function call
        """
        return FunctionExpression(func_call)

    # === General functions ===
    def cast(self, type_: str, **kwargs) -> "FunctionExpression":
        """Cast expression to specified type

        Args:
            type_: Target type name
            **kwargs: Additional type parameters

        Returns:
            FunctionExpression with cast operation
        """
        from .fields import create_type_instance

        sqlalchemy_type = create_type_instance(type_, kwargs)
        return self._create_result(func.cast(self._get_expression(), sqlalchemy_type))

    def is_null(self) -> ColumnElement[bool]:
        """Check if expression is NULL

        Returns:
            Boolean expression for NULL check
        """
        return self._get_expression().is_(None)

    def is_not_null(self) -> ColumnElement[bool]:
        """Check if expression is NOT NULL

        Returns:
            Boolean expression for NOT NULL check
        """
        return self._get_expression().is_not(None)

    def case(self, *conditions, else_=None) -> "FunctionExpression":
        """Create CASE expression

        Args:
            *conditions: Condition tuples or dictionary
            else_: Default value for ELSE clause

        Returns:
            FunctionExpression with CASE operation
        """
        if len(conditions) == 1 and isinstance(conditions[0], dict):
            cases = list(conditions[0].items())
        else:
            cases = conditions
        return self._create_result(func.case(*cases, else_=else_))

    def coalesce(self, *values) -> "FunctionExpression":
        """Return first non-NULL value

        Args:
            *values: Values to check for non-NULL

        Returns:
            FunctionExpression with COALESCE operation
        """
        return self._create_result(func.coalesce(self._get_expression(), *values))

    def nullif(self, value) -> "FunctionExpression":
        """Return NULL if expression equals value

        Args:
            value: Value to compare against

        Returns:
            FunctionExpression with NULLIF operation
        """
        return self._create_result(func.nullif(self._get_expression(), value))


class StringFunctionMixin(FunctionMixin):
    """String function mixin for text operations

    Provides string manipulation functions like upper, lower, trim, etc.
    """

    def upper(self) -> "FunctionExpression":
        """Convert string to uppercase"""
        return self._create_result(func.upper(self._get_expression()))

    def lower(self) -> "FunctionExpression":
        """Convert string to lowercase"""
        return self._create_result(func.lower(self._get_expression()))

    def trim(self) -> "FunctionExpression":
        """Remove leading and trailing whitespace"""
        return self._create_result(func.trim(self._get_expression()))

    def length(self) -> "FunctionExpression":
        """Get string length"""
        return self._create_result(func.length(self._get_expression()))

    def substring(self, start: int, length: int | None = None) -> "FunctionExpression":
        """Extract substring from string

        Args:
            start: Starting position (1-based)
            length: Optional length of substring
        """
        expr = self._get_expression()
        if length is not None:
            return self._create_result(func.substring(expr, start, length))
        return self._create_result(func.substring(expr, start))

    def regexp_replace(self, pattern: str, replacement: str) -> "FunctionExpression":
        """Replace text using regular expression

        Args:
            pattern: Regular expression pattern
            replacement: Replacement string
        """
        return self._create_result(func.regexp_replace(self._get_expression(), pattern, replacement))

    def split_part(self, delimiter: str, field: int) -> "FunctionExpression":
        """Split string and return specified part

        Args:
            delimiter: String delimiter
            field: Field number to return (1-based)
        """
        return self._create_result(func.split_part(self._get_expression(), delimiter, field))

    def position(self, substring: str) -> "FunctionExpression":
        """Find position of substring

        Args:
            substring: Substring to find
        """
        return self._create_result(func.position(substring, self._get_expression()))

    def reverse(self) -> "FunctionExpression":
        """Reverse string"""
        return self._create_result(func.reverse(self._get_expression()))

    def md5(self) -> "FunctionExpression":
        """Calculate MD5 hash of string"""
        return self._create_result(func.md5(self._get_expression()))


class NumericFunctionMixin(FunctionMixin):
    """Numeric function mixin for mathematical operations

    Provides mathematical functions like abs, round, sqrt, and aggregates.
    """

    def abs(self) -> "FunctionExpression":
        """Get absolute value"""
        return self._create_result(func.abs(self._get_expression()))

    def round(self, precision: int = 0) -> "FunctionExpression":
        """Round to specified precision

        Args:
            precision: Number of decimal places
        """
        return self._create_result(func.round(self._get_expression(), precision))

    def ceil(self) -> "FunctionExpression":
        """Round up to nearest integer"""
        return self._create_result(func.ceil(self._get_expression()))

    def floor(self) -> "FunctionExpression":
        """Round down to nearest integer"""
        return self._create_result(func.floor(self._get_expression()))

    def sqrt(self) -> "FunctionExpression":
        """Calculate square root"""
        return self._create_result(func.sqrt(self._get_expression()))

    def power(self, exponent) -> "FunctionExpression":
        """Raise to power

        Args:
            exponent: Exponent value
        """
        return self._create_result(func.power(self._get_expression(), exponent))

    def mod(self, divisor) -> "FunctionExpression":
        """Calculate modulo

        Args:
            divisor: Divisor value
        """
        return self._create_result(func.mod(self._get_expression(), divisor))

    def sign(self) -> "FunctionExpression":
        """Get sign of number (-1, 0, or 1)"""
        return self._create_result(func.sign(self._get_expression()))

    # Aggregate functions
    def sum(self) -> "FunctionExpression":
        """Calculate sum aggregate"""
        return self._create_result(func.sum(self._get_expression()))

    def avg(self) -> "FunctionExpression":
        """Calculate average aggregate"""
        return self._create_result(func.avg(self._get_expression()))

    def max(self) -> "FunctionExpression":
        """Calculate maximum aggregate"""
        return self._create_result(func.max(self._get_expression()))

    def min(self) -> "FunctionExpression":
        """Calculate minimum aggregate"""
        return self._create_result(func.min(self._get_expression()))

    def count(self) -> "FunctionExpression":
        """Calculate count aggregate"""
        return self._create_result(func.count(self._get_expression()))


class DateTimeFunctionMixin(FunctionMixin):
    """DateTime function mixin for date/time operations

    Provides date and time manipulation functions like extract, age, etc.
    """

    def extract(self, field: str) -> "FunctionExpression":
        """Extract date/time component

        Args:
            field: Component to extract (year, month, day, etc.)
        """
        return self._create_result(func.extract(field, self._get_expression()))

    def year(self) -> "FunctionExpression":
        """Extract year component"""
        return self._create_result(func.extract("year", self._get_expression()))

    def month(self) -> "FunctionExpression":
        """Extract month component"""
        return self._create_result(func.extract("month", self._get_expression()))

    def day(self) -> "FunctionExpression":
        """Extract day component"""
        return self._create_result(func.extract("day", self._get_expression()))

    def hour(self) -> "FunctionExpression":
        """Extract hour component"""
        return self._create_result(func.extract("hour", self._get_expression()))

    def minute(self) -> "FunctionExpression":
        """Extract minute component"""
        return self._create_result(func.extract("minute", self._get_expression()))

    def age_in_years(self) -> "FunctionExpression":
        """Calculate age in years from current date"""
        expr = self._get_expression()
        return self._create_result(func.extract("year", func.age(func.now(), expr)))

    def age_in_months(self) -> "FunctionExpression":
        """Calculate age in months from current date"""
        expr = self._get_expression()
        return self._create_result(func.extract("month", func.age(func.now(), expr)))

    def days_between(self, end_date) -> "FunctionExpression":
        """Calculate days between dates

        Args:
            end_date: End date for calculation
        """
        expr = self._get_expression()
        return self._create_result(func.extract("day", func.age(end_date, expr)))

    def date_trunc(self, precision: str) -> "FunctionExpression":
        """Truncate date to specified precision

        Args:
            precision: Precision level (day, month, year, etc.)
        """
        return self._create_result(func.date_trunc(precision, self._get_expression()))

    def to_char(self, format_str: str) -> "FunctionExpression":
        """Format date as string

        Args:
            format_str: Format string
        """
        return self._create_result(func.to_char(self._get_expression(), format_str))

    def add_days(self, days: int) -> "FunctionExpression":
        """Add days to date

        Args:
            days: Number of days to add
        """
        expr = self._get_expression()
        return self._create_result(expr + func.interval(f"{days} days"))


class FunctionExpression:
    """Function call result supporting continued method chaining

    Wraps SQLAlchemy function expressions and provides chainable methods
    for building complex database expressions.
    """

    # === Core Infrastructure ===

    def __init__(self, expression):
        """Initialize function expression

        Args:
            expression: SQLAlchemy expression object to wrap
        """
        self.expression = expression

    def __getattr__(self, name):
        """Proxy attribute access to underlying expression

        Args:
            name: Attribute name to access

        Returns:
            Attribute value from the underlying expression
        """
        return getattr(self.expression, name)

    # === String Functions ===

    def upper(self) -> "FunctionExpression":
        return FunctionExpression(func.upper(self.expression))

    def lower(self) -> "FunctionExpression":
        return FunctionExpression(func.lower(self.expression))

    def trim(self) -> "FunctionExpression":
        return FunctionExpression(func.trim(self.expression))

    def length(self) -> "FunctionExpression":
        return FunctionExpression(func.length(self.expression))

    def substring(self, start: int, length: int | None = None) -> "FunctionExpression":
        if length is not None:
            return FunctionExpression(func.substring(self.expression, start, length))
        return FunctionExpression(func.substring(self.expression, start))

    def regexp_replace(self, pattern: str, replacement: str) -> "FunctionExpression":
        return FunctionExpression(func.regexp_replace(self.expression, pattern, replacement))

    def position(self, substring: str) -> "FunctionExpression":
        return FunctionExpression(func.position(substring, self.expression))

    def split_part(self, delimiter: str, field: int) -> "FunctionExpression":
        return FunctionExpression(func.split_part(self.expression, delimiter, field))

    def reverse(self) -> "FunctionExpression":
        return FunctionExpression(func.reverse(self.expression))

    def md5(self) -> "FunctionExpression":
        return FunctionExpression(func.md5(self.expression))

    def concat(self, *args) -> "FunctionExpression":
        return FunctionExpression(func.concat(self.expression, *args))

    def left(self, length: int) -> "FunctionExpression":
        return FunctionExpression(func.left(self.expression, length))

    def right(self, length: int) -> "FunctionExpression":
        return FunctionExpression(func.right(self.expression, length))

    def lpad(self, length: int, fill_char: str = " ") -> "FunctionExpression":
        return FunctionExpression(func.lpad(self.expression, length, fill_char))

    def rpad(self, length: int, fill_char: str = " ") -> "FunctionExpression":
        return FunctionExpression(func.rpad(self.expression, length, fill_char))

    def ltrim(self, chars: str | None = None) -> "FunctionExpression":
        if chars:
            return FunctionExpression(func.ltrim(self.expression, chars))
        return FunctionExpression(func.ltrim(self.expression))

    def rtrim(self, chars: str | None = None) -> "FunctionExpression":
        if chars:
            return FunctionExpression(func.rtrim(self.expression, chars))
        return FunctionExpression(func.rtrim(self.expression))

    def replace(self, old: str, new: str) -> "FunctionExpression":
        return FunctionExpression(func.replace(self.expression, old, new))

    # === Numeric Functions ===

    def abs(self) -> "FunctionExpression":
        return FunctionExpression(func.abs(self.expression))

    def round(self, precision: int = 0) -> "FunctionExpression":
        return FunctionExpression(func.round(self.expression, precision))

    def ceil(self) -> "FunctionExpression":
        return FunctionExpression(func.ceil(self.expression))

    def floor(self) -> "FunctionExpression":
        return FunctionExpression(func.floor(self.expression))

    def sqrt(self) -> "FunctionExpression":
        return FunctionExpression(func.sqrt(self.expression))

    def power(self, exponent) -> "FunctionExpression":
        return FunctionExpression(func.power(self.expression, exponent))

    def mod(self, divisor) -> "FunctionExpression":
        return FunctionExpression(func.mod(self.expression, divisor))

    def sign(self) -> "FunctionExpression":
        return FunctionExpression(func.sign(self.expression))

    def trunc(self, precision: int = 0) -> "FunctionExpression":
        return FunctionExpression(func.trunc(self.expression, precision))

    def exp(self) -> "FunctionExpression":
        return FunctionExpression(func.exp(self.expression))

    def ln(self) -> "FunctionExpression":
        return FunctionExpression(func.ln(self.expression))

    def log(self, base: int = 10) -> "FunctionExpression":
        return FunctionExpression(func.log(base, self.expression))

    # === Aggregate Functions ===

    def sum(self) -> "FunctionExpression":
        return FunctionExpression(func.sum(self.expression))

    def avg(self) -> "FunctionExpression":
        return FunctionExpression(func.avg(self.expression))

    def max(self) -> "FunctionExpression":
        return FunctionExpression(func.max(self.expression))

    def min(self) -> "FunctionExpression":
        return FunctionExpression(func.min(self.expression))

    def count(self) -> "FunctionExpression":
        return FunctionExpression(func.count(self.expression))

    def count_distinct(self) -> "FunctionExpression":
        return FunctionExpression(func.count(func.distinct(self.expression)))

    def distinct(self) -> "FunctionExpression":
        return FunctionExpression(func.distinct(self.expression))

    # === Date/Time Functions ===

    def year(self) -> "FunctionExpression":
        return FunctionExpression(func.extract("year", self.expression))

    def month(self) -> "FunctionExpression":
        return FunctionExpression(func.extract("month", self.expression))

    def day(self) -> "FunctionExpression":
        return FunctionExpression(func.extract("day", self.expression))

    def hour(self) -> "FunctionExpression":
        return FunctionExpression(func.extract("hour", self.expression))

    def minute(self) -> "FunctionExpression":
        return FunctionExpression(func.extract("minute", self.expression))

    def extract(self, field: str) -> "FunctionExpression":
        return FunctionExpression(func.extract(field, self.expression))

    def date_trunc(self, precision: str) -> "FunctionExpression":
        return FunctionExpression(func.date_trunc(precision, self.expression))

    def age_in_years(self) -> "FunctionExpression":
        return FunctionExpression(func.extract("year", func.age(func.now(), self.expression)))

    def age_in_months(self) -> "FunctionExpression":
        return FunctionExpression(func.extract("month", func.age(func.now(), self.expression)))

    def days_between(self, end_date) -> "FunctionExpression":
        return FunctionExpression(func.extract("day", func.age(end_date, self.expression)))

    def to_char(self, format_str: str) -> "FunctionExpression":
        return FunctionExpression(func.to_char(self.expression, format_str))

    def add_days(self, days: int) -> "FunctionExpression":
        return FunctionExpression(self.expression + func.interval(f"{days} days"))

    # === General Functions ===

    def cast(self, type_: str, **kwargs) -> "FunctionExpression":
        from .fields import create_type_instance

        sqlalchemy_type = create_type_instance(type_, kwargs)
        return FunctionExpression(func.cast(self.expression, sqlalchemy_type))

    def coalesce(self, *values) -> "FunctionExpression":
        return FunctionExpression(func.coalesce(self.expression, *values))

    def nullif(self, value) -> "FunctionExpression":
        return FunctionExpression(func.nullif(self.expression, value))

    def case(self, *conditions, else_=None) -> "FunctionExpression":  # noqa
        if len(conditions) == 1 and isinstance(conditions[0], dict):
            cases = list(conditions[0].items())
        else:
            cases = conditions
        return FunctionExpression(func.case(*cases, else_=else_))

    def greatest(self, *args) -> "FunctionExpression":
        return FunctionExpression(func.greatest(self.expression, *args))

    def least(self, *args) -> "FunctionExpression":
        return FunctionExpression(func.least(self.expression, *args))

    # === SQLAlchemy Integration ===

    def label(self, name: str):
        return self.expression.label(name)

    def asc(self):
        return self.expression.asc()

    def desc(self):
        return self.expression.desc()

    # === Comparison Operators ===

    def __eq__(self, other) -> ColumnElement[bool]:  # type: ignore[reportIncompatibleMethodOverride]
        return self.expression == other  # noqa

    def __ne__(self, other) -> ColumnElement[bool]:  # type: ignore[reportIncompatibleMethodOverride]
        return self.expression != other  # noqa

    def __lt__(self, other) -> ColumnElement[bool]:
        return self.expression < other  # noqa

    def __le__(self, other) -> ColumnElement[bool]:
        return self.expression <= other  # noqa

    def __gt__(self, other) -> ColumnElement[bool]:
        return self.expression > other  # noqa

    def __ge__(self, other) -> ColumnElement[bool]:
        return self.expression >= other  # noqa

    def like(self, pattern: str) -> ColumnElement[bool]:
        return self.expression.like(pattern)

    def ilike(self, pattern: str) -> ColumnElement[bool]:
        return self.expression.ilike(pattern)

    def not_like(self, pattern: str) -> ColumnElement[bool]:
        return ~self.expression.like(pattern)

    def not_ilike(self, pattern: str) -> ColumnElement[bool]:
        return ~self.expression.ilike(pattern)

    def between(self, min_val, max_val) -> ColumnElement[bool]:
        return self.expression.between(min_val, max_val)

    def in_(self, values) -> ColumnElement[bool]:
        # Auto-wrap SubqueryExpression in list
        if isinstance(values, SubqueryExpression):
            values = [values]
        return self.expression.in_(values)

    def not_in(self, values) -> ColumnElement[bool]:
        # Auto-wrap SubqueryExpression in list
        if isinstance(values, SubqueryExpression):
            values = [values]
        return ~self.expression.in_(values)

    def is_(self, other) -> ColumnElement[bool]:
        return self.expression.is_(other)

    def is_not(self, other) -> ColumnElement[bool]:
        return self.expression.is_not(other)
