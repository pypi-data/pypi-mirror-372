"""SQLObjects Fields Module - Type-safe field definitions with enhanced functionality.

This module provides the core field system for SQLObjects, offering:
- Type-safe field definitions with comprehensive type annotations
- Enhanced SQLAlchemy types with database function chaining
- Unified field creation API with intelligent parameter handling
- Performance optimization features (deferred loading, caching)
- Code generation control for dataclass integration
- Validation system integration

Core Components:
- Column: Main field descriptor with full API compatibility
- ColumnAttribute: Enhanced column with model integration
- TypeRegistry: Centralized type system with comparator mapping
- Shortcut functions: Convenient field creation helpers

Example Usage:
    from sqlobjects.fields import column, StringColumn, IntegerColumn

    class User(ObjectModel):
        # Using column() function
        name: Column[str] = column(type="string", length=100)
        age: Column[int | None] = column(type="integer", nullable=True)

        # Using shortcut classes
        email: Column[str] = StringColumn(length=255, unique=True)
        score: Column[int] = IntegerColumn(default=0)
"""

import inspect
from collections.abc import Callable
from typing import Any, Generic, Literal, NotRequired, TypedDict, TypeVar, cast, overload

from sqlalchemy import Column as CoreColumn
from sqlalchemy import Computed, ForeignKey, Identity, func
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.sqltypes import (
    ARRAY,
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Double,
    Enum,
    Float,
    Integer,
    Interval,
    LargeBinary,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    TypeEngine,
    Uuid,
)

from .expressions import ColumnAttributeFunctionMixin, ColumnFunctionMixin, FunctionExpression
from .relations import M2MTable, relationship


__all__ = [
    # Core
    "Column",
    "column",
    "ColumnAttribute",
    "Auto",
    "ForeignKey",
    # Field compatibility
    "is_field_definition",
    "get_column_from_field",
    # Type system
    "register_field_type",
    "create_type_instance",
    "get_type_definition",
    # Column Types
    "StringColumn",
    "TextColumn",
    "IntegerColumn",
    "FloatColumn",
    "NumericColumn",
    "BooleanColumn",
    "DateTimeColumn",
    "BinaryColumn",
    "UuidColumn",
    "JsonColumn",
    "ArrayColumn",
    "EnumColumn",
    "IdentityColumn",
    "ComputedColumn",
    # Shortcut functions
    "identity",
    "computed",
    "foreign_key",
    # Relationship fields
    "M2MTable",
    "relationship",
    # Validation utilities
    "get_field_validators",
    "get_model_metadata",
]


# ===================================================================
# Type definitions and constants
# ===================================================================

T = TypeVar("T")
NullableT = TypeVar("NullableT")


class TypeArgument(TypedDict):
    """Type argument definition for SQLAlchemy type constructor parameters.

    Defines metadata for a single constructor parameter of a SQLAlchemy type,
    including validation rules and transformation functions.

    Attributes:
        name: Parameter name in the constructor
        type: Expected Python type for the parameter
        required: Whether the parameter is required
        default: Default value if parameter is not provided
        transform: Optional function to transform parameter value
        positional: Whether parameter can be passed positionally
    """

    name: str
    type: type[Any]
    required: bool
    default: Any
    transform: NotRequired[Callable[[Any], Any]]
    positional: NotRequired[bool]


class TypeConfig(TypedDict):
    """Type configuration for registry storage and retrieval.

    Internal storage format for type definitions in the TypeRegistry.

    Attributes:
        sqlalchemy_type: SQLAlchemy type class
        comparator_class: Comparator class for database functions
        default_params: Default construction parameters
        arguments: Constructor parameter definitions
    """

    sqlalchemy_type: type[Any]
    comparator_class: type[Any]
    default_params: dict[str, Any]
    arguments: list[TypeArgument]


class Auto(TypeEngine):
    """Automatic type inference placeholder for SQLAlchemy columns.

    Special type that indicates the actual type should be inferred from
    the Python type annotation or default value. Used as a placeholder
    during field definition and replaced with concrete type during
    model processing.

    Example:
        # Type inferred from annotation
        name: Column[str] = column()  # Uses Auto(), inferred as String
        age: Column[int] = column()   # Uses Auto(), inferred as Integer
    """

    def __init__(self):
        """Initialize Auto type instance.

        Creates a placeholder type that will be replaced during model processing
        with the appropriate concrete SQLAlchemy type.
        """
        super().__init__()


# ===================================================================
# Type system infrastructure
# ===================================================================


def _extract_constructor_params(type_class: type[Any]) -> list[TypeArgument]:
    """Extract constructor parameters from SQLAlchemy type class.

    Uses Python's inspect module to analyze the __init__ method signature
    and create TypeArgument definitions for each parameter.

    Args:
        type_class: SQLAlchemy type class to analyze

    Returns:
        List of TypeArgument definitions for constructor parameters

    Note:
        Returns empty list if inspection fails to ensure graceful degradation.
    """
    try:
        sig = inspect.signature(type_class.__init__)
        arguments = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            arguments.append(
                {
                    "name": param_name,
                    "type": Any,
                    "required": param.default == inspect.Parameter.empty,
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                }
            )
        return arguments
    except Exception:  # noqa
        return []


