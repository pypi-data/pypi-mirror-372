from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.soma.mixins.data import (
    DataIdentifier,
    DataStatus,
    DataLifecycleTimestamp,
    DataTimestamp,
)
from maleo.metadata.dtos.data.service import ServiceDataDTO
from maleo.metadata.enums.service import Service


class ServiceKeyMixin(BaseModel):
    service: Service = Field(..., description="Single Service")


class OptionalServiceKeyMixin(BaseModel):
    service: Optional[Service] = Field(None, description="Single Service. (Optional)")


class ListOfServiceKeysMixinMixin(BaseModel):
    services: List[Service] = Field(..., description="Multiple Services")


class OptionalListOfServiceKeysMixin(BaseModel):
    services: Optional[List[Service]] = Field(
        None, description="Multiple Services. (Optional)"
    )


class BasicServiceDataSchema(
    ServiceDataDTO,
    DataStatus,
    DataIdentifier,
):
    pass


class StandardServiceDataSchema(
    ServiceDataDTO,
    DataStatus,
    DataLifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullServiceDataSchema(
    ServiceDataDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


ServiceDetailsT = TypeVar(
    "ServiceDetailsT",
    BasicServiceDataSchema,
    StandardServiceDataSchema,
    FullServiceDataSchema,
)


class ServiceDetailsMixin(BaseModel, Generic[ServiceDetailsT]):
    service_details: ServiceDetailsT = Field(..., description="Single Service Data")


class OptionalServiceDetailsMixin(BaseModel, Generic[ServiceDetailsT]):
    service_details: Optional[ServiceDetailsT] = Field(
        None, description="Single Service Data. (Optional)"
    )


class ListOfServiceDetailsMixin(BaseModel, Generic[ServiceDetailsT]):
    services_details: List[ServiceDetailsT] = Field(
        ..., description="Multiple Services Data"
    )


class OptionalListOfServiceDetailsMixin(BaseModel, Generic[ServiceDetailsT]):
    services_details: Optional[List[ServiceDetailsT]] = Field(
        None, description="Multiple Services Data. (Optional)"
    )
