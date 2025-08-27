from maleo.soma.mixins.general import OrganizationId, UserId
from maleo.soma.mixins.parameter import OptionalListOfDataStatuses, UseCache
from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo.identity.mixins.organization_role import Key
from maleo.identity.mixins.user_organization_role import Include


class ReadSingleQueryParameter(Include, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Include, UseCache, OptionalListOfDataStatuses, Key, OrganizationId, UserId
):
    pass
