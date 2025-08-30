###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any
import inspect

from everysk.core.exceptions import HttpError, SDKError
from everysk.core.fields import ListField
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.object import BaseDict, BaseObject
from everysk.core.string import import_from_string


###############################################################################
#   Public Functions Implementation
###############################################################################
def handler_input_args(input_args: Any) -> Any:
    """
    This function handles the input arguments and returns the dictionary.

    Args:
        input_args (Any): The input arguments to be handled.

    Returns:
        Any: The parsed object.
    """
    ret: Any = input_args
    if isinstance(input_args, dict):
        ret = BaseDict()
        for key, value in input_args.items():
            ret[key] = handler_input_args(value)

    elif isinstance(input_args, list):
        ret = type(input_args)()
        for item in input_args:
            ret.append(handler_input_args(item))

    return ret


###############################################################################
#   BaseSDK Class Implementation
###############################################################################
class BaseSDK(BaseObject):
    """
    A base class for SDK classes.

    This class provides a base implementation for SDK classes.
    """

    @classmethod
    def get_response(cls, **kwargs: dict) -> Any:
        """
        Get a response from an SDK method.

        This method sends an HTTP POST request to a remote service and returns the response as a dictionary.

        Args:
            **kwargs (dict): Keyword arguments used to configure the HTTP request and SDK behavior.

        Keyword Args:
            class_name (str, optional): The name of the SDK class making the request. Defaults to the class name of the calling class.
            method_name (str, optional): The name of the SDK method making the request. Defaults to the name of the calling function.
            self_obj (object, optional): An instance of the calling SDK class, if applicable. Defaults to None.
            params (dict, optional): Additional parameters to include in the HTTP request. Defaults to an empty dictionary.

        Returns:
            Any: The response from the remote service.

        Raises:
            SDKError: If there is an issue with the SDK operation.
        """

        # Set default values for keyword arguments if not provided
        kwargs.setdefault('class_name', cls.__name__)
        kwargs.setdefault('method_name', inspect.stack()[1].function)
        kwargs.setdefault('self_obj', None)
        kwargs.setdefault('params', {})

        try:
            response: httpx.Response = HttpSDKPOSTConnection(**kwargs).get_response()
        except HttpError as error:
            raise SDKError(error.msg) from error

        if response and isinstance(response, (dict, BaseDict)) and 'error_message' in response and 'error_module' in response:
            error_module = import_from_string(response['error_module'])
            raise error_module(response['error_message'])

        return response
