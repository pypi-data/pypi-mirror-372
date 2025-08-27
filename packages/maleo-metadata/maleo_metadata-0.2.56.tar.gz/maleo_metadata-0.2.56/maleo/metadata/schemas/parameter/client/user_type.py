from typing import List, Optional
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.enums.field import ExcludableField
from maleo.soma.enums.sort import SortOrder
from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo.soma.schemas.filter import DateFilter
from maleo.soma.schemas.parameter.client import (
    ReadUnpaginatedMultipleParameterSchema,
    ReadUnpaginatedMultipleQueryParameterSchema,
)
from maleo.soma.schemas.sort import SortColumn
from maleo.soma.types.base import (
    ListOfDataStatuses,
    OptionalInteger,
    OptionalListOfIntegers,
    OptionalListOfUUIDs,
    OptionalListOfStrings,
    OptionalString,
)
from maleo.metadata.mixins.user_type import Exclude


class ReadMultipleParameter(
    Exclude,
    ReadUnpaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    @classmethod
    def new(
        cls,
        ids: OptionalListOfIntegers = None,
        uuids: OptionalListOfUUIDs = None,
        keys: OptionalListOfStrings = None,
        names: OptionalListOfStrings = None,
        date_filters: List[DateFilter] = [],
        statuses: ListOfDataStatuses = ALL_STATUSES,
        search: OptionalString = None,
        sort_columns: List[SortColumn] = [SortColumn(name="id", order=SortOrder.ASC)],
        page: int = 1,
        limit: OptionalInteger = None,
        use_cache: bool = True,
        exclude: Optional[List[ExcludableField]] = None,
    ) -> "ReadMultipleParameter":
        return cls(
            ids=ids,
            uuids=uuids,
            keys=keys,
            names=names,
            date_filters=date_filters,
            statuses=statuses,
            search=search,
            sort_columns=sort_columns,
            page=page,
            limit=limit,
            use_cache=use_cache,
            exclude=exclude,
        )


class ReadMultipleQueryParameter(
    Exclude,
    ReadUnpaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
