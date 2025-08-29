"""SQLObjects relationship field system - unified relationship interface implementation"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, ForeignKey, Table, select


if TYPE_CHECKING:
    from .model import ObjectModel


__all__ = [
    "M2MTable",
    "RelationshipType",
    "RelationshipResolver",
    "RelationshipProperty",
    "RelationshipDescriptor",
    "RelatedObjectProxy",
    "BaseRelatedCollection",
    "OneToManyCollection",
    "M2MCollectionMixin",
    "M2MRelatedCollection",
    "RelatedQuerySet",
    "NoLoadProxy",
    "RaiseProxy",
    "relationship",
]


@dataclass
class M2MTable:
    """Many-to-Many table definition with flexible field mapping.

    Supports custom field names and non-primary key references for complex scenarios.
    """

    table_name: str
    left_model: str
    right_model: str
    left_field: str | None = None  # M2M table left foreign key field name
    right_field: str | None = None  # M2M table right foreign key field name
    left_ref_field: str | None = None  # Left model reference field name
    right_ref_field: str | None = None  # Right model reference field name

    def __post_init__(self):
        """Fill default field names if not provided."""
        if self.left_field is None:
            self.left_field = f"{self.left_model.lower()}_id"
        if self.right_field is None:
            self.right_field = f"{self.right_model.lower()}_id"
        if self.left_ref_field is None:
            self.left_ref_field = "id"
        if self.right_ref_field is None:
            self.right_ref_field = "id"

    def create_table(self, metadata: Any, left_table: Any, right_table: Any) -> Table:
        """Create SQLAlchemy Table for this M2M relationship.

        Args:
            metadata: SQLAlchemy MetaData instance
            left_table: Left model's table
            right_table: Right model's table

        Returns:
            SQLAlchemy Table instance for the M2M relationship
        """
        # Get reference columns
        left_ref_col = left_table.c[self.left_ref_field]
        right_ref_col = right_table.c[self.right_ref_field]

        return Table(
            self.table_name,
            metadata,
            Column(
                self.left_field,
                left_ref_col.type,
                ForeignKey(f"{left_table.name}.{self.left_ref_field}"),
                primary_key=True,
            ),
            Column(
                self.right_field,
                right_ref_col.type,
                ForeignKey(f"{right_table.name}.{self.right_ref_field}"),
                primary_key=True,
            ),
        )


class RelationshipType:
    """Relationship type enumeration."""

    MANY_TO_ONE = "many_to_one"
    ONE_TO_MANY = "one_to_many"
    ONE_TO_ONE = "one_to_one"
    MANY_TO_MANY = "many_to_many"


class RelationshipProperty:
    """Relationship property configuration and metadata."""

    def __init__(
        self,
        argument: str | type["ObjectModel"],
        foreign_keys: str | list[str] | None = None,
        back_populates: str | None = None,
        backref: str | None = None,
        lazy: str = "select",
        uselist: bool | None = None,
        secondary: str | None = None,
        primaryjoin: str | None = None,
        secondaryjoin: str | None = None,
        order_by: str | list[str] | None = None,
        cascade: str | None = None,
        passive_deletes: bool = False,
        **kwargs,
    ):
        """Initialize relationship property.

        Args:
            argument: Target model class or string name
            foreign_keys: Foreign key field name(s)
            back_populates: Name of reverse relationship attribute
            backref: Name for automatic reverse relationship
            lazy: Loading strategy ('select', 'dynamic', 'noload', 'raise')
            uselist: Whether relationship returns a list
            secondary: M2M table name
            primaryjoin: Custom primary join condition
            secondaryjoin: Custom secondary join condition for M2M
            order_by: Default ordering for collections
            cascade: Cascade options
            passive_deletes: Whether to use passive deletes
            **kwargs: Additional relationship options
        """
        self.argument = argument
        self.foreign_keys = foreign_keys
        self.back_populates = back_populates
        self.backref = backref
        self.lazy = lazy
        self.uselist = uselist
        self.secondary = secondary
        self.m2m_definition: M2MTable | None = None  # M2M table definition
        self.primaryjoin = primaryjoin
        self.secondaryjoin = secondaryjoin
        self.order_by = order_by
        self.cascade = cascade
        self.passive_deletes = passive_deletes
        self.name: str | None = None
        self.resolved_model: type[ObjectModel] | None = None
        self.relationship_type: str | None = None
        self.is_many_to_many: bool = False  # M2M relationship flag

        # Store additional relationship configuration parameters
        self.extra_kwargs = kwargs


class RelationshipResolver:
    """Relationship type resolver."""

    @staticmethod
    def resolve_relationship_type(property_: RelationshipProperty) -> str:
        """Automatically infer relationship type based on parameters.

        Args:
            property_: RelationshipProperty instance to analyze

        Returns:
            String representing the relationship type
        """
        if property_.uselist is False:
            return RelationshipType.MANY_TO_ONE if property_.foreign_keys else RelationshipType.ONE_TO_ONE
        elif property_.uselist is True:  # noqa
            return RelationshipType.MANY_TO_MANY if property_.secondary else RelationshipType.ONE_TO_MANY

        if property_.secondary:
            property_.is_many_to_many = True
            return RelationshipType.MANY_TO_MANY
        elif property_.foreign_keys:
            return RelationshipType.MANY_TO_ONE
        else:
            return RelationshipType.ONE_TO_MANY


class RelatedObjectProxy:
    """Proxy for single related object."""

    def __init__(self, instance: "ObjectModel", descriptor: "RelationshipDescriptor"):
        """Initialize related object proxy.

        Args:
            instance: Parent model instance
            descriptor: Relationship descriptor
        """
        self.instance = instance
        self.descriptor = descriptor
        self.property = descriptor.property
        self._cached_object = None
        self._loaded = False

    async def get(self):
        """Get the related object.

        Returns:
            Related object instance or None
        """
        if not self._loaded:
            await self._load()
        return self._cached_object

    def __await__(self):
        """Support await syntax."""
        return self.get().__await__()

    async def _load(self):
        """Load related object from database."""
        if self.property.foreign_keys and self.property.resolved_model:
            # Handle foreign_keys as string or list
            fk_field = self.property.foreign_keys
            if isinstance(fk_field, list):
                fk_field = fk_field[0]  # Use first foreign key

            fk_value = getattr(self.instance, fk_field)
            if fk_value is not None:
                related_table = self.property.resolved_model.get_table()
                pk_col = list(related_table.primary_key.columns)[0]

                query = select(related_table).where(pk_col == fk_value)  # noqa
                session = self.instance._get_session()  # noqa
                result = await session.execute(query)
                row = result.first()

                if row:
                    self._cached_object = self.property.resolved_model(**dict(row._mapping))  # noqa

        self._loaded = True


class BaseRelatedCollection:
    """Base class for related object collections."""

    def __init__(self, instance: "ObjectModel", descriptor: "RelationshipDescriptor"):
        """Initialize related collection.

        Args:
            instance: Parent model instance
            descriptor: Relationship descriptor
        """
        self.instance = instance
        self.descriptor = descriptor
        self.property = descriptor.property
        self._cached_objects = None
        self._loaded = False

    async def all(self):
        """Get all related objects.

        Returns:
            List of related object instances
        """
        if not self._loaded:
            await self._load()
        return self._cached_objects or []

    def __await__(self):
        """Support await syntax."""
        return self.all().__await__()

    async def _load(self):
        """Load related object list from database - implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _load method")

    def _set_empty_result(self):
        """Common method to set empty result."""
        self._cached_objects = []
        self._loaded = True


