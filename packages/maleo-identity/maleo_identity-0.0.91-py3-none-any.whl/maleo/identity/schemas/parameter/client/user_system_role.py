from maleo.soma.mixins.general import UserId
from maleo.soma.mixins.parameter import OptionalListOfUserIds
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.metadata.schemas.data.system_role import OptionalListOfSimpleSystemRolesMixin
from maleo.identity.mixins.user_system_role import Include


class ReadMultipleFromUserParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfSimpleSystemRolesMixin,
    UserId,
):
    pass


class ReadMultipleParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfSimpleSystemRolesMixin,
    OptionalListOfUserIds,
):
    pass


class ReadMultipleFromUserQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfSimpleSystemRolesMixin,
):
    pass


class ReadMultipleQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfSimpleSystemRolesMixin,
    OptionalListOfUserIds,
):
    pass
