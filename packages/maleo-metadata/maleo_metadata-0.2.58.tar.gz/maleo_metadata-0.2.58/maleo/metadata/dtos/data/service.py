from maleo.soma.mixins.general import OptionalOrder
from maleo.metadata.mixins.service import ServiceType, Category, Key, Name, Secret


class ServiceDataDTO(
    Secret,
    Name,
    Key,
    ServiceType,
    Category,
    OptionalOrder,
):
    pass
