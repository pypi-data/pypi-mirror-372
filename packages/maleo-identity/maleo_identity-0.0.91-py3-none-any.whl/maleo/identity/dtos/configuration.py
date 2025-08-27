from maleo.soma.dtos.configurations import ConfigurationDTO as BaseConfigurationDTO
from maleo.soma.dtos.configurations.client.maleo import (
    MaleoMetadataClientConfigurationMixin,
)
from maleo.soma.dtos.configurations.pubsub.publisher import TopicsConfigurationDTO


class MaleoClientsConfiguration(MaleoMetadataClientConfigurationMixin):
    pass


class ConfigurationDTO(
    BaseConfigurationDTO[MaleoClientsConfiguration, TopicsConfigurationDTO, None]
):
    pass
