#!/bin/bash
set -e
uv run alembic upgrade head
uv run python -c "import asyncio; from app.services.sync_service import sync_all; asyncio.run(sync_all())"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
