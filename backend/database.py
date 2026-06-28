from pathlib import Path
import os
from typing import Any, Optional

import asyncpg
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL",)

pool: Optional[asyncpg.Pool] = None
pool_error: Optional[str] = None


async def init_db_pool() -> Optional[asyncpg.Pool]:
    global pool, pool_error
    if pool is not None:
        return pool

    try:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5, command_timeout=60)
        pool_error = None
        return pool
    except Exception as exc:  # pragma: no cover - best effort for demo startup
        pool_error = str(exc)
        pool = None
        return None


async def close_db_pool() -> None:
    global pool
    if pool is not None:
        await pool.close()
        pool = None


async def fetch_rows(query: str, params: Optional[tuple[Any, ...]] = None) -> list[dict[str, Any]]:
    await init_db_pool()
    if pool is None:
        raise RuntimeError(pool_error or "Database unavailable")

    async with pool.acquire() as connection:
        rows = await connection.fetch(query, *(params or ()))
        return [dict(row) for row in rows]
