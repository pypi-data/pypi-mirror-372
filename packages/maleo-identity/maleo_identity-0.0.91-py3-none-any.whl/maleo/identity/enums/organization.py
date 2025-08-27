from enum import StrEnum


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"


class IncludableField(StrEnum):
    ORGANIZATION_TYPE = "organization_type"
    REGISTRATION_CODE = "registration_code"
