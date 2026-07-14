from unittest.mock import AsyncMock

import pytest

from app.services.events_paginator import EventsPaginator
from app.services.provider_client import EventsProviderClient


@pytest.fixture
def mock_client():
    client = AsyncMock(spec=EventsProviderClient)
    return client


@pytest.mark.asyncio
async def test_single_page(mock_client):
    mock_client.fetch_events.return_value = {
        "next": None,
        "previous": None,
        "results": [{"id": "1"}, {"id": "2"}],
    }
    paginator = EventsPaginator(mock_client, "2024-01-01")
    results = []
    async for event in paginator:
        results.append(event)
    assert len(results) == 2
    assert results[0]["id"] == "1"
    assert results[1]["id"] == "2"
    mock_client.fetch_events.assert_called_once_with("2024-01-01", None)


@pytest.mark.asyncio
async def test_multiple_pages(mock_client):
    mock_client.fetch_events.side_effect = [
        {
            "next": "http://test.api/?cursor=abc",
            "results": [{"id": "1"}],
        },
        {
            "next": None,
            "results": [{"id": "2"}],
        },
    ]
    paginator = EventsPaginator(mock_client, "2024-01-01")
    results = []
    async for event in paginator:
        results.append(event)
    assert len(results) == 2
    assert results[0]["id"] == "1"
    assert results[1]["id"] == "2"
    assert mock_client.fetch_events.call_count == 2


@pytest.mark.asyncio
async def test_empty_response(mock_client):
    mock_client.fetch_events.return_value = {
        "next": None,
        "results": [],
    }
    paginator = EventsPaginator(mock_client, "2024-01-01")
    results = []
    async for event in paginator:
        results.append(event)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_three_pages(mock_client):
    mock_client.fetch_events.side_effect = [
        {
            "next": "http://test.api/?cursor=p1",
            "results": [{"id": "1"}],
        },
        {
            "next": "http://test.api/?cursor=p2",
            "results": [{"id": "2"}],
        },
        {
            "next": None,
            "results": [{"id": "3"}],
        },
    ]
    paginator = EventsPaginator(mock_client, "2024-01-01")
    results = []
    async for event in paginator:
        results.append(event)
    assert len(results) == 3
    assert mock_client.fetch_events.call_count == 3
