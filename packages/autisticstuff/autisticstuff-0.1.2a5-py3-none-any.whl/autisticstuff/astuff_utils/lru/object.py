from collections.abc import Callable
from functools import lru_cache


def add_cached_handler_for_instance(instance: type[object], *args: object, **kwargs: object) -> Callable[[], object]:
	"""Get a @lru_cache wrapper for object instance

	Args:
		instance (type[object]): uninitialized object
		*args (Any): positional arguments to pass on initialization,
		**kwargs (dict[str, Any]): keyword arguments to pass on initialization

	Returns:
		- Callable[[], object] - @lru_cache-wrapped function to retrieve a given instance
	"""

	@lru_cache
	def _():
		return instance(*args, **kwargs)

	return _
