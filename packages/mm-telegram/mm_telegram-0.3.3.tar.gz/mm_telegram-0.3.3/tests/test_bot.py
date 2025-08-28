from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationHandlerStop,
    BaseHandler,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from mm_telegram.bot import TelegramBot, TelegramHandler, is_admin, ping, unknown


@pytest.fixture
def mock_update() -> Update:
    """Fixture to create a mock Update object."""
    update = MagicMock(spec=Update)
    update.effective_chat = MagicMock()
    update.effective_chat.id = 12345
    update.effective_user = MagicMock()
    update.effective_user.id = 67890
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context() -> ContextTypes.DEFAULT_TYPE:
    """Fixture to create a mock CallbackContext object."""
    context = MagicMock(spec=CallbackContext)
    context.bot = AsyncMock()
    context.bot_data = {}
    return context


@pytest.fixture
def mock_application() -> MagicMock:
    """Fixture to create a mock Application object."""
    app = MagicMock(spec=Application)
    app.update_queue = AsyncMock()
    app.bot_data = {}
    app.initialize = AsyncMock()
    app.start = AsyncMock()
    app.shutdown = AsyncMock()
    app.updater = MagicMock()
    app.updater.start_polling = AsyncMock()
    app.add_handler = MagicMock()
    app.process_update = AsyncMock()
    return app


def test_telegram_bot_init() -> None:
    """Test TelegramBot initialization."""
    mock_handler = MagicMock(spec=BaseHandler[Update, ContextTypes.DEFAULT_TYPE, object])
    handlers: list[TelegramHandler] = [mock_handler]
    bot_data: dict[str, object] = {"key": "value"}
    bot = TelegramBot(handlers=handlers, bot_data=bot_data)

    assert bot.handlers == handlers
    assert bot.bot_data == bot_data
    assert bot.app is None


@pytest.mark.asyncio
@patch("mm_telegram.bot.ApplicationBuilder")
async def test_telegram_bot_start_success(mock_application_builder_cls: MagicMock, mock_application: MagicMock) -> None:
    """Test TelegramBot.start successfully initializes and starts the application."""
    mock_builder_instance = MagicMock()
    mock_builder_instance.token.return_value = mock_builder_instance
    mock_builder_instance.build.return_value = mock_application
    mock_application_builder_cls.return_value = mock_builder_instance

    # Make lambda async
    async def dummy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pass

    custom_handler = CommandHandler("custom", dummy_handler)
    handlers: list[TelegramHandler] = [custom_handler]
    initial_bot_data: dict[str, object] = {"initial_key": "initial_value"}
    bot = TelegramBot(handlers=handlers, bot_data=initial_bot_data)

    token = "test_token"
    admins = [123, 456]

    await bot.start(token=token, admins=admins)

    mock_application_builder_cls.assert_called_once_with()
    mock_builder_instance.token.assert_called_once_with(token)
    mock_builder_instance.build.assert_called_once_with()

    assert mock_application.bot_data["initial_key"] == "initial_value"
    assert mock_application.bot_data["admins"] == admins

    # Check handlers: 1 custom + 2 default (ping, unknown)
    assert mock_application.add_handler.call_count == 3
    # Check specific handlers were added
    added_handlers = [call.args[0] for call in mock_application.add_handler.call_args_list]
    assert custom_handler in added_handlers
    assert any(isinstance(h, CommandHandler) and h.callback == ping for h in added_handlers)
    assert any(isinstance(h, MessageHandler) and h.callback == unknown and h.filters == filters.COMMAND for h in added_handlers)

    mock_application.initialize.assert_awaited_once()
    mock_application.start.assert_awaited_once()
    assert bot.app == mock_application
    if mock_application.updater:
        mock_application.updater.start_polling.assert_awaited_once()


@pytest.mark.asyncio
async def test_telegram_bot_start_no_admins_raises_value_error() -> None:
    """Test TelegramBot.start raises ValueError if no admins are provided."""
    bot = TelegramBot(handlers=[], bot_data={})
    with pytest.raises(ValueError, match="No admins provided"):
        await bot.start(token="test_token", admins=[])


@pytest.mark.asyncio
async def test_telegram_bot_shutdown(
    mock_application: MagicMock,  # Use the fixture
) -> None:
    """Test TelegramBot.shutdown calls app.shutdown()."""
    bot = TelegramBot(handlers=[], bot_data={})
    bot.app = mock_application  # Assign the mocked application

    await bot.shutdown()

    mock_application.shutdown.assert_awaited_once()
    assert bot.app is None


@pytest.mark.asyncio
async def test_telegram_bot_shutdown_no_app() -> None:
    """Test TelegramBot.shutdown does nothing if app is None."""
    bot = TelegramBot(handlers=[], bot_data={})
    assert bot.app is None
    # Should not raise any error and complete successfully
    await bot.shutdown()
    assert bot.app is None  # Still None


