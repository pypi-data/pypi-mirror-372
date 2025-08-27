from maleo.soma.mixins.general import OrganizationId, UserId
from maleo.soma.mixins.parameter import OptionalListOfDataStatuses, UseCache
from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo.identity.mixins.user_organization import Include


class ReadSingleQueryParameter(Include, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Include, UseCache, OptionalListOfDataStatuses, OrganizationId, UserId
):
    pass


class CreateParameter(Include, UserId, OrganizationId):
    pass
