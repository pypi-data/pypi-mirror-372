"""
    QApp Platform Project qapp_qiskit_provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qiskit_aer import Aer

from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider
from quapp_common.config.logging_config import logger


class QappQiskitProvider(Provider):

    def __init__(self, ):
        super().__init__(ProviderTag.QUAO_QUANTUM_SIMULATOR)

    def get_backend(self, device_specification):
        logger.debug('[QappQiskitProvider] get_backend()')

        provider = self.collect_provider()

        device_names = set(map(self.__map_aer_backend_name, provider.backends()))

        if device_names.__contains__(device_specification):
            return provider.get_backend(device_specification)

        raise Exception('[QappQiskitProvider] Unsupported device')

    def collect_provider(self):
        logger.debug('[QappQiskitProvider] collect_provider()')

        return Aer

    @staticmethod
    def __map_aer_backend_name(backend):
        return backend.configuration().backend_name
