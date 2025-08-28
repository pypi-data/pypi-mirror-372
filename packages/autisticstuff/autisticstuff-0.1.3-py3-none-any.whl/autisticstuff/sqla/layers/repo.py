from collections.abc import Coroutine, Iterable
from typing import Any
import uuid

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from ..utils.validate import validate_kwargs_for_model
from .mapping import _BaseMapping


class _BaseRepository:
	"""Base repository class providing common database operations.

	This class implements the repository pattern for SQLAlchemy models,
	providing a consistent interface for CRUD operations and query building.

	**Attributes:**

	- `mapping`: SQLAlchemy mapping class with which this repository will operate on

	**Parameters:**

	- `session`: Asynchronous session of type sqlalchemy.ext.asyncio.AsyncSession

	**Note:**

	You can add autoimport via mixin declared in your own project:

	>>> class AutoimportMixin:
	...     def __init_subclass__(cls) -> None:
	...         cls.mapping = getattr(
	...             __import__(
	...                 name="local_module",
	...                 fromlist=[_model := cls.__class__.__name__.replace("Repository", "*your mapping suffix*")],
	...             ),
	...             _model,
	...         )

	>>> class BaseRepository(_BaseRepository, AutoImportMixin):
	...     pass

	"""

	mapping: _BaseMapping

	def __init__(self, session: AsyncSession, mapping: _BaseMapping = None) -> None:
		"""Initialize the repository with a database session.

		**Parameters:**

		- `session`: SQLAlchemy async session for database operations
		- `mapping`: Mapping to which repository should refer if it is not classwide-defined
		"""
		self.session = session
		if self.__class__.mapping is None and mapping is not None:
			self.__class__.mapping = mapping

	async def get_by_pk(
		self,
		obj_id: Any,
		eager_load: list[str] | None = None,
		key: str | list[str] = "id",
	) -> Coroutine[Any, Any, _BaseMapping | None]:
		"""Retrieve a single object by its primary key or composite key.

		**Parameters:**

		- `obj_id`: The primary key value(s). For composite keys, pass a tuple
		- `eager_load`: List of relationship names to eager load
		- `key`: Column name(s) to use as key. For composite keys, pass a list

		**Returns:**

		The model instance if found, None otherwise
		"""
		query = select(self.mapping)
		if isinstance(key, str):
			if not hasattr(self.mapping, key):
				raise KeyError(f"model {self.mapping.__name__} has no attr {key}")

			instr_attr: InstrumentedAttribute = getattr(self.mapping, key)
			if not isinstance(obj_id, instr_attr.type.python_type):
				raise TypeError(f"obj_id is not an instance of {key} col type")

			query = query.where(getattr(self.mapping, key) == obj_id)
		else:
			if not isinstance(obj_id, tuple) or len(obj_id) != len(key):
				raise ValueError(f"obj_id should be a tuple with {len(key)} elements for composite key")

			conditions = []
			for k, v in zip(key, obj_id, strict=False):
				if not hasattr(self.mapping, k):
					raise KeyError(f"model {self.mapping.__name__} has no attr {k}")
				conditions.append(getattr(self.mapping, k) == v)

			query = query.where(*conditions)

		if eager_load:
			for rel in eager_load:
				if not hasattr(self.mapping, rel):
					raise KeyError(f"model {self.mapping.__name__} has no rel {rel}")
				query = query.options(selectinload(getattr(self.mapping, rel)))

		result = await self.session.execute(query)
		return result.scalars().first()

	async def delete_by_id(self, obj_id: int | uuid.UUID | tuple, key: str | list[str] = "id") -> bool:
		"""Delete an object by its primary key.

		**Parameters:**

		- `obj_id`: The primary key value(s) to delete
		- `key`: Column name(s) to use as key

		**Returns:**

		True if the object was found and deleted, False if not found
		"""
		obj = await self.get_by_pk(obj_id, key=key)
		if obj is None:
			return False
		await self.session.delete(obj)
		await self.session.commit()
		return True

	async def count_by_key_or_none(
		self,
		pair: tuple[str, Any] | None = None,
		opt_args: Iterable[tuple[Any, Any]] | None = None,
	) -> int | None:
		"""Count records matching optional criteria.

		**Parameters:**

		- `pair`: Optional tuple of (column_name, value) for filtering
		- `opt_args`: Optional iterable of (method_name, clause) for additional query methods

		**Returns:**

		Count of matching records, or None if no results
		"""
		stmt = select(sqlalchemy.func.count()).select_from(self.mapping)
		if pair is not None:
			stmt = stmt.where(getattr(self.mapping, pair[0]) == pair[1])

		if opt_args is not None:
			for method, clause in opt_args:
				stmt = getattr(stmt, method)(clause)

		return (await self.session.execute(stmt)).scalar_one_or_none()

	async def create_instance(self, *_, **kwargs) -> Any:
		"""**Parameters:**

		- `**kwargs`: Field values for the new instance

		**Returns:**

		The created and refreshed model instance
		"""
		validate_kwargs_for_model(self.mapping, kwargs)
		instance = self.mapping(**kwargs)  # noqa
		self.session.add(instance)
		await self.session.commit()
		await self.session.refresh(instance)
		return instance

	async def get_all_by_key_or_none(
		self,
		page: int | None = None,
		page_size: int | None = None,
		pair: tuple[str, Any] | None = None,
		opt_args: Iterable[tuple[Any, Any]] | None = None,
		unique: bool = False,
	) -> Coroutine[Any, Any, list[_BaseMapping] | None]:
		"""Retrieve multiple records with optional filtering, pagination, and uniqueness.

		**Parameters:**

		- `page`: Page number for pagination (0-based)
		- `page_size`: Number of records per page
		- `pair`: Optional tuple of (column_name, value) for filtering
		- `opt_args`: Optional iterable of (method_name, clause) for additional query methods
		- `unique`: Whether to return unique results only

		**Returns:**

		List of matching model instances
		"""
		stmt = select(self.mapping)

		if pair is not None:
			stmt = stmt.where(getattr(self.mapping, pair[0]) == pair[1])

		if page is not None and page_size is not None:
			stmt = stmt.offset(page * page_size).limit(page_size)

		if opt_args is not None:
			for method, clause in opt_args:
				stmt = getattr(stmt, method)(clause)

		result = (await self.session.execute(stmt)).scalars()

		if unique:
			result = result.unique()

		return result.all()