class OneToManyCollection(BaseRelatedCollection):
    """One-to-many related object collection."""

    async def _load(self):
        """Load one-to-many relationship."""
        if not self.property.resolved_model:
            self._set_empty_result()
            return

        instance_pk = self.instance.id
        related_table = self.property.resolved_model.get_table()

        # Handle foreign_keys as string or list
        fk_name = self.property.foreign_keys
        if isinstance(fk_name, list):
            fk_name = fk_name[0]  # Use first foreign key
        elif fk_name is None:
            fk_name = f"{self.instance.__class__.__name__.lower()}_id"

        fk_col = related_table.c[fk_name]

        query = select(related_table).where(fk_col == instance_pk)  # noqa
        session = self.instance._get_session()  # noqa
        result = await session.execute(query)

        self._cached_objects = [self.property.resolved_model(**dict(row._mapping)) for row in result]  # noqa
        self._loaded = True


class M2MCollectionMixin:
    """Mixin class for M2M collection functionality."""

    # Type hints for mixin attributes
    instance: "ObjectModel"
    property: RelationshipProperty

    def _load_m2m_data(self) -> tuple[M2MTable | None, Any | None, Any | None, Any | None]:
        """Load M2M basic data.

        Returns:
            Tuple of (m2m_def, registry, m2m_table, instance_id)
        """
        m2m_def = self.property.m2m_definition
        if not m2m_def:
            return None, None, None, None

        registry = getattr(self.instance.__class__, "__registry__", None)
        if not registry:
            return None, None, None, None

        m2m_table = registry.get_m2m_table(m2m_def.table_name)
        if not m2m_table:
            return None, None, None, None

        if not m2m_def.left_ref_field:
            return None, None, None, None

        instance_id = getattr(self.instance, m2m_def.left_ref_field)
        if instance_id is None:
            return None, None, None, None

        return m2m_def, registry, m2m_table, instance_id

    def _build_m2m_query(self, m2m_def: M2MTable, m2m_table: Any, instance_id: Any) -> Any:
        """Build M2M query.

        Args:
            m2m_def: M2M table definition
            m2m_table: M2M table instance
            instance_id: Current instance ID

        Returns:
            SQLAlchemy query or None
        """
        if not self.property.resolved_model:
            return None

        related_table = self.property.resolved_model.get_table()

        from sqlalchemy import join

        if not (m2m_def.right_field and m2m_def.right_ref_field and m2m_def.left_field):
            return None

        joined_tables = join(
            m2m_table,
            related_table,
            getattr(m2m_table.c, m2m_def.right_field) == getattr(related_table.c, m2m_def.right_ref_field),  # noqa
        )

        return (
            select(related_table)
            .select_from(joined_tables)
            .where(getattr(m2m_table.c, m2m_def.left_field) == instance_id)  # noqa
        )


