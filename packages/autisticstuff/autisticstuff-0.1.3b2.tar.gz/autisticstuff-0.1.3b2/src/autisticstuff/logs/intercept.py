from collections.abc import Callable
from enum import Enum, IntEnum
import logging
import sys

from loguru import _logger, logger

from .factory import get_logger


class InterceptHandler(logging.Handler):
	"""Bridge handler that forwards stdlib logging records to loguru.

	The handler preserves the original caller depth so loguru shows correct
	file, line and function, and it maps stdlib levels to loguru levels.
	"""

	def _logger_factory(self, name: str | None = None) -> logging.Logger | _logger.Logger:
		"""Return the target logger instance used to emit the message.

		**Parameters:**

		- `name`: Logger name from the stdlib record.

		**Returns:**

		logging.Logger | _logger.Logger: A logger to forward the record to.
		"""
		return get_logger(name)

	def emit(self, record) -> None:
		"""Forward a stdlib LogRecord to loguru.

		This method translates the record level to loguru, finds the correct
		call stack depth (skipping stdlib logging internals), and then emits
		the message via loguru.

		**Parameters:**

		- `record`: The stdlib LogRecord to be handled.
		"""
		try:
			level = logger.level(name=record.levelname).name
		except ValueError:
			level = record.levelno

		frame, depth = sys._getframe(6), 6
		while frame and frame.f_code.co_filename == logging.__file__:
			frame = frame.f_back
			depth += 1

		intercept_logger = self._logger_factory(record.name)

		intercept_logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _register_interception(names: tuple[str], level: "Level" = 30) -> None:
	"""Attach InterceptHandler to given logger names.

	**Parameters:**

	- `names`: Tuple of logger names to intercept.
	- `level`: Minimal logging level for these loggers.
	"""
	for logger_name in names:
		intercepted_logger = logging.getLogger(name=logger_name)
		intercepted_logger.setLevel(level=level.value)
		intercepted_logger.handlers = [InterceptHandler()]


class InterceptionPreset(Enum):
	"""Common logger name presets for popular libraries."""

	_AIOGRAM = ("aiogram",)
	_AIOHTTP = ("aiohttp",)
	_SQLALCHEMY = ("sqlalchemy",)
	_ASYNCPG = ("asyncpg",)
	_UVICORN = ("uvicorn", "uvicorn.access", "uvicorn.error")
	_FASTAPI = ("fastapi",)
	_TASKIQ = ("taskiq",)


class Level(IntEnum):
	"""Integer-based logging levels aligned with stdlib."""

	CRITICAL = 50
	FATAL = 50
	ERROR = 40
	WARNING = 30
	WARN = 30
	INFO = 20
	DEBUG = 10
	NOTSET = 0


def setup_interception_through_loguru(modules: dict[InterceptionPreset | tuple[str], Level]) -> None:
	"""Route stdlib logging through loguru and intercept given modules.

	This sets root logging to use InterceptHandler and reconfigures provided
	modules to go through the handler with the specified level.

	**Parameters:**

	- `modules`: Mapping between a preset (or tuple of logger names) and the minimal Level.
	"""
	logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
	for module, lvl in modules.items():
		_register_interception(names=(module if isinstance(module, tuple) else module.value), level=lvl)


def set_logger_factory_for_interception(factory: Callable[[str], logging.Logger | _logger.Logger]) -> None:
	"""Override the logger factory used by InterceptHandler.

	Use this to customize how the target logger is created per record name
	(e.g., binding extra or switching output).

	**Parameters:**

	- `factory`: Callable that accepts an optional logger name and returns a Logger.

	**Raises:**

	- `TypeError`: If the provided factory is not callable with the expected signature.
	"""
	if not callable(factory):
		raise TypeError(f"factory should be callable, not {type(factory)}")

	InterceptHandler._logger_factory = factory
