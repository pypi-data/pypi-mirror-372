from maleo.soma.mixins.general import IsRoot, IsParent, IsChild, IsLeaf, OrganizationId
from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfKeys,
    OptionalListOfParentIds,
    OptionalListOfUuids,
)
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.metadata.schemas.data.organization_type import (
    OptionalListOfSimpleOrganizationTypesMixin,
)
from maleo.identity.mixins.organization import Include


class ReadMultipleParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfSimpleOrganizationTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleChildrenParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    IsLeaf,
    IsParent,
    OrganizationId,
    OptionalListOfSimpleOrganizationTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfSimpleOrganizationTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleChildrenQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
    IsLeaf,
    IsParent,
    OptionalListOfSimpleOrganizationTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