class M2MRelatedCollection(BaseRelatedCollection, M2MCollectionMixin):
    """Many-to-many related object collection."""

    async def _load(self) -> None:
        """Load M2M related object list from database."""
        m2m_def, registry, m2m_table, instance_id = self._load_m2m_data()
        if not m2m_def or not registry or not m2m_table or instance_id is None:
            self._set_empty_result()
            return

        query = self._build_m2m_query(m2m_def, m2m_table, instance_id)
        if not query:
            self._set_empty_result()
            return

        session = self.instance._get_session()  # noqa
        result = await session.execute(query)

        if self.property.resolved_model:
            self._cached_objects = [self.property.resolved_model(**dict(row._mapping)) for row in result]  # noqa
        else:
            self._cached_objects = []
        self._loaded = True

    async def add(self, *objects: "ObjectModel") -> None:
        """Add M2M relationships.

        Args:
            *objects: Objects to add to the relationship
        """
        m2m_def, registry, m2m_table, instance_id = self._load_m2m_data()
        if not m2m_def or not registry or not m2m_table or instance_id is None:
            return

        from sqlalchemy import insert

        session = self.instance._get_session(readonly=False)  # noqa

        if not (m2m_def.right_ref_field and m2m_def.left_field and m2m_def.right_field):
            return

        for obj in objects:
            related_id = getattr(obj, m2m_def.right_ref_field)
            if related_id is not None:
                stmt = insert(m2m_table).values({m2m_def.left_field: instance_id, m2m_def.right_field: related_id})
                await session.execute(stmt)

        # Clear cache
        self._loaded = False
        self._cached_objects = None

    async def remove(self, *objects: "ObjectModel") -> None:
        """Remove M2M relationships.

        Args:
            *objects: Objects to remove from the relationship
        """
        m2m_def, registry, m2m_table, instance_id = self._load_m2m_data()
        if not m2m_def or not registry or not m2m_table or instance_id is None:
            return

        from sqlalchemy import and_, delete

        session = self.instance._get_session(readonly=False)  # noqa

        if not (m2m_def.right_ref_field and m2m_def.left_field and m2m_def.right_field):
            return

        for obj in objects:
            related_id = getattr(obj, m2m_def.right_ref_field)
            if related_id is not None:
                stmt = delete(m2m_table).where(
                    and_(
                        getattr(m2m_table.c, m2m_def.left_field) == instance_id,
                        getattr(m2m_table.c, m2m_def.right_field) == related_id,
                    )
                )
                await session.execute(stmt)

        # Clear cache
        self._loaded = False
        self._cached_objects = None


