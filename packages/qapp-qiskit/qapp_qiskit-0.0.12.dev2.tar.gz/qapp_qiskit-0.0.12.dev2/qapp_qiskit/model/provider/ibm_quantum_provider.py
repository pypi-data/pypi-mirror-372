"""
    QApp Platform Project ibm_quantum_provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qiskit_ibm_provider import IBMProvider

from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider
from quapp_common.config.logging_config import logger


class IbmQuantumProvider(Provider):

    def __init__(self, api_token):
        super().__init__(ProviderTag.IBM_QUANTUM)
        self.api_token = api_token

    def get_backend(self, device_specification: str):
        logger.debug('[IbmQuantumProvider] get_backend()')

        provider = self.collect_provider()

        return provider.get_backend(device_specification)

    def collect_provider(self):
        logger.debug('[IbmQuantumProvider] collect_provider()')

        return IBMProvider(token=self.api_token)
