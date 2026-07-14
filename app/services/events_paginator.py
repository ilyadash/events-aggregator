from urllib.parse import parse_qs, urlparse

from app.services.provider_client import EventsProviderClient


class EventsPaginator:
    def __init__(self, client: EventsProviderClient, changed_at: str):
        self._client = client
        self._changed_at = changed_at
        self._cursor: str | None = None
        self._buffer: list = []
        self._exhausted = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._buffer and not self._exhausted:
            resp = await self._client.fetch_events(self._changed_at, self._cursor)
            self._buffer = resp.get("results", [])
            next_url = resp.get("next")
            if next_url:
                qs = parse_qs(urlparse(next_url).query)
                self._cursor = qs.get("cursor", [None])[0]
            else:
                self._exhausted = True
        if not self._buffer:
            raise StopAsyncIteration
        return self._buffer.pop(0)
