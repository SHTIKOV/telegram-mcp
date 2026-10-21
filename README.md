# telegram-mcp

Минимальный **read-only** [MCP](https://modelcontextprotocol.io/) сервер для Telegram.

Агент в Cursor (или другом MCP-клиенте) может читать историю и искать сообщения **только в явно разрешённых чатах**. Отправки, правок и удаления нет.

Стек: Python 3.10+, [Telethon](https://docs.telethon.dev/) (MTProto), официальный MCP Python SDK.

## Зачем свой, а не чужой

Сторонние Telegram MCP обычно дают полный user-session и десятки write-tools. Здесь наоборот:

- fail-closed allowlist (`TELEGRAM_ALLOWED_CHAT_IDS` обязателен);
- только чтение;
- маленький код, который можно просмотреть целиком.

## Tools

| Tool | Описание |
|------|----------|
| `list_allowed_chats` | Диалоги из allowlist |
| `get_chat` | Метаданные чата |
| `get_history` | История (до 100 сообщений, newest first) |
| `search_messages` | Поиск по тексту внутри одного чата |

## Требования

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (рекомендуется)
- Telegram API ID / Hash с [my.telegram.org/apps](https://my.telegram.org/apps)
- Аккаунт, который уже состоит в нужных группах (лучше отдельный, не основной)

## Быстрый старт

```bash
git clone https://github.com/SHTIKOV/telegram-mcp.git
cd telegram-mcp
uv sync --extra dev
cp .env.example .env
```

Заполни в `.env`:

```env
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELEGRAM_SESSION_PATH=~/.local/state/telegram-readonly-mcp/session
TELEGRAM_ALLOWED_CHAT_IDS=-1001234567890,@your_group
```

Авторизация (код придёт в Telegram / 2FA при необходимости):

```bash
uv run telegram-readonly-login
```

Проверка тестов:

```bash
uv run pytest -q
```

Запуск MCP (stdio):

```bash
uv run telegram-readonly-mcp
```

## Cursor

Добавь в `~/.cursor/mcp.json` (путь к клону подставь свой):

```json
{
  "mcpServers": {
    "telegram-readonly": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/telegram-mcp",
        "run",
        "telegram-readonly-mcp"
      ],
      "env": {
        "TELEGRAM_API_ID": "YOUR_API_ID",
        "TELEGRAM_API_HASH": "YOUR_API_HASH",
        "TELEGRAM_SESSION_PATH": "/home/YOU/.local/state/telegram-readonly-mcp/session",
        "TELEGRAM_ALLOWED_CHAT_IDS": "-1001234567890,@your_group"
      }
    }
  }
}
```

Перезапусти MCP в Cursor. Дальше можно просить: «покажи последние сообщения в группе X» / «найди в чате Y обсуждение деплоя».

## Allowlist

`TELEGRAM_ALLOWED_CHAT_IDS` — обязательный список через запятую:

- numeric id: `-1001234567890`
- username: `@group` или `group`

Пустое значение → сервер не стартует. Запросы вне списка → `access_denied`.

Как узнать id: временно добавь `@username` в allowlist, вызови `list_allowed_chats`, возьми `id` из ответа.

## Безопасность

- Session file / session string = **полный доступ к аккаунту**. Не коммить `.env`, `*.session`, `TELEGRAM_SESSION_STRING`.
- Предпочтительно отдельный Telegram-аккаунт только в нужных группах.
- Не ставь `TELEGRAM_ALLOWED_CHAT_IDS` шире, чем нужно.
- Опциональная транскрипция / отправка сообщений в этом проекте **не реализованы** намеренно.

## Структура

```
src/telegram_readonly_mcp/
  allowlist.py   # парсинг и проверка чатов
  client.py      # Telethon client из env
  format.py      # сериализация сообщений/чатов
  login.py       # CLI авторизации
  server.py      # MCP tools (stdio)
  service.py     # read-only операции
tests/           # unit-тесты с моками (без сети)
```

## Лицензия

MIT — используй и меняй как удобно.
