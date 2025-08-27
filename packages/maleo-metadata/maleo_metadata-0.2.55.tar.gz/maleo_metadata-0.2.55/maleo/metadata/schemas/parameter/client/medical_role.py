from typing import List, Optional
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.enums.field import ExcludableField
from maleo.soma.enums.pagination import Limit
from maleo.soma.enums.sort import SortOrder
from maleo.soma.mixins.general import IsRoot, IsParent, IsChild, IsLeaf
from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfCodes,
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
    OptionalBoolean,
    OptionalListOfIntegers,
    OptionalListOfUUIDs,
    OptionalListOfStrings,
    OptionalString,
)
from maleo.metadata.mixins.medical_role import MedicalRoleId, Exclude


class ReadMultipleParameter(
    Exclude,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    @classmethod
    def new(
        cls,
        ids: OptionalListOfIntegers = None,
        uuids: OptionalListOfUUIDs = None,
        parent_ids: OptionalListOfIntegers = None,
        is_root: OptionalBoolean = None,
        is_parent: OptionalBoolean = None,
        is_child: OptionalBoolean = None,
        is_leaf: OptionalBoolean = None,
        codes: OptionalListOfStrings = None,
        keys: OptionalListOfStrings = None,
        names: OptionalListOfStrings = None,
        date_filters: List[DateFilter] = [],
        statuses: ListOfDataStatuses = ALL_STATUSES,
        search: OptionalString = None,
        sort_columns: List[SortColumn] = [SortColumn(name="id", order=SortOrder.ASC)],
        page: int = 1,
        limit: Limit = Limit.LIM_10,
        use_cache: bool = True,
        exclude: Optional[List[ExcludableField]] = None,
    ) -> "ReadMultipleParameter":
        return cls(
            ids=ids,
            uuids=uuids,
            parent_ids=parent_ids,
            is_root=is_root,
            is_parent=is_parent,
            is_child=is_child,
            is_leaf=is_leaf,
            codes=codes,
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


class ReadMultipleSpecializationsParameter(
    Exclude,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    OptionalListOfUuids,
    OptionalListOfIds,
    MedicalRoleId,
):
    @classmethod
    def new(
        cls,
        medical_role_id: int,
        ids: OptionalListOfIntegers = None,
        uuids: OptionalListOfUUIDs = None,
        codes: OptionalListOfStrings = None,
        keys: OptionalListOfStrings = None,
        names: OptionalListOfStrings = None,
        date_filters: List[DateFilter] = [],
        statuses: ListOfDataStatuses = ALL_STATUSES,
        search: OptionalString = None,
        sort_columns: List[SortColumn] = [SortColumn(name="id", order=SortOrder.ASC)],
        page: int = 1,
        limit: Limit = Limit.LIM_10,
        use_cache: bool = True,
        exclude: Optional[List[ExcludableField]] = None,
    ) -> "ReadMultipleSpecializationsParameter":
        return cls(
            medical_role_id=medical_role_id,
            ids=ids,
            uuids=uuids,
            codes=codes,
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
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleSpecializationsQueryParameter(
    Exclude,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
