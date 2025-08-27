from maleo.soma.mixins.general import UserId
from maleo.soma.mixins.parameter import OptionalListOfDataStatuses, UseCache
from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo.metadata.schemas.data.system_role import SimpleSystemRoleMixin
from maleo.identity.mixins.user_system_role import Include


class ReadSingleQueryParameter(
    Include,
    ReadSingleQueryParameterSchema,
):
    pass


class ReadSingleParameter(
    Include,
    UseCache,
    OptionalListOfDataStatuses,
    SimpleSystemRoleMixin,
    UserId,
):
    pass


class CreateParameter(
    Include,
    SimpleSystemRoleMixin,
    UserId,
):
    pass
