from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo.soma.schemas.parameter.service import (
    ReadUnpaginatedMultipleQueryParameterSchema,
    ReadUnpaginatedMultipleParameterSchema,
)
from maleo.metadata.mixins.system_role import Exclude


class ReadMultipleQueryParameter(
    Exclude,
    ReadUnpaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleParameter(
    Exclude,
    ReadUnpaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
