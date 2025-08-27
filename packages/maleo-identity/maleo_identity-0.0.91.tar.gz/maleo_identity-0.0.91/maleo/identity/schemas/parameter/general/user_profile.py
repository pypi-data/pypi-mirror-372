from typing import List, Literal, Optional, overload
from uuid import UUID
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.mixins.general import UserId
from maleo.soma.mixins.parameter import IdentifierTypeValue as IdentifierTypeValueMixin
from maleo.soma.schemas.parameter.general import (
    ReadSingleQueryParameterSchema,
    ReadSingleParameterSchema,
)
from maleo.soma.types.base import ListOfDataStatuses
from maleo.metadata.schemas.data.blood_type import OptionalSimpleBloodTypeMixin
from maleo.metadata.schemas.data.gender import OptionalSimpleGenderMixin
from maleo.identity.enums.user_profile import IdentifierType, IncludableField
from maleo.identity.mixins.user_profile import (
    Include,
    OptionalIdCard,
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    BirthPlace,
    BirthDate,
    OptionalAvatarName,
    AvatarData,
)
from maleo.identity.types.base.user_profile import IdentifierValueType


class ReadSingleQueryParameter(
    Include,
    ReadSingleQueryParameterSchema,
):
    pass


class ReadSingleParameter(
    Include, ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID, IdentifierType.USER_ID],
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
        identifier: Literal[IdentifierType.ID_CARD],
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


class CreateOrUpdateQuery(Include):
    pass


class CreateOrUpdateBody(
    OptionalAvatarName,
    OptionalSimpleGenderMixin,
    OptionalSimpleBloodTypeMixin,
    BirthDate,
    BirthPlace,
    EndingTitle,
    LastName,
    MiddleName,
    FirstName,
    LeadingTitle,
    OptionalIdCard,
    UserId,
):
    pass


class CreateParameter(AvatarData, CreateOrUpdateBody, CreateOrUpdateQuery):
    pass


class UpdateParameter(
    AvatarData,
    CreateOrUpdateBody,
    CreateOrUpdateQuery,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
