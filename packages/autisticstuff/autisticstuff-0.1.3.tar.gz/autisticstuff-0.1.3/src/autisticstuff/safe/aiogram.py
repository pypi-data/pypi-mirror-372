import asyncio
import contextlib

from aiogram.exceptions import (
	TelegramBadRequest,
	TelegramNetworkError,
	TelegramRetryAfter,
)
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
import aiohttp

from autisticstuff.logs import get_logger

from .core import retry_with_backoff


_logger = get_logger("safe.aiogram")


async def safe_edit_text_with_retry(message: Message, text: str, max_retries: int = 3, **kwargs) -> None:
	async def _edit_text():
		try:
			await message.edit_text(text, **kwargs)
		except TelegramBadRequest as e:
			error_msg = str(e).lower()
			if any(
				phrase in error_msg
				for phrase in [
					"message can't be edited",
					"message to edit not found",
					"new message content and reply markup are exactly the same",
				]
			):
				await message.answer(text, **kwargs)
				if "new message content" in error_msg:
					with contextlib.suppress(Exception):
						await message.delete()
			else:
				raise e
		except TelegramRetryAfter as e:
			_logger.warning(f"rate limited, waiting {e.retry_after} seconds")
			await asyncio.sleep(e.retry_after)
			await message.edit_text(text, **kwargs)

	await retry_with_backoff(
		_edit_text,
		max_retries=max_retries,
		exceptions=(TelegramNetworkError, aiohttp.ClientError, asyncio.TimeoutError),
	)


async def safe_send_message_with_retry(
	event: Message | CallbackQuery,
	text: str,
	reply_markup: InlineKeyboardMarkup | None = None,
	max_retries: int = 3,
	**kwargs,
) -> Message:
	chat_id = event.from_user.id

	async def _send_message():
		try:
			return await event._bot.send_message(chat_id, text, reply_markup=reply_markup, **kwargs)
		except TelegramRetryAfter as e:
			_logger.warning(f"rate limited, waiting {e.retry_after} seconds")
			await asyncio.sleep(e.retry_after)
			return await event._bot.send_message(chat_id, text, reply_markup=reply_markup, **kwargs)

	return await retry_with_backoff(
		_send_message,
		max_retries=max_retries,
		exceptions=(TelegramNetworkError, aiohttp.ClientError, asyncio.TimeoutError),
	)
