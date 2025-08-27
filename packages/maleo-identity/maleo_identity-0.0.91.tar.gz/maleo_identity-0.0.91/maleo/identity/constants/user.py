from typing import Callable, Dict, List
from uuid import UUID
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.user import IdentifierType, IncludableField
from maleo.identity.types.base.user import IdentifierValueType

IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[..., IdentifierValueType]
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.USERNAME: str,
    IdentifierType.EMAIL: str,
}

EXPANDABLE_FIELDS_DEPENDENCIES_MAP: Dict[IncludableField, List[IncludableField]] = {
    IncludableField.PROFILE: [IncludableField.GENDER, IncludableField.BLOOD_TYPE],
    IncludableField.SYSTEM_ROLES: [IncludableField.SYSTEM_ROLE_DETAILS],
}

RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="users", name="Users", url_slug="users")],
    details=None,
)
