"""
    QApp Platform Project job_fetching_handler.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.handler.handler import Handler
from quapp_common.config.logging_config import logger

from ..component.backend.qiskit_job_fetching import QiskitJobFetching


class JobFetchingHandler(Handler):
    def __init__(self,
                 request_data: dict,
                 post_processing_fn):
        super().__init__(request_data, post_processing_fn)

    def handle(self):
        logger.info("[JobFetchingHandler] handle()")

        request = JobFetchingRequest(self.request_data)

        job_fetching = QiskitJobFetching(request)

        fetching_result = job_fetching.fetch(post_processing_fn=self.post_processing_fn)

        return fetching_result
