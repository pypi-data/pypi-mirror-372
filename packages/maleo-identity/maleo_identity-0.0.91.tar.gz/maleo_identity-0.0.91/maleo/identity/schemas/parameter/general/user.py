from typing import List, Literal, Optional, overload
from uuid import UUID
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.mixins.general import OptionalOrganizationId
from maleo.soma.mixins.parameter import (
    IdentifierType as IdentifierTypeMixin,
    IdentifierValue as IdentifierValueMixin,
)
from maleo.soma.schemas.parameter.general import (
    ReadSingleQueryParameterSchema,
    ReadSingleParameterSchema,
)
from maleo.soma.types.base import ListOfDataStatuses
from maleo.metadata.schemas.data.blood_type import OptionalSimpleBloodTypeMixin
from maleo.metadata.schemas.data.gender import OptionalSimpleGenderMixin
from maleo.metadata.schemas.data.user_type import SimpleUserTypeMixin
from maleo.identity.enums.user import IdentifierType, IncludableField
from maleo.identity.mixins.user import (
    Username,
    Email,
    Phone,
    Password,
    PasswordConfirmation,
    RegistrationCode,
    Include,
)
from maleo.identity.mixins.user_profile import (
    OptionalIdCard,
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    BirthPlace,
    BirthDate,
    OptionalAvatar,
    OptionalAvatarContentType,
    OptionalAvatarName,
)
from maleo.identity.types.base.user import IdentifierValueType


class ReadSingleQueryParameter(Include, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Include, ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        include: Optional[List[IncludableField]] = None,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        include: Optional[List[IncludableField]] = None,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.EMAIL, IdentifierType.USERNAME],
        value: str,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        include: Optional[List[IncludableField]] = None,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        include: Optional[List[IncludableField]] = None,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            value=value,
            statuses=statuses,
            use_cache=use_cache,
            include=include,
        )


class ReadSinglePassword(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class UpdateBody(Phone, Email, Username):
    pass


class UpdateParameter(
    Include,
    UpdateBody,
    IdentifierValueMixin[IdentifierValueType],
    IdentifierTypeMixin[IdentifierType],
):
    pass


class CreateBody(Password, UpdateBody, SimpleUserTypeMixin, OptionalOrganizationId):
    pass


class CreateParameter(
    Include,
    CreateBody,
):
    pass


class RegisterParameter(
    Include,
    OptionalAvatarName,
    OptionalAvatarContentType,
    OptionalAvatar,
    OptionalSimpleBloodTypeMixin,
    OptionalSimpleGenderMixin,
    BirthDate,
    BirthPlace,
    EndingTitle,
    LastName,
    MiddleName,
    FirstName,
    LeadingTitle,
    OptionalIdCard,
    PasswordConfirmation,
    Password,
    Phone,
    Email,
    Username,
    RegistrationCode,
):
    pass
