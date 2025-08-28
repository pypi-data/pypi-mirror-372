import logging
from typing import Any

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ApplicationHandlerStop,
    BaseHandler,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)


type TelegramHandler = BaseHandler[Any, CallbackContext[ExtBot[None], dict[Any, Any], dict[Any, Any], dict[Any, Any]], Any]


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds with 'pong' to /ping command."""
    if update.effective_chat is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="pong")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles unknown commands with a default response."""
    if update.effective_chat is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks if user is admin and blocks access if not.

    Raises ApplicationHandlerStop if user is not in the admins list.
    """
    admins: list[int] = context.bot_data.get("admins", [])

    if update.effective_user is None or update.message is None:
        raise ApplicationHandlerStop

    if update.effective_user.id not in admins:
        logger.warning("is not admin", extra={"telegram_user_id": update.effective_user.id})
        await update.message.reply_text("Who are you?")
        raise ApplicationHandlerStop


class TelegramBot:
    """Telegram bot wrapper that manages application lifecycle and handlers."""

    app: Application[Any, Any, Any, Any, Any, Any] | None

    def __init__(self, handlers: list[TelegramHandler], bot_data: dict[str, object]) -> None:
        """Initialize bot with custom handlers and initial bot data."""
        self.handlers = handlers
        self.bot_data = bot_data
        self.app = None

    async def start(self, token: str, admins: list[int]) -> None:
        """Start the bot with given token and admin list.

        Raises ValueError if no admins are provided.
        """
        if not admins:
            raise ValueError("No admins provided")
        logger.debug("Starting telegram bot...")
        app = ApplicationBuilder().token(token).build()
        for key, value in self.bot_data.items():
            app.bot_data[key] = value
        app.bot_data["admins"] = admins

        for handler in self.handlers:
            app.add_handler(handler)

        app.add_handler(CommandHandler("ping", ping))
        app.add_handler(MessageHandler(filters.COMMAND, unknown))

        await app.initialize()
        await app.start()
        if app.updater is not None:
            await app.updater.start_polling()
            logger.debug("Telegram bot started.")

        self.app = app

    async def shutdown(self) -> None:
        """Stop the bot and clean up resources."""
        if self.app is not None:
            await self.app.shutdown()
            self.app = None
            logger.debug("Telegram bot stopped.")
