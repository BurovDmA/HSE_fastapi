from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from redis import asyncio as aioredis
from config import FULL_URL


# REDIS_URL = "redis://localhost:6379"
#
# async def get_redis():
#     redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
#     try:
#         yield redis
#     finally:
#         await redis.close()

DATABASE_URL = FULL_URL

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session