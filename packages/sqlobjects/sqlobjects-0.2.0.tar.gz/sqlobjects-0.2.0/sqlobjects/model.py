"""SQLObjects Model Module - Optimized core model implementation"""

from functools import lru_cache
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from sqlalchemy import Table, and_, delete, insert, select, update

from .exceptions import DeferredFieldError, PrimaryKeyError, ValidationError
from .fields import get_column_from_field, is_field_definition
from .history import HistoryTrackingMixin
from .metadata import ModelProcessor
from .session import AsyncSession, SessionContextManager
from .signals import Operation, SignalMixin, emit_signals


if TYPE_CHECKING:
    pass


__all__ = [
    "ObjectModel",
    "ModelMixin",
    "DeferredFieldProxy",
    "RelationFieldProxy",
    "StateManager",
    "BaseMixin",
    "SessionMixin",
    "PrimaryKeyMixin",
    "ValidationMixin",
    "DeferredLoadingMixin",
    "DataConversionMixin",
    "FieldCacheMixin",
]


class DeferredFieldProxy:
    """Optimized proxy for deferred fields with caching."""

    def __init__(self, instance: "DeferredLoadingMixin", field_name: str) -> None:
        self.instance = instance
        self.field_name = field_name
        self._cached_value = None
        self._is_loaded = False

    async def fetch(self) -> Any:
        """Fetch field value, auto-loading if not loaded."""
        if not self._is_loaded:
            await self.instance.load_deferred_field(self.field_name)
            self._cached_value = getattr(self.instance, self.field_name, None)
            self._is_loaded = True
        return self._cached_value

    def is_loaded(self) -> bool:
        return self.instance.is_field_loaded(self.field_name)

    def is_deferred(self) -> bool:
        return self.instance.is_field_deferred(self.field_name)

    def __iter__(self):
        raise DeferredFieldError(
            f"Cannot iterate over deferred field '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __len__(self):
        raise DeferredFieldError(
            f"Cannot get length of deferred field '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __bool__(self):
        raise DeferredFieldError(
            f"Cannot check boolean value of deferred field '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __getitem__(self, key):
        raise DeferredFieldError(
            f"Cannot access items of deferred field '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __contains__(self, item):
        raise DeferredFieldError(
            f"Cannot check containment in deferred field '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __add__(self, other):
        raise DeferredFieldError(
            f"Cannot perform arithmetic on deferred field '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __str__(self):
        return f"<DeferredField: {self.field_name}>"

    def __repr__(self):
        return f"DeferredFieldProxy(field_name='{self.field_name}')"


class RelationFieldProxy:
    """Optimized proxy for relationship fields with caching."""

    def __init__(self, instance: Any, field_name: str) -> None:
        self.instance = instance
        self.field_name = field_name
        self._cached_objects = None
        self._is_loaded = False

    async def fetch(self) -> Any:
        """Fetch relationship objects, auto-loading if not loaded."""
        if not self._is_loaded:
            await self._load_relationship()
            self._cached_objects = self._get_cached_objects()
            self._is_loaded = True
        return self._cached_objects

    def is_loaded(self) -> bool:
        cache_attr = f"_{self.field_name}_cache"
        return hasattr(self.instance, cache_attr)

    def is_deferred(self) -> bool:
        return not self.is_loaded()

    async def _load_relationship(self) -> None:
        """Load relationship using existing relationship loading logic."""
        if not hasattr(self.instance.__class__, "_relationships"):
            return

        relationships = getattr(self.instance.__class__, "_relationships", {})
        if self.field_name not in relationships:
            return

        relationship_desc = relationships[self.field_name]

        from .queries import QuerySet

        table = self.instance.get_table()
        queryset = QuerySet(table, self.instance.__class__)

        session = self.instance._get_session()  # noqa
        if hasattr(queryset, "_prefetch_relationship") and relationship_desc.property.resolved_model:
            await queryset._prefetch_relationship(  # noqa # type: ignore
                [self.instance], relationship_desc, relationship_desc.property.resolved_model, session
            )

    def _get_cached_objects(self) -> Any:
        cache_attr = f"_{self.field_name}_cache"
        return getattr(self.instance, cache_attr, None)

    def __iter__(self):
        raise DeferredFieldError(
            f"Cannot iterate over unloaded relationship '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __len__(self):
        raise DeferredFieldError(
            f"Cannot get length of unloaded relationship '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __bool__(self):
        raise DeferredFieldError(
            f"Cannot check boolean value of unloaded relationship '{self.field_name}' "
            f"on {self.instance.__class__.__name__}"
        )

    def __getitem__(self, key):
        raise DeferredFieldError(
            f"Cannot access items of unloaded relationship '{self.field_name}' on {self.instance.__class__.__name__}"
        )

    def __contains__(self, item):
        raise DeferredFieldError(
            f"Cannot check containment in unloaded relationship '{self.field_name}' "
            f"on {self.instance.__class__.__name__}"
        )

    def __add__(self, other):
        raise DeferredFieldError(
            f"Cannot perform arithmetic on unloaded relationship '{self.field_name}' "
            f"on {self.instance.__class__.__name__}"
        )

    def __str__(self):
        return f"<RelationField: {self.field_name}>"

    def __repr__(self):
        return f"RelationFieldProxy(field_name='{self.field_name}')"


class StateManager:
    """Unified state management for model instances."""

    def __init__(self):
        """Initialize empty state dictionary."""
        self._state: dict[str, Any] = {}

    def get(self, key: str, default=None):
        """Get state value by key.

        Args:
            key: State key to retrieve
            default: Default value if key not found

        Returns:
            State value or default
        """
        return self._state.get(key, default)

    def set(self, key: str, value):
        """Set state value by key.

        Args:
            key: State key to set
            value: Value to store
        """
        self._state[key] = value


class BaseMixin:
    """Base mixin with common functionality and state management."""

    if TYPE_CHECKING:
        __table__: ClassVar[Table]

    def __init__(self):
        """Initialize state manager if not already present."""
        if not hasattr(self, "_state_manager"):
            self._state_manager = StateManager()

    @classmethod
    def get_table(cls) -> Table:
        """Get SQLAlchemy Core Table definition.

        Returns:
            SQLAlchemy Table instance for this model
        """
        ...

    @classmethod
    @lru_cache(maxsize=1)
    def _get_field_names(cls) -> list[str]:
        """Get field names from the table definition (cached).

        Returns:
            List of field names from the table columns
        """
        return list(cls.get_table().columns.keys())


class SessionMixin(BaseMixin):
    """Session management - Layer 1."""

    def get_session(self) -> AsyncSession:
        """Get the effective session for database operations.

        Returns:
            AsyncSession instance for database operations
        """
        bound_session = self._state_manager.get("bound_session")
        if isinstance(bound_session, str):
            return SessionContextManager.get_session(bound_session)
        return bound_session or SessionContextManager.get_session()

    def using(self, db_or_session: str | AsyncSession):
        """Return self bound to specific database/connection.

        Args:
            db_or_session: Database name or AsyncSession instance

        Returns:
            Self with bound session for method chaining
        """
        self._state_manager.set("bound_session", db_or_session)
        return self


class PrimaryKeyMixin(SessionMixin):
    """Primary key operations - Layer 2."""

    @classmethod
    @lru_cache(maxsize=1)
    def _get_primary_key_info(cls) -> dict[str, Any]:
        """Cache primary key information at class level.

        Returns:
            Dictionary with 'columns' and 'names' keys containing
            primary key column objects and names respectively
        """
        table = cls.get_table()
        pk_columns = list(table.primary_key.columns)
        return {"columns": pk_columns, "names": [col.name for col in pk_columns]}

    def _get_primary_key_values(self) -> dict[str, Any]:
        """Get primary key values as dict.

        Returns:
            Dictionary mapping primary key field names to their values
        """
        pk_info = self._get_primary_key_info()
        return {name: getattr(self, name, None) for name in pk_info["names"]}

    def _has_primary_key_values(self) -> bool:
        """Check if instance has primary key values set.

        Returns:
            True if all primary key fields have non-None values
        """
        pk_values = self._get_primary_key_values()
        return all(value is not None for value in pk_values.values())

    def _build_pk_conditions(self) -> list:
        """Build primary key conditions for queries.

        Returns:
            List of SQLAlchemy condition expressions for primary key matching

        Raises:
            PrimaryKeyError: If primary key values are not set
        """
        if not self._has_primary_key_values():
            raise PrimaryKeyError("Cannot build conditions without primary key values")

        table = self.get_table()
        pk_values = self._get_primary_key_values()
        return [table.c[name] == value for name, value in pk_values.items()]


class ValidationMixin(PrimaryKeyMixin):
    """Validation logic - Layer 3."""

    def validate_field(self, field_name: str) -> None:
        """Validate a single field.

        Args:
            field_name: Name of the field to validate

        Raises:
            ValueError: If field does not exist
            ValidationError: If validation fails
        """
        if field_name not in self._get_field_names():
            raise ValueError(f"Field '{field_name}' does not exist")

        field_attr = getattr(self.__class__, field_name, None)
        if field_attr is not None and is_field_definition(field_attr):
            column = get_column_from_field(field_attr)
            validators = (
                column.info.get("_enhanced", {}).get("validators", []) if column is not None and column.info else []
            )
            if validators:
                value = getattr(self, field_name, None)
                try:
                    from .validators import validate_field_value

                    validated_value = validate_field_value(validators, value, field_name)
                    setattr(self, field_name, validated_value)
                except Exception as e:
                    raise ValidationError(str(e), field=field_name) from e

    def validate_all_fields(self, fields: list[str] | None = None) -> None:
        """Validate multiple fields efficiently.

        Args:
            fields: List of field names to validate, or None for all fields

        Raises:
            ValidationError: If any validation fails, with combined error messages
        """
        field_names = fields if fields is not None else self._get_field_names()
        errors = []
        for field_name in field_names:
            try:
                self.validate_field(field_name)
            except ValidationError as e:
                errors.append(e)
        if errors:
            error_messages = [str(e) for e in errors]
            raise ValidationError("; ".join(error_messages))


class DeferredLoadingMixin(ValidationMixin):
    """Deferred loading functionality - Layer 4."""

    def __init__(self):
        """Initialize deferred loading state."""
        super().__init__()
        self._state_manager.set("deferred_fields", set())
        self._state_manager.set("loaded_deferred_fields", set())
        self._state_manager.set("is_from_db", False)

    @property
    def _deferred_fields(self) -> set[str]:
        result = self._state_manager.get("deferred_fields", set())
        return result if isinstance(result, set) else set()

    @property
    def _loaded_deferred_fields(self) -> set[str]:
        result = self._state_manager.get("loaded_deferred_fields", set())
        return result if isinstance(result, set) else set()

    def get_deferred_fields(self) -> set[str]:
        """Get all deferred fields.

        Returns:
            Set of field names that are deferred
        """
        return self._deferred_fields.copy()

    def get_loaded_deferred_fields(self) -> set[str]:
        """Get loaded deferred fields.

        Returns:
            Set of deferred field names that have been loaded
        """
        return self._loaded_deferred_fields.copy()

    def is_field_deferred(self, field_name: str) -> bool:
        """Check if field is deferred.

        Args:
            field_name: Name of the field to check

        Returns:
            True if field is deferred
        """
        return field_name in self._deferred_fields

    def is_field_loaded(self, field_name: str) -> bool:
        """Check if deferred field is loaded.

        Args:
            field_name: Name of the field to check

        Returns:
            True if field is not deferred or has been loaded
        """
        if field_name not in self._deferred_fields:
            return True
        return field_name in self._loaded_deferred_fields

    def is_from_database(self) -> bool:
        """Check if instance was loaded from database.

        Returns:
            True if instance was loaded from database
        """
        result = self._state_manager.get("is_from_db", False)
        return bool(result)

    async def load_deferred_field(self, field_name: str) -> None:
        """Load a single deferred field.

        Args:
            field_name: Name of the field to load
        """
        await self.load_deferred_fields([field_name])

    async def load_deferred_fields(self, fields: list[str] | None = None) -> None:
        """Load multiple deferred fields efficiently.

        Args:
            fields: List of field names to load, or None for all deferred fields

        Raises:
            PrimaryKeyError: If primary key values are not set
        """
        table = self.get_table()

        pk_conditions = self._build_pk_conditions()
        if not all(value is not None for value in pk_conditions):
            raise PrimaryKeyError("Cannot load deferred fields without primary key")

        if fields is None:
            fields_to_load = self._deferred_fields - self._loaded_deferred_fields
        else:
            fields_to_load = set(fields) & self._deferred_fields - self._loaded_deferred_fields

        if not fields_to_load:
            return

        valid_fields = [f for f in fields_to_load if f in table.columns]
        if not valid_fields:
            return

        columns = [table.c[field] for field in valid_fields]
        stmt = select(*columns).where(and_(*pk_conditions))

        session = self.get_session()
        result = await session.execute(stmt)
        row = result.first()

        if row:
            loaded_fields = self._state_manager.get("loaded_deferred_fields", set())
            if isinstance(loaded_fields, set):
                for i, field in enumerate(valid_fields):
                    setattr(self, field, row[i])
                    loaded_fields.add(field)


class DataConversionMixin(DeferredLoadingMixin):
    """Data conversion functionality - Layer 5."""

    def to_dict(
        self,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        include_deferred: bool = False,
        safe_access: bool = True,
    ) -> dict[str, Any]:
        """Convert model instance to dictionary.

        Args:
            include: List of fields to include, or None for all fields
            exclude: List of fields to exclude
            include_deferred: Whether to include deferred fields
            safe_access: Whether to skip unloaded deferred fields safely

        Returns:
            Dictionary representation of the model instance
        """
        all_fields = set(self._get_field_names())

        if include is not None:
            fields = set(include) & all_fields
        else:
            fields = all_fields

        if exclude is not None:
            fields = fields - set(exclude)

        if not include_deferred:
            fields = fields - self._deferred_fields

        result = {}
        for field in fields:
            if safe_access and field in self._deferred_fields and field not in self._loaded_deferred_fields:
                continue
            try:
                result[field] = getattr(self, field)
            except AttributeError:
                if not safe_access:
                    raise
                continue

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any], validate: bool = True):
        """Create model instance from dictionary with validation.

        Args:
            data: Dictionary of field values
            validate: Whether to validate fields after creation

        Returns:
            New model instance created from dictionary data
        """
        all_fields = set(cls._get_field_names())
        filtered_data = {k: v for k, v in data.items() if k in all_fields}

        table = cls.get_table()
        for col in table.columns:  # noqa
            if col.name not in filtered_data:
                field_attr = getattr(cls, col.name, None)
                if field_attr is not None and hasattr(field_attr, "get_default_factory"):
                    factory = field_attr.get_default_factory()
                    if factory and callable(factory):
                        filtered_data[col.name] = factory()
                        continue

                if col.default is not None:
                    if hasattr(col.default, "is_scalar") and col.default.is_scalar:
                        filtered_data[col.name] = getattr(col.default, "arg", None)

        init_data = {}
        non_init_data = {}

        for field_name, value in filtered_data.items():
            field_attr = getattr(cls, field_name, None)
            if field_attr is not None and hasattr(field_attr, "get_codegen_params"):
                codegen_params = field_attr.get_codegen_params()
                if codegen_params.get("init", True):
                    init_data[field_name] = value
                else:
                    non_init_data[field_name] = value
            else:
                init_data[field_name] = value

        instance = cls(**init_data)  # noqa

        for field_name, value in non_init_data.items():
            setattr(instance, field_name, value)

        # Clear dirty fields since this is initial creation from dict
        dirty_fields = instance._state_manager.get("dirty_fields", set())
        if isinstance(dirty_fields, set):
            dirty_fields.clear()

        if validate:
            instance.validate_all_fields()

        return instance


class FieldCacheMixin(DataConversionMixin):
    """Field caching and attribute access optimization - Layer 6."""

    @classmethod
    def _get_field_cache(cls):
        """Auto-initialize and cache field information.

        Returns:
            Dictionary containing categorized field information
        """
        cache_attr = "_cached_field_info"
        if not hasattr(cls, cache_attr):
            setattr(cls, cache_attr, cls._build_field_cache())
        return getattr(cls, cache_attr)

    @classmethod
    def _build_field_cache(cls):
        """Build field cache with error handling.

        Returns:
            Dictionary with field categories: deferred_fields, relationship_fields, regular_fields
        """
        cache = {"deferred_fields": set(), "relationship_fields": set(), "regular_fields": set()}

        try:
            if hasattr(cls, "__table__"):
                table = getattr(cls, "__table__", None)
                if table is not None:
                    for col_name in table.columns.keys():
                        cls._categorize_field(col_name, cache)

            if hasattr(cls, "_relationships"):
                relationships = getattr(cls, "_relationships", {})
                cache["relationship_fields"].update(relationships.keys())
        except Exception:  # noqa
            pass

        return cache

    @classmethod
    def _categorize_field(cls, field_name, cache):
        """Categorize a single field into cache.

        Args:
            field_name: Name of the field to categorize
            cache: Cache dictionary to update
        """
        try:
            attr = getattr(cls, field_name, None)
            if attr is not None and is_field_definition(attr):
                # Check if this is a relationship field
                if hasattr(attr, "_is_relationship") and attr._is_relationship:  # noqa
                    cache["relationship_fields"].add(field_name)
                    return

                # Handle database field
                column = get_column_from_field(attr)
                if column is not None and hasattr(column, "info") and column.info is not None:
                    performance_params = column.info.get("_performance", {})
                    if performance_params.get("deferred", False):
                        cache["deferred_fields"].add(field_name)
                    else:
                        cache["regular_fields"].add(field_name)
                else:
                    cache["regular_fields"].add(field_name)
        except (AttributeError, TypeError):
            cache["regular_fields"].add(field_name)

    @classmethod
    def _invalidate_field_cache(cls):
        """Manually invalidate field cache.

        Use this when field definitions change at runtime.
        """
        cache_attr = "_cached_field_info"
        if hasattr(cls, cache_attr):
            delattr(cls, cache_attr)

    def __getattribute__(self, name: str):
        """Optimized attribute access using automatic field cache.

        Provides intelligent attribute access with proxy objects for
        deferred and relationship fields. Skips optimization for
        special attributes and methods to avoid recursion.

        Args:
            name: Attribute name to access

        Returns:
            Attribute value or proxy object
        """
        if name.startswith("_") or name in (
            "get_table",
            "load_deferred_fields",
            "validate_all_fields",
            "save",
            "delete",
            "refresh",
            "to_dict",
            "from_dict",
            "using",
            "is_field_deferred",
            "is_field_loaded",
            "get_deferred_fields",
            "_get_field_cache",
            "get_session",
            "validate_field",
            "load_deferred_field",
            "is_from_database",
        ):
            return super().__getattribute__(name)

        model_class = super().__getattribute__("__class__")
        field_cache = model_class._get_field_cache()  # noqa

        deferred_fields = field_cache.get("deferred_fields", set())
        if isinstance(deferred_fields, set) and name in deferred_fields:
            if (
                hasattr(self, "_state_manager")
                and self._state_manager.get("is_from_db", False)
                and name in self._deferred_fields
                and not self.is_field_loaded(name)
            ):
                proxy_cache = self._state_manager.get("proxy_cache", {})
                if isinstance(proxy_cache, dict) and name not in proxy_cache:
                    proxy_cache[name] = DeferredFieldProxy(self, name)
                    self._state_manager.set("proxy_cache", proxy_cache)
                if isinstance(proxy_cache, dict):
                    return proxy_cache[name]

        relationship_fields = field_cache.get("relationship_fields", set())
        if isinstance(relationship_fields, set) and name in relationship_fields:
            cache_name = f"_{name}_cache"
            try:
                if hasattr(self, cache_name):
                    cached_value = super().__getattribute__(cache_name)
                    if cached_value is not None:
                        return cached_value
            except AttributeError:
                pass

            proxy_cache = self._state_manager.get("proxy_cache", {})
            if isinstance(proxy_cache, dict) and name not in proxy_cache:
                proxy_cache[name] = RelationFieldProxy(self, name)
                self._state_manager.set("proxy_cache", proxy_cache)
            if isinstance(proxy_cache, dict):
                return proxy_cache[name]

        return super().__getattribute__(name)


# Type variable for ModelMixin
M = TypeVar("M", bound="ModelMixin")


class ModelMixin(FieldCacheMixin, SignalMixin, HistoryTrackingMixin):
    """Optimized mixin class with linear inheritance and performance improvements.

    Combines field caching, signal handling, and history tracking into a single
    optimized mixin. Provides core CRUD operations with intelligent dirty field
    tracking and efficient database operations.

    Features:
    - Automatic dirty field tracking for optimized updates
    - Signal emission for lifecycle events
    - History tracking for audit trails
    - Deferred loading support
    - Validation integration
    """

    @classmethod
    def get_table(cls):
        """Get SQLAlchemy Core Table definition.

        Returns:
            SQLAlchemy Table instance for this model

        Raises:
            AttributeError: If model has no __table__ attribute
        """
        table = getattr(cls, "__table__", None)
        if table is None:
            raise AttributeError(f"Model {cls.__name__} has no __table__ attribute")
        return table

    def __init__(self, **kwargs):
        """Initialize optimized model instance.

        Args:
            **kwargs: Field values to set on the instance
        """
        super().__init__()
        self._state_manager.set("dirty_fields", set())

        # Set history initialization flag before setting values
        if hasattr(self, "_history_initialized"):
            self._history_initialized = False

        # Set field values
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Enable history tracking after initialization
        if hasattr(self, "_history_initialized"):
            self._history_initialized = True

    def validate(self) -> None:
        """Model-level validation hook that subclasses can override.

        Override this method to implement custom model-level validation
        logic that goes beyond field-level validation.

        Raises:
            ValidationError: If validation fails
        """
        pass

    def _get_all_data(self) -> dict:
        """Get all field data.

        Returns:
            Dictionary mapping field names to their current values
        """
        return {name: getattr(self, name, None) for name in self._get_field_names()}

    def _get_dirty_data(self) -> dict:
        """Get modified field data.

        Returns:
            Dictionary mapping dirty field names to their current values,
            or all field data if no dirty fields are tracked
        """
        dirty_fields = self._state_manager.get("dirty_fields", set())
        if not dirty_fields:
            return self._get_all_data()
        return {name: getattr(self, name, None) for name in dirty_fields}

    def _set_primary_key_values(self, pk_values):
        """Set primary key values.

        Args:
            pk_values: Sequence of primary key values to set
        """
        table = self.get_table()
        pk_columns = list(table.primary_key.columns)
        for i, col in enumerate(pk_columns):
            if i < len(pk_values):
                setattr(self, col.name, pk_values[i])

    @emit_signals(Operation.SAVE)
    async def save(self, validate: bool = True):
        """Optimized save operation with better error handling.

        Automatically determines whether to INSERT or UPDATE based on
        primary key presence. Uses dirty field tracking for efficient
        updates that only modify changed fields.

        Args:
            validate: Whether to run validation before saving

        Returns:
            Self for method chaining

        Raises:
            PrimaryKeyError: If save operation fails
            ValidationError: If validation fails and validate=True
        """
        session = self.get_session()
        table = self.get_table()

        if validate:
            self.validate_all_fields()

        try:
            if self._has_primary_key_values():
                # UPDATE operation
                pk_conditions = self._build_pk_conditions()
                update_data = self._get_dirty_data()
                if update_data:
                    stmt = update(table).where(and_(*pk_conditions)).values(**update_data)
                    await session.execute(stmt)
            else:
                # INSERT operation
                stmt = insert(table).values(**self._get_all_data())
                result = await session.execute(stmt)
                if result.inserted_primary_key:
                    self._set_primary_key_values(result.inserted_primary_key)
        except Exception as e:
            raise PrimaryKeyError(f"Save operation failed: {e}") from e

        # Clear dirty fields after successful save
        dirty_fields = self._state_manager.get("dirty_fields", set())
        if isinstance(dirty_fields, set):
            dirty_fields.clear()
        return self

    @emit_signals(Operation.DELETE)
    async def delete(self):
        """Delete this model instance from the database.

        Raises:
            PrimaryKeyError: If instance has no primary key values or delete fails
        """
        session = self.get_session()
        table = self.get_table()

        if not self._has_primary_key_values():
            raise PrimaryKeyError("Cannot delete instance without primary key values")

        try:
            pk_conditions = self._build_pk_conditions()
            stmt = delete(table).where(and_(*pk_conditions))
            await session.execute(stmt)
        except Exception as e:
            raise PrimaryKeyError(f"Delete operation failed: {e}") from e

    async def refresh(self, fields: list[str] | None = None, include_deferred: bool = True):
        """Refresh this instance with the latest data from the database.

        Args:
            fields: Specific fields to refresh, or None for all fields
            include_deferred: Whether to include deferred fields in refresh

        Returns:
            Self for method chaining

        Raises:
            ValueError: If instance has no primary key values
        """
        session = self.get_session()
        table = self.get_table()

        if not self._has_primary_key_values():
            raise ValueError("Cannot refresh instance without primary key values")

        pk_conditions = self._build_pk_conditions()

        if fields:
            columns_to_select = [table.c[field] for field in fields]
        else:
            if not include_deferred:
                field_names = [f for f in self._get_field_names() if f not in self._deferred_fields]
                columns_to_select = [table.c[field] for field in field_names]
            else:
                columns_to_select = [table]

        stmt = select(*columns_to_select).where(and_(*pk_conditions))
        result = await session.execute(stmt)
        fresh_data = result.first()

        if fresh_data:
            loaded_deferred_fields = self._state_manager.get("loaded_deferred_fields", set())
            if isinstance(loaded_deferred_fields, set):
                if fields:
                    for i, field in enumerate(fields):
                        setattr(self, field, fresh_data[i])
                        if field in self._deferred_fields:
                            loaded_deferred_fields.add(field)
                else:
                    for col_name, value in fresh_data._mapping.items():  # noqa
                        setattr(self, col_name, value)
                        if col_name in self._deferred_fields:
                            loaded_deferred_fields.add(col_name)

        return self

    def __setattr__(self, name, value):
        """Track dirty fields when setting attributes.

        Automatically tracks field modifications for optimized UPDATE
        operations. Skips tracking for private attributes and during
        initialization.

        Args:
            name: Attribute name
            value: Attribute value
        """
        if not name.startswith("_") and hasattr(self, "_state_manager"):
            dirty_fields = self._state_manager.get("dirty_fields", set())
            if isinstance(dirty_fields, set):
                dirty_fields.add(name)
        super().__setattr__(name, value)


class ObjectModel(ModelMixin, metaclass=ModelProcessor):
    """Base model class with configuration support and common functionality.

    This is the main base class for all SQLObjects models. It combines
    the ModelProcessor metaclass for automatic table generation with
    the ModelMixin for runtime functionality.

    Features:
    - Automatic table generation from field definitions
    - Built-in CRUD operations with signal support
    - Query manager (objects) for database operations
    - Validation and history tracking
    - Deferred loading and field caching

    Usage:
        class User(ObjectModel):
            name: Column[str] = str_column(length=100)
            email: Column[str] = str_column(length=255, unique=True)
    """

    __abstract__ = True

    def __init_subclass__(cls, **kwargs):
        """Process subclass initialization and setup objects manager.

        Automatically sets up the objects manager for database operations
        and initializes validators for non-abstract model classes.

        Args:
            **kwargs: Additional keyword arguments passed to parent
        """
        super().__init_subclass__(**kwargs)

        # Check if this class explicitly defines __abstract__ in its own __dict__
        # If not, it's a concrete model (not abstract)
        is_abstract = cls.__dict__.get("__abstract__", False)

        # For concrete models, explicitly set __abstract__ = False to avoid inheritance confusion
        if not is_abstract:
            cls.__abstract__ = False

        # Setup objects manager for non-abstract models
        if not is_abstract and not hasattr(cls, "objects"):
            from .objects import ObjectsDescriptor

            cls.objects = ObjectsDescriptor(cls)

        # Setup validators if method exists
        setup_validators = getattr(cls, "_setup_validators", None)
        if setup_validators and callable(setup_validators):
            setup_validators()
