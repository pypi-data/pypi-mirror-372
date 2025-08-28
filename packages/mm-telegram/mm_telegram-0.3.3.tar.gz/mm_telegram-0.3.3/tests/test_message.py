import pytest

from mm_telegram import send_message


@pytest.mark.asyncio
async def test_send_message_short_message(telegram_token, telegram_chat_id):
    res = await send_message(telegram_token, telegram_chat_id, "bla")
    assert len(res.unwrap()) == 1


@pytest.mark.asyncio
async def test_send_message_long_message(telegram_token, telegram_chat_id):
    message = ""
    for i in range(1800):
        message += f"{i} "
    res = await send_message(telegram_token, telegram_chat_id, message)
    assert len(res.unwrap()) == 2
