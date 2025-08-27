from typing import Dict, List
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.organization import (
    IncludableField as OrganizationIncludableField,
)
from maleo.identity.enums.organization_role import (
    IncludableField as OrganizationRoleIncludableField,
)

EXPANDABLE_FIELDS_DEPENDENCIES_MAP: Dict[
    OrganizationRoleIncludableField, List[OrganizationRoleIncludableField]
] = {
    OrganizationRoleIncludableField.ORGANIZATION: [
        OrganizationRoleIncludableField.ORGANIZATION_TYPE,
        OrganizationRoleIncludableField.REGISTRATION_CODE,
    ]
}

ORGANIZATION_EXPANDABLE_FIELDS_MAP: Dict[
    OrganizationRoleIncludableField, OrganizationIncludableField
] = {
    OrganizationRoleIncludableField.ORGANIZATION_TYPE: OrganizationIncludableField.ORGANIZATION_TYPE,
    OrganizationRoleIncludableField.REGISTRATION_CODE: OrganizationIncludableField.REGISTRATION_CODE,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organization_roles",
            name="Organization Roles",
            url_slug="organization-roles",
        )
    ],
    details=None,
)
