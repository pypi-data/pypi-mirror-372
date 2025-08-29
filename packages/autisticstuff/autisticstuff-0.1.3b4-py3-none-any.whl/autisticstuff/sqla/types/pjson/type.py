from typing import final, override, TYPE_CHECKING

from pydantic import BaseModel
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


if TYPE_CHECKING:
	from typing import Any  # noqa
	from sqlalchemy import Dialect  # noqa
	from sqlalchemy.sql.type_api import TypeEngine  # noqa


@final
class PydanticJSON(sa.types.TypeDecorator["BaseModel"]):
	"""A custom SQLAlchemy type decorator for handling Pydantic models as JSON.

	This class allows storing and retrieving Pydantic models in a database
	column, with support for PostgreSQL's JSONB type.

	**Attributes:**

	- `pydantic_type`: The Pydantic model type to be used.
	- `postgres_use_jsonb`: Whether to use PostgreSQL's JSONB type instead of JSON. Defaults to True.
	"""

	impl = sa.types.JSON

	def __init__(self, pydantic_type: type["BaseModel"], postgres_use_jsonb: bool = True) -> None:
		"""Initialize the PydanticJSON type.

		**Parameters:**

		- `pydantic_type`: The Pydantic model type to be used.
		- `postgres_use_jsonb`: Whether to use PostgreSQL's JSONB type. Defaults to True.

		**Raises:**

		- `TypeError`: If the provided `pydantic_type` is not a subclass of `BaseModel`.
		"""
		super().__init__()
		if not issubclass(pydantic_type, BaseModel):
			raise TypeError(f"{pydantic_type.__name__} is not a subclass of `pydantic.BaseModel`")
		self.pydantic_type = pydantic_type
		self.postgres_use_jsonb = postgres_use_jsonb

	@override
	def load_dialect_impl(self, dialect: "Dialect") -> "TypeEngine[JSONB | sa.JSON]":
		if dialect.name == "postgresql" and self.postgres_use_jsonb:
			return dialect.type_descriptor(JSONB())
		else:
			return dialect.type_descriptor(sa.JSON())

	@override
	def process_bind_param(
		self,
		value: "BaseModel | None",
		dialect: "Dialect",
	) -> "dict[str, Any] | None":
		if value is None:
			return None

		if not isinstance(value, BaseModel):  # dynamic typing.
			raise TypeError(f'The value "{value!r}" is not a pydantic model')  # noqa

		return value.model_dump(mode="json", exclude_unset=True)

	@override
	def process_result_value(
		self,
		value: "dict[str, Any] | None",
		dialect: "Dialect",
	) -> "BaseModel | None":
		return self.pydantic_type(**value) if value else None
