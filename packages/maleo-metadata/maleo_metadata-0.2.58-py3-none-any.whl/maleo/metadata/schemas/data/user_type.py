from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.soma.mixins.data import (
    DataIdentifier,
    DataStatus,
    DataLifecycleTimestamp,
    DataTimestamp,
)
from maleo.metadata.dtos.data.user_type import UserTypeDataDTO
from maleo.metadata.enums.user_type import UserType


class UserTypeKeyMixin(BaseModel):
    user_type: UserType = Field(..., description="Single User Type")


class OptionalUserTypeKeyMixin(BaseModel):
    user_type: Optional[UserType] = Field(
        None, description="Single User Type. (Optional)"
    )


class ListOfUserTypeKeysMixinMixin(BaseModel):
    user_types: List[UserType] = Field(..., description="Multiple User Types")


class OptionalListOfUserTypeKeysMixin(BaseModel):
    user_types: Optional[List[UserType]] = Field(
        None, description="Multiple User Types. (Optional)"
    )


class BasicUserTypeDataSchema(
    UserTypeDataDTO,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardUserTypeDataSchema(
    UserTypeDataDTO,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullUserTypeDataSchema(
    UserTypeDataDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


UserTypeDetailsT = TypeVar(
    "UserTypeDetailsT",
    BasicUserTypeDataSchema,
    StandardUserTypeDataSchema,
    FullUserTypeDataSchema,
)


class UserTypeDetailsMixin(BaseModel, Generic[UserTypeDetailsT]):
    user_type_details: UserTypeDetailsT = Field(
        ..., description="Single User Type Data"
    )


class OptionalUserTypeDetailsMixin(BaseModel, Generic[UserTypeDetailsT]):
    user_type_details: Optional[UserTypeDetailsT] = Field(
        None, description="Single User Type Data. (Optional)"
    )


class ListOfUserTypeDetailsMixin(BaseModel, Generic[UserTypeDetailsT]):
    user_types_details: List[UserTypeDetailsT] = Field(
        ..., description="Multiple User Types Data"
    )


class OptionalListOfUserTypeDetailsMixin(BaseModel, Generic[UserTypeDetailsT]):
    user_types_details: Optional[List[UserTypeDetailsT]] = Field(
        None, description="Multiple User Types Data. (Optional)"
    )
