from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

from telegram_readonly_mcp.allowlist import parse_allowed_chat_ids
from telegram_readonly_mcp.client import build_client
from telegram_readonly_mcp.service import AccessDenied, TelegramReadonlyService

load_dotenv()


class AppState:
    service: TelegramReadonlyService | None = None


STATE = AppState()


@asynccontextmanager
async def lifespan(_server: MCPServer) -> AsyncIterator[dict[str, Any]]:
    allowlist = parse_allowed_chat_ids(os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", ""))
    client = build_client()
    await client.connect()
    if not await client.is_user_authorized():
        await client.disconnect()
        raise RuntimeError("Telegram session is not authorized. Run telegram-readonly-login.")
    STATE.service = TelegramReadonlyService(client=client, allowlist=allowlist)
    try:
        yield {"service": STATE.service}
    finally:
        STATE.service = None
        await client.disconnect()


mcp = MCPServer(
    name="telegram-readonly",
    instructions=(
        "Read-only Telegram access limited to TELEGRAM_ALLOWED_CHAT_IDS. "
        "Use list_allowed_chats, get_chat, get_history, search_messages."
    ),
    lifespan=lifespan,
)


def _service() -> TelegramReadonlyService:
    if STATE.service is None:
        raise RuntimeError("Telegram service is not initialized")
    return STATE.service


def _dump(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
async def list_allowed_chats() -> str:
    """List dialogs visible under TELEGRAM_ALLOWED_CHAT_IDS."""
    chats = await _service().list_chats()
    return _dump({"chats": chats, "count": len(chats)})


@mcp.tool()
async def get_chat(chat: str) -> str:
    """Get metadata for one allowed chat (id, @username, or title fragment Telegram resolves)."""
    try:
        return _dump(await _service().get_chat(chat))
    except AccessDenied as exc:
        return _dump({"error": "access_denied", "message": str(exc)})


@mcp.tool()
async def get_history(chat: str, limit: int = 50, offset_id: int = 0) -> str:
    """Fetch recent messages from an allowed chat (newest first). limit max 100."""
    try:
        return _dump(
            await _service().get_history(chat=chat, limit=limit, offset_id=offset_id)
        )
    except AccessDenied as exc:
        return _dump({"error": "access_denied", "message": str(exc)})


@mcp.tool()
async def search_messages(chat: str, query: str, limit: int = 50) -> str:
    """Search message text inside one allowed chat. limit max 100."""
    try:
        return _dump(
            await _service().search_messages(chat=chat, query=query, limit=limit)
        )
    except AccessDenied as exc:
        return _dump({"error": "access_denied", "message": str(exc)})


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
