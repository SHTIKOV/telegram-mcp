from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from telegram_readonly_mcp.allowlist import ChatAllowlist
from telegram_readonly_mcp.service import AccessDenied, TelegramReadonlyService


@pytest.fixture
def allowlist():
    return ChatAllowlist(numeric_ids={-1001}, usernames={"ops"})


@pytest.fixture
def client():
    return AsyncMock()


@pytest.fixture
def service(client, allowlist):
    return TelegramReadonlyService(client=client, allowlist=allowlist)


async def test_list_chats_filters_to_allowlist(service, client):
    allowed = SimpleNamespace(id=-1001, title="A", username=None, participants_count=3)
    other = SimpleNamespace(id=-2002, title="B", username=None, participants_count=1)
    by_username = SimpleNamespace(id=-3003, title="Ops", username="ops", participants_count=9)
    client.get_dialogs = AsyncMock(
        return_value=[
            SimpleNamespace(entity=allowed),
            SimpleNamespace(entity=other),
            SimpleNamespace(entity=by_username),
        ]
    )
    client.get_entity = AsyncMock(side_effect=AssertionError("should not resolve"))

    chats = await service.list_chats()
    assert {c["id"] for c in chats} == {-1001, -3003}


async def test_get_history_denies_outside_allowlist(service, client):
    entity = SimpleNamespace(id=-999, title="Secret", username=None)
    client.get_entity = AsyncMock(return_value=entity)

    with pytest.raises(AccessDenied):
        await service.get_history(chat="-999", limit=10)

    client.get_messages.assert_not_called()


async def test_get_history_returns_messages(service, client):
    entity = SimpleNamespace(id=-1001, title="Allowed", username=None)
    client.get_entity = AsyncMock(return_value=entity)
    msg = SimpleNamespace(
        id=1,
        date=SimpleNamespace(isoformat=lambda: "2026-01-01T00:00:00+00:00"),
        message="hi",
        sender_id=7,
        reply_to=None,
        media=None,
    )
    client.get_messages = AsyncMock(return_value=[msg])

    result = await service.get_history(chat="-1001", limit=5)
    assert result["chat"]["id"] == -1001
    assert result["messages"][0]["text"] == "hi"
    client.get_messages.assert_awaited_once()


async def test_search_messages_requires_allowlist(service, client):
    entity = SimpleNamespace(id=-1001, title="Allowed", username=None)
    client.get_entity = AsyncMock(return_value=entity)
    client.get_messages = AsyncMock(return_value=[])

    result = await service.search_messages(chat="-1001", query="deploy", limit=20)
    assert result["messages"] == []
    kwargs = client.get_messages.await_args.kwargs
    assert kwargs["search"] == "deploy"
