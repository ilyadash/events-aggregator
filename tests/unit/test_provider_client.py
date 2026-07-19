from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from app.services.provider_client import EventsProviderClient, ProviderError

TEST_EVENT_ID = UUID("00000000-0000-0000-0000-000000000001")


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
    result = await client.fetch_seats(TEST_EVENT_ID)
    assert result == ["A1", "A2"]


@pytest.mark.asyncio
async def test_fetch_seats_url(client):
    client._client.get.return_value = MagicMock(
        status_code=200, json=lambda: {"seats": []}, text="{}"
    )
    await client.fetch_seats(TEST_EVENT_ID)
    client._client.get.assert_called_once_with(
        "/api/events/00000000-0000-0000-0000-000000000001/seats/"
    )


@pytest.mark.asyncio
async def test_fetch_seats_404(client):
    client._client.get = _make_async_response(404, {"detail": "Not found"})
    with pytest.raises(ProviderError) as exc:
        await client.fetch_seats(TEST_EVENT_ID)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_fetch_seats_500(client):
    client._client.get = _make_async_response(500, {"detail": "Not published"})
    with pytest.raises(ProviderError) as exc:
        await client.fetch_seats(TEST_EVENT_ID)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_register_success(client):
    client._client.post = _make_async_response(201, {"ticket_id": "ticket-123"})
    result = await client.register(TEST_EVENT_ID, {"seat": "A1"})
    assert result["ticket_id"] == "ticket-123"


@pytest.mark.asyncio
async def test_register_url(client):
    client._client.post.return_value = MagicMock(
        status_code=201, json=lambda: {"ticket_id": "ticket-123"}, text='{"ticket_id": "ticket-123"}'
    )
    await client.register(TEST_EVENT_ID, {"seat": "A1"})
    client._client.post.assert_called_once_with(
        "/api/events/00000000-0000-0000-0000-000000000001/register/",
        json={"seat": "A1"},
    )


@pytest.mark.asyncio
async def test_register_error(client):
    client._client.post = _make_async_response(409, {"detail": "Conflict"})
    with pytest.raises(ProviderError) as exc:
        await client.register(TEST_EVENT_ID, {"seat": "A1"})
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_unregister_success(client):
    client._client.request = _make_async_response(200, {"success": True})
    result = await client.unregister(TEST_EVENT_ID, "ticket-123")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_unregister_url(client):
    client._client.request.return_value = MagicMock(
        status_code=200, json=lambda: {"success": True}, text='{"success": true}'
    )
    await client.unregister(TEST_EVENT_ID, "ticket-123")
    client._client.request.assert_called_once_with(
        "DELETE",
        "/api/events/00000000-0000-0000-0000-000000000001/unregister/",
        json={"ticket_id": "ticket-123"},
    )


@pytest.mark.asyncio
async def test_unregister_error(client):
    client._client.request = _make_async_response(404, {"detail": "Not found"})
    with pytest.raises(ProviderError) as exc:
        await client.unregister(TEST_EVENT_ID, "ticket-123")
    assert exc.value.status_code == 404
