from _collections_abc import Coroutine, Iterable
import importlib
import threading
from typing import Any
import uuid

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from autisticstuff.astuff_sqla.utilities.validate import validate_kwargs_for_model

from ..mapping.inst import _BaseMapping


class _LazyMapping:
	"""Descriptor that imports and caches the mapping on first access."""

	def __init__(self, _module: str, _name: str) -> None:
		self._module = _module
		self._class_name = _name
		self._resolved = None
		self._lock = threading.Lock()

	def __get__(self, instance, owner) -> Any:
		if self._resolved is not None:
			return self._resolved
		with self._lock:
			if self._resolved is None:
				try:
					mod = importlib.import_module(self._module)
					self._resolved = getattr(mod, self._class_name)
					owner.mapping = self._resolved
				except Exception as e:
					raise ImportError(f"Could not import mapping '{self._class_name}' from '{self._module}'.") from e
		return self._resolved


class _BaseRepository:
	"""Base repository class providing common database operations.

	This class implements the repository pattern for SQLAlchemy models,
	providing a consistent interface for CRUD operations and query building.

	Attributes:
		mapping: The SQLAlchemy model class this repository operates on
		session: The async database session
	"""

	mapping: _BaseMapping

	def __init__(self, session: AsyncSession) -> None:
		"""Initialize the repository with a database session.

		Args:
			session: SQLAlchemy async session for database operations
		"""
		self.session = session

	async def get_by_pk(
		self,
		obj_id: Any,
		eager_load: list[str] | None = None,
		key: str | list[str] = "id",
	) -> Coroutine[Any, Any, _BaseMapping | None]:
		"""Retrieve a single object by its primary key or composite key.

		Args:
			obj_id: The primary key value(s). For composite keys, pass a tuple
			eager_load: List of relationship names to eager load
			key: Column name(s) to use as key. For composite keys, pass a list

		Returns:
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

		Args:
			obj_id: The primary key value(s) to delete
			key: Column name(s) to use as key

		Returns:
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

		Args:
			pair: Optional tuple of (column_name, value) for filtering
			opt_args: Optional iterable of (method_name, clause) for additional query methods

		Returns:
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
		"""Args:
			**kwargs: Field values for the new instance

		Returns:
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

		Args:
			page: Page number for pagination (0-based)
			page_size: Number of records per page
			pair: Optional tuple of (column_name, value) for filtering
			opt_args: Optional iterable of (method_name, clause) for additional query methods
			unique: Whether to return unique results only

		Returns:
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


def get_base_repository(
	autoimport_mapping: bool = False,
	from_module: str | None = None,
	by_name_replace: tuple[str, str] = ("Repository", "Mapping"),
) -> type[_BaseRepository]:
	"""Factory function to create a base repository class with optional auto-import functionality.

	This factory allows you to create repository base classes that can automatically
	import their corresponding model mappings based on naming conventions.

	Args:
		autoimport_mapping: Whether to enable auto-import of the mapping. Defaults to False.
		from_module: The module to import the mapping from. Required if autoimport_mapping is True.
		by_name_replace: A tuple specifying the replacement pattern for class names if autoimport_mapping is True.
			Defaults to ("Repository", "Mapping").

	Returns:
		type: The base repository class configured with the specified options.

	Raises:
		ImportError: If autoimport_mapping is True but the mapping cannot be imported

	Warnings:
		If autoimport_mapping is set to True, from_module becomes a required argument.
		Otherwise, you should declare cls.mapping for every child repository manually.

	Examples:
		>>> # Manual mapping assignment
		>>> BaseRepo = get_base_repository()
		>>> class UserRepository(BaseRepo):
		...     mapping = User

		>>> # Auto-import mapping
		>>> BaseRepo = get_base_repository(autoimport_mapping=True, from_module="myapp.models")
		>>> class UserRepository(BaseRepo):  # Will auto-import UserMapping
		...     pass
	"""
	if autoimport_mapping and from_module:

		class _BaseRepo(_BaseRepository):
			def __init_subclass__(cls) -> None:
				_name = cls.__name__.replace(*by_name_replace)
				if getattr(cls, "mapping", None) is None:
					cls.mapping = _LazyMapping(_module=from_module, _name=_name)

		return _BaseRepo

	return _BaseRepository