def _get_type_params(type_config: TypeConfig, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Extract and validate type construction parameters from user input.

    Processes user-provided kwargs to extract parameters relevant to the
    SQLAlchemy type constructor, applies transformations, and sets defaults.

    Args:
        type_config: Type configuration from registry
        kwargs: User-provided parameters

    Returns:
        Dictionary of validated parameters for type construction

    Note:
        Only includes parameters defined in type_config.arguments.
        Applies transformation functions if specified in argument definitions.
    """
    type_params = {}
    type_param_names = {arg["name"] for arg in type_config["arguments"]}

    for key, value in kwargs.items():
        if key in type_param_names:
            arg_def = next(arg for arg in type_config["arguments"] if arg["name"] == key)
            if "transform" in arg_def and arg_def["transform"]:
                value = arg_def["transform"](value)
            type_params[key] = value

    # Apply default values
    for arg in type_config["arguments"]:
        if arg["name"] not in type_params and not arg["required"] and arg["default"] is not None:
            default_value = arg["default"]
            if "transform" in arg and arg["transform"]:
                default_value = arg["transform"](default_value)
            type_params[arg["name"]] = default_value

    return type_params


def _transform_array_item_type(item_type: str | type[Any]) -> type[Any]:
    """Transform array item_type from string name to SQLAlchemy type instance.

    Converts string type names (like 'string', 'integer') to actual SQLAlchemy
    type instances for use in ARRAY type construction.

    Args:
        item_type: String type name or SQLAlchemy type class

    Returns:
        SQLAlchemy type instance for array items

    Raises:
        ValueError: If string type name is not registered in type registry
    """
    if isinstance(item_type, str):
        type_config = _registry.get_type_config(item_type)
        if type_config:
            return type_config["sqlalchemy_type"]()
        else:
            raise ValueError(f"Unknown array item type: {item_type}")
    return item_type


# ===================================================================
# Comparers and expression system
# ===================================================================


class ComparatorMixin:
    """Base mixin class providing common database function methods.

    Provides database-agnostic functions that work across all field types.
    These methods generate SQL function expressions that can be used in
    queries, annotations, and other database operations.

    All methods return FunctionExpression objects that can be chained
    with other query operations.
    """

    def cast(self, type_, **kwargs):
        """Cast column value to specified type.

        Args:
            type_: Target type name (string) or SQLAlchemy type
            **kwargs: Additional parameters for type construction

        Returns:
            FunctionExpression wrapping CAST SQL function

        Example:
            User.age.cast('string')  # CAST(age AS VARCHAR)
            User.score.cast('numeric', precision=10, scale=2)
        """
        sqlalchemy_type = create_type_instance(type_, kwargs)
        return FunctionExpression(func.cast(self, sqlalchemy_type))  # type: ignore[arg-type]

    def coalesce(self, *values):
        """Return first non-null value from arguments.

        Args:
            *values: Values to check for non-null

        Returns:
            FunctionExpression wrapping COALESCE SQL function

        Example:
            User.nickname.coalesce(User.username, 'Anonymous')
            # COALESCE(nickname, username, 'Anonymous')
        """
        return FunctionExpression(func.coalesce(self, *values))

    def nullif(self, value):
        """Return null if column equals value, otherwise return column.

        Args:
            value: Value to compare against

        Returns:
            FunctionExpression wrapping NULLIF SQL function

        Example:
            User.status.nullif('inactive')  # NULLIF(status, 'inactive')
        """
        return FunctionExpression(func.nullif(self, value))

    def case(self, *conditions, else_=None):  # noqa
        """Create conditional CASE expression.

        Args:
            *conditions: Condition tuples or dictionary mapping
            else_: Default value if no conditions match

        Returns:
            FunctionExpression wrapping CASE SQL expression

        Example:
            User.age.case(
                (User.age < 18, 'minor'),
                (User.age < 65, 'adult'),
                else_='senior'
            )
        """
        if len(conditions) == 1 and isinstance(conditions[0], dict):
            cases = list(conditions[0].items())
        else:
            cases = conditions
        return FunctionExpression(func.case(*cases, else_=else_))

    def greatest(self, *args):
        """Return greatest value among arguments.

        Args:
            *args: Values to compare

        Returns:
            FunctionExpression wrapping GREATEST SQL function

        Example:
            User.score.greatest(User.bonus, 100)  # GREATEST(score, bonus, 100)
        """
        return FunctionExpression(func.greatest(self, *args))

    def least(self, *args):
        """Return smallest value among arguments.

        Args:
            *args: Values to compare

        Returns:
            FunctionExpression wrapping LEAST SQL function

        Example:
            User.age.least(User.max_age, 120)  # LEAST(age, max_age, 120)
        """
        return FunctionExpression(func.least(self, *args))


class StringComparator(ComparatorMixin, String.Comparator):
    """String type comparator with comprehensive string function methods.

    Provides database string functions for text manipulation, searching,
    and formatting. All methods generate SQL function expressions that
    work across different database backends.

    Inherits from both ComparatorMixin (common functions) and
    String.Comparator (SQLAlchemy string operations).
    """

    # Basic string operations
    def upper(self):
        """Convert string to uppercase.

        Returns:
            FunctionExpression wrapping UPPER SQL function

        Example:
            User.username.upper()  # UPPER(username)
        """
        return FunctionExpression(func.upper(self))

    def lower(self):
        """Convert string to lowercase.

        Returns:
            FunctionExpression wrapping LOWER SQL function

        Example:
            User.email.lower()  # LOWER(email)
        """
        return FunctionExpression(func.lower(self))

    def trim(self):
        """Remove leading and trailing whitespace.

        Returns:
            FunctionExpression wrapping TRIM SQL function

        Example:
            User.bio.trim()  # TRIM(bio)
        """
        return FunctionExpression(func.trim(self))

    def length(self):
        """Return string length in characters.

        Returns:
            FunctionExpression wrapping LENGTH SQL function

        Example:
            User.username.length()  # LENGTH(username)
        """
        return FunctionExpression(func.length(self))

    def substring(self, start, length=None):
        """Extract substring from start position with optional length.

        Args:
            start: Starting position (1-based)
            length: Optional length of substring

        Returns:
            FunctionExpression wrapping SUBSTRING SQL function

        Example:
            User.username.substring(1, 3)  # SUBSTRING(username, 1, 3)
            User.email.substring(5)        # SUBSTRING(email FROM 5)
        """
        if length is not None:
            return FunctionExpression(func.substring(self, start, length))
        return FunctionExpression(func.substring(self, start))

    # Advanced string operations
    def regexp_replace(self, pattern, replacement, flags=None):  # type: ignore[override]
        """Replace text using regular expression pattern.

        Args:
            pattern: Regular expression pattern
            replacement: Replacement text
            flags: Optional regex flags (database-specific)

        Returns:
            FunctionExpression wrapping REGEXP_REPLACE SQL function

        Example:
            User.phone.regexp_replace(r'[^0-9]', '')  # Remove non-digits
        """
        if flags is not None:
            return FunctionExpression(func.regexp_replace(self, pattern, replacement, flags))  # noqa
        return FunctionExpression(func.regexp_replace(self, pattern, replacement))  # noqa

    def split_part(self, delimiter, field):
        """Split string by delimiter and return specified field.

        Args:
            delimiter: String delimiter to split on
            field: Field number to return (1-based)

        Returns:
            FunctionExpression wrapping SPLIT_PART SQL function

        Example:
            User.full_name.split_part(' ', 1)  # First name
            User.email.split_part('@', 2)      # Domain part
        """
        return FunctionExpression(func.split_part(self, delimiter, field))

    def position(self, substring):
        """Find position of substring in string.

        Args:
            substring: Substring to search for

        Returns:
            FunctionExpression wrapping POSITION SQL function

        Example:
            User.email.position('@')  # Position of @ symbol
        """
        return FunctionExpression(func.position(substring, self))

    def reverse(self):
        """Reverse string characters.

        Returns:
            FunctionExpression wrapping REVERSE SQL function

        Example:
            User.username.reverse()  # REVERSE(username)
        """
        return FunctionExpression(func.reverse(self))

    def md5(self):
        """Calculate MD5 hash of string.

        Returns:
            FunctionExpression wrapping MD5 SQL function

        Example:
            User.password.md5()  # MD5(password)
        """
        return FunctionExpression(func.md5(self))

    def concat(self, *args):  # type: ignore[override]
        """Concatenate strings together.

        Args:
            *args: Strings or expressions to concatenate

        Returns:
            FunctionExpression wrapping CONCAT SQL function

        Example:
            User.first_name.concat(' ', User.last_name)  # Full name
        """
        return FunctionExpression(func.concat(self, *args))  # noqa

    def left(self, length):
        """Return leftmost characters of specified length.

        Args:
            length: Number of characters to return

        Returns:
            FunctionExpression wrapping LEFT SQL function

        Example:
            User.username.left(3)  # First 3 characters
        """
        return FunctionExpression(func.left(self, length))

    def right(self, length):
        """Return rightmost characters of specified length.

        Args:
            length: Number of characters to return

        Returns:
            FunctionExpression wrapping RIGHT SQL function

        Example:
            User.username.right(3)  # Last 3 characters
        """
        return FunctionExpression(func.right(self, length))

    def lpad(self, length, fill_char=" "):
        """Left-pad string to specified length with fill character.

        Args:
            length: Target string length
            fill_char: Character to pad with (default: space)

        Returns:
            FunctionExpression wrapping LPAD SQL function

        Example:
            User.id.lpad(5, '0')  # Pad ID with zeros: '00123'
        """
        return FunctionExpression(func.lpad(self, length, fill_char))

    def rpad(self, length, fill_char=" "):
        """Right-pad string to specified length with fill character.

        Args:
            length: Target string length
            fill_char: Character to pad with (default: space)

        Returns:
            FunctionExpression wrapping RPAD SQL function

        Example:
            User.code.rpad(10, 'X')  # Pad code with X's
        """
        return FunctionExpression(func.rpad(self, length, fill_char))

    def ltrim(self, chars=None):
        """Remove specified characters from left side of string.

        Args:
            chars: Characters to remove (default: whitespace)

        Returns:
            FunctionExpression wrapping LTRIM SQL function

        Example:
            User.username.ltrim('_')  # Remove leading underscores
        """
        if chars:
            return FunctionExpression(func.ltrim(self, chars))
        return FunctionExpression(func.ltrim(self))

    def rtrim(self, chars=None):
        """Remove specified characters from right side of string.

        Args:
            chars: Characters to remove (default: whitespace)

        Returns:
            FunctionExpression wrapping RTRIM SQL function

        Example:
            User.username.rtrim('_')  # Remove trailing underscores
        """
        if chars:
            return FunctionExpression(func.rtrim(self, chars))
        return FunctionExpression(func.rtrim(self))

    def replace(self, old, new):
        """Replace all occurrences of old substring with new substring.

        Args:
            old: Substring to replace
            new: Replacement substring

        Returns:
            FunctionExpression wrapping REPLACE SQL function

        Example:
            User.phone.replace('-', '')  # Remove dashes from phone
        """
        return FunctionExpression(func.replace(self, old, new))


class IntegerComparator(ComparatorMixin, Integer.Comparator):
    """Integer type comparator with comprehensive mathematical functions.

    Provides database mathematical functions for numeric calculations,
    rounding, and aggregate operations. All methods generate SQL function
    expressions that work across different database backends.

    Inherits from both ComparatorMixin (common functions) and
    Integer.Comparator (SQLAlchemy integer operations).
    """

    # Basic mathematical functions
    def abs(self):
        """Return absolute value"""
        return FunctionExpression(func.abs(self))

    def sqrt(self):
        """Return square root"""
        return FunctionExpression(func.sqrt(self))

    def power(self, exponent):
        """Raise to specified power"""
        return FunctionExpression(func.power(self, exponent))

    def mod(self, divisor):
        """Return modulo (remainder) of division"""
        return FunctionExpression(func.mod(self, divisor))

    def sign(self):
        """Return sign of number (-1, 0, or 1)"""
        return FunctionExpression(func.sign(self))

    def exp(self):
        """Return e raised to the power of value"""
        return FunctionExpression(func.exp(self))

    def ln(self):
        """Return natural logarithm"""
        return FunctionExpression(func.ln(self))

    def log(self, base=10):
        """Return logarithm with specified base"""
        return FunctionExpression(func.log(base, self))

    # Aggregate functions
    def sum(self):
        """Calculate sum of values"""
        return FunctionExpression(func.sum(self))

    def avg(self):
        """Calculate average of values"""
        return FunctionExpression(func.avg(self))

    def count_distinct(self):
        """Count distinct values"""
        return FunctionExpression(func.count(func.distinct(self)))


class NumericComparator(ComparatorMixin, Numeric.Comparator):
    """Numeric type comparator for Float and Decimal types.

    Provides mathematical functions for floating-point and decimal numbers.
    Similar to IntegerComparator but optimized for decimal precision.

    Inherits from both ComparatorMixin (common functions) and
    Numeric.Comparator (SQLAlchemy numeric operations).
    """

    def abs(self):
        """Return absolute value of number.

        Returns:
            FunctionExpression wrapping ABS SQL function

        Example:
            User.balance.abs()  # ABS(balance)
        """
        return FunctionExpression(func.abs(self))

    def round(self, precision=0):
        """Round to specified decimal places"""
        return FunctionExpression(func.round(self, precision))

    def ceil(self):
        """Return smallest integer greater than or equal to value"""
        return FunctionExpression(func.ceil(self))

    def floor(self):
        """Return largest integer less than or equal to value"""
        return FunctionExpression(func.floor(self))

    def sqrt(self):
        """Return square root"""
        return FunctionExpression(func.sqrt(self))

    def power(self, exponent):
        """Raise to specified power"""
        return FunctionExpression(func.power(self, exponent))

    def sum(self):
        """Calculate sum of values"""
        return FunctionExpression(func.sum(self))

    def avg(self):
        """Calculate average of values"""
        return FunctionExpression(func.avg(self))


class DateTimeComparator(ComparatorMixin, DateTime.Comparator):
    """DateTime type comparator with comprehensive date/time functions.

    Provides database date/time functions for extraction, formatting,
    and calculations. All methods generate SQL function expressions
    that work across different database backends.

    Inherits from both ComparatorMixin (common functions) and
    DateTime.Comparator (SQLAlchemy datetime operations).
    """

    # Date component extraction
    def extract(self, field):
        """Extract specified field from date/time value.

        Args:
            field: Date/time field to extract (year, month, day, hour, etc.)

        Returns:
            FunctionExpression wrapping EXTRACT SQL function

        Example:
            User.created_at.extract('year')  # EXTRACT(year FROM created_at)
        """
        return FunctionExpression(func.extract(field, self))

    def year(self):
        """Extract year component from date/time.

        Returns:
            FunctionExpression wrapping EXTRACT(year) SQL function

        Example:
            User.birth_date.year()  # EXTRACT(year FROM birth_date)
        """
        return FunctionExpression(func.extract("year", self))

    def month(self):
        """Extract month component from date/time.

        Returns:
            FunctionExpression wrapping EXTRACT(month) SQL function

        Example:
            User.birth_date.month()  # EXTRACT(month FROM birth_date)
        """
        return FunctionExpression(func.extract("month", self))

    def day(self):
        """Extract day component from date/time.

        Returns:
            FunctionExpression wrapping EXTRACT(day) SQL function

        Example:
            User.birth_date.day()  # EXTRACT(day FROM birth_date)
        """
        return FunctionExpression(func.extract("day", self))

    def hour(self):
        """Extract hour component from date/time.

        Returns:
            FunctionExpression wrapping EXTRACT(hour) SQL function

        Example:
            User.last_login.hour()  # EXTRACT(hour FROM last_login)
        """
        return FunctionExpression(func.extract("hour", self))

    def minute(self):
        """Extract minute component from date/time.

        Returns:
            FunctionExpression wrapping EXTRACT(minute) SQL function

        Example:
            User.last_login.minute()  # EXTRACT(minute FROM last_login)
        """
        return FunctionExpression(func.extract("minute", self))

    # Date operations
    def date_trunc(self, precision):
        """Truncate date to specified precision.

        Args:
            precision: Precision level (year, month, day, hour, minute, second)

        Returns:
            FunctionExpression wrapping DATE_TRUNC SQL function

        Example:
            User.created_at.date_trunc('month')  # Start of month
        """
        return FunctionExpression(func.date_trunc(precision, self))

    def age_in_years(self):
        """Calculate age in years from current date.

        Returns:
            FunctionExpression calculating years between date and now

        Example:
            User.birth_date.age_in_years()  # Current age in years
        """
        return FunctionExpression(func.extract("year", func.age(func.now(), self)))

    def age_in_months(self):
        """Calculate age in months from current date.

        Returns:
            FunctionExpression calculating months between date and now

        Example:
            User.birth_date.age_in_months()  # Current age in months
        """
        return FunctionExpression(func.extract("month", func.age(func.now(), self)))

    def days_between(self, end_date):
        """Calculate days between this date and end_date.

        Args:
            end_date: End date for calculation

        Returns:
            FunctionExpression calculating days between dates

        Example:
            User.start_date.days_between(User.end_date)  # Duration in days
        """
        return FunctionExpression(func.extract("day", func.age(end_date, self)))

    def to_char(self, format_str):
        """Format date/time as string using format specification.

        Args:
            format_str: Format string (database-specific)

        Returns:
            FunctionExpression wrapping TO_CHAR SQL function

        Example:
            User.created_at.to_char('YYYY-MM-DD')  # Format as date string
        """
        return FunctionExpression(func.to_char(self, format_str))

    def add_days(self, days):
        """Add specified number of days to date.

        Args:
            days: Number of days to add

        Returns:
            FunctionExpression adding interval to date

        Example:
            User.start_date.add_days(30)  # Add 30 days
        """
        return FunctionExpression(self + func.interval(f"{days} days"))


class JSONComparator(ComparatorMixin, JSON.Comparator):
    """JSON type comparator with JSON extraction and manipulation methods.

    Provides database JSON functions for extracting values from JSON columns.
    Methods work with PostgreSQL JSON operators and similar functionality
    in other databases.

    Inherits from both ComparatorMixin (common functions) and
    JSON.Comparator (SQLAlchemy JSON operations).
    """

    def extract_path(self, path):
        """Extract JSON value at specified path.

        Args:
            path: JSON path expression

        Returns:
            FunctionExpression wrapping JSON_EXTRACT_PATH SQL function

        Example:
            User.metadata.extract_path('profile.name')  # Extract nested value
        """
        return FunctionExpression(func.json_extract_path(self, path))

    def extract_text(self, path):
        """Extract JSON value at specified path as text.

        Args:
            path: JSON path expression

        Returns:
            FunctionExpression wrapping JSON_EXTRACT_PATH_TEXT SQL function

        Example:
            User.settings.extract_text('theme')  # Extract as text value
        """
        return FunctionExpression(func.json_extract_path_text(self, path))


class BooleanComparator(ComparatorMixin, Boolean.Comparator):
    """Boolean type comparator with boolean check methods.

    Provides convenient methods for boolean value checking and comparison.
    Extends standard boolean operations with explicit true/false checks.

    Inherits from both ComparatorMixin (common functions) and
    Boolean.Comparator (SQLAlchemy boolean operations).
    """

    def is_true(self):
        """Check if boolean value is True.

        Returns:
            Boolean expression checking for True value

        Example:
            User.is_active.is_true()  # WHERE is_active IS TRUE
        """
        return self.is_(True)

    def is_false(self):
        """Check if boolean value is False.

        Returns:
            Boolean expression checking for False value

        Example:
            User.is_deleted.is_false()  # WHERE is_deleted IS FALSE
        """
        return self.is_(False)


class DefaultComparator(ComparatorMixin, TypeEngine.Comparator):
    """Default comparator for custom types."""

    pass


# ===================================================================
# Type registration system
# ===================================================================


class TypeRegistry:
    """Registry for SQLAlchemy types and comparator mappings.

    Central registry that manages the mapping between string type names
    and SQLAlchemy type classes, along with their associated comparator
    classes for database function support.

    Features:
    - Type registration with aliases
    - Automatic constructor parameter extraction
    - Enhanced type creation with comparators
    - Lazy initialization of built-in types

    Example:
        registry = TypeRegistry()
        registry.register_type(String, 'string', StringComparator)
        type_instance = registry.create_enhanced_type('string', length=100)
    """

    def __init__(self):
        """Initialize empty type registry.

        Creates an empty registry that will be populated with built-in types
        on first access. Uses lazy initialization for better startup performance.
        """
        self._type_configs: dict[str, TypeConfig] = {}
        self._aliases: dict[str, str] = {}
        self._initialized = False

    def register_type(
        self,
        field_type: type,
        name: str,
        comparator: type,
        aliases: list[str] | None = None,
        default_params: dict | None = None,
    ):
        """Register SQLAlchemy field type with associated comparator class and aliases.

        Args:
            field_type: SQLAlchemy type class to register
            name: Primary name for the type
            comparator: Comparator class providing database functions
            aliases: Alternative names for the type
            default_params: Default parameters for type construction

        Example:
            registry.register_type(
                String, 'string', StringComparator,
                aliases=['str'], default_params={'length': 255}
            )
        """
        # Extract constructor parameters
        arguments = _extract_constructor_params(field_type)

        config: TypeConfig = {
            "sqlalchemy_type": field_type,
            "comparator_class": comparator,
            "default_params": default_params or {},  # noqa
            "arguments": arguments,
        }

        self._type_configs[name] = config

        if aliases:
            for alias in aliases:
                self._aliases[alias] = name

    def get_type_config(self, name: str) -> TypeConfig:
        """Get complete type configuration by registered name or alias.

        Args:
            name: Type name or alias to look up

        Returns:
            Complete type configuration with SQLAlchemy type and comparator

        Raises:
            ValueError: If type name is not registered

        Example:
            config = registry.get_type_config('string')
            # Returns TypeConfig with String class and StringComparator
        """
        if not self._initialized:
            self._init_builtin_types()

        resolved_name = self._aliases.get(name, name)
        config = self._type_configs.get(resolved_name)
        if not config:
            available_types = list(self._type_configs.keys())
            raise ValueError(f"Unknown type: '{name}'. Available types: {available_types}")
        return config

    def create_enhanced_type(self, name: str, **params) -> Any:
        """Create SQLAlchemy type instance with enhanced comparator.

        Args:
            name: Type name to create
            **params: Parameters for type construction

        Returns:
            SQLAlchemy type instance with comparator_factory set

        Example:
            string_type = registry.create_enhanced_type('string', length=100)
            # Returns String(100) with StringComparator attached
        """
        config = self.get_type_config(name)

        # Extract valid type parameters using constructor analysis
        type_params = _get_type_params(config, params)
        final_params = {**config["default_params"], **type_params}

        # Special handling for ARRAY type
        if name == "array" and "item_type" in final_params:
            final_params["item_type"] = _transform_array_item_type(final_params["item_type"])

        type_instance = config["sqlalchemy_type"](**final_params)
        type_instance.comparator_factory = config["comparator_class"]

        return type_instance

    def _init_builtin_types(self):
        """Register all built-in SQLAlchemy types with their comparator mappings.

        Registers standard SQLAlchemy types (String, Integer, etc.) with
        their corresponding comparator classes and common aliases.
        Called automatically on first registry access.
        """
        # Use type: ignore to suppress pyright warnings while keeping code readable
        builtin_types = [
            (String, "string", StringComparator, ["str"], {"length": 255}),
            (Text, "text", StringComparator, [], {}),
            (Integer, "integer", IntegerComparator, ["int"], {}),
            (BigInteger, "bigint", IntegerComparator, [], {}),
            (SmallInteger, "smallint", IntegerComparator, [], {}),
            (Float, "float", NumericComparator, [], {}),
            (Double, "double", NumericComparator, [], {}),
            (Numeric, "numeric", NumericComparator, ["decimal"], {}),
            (Boolean, "boolean", BooleanComparator, ["bool"], {}),
            (DateTime, "datetime", DateTimeComparator, [], {}),
            (Date, "date", DateTimeComparator, [], {}),
            (Time, "time", DateTimeComparator, [], {}),
            (Interval, "interval", DateTimeComparator, [], {}),
            (LargeBinary, "binary", DefaultComparator, ["bytes"], {}),
            (Uuid, "uuid", StringComparator, [], {}),
            (JSON, "json", JSONComparator, ["dict"], {}),
        ]

        # Special types
        special_types = [
            (ARRAY, "array", DefaultComparator, [], {}),
            (Enum, "enum", DefaultComparator, [], {}),
            (Auto, "auto", DefaultComparator, [], {}),
        ]

        for field_type, name, comparator, aliases, defaults in builtin_types + special_types:
            self.register_type(field_type, name, comparator, aliases, defaults)

        self._initialized = True


# Global registry instance
_registry = TypeRegistry()


def register_field_type(
    field_type: type[Any],
    type_name: str,
    *,
    comparator: type[Any] | None = None,
    aliases: list[str] | None = None,
    default_params: dict[str, Any] | None = None,
) -> None:
    """Register a custom field type in the global registry.

    Allows registration of custom SQLAlchemy types for use with the
    column() function and type system.

    Args:
        field_type: SQLAlchemy type class to register
        type_name: Name to register the type under
        comparator: Custom comparator class (defaults to ComparatorMixin)
        aliases: Alternative names for the type
        default_params: Default parameters for type construction

    Example:
        from sqlalchemy import INET

        register_field_type(
            INET, 'inet',
            aliases=['ip_address'],
            default_params={}
        )

        # Now can use: column(type='inet') or column(type='ip_address')
    """
    _registry.register_type(
        field_type=field_type,
        name=type_name,
        comparator=comparator or ComparatorMixin,
        aliases=aliases,
        default_params=default_params,
    )


def create_type_instance(type_name: str, kwargs: dict[str, Any]) -> Any:
    """Create SQLAlchemy type instance from registered type name and parameters.

    Args:
        type_name: Registered type name (e.g., 'string', 'integer')
        kwargs: Parameters for type construction

    Returns:
        SQLAlchemy type instance with enhanced comparator

    Example:
        string_type = create_type_instance('string', {'length': 100})
        # Returns String(100) with StringComparator
    """
    return _registry.create_enhanced_type(type_name, **kwargs)


def get_type_definition(type_name: str) -> TypeConfig:
    """Get complete type configuration definition by registered name.

    Args:
        type_name: Registered type name to look up

    Returns:
        Complete type configuration with all metadata

    Example:
        config = get_type_definition('string')
        # Returns TypeConfig with String class, StringComparator, etc.
    """
    return _registry.get_type_config(type_name)


# ===================================================================
# Column implementation
# ===================================================================


class Column(ColumnFunctionMixin, Generic[T]):
    """Unified field descriptor supporting both database and relationship fields."""

    def __init__(self, **params):
        self._params = params
        self._column_attribute = None
        self._relationship_descriptor = None
        self._is_relationship = params.get("is_relationship", False)
        self._nullable = params.get("nullable", True)  # Store nullable info for type inference
        self.name = None
        self._private_name = None

    def __set_name__(self, owner, name):
        self.name = name
        self._private_name = f"_{name}"

        if self._is_relationship:
            self._setup_relationship(owner, name)
        else:
            self._setup_column(owner, name)

    def _setup_relationship(self, owner, name):
        """Set relationship field"""
        from .relations import RelationshipDescriptor

        relationship_property = self._params.get("relationship_property")
        if relationship_property:
            self._relationship_descriptor = RelationshipDescriptor(relationship_property)
            self._relationship_descriptor.__set_name__(owner, name)

    def _setup_column(self, owner, name):
        """Set database field"""
        params = self._params.copy()
        foreign_key = params.pop("foreign_key", None)  # noqa
        type_name = params.pop("type", "auto")

        # Process extended parameters
        info = params.pop("info", None) or {}

        # Collect code generation parameters
        codegen_params = {}
        for key in ["init", "repr", "compare", "hash", "kw_only"]:
            if key in params:
                codegen_params[key] = params.pop(key)

        # Collect performance parameters
        performance_params = {}
        for key in ["deferred", "deferred_group", "deferred_raiseload", "active_history"]:
            if key in params:
                performance_params[key] = params.pop(key)

        # Collect enhanced parameters
        enhanced_params = {}
        for key in ["default_factory", "insert_default", "validators"]:
            if key in params:
                enhanced_params[key] = params.pop(key)

        # Apply intelligent defaults
        column_kwargs = {
            "primary_key": params.get("primary_key", False),
            "autoincrement": params.get("autoincrement", "auto"),
            "server_default": params.get("server_default"),
        }
        codegen_params = _apply_codegen_defaults(codegen_params, column_kwargs)

        # Store parameters to info
        info["_codegen"] = codegen_params
        info["_performance"] = performance_params
        info["_enhanced"] = enhanced_params

        # Handle default value logic
        default = params.get("default")
        default_factory = enhanced_params.get("default_factory")
        insert_default = enhanced_params.get("insert_default")
        final_default = _resolve_default_value(default, default_factory, insert_default)
        if final_default is not None:
            params["default"] = final_default

        # Separate type parameters and column parameters
        type_params = _extract_type_params(params)
        column_params = _extract_column_params(params)
        column_params["info"] = info

        # Remove potentially conflicting parameters
        params.pop("name", None)
        type_params.pop("name", None)

        # Create enhanced type
        enhanced_type = create_type_instance(type_name, type_params)

        # foreign_key - passed as explicit parameter
        self._column_attribute = ColumnAttribute(
            name, enhanced_type, foreign_key=foreign_key, model_class=owner, **column_params
        )

    @overload
    def __get__(self, instance: None, owner: type) -> "ColumnAttribute[T]": ...

    @overload
    def __get__(self, instance: Any, owner: type) -> T: ...

    def __get__(self, instance, owner):
        if self._is_relationship and self._relationship_descriptor:
            return self._relationship_descriptor.__get__(instance, owner)
        else:
            if instance is None:
                return self._column_attribute
            else:
                # For non-nullable fields, cast to T; for nullable fields, cast to T | None
                value = getattr(instance, self._private_name or f"_{self.name}", None)
                if self._nullable:
                    return cast(T | None, value)
                else:
                    return cast(T, value)

    def __set__(self, instance, value):
        if self._is_relationship:
            # Relationship fields may not support direct setting
            pass
        else:
            if instance is None:
                raise AttributeError("Cannot set attribute on class")
            if self._private_name is not None:
                setattr(instance, self._private_name, value)

    def _get_expression(self):
        """Get expression object for ColumnFunctionMixin"""
        return self._column_attribute


class ColumnAttribute(CoreColumn, ColumnAttributeFunctionMixin, Generic[T]):
    """Enhanced column attribute with SQLAlchemy CoreColumn compatibility.

    Extends SQLAlchemy's Column with additional functionality for validation,
    performance optimization, and code generation control. Used when accessing
    fields on model classes for query building.

    Features:
    - Validation system integration
    - Deferred loading support
    - Code generation parameter control
    - Enhanced default value handling
    - Performance optimization settings

    Example:
        # Accessed when building queries
        User.name  # Returns ColumnAttribute instance
        User.objects.filter(User.name == 'John')  # Uses ColumnAttribute
    """

    inherit_cache = True  # make use of the cache key generated by the superclass from SQLAlchemy

    def __init__(self, name, type_, foreign_key=None, *, model_class, **kwargs):  # noqa
        # Extract enhanced parameters from info dict
        info = kwargs.get("info", {})
        enhanced_params = info.get("_enhanced", {})
        performance_params = info.get("_performance", {})
        codegen_params = info.get("_codegen", {})

        # Filter out invalid SQLAlchemy Column parameters
        valid_kwargs = _extract_column_params(kwargs)

        # Call CoreColumn initialization with optional ForeignKey
        if foreign_key is not None:
            super().__init__(name, type_, foreign_key, **valid_kwargs)
        else:
            super().__init__(name, type_, **valid_kwargs)

        # Save enhanced functionality parameters
        self.model_class = model_class
        self._enhanced_params = enhanced_params
        self._performance_params = performance_params
        self._codegen_params = codegen_params

    # === Core functionality interfaces ===

    # Validation related
    @property
    def validators(self) -> list[Any]:
        return self._enhanced_params.get("validators", [])

    def validate_value(self, value: Any, field_name: str) -> Any:
        """Validate field value using registered validators"""
        validators = self.validators
        if validators:
            from .validators import validate_field_value

            return validate_field_value(validators, value, field_name)
        return value

    # Default value related
    def get_default_factory(self) -> Callable[[], Any] | None:
        return self._enhanced_params.get("default_factory")

    def get_insert_default(self) -> Any:
        return self._enhanced_params.get("insert_default")

    def has_insert_default(self) -> bool:
        return "insert_default" in self._enhanced_params

    def get_effective_default(self) -> Any:
        """Get effective default value by priority order"""
        if self.default is not None:
            return self.default

        default_factory = self.get_default_factory()
        if default_factory is not None:
            return default_factory

        insert_default = self.get_insert_default()
        if insert_default is not None:
            return insert_default

        return None

    # Performance optimization related
    @property
    def is_deferred(self) -> bool:
        return self._performance_params.get("deferred", False)

    @property
    def deferred_group(self) -> str | None:
        return self._performance_params.get("deferred_group")

    @property
    def has_active_history(self) -> bool:
        return self._performance_params.get("active_history", False)

    @property
    def deferred_raiseload(self) -> bool | None:
        return self._performance_params.get("deferred_raiseload")

    # Code generation related
    @property
    def include_in_init(self) -> bool | None:
        return self._codegen_params.get("init")

    @property
    def include_in_repr(self) -> bool | None:
        return self._codegen_params.get("repr")

    @property
    def include_in_compare(self) -> bool | None:
        return self._codegen_params.get("compare")

    @property
    def include_in_hash(self) -> bool | None:
        return self._codegen_params.get("hash")

    @property
    def is_kw_only(self) -> bool | None:
        return self._codegen_params.get("kw_only")

    # === General parameter access methods ===

    def get_param(self, category: str, name: str, default: Any = None) -> Any:
        """Get parameter from specified category"""
        param_dict = getattr(self, f"_{category}_params", {})
        return param_dict.get(name, default)

    def get_codegen_params(self) -> dict[str, Any]:
        """Get code generation parameters"""
        return self._codegen_params

    def get_field_metadata(self) -> dict[str, Any]:
        """Get complete field metadata information"""
        metadata = {
            "name": self.name,
            "type": str(self.type),
            "nullable": getattr(self, "nullable", True),
            "primary_key": getattr(self, "primary_key", False),
            "unique": getattr(self, "unique", False),
            "index": getattr(self, "index", False),
        }

        # Add comments and documentation
        if hasattr(self, "comment") and self.comment:
            metadata["comment"] = self.comment
        if hasattr(self, "doc") and self.doc:
            metadata["doc"] = self.doc

        # Add extended parameters
        if self._enhanced_params:
            metadata["enhanced"] = self._enhanced_params
        if self._performance_params:
            metadata["performance"] = self._performance_params
        if self._codegen_params:
            metadata["codegen"] = self._codegen_params

        return metadata


# ===================================================================
# Helper functions
# ===================================================================


def _extract_column_params(kwargs: dict) -> dict:
    """Extract SQLAlchemy Column parameters"""
    column_param_names = {
        "primary_key",
        "nullable",
        "default",
        "index",
        "unique",
        "autoincrement",
        "doc",
        "key",
        "onupdate",
        "comment",
        "system",
        "server_default",
        "server_onupdate",
        "quote",
        "info",
    }
    return {k: v for k, v in kwargs.items() if k in column_param_names}


def _extract_type_params(kwargs: dict) -> dict:
    """Extract type-specific parameters"""
    column_param_names = {
        "primary_key",
        "nullable",
        "default",
        "index",
        "unique",
        "autoincrement",
        "doc",
        "key",
        "onupdate",
        "comment",
        "system",
        "server_default",
        "server_onupdate",
        "quote",
        "info",
    }
    return {k: v for k, v in kwargs.items() if k not in column_param_names}


def _apply_codegen_defaults(codegen_params: dict, column_kwargs: dict) -> dict:
    """Apply default values for code generation parameters"""
    defaults = {"init": True, "repr": True, "compare": False, "hash": None, "kw_only": False}

    # Primary key fields: don't participate in initialization, but participate in comparison and display
    if column_kwargs.get("primary_key"):
        defaults.update({"init": False, "repr": True, "compare": True})

    # Auto-increment fields: only when it is True, don't participate in initialization
    if column_kwargs.get("autoincrement") is True:  # noqa
        defaults["init"] = False

    # Server default value fields: don't participate in initialization
    if column_kwargs.get("server_default") is not None:
        defaults["init"] = False

    # Apply defaults only for parameters not explicitly set or set to None
    for key, default_value in defaults.items():
        if key not in codegen_params or codegen_params[key] is None:
            codegen_params[key] = default_value

    return codegen_params


def _resolve_default_value(
    default: Any,
    default_factory: Callable[[], Any] | None,
    insert_default: Any,
) -> Any:
    """Resolve default value priority: default > default_factory > insert_default"""
    if default is not None:
        return default

    if default_factory is not None:
        # Wrap as SQLAlchemy compatible callable
        return lambda: default_factory()

    if insert_default is not None:
        # Support SQLAlchemy function expressions
        return insert_default

    return None


# ===================================================================
# Sshortcut types
# ===================================================================


class StringColumn(Column[str]):
    """String column type (type='string' or 'str')"""

    def __init__(
        self,
        *,
        length: int | None = None,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params: dict = {"type": "string", **locals()}
        params.pop("self")
        if length is not None:
            params["length"] = length
        super().__init__(**params)


class TextColumn(Column[str]):
    """Text column type (type='text')"""

    def __init__(
        self,
        *,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": "text", **locals()}
        params.pop("self")
        super().__init__(**params)


class IntegerColumn(Column[int]):
    """Integer column type (type='integer'/'bigint'/'smallint' or 'int')"""

    def __init__(
        self,
        *,
        type: Literal["integer", "bigint", "smallint", "int"] = "integer",  # noqa
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": type, **locals()}
        params.pop("self")
        super().__init__(**params)


class FloatColumn(Column[float]):
    """Float column type (type='float'/'double')"""

    def __init__(
        self,
        *,
        type: Literal["float", "double"] = "float",  # noqa
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": type, **locals()}
        params.pop("self")
        super().__init__(**params)


class NumericColumn(Column[Any]):
    """Numeric column type (type='numeric' or 'decimal')"""

    def __init__(
        self,
        *,
        precision: int | None = None,
        scale: int | None = None,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params: dict = {"type": "numeric", **locals()}
        params.pop("self")
        if precision is not None:
            params["precision"] = precision
        if scale is not None:
            params["scale"] = scale
        super().__init__(**params)


class BooleanColumn(Column[bool]):
    """Boolean column type (type='boolean' or 'bool')"""

    def __init__(
        self,
        *,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": "boolean", **locals()}
        params.pop("self")
        super().__init__(**params)


class DateTimeColumn(Column[Any]):
    """DateTime column type (type='datetime'/'date'/'time'/'interval')"""

    def __init__(
        self,
        *,
        type: Literal["datetime", "date", "time", "interval"] = "datetime",  # noqa
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": type, **locals()}
        params.pop("self")
        super().__init__(**params)


class BinaryColumn(Column[bytes]):
    """Binary column type (type='binary' or 'bytes')"""

    def __init__(
        self,
        *,
        length: int | None = None,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params: dict = {"type": "binary", **locals()}
        params.pop("self")
        if length is not None:
            params["length"] = length
        super().__init__(**params)


class UuidColumn(Column[str]):
    """UUID column type (type='uuid')"""

    def __init__(
        self,
        *,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": "uuid", **locals()}
        params.pop("self")
        super().__init__(**params)


class JsonColumn(Column[dict]):
    """JSON column type (type='json' or 'dict')"""

    def __init__(
        self,
        *,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": "json", **locals()}
        params.pop("self")
        super().__init__(**params)


class ArrayColumn(Column[list]):
    """Array column type (type='array')"""

    def __init__(
        self,
        item_type: str | type[Any],
        *,
        dimensions: int = 1,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": "array", "item_type": item_type, "dimensions": dimensions, **locals()}
        params.pop("self")
        params.pop("item_type")  # Already included above
        params.pop("dimensions")  # Already included above
        super().__init__(**params)


class EnumColumn(Column[Any]):
    """Enum column type (type='enum')"""

    def __init__(
        self,
        enum_class: type[Any],
        *,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_default: Any = None,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        params = {"type": "enum", "enum_class": enum_class, **locals()}
        params.pop("self")
        params.pop("enum_class")  # Already included above
        super().__init__(**params)


class IdentityColumn(Column[int]):
    """Identity column type with database-native auto-increment support"""

    def __init__(
        self,
        *,
        start: int = 1,
        increment: int = 1,
        minvalue: int | None = None,
        maxvalue: int | None = None,
        cycle: bool = False,
        cache: int | None = None,
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = True,  # Identity columns are typically primary keys
        nullable: bool = False,  # Identity columns are typically non-nullable
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = True,
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        # Validate parameters
        if start < 1:
            raise ValueError("Identity start value must be >= 1")
        if increment == 0:
            raise ValueError("Identity increment cannot be 0")

        # Create SQLAlchemy Identity object
        identity_col = Identity(
            start=start, increment=increment, minvalue=minvalue, maxvalue=maxvalue, cycle=cycle, cache=cache
        )

        # Prepare parameters
        params: dict = {"type": "integer", **locals()}
        params.pop("self")
        params.pop("start")
        params.pop("increment")
        params.pop("minvalue")
        params.pop("maxvalue")
        params.pop("cycle")
        params.pop("cache")
        params.pop("identity_col")
        params["server_default"] = identity_col
        params["autoincrement"] = True  # Identity columns should have autoincrement=True

        super().__init__(**params)


class ComputedColumn(Column[T]):
    """Computed column type with expression-based values"""

    def __init__(
        self,
        sqltext: str | ColumnElement,
        *,
        persisted: bool | None = None,
        column_type: str = "auto",
        # SQLAlchemy Column parameters
        name: str | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,  # Will be validated and rejected
        index: bool = False,
        unique: bool = False,
        autoincrement: str | bool = "auto",
        doc: str | None = None,
        key: str | None = None,
        onupdate: Any = None,
        comment: str | None = None,
        system: bool = False,
        server_onupdate: Any = None,
        quote: bool | None = None,
        info: dict[str, Any] | None = None,
        # Enhanced functionality parameters
        default_factory: Callable[[], Any] | None = None,
        validators: list[Any] | None = None,
        deferred: bool = False,
        deferred_group: str | None = None,
        insert_default: Any = None,
        init: bool | None = None,
        repr: bool | None = None,  # noqa
        compare: bool | None = None,
        active_history: bool = False,
        deferred_raiseload: bool | None = None,
        hash: bool | None = None,  # noqa
        kw_only: bool | None = None,
        foreign_key: ForeignKey | None = None,  # noqa
    ):
        # Validate parameters
        if default is not None:
            raise ValueError("Computed columns cannot have default values")

        # Create SQLAlchemy Computed object
        computed_col = Computed(sqltext, persisted=persisted)

        # Prepare parameters
        params: dict = {"type": column_type, **locals()}
        params.pop("self")
        params.pop("sqltext")
        params.pop("persisted")
        params.pop("column_type")
        params.pop("computed_col")
        params["server_default"] = computed_col
        params.pop("default")  # Remove default since it's not allowed

        super().__init__(**params)


# ===================================================================
# Primary column functions
# ===================================================================


def column(
    *,
    type: str = "auto",  # noqa
    name: str | None = None,
    # SQLAlchemy Column parameters
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    autoincrement: str | bool = "auto",
    doc: str | None = None,
    key: str | None = None,
    onupdate: Any = None,
    comment: str | None = None,
    system: bool = False,
    server_default: Any = None,
    server_onupdate: Any = None,
    quote: bool | None = None,
    info: dict[str, Any] | None = None,
    # Essential functionality parameters
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    # Experience enhancement parameters
    deferred_group: str | None = None,
    insert_default: Any = None,
    init: bool | None = None,
    repr: bool | None = None,  # noqa
    compare: bool | None = None,
    # Advanced functionality parameters
    active_history: bool = False,
    deferred_raiseload: bool | None = None,
    hash: bool | None = None,  # noqa
    kw_only: bool | None = None,
    # Foreign key constraint
    foreign_key: ForeignKey | None = None,  # noqa
    # Type parameters (passed through **kwargs)
    **kwargs: Any,
) -> "Column[Any]":
    """Create field descriptor with new unified architecture"""
    # Collect all parameters
    all_params = {
        "type": type,
        "name": name,
        "primary_key": primary_key,
        "nullable": nullable,
        "default": default,
        "index": index,
        "unique": unique,
        "autoincrement": autoincrement,
        "doc": doc,
        "key": key,
        "onupdate": onupdate,
        "comment": comment,
        "system": system,
        "server_default": server_default,
        "server_onupdate": server_onupdate,
        "quote": quote,
        "info": info,
        "default_factory": default_factory,
        "validators": validators,
        "deferred": deferred,
        "deferred_group": deferred_group,
        "insert_default": insert_default,
        "init": init,
        "repr": repr,
        "compare": compare,
        "active_history": active_history,
        "deferred_raiseload": deferred_raiseload,
        "hash": hash,
        "kw_only": kw_only,
        "foreign_key": foreign_key,
        **kwargs,
    }

    # Pass parameters directly to new Column class
    return Column(**all_params)


def identity(
    *,
    start: int = 1,
    increment: int = 1,
    minvalue: int | None = None,
    maxvalue: int | None = None,
    cycle: bool = False,
    cache: int | None = None,
    **kwargs,
) -> IdentityColumn:
    """Create identity column with auto-increment functionality"""
    return IdentityColumn(
        start=start, increment=increment, minvalue=minvalue, maxvalue=maxvalue, cycle=cycle, cache=cache, **kwargs
    )


def computed(
    sqltext: str | ColumnElement, *, persisted: bool | None = None, column_type: str = "auto", **kwargs
) -> ComputedColumn:
    """Create computed column with expression-based values"""
    return ComputedColumn(sqltext=sqltext, persisted=persisted, column_type=column_type, **kwargs)


def foreign_key(
    reference: str,
    *,
    type: str = "integer",  # noqa
    nullable: bool = True,
    **kwargs: Any,
) -> "Column[int]":
    """Create foreign key column with reference constraint.

    Args:
        reference: Foreign key reference in format "table.column"
        type: Column type (default: "integer")
        nullable: Whether column can be null
        **kwargs: Additional column parameters

    Returns:
        Column descriptor with foreign key constraint

    Example:
        author_id: Column[int] = foreign_key("users.id")
        category_id: Column[int] = foreign_key("categories.id", nullable=False)
    """
    # Create ForeignKey constraint
    fk_constraint = ForeignKey(reference)

    # Use existing column() function with foreign key
    return column(
        type=type,
        nullable=nullable,
        foreign_key=fk_constraint,
        **kwargs,
    )


# ===================================================================
# Field and metadata utilities
# ===================================================================


def is_field_definition(attr) -> bool:
    """Check if attribute is a field definition.

    Determines whether an attribute represents a database field by checking
    for Column descriptor or ColumnAttribute characteristics.

    Args:
        attr: Attribute to check for field definition

    Returns:
        True if attribute is a field definition (Column descriptor or ColumnAttribute)

    Example:
        class User(ObjectModel):
            name = StringColumn()

        is_field_definition(User.name)  # True
        is_field_definition(User.__init__)  # False
    """
    from .relations import RelationshipDescriptor

    return (
        isinstance(attr, RelationshipDescriptor)  # Relationship fields
        or hasattr(attr, "_column_attribute")  # New architecture
        or isinstance(attr, CoreColumn)  # Direct ColumnAttribute
    )


def get_column_from_field(field_def):
    """Get SQLAlchemy Column object from field definition.

    Extracts the underlying SQLAlchemy Column from various field definition
    formats used in SQLObjects.

    Args:
        field_def: Field definition (Column descriptor or ColumnAttribute)

    Returns:
        SQLAlchemy Column object or None if not a field definition or is a relationship field

    Example:
        user_name_field = User.name  # Column descriptor
        column = get_column_from_field(user_name_field)
        # Returns underlying SQLAlchemy Column
    """
    # Check if it's a relationship field first
    if hasattr(field_def, "_is_relationship") and field_def._is_relationship:  # noqa
        return None
    # New architecture - Column descriptor with _column_attribute
    if hasattr(field_def, "_column_attribute"):
        return field_def._column_attribute  # noqa
    # Direct ColumnAttribute instance
    elif isinstance(field_def, CoreColumn):
        return field_def
    return None


def get_field_validators(model_class: type, field_name: str) -> list[Any]:
    """Get validator list for specified field.

    Args:
        model_class: Model class to inspect
        field_name: Name of field to get validators for

    Returns:
        List of validator functions for the field

    Example:
        validators = get_field_validators(User, 'email')
        # Returns list of validation functions
    """
    if hasattr(model_class, "_field_validators"):
        return model_class._field_validators.get(field_name, [])  # noqa
    return []


def get_model_metadata(model_class: type) -> dict[str, Any]:
    """Get complete metadata information for model.

    Extracts comprehensive metadata about a model class including
    field definitions, validators, and configuration.

    Args:
        model_class: Model class to inspect

    Returns:
        Dictionary containing complete model metadata

    Example:
        metadata = get_model_metadata(User)
        # {
        #     'model_name': 'User',
        #     'table_name': 'users',
        #     'fields': {...},
        #     'validators': {...},
        #     'config': {...}
        # }
    """
    metadata = {
        "model_name": model_class.__name__,
        "table_name": getattr(model_class.__table__, "name", None) if hasattr(model_class, "__table__") else None,
        "fields": {},
        "validators": getattr(model_class, "_field_validators", {}),
    }

    # Collect field metadata
    for name in dir(model_class):
        if name.startswith("_"):
            continue
        try:
            attr = getattr(model_class, name)
            if hasattr(attr, "get_field_metadata"):
                metadata["fields"][name] = attr.get_field_metadata()
        except Exception:  # noqa
            continue

    # Add model configuration information
    if hasattr(model_class, "Config"):
        config_attrs = {}
        config_class = model_class.Config
        for attr_name in dir(config_class):
            if not attr_name.startswith("_") and not callable(getattr(config_class, attr_name, None)):
                try:
                    value = getattr(config_class, attr_name)
                    if not callable(value):
                        config_attrs[attr_name] = (
                            str(value) if hasattr(value, "__iter__") and not isinstance(value, str | bytes) else value
                        )
                except Exception:  # noqa
                    continue
        if config_attrs:
            metadata["config"] = config_attrs

    return metadata
