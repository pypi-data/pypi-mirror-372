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
    DeletableAPIResource,
    CreateableAPIResource,
    UpdateableAPIResource
)
from everysk.api.api_resources.workflow_execution import WorkflowExecution
from everysk.api import utils

###############################################################################
#   Workflow Implementation
###############################################################################
class Workflow(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    CreateableAPIResource,
    UpdateableAPIResource
):

    @classmethod
    def run(cls, id, **kwargs):
        """
        Executes a workflow based on the provided ID, and any additional keyword arguments provided.
        This method constructs an API request to trigger the execution of a specific workflow. It uses the
        `create_api_requestor` function to establish API communication, constructs the appropriate URL,
        and sends a POST request to initiate the workflow execution.

        Args:
            id (str):
                The identifier of the workflow to be executed.

            **kwargs:
                Additional keyword arguments passed for the API request customization.

        Returns:
            WorkflowExecution: An instance of WorkflowExecution

        Example:
            >>> from everysk.api.api_resources.workflow import Workflow
            >>> response = Workflow.run('12345', param1='value1', param2='value2')
            >>> print(response)
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'{cls.class_url()}/{id}/run'
        response = api_req.post(url, kwargs)
        extra_keys = None

        if kwargs.get('synchronous', None):
            extra_keys = ['result']
        return utils.to_object(WorkflowExecution, kwargs, response, extra_keys=extra_keys)
