from maleo.soma.mixins.general import OrganizationId
from maleo.soma.mixins.parameter import (
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
)
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.identity.mixins.organization_role import Include


class ReadMultipleFromOrganizationParameter(
    Include, ReadPaginatedMultipleParameterSchema, OptionalListOfKeys, OrganizationId
):
    pass


class ReadMultipleParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleFromOrganizationQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
):
    pass


class ReadMultipleQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
):
    pass
