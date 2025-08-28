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
from .worker_execution import WorkerExecution

###############################################################################
#   Workflow Execution Implementation
###############################################################################
class WorkflowExecution(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource
):

    @classmethod
    def retrieve(cls, workflow_id, **kwargs):
        """
        Retrieves a single workflow execution or a paginated list of workflow executions associated with a given workflow ID.
        When a specific workflow execution ID is provided, details for that execution are returned. Without an execution ID,
        the method returns a paginated list of all executions for the workflow.
        If `workflow_execution_id` is not provided, pagination parameters (`page_size` and `page_token`) can be used to
        navigate through a potentially large set of workflow executions.

        Args:
            workflow_id (str):
                The unique identifier of the workflow for which executions are being retrieved.

            workflow_execution_id (str, optional):
                The specific workflow execution ID to retrieve. If provided, the method
                returns information for this execution only.

            page_size (int, optional):
                The number of items to return in a single page (applicable when retrieving a list
                of workflow executions).

            page_token (str, optional):
                The token for the next page of results (applicable when retrieving a list of
                workflow executions).

        Returns:
            WorkflowExecution or list: If a `workflow_execution_id` is provided, returns a `WorkflowExecution` object for that ID.
            Otherwise, returns a list of `WorkflowExecution` objects for the specified workflow ID,
            potentially paginated.
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'/workflows/{workflow_id}{cls.class_url()}'
        response = api_req.get(url, kwargs)
        return utils.to_object(WorkflowExecution, kwargs, response)

    @classmethod
    def syncronous_retrieve(cls, workflow_id, **kwargs):
        """
        Retrieves a workflow execution synchronously.
        This class method retrieves a workflow execution synchronously, continuously polling the API until the execution is completed.

        Args:
            workflow_id (str):
                The unique identifier of the workflow for which the execution is being retrieved.

            **kwargs:
                Additional keyword arguments passed to the `retrieve` method. These can include parameters like
                `workflow_execution_id` to specify the exact execution to poll, or pagination parameters (`page_size`,
                `page_token`) when expecting a list of executions.

        Returns:
            An instance of `WorkerExecution` containing the details of the ender worker execution of the completed workflow, including execution results.
        """
        workflow_execution = None
        status = None

        while status != 'COMPLETED':
            workflow_execution = cls.retrieve(workflow_id, **kwargs)
            status = workflow_execution['status']
            utils.sleep(1)

        worker_execution_id = workflow_execution['ender_worker_execution_id']
        return WorkerExecution.retrieve(worker_execution_id=worker_execution_id, with_result=True)
