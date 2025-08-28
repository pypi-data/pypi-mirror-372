from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from os import getenv, PathLike
import re
from types import NoneType, UnionType
from typing import Any

from dotenv import load_dotenv
import loguru

from ...logs import get_logger


@dataclass(init=True, slots=True, frozen=True)
class SettingsField[T: type]:
	"""Typed field declaration for AppSettings.

	**Parameters:**

	- `T`: Python type of the value.

	**Attributes:**

	- `default`: Optional fallback value when the variable is missing.
	- `factory`: A callable returning a value, or a name of a @property on the class that will be evaluated after initialization.
	- `nullable`: Whether None is allowed when no value is provided and no default/factory is set.
	"""

	default: T = None
	factory: Callable[[], T] | str = None
	nullable: bool = True


@dataclass
class AppSettings:
	"""Base class for reading typed settings from environment variables.

	Declare attributes with type annotations and assign SettingsField(...) to each.
	On initialization, values are resolved from the environment (loading .env if provided),
	then from default/factory, or set to None if nullable.

	**Notes:**

	Only immutable primitive types are allowed: int, float, complex, str, bool, None.

	If explicit_format is True, attribute names must be UPPER_SNAKE_CASE.

	**Example:**


	>>> class MySettings(AppSettings):
	...     BOT_TOKEN: str = SettingsField(nullable=False)
	...     POSTGRES_USER: str = SettingsField(default="pguser")
	...     POSTGRES_PASSWORD: str = SettingsField(nullable=False, factory=secrets.rand_urlsafe(8))
	...     SECRET_ALIAS: str = SettingsField(factory="secret")
	...
	...     @property
	...     def secret(self) -> str:
	...         return "computed"


	>>> settings = MySettings()

	"""

	__ALLOWED_TYPES: frozenset[type] = frozenset((int, float, complex, str, bool, NoneType))

	@staticmethod
	def _evaluate_var(_type: type, _var: str) -> Any:
		if _type is bool:
			return "true" in _var.lower()
		return _type(_var)

	def __init__(
		self,
		dotenv_path: str | PathLike[str] | None = None,
		logger: logging.Logger | loguru.Logger | None = None,
		explicit_format: bool = True,
	) -> None:
		"""Initialize AppSettings and resolve annotated fields.

		**Parameters:**

		- `dotenv_path`: Optional path to a .env file. If None, python-dotenv searches recursively.
		- `logger`: Optional logging or loguru logger. Defaults to autisticstuff.astuff_logs.factory.get_logger("utilities.appsettings") if not provided.
		- `explicit_format`: If True, attribute names must be uppercase with underscores.

		**Raises:**

		- `AttributeError`: If an attribute name violates explicit_format constraint or a declared property is missing.
		- `TypeError`: If an annotation uses a disallowed (mutable) type or a factory reference is not a property.
		- `ValueError`: If a required field (nullable=False, no default/factory) is missing in the environment.
		"""
		load_dotenv(dotenv_path=dotenv_path)
		self._logger: loguru.Logger = get_logger("utilities.appsettings") if logger is None else logger
		_settings_fields: dict[str, SettingsField] = {}
		for _attribute in self.__annotations__:
			_settings_fields[_attribute] = self.__class__.__dict__[_attribute]
		_attribute_map: list[tuple[str, str]] = []
		_annotations: dict[str, type] = self.__annotations__
		for _attribute in _settings_fields:
			if explicit_format and not re.match(r"[A-Z_]", _attribute):
				raise AttributeError("AppSettings attributes should contain only capital letters and underscores")

			_settings_field: SettingsField = _settings_fields[_attribute]
			_annotated_type: type = _annotations[_attribute]
			if (
				_annotated_type not in self.__ALLOWED_TYPES
				and isinstance(_annotated_type, UnionType)
				and not all(_type in self.__ALLOWED_TYPES for _type in _annotated_type.__args__)
			):
				raise TypeError(f"{_annotated_type} is not allowed for annotations as it is mutable")
			_string_value: str | None = getenv(_attribute, None)

			if _string_value is None:
				if _settings_field.default is not None:
					self._logger.info(f"Successfully evaluated {_attribute}={_settings_field.default} by default")
					setattr(self, _attribute, _settings_field.default)
					continue
				if _settings_field.factory is not None and isinstance(_settings_field.factory, str):
					self._logger.info(f"Postponed {_attribute} initialization as factory is a property")
					_attribute_map.append((_attribute, _settings_field.factory))
					continue
				if callable(_settings_field.factory):
					self._logger.info(f"Successfully evaluated {_attribute} from factory")
					setattr(self, _attribute, _settings_field.factory())
					continue
				if _settings_field.nullable:
					self._logger.info(f"Nulled {_attribute}")
					setattr(self, _attribute, None)
					continue
				raise ValueError(f"Required field {_attribute} was not found in .env")

			_value: _annotated_type = self._evaluate_var(_annotated_type, _string_value)  # type: ignore
			self._logger.info(f"Successfully evaluated {_attribute}={_value}")
			setattr(self, _attribute, _value)

		self.__init_factory_defined(_attribute_map=_attribute_map)

	def __init_factory_defined(self, _attribute_map: list[tuple[str, str]]):
		for _attribute, _property in _attribute_map:
			if _property not in self.__class__.__dict__:
				raise AttributeError(f"Property {_property} was not found in {self.__class__.__name__}")
			if not isinstance(getattr(self.__class__, _property), property):
				raise TypeError(f"Method {_property} is not a property")
			self._logger.info(f"Successfully evaluated {_attribute} from property {_property}")
			setattr(self, _attribute, getattr(self, _property))
