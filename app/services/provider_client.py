from typing import Any
from uuid import UUID

import httpx

from app.config import settings


class ProviderError(Exception):
    def __init__(self, status_code: int, detail: Any = None):
        self.status_code = status_code
        self.detail = detail


class EventsProviderClient:
    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self.base_url = base_url or settings.EVENT_PROVIDER_URL
        self.api_key = api_key or settings.LMS_API_KEY
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"x-api-key": self.api_key},
                timeout=30,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def fetch_events(
        self, changed_at: str, cursor: str | None = None
    ) -> dict:
        client = await self._get_client()
        params: dict[str, str] = {"changed_at": changed_at}
        if cursor:
            params["cursor"] = cursor
        resp = await client.get("/api/events/", params=params)
        if resp.status_code != 200:
            raise ProviderError(resp.status_code, resp.text)
        return resp.json()

    async def fetch_seats(self, event_id: UUID) -> list[str]:
        client = await self._get_client()
        resp = await client.get(f"/api/events/{event_id}/seats/")
        if resp.status_code == 404:
            raise ProviderError(404, "Event not found")
        if resp.status_code == 500:
            raise ProviderError(500, "Event is not published")
        if resp.status_code != 200:
            raise ProviderError(resp.status_code, resp.text)
        return resp.json()["seats"]

    async def register(self, event_id: UUID, body: dict) -> dict:
        client = await self._get_client()
        resp = await client.post(
            f"/api/events/{event_id}/register/", json=body
        )
        if resp.status_code not in (200, 201):
            raise ProviderError(resp.status_code, resp.text)
        return resp.json()

    async def unregister(self, event_id: UUID, ticket_id: str) -> dict:
        client = await self._get_client()
        resp = await client.request(
            "DELETE",
            f"/api/events/{event_id}/unregister/",
            json={"ticket_id": ticket_id},
        )
        if resp.status_code != 200:
            raise ProviderError(resp.status_code, resp.text)
        return resp.json()
