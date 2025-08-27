from maleo.soma.mixins.general import OrganizationId
from maleo.soma.mixins.parameter import OptionalListOfDataStatuses, UseCache
from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo.identity.mixins.organization_role import Key, Include


class ReadSingleQueryParameter(Include, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Include, UseCache, OptionalListOfDataStatuses, Key, OrganizationId
):
    pass
