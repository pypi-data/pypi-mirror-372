from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.soma.mixins.data import (
    DataIdentifier,
    DataStatus,
    DataLifecycleTimestamp,
    DataTimestamp,
)
from maleo.metadata.dtos.data.medical_role import MedicalRoleDataDTO
from maleo.metadata.enums.medical_role import MedicalRole


class MedicalRoleKeyMixin(BaseModel):
    medical_role: MedicalRole = Field(..., description="Single Medical Role")


class OptionalMedicalRoleKeyMixin(BaseModel):
    medical_role: Optional[MedicalRole] = Field(
        None, description="Single Medical Role. (Optional)"
    )


class ListOfMedicalRoleKeysMixinMixin(BaseModel):
    medical_roles: List[MedicalRole] = Field(..., description="Multiple Medical Roles")


class OptionalListOfMedicalRoleKeysMixin(BaseModel):
    medical_roles: Optional[List[MedicalRole]] = Field(
        None, description="Multiple Medical Roles. (Optional)"
    )


class BasicMedicalRoleDataSchema(
    MedicalRoleDataDTO,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardMedicalRoleDataSchema(
    MedicalRoleDataDTO,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullMedicalRoleDataSchema(
    MedicalRoleDataDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


MedicalRoleDetailsT = TypeVar(
    "MedicalRoleDetailsT",
    BasicMedicalRoleDataSchema,
    StandardMedicalRoleDataSchema,
    FullMedicalRoleDataSchema,
)


class MedicalRoleDetailsMixin(BaseModel, Generic[MedicalRoleDetailsT]):
    medical_role_details: MedicalRoleDetailsT = Field(
        ..., description="Single Medical Role Data"
    )


class OptionalMedicalRoleDetailsMixin(BaseModel, Generic[MedicalRoleDetailsT]):
    medical_role_details: Optional[MedicalRoleDetailsT] = Field(
        None, description="Single Medical Role Data. (Optional)"
    )


class ListOfMedicalRoleDetailsMixin(BaseModel, Generic[MedicalRoleDetailsT]):
    medical_roles_details: List[MedicalRoleDetailsT] = Field(
        ..., description="Multiple Medical Roles Data"
    )


class OptionalListOfMedicalRoleDetailsMixin(BaseModel, Generic[MedicalRoleDetailsT]):
    medical_roles_details: Optional[List[MedicalRoleDetailsT]] = Field(
        None, description="Multiple Medical Roles Data. (Optional)"
    )
