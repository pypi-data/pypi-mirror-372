from collections.abc import Callable, Coroutine
from typing import Any


__all__ = ["sync_update_with_callback", "update_with_callback"]


async def update_with_callback(
	obj: object | dict[str, Any],
	data: dict[str, Any],
	_onupdate: dict[str, Coroutine | tuple[Callable[..., Coroutine], bool]] | None = None,
) -> tuple[object | dict, list[str]]:
	"""Asynchronously updates the attributes of an object if their values differ
	from the provided data and tracks the modified attributes.

	**Parameters:**

	- `obj`: The object whose attributes are to be updated. Needs to have __getattr__ and __setattr__ implemented.
	- `data`: A dictionary containing attribute-value pairs to update.
	- `_onupdate`: A dictionary mapping attribute names to coroutines or tuples of (callable, bool). If a tuple is provided, the boolean determines whether the callable is invoked with the new value.

	**Returns:**

	A tuple containing the updated object and a list of modified attributes.
	"""
	if _onupdate is None:
		_onupdate = {}
	modified = []
	for attr, val in data.items():
		if getattr(obj, attr) != val:
			modified.append(attr)
			setattr(obj, attr, val)
			if attr in _onupdate:
				if not isinstance(_onupdate[attr], tuple):
					await _onupdate[attr]
				elif _onupdate[attr][1]:
					await _onupdate[attr][0](val)
				else:
					await _onupdate[attr][0]()
	return obj, modified


def sync_update_with_callback(
	obj,
	data: dict[str, Any],
	_onupdate: dict[str, tuple[Callable[..., None], bool]] | None = None,
):
	"""Synchronously updates the attributes of an object if their values differ
	from the provided data and tracks the modified attributes.

	**Parameters:**

	- `obj`: The object whose attributes are to be updated. Needs to have __getattr__ and __setattr__ implemented.
	- `data`: A dictionary containing attribute-value pairs to update.
	- `_onupdate`: A dictionary mapping attribute names to tuples of (callable, bool). The boolean determines whether the callable is invoked with the new value.

	**Returns:**

	A tuple containing the updated object and a list of modified attributes.
	"""
	if _onupdate is None:
		_onupdate = {}
	modified = []
	for attr, val in data.items():
		if getattr(obj, attr) != val:
			modified.append(attr)
			setattr(obj, attr, val)
			if attr in _onupdate:
				if _onupdate[attr][1]:
					_onupdate[attr][0](val)
				else:
					_onupdate[attr][0]()
	return obj, modified
