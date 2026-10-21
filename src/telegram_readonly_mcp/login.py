from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession


async def _login(api_id: int, api_hash: str, session_path: Path) -> str:
    session_path.parent.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(str(session_path), api_id, api_hash)
    await client.start()
    me = await client.get_me()
    string = StringSession.save(client.session)
    await client.disconnect()
    print(f"Logged in as: {me.username or me.id}")
    print(f"Session file: {session_path}")
    print("\nTELEGRAM_SESSION_STRING (optional alternative to session file):")
    print(string)
    return string


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Authorize Telegram for readonly MCP")
    parser.add_argument(
        "--session-path",
        default=os.environ.get(
            "TELEGRAM_SESSION_PATH",
            str(Path.home() / ".local/state/telegram-readonly-mcp/session"),
        ),
        help="Path for Telethon .session file (without .session suffix is fine)",
    )
    args = parser.parse_args()

    api_id = os.environ.get("TELEGRAM_API_ID", "").strip()
    api_hash = os.environ.get("TELEGRAM_API_HASH", "").strip()
    if not api_id or not api_hash:
        raise SystemExit(
            "Set TELEGRAM_API_ID and TELEGRAM_API_HASH "
            "(from https://my.telegram.org/apps) in env or .env"
        )

    asyncio.run(_login(int(api_id), api_hash, Path(args.session_path).expanduser()))


if __name__ == "__main__":
    main()
