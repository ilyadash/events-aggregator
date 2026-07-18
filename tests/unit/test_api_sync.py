from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_trigger_sync(client, monkeypatch):
    mock_job = AsyncMock()
    monkeypatch.setattr("app.api.routes.sync.run_sync_job", mock_job)

    resp = await client.post("/api/sync/trigger")

    assert resp.status_code == 200
    assert resp.json() == {"status": "started"}
    mock_job.assert_called_once_with()
