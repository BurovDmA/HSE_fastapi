import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Link
import aioredis
from datetime import datetime, timedelta

# Тестовая база данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
TEST_REDIS_URL = "redis://localhost:6379/1"

@pytest.fixture(scope="session")
def test_db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
async def test_db(test_db_engine):
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_db_engine, test_db):
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
async def redis_client():
    redis = await aioredis.from_url(TEST_REDIS_URL, encoding="utf8", decode_responses=True)
    yield redis
    await redis.flushdb()
    await redis.close()

@pytest.fixture
def client(db_session, redis_client):
    async def override_get_db():
        yield db_session

    async def override_get_redis():
        yield redis_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def test_link(db_session):
    link = Link(
        original_url="https://example.com",
        short_code="test123",
        expires_at=datetime.utcnow() + timedelta(days=7),
        custom_alias=None
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)
    return link 