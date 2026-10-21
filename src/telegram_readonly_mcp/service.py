from __future__ import annotations

from typing import Any

from telegram_readonly_mcp.allowlist import ChatAllowlist
from telegram_readonly_mcp.format import format_chat, format_message


class AccessDenied(PermissionError):
    """Raised when a chat is outside TELEGRAM_ALLOWED_CHAT_IDS."""


class TelegramReadonlyService:
    def __init__(self, *, client: Any, allowlist: ChatAllowlist) -> None:
        self._client = client
        self._allowlist = allowlist

    def _ensure_allowed(self, entity: Any) -> None:
        chat_id = getattr(entity, "id", None)
        username = getattr(entity, "username", None)
        if not self._allowlist.is_allowed(chat_id=chat_id, username=username):
            raise AccessDenied(
                f"Access to chat '{chat_id or username}' is denied by TELEGRAM_ALLOWED_CHAT_IDS"
            )

    async def _resolve_entity(self, chat: str | int) -> Any:
        entity = await self._client.get_entity(chat)
        self._ensure_allowed(entity)
        return entity

    async def list_chats(self) -> list[dict[str, Any]]:
        dialogs = await self._client.get_dialogs()
        by_id: dict[int, dict[str, Any]] = {}
        for dialog in dialogs:
            entity = getattr(dialog, "entity", dialog)
            chat_id = getattr(entity, "id", None)
            username = getattr(entity, "username", None)
            if chat_id is not None and self._allowlist.is_allowed(
                chat_id=chat_id, username=username
            ):
                by_id[chat_id] = format_chat(entity)

        for chat_id in self._allowlist.numeric_ids:
            if chat_id in by_id:
                continue
            try:
                entity = await self._client.get_entity(chat_id)
            except Exception:
                continue
            if self._allowlist.is_allowed(
                chat_id=getattr(entity, "id", None),
                username=getattr(entity, "username", None),
            ):
                by_id[entity.id] = format_chat(entity)

        known_usernames = {
            (c.get("username") or "").lower() for c in by_id.values() if c.get("username")
        }
        for username in self._allowlist.usernames:
            if username in known_usernames:
                continue
            try:
                entity = await self._client.get_entity(username)
            except Exception:
                continue
            entity_id = getattr(entity, "id", None)
            if entity_id is not None and self._allowlist.is_allowed(
                chat_id=entity_id,
                username=getattr(entity, "username", None),
            ):
                by_id[entity_id] = format_chat(entity)

        return list(by_id.values())

    async def get_chat(self, chat: str | int) -> dict[str, Any]:
        entity = await self._resolve_entity(chat)
        return format_chat(entity)

    async def get_history(
        self,
        *,
        chat: str | int,
        limit: int = 50,
        offset_id: int = 0,
    ) -> dict[str, Any]:
        entity = await self._resolve_entity(chat)
        limit = max(1, min(int(limit), 100))
        messages = await self._client.get_messages(
            entity,
            limit=limit,
            offset_id=offset_id,
        )
        return {
            "chat": format_chat(entity),
            "messages": [format_message(m) for m in messages],
        }

    async def search_messages(
        self,
        *,
        chat: str | int,
        query: str,
        limit: int = 50,
    ) -> dict[str, Any]:
        entity = await self._resolve_entity(chat)
        limit = max(1, min(int(limit), 100))
        messages = await self._client.get_messages(
            entity,
            limit=limit,
            search=query,
        )
        return {
            "chat": format_chat(entity),
            "query": query,
            "messages": [format_message(m) for m in messages],
        }
