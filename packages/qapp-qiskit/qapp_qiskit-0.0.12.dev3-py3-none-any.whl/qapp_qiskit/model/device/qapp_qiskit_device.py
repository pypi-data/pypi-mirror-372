"""
    QApp Platform Project qapp_qiskit_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qiskit import transpile

from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.model.provider.provider import Provider
from quapp_common.config.logging_config import logger

from .qiskit_device import QiskitDevice


class QappQiskitDevice(QiskitDevice):
    def __init__(self, provider: Provider,
                 device_specification: str):
        super().__init__(provider, device_specification)

    def _create_job(self, circuit, options: CircuitRunningOption):
        logger.debug('[QappQiskitDevice] _create_job() with {0} shots'.format(options.shots))

        self.device.set_options(device=options.processing_unit.value,
                                shots=options.shots,
                                executor=options.executor,
                                max_job_size=options.max_job_size)
        transpiled_circuit = transpile(circuits=circuit, backend=self.device)

        return self.device.run(transpiled_circuit)

    def _is_simulator(self) -> bool:
        logger.debug('[QappQiskitDevice] _is_simulator()')

        return True