@pytest.mark.asyncio
async def test_ping_handler(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test the ping handler sends 'pong'."""
    assert mock_update.effective_chat is not None
    await ping(mock_update, mock_context)
    cast(AsyncMock, mock_context.bot.send_message).assert_awaited_once_with(chat_id=mock_update.effective_chat.id, text="pong")


@pytest.mark.asyncio
async def test_ping_handler_no_effective_chat(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test the ping handler does nothing if effective_chat is None."""
    cast(MagicMock, mock_update).configure_mock(effective_chat=None)

    await ping(mock_update, mock_context)
    cast(AsyncMock, mock_context.bot.send_message).assert_not_awaited()


@pytest.mark.asyncio
async def test_unknown_handler(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test the unknown handler sends a specific message."""
    assert mock_update.effective_chat is not None  # From fixture
    await unknown(mock_update, mock_context)
    cast(AsyncMock, mock_context.bot.send_message).assert_awaited_once_with(
        chat_id=mock_update.effective_chat.id, text="Sorry, I didn't understand that command."
    )


@pytest.mark.asyncio
async def test_unknown_handler_no_effective_chat(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test the unknown handler does nothing if effective_chat is None."""
    cast(MagicMock, mock_update).configure_mock(effective_chat=None)
    await unknown(mock_update, mock_context)
    cast(AsyncMock, mock_context.bot.send_message).assert_not_awaited()


@pytest.mark.asyncio
async def test_is_admin_user_is_admin(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test is_admin allows an admin user."""
    admin_user_id = 67890
    mock_context.bot_data["admins"] = [admin_user_id]
    assert mock_update.effective_user is not None
    mock_update.effective_user.id = admin_user_id

    # Should not raise ApplicationHandlerStop
    await is_admin(mock_update, mock_context)
    # Ensure no reply was sent (meaning access granted)
    assert mock_update.message is not None
    cast(AsyncMock, mock_update.message.reply_text).assert_not_awaited()


@pytest.mark.asyncio
async def test_is_admin_user_not_admin(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test is_admin blocks a non-admin user and replies."""
    non_admin_user_id = 11111
    mock_context.bot_data["admins"] = [12345]  # Some other admin
    assert mock_update.effective_user is not None
    mock_update.effective_user.id = non_admin_user_id
    assert mock_update.message is not None

    with pytest.raises(ApplicationHandlerStop):
        await is_admin(mock_update, mock_context)

    assert mock_update.message is not None
    cast(AsyncMock, mock_update.message.reply_text).assert_awaited_once_with("Who are you?")


@pytest.mark.asyncio
async def test_is_admin_no_admins_in_bot_data(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test is_admin blocks if 'admins' list is not in bot_data."""
    # Ensure 'admins' key is missing or empty
    if "admins" in mock_context.bot_data:
        del mock_context.bot_data["admins"]
    # Or mock_context.bot_data["admins"] = [] -> this also works due to `get("admins", [])`

    assert mock_update.effective_user is not None
    mock_update.effective_user.id = 12345  # Any user ID
    assert mock_update.message is not None

    with pytest.raises(ApplicationHandlerStop):
        await is_admin(mock_update, mock_context)

    assert mock_update.message is not None
    cast(AsyncMock, mock_update.message.reply_text).assert_awaited_once_with("Who are you?")


@pytest.mark.asyncio
async def test_is_admin_no_effective_user(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test is_admin blocks if effective_user is None."""
    cast(MagicMock, mock_update).configure_mock(effective_user=None)
    mock_context.bot_data["admins"] = [12345]

    with pytest.raises(ApplicationHandlerStop):
        await is_admin(mock_update, mock_context)
    # No reply_text should be called because it exits before that
    assert mock_update.message is not None
    cast(AsyncMock, mock_update.message.reply_text).assert_not_awaited()


@pytest.mark.asyncio
async def test_is_admin_no_message(mock_update: Update, mock_context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test is_admin blocks if message is None (after effective_user check)."""
    # effective_user must exist for this path
    assert mock_update.effective_user is not None
    mock_update.effective_user.id = 11111  # Non-admin, to try to reach reply_text path
    mock_context.bot_data["admins"] = [67890]  # Different admin

    cast(MagicMock, mock_update).configure_mock(message=None)

    with pytest.raises(ApplicationHandlerStop):
        await is_admin(mock_update, mock_context)
    # reply_text is on update.message, so if message is None, this can't be called.
    # The check `if update.message is None: raise ApplicationHandlerStop` prevents it.
    # If reply_text were on context.bot.send_message, we'd check it. But it's on update.message.


# End of tests
