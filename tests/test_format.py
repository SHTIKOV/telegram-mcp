from types import SimpleNamespace

from telegram_readonly_mcp.format import format_message, format_chat


def test_format_message_basic():
    msg = SimpleNamespace(
        id=10,
        date=SimpleNamespace(isoformat=lambda: "2026-10-21T10:00:00+00:00"),
        message="hello",
        sender_id=55,
        reply_to=None,
        media=None,
    )
    assert format_message(msg) == {
        "id": 10,
        "date": "2026-10-21T10:00:00+00:00",
        "text": "hello",
        "sender_id": 55,
        "reply_to_msg_id": None,
        "has_media": False,
    }


def test_format_message_with_reply_and_media():
    msg = SimpleNamespace(
        id=11,
        date=None,
        message=None,
        sender_id=None,
        reply_to=SimpleNamespace(reply_to_msg_id=7),
        media=object(),
    )
    out = format_message(msg)
    assert out["reply_to_msg_id"] == 7
    assert out["has_media"] is True
    assert out["text"] == ""
    assert out["date"] is None


def test_format_chat():
    entity = SimpleNamespace(
        id=-100123,
        title="Dev Ops",
        username="devops",
        participants_count=12,
    )
    assert format_chat(entity) == {
        "id": -100123,
        "title": "Dev Ops",
        "username": "devops",
        "participants_count": 12,
    }
