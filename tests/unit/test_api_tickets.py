from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from app.deps import get_cancel_ticket_uc, get_create_ticket_uc
from app.services.provider_client import ProviderError
from app.usecases.cancel_ticket import CancelTicketUsecase
from app.usecases.create_ticket import CreateTicketUsecase


def make_register_body(event_id=None):
    return {
        "event_id": str(event_id or uuid4()),
        "first_name": "Ivan",
        "last_name": "Petrov",
        "email": "ivan.petrov@example.com",
        "seat": "A1",
    }


@pytest.fixture
def create_ticket_uc(api_app):
    uc = AsyncMock(spec=CreateTicketUsecase)
    api_app.dependency_overrides[get_create_ticket_uc] = lambda: uc
    return uc


@pytest.fixture
def cancel_ticket_uc(api_app):
    uc = AsyncMock(spec=CancelTicketUsecase)
    api_app.dependency_overrides[get_cancel_ticket_uc] = lambda: uc
    return uc


@pytest.mark.asyncio
async def test_create_ticket_created(client, create_ticket_uc):
    event_id = uuid4()
    ticket_id = uuid4()
    create_ticket_uc.do.return_value = ticket_id

    resp = await client.post("/api/tickets", json=make_register_body(event_id))

    assert resp.status_code == 201
    assert resp.json() == {"ticket_id": str(ticket_id)}
    create_ticket_uc.do.assert_awaited_once_with(
        event_id=str(event_id),
        first_name="Ivan",
        last_name="Petrov",
        email="ivan.petrov@example.com",
        seat="A1",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "detail"),
    [
        (404, "Event not found"),
        (400, "Event is not published"),
        (400, "Registration deadline has passed"),
        (400, "Seat is not available"),
    ],
)
async def test_create_ticket_provider_error(
    client, create_ticket_uc, status_code, detail
):
    create_ticket_uc.do.side_effect = ProviderError(status_code, detail)

    resp = await client.post("/api/tickets", json=make_register_body())

    assert resp.status_code == status_code
    assert resp.json()["detail"] == detail


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("event_id", "not-a-uuid"),
        ("email", "not-an-email"),
        ("first_name", None),
        ("seat", None),
    ],
)
async def test_create_ticket_invalid_body(
    client, create_ticket_uc, field, value
):
    body = make_register_body()
    if value is None:
        del body[field]
    else:
        body[field] = value

    resp = await client.post("/api/tickets", json=body)

    assert resp.status_code == 422
    create_ticket_uc.do.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_ticket_ok(client, cancel_ticket_uc):
    ticket_id = uuid4()
    cancel_ticket_uc.do.return_value = True

    resp = await client.delete(f"/api/tickets/{ticket_id}")

    assert resp.status_code == 200
    assert resp.json() == {"success": True}
    cancel_ticket_uc.do.assert_awaited_once_with(ticket_id)
    assert isinstance(cancel_ticket_uc.do.await_args.args[0], UUID)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "detail"),
    [
        (404, "Registration not found"),
        (404, "Event not found"),
        (400, "Event has already passed"),
    ],
)
async def test_cancel_ticket_provider_error(
    client, cancel_ticket_uc, status_code, detail
):
    cancel_ticket_uc.do.side_effect = ProviderError(status_code, detail)

    resp = await client.delete(f"/api/tickets/{uuid4()}")

    assert resp.status_code == status_code
    assert resp.json()["detail"] == detail


@pytest.mark.asyncio
async def test_cancel_ticket_invalid_uuid(client, cancel_ticket_uc):
    resp = await client.delete("/api/tickets/not-a-uuid")

    assert resp.status_code == 422
    cancel_ticket_uc.do.assert_not_awaited()
