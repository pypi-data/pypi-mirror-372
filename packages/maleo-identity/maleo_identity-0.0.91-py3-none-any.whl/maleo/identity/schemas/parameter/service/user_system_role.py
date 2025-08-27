from maleo.soma.mixins.parameter import OptionalListOfUserIds
from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.metadata.schemas.data.system_role import OptionalSimpleSystemRoleMixin
from maleo.identity.mixins.user_system_role import Include


class ReadMultipleFromuserQueryParameter(
    Include, ReadPaginatedMultipleQueryParameterSchema, OptionalSimpleSystemRoleMixin
):
    pass


class ReadMultipleQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalSimpleSystemRoleMixin,
    OptionalListOfUserIds,
):
    pass


class ReadMultipleParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalSimpleSystemRoleMixin,
    OptionalListOfUserIds,
):
    pass
