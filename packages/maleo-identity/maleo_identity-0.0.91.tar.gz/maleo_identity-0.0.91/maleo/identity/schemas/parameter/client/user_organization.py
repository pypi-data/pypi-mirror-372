from maleo.soma.mixins.general import OrganizationId, UserId
from maleo.soma.mixins.parameter import (
    OptionalListOfOrganizationIds,
    OptionalListOfUserIds,
)
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.identity.mixins.user_organization import Include


class ReadMultipleFromUserParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfOrganizationIds,
    UserId,
):
    pass


class ReadMultipleFromOrganizationParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfUserIds,
    OrganizationId,
):
    pass


class ReadMultipleParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleFromUserQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleFromOrganizationQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfUserIds,
):
    pass


class ReadMultipleQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass
