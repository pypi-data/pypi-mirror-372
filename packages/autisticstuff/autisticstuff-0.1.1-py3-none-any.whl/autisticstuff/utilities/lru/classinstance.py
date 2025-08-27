from collections.abc import Callable
from functools import lru_cache


def add_cached_handler_for_instance(instance: type[object], *args: object, **kwargs: object) -> Callable[[], object]:
	"""
	Get a @lru_cached wrapper for instance

	Args:
		instance (type[object]): uninitialized instance to lru
		*args (Any): positional arguments to pass to instance,
		**kwargs (dict[str, Any]): keyword arguments to pass to instance

	Returns:
		- Callable[[], object] - @lru_cache-wrapped function to retrieve a given instance
	"""

	@lru_cache
	def _():
		return instance(*args, **kwargs)

	return _
