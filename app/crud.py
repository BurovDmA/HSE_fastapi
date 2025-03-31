import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import aioredis
from app import crud, models, schemas


@pytest.mark.asyncio
async def test_generate_short_code():
    code1 = crud.generate_short_code()
    code2 = crud.generate_short_code()
    assert len(code1) == 6
    assert code1 != code2  # Проверка уникальности


@pytest.mark.asyncio
async def test_create_link_with_custom_alias(mock_db: AsyncSession):
    link_data = schemas.LinkCreate(
        original_url="https://example.com",
        custom_alias="custom"
    )
    mock_db.commit = AsyncMock()

    result = await crud.create_link(mock_db, link_data)
    assert result["short_code"] == "custom"


@pytest.mark.asyncio
async def test_create_link_with_auto_generated_code(mock_db: AsyncSession):
    link_data = schemas.LinkCreate(original_url="https://example.com")
    mock_db.commit = AsyncMock()

    result = await crud.create_link(mock_db, link_data)
    assert len(result["short_code"]) == 6


@pytest.mark.asyncio
async def test_get_link_by_short_code(mock_db: AsyncSession):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = models.Link(
        short_code="test123",
        original_url="https://example.com"
    )
    mock_db.execute = AsyncMock(return_value=mock_result)

    link = await crud.get_link_by_short_code(mock_db, "test123")
    assert link.short_code == "test123"


@pytest.mark.asyncio
async def test_delete_link(mock_db: AsyncSession):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = models.Link(short_code="test123")
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    await crud.get_link_deleted(mock_db, "test123")
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_link_clicks(mock_db: AsyncSession):
    test_link = models.Link(clicks=0)
    mock_db.commit = AsyncMock()

    updated = await crud.update_link_clicks(mock_db, test_link)
    assert updated.clicks == 1
    assert updated.last_accessed_at is not None


@pytest.mark.asyncio
async def test_delete_expired_links(mock_db: AsyncSession):
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()

    await crud.delete_expired_links(mock_db)
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_cache_popular_links(mock_db: AsyncSession, mock_redis: aioredis.Redis):
    mock_result = MagicMock()
    mock_result.scalars.return_value = [
        models.Link(short_code="popular1", original_url="https://example.com/1", clicks=100),
        models.Link(short_code="popular2", original_url="https://example.com/2", clicks=50)
    ]
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_redis.setex = AsyncMock()

    await crud.cache_popular_links(mock_db, mock_redis)
    assert mock_redis.setex.await_count == 2