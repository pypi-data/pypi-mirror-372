"""
    QApp Platform Project ibm_quantum_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qiskit import transpile

from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.config.logging_config import logger

from .qiskit_device import QiskitDevice


class IbmQuantumDevice(QiskitDevice):

    def _is_simulator(self) -> bool:
        logger.debug('[IbmQuantumDevice] _is_simulator()')

        return self.device.configuration().simulator

    def _create_job(self, circuit, options: CircuitRunningOption):
        logger.debug('[IbmQuantumDevice] _create_job() with {0} shots'.format(options.shots))

        transpile_circuit = transpile(circuit, self.device)

        return self.device.run(transpile_circuit, shots=options.shots)
