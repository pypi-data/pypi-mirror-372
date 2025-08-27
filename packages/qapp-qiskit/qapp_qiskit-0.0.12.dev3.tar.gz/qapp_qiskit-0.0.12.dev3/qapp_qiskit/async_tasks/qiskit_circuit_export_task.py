"""
    QApp Platform Project qiskit_circuit_export_task.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qiskit import transpile

from quapp_common.async_tasks.export_circuit_task import CircuitExportTask
from quapp_common.config.logging_config import logger
from quapp_common.enum.sdk import Sdk

from ..factory.qiskit_provider_factory import QiskitProviderFactory
from ..model.provider.oqc_cloud_provider import OqcCloudProvider


class QiskitCircuitExportTask(CircuitExportTask):

    def _transpile_circuit(self):
        logger.debug("[QiskitCircuitExportTask] _transpile_circuit()")

        circuit = self.circuit_data_holder.circuit
        backend_information = self.backend_data_holder.backend_information

        provider = QiskitProviderFactory.create_provider(
            sdk=Sdk.QISKIT,
            provider_type=backend_information.provider_tag,
            authentication=backend_information.authentication)

        if isinstance(provider, OqcCloudProvider):
            return circuit

        backend = provider.get_backend(backend_information.device_name)

        return transpile(circuits=circuit, backend=backend)
