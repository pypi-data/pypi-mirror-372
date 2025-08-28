from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.soma.mixins.data import (
    DataIdentifier,
    DataStatus,
    DataLifecycleTimestamp,
    DataTimestamp,
)
from maleo.metadata.dtos.data.blood_type import BloodTypeDataDTO
from maleo.metadata.enums.blood_type import BloodType


class BloodTypeKeyMixin(BaseModel):
    blood_type: BloodType = Field(..., description="Single Blood Type")


class OptionalBloodTypeKeyMixin(BaseModel):
    blood_type: Optional[BloodType] = Field(
        None, description="Single Blood Type. (Optional)"
    )


class ListOfBloodTypeKeysMixinMixin(BaseModel):
    blood_types: List[BloodType] = Field(..., description="Multiple Blood Types")


class OptionalListOfBloodTypeKeysMixin(BaseModel):
    blood_types: Optional[List[BloodType]] = Field(
        None, description="Multiple Blood Types. (Optional)"
    )


class BasicBloodTypeDataSchema(
    BloodTypeDataDTO,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardBloodTypeDataSchema(
    BloodTypeDataDTO,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullBloodTypeDataSchema(
    BloodTypeDataDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


BloodTypeDetailsT = TypeVar(
    "BloodTypeDetailsT",
    BasicBloodTypeDataSchema,
    StandardBloodTypeDataSchema,
    FullBloodTypeDataSchema,
)


class BloodTypeDetailsMixin(BaseModel, Generic[BloodTypeDetailsT]):
    blood_type_details: BloodTypeDetailsT = Field(
        ..., description="Single Blood Type Data"
    )


class OptionalBloodTypeDetailsMixin(BaseModel, Generic[BloodTypeDetailsT]):
    blood_type_details: Optional[BloodTypeDetailsT] = Field(
        None, description="Single Blood Type Data. (Optional)"
    )


class ListOfBloodTypeDetailsMixin(BaseModel, Generic[BloodTypeDetailsT]):
    blood_types_details: List[BloodTypeDetailsT] = Field(
        ..., description="Multiple Blood Types Data"
    )


class OptionalListOfBloodTypeDetailsMixin(BaseModel, Generic[BloodTypeDetailsT]):
    blood_types_details: Optional[List[BloodTypeDetailsT]] = Field(
        None, description="Multiple Blood Types Data. (Optional)"
    )
