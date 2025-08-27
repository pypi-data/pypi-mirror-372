from enum import StrEnum


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    USER_ID = "user_id"
    ID_CARD = "id_card"


class ValidImageMimeType(StrEnum):
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    PNG = "image/png"


class IncludableField(StrEnum):
    GENDER = "gender_details"
    BLOOD_TYPE = "blood_type_details"
