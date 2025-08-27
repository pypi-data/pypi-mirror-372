"""
    QApp Platform Project ibm_cloud_provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.accounts import ChannelType

from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider
from quapp_common.config.logging_config import logger


class IbmCloudProvider(Provider):

    def __init__(self, api_key, crn):
        super().__init__(ProviderTag.IBM_CLOUD)
        self.api_key = api_key
        self.crn = crn
        self.channel: ChannelType = "ibm_cloud"

    def get_backend(self, device_specification: str):
        logger.debug('[IbmCloudProvider] Get backend')

        provider = self.collect_provider()

        return provider.get_backend(name=device_specification)

    def collect_provider(self):
        logger.debug('[IbmCloudProvider] Connect to provider')

        return QiskitRuntimeService(channel=self.channel,
                                    token=self.api_key,
                                    instance=self.crn)
