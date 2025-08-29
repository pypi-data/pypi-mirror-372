import contextvars
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from .exceptions import convert_sqlalchemy_error


if TYPE_CHECKING:
    from .database import Database  # noqa


__all__ = [
    "AsyncSession",
    "SessionContextManager",
    "ctx_session",
    "ctx_sessions",
]


# Explicit session management (highest priority)
_explicit_sessions: contextvars.ContextVar[dict[str, "AsyncSession"]] = contextvars.ContextVar("explicit_sessions")


class AsyncSession(ABC):
    """Abstract base class for database sessions.

    This class should not be instantiated directly. Use ctx_session() or
    SessionContextManager.get_session() to obtain session instances.
    """

    @property
    @abstractmethod
    def db_name(self) -> str:
        """Database name for this session."""
        pass

    @abstractmethod
    async def execute(self, statement: Any, parameters: Any = None) -> Any:
        """Execute statement with automatic transaction management."""
        pass

    @abstractmethod
    async def stream(self, statement: Any, parameters: Any = None) -> Any:
        """Execute statement and return streaming result."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction if exists and not readonly."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction if exists and not readonly."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close session and cleanup resources."""
        pass

    @abstractmethod
    async def __aenter__(self) -> "AsyncSession":
        """Async context manager entry."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with automatic cleanup."""
        pass