class RelatedQuerySet:
    """Related query set - inherits full QuerySet functionality (lazy='dynamic')."""

    def __init__(self, instance: "ObjectModel", descriptor: "RelationshipDescriptor"):
        """Initialize related query set.

        Args:
            instance: Parent model instance
            descriptor: Relationship descriptor
        """
        self.parent_instance = instance
        self.relationship_desc = descriptor
        self._queryset: Any = None
        self._initialized = False

    def _get_queryset(self) -> Any:
        """Lazy initialize QuerySet.

        Returns:
            Initialized QuerySet instance
        """
        if not self._initialized:
            from .queries import QuerySet

            if not self.relationship_desc.property.resolved_model:
                raise ValueError(f"Relationship '{self.relationship_desc.name}' model not resolved")

            related_model = self.relationship_desc.property.resolved_model
            related_table = related_model.get_table()

            # Create base QuerySet
            self._queryset = QuerySet(related_table, related_model)

            # Automatically add relationship filter conditions
            self._apply_relationship_filter()
            self._initialized = True

        return self._queryset

    def _apply_relationship_filter(self) -> None:
        """Automatically add relationship filter conditions."""
        if not self._queryset:
            return

        relationship_type = RelationshipResolver.resolve_relationship_type(self.relationship_desc.property)

        if relationship_type == RelationshipType.ONE_TO_MANY:
            fk_name = self._get_foreign_key_name()
            fk_col = self._queryset._table.c[fk_name]  # noqa
            self._queryset = self._queryset.filter(fk_col == self.parent_instance.id)
        elif relationship_type == RelationshipType.MANY_TO_MANY:
            self._apply_m2m_filter()

    def _get_foreign_key_name(self) -> str:
        """Get foreign key field name.

        Returns:
            Foreign key field name
        """
        fk_name = self.relationship_desc.property.foreign_keys
        if isinstance(fk_name, list):
            return fk_name[0]
        elif fk_name is None:
            return f"{self.parent_instance.__class__.__name__.lower()}_id"
        return fk_name

    def _apply_m2m_filter(self) -> None:
        """Apply many-to-many relationship filtering."""
        if not self._queryset:
            return

        m2m_def = self.relationship_desc.property.m2m_definition
        if not m2m_def:
            return

        # Get M2M table
        registry = getattr(self.parent_instance.__class__, "__registry__", None)
        if not registry:
            return

        m2m_table = registry.get_m2m_table(m2m_def.table_name)
        if not m2m_table:
            return

        # Build M2M subquery
        from sqlalchemy import select

        if not (m2m_def.left_field and m2m_def.right_field and m2m_def.left_ref_field and m2m_def.right_ref_field):
            return

        instance_id = getattr(self.parent_instance, m2m_def.left_ref_field)
        if instance_id is None:
            return

        # Subquery to get related IDs
        subquery = select(getattr(m2m_table.c, m2m_def.right_field)).where(
            getattr(m2m_table.c, m2m_def.left_field) == instance_id  # noqa
        )

        # Apply filter
        related_pk_col = getattr(self._queryset._table.c, m2m_def.right_ref_field)  # noqa
        self._queryset = self._queryset.filter(related_pk_col.in_(subquery))

    # Proxy all QuerySet methods
    def __getattr__(self, name: str) -> Any:
        """Proxy all QuerySet methods.

        Args:
            name: Method name to proxy

        Returns:
            Proxied method or attribute
        """
        qs = self._get_queryset()
        attr = getattr(qs, name)

        # If it's a method that returns a new QuerySet, need to wrap the return value
        if callable(attr) and name in {
            "filter",
            "exclude",
            "order_by",
            "limit",
            "offset",
            "distinct",
            "only",
            "defer",
            "select_related",
            "prefetch_related",
            "annotate",
            "group_by",
            "having",
            "join",
            "leftjoin",
            "outerjoin",
            "select_for_update",
            "select_for_share",
            "extra",
            "none",
            "reverse",
            "options",
            "skip_default_ordering",
        }:

            def wrapper(*args: Any, **kwargs: Any) -> "RelatedQuerySet":
                new_qs = attr(*args, **kwargs)
                # Create new RelatedQuerySet instance
                related_qs = RelatedQuerySet(self.parent_instance, self.relationship_desc)
                related_qs._queryset = new_qs
                related_qs._initialized = True
                return related_qs

            return wrapper

        return attr


