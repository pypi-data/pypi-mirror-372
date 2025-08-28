from __future__ import annotations

from typing import Any

from pydantic import Field

from ..base import BaseSO


__all__ = ["ErrorSO", "ResponseSO"]


class ErrorSO(BaseSO):
	spec: str = "unknown"
	detail: str | None = None
	context: dict[str, Any] = Field(default_factory=dict)


class ResponseSO[T: BaseSO](BaseSO):
	payload: T | None = None
	error: ErrorSO | None = None
