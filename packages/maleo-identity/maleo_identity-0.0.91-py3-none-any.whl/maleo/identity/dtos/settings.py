from pydantic import model_validator
from typing import Self
from maleo.soma.dtos.settings import Settings as BaseSettings
from maleo.soma.enums.service import ServiceKey, ServiceName


class Settings(BaseSettings):
    @model_validator(mode="after")
    def validate_service_key_name(self) -> Self:
        assert (
            self.SERVICE_KEY is ServiceKey.IDENTITY
        ), f"'SERVICE_KEY' must be '{ServiceKey.IDENTITY}'"
        assert (
            self.SERVICE_NAME is ServiceName.IDENTITY
        ), f"'SERVICE_NAME' must be '{ServiceName.IDENTITY}'"

        return self