class NoLoadProxy:
    """No-load proxy (lazy='noload')."""

    def __init__(self, instance: "ObjectModel", descriptor: "RelationshipDescriptor"):
        """Initialize no-load proxy.

        Args:
            instance: Parent model instance
            descriptor: Relationship descriptor
        """
        self.instance = instance
        self.descriptor = descriptor
        self.property = descriptor.property

    def __await__(self) -> Any:
        """Async access returns empty result."""
        return self._empty_result().__await__()

    async def _empty_result(self) -> list[Any] | None:
        """Return empty result.

        Returns:
            Empty list for collections, None for single objects
        """
        return [] if self.property.uselist else None

    def __iter__(self) -> Any:
        """Iterator returns empty."""
        return iter([])

    def __len__(self) -> int:
        """Length is 0."""
        return 0

    def __bool__(self) -> bool:
        """Boolean value is False."""
        return False


class RaiseProxy:
    """Raise exception proxy (lazy='raise')."""

    def __init__(self, instance: "ObjectModel", descriptor: "RelationshipDescriptor"):
        """Initialize raise proxy.

        Args:
            instance: Parent model instance
            descriptor: Relationship descriptor
        """
        self.instance = instance
        self.descriptor = descriptor
        self.property = descriptor.property

    def __await__(self) -> Any:
        """Async access raises exception."""
        raise AttributeError(
            f"Relationship '{self.property.name}' is configured with lazy='raise'. "
            f"Use explicit loading with select_related() or prefetch_related()."
        )

    def __iter__(self) -> Any:
        """Iterator access raises exception."""
        raise AttributeError(
            f"Relationship '{self.property.name}' is configured with lazy='raise'. "
            f"Use explicit loading with select_related() or prefetch_related()."
        )

    def __len__(self) -> int:
        """Length access raises exception."""
        raise AttributeError(
            f"Relationship '{self.property.name}' is configured with lazy='raise'. "
            f"Use explicit loading with select_related() or prefetch_related()."
        )

    def __bool__(self) -> bool:
        """Boolean access raises exception."""
        raise AttributeError(
            f"Relationship '{self.property.name}' is configured with lazy='raise'. "
            f"Use explicit loading with select_related() or prefetch_related()."
        )


