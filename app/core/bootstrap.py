from __future__ import annotations

import logging
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.models import Base
from app.models.user import User
from app.models.internship import Internship  # noqa: F401
from app.models.application import Application  # noqa: F401

logger = logging.getLogger(__name__)


def _get_sync_url(async_url: str) -> str:
    # Use psycopg driver for sync engine as well
    if "+psycopg" not in async_url:
        return async_url.replace("postgresql://", "postgresql+psycopg://")
    return async_url


async def _ensure_tables_exist_with_sqlalchemy() -> None:
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def _has_alembic_version_table() -> bool:
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    async with engine.connect() as conn:
        def _check(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.has_table("alembic_version")

        exists = await conn.run_sync(_check)
    await engine.dispose()
    return bool(exists)


async def check_db_initialized() -> None:
    # Determine initialization via alembic_version or core tables
    initialized = False

    if await _has_alembic_version_table():
        # Check at least one row
        engine = create_async_engine(settings.DATABASE_URL, future=True)
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT COUNT(1) FROM alembic_version"))
            count = res.scalar_one()
            initialized = count >= 1
        await engine.dispose()
    else:
        # Fallback: check presence of core tables
        engine = create_async_engine(settings.DATABASE_URL, future=True)
        async with engine.connect() as conn:
            def _check_tables(sync_conn):
                inspector = inspect(sync_conn)
                table_names = inspector.get_table_names()
                required_tables = {"users", "internships", "applications"}
                return required_tables.issubset(set(table_names))
            
            present = await conn.run_sync(_check_tables)
            initialized = present
        await engine.dispose()

    if not initialized:
        if settings.ALLOW_AUTO_DB_INIT:
            logger.info("DB not initialized. Auto-initializing with SQLAlchemy metadata.")
            await _ensure_tables_exist_with_sqlalchemy()
        else:
            raise RuntimeError(
                "Database not initialized. Run Alembic migrations or enable ALLOW_AUTO_DB_INIT."
            )


async def bootstrap() -> None:
    if not settings.ENABLE_BOOTSTRAP:
        return

    # Ensure tables exist (prefer alembic if present; here we fallback to metadata)
    await _ensure_tables_exist_with_sqlalchemy()

    # Create default admin if requested
    if settings.CREATE_DEFAULT_ADMIN:
        engine = create_async_engine(settings.DATABASE_URL, future=True)
        async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            from sqlalchemy import select

            res = await session.execute(select(User).where(User.email == settings.DEFAULT_ADMIN_EMAIL))
            existing = res.scalar_one_or_none()
            if not existing:
                user = User(
                    email=settings.DEFAULT_ADMIN_EMAIL,
                    hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                    role="admin",
                )
                session.add(user)
                await session.commit()
                logger.info("Default admin created: %s", settings.DEFAULT_ADMIN_EMAIL)
        await engine.dispose()


