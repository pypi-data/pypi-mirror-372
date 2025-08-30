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
from everysk.api.api_resources.api_resource import APIResource
from everysk.api import utils

###############################################################################
#   Parser Implementation
###############################################################################
class Parser(
    APIResource
):

    @classmethod
    def __call_method(cls, method, **kwargs):
        """
        A generic method to call various methods on the Parser object. This function dynamically
        constructs and executes an API request based on the specified method and additional arguments.
        It constructs and sends an API request, adapting the URL method and the arguments provided.
        Since this is a generic function, the callers must ensure that the 'method' argument and the '**kwargs' are appropriate for the specific API function.

        Args:
            method (str):
                The name of the method to be called. This method should correspond to a valid API endpoint
                or a function within the class, determining the nature of the API request to be made.

            **kwargs:
                A variable set of keyword arguments. These are passed dynamically to the method being called and
                should align with the expected parameters for that specific method or API endpoint.

        Returns:
            dict: The API response.

        Example:
            Assuming there's a method 'fetch_data' that expects parameters 'data_id' and 'filter':
            >>> response = ClassName.__call_method('fetch_data', data_id=123, filter='typeA')
            >>> print(response)
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'{cls.class_url()}/{method}'
        response = api_req.post(url, kwargs)
        return response

    @classmethod
    def parse(cls, method, **kwargs):
        """
        Parses data using the specified method.

        Args:
            method (str): The parsing method.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The parsed data.
        """
        return cls.__call_method(f'{method}/parse', **kwargs)
