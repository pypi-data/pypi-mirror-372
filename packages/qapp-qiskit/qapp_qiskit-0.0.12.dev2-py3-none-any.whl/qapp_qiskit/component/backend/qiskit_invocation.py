"""
    QApp Platform Project qiskit_invocation.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qiskit import QuantumCircuit

from quapp_common.component.backend.invocation import Invocation
from quapp_common.data.async_task.circuit_export.backend_holder import BackendDataHolder
from quapp_common.data.async_task.circuit_export.circuit_holder import CircuitDataHolder
from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.model.provider.provider import Provider
from quapp_common.config.logging_config import logger
from quapp_common.config.thread_config import circuit_exporting_pool

from ...factory.qiskit_provider_factory import QiskitProviderFactory
from ...factory.qiskit_device_factory import QiskitDeviceFactory
from ...async_tasks.qiskit_circuit_export_task import QiskitCircuitExportTask


class QiskitInvocation(Invocation):

    def __init__(self, request_data: InvocationRequest):
        super().__init__(request_data)

    def _export_circuit(self, circuit):
        logger.info("[QiskitInvocation] _export_circuit()")

        circuit_export_task = QiskitCircuitExportTask(
            circuit_data_holder=CircuitDataHolder(circuit, self.circuit_export_url),
            backend_data_holder=BackendDataHolder(
                self.backend_information, self.authentication.user_token
            ),
        )

        circuit_exporting_pool.submit(circuit_export_task.do)

    def _create_provider(self):
        logger.info("[QiskitInvocation] _create_provider()")

        return QiskitProviderFactory.create_provider(
            provider_type=self.backend_information.provider_tag,
            sdk=self.sdk,
            authentication=self.backend_information.authentication,
        )

    def _create_device(self, provider: Provider):
        logger.info("[QiskitInvocation] _create_device()")

        return QiskitDeviceFactory.create_device(
            provider=provider,
            device_specification=self.backend_information.device_name,
            authentication=self.backend_information.authentication,
            sdk=self.sdk,
        )

    def _get_qubit_amount(self, circuit):
        if isinstance(circuit, QuantumCircuit):
            return int(circuit.num_qubits)

        raise Exception("Invalid circuit type!")
