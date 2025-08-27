from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
)
from maleo.metadata.schemas.data.blood_type import OptionalListOfSimpleBloodTypesMixin
from maleo.metadata.schemas.data.gender import OptionalListOfSimpleGendersMixin
from maleo.metadata.schemas.data.user_type import OptionalListOfSimpleUserTypesMixin
from maleo.identity.mixins.user import (
    OptionalListOfUsernames,
    OptionalListOfEmails,
    OptionalListOfPhones,
    Include,
)


class ReadMultipleQueryParameter(
    Include,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfSimpleBloodTypesMixin,
    OptionalListOfSimpleGendersMixin,
    OptionalListOfPhones,
    OptionalListOfEmails,
    OptionalListOfUsernames,
    OptionalListOfSimpleUserTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleParameter(
    Include,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfSimpleBloodTypesMixin,
    OptionalListOfSimpleGendersMixin,
    OptionalListOfPhones,
    OptionalListOfEmails,
    OptionalListOfUsernames,
    OptionalListOfSimpleUserTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
