from typing import Any
from sqlalchemy import Column
from sqlalchemy.orm import DeclarativeBase

__all__ = ["validate_kwargs_for_model"]

def _extract_primary_keys(model: DeclarativeBase) -> set[Column]:
	return {
		c
		for c in model.__table__.columns
		if hasattr(c, "primary_key")
		and c.default is None
		and c.server_default is None
		and c.primary_key
	}


def _extract_not_nullable_without_default(model: DeclarativeBase) -> set[Column]:
	return {
		c
		for c in model.__table__.columns
		if hasattr(c, "nullable")
		and c.default is None
		and c.server_default is None
		and not c.nullable
	}


def validate_kwargs_for_model(model: DeclarativeBase, kwargs: dict[str, Any]):
	required = _extract_primary_keys(model) | _extract_not_nullable_without_default(
		model
	)
	required = {c.name for c in required}
	if not required.issubset(set(kwargs.keys())):
		raise KeyError(
			f"required columns not specified, req={required}, kw={kwargs.keys()}"
		)