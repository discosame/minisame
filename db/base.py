from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os, asyncpg, asyncio, aiohttp

load_dotenv()

DB_DSN = os.environ.get("DB") #postgres://user_name:password@hostname/db_name

__all__ = ("session_scope",)

pool = None


@asynccontextmanager
async def session_scope():
    "DBと接続する"
    global pool

    if pool is None:
        pool = await asyncpg.create_pool(
            DB_DSN, min_size=1, max_size=1, max_inactive_connection_lifetime=3
        )

    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn
