from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.soma.mixins.data import (
    DataIdentifier,
    DataStatus,
    DataLifecycleTimestamp,
    DataTimestamp,
)
from maleo.metadata.dtos.data.gender import GenderDataDTO
from maleo.metadata.enums.gender import Gender


class GenderKeyMixin(BaseModel):
    gender: Gender = Field(..., description="Single Gender")


class OptionalGenderKeyMixin(BaseModel):
    gender: Optional[Gender] = Field(None, description="Single Gender. (Optional)")


class ListOfGenderKeysMixinMixin(BaseModel):
    genders: List[Gender] = Field(..., description="Multiple Genders")


class OptionalListOfGenderKeysMixin(BaseModel):
    genders: Optional[List[Gender]] = Field(
        None, description="Multiple Genders. (Optional)"
    )


class BasicGenderDataSchema(
    GenderDataDTO,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardGenderDataSchema(
    GenderDataDTO,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullGenderDataSchema(
    GenderDataDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


GenderDetailsT = TypeVar(
    "GenderDetailsT",
    BasicGenderDataSchema,
    StandardGenderDataSchema,
    FullGenderDataSchema,
)


class GenderDetailsMixin(BaseModel, Generic[GenderDetailsT]):
    gender_details: GenderDetailsT = Field(..., description="Single Gender Data")


class OptionalGenderDetailsMixin(BaseModel, Generic[GenderDetailsT]):
    gender_details: Optional[GenderDetailsT] = Field(
        None, description="Single Gender Data. (Optional)"
    )


class ListOfGenderDetailsMixin(BaseModel, Generic[GenderDetailsT]):
    genders_details: List[GenderDetailsT] = Field(
        ..., description="Multiple Genders Data"
    )


class OptionalListOfGenderDetailsMixin(BaseModel, Generic[GenderDetailsT]):
    genders_details: Optional[List[GenderDetailsT]] = Field(
        None, description="Multiple Genders Data. (Optional)"
    )
