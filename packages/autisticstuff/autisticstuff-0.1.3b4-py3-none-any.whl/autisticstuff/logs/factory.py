from functools import lru_cache

from loguru import _logger, logger


@lru_cache
def get_logger(logger_name: str | None = None) -> _logger.Logger:
	"""Return a cached loguru Logger optionally bound with a humanized name.

	If a name is provided, the returned logger is bound with extra["logger_name"]
	in a " src -> sub -> leaf " format so it can be referenced in loguru sinks.

	**Parameters:**

	- `logger_name`: Dotted logger name (e.g., "src.database.service"). If None, return the global logger.

	**Returns:**

	A cached loguru Logger with the extra context bound when name is provided.
	"""
	if logger_name is not None:
		return logger.bind(logger_name=f" {logger_name.replace('.', ' -> ')} ")
	return logger
