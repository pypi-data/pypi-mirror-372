from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import DeclarativeBase

from autisticstuff.sqla.layers.mapping import _BaseMapping

from .base import BaseSO


def get_base_mso_for_base_mapping(_base_mapping: type[DeclarativeBase] = _BaseMapping):
	if not hasattr(_base_mapping, "to_dict") or not callable(_base_mapping.to_dict):
		raise NotImplementedError(f"{type(_base_mapping)} has no .to_dict() method impl")

	class _BMSO(BaseSO):
		is_active: bool
		created_at: datetime
		updated_at: datetime

		@classmethod
		def from_mapping(cls, mapping: _base_mapping, **kwargs) -> _BMSO:  # type: ignore
			return cls.model_validate(mapping.to_dict() | kwargs)

	return _BMSO
