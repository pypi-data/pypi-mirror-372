"""
    QApp Platform Project qiskit_handler_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""

from quapp_common.config.logging_config import logger
from quapp_common.factory.handler_factory import HandlerFactory
from quapp_common.handler.handler import Handler

from ..handler.invocation_handler import InvocationHandler
from ..handler.job_fetching_handler import JobFetchingHandler


class QiskitHandlerFactory(HandlerFactory):

    @staticmethod
    def create_handler(event, circuit_preparation_fn, post_processing_fn) -> Handler:
        logger.info("[QiskitHandlerFactory] create_handler()")

        request_data = event.json()
        provider_job_id = request_data.get("providerJobId")

        if provider_job_id is None:
            logger.debug("Create InvocationHandler")
            return InvocationHandler(
                request_data=request_data,
                circuit_preparation_fn=circuit_preparation_fn,
                post_processing_fn=post_processing_fn,
            )

        logger.debug("Create JobFetchingHandler")
        return JobFetchingHandler(
            request_data=request_data, post_processing_fn=post_processing_fn
        )
