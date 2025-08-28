from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from sqlalchemy import func, inspect, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class _BaseMapping(DeclarativeBase):
	"""Base SQLAlchemy mapping class with common functionality.

	This abstract base class provides standard fields and methods that are
	commonly needed across database models including audit timestamps,
	soft delete functionality, and utility methods for serialization.

	**Attributes:**

	- `created_at`: Timestamp when the record was created (set by DBMS)
	- `updated_at`: Timestamp when the record was last updated (set by DBMS)
	- `is_active`: Boolean flag for soft delete functionality
	"""

	__abstract__ = True

	created_at: Mapped[datetime] = mapped_column(server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
	is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

	def to_dict(self, **kw) -> dict[str, Any]:
		"""Convert the model instance to a dictionary representation.

		This method serializes all table columns to a dictionary, with optional
		additional key-value pairs that can be merged in.

		**Parameters:**

		- `**kw`: Additional key-value pairs to merge into the result dictionary

		**Returns:**

		Dictionary containing all column values plus any additional kwargs
		"""
		result = {field.name: getattr(self, field.name) for field in self.__table__.c}
		if kw is not None:
			result.update(kw)
		return result

	def is_loaded(self, key: str):
		"""Check if a specific attribute/relationship has been loaded from the database.

		This method is useful for determining whether accessing an attribute will
		trigger a lazy load operation or if the data is already available in memory.

		**Parameters:**

		- `key`: The name of the attribute/relationship to check

		**Returns:**

		True if the attribute is loaded, False if it would trigger a lazy load

		**Raises:**

		- `KeyError`: If the specified key doesn't exist on the model, includes available keys in the error message
		"""
		if key not in (k := {c.key for c in inspect(self).mapper.all_orm_descriptors}):
			raise KeyError(k)
		return key not in inspect(self).unloaded

	def __str__(self):
		"""
		Return a string representation of the model instance.

		**Returns:**

		String in format "ClassName: {dict_representation}"
		"""
		return f"{self.__class__.__name__}: {self.to_dict()}"


def get_base_mapping(_mixins: Iterable[object], _metadata: MetaData = None) -> type[_BaseMapping]:
	"""Factory function to create a base mapping class with custom mixins and metadata.

	This factory allows you to create customized base mapping classes by combining
	the standard _BaseMapping functionality with additional mixins and custom metadata.

	**Parameters:**

	- `mixins`: An iterable of mixin classes to include in the base mapping. These mixins will be combined with _BaseMapping to create the final base class.
	- `md`: SQLAlchemy MetaData instance to use for the declarative base. Defaults to a new MetaData() instance.

	**Returns:**

	A new base mapping class that combines _BaseMapping with the provided mixins

	**Examples:**

	>>> class TimestampMixin:
	...     def get_age(self):
	...         return datetime.utcnow() - self.created_at

	>>> class SoftDeleteMixin:
	...     def soft_delete(self):
	...         self.is_active = False


	>>> BaseMapping = get_base_mapping([TimestampMixin, SoftDeleteMixin])
	... ...


	>>> class User(BaseMapping):
	...     __tablename__ = "users"
	...     id: Mapped[int] = mapped_column(primary_key=True)
	...     name: Mapped[str]


	>>> # Now User has methods from both mixins plus _BaseMapping functionality
	>>> user = User(name="John")
	>>> user.get_age()  # From TimestampMixin
	>>> user.soft_delete()  # From SoftDeleteMixin
	>>> user.to_dict()  # From _BaseMapping
	"""

	class _Base(_BaseMapping, *_mixins):
		__abstract__ = True
		metadata = _metadata or MetaData()

	return _Base
