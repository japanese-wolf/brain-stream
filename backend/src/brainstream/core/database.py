"""Database configuration and session management."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from brainstream.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Create async engine
engine = create_async_engine(
    settings.database_url.replace("~", str(settings.data_dir.parent)),
    echo=settings.debug,
    future=True,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def _migrate_add_columns(conn) -> None:
    """Add missing columns to existing tables.

    SQLAlchemy's create_all() only creates new tables; it does not
    alter existing ones.  This function inspects each table via
    PRAGMA table_info and issues ALTER TABLE ADD COLUMN for any
    column defined in the model but absent from the database.
    """
    migrations: list[tuple[str, str, str]] = [
        # (table, column, column_def)
        ("user_profiles", "domains", "JSON DEFAULT '[]'"),
        ("user_profiles", "roles", "JSON DEFAULT '[]'"),
        ("user_profiles", "goals", "JSON DEFAULT '[]'"),
        ("articles", "related_technologies", "JSON"),
        ("articles", "tech_stack_connection", "TEXT"),
    ]

    for table, column, col_def in migrations:
        result = await conn.execute(text(f"PRAGMA table_info({table})"))
        existing = {row[1] for row in result.fetchall()}
        if column not in existing:
            await conn.execute(
                text(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
            )
            logger.info("Migration: added %s.%s", table, column)


async def init_db() -> None:
    """Initialize database and create all tables."""
    # Ensure data directory exists
    settings.ensure_data_dir()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _migrate_add_columns(conn)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.

    Usage:
        async with get_session() as session:
            # Use session
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
