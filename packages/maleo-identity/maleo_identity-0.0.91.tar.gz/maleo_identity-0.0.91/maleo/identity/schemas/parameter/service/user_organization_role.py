from maleo.soma.mixins.parameter import (
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
    OptionalListOfUserIds,
)
from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.identity.mixins.user_organization_role import Include


class ReadMultipleFromUserOrganizationQueryParameter(
    Include, ReadPaginatedMultipleQueryParameterSchema, OptionalListOfKeys
):
    pass


class ReadMultipleQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass
