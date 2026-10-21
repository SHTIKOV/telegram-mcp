from __future__ import annotations

import os
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession


def build_client() -> TelegramClient:
    api_id = os.environ.get("TELEGRAM_API_ID", "").strip()
    api_hash = os.environ.get("TELEGRAM_API_HASH", "").strip()
    if not api_id or not api_hash:
        raise RuntimeError("TELEGRAM_API_ID and TELEGRAM_API_HASH are required")

    session_string = os.environ.get("TELEGRAM_SESSION_STRING", "").strip()
    session_path = os.environ.get("TELEGRAM_SESSION_PATH", "").strip()

    if session_string:
        session: StringSession | str = StringSession(session_string)
    elif session_path:
        session = str(Path(session_path).expanduser())
    else:
        raise RuntimeError(
            "Set TELEGRAM_SESSION_STRING or TELEGRAM_SESSION_PATH "
            "(run telegram-readonly-login first)."
        )

    return TelegramClient(session, int(api_id), api_hash)
