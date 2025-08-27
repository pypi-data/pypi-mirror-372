from typing import Dict, List
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.user_system_role import IncludableField

EXPANDABLE_FIELDS_DEPENDENCIES_MAP: Dict[IncludableField, List[IncludableField]] = {}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_system_roles",
            name="User System Roles",
            url_slug="user-system-roles",
        )
    ],
    details=None,
)
