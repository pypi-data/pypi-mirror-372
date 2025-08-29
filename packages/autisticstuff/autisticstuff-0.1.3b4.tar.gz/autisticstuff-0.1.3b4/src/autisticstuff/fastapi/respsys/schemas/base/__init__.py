from typing import Any, ClassVar

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


__all__ = ["BaseSI", "BaseSO"]


class BaseSchema(BaseModel):
	@classmethod
	def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
		cls_name = cls.__name__
		if "[" in cls_name:
			cls_name = cls_name.split("[")[0]
		if not (cls_name.endswith(("SO", "SI"))):
			raise ValueError(
				"child classes of BaseSchema should end with SO or SI for schema-in and schema-out correspondingly"
			)
		super().__init_subclass__(**kwargs)


class BaseSI(BaseSchema):
	model_config: ClassVar[ConfigDict] = ConfigDict(
		use_enum_values=True,
		extra="ignore",
		validate_assignment=True,
		validate_by_alias=True,
		serialize_by_alias=False,
		from_attributes=True,
		defer_build=True,
		alias_generator=AliasGenerator(validation_alias=to_camel),
	)


class BaseSO(BaseSchema):
	model_config: ClassVar[ConfigDict] = ConfigDict(
		use_enum_values=True,
		extra="ignore",
		validate_assignment=True,
		validate_by_alias=False,
		serialize_by_alias=True,
		from_attributes=True,
		defer_build=True,
		alias_generator=AliasGenerator(serialization_alias=to_camel),
	)
