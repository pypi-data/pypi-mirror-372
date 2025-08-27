from pydantic import BaseModel, Field
from maleo.soma.enums.field import ExcludableField
from maleo.soma.mixins.parameter import Exclude as BaseExclude
from maleo.soma.types.base import OptionalString


class Exclude(BaseExclude[ExcludableField]):
    pass


class Key(BaseModel):
    key: str = Field(..., max_length=20, description="User type's key")


class Name(BaseModel):
    name: str = Field(..., max_length=20, description="User type's name")


class OptionalName(BaseModel):
    name: OptionalString = Field(
        None, max_length=20, description="User type's name. (Optional)"
    )
