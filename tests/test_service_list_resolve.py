from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from telegram_readonly_mcp.allowlist import ChatAllowlist
from telegram_readonly_mcp.service import TelegramReadonlyService


async def test_list_chats_also_resolves_allowlist_entries_missing_from_dialogs():
    allowlist = ChatAllowlist(numeric_ids={-1001, -1002}, usernames={"ops"})
    client = AsyncMock()
    in_dialogs = SimpleNamespace(id=-1001, title="A", username=None, participants_count=1)
    client.get_dialogs = AsyncMock(return_value=[SimpleNamespace(entity=in_dialogs)])

    async def get_entity(ref):
        if ref == -1002:
            return SimpleNamespace(id=-1002, title="B", username=None, participants_count=2)
        if ref == "ops":
            return SimpleNamespace(id=-1003, title="Ops", username="ops", participants_count=3)
        raise AssertionError(ref)

    client.get_entity = AsyncMock(side_effect=get_entity)
    service = TelegramReadonlyService(client=client, allowlist=allowlist)

    chats = await service.list_chats()
    ids = {c["id"] for c in chats}
    assert ids == {-1001, -1002, -1003}
