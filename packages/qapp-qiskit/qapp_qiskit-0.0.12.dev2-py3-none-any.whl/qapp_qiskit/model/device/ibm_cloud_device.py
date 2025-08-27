"""
    QApp Platform Project ibm_cloud_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qiskit_ibm_runtime import Options, Session, Sampler

from quapp_common.config.logging_config import logger
from quapp_common.data.device.circuit_running_option import CircuitRunningOption

from .qiskit_device import QiskitDevice


class IbmCloudDevice(QiskitDevice):
    def _is_simulator(self) -> bool:
        logger.debug('[IBM Cloud] Get device type')

        return self.device.configuration().simulator

    def _create_job(self, circuit, options: CircuitRunningOption):
        logger.debug('[IBM Cloud] Create job with {0} shots'.format(options.shots))

        running_options = Options(optimization_level=1)
        running_options.execution.shots = options.shots

        with Session(service=self.provider.collect_provider(), backend=self.device) as session:
            sampler = Sampler(session=session, options=running_options)
            job = sampler.run(circuits=circuit)

            return job
