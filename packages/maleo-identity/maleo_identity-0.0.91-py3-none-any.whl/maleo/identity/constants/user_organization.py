from typing import Dict, List
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.user import IncludableField as UserIncludableField
from maleo.identity.enums.organization import (
    IncludableField as OrganizationIncludableField,
)
from maleo.identity.enums.user_organization import (
    IncludableField as UserOrganizationIncludableField,
)

EXPANDABLE_FIELDS_DEPENDENCIES_MAP: Dict[
    UserOrganizationIncludableField, List[UserOrganizationIncludableField]
] = {
    UserOrganizationIncludableField.USER: [
        UserOrganizationIncludableField.USER_TYPE,
        UserOrganizationIncludableField.PROFILE,
    ],
    UserOrganizationIncludableField.PROFILE: [
        UserOrganizationIncludableField.BLOOD_TYPE,
        UserOrganizationIncludableField.GENDER,
    ],
    UserOrganizationIncludableField.SYSTEM_ROLES: [
        UserOrganizationIncludableField.SYSTEM_ROLE_DETAILS
    ],
    UserOrganizationIncludableField.ORGANIZATION: [
        UserOrganizationIncludableField.ORGANIZATION_TYPE,
        UserOrganizationIncludableField.REGISTRATION_CODE,
    ],
}

USER_EXPANDABLE_FIELDS_MAP: Dict[
    UserOrganizationIncludableField, UserIncludableField
] = {
    UserOrganizationIncludableField.USER_TYPE: UserIncludableField.USER_TYPE,
    UserOrganizationIncludableField.PROFILE: UserIncludableField.PROFILE,
    UserOrganizationIncludableField.BLOOD_TYPE: UserIncludableField.BLOOD_TYPE,
    UserOrganizationIncludableField.GENDER: UserIncludableField.GENDER,
    UserOrganizationIncludableField.SYSTEM_ROLES: UserIncludableField.SYSTEM_ROLES,
    UserOrganizationIncludableField.SYSTEM_ROLE_DETAILS: UserIncludableField.SYSTEM_ROLE_DETAILS,
}

ORGANIZATION_EXPANDABLE_FIELDS_MAP: Dict[
    UserOrganizationIncludableField, OrganizationIncludableField
] = {
    UserOrganizationIncludableField.ORGANIZATION_TYPE: OrganizationIncludableField.ORGANIZATION_TYPE,
    UserOrganizationIncludableField.REGISTRATION_CODE: OrganizationIncludableField.REGISTRATION_CODE,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_organizations",
            name="User Organizations",
            url_slug="user-organizations",
        )
    ],
    details=None,
)
