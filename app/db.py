import asyncpg
from typing import AsyncGenerator
from fastapi import FastAPI

from app.core.config import AUTH_DB_URL  # e.g. "postgresql://user:pass@host:port/dbname"

pool: asyncpg.pool.Pool | None = None


async def init_db(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(AUTH_DB_URL, min_size=1, max_size=5)
    app.state.db_pool = pool


async def close_db(app: FastAPI):
    global pool
    if pool:
        await pool.close()
        pool = None


async def get_db_pool() -> AsyncGenerator[asyncpg.pool.Pool, None]:
    """
    FastAPI dependency to inject the asyncpg pool.
    """
    if pool is None:
        raise RuntimeError("DB pool not initialized")
    yield pool
