import os

import pytest
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


@pytest.fixture
def telegram_token() -> str:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN is not set")
    return TELEGRAM_TOKEN


@pytest.fixture
def telegram_chat_id() -> int:
    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is not set")
    return int(TELEGRAM_CHAT_ID)
