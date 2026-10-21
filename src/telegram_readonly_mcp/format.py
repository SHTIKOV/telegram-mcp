from __future__ import annotations

from typing import Any


def format_message(msg: Any) -> dict[str, Any]:
    reply_to = getattr(msg, "reply_to", None)
    reply_to_msg_id = getattr(reply_to, "reply_to_msg_id", None) if reply_to else None
    date = getattr(msg, "date", None)
    text = getattr(msg, "message", None) or ""

    return {
        "id": getattr(msg, "id", None),
        "date": date.isoformat() if date is not None and hasattr(date, "isoformat") else None,
        "text": text,
        "sender_id": getattr(msg, "sender_id", None),
        "reply_to_msg_id": reply_to_msg_id,
        "has_media": getattr(msg, "media", None) is not None,
    }


def format_chat(entity: Any) -> dict[str, Any]:
    return {
        "id": getattr(entity, "id", None),
        "title": getattr(entity, "title", None) or getattr(entity, "first_name", None),
        "username": getattr(entity, "username", None),
        "participants_count": getattr(entity, "participants_count", None),
    }
