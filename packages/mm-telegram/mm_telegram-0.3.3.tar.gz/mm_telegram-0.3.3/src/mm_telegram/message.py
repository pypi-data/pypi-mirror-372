import asyncio

from mm_http import http_request
from mm_result import Result


async def send_message(
    bot_token: str,
    chat_id: int,
    message: str,
    timeout: float = 5,
    inter_message_delay_seconds: int = 3,
) -> Result[list[int]]:
    """
    Sends a message to a Telegram chat.

    If the message exceeds the Telegram character limit (4096),
    it will be split into multiple messages and sent sequentially
    with a delay between each part.

    Args:
        bot_token: The Telegram bot token.
        chat_id: The target chat ID.
        message: The message text to send.
        timeout: The HTTP request timeout in seconds. Defaults to 5.
        inter_message_delay_seconds: The delay in seconds between sending
            parts of a long message. Defaults to 3.

    Returns:
        A Result object containing a list of message IDs for the sent messages
        on success, or an error details on failure. The 'extra' field in the
        Result contains the raw responses from the Telegram API.
    """
    messages = _split_string(message, 4096)
    responses = []
    result_message_ids = []
    while True:
        text_part = messages.pop(0)
        params = {"chat_id": chat_id, "text": text_part}
        res = await http_request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage", method="post", json=params, timeout=timeout
        )
        responses.append(res.to_dict())
        if res.is_err():
            return Result.err(res.error or "error sending message", extra={"responses": responses})

        message_id = res.parse_json_body("result.message_id", none_on_error=True)
        if message_id:
            result_message_ids.append(message_id)
        else:
            # Log the unexpected response for debugging?
            return Result.err("unknown_response_structure", extra={"responses": responses})

        if len(messages):
            await asyncio.sleep(inter_message_delay_seconds)
        else:
            break
    return Result.ok(result_message_ids, extra={"responses": responses})


def _split_string(text: str, chars_per_string: int) -> list[str]:
    """Splits a string into a list of strings, each with a maximum length."""
    return [text[i : i + chars_per_string] for i in range(0, len(text), chars_per_string)]
