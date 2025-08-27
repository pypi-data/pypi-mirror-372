"""
    QApp Platform Project qiskit_provider_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.provider_factory import ProviderFactory
from quapp_common.config.logging_config import logger

from ..model.provider.oqc_cloud_provider import OqcCloudProvider
from ..model.provider.qapp_qiskit_provider import QappQiskitProvider
from ..model.provider.ibm_quantum_provider import IbmQuantumProvider
from ..model.provider.ibm_cloud_provider import IbmCloudProvider


class QiskitProviderFactory(ProviderFactory):

    @staticmethod
    def create_provider(provider_type: ProviderTag, sdk: Sdk, authentication: dict):
        logger.info("[QiskitProviderFactory] create_provider()")

        if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(provider_type) and Sdk.QISKIT.__eq__(sdk):
            return QappQiskitProvider()

        if ProviderTag.IBM_QUANTUM.__eq__(provider_type):
            return IbmQuantumProvider(authentication.get("token"))

        if ProviderTag.IBM_CLOUD.__eq__(provider_type):
            return IbmCloudProvider(
                authentication.get("token"),
                authentication.get("crn")
            )

        if ProviderTag.OQC_CLOUD.__eq__(provider_type):
            return OqcCloudProvider(
                authentication.get("url"),
                authentication.get("accessToken")
            )

        raise Exception("Unsupported provider!")
