from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.provider_client import EventsProviderClient, ProviderError


def _make_async_response(status_code: int, json_data: dict):
    """Create an awaitable mock that behaves like httpx.Response."""
    async def fake(*args, **kwargs):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data
        resp.text = str(json_data)
        return resp
    return fake


@pytest.fixture
def client():
    c = EventsProviderClient("http://test.api", "test-key")
    c._client = AsyncMock()
    return c


@pytest.mark.asyncio
async def test_fetch_events_success(client):
    client._client.get = _make_async_response(200, {
        "next": None, "previous": None, "results": []
    })
    result = await client.fetch_events("2024-01-01")
    assert result["results"] == []


@pytest.mark.asyncio
async def test_fetch_events_with_cursor(client):
    client._client.get = _make_async_response(200, {
        "next": "http://test.api/events/?cursor=abc", "results": [{"id": "1"}]
    })
    result = await client.fetch_events("2024-01-01", "abc")
    assert result["results"][0]["id"] == "1"


@pytest.mark.asyncio
async def test_fetch_events_error(client):
    client._client.get = _make_async_response(401, {"detail": "Unauthorized"})
    with pytest.raises(ProviderError) as exc:
        await client.fetch_events("2024-01-01")
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_fetch_seats_success(client):
    client._client.get = _make_async_response(200, {"seats": ["A1", "A2"]})
    result = await client.fetch_seats("00000000-0000-0000-0000-000000000001")
    assert result == ["A1", "A2"]


@pytest.mark.asyncio
async def test_fetch_seats_404(client):
    client._client.get = _make_async_response(404, {"detail": "Not found"})
    with pytest.raises(ProviderError) as exc:
        await client.fetch_seats("00000000-0000-0000-0000-000000000001")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_register_success(client):
    client._client.post = _make_async_response(201, {"ticket_id": "ticket-123"})
    result = await client.register("00000000-0000-0000-0000-000000000001", {"seat": "A1"})
    assert result["ticket_id"] == "ticket-123"


@pytest.mark.asyncio
async def test_unregister_success(client):
    client._client.request = _make_async_response(200, {"success": True})
    result = await client.unregister("00000000-0000-0000-0000-000000000001", "ticket-123")
    assert result["success"] is True
