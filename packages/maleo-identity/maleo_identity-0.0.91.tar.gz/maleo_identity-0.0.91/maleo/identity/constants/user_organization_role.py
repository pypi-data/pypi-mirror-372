from typing import Dict, List
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.user import IncludableField as UserIncludableField
from maleo.identity.enums.organization import (
    IncludableField as OrganizationIncludableField,
)
from maleo.identity.enums.user_organization_role import (
    IncludableField as UserOrganizationRoleIncludableField,
)

EXPANDABLE_FIELDS_DEPENDENCIES_MAP: Dict[
    UserOrganizationRoleIncludableField, List[UserOrganizationRoleIncludableField]
] = {
    UserOrganizationRoleIncludableField.USER: [
        UserOrganizationRoleIncludableField.USER_TYPE,
        UserOrganizationRoleIncludableField.PROFILE,
    ],
    UserOrganizationRoleIncludableField.ORGANIZATION: [
        UserOrganizationRoleIncludableField.ORGANIZATION_TYPE,
        UserOrganizationRoleIncludableField.REGISTRATION_CODE,
    ],
}

USER_EXPANDABLE_FIELDS_MAP: Dict[
    UserOrganizationRoleIncludableField, UserIncludableField
] = {
    UserOrganizationRoleIncludableField.USER_TYPE: UserIncludableField.USER_TYPE,
    UserOrganizationRoleIncludableField.PROFILE: UserIncludableField.PROFILE,
}

ORGANIZATION_EXPANDABLE_FIELDS_MAP: Dict[
    UserOrganizationRoleIncludableField, OrganizationIncludableField
] = {
    UserOrganizationRoleIncludableField.ORGANIZATION_TYPE: OrganizationIncludableField.ORGANIZATION_TYPE,
    UserOrganizationRoleIncludableField.REGISTRATION_CODE: OrganizationIncludableField.REGISTRATION_CODE,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_organization_roles",
            name="UserOrganization Roles",
            url_slug="user-organization-roles",
        )
    ],
    details=None,
)
