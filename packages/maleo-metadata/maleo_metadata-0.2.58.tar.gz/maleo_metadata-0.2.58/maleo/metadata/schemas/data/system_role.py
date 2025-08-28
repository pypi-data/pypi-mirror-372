from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.soma.mixins.data import (
    DataIdentifier,
    DataStatus,
    DataLifecycleTimestamp,
    DataTimestamp,
)
from maleo.metadata.dtos.data.system_role import SystemRoleDataDTO
from maleo.metadata.enums.system_role import SystemRole


class SystemRoleKeyMixin(BaseModel):
    system_role: SystemRole = Field(..., description="Single System Role")


class OptionalSystemRoleKeyMixin(BaseModel):
    system_role: Optional[SystemRole] = Field(
        None, description="Single System Role. (Optional)"
    )


class ListOfSystemRoleKeysMixinMixin(BaseModel):
    system_roles: List[SystemRole] = Field(..., description="Multiple System Roles")


class OptionalListOfSystemRoleKeysMixin(BaseModel):
    system_roles: Optional[List[SystemRole]] = Field(
        None, description="Multiple System Roles. (Optional)"
    )


class BasicSystemRoleDataSchema(
    SystemRoleDataDTO,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardSystemRoleDataSchema(
    SystemRoleDataDTO,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullSystemRoleDataSchema(
    SystemRoleDataDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


SystemRoleDetailsT = TypeVar(
    "SystemRoleDetailsT",
    BasicSystemRoleDataSchema,
    StandardSystemRoleDataSchema,
    FullSystemRoleDataSchema,
)


class SystemRoleDetailsMixin(BaseModel, Generic[SystemRoleDetailsT]):
    system_role_details: SystemRoleDetailsT = Field(
        ..., description="Single System Role Data"
    )


class OptionalSystemRoleDetailsMixin(BaseModel, Generic[SystemRoleDetailsT]):
    system_role_details: Optional[SystemRoleDetailsT] = Field(
        None, description="Single System Role Data. (Optional)"
    )


class ListOfSystemRoleDetailsMixin(BaseModel, Generic[SystemRoleDetailsT]):
    system_roles_details: List[SystemRoleDetailsT] = Field(
        ..., description="Multiple System Roles Data"
    )


class OptionalListOfSystemRoleDetailsMixin(BaseModel, Generic[SystemRoleDetailsT]):
    system_roles_details: Optional[List[SystemRoleDetailsT]] = Field(
        None, description="Multiple System Roles Data. (Optional)"
    )
