from __future__ import annotations

import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

logger = logging.getLogger(__name__)


async def run_preflight_checks() -> None:
    if not settings.ENABLE_PREFLIGHT:
        return

    required_envs = [
        "DATABASE_URL",
        "JWT_SECRET",
        "ACCESS_TOKEN_EXPIRES_MIN",
        "REFRESH_TOKEN_EXPIRES_MIN",
    ]
    missing = [name for name in required_envs if not getattr(settings, name, None)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    engine = create_async_engine(settings.DATABASE_URL, future=True)
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    await engine.dispose()
    logger.info("Preflight checks passed")


