from typing import List, Literal, Optional, overload
from uuid import UUID
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.enums.field import ExcludableField
from maleo.soma.mixins.general import OptionalOrder, OptionalParentId
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
)
from maleo.soma.schemas.parameter.general import (
    ReadSingleQueryParameterSchema,
    ReadSingleParameterSchema,
    StatusUpdateQueryParameterSchema,
)
from maleo.soma.types.base import ListOfDataStatuses
from maleo.metadata.dtos.data.medical_role import MedicalRoleDataDTO
from maleo.metadata.enums.medical_role import IdentifierType
from maleo.metadata.mixins.medical_role import (
    Code,
    OptionalCode,
    Name,
    OptionalName,
    Exclude,
)
from maleo.metadata.types.base.medical_role import IdentifierValueType


class CommonQueryParameter(Exclude):
    pass


class CreateBody(MedicalRoleDataDTO):
    pass


class CreateParameter(CommonQueryParameter, CreateBody):
    pass


class ReadSingleQueryParameter(CommonQueryParameter, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    ReadSingleQueryParameter,
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        exclude: Optional[List[ExcludableField]] = None,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        exclude: Optional[List[ExcludableField]] = None,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.KEY, IdentifierType.NAME],
        value: str,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        exclude: Optional[List[ExcludableField]] = None,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        exclude: Optional[List[ExcludableField]] = None,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            value=value,
            statuses=statuses,
            use_cache=use_cache,
            exclude=exclude,
        )


class FullDataUpdateBody(
    Name,
    Code,
    OptionalOrder,
    OptionalParentId,
):
    pass


class FullDataUpdateParameter(
    CommonQueryParameter,
    FullDataUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class PartialDataUpdateBody(
    OptionalName, OptionalCode, OptionalOrder, OptionalParentId
):
    pass


class PartialDataUpdateParameter(
    CommonQueryParameter,
    PartialDataUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class StatusUpdateQueryParameter(
    CommonQueryParameter,
    StatusUpdateQueryParameterSchema,
):
    pass


class StatusUpdateParameter(
    StatusUpdateQueryParameter,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
