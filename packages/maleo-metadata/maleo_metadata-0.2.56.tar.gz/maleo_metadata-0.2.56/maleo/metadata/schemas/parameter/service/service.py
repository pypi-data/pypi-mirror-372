from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.metadata.mixins.service import Include, Exclude


class ReadMultipleQueryParameter(
    Include,
    Exclude,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleParameter(
    Include,
    Exclude,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
