from typing import List, Literal, Optional, overload
from uuid import UUID
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.enums.field import ExcludableField
from maleo.soma.mixins.general import OptionalOrder
from maleo.soma.mixins.parameter import IdentifierTypeValue as IdentifierTypeValueMixin
from maleo.soma.schemas.parameter.general import (
    ReadSingleQueryParameterSchema,
    ReadSingleParameterSchema,
    StatusUpdateQueryParameterSchema,
)
from maleo.soma.types.base import ListOfDataStatuses
from maleo.metadata.enums.blood_type import IdentifierType
from maleo.metadata.mixins.blood_type import Name, OptionalName, Exclude
from maleo.metadata.types.base.blood_type import IdentifierValueType


class CommonQueryParameter(Exclude):
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
    OptionalOrder,
):
    pass


class FullDataUpdateParameter(
    CommonQueryParameter,
    FullDataUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class PartialDataUpdateBody(
    OptionalName,
    OptionalOrder,
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
