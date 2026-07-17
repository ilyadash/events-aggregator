from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from app.database import Base
from app.models.event import Event
from app.models.place import Place


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: requires a real PostgreSQL container"
    )


@pytest.fixture(scope="session")
def pg_container():
    container = PostgresContainer("postgres:16-alpine", driver="asyncpg")
    try:
        container.start()
    except Exception as e:
        pytest.skip(f"Docker is not available: {e}")
    yield container
    container.stop()


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def async_engine(pg_container):
    url = pg_container.get_connection_url()
    engine = create_async_engine(url, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine):
    conn = await async_engine.connect()
    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    yield session
    await session.close()
    await trans.rollback()
    await conn.close()


def make_place(**overrides):
    data = dict(
        id=uuid4(),
        name="Main Hall",
        city="Moscow",
        address="Tverskaya 1",
        seats_pattern="A-C:1-10",
        changed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    data.update(overrides)
    return Place(**data)


def make_event(place=None, **overrides):
    place = place or make_place()
    data = dict(
        id=uuid4(),
        name="Concert",
        place_id=place.id,
        event_time=datetime(2026, 8, 1, 19, 0, tzinfo=timezone.utc),
        registration_deadline=datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc),
        status="published",
        number_of_visitors=42,
        changed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        status_changed_at=datetime.now(timezone.utc),
    )
    data.update(overrides)
    return Event(**data)
