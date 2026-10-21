import pytest

from telegram_readonly_mcp.allowlist import ChatAllowlist, parse_allowed_chat_ids


def test_parse_empty_raises():
    with pytest.raises(ValueError, match="TELEGRAM_ALLOWED_CHAT_IDS"):
        parse_allowed_chat_ids("")


def test_parse_whitespace_only_raises():
    with pytest.raises(ValueError, match="TELEGRAM_ALLOWED_CHAT_IDS"):
        parse_allowed_chat_ids("  ,  ")


def test_parse_ids_and_usernames():
    allowlist = parse_allowed_chat_ids("123, -100987654321, @MyGroup, mychannel")
    assert allowlist.numeric_ids == {123, -100987654321}
    assert allowlist.usernames == {"mygroup", "mychannel"}


def test_allows_numeric_id():
    allowlist = ChatAllowlist(numeric_ids={-1001}, usernames=set())
    assert allowlist.is_allowed(chat_id=-1001)
    assert not allowlist.is_allowed(chat_id=-1002)


def test_allows_username_case_insensitive():
    allowlist = ChatAllowlist(numeric_ids=set(), usernames={"schooldevs"})
    assert allowlist.is_allowed(username="SchoolDevs")
    assert allowlist.is_allowed(username="@schooldevs")
    assert not allowlist.is_allowed(username="other")


def test_allows_when_either_id_or_username_matches():
    allowlist = ChatAllowlist(numeric_ids={42}, usernames={"ops"})
    assert allowlist.is_allowed(chat_id=99, username="ops")
    assert allowlist.is_allowed(chat_id=42, username="nope")
    assert not allowlist.is_allowed(chat_id=99, username="nope")
