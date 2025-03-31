import pytest
from datetime import datetime, timedelta
from fastapi import status

@pytest.mark.asyncio
async def test_create_short_link(client):
    response = client.post(
        "/links/shorten",
        json={
            "original_url": "https://example.com",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "short_code" in response.json()

@pytest.mark.asyncio
async def test_create_short_link_with_custom_alias(client):
    response = client.post(
        "/links/shorten",
        json={
            "original_url": "https://example.com",
            "custom_alias": "custom123",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["short_code"] == "custom123"

@pytest.mark.asyncio
async def test_create_short_link_invalid_url(client):
    response = client.post(
        "/links/shorten",
        json={
            "original_url": "not-a-url",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_redirect_to_original(client, test_link):
    response = client.get(f"/links/{test_link.short_code}", allow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == test_link.original_url

@pytest.mark.asyncio
async def test_redirect_to_nonexistent_link(client):
    response = client.get("/links/nonexistent", allow_redirects=False)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_link(client, test_link):
    response = client.delete(f"/links/{test_link.short_code}")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

    # Проверяем, что ссылка действительно удалена
    response = client.get(f"/links/{test_link.short_code}", allow_redirects=False)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_link(client, test_link):
    new_url = "https://updated-example.com"
    response = client.put(
        f"/links/{test_link.short_code}",
        json={
            "original_url": new_url,
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

    # Проверяем, что ссылка обновлена
    response = client.get(f"/links/{test_link.short_code}", allow_redirects=False)
    assert response.headers["location"] == new_url

@pytest.mark.asyncio
async def test_get_link_stats(client, test_link):
    response = client.get(f"/links/{test_link.short_code}/stats")
    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert stats["original_url"] == test_link.original_url
    assert stats["short_code"] == test_link.short_code
    assert "clicks" in stats
    assert "last_accessed_at" in stats

@pytest.mark.asyncio
async def test_search_links(client, test_link):
    response = client.get(f"/links/search?original_url=example.com")
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) > 0
    assert any(link["original_url"] == test_link.original_url for link in results) 