class RelationshipDescriptor:
    """Unified relationship field descriptor."""

    def __init__(self, property_: RelationshipProperty):
        """Initialize relationship descriptor.

        Args:
            property_: Relationship property configuration
        """
        self.property = property_
        self.name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        """Set descriptor name and register with model.

        Args:
            owner: Model class that owns this descriptor
            name: Field name
        """
        self.name = name
        self.property.name = name

        # Register relationship with model
        if not hasattr(owner, "_relationships"):
            owner._relationships = {}
        owner._relationships[name] = self

    def __get__(self, instance: "ObjectModel | None", owner: type) -> Any:
        """Get relationship value.

        Args:
            instance: Model instance or None for class access
            owner: Model class

        Returns:
            Appropriate relationship proxy based on lazy strategy
        """
        if instance is None:
            return self

        # Ensure relationships are resolved
        registry = getattr(instance.__class__, "__registry__", None)
        if registry:
            registry.resolve_all_relationships()

        # Check if already preloaded
        if self.name:
            cache_attr = f"_{self.name}_cache"
            if hasattr(instance, cache_attr):
                return getattr(instance, cache_attr)

        # Return different objects based on lazy strategy
        if self.property.lazy == "dynamic":
            return RelatedQuerySet(instance, self)
        elif self.property.lazy == "noload":
            return NoLoadProxy(instance, self)
        elif self.property.lazy == "raise":
            return RaiseProxy(instance, self)
        elif self.property.is_many_to_many:
            return M2MRelatedCollection(instance, self)
        elif self.property.uselist:
            return OneToManyCollection(instance, self)
        else:
            return RelatedObjectProxy(instance, self)


def relationship(
    argument: str | type["ObjectModel"],
    *,
    foreign_keys: str | list[str] | None = None,
    back_populates: str | None = None,
    backref: str | None = None,
    lazy: str = "select",
    uselist: bool | None = None,
    secondary: str | M2MTable | None = None,
    primaryjoin: str | None = None,
    secondaryjoin: str | None = None,
    order_by: str | list[str] | None = None,
    cascade: str | None = None,
    passive_deletes: bool = False,
    **kwargs: Any,
):
    """Define model relationship using unified Column syntax.

    Args:
        argument: Target model class or string name
        foreign_keys: Foreign key field name(s)
        back_populates: Name of reverse relationship attribute
        backref: Name for automatic reverse relationship
        lazy: Loading strategy ('select', 'dynamic', 'noload', 'raise')
        uselist: Whether relationship returns a list
        secondary: M2M table name or M2MTable instance
        primaryjoin: Custom primary join condition
        secondaryjoin: Custom secondary join condition for M2M
        order_by: Default ordering for collections
        cascade: Cascade options
        passive_deletes: Whether to use passive deletes
        **kwargs: Additional relationship options

    Returns:
        Column instance marked as relationship field

    Raises:
        ValueError: If both back_populates and backref are specified
    """

    # Validate mutually exclusive parameters
    if back_populates and backref:
        raise ValueError("Cannot specify both 'back_populates' and 'backref'")

    # Handle M2M table definition
    secondary_table_name = None
    m2m_def = None

    if isinstance(secondary, M2MTable):
        m2m_def = secondary
        secondary_table_name = secondary.table_name
    elif isinstance(secondary, str):
        secondary_table_name = secondary

    property_ = RelationshipProperty(
        argument=argument,
        foreign_keys=foreign_keys,
        back_populates=back_populates,
        backref=backref,
        lazy=lazy,
        uselist=uselist,
        secondary=secondary_table_name,
        primaryjoin=primaryjoin,
        secondaryjoin=secondaryjoin,
        order_by=order_by,
        cascade=cascade,
        passive_deletes=passive_deletes,
        **kwargs,
    )

    # Set M2M definition if provided
    if m2m_def:
        property_.m2m_definition = m2m_def
        property_.is_many_to_many = True

    # Return our own Column instance, marked as relationship field
    from .fields import Column as SQLObjectsColumn

    return SQLObjectsColumn[Any](is_relationship=True, relationship_property=property_)
