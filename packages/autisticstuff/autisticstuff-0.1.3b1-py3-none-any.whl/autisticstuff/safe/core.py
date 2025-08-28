import asyncio
from collections.abc import Callable
from typing import Any

from autisticstuff.logs import get_logger


_logger = get_logger("aiohttp.retry_with_backoff")


async def retry_with_backoff(
	func: Callable,
	*args,
	max_retries: int,
	delay: float,
	backoff_factor: float = 2.0,
	exceptions: tuple = (Exception,),
	**kwargs,
) -> Any:
	"""
	Executes an asynchronous function with retry logic and exponential backoff.

	Parameters:
	    func (Callable): The asynchronous function to execute.
	    *args: Positional arguments to pass to `func`.
	    max_retries (int): The maximum number of retry attempts before giving up.
	    delay (float): The initial delay (in seconds) before the first retry.
	    backoff_factor (float, optional): The multiplier applied to the delay after each failed attempt. Default is 2.0.
	    exceptions (tuple, optional): A tuple of exception classes that should trigger a retry. Default is (Exception,).
	    **kwargs: Keyword arguments to pass to `func`.

	Returns:
	    Any: The result returned by `func` if it succeeds.

	Raises:
	    Exception: The last exception raised by `func` if all retries fail.

	Behavior:
	    The function attempts to execute `func` with the provided arguments. If `func` raises an exception specified in `exceptions`,
	    it will retry up to `max_retries` times, waiting for an exponentially increasing delay between attempts (calculated as
	    `delay * (backoff_factor ** attempt)`). If all retries fail, the last exception is raised.
	"""
	for attempt in range(max_retries + 1):
		try:
			return await func(*args, **kwargs)
		except exceptions as e:
			if attempt == max_retries:
				_logger.error(f"failed after {max_retries} retries: {e}")
				raise

			wait_time = delay * (backoff_factor**attempt)
			_logger.warning(f"attempt {attempt + 1} failed: {e}; retrying in {wait_time:.2f}s")
			await asyncio.sleep(wait_time)
