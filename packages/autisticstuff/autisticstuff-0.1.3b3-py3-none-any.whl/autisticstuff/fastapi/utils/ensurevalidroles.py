from collections.abc import Callable
from enum import StrEnum
from typing import Any

from fastapi import Depends

from autisticstuff.utils._dev.placeholders import _raise_ni_error


class EnsureValidRoles:
	"""
	This class is an async callable intended to be used as a FastAPI dependency (for example, Depends(EnsureValidRoles("admin"))).
	When invoked by FastAPI, it obtains a user object from the configured dependency, checks that the user's roles include all required roles, and returns the user if the check passes. If the check fails, the configured exception is raised.

	**Attributes:**

	- `_TO_RAISE`: Exception type to raise when the user does not have the required roles `(default: PermissionError)`. Subclass to change the exception (for example, to an `HTTPException` to control HTTP response).

	- `_GET_USER_DEPENDENCY`: Callable used as the FastAPI dependency to obtain the current user. By default this is an internal placeholder raising `NotImplementedError` and should be overridden to integrate with the application's auth.

	- `_ROLES_ATTR`: Attribute name on the user object that contains the user's roles (default: `roles`).

	**Parameters:**

	- `*roles`: One or more role identifiers required for access. Each role may be a plain string or a StrEnum member. Roles passed to the constructor are collected into an immutable frozenset and used for membership checks.

	**Raises:**

	- `_TO_RAISE`: If the authenticated user's roles do not include all required roles.

	**Examples:**

	```python
	from ... import EnsureValidRoles
	EnsureValidRoles._GET_USER_DEPENDENCY = __your_get_current_user_dependency
	@router.get("/", dependencies=[Depends(EnsureValidRoles("admin"))])
	async def(*, _)...
	```

	**Notes:**

	Role comparison is performed by set membership; ensure roles are comparable (for example, same enum type or strings)."""

	_TO_RAISE: BaseException = PermissionError
	_GET_USER_DEPENDENCY: Callable[..., Any] = _raise_ni_error
	_ROLES_ATTR: str = "roles"

	def __init__(self, *roles: str | StrEnum):
		self.roles = frozenset(roles)

	async def __call__(self, user: Any = Depends(_GET_USER_DEPENDENCY)) -> Any:
		roles_attr = getattr(user, self._ROLES_ATTR, None)
		if roles_attr is None or isinstance(roles_attr, str):
			raise self._TO_RAISE(f"user object does not have a valid iterable '{self._ROLES_ATTR}' attribute")
		try:
			user_roles = frozenset(roles_attr)
		except TypeError:
			raise self._TO_RAISE(f"user '{self._ROLES_ATTR}' attribute is not iterable")
		if not self.roles.issubset(user_roles):
			raise self._TO_RAISE("user does not have required roles")
		return user
