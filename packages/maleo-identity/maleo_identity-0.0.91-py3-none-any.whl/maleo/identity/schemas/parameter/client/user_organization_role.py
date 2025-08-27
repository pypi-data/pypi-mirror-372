from maleo.soma.mixins.general import OrganizationId, UserId
from maleo.soma.mixins.parameter import (
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
    OptionalListOfUserIds,
)
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.identity.mixins.user_organization_role import Include


class ReadMultipleFromUserOrganizationParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    UserId,
    OrganizationId,
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


class ReadMultipleFromUserOrganizationQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
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
