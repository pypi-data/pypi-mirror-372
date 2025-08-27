"""
    QApp Platform Project qiskit_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC
from qiskit import QiskitError

from quapp_common.model.device.device import Device
from quapp_common.config.logging_config import logger


class QiskitDevice(Device, ABC):

    def _produce_histogram_data(self, job_result) -> dict | None:
        logger.info('[QiskitDevice] _produce_histogram_data()')

        try:
            histogram_data = job_result.get_counts()
        except QiskitError as qiskit_error:
            logger.debug("[QiskitDevice] Can't produce histogram with error: {0}".format(str(qiskit_error)))
            histogram_data = None

        return histogram_data

    def _get_provider_job_id(self, job) -> str:
        logger.debug('[QiskitDevice] Get provider job id')

        return job.job_id()

    def _get_job_status(self, job) -> str:
        logger.debug('[QiskitDevice] Get job status')

        return job.status().name

    def _calculate_execution_time(self, job_result):
        logger.debug('[QiskitDevice] Calculate execution time')

        if "metadata" not in job_result:
            return None

        metadata = job_result["metadata"]

        if metadata is None or not bool(metadata) or "time_taken_execute" not in metadata:
            return None

        self.execution_time = metadata["time_taken_execute"]

        logger.debug('[QiskitDevice] Execution time calculation was: {0} seconds'
                     .format(self.execution_time))

    def _get_job_result(self, job):
        logger.debug('[QiskitDevice] _get_job_result()')

        return job.result()
