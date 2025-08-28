###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.api.api_resources.api_resource import (
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource
)
from everysk.api import utils

###############################################################################
#   Worker Execution Implementation
###############################################################################
class WorkerExecution(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource
):

    @classmethod
    def retrieve(cls, **kwargs):
        """
        Retrieves details of a single worker execution or a list of worker executions based on the provided arguments.
        This class method sends a GET request to the API to retrieve a worker execution.

        Args:
            worker_execution_id (str, optional):
                The ID of the worker execution to retrieve. If specified, the method
                returns details for this specific worker execution. If omitted, the
                method may return a list of worker executions based on other filters.

            workflow_execution_id (str, optional):
                The ID of the workflow execution to fetch the worker executions for.
                This argument is considered only if 'worker_execution_id' is not provided.

            with_result (bool, optional):
                Indicates whether to include detailed results in the response. The default
                behavior depends on the context of the request (detailed for a single execution,
                summary for a list).

        Returns:
            WorkerExecution: An instance of the WorkerExecution class

        Example:
            # Retrieve details for a specific worker execution
            >>> worker_execution = WorkerExecution.retrieve(worker_execution_id='12345')

            # Retrieve a list of worker executions for a specific workflow execution
            >>> worker_executions = WorkerExecution.retrieve(workflow_execution_id='67890')
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'/workflows{cls.class_url()}'
        response = api_req.get(url, kwargs)
        return utils.to_object(WorkerExecution, kwargs, response)
