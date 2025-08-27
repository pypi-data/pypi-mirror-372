from typing import List
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.enums.pagination import Limit
from maleo.soma.enums.sort import SortOrder
from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo.soma.schemas.filter import DateFilter
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.soma.schemas.sort import SortColumn
from maleo.soma.types.base import (
    ListOfDataStatuses,
    OptionalListOfIntegers,
    OptionalListOfUUIDs,
    OptionalListOfStrings,
    OptionalString,
)


class ReadMultipleParameter(
    ReadPaginatedMultipleParameterSchema,
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
        limit: Limit = Limit.LIM_10,
        use_cache: bool = True,
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
        )


class ReadMultipleQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