class _AsyncSession(AsyncSession):
    """Internal AsyncSession implementation with smart connection and transaction management.

    Two main usage patterns:
    1. Explicit sessions (ctx_session): auto_commit=False, manual transaction control
    2. Implicit sessions (get_session): auto_commit=True, automatic cleanup after each operation
    """

    def __init__(self, db_name: str, readonly: bool = True, auto_commit: bool = True):
        """Initialize AsyncSession with lazy connection.

        Args:
            db_name: Database name
            readonly: True for readonly (no transaction), False for transactional
            auto_commit: True to auto-commit and close after each operation (ignored if readonly=True)
        """
        self._db_name = db_name
        self.readonly = readonly
        self.auto_commit = auto_commit and not readonly  # readonly sessions never auto-commit
        self._conn: AsyncConnection | None = None
        self._trans = None

    @property
    def db_name(self) -> str:
        """Database name for this session."""
        return self._db_name

    async def execute(self, statement: Any, parameters: Any = None) -> Any:
        """Execute statement with automatic transaction management."""
        await self._ensure_connection()

        # Auto-begin transaction for non-readonly sessions
        if not self.readonly and self._trans is None:
            self._trans = await self._conn.begin()  # type: ignore

        try:
            result = await self._conn.execute(statement, parameters)  # type: ignore

            # Auto-commit for implicit sessions
            if self.auto_commit:
                await self.commit()

            return result
        except SQLAlchemyError as e:
            # Rollback transaction on SQLAlchemy error and convert
            await self.rollback()
            raise convert_sqlalchemy_error(e) from e
        except Exception:
            # Rollback transaction on other errors
            await self.rollback()
            raise
        finally:
            # Auto-close connection for implicit sessions to prevent resource leaks
            if self.auto_commit:
                await self.close()

    async def stream(self, statement: Any, parameters: Any = None) -> Any:
        """Execute statement and return streaming result."""
        await self._ensure_connection()

        # Auto-begin transaction for non-readonly sessions
        if not self.readonly and self._trans is None:
            self._trans = await self._conn.begin()  # type: ignore

        try:
            result = await self._conn.stream(statement, parameters)  # type: ignore

            # Note: No auto-commit for streaming results as they need to remain open
            # Connection cleanup will happen when the stream is consumed

            return result
        except SQLAlchemyError as e:
            # Rollback transaction on SQLAlchemy error and convert
            await self.rollback()
            # Auto-close connection on error for implicit sessions
            if self.auto_commit:
                await self.close()
            raise convert_sqlalchemy_error(e) from e
        except Exception:
            # Rollback transaction on other errors
            await self.rollback()
            # Auto-close connection on error for implicit sessions
            if self.auto_commit:
                await self.close()
            raise

    async def commit(self):
        """Commit transaction if exists and not readonly."""
        if self._trans and not self.readonly:
            await self._trans.commit()
            self._trans = None

    async def rollback(self):
        """Rollback transaction if exists and not readonly."""
        if self._trans and not self.readonly:
            await self._trans.rollback()
            self._trans = None

    async def close(self):
        """Close session and cleanup resources."""
        if self._trans:
            await self._trans.rollback()
            self._trans = None

        if self._conn:
            await self._conn.close()
            self._conn = None

    async def _ensure_connection(self):
        """Ensure connection is available (lazy initialization)."""
        if self._conn is None:
            engine = SessionContextManager.engines[self._db_name]
            self._conn = await engine.connect()

    async def __aenter__(self) -> "AsyncSession":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with automatic cleanup."""
        await self.close()

    def __getattr__(self, name: str) -> Any:
        """Proxy AsyncConnection methods."""
        if self._conn and hasattr(self._conn, name):
            return getattr(self._conn, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class SessionContextManager:
    """Multi-database session context manager with readonly optimization.

    Provides automatic session management based on SQLAlchemy Core,
    supporting both readonly and transactional modes with intelligent session reuse.

    Examples:
        >>> # Set database engine
        >>> SessionContextManager.set_engine(engine, "main", is_default=True)
        >>> # Get readonly session (optimized for SELECT)
        >>> async with SessionContextManager.get_session(readonly=True) as session:
        ...     result = await session.execute(text("SELECT 1"))
        >>> # Get transactional session with auto-commit
        >>> async with SessionContextManager.get_session(readonly=False) as session:
        ...     await session.execute(text("UPDATE users SET status='active'"))
    """

    engines: dict[str, AsyncEngine] = {}
    default_db: str | None = None

    @classmethod
    def set_engine(cls, engine: AsyncEngine, db_name: str = "default", is_default: bool = False) -> None:
        """Set database engine."""
        cls.engines[db_name] = engine
        if is_default or cls.default_db is None:
            cls.default_db = db_name

    @classmethod
    def get_session(cls, db_name: str | None = None, readonly: bool = True, auto_commit: bool = True) -> AsyncSession:
        """Get database session with readonly optimization.

        Args:
            db_name: Database name (uses default database if None)
            readonly: True for readonly (no transaction), False for transactional
            auto_commit: True to auto-commit after each operation (ignored if readonly=True)

        Returns:
            AsyncSession instance

        Priority:
            1. Explicitly set sessions (ctx_session, ctx_sessions)
            2. Create new AsyncSession with specified parameters
        """
        name = db_name or cls.default_db or "default"

        # Priority 1: Explicitly set sessions
        try:
            explicit_sessions = _explicit_sessions.get({})
            if name in explicit_sessions:
                return explicit_sessions[name]
        except LookupError:
            pass

        # Priority 2: Create new _AsyncSession
        return _AsyncSession(name, readonly, auto_commit)

    @classmethod
    def set_session(cls, session: AsyncSession, db_name: str | None = None) -> None:
        """Set active session in current context."""
        name = db_name or cls.default_db or "default"
        try:
            current_sessions = _explicit_sessions.get({})
        except LookupError:
            current_sessions = {}
        new_sessions = current_sessions.copy()
        new_sessions[name] = session
        _explicit_sessions.set(new_sessions)

    @classmethod
    def set_default(cls, db_name: str) -> None:
        """Set default database by name."""
        if db_name not in cls.engines:
            raise RuntimeError(f"Database '{db_name}' is not initialized")
        cls.default_db = db_name

    @classmethod
    def clear_session(cls, db_name: str | None = None) -> None:
        """Clear active session from current context."""
        try:
            current_sessions = _explicit_sessions.get({})
            if db_name:
                if db_name in current_sessions:
                    new_sessions = current_sessions.copy()
                    del new_sessions[db_name]
                    _explicit_sessions.set(new_sessions)
            else:
                _explicit_sessions.set({})
        except LookupError:
            pass

    # DatabaseObserver protocol implementation
    @classmethod
    def on_database_added(cls, name: str, database: "Database", is_default: bool) -> None:
        """Register engine when database is added"""
        cls.set_engine(database.engine, name, is_default)

    @classmethod
    def on_database_closed(cls, name: str) -> None:
        """Clean up engine when database is closed"""
        if name in cls.engines:
            del cls.engines[name]

    @classmethod
    def on_default_changed(cls, old_default: str | None, new_default: str | None) -> None:
        """Update default setting when default database changes"""
        cls.default_db = new_default


@asynccontextmanager
async def ctx_session(db_name: str | None = None) -> AsyncGenerator[AsyncSession, None]:
    """Get async context manager for single database transactional session.

    Creates a transactional session with manual commit control (auto_commit=False).
    Transaction is automatically committed on successful exit or rolled back on exception.

    Args:
        db_name: Database name (uses default database if None)

    Yields:
        AsyncSession: Transactional session with manual commit control
    """
    name = db_name or SessionContextManager.default_db or "default"
    session = _AsyncSession(name, readonly=False, auto_commit=False)

    # Set as explicit session in context
    SessionContextManager.set_session(session, name)

    try:
        yield session
        # Auto-commit on successful exit
        await session.commit()
    except Exception:
        # Auto-rollback on exception
        await session.rollback()
        raise
    finally:
        # Cleanup
        await session.close()
        SessionContextManager.clear_session(name)


@asynccontextmanager
async def ctx_sessions(*db_names: str) -> AsyncGenerator[dict[str, AsyncSession], None]:
    """Get async context manager for multiple database transactional sessions.

    Creates transactional sessions for multiple databases with manual commit control.
    All transactions are automatically committed on successful exit or rolled back on exception.

    Args:
        *db_names: Database names

    Yields:
        dict[str, AsyncSession]: Dictionary mapping database names to sessions
    """
    if not db_names:
        raise ValueError("At least one database name must be provided")

    sessions: dict[str, AsyncSession] = {}

    try:
        # Create sessions for all databases
        for db_name in db_names:
            session = _AsyncSession(db_name, readonly=False, auto_commit=False)
            sessions[db_name] = session
            SessionContextManager.set_session(session, db_name)

        yield sessions

        # Auto-commit all sessions on successful exit
        for session in sessions.values():
            await session.commit()

    except Exception:
        # Auto-rollback all sessions on exception
        for session in sessions.values():
            await session.rollback()
        raise

    finally:
        # Cleanup all sessions
        for db_name, session in sessions.items():
            await session.close()
            SessionContextManager.clear_session(db_name)
