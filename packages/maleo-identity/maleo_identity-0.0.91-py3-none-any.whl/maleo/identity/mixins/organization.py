from pydantic import BaseModel, Field
from maleo.soma.mixins.parameter import Include as BaseInclude
from maleo.identity.enums.organization import IncludableField


class Include(BaseInclude[IncludableField]):
    pass


class Key(BaseModel):
    key: str = Field(..., max_length=255, description="Organization's key")


class Name(BaseModel):
    name: str = Field(..., max_length=255, description="Organization's name")
