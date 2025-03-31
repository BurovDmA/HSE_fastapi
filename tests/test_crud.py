import pytest
from datetime import datetime, timedelta
from app import crud, schemas
from app.models import Link

@pytest.mark.asyncio
async def test_generate_short_code():
    code = crud.generate_short_code()
    assert len(code) == 6
    assert code.isalnum()

@pytest.mark.asyncio
async def test_create_link(db_session):
    link_data = schemas.LinkCreate(
        original_url="https://example.com",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    result = await crud.create_link(db_session, link_data)
    assert "short_code" in result
    assert len(result["short_code"]) == 6

@pytest.mark.asyncio
async def test_create_link_with_custom_alias(db_session):
    link_data = schemas.LinkCreate(
        original_url="https://example.com",
        custom_alias="custom123",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    result = await crud.create_link(db_session, link_data)
    assert result["short_code"] == "custom123"

@pytest.mark.asyncio
async def test_get_link_by_short_code(db_session, test_link):
    link = await crud.get_link_by_short_code(db_session, "test123")
    assert link is not None
    assert link.original_url == "https://example.com"
    assert link.short_code == "test123"

@pytest.mark.asyncio
async def test_get_link_by_origin(db_session, test_link):
    links = await crud.get_link_by_origin(db_session, "example.com")
    assert len(links) > 0
    assert any(link.original_url == "https://example.com" for link in links)

@pytest.mark.asyncio
async def test_update_link_clicks(db_session, test_link):
    initial_clicks = test_link.clicks
    updated_link = await crud.update_link_clicks(db_session, test_link)
    assert updated_link.clicks == initial_clicks + 1
    assert updated_link.last_accessed_at is not None

@pytest.mark.asyncio
async def test_delete_expired_links(db_session):
    # Создаем просроченную ссылку
    expired_link = Link(
        original_url="https://expired.com",
        short_code="expired123",
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db_session.add(expired_link)
    await db_session.commit()

    # Запускаем очистку
    await crud.delete_expired_links(db_session)

    # Проверяем, что ссылка удалена
    link = await crud.get_link_by_short_code(db_session, "expired123")
    assert link is None

@pytest.mark.asyncio
async def test_cache_popular_links(db_session, redis_client):
    # Создаем несколько ссылок с разным количеством кликов
    links = [
        Link(
            original_url=f"https://example{i}.com",
            short_code=f"test{i}",
            clicks=i,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        for i in range(1, 4)
    ]
    for link in links:
        db_session.add(link)
    await db_session.commit()

    # Кэшируем популярные ссылки
    await crud.cache_popular_links(db_session, redis_client, limit=2)

    # Проверяем, что только топ-2 ссылки закэшированы
    for i in range(1, 4):
        cached_url = await redis_client.get(f"popular:test{i}")
        if i >= 2:
            assert cached_url is not None
        else:
            assert cached_url is None 