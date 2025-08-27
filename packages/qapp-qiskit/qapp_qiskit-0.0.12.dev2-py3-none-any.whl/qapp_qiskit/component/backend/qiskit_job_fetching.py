"""
    QApp Platform Project qiskit_job_fetching.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.component.backend.job_fetching import JobFetching
from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk

from ...factory.qiskit_provider_factory import QiskitProviderFactory


class QiskitJobFetching(JobFetching):

    def __init__(self, request_data: JobFetchingRequest):
        super().__init__(request_data)

    def _collect_provider(self, ):
        logger.info("[QiskitJobFetching] _collect_provider()")

        return QiskitProviderFactory.create_provider(
            provider_type=ProviderTag.IBM_QUANTUM,
            sdk=Sdk.QISKIT,
            authentication=self.provider_authentication).collect_provider()

    def _retrieve_job(self, provider):
        logger.info("[QiskitJobFetching] _retrieve_job()")

        return provider.retrieve_job(job_id=self.provider_job_id)

    def _get_job_status(self, job):
        logger.info("[QiskitJobFetching] _get_job_status()")

        return job.status().name

    def _get_job_result(self, job):
        logger.info("[QiskitJobFetching] _get_job_result()")

        return job.result()
