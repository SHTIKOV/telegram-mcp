from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatAllowlist:
    numeric_ids: set[int]
    usernames: set[str]

    def is_allowed(
        self,
        *,
        chat_id: int | None = None,
        username: str | None = None,
    ) -> bool:
        if chat_id is not None and chat_id in self.numeric_ids:
            return True
        if username:
            normalized = username.lstrip("@").lower()
            if normalized in self.usernames:
                return True
        return False


def parse_allowed_chat_ids(raw: str) -> ChatAllowlist:
    """Parse TELEGRAM_ALLOWED_CHAT_IDS. Fail closed: empty is an error."""
    tokens = [part.strip() for part in (raw or "").split(",")]
    tokens = [t for t in tokens if t]

    if not tokens:
        raise ValueError(
            "TELEGRAM_ALLOWED_CHAT_IDS is required and must list at least one "
            "chat id or @username (comma-separated)."
        )

    numeric_ids: set[int] = set()
    usernames: set[str] = set()

    for token in tokens:
        if token.lstrip("-").isdigit():
            numeric_ids.add(int(token))
        else:
            usernames.add(token.lstrip("@").lower())

    return ChatAllowlist(numeric_ids=numeric_ids, usernames=usernames)
