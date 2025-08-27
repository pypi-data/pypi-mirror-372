from typing import Literal, overload
from uuid import UUID
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.mixins.general import OptionalOrder
from maleo.soma.mixins.parameter import IdentifierTypeValue as IdentifierTypeValueMixin
from maleo.soma.schemas.parameter.general import (
    ReadSingleParameterSchema,
    StatusUpdateQueryParameterSchema,
)
from maleo.soma.types.base import ListOfDataStatuses
from maleo.metadata.enums.blood_type import IdentifierType
from maleo.metadata.mixins.blood_type import Name, OptionalName
from maleo.metadata.types.base.blood_type import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.KEY, IdentifierType.NAME],
        value: str,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier, value=value, statuses=statuses, use_cache=use_cache
        )


class FullDataUpdateBody(
    Name,
    OptionalOrder,
):
    pass


class FullDataUpdateParameter(
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
    PartialDataUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class StatusUpdateParameter(
    StatusUpdateQueryParameterSchema,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
