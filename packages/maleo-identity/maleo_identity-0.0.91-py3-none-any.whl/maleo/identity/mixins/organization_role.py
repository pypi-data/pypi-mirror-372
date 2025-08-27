from pydantic import BaseModel, Field
from maleo.soma.mixins.parameter import Include as BaseInclude
from maleo.identity.enums.organization_role import IncludableField


class Include(BaseInclude[IncludableField]):
    pass


class Key(BaseModel):
    key: str = Field(..., max_length=50, description="Organization role's key")


class Name(BaseModel):
    name: str = Field(..., max_length=50, description="Organization role's name")
