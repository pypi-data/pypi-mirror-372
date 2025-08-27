from maleo.soma.mixins.general import UserId
from maleo.metadata.schemas.data.gender import OptionalSimpleGenderMixin
from maleo.metadata.schemas.data.blood_type import OptionalSimpleBloodTypeMixin
from maleo.identity.mixins.user_profile import (
    IdCard,
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    FullName,
    BirthPlace,
    BirthDate,
    AvatarName,
)


class UserProfileDTO(
    AvatarName,
    OptionalSimpleBloodTypeMixin,
    OptionalSimpleGenderMixin,
    BirthDate,
    BirthPlace,
    FullName,
    EndingTitle,
    LastName,
    MiddleName,
    FirstName,
    LeadingTitle,
    IdCard,
    UserId,
):
    pass
