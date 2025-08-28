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
    UpdateableAPIResource,
    FilterableAPIResource
)
from everysk.api import utils

###############################################################################
#   Datastore Implementation
###############################################################################
class Datastore(
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    CreateableAPIResource,
    UpdateableAPIResource,
    FilterableAPIResource
):
    @classmethod
    def explore(cls, **kwargs):
        """
        Explores the Datastore resource by executing a query with specified parameters to retrieve or manipulate data
        within a given workspace.

        Args:
            user_id (int):
                The ID of the user initiating the request, ensuring that the operation is conducted within
                the user's context and permissions.

            user_role (str):
                The role of the user, which may define the access level and capabilities within the explore operation.

            user_time_zone (str):
                The user's time zone, which can influence how time-based data is retrieved or displayed.

            model (object):
                The model object or identifier specifying the data or views to be explored within the datastore.
                This parameter is mandatory and should start with 'view_' if it's a string object.

            overwrites (object, optional):
                An optional object containing properties to overwrite in the model. This allows
                for dynamic modifications to the model during the exploration.

            workspace (str):
                The workspace identifier within which the exploration is to be conducted. This parameter is mandatory
                and specifies the context or environment for the operation.

        Returns:
            dict: The response from the API request.

        Example:
            >>> response = ClassName.explore(
            >>> ... user_id=12345,
            >>> ... user_role='analyst',
            >>> ... user_time_zone='UTC',
            >>> ... model={'some_model_key': 'some_model_value'},
            >>> ... overwrites={'key_to_overwrite': 'new_value'},
            >>> ... workspace='my_workspace'
            >>> )
            >>> print(response)
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'/{cls.class_name_list()}/explore'
        response = api_req.post(url, kwargs)
        return response
