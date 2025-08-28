# mm-telegram

A Python library for building Telegram bots with type safety and modern async/await patterns.

## Features

- **Type-safe**: Full type annotations with mypy strict mode support
- **Async/await**: Built on python-telegram-bot with modern async patterns
- **Message splitting**: Automatic handling of long messages (>4096 chars)
- **Admin control**: Built-in admin authorization system
- **Simple API**: Minimal boilerplate for common bot operations

## Quick Start

### Basic Bot

```python
from mm_telegram import TelegramBot
from telegram.ext import CommandHandler

async def hello(update, context):
    await update.message.reply_text("Hello!")

bot = TelegramBot(
    handlers=[CommandHandler("hello", hello)],
    bot_data={}
)

await bot.start(token="YOUR_BOT_TOKEN", admins=[YOUR_USER_ID])
```

### Send Messages

```python
from mm_telegram import send_message

result = await send_message(
    bot_token="YOUR_BOT_TOKEN",
    chat_id=123456789,
    message="Your message here"
)

if result.is_ok():
    message_ids = result.value
    print(f"Sent messages: {message_ids}")
```

## API Reference

### TelegramBot

Main bot wrapper that manages application lifecycle.

```python
bot = TelegramBot(handlers, bot_data)
await bot.start(token, admins)
await bot.shutdown()
```

- `handlers`: List of telegram handlers (CommandHandler, MessageHandler, etc.)
- `bot_data`: Initial bot data dictionary
- `token`: Bot token from @BotFather
- `admins`: List of admin user IDs

### send_message

Send messages with automatic splitting for long text.

```python
result = await send_message(
    bot_token="token",
    chat_id=123,
    message="text",
    timeout=5,
    inter_message_delay_seconds=3
)
```

Returns `Result[list[int]]` with message IDs on success.

### Built-in Handlers

- `/ping` - Responds with "pong"
- Unknown commands - "Sorry, I didn't understand that command."
- Admin check - Blocks non-admin users
