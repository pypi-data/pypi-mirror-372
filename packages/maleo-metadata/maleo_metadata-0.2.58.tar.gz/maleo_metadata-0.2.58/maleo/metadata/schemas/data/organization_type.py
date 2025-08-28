from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.soma.mixins.data import (
    DataIdentifier,
    DataStatus,
    DataLifecycleTimestamp,
    DataTimestamp,
)
from maleo.metadata.dtos.data.organization_type import OrganizationTypeDataDTO
from maleo.metadata.enums.organization_type import OrganizationType


class OrganizationTypeKeyMixin(BaseModel):
    organization_type: OrganizationType = Field(
        ..., description="Single Organization Type"
    )


class OptionalOrganizationTypeKeyMixin(BaseModel):
    organization_type: Optional[OrganizationType] = Field(
        None, description="Single Organization Type. (Optional)"
    )


class ListOfOrganizationTypeKeysMixinMixin(BaseModel):
    organization_types: List[OrganizationType] = Field(
        ..., description="Multiple Organization Types"
    )


class OptionalListOfOrganizationTypeKeysMixin(BaseModel):
    organization_types: Optional[List[OrganizationType]] = Field(
        None, description="Multiple Organization Types. (Optional)"
    )


class BasicOrganizationTypeDataSchema(
    OrganizationTypeDataDTO,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardOrganizationTypeDataSchema(
    OrganizationTypeDataDTO,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullOrganizationTypeDataSchema(
    OrganizationTypeDataDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


OrganizationTypeDetailsT = TypeVar(
    "OrganizationTypeDetailsT",
    BasicOrganizationTypeDataSchema,
    StandardOrganizationTypeDataSchema,
    FullOrganizationTypeDataSchema,
)


class OrganizationTypeDetailsMixin(BaseModel, Generic[OrganizationTypeDetailsT]):
    organization_type_details: OrganizationTypeDetailsT = Field(
        ..., description="Single Organization Type Data"
    )


class OptionalOrganizationTypeDetailsMixin(
    BaseModel, Generic[OrganizationTypeDetailsT]
):
    organization_type_details: Optional[OrganizationTypeDetailsT] = Field(
        None, description="Single Organization Type Data. (Optional)"
    )


class ListOfOrganizationTypeDetailsMixin(BaseModel, Generic[OrganizationTypeDetailsT]):
    organization_types_details: List[OrganizationTypeDetailsT] = Field(
        ..., description="Multiple Organization Types Data"
    )


class OptionalListOfOrganizationTypeDetailsMixin(
    BaseModel, Generic[OrganizationTypeDetailsT]
):
    organization_types_details: Optional[List[OrganizationTypeDetailsT]] = Field(
        None, description="Multiple Organization Types Data. (Optional)"
    )
