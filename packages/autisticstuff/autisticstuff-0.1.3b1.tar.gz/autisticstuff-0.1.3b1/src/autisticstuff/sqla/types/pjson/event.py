from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm.attributes import flag_modified

from .type import PydanticJSON


def flag_pydantic_changes(target):
	"""Function to be binded on 'before_update' SQLA event for BaseModel.

	Example:
	>>> from sqlalchemy import event
	>>> from pydantic import BaseModel
	>>> @event.listens_for(BaseModel, "before_update")
	>>> def _(mapper, connection, target) -> None:
	...     flag_pydantic_changes(target)
	"""
	inspector = inspect(target)
	mapper = inspector.mapper

	for attr in inspector.attrs:
		key = attr.key
		prop = mapper.attrs.get(key)

		if not isinstance(prop, ColumnProperty):
			continue

		is_pyd_type = any(isinstance(col.type, PydanticJSON) for col in prop.columns)

		if is_pyd_type:
			hist = attr.history
			original_dict = hist.unchanged[0] if hist.unchanged else None
			current_dict = attr.value.model_dump() if issubclass(attr.value.__class__, BaseModel) else attr.value

			if original_dict != current_dict:
				flag_modified(target, key)
