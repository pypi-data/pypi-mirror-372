###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import json
import time

from everysk.api import api_requestor, get_api_config


###############################################################################
#   Private Functions Implementation
###############################################################################
def dumps_json(obj):
    """
    Serializes a Python object into a JSON-formatted string with sorted keys and pretty-printing.

    Args:
        obj:
            The Python object to serialize

    Returns:
        str:  A JSON-formatted string representing the serialized output. The keys will be sorted with an level 2 of indentation

    Example:
        >>> from everysk.api.utils import dumps_json
        >>> data = {
        ...     2: 'apple',
        ...     1: 'banana',
        ...     3: 'cherry'
        ... }
        >>> json_str = dumps_json(data)
        >>> print(json_str)
        {
        "1": "banana",
        "2": "apple",
        "3": "cherry"
        }
    """
    return json.dumps(obj, sort_keys=True, indent=2)


###############################################################################
#   Everysk Object Implementation
###############################################################################
class EveryskObject(dict):
    def __init__(self, retrieve_params, params) -> None: # pylint: disable=unused-argument
        super().__init__()
        self.__unsaved_values = set()
        self.update(params)
        self.clear_unsaved_values()

    def get_unsaved_values(self):
        return {k:self[k] for k in self.__unsaved_values}

    def clear_unsaved_values(self):
        self.__unsaved_values = set()

    def __str__(self):
        return dumps_json(self)

    def __repr__(self):
        ident_parts = [type(self).__name__]
        ident_parts.append(f"id={self.get('id')}")
        unicode_repr = f"<{' '.join(ident_parts)} at {hex(id(self))}> JSON: {str(self)}"
        return unicode_repr

    def update(self, dict_) -> None:
        for k, v in dict_.items():
            self.__setattr__(k, v)

    def __setattr__(self, k, v):
        if k.startswith('_') or k in self.__dict__:
            return super().__setattr__(k, v)

        self[k] = v
        return None

    def __getattr__(self, k):
        if k.startswith('_'):
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args) # pylint: disable=raise-missing-from

    def __delattr__(self, k):
        if k.startswith('_') or k in self.__dict__:
            return super().__delattr__(k)
        else:
            del self[k]

    def __setitem__(self, k, v) -> None:
        self.__unsaved_values.add(k)
        super().__setitem__(k, v)

    def __getitem__(self, k):
        return super().__getitem__(k)

    def __delitem__(self, k) -> None:
        super().__delitem__(k)
        self.__unsaved_values.remove(k)

        # # Allows for unpickling in Python 3.x
        # if hasattr(self, '_unsaved_values'):
        #     self._unsaved_values.remove(k)


###############################################################################
#   Everysk List Implementation
###############################################################################
class EveryskList(list):
    def __init__(self, retrieve_params, response, key, cls) -> None:
        """
        Initializes the EveryskList object.

        Args:
            retrieve_params (dict): The parameters used for retrieving data.
            response (dict): The response containing the data.
            key (str): The key in the response dictionary that contains the data.
            cls (class): The class used to create objects from the data.
        """
        super().__init__()
        self.__page_size = retrieve_params.get('page_size', 10)
        self.__next_page_token = response.get('next_page_token', None)
        self.extend([cls({}, params) for params in response[key]])

    def page_size(self):
        """
        Returns the page size used for pagination.

        Returns:
            int: The page size used for pagination.
        """
        return self.__page_size

    def next_page_token(self):
        """
        Retrieves the next page token.

        Returns:
            The next page token.
        """
        return self.__next_page_token


###############################################################################
#   Private Functions Implementation
###############################################################################
def create_api_requestor(params=None):
    """
    Creates an APIRequestor object configured with API settings extracted or derived from the provided parameters.
    It initializes an APIRequestor with configuration settings such as API token, API session ID, API entry point, and SSL certificates status.

    Args:
        params (dict, optional):
            A dictionary of parameters containing API configuration settings. Defaults to an empty dictionary.

    Returns:
        APIRequestor: An instance of APIRequestor, configured with the API settings

    Example:
        >>> api_config_params = {
        >>> ... 'api_entry': 'https://api.example.com',
        >>> ... 'api_version': 'v1',
        >>> ... 'api_sid': 'session123',
        >>> ... 'api_token': 'token456',
        >>> ... 'verify_ssl_certs': False
        >>> }
        >>> api_requestor = create_api_requestor(api_config_params)
        >>> print(api_requestor.base_url)  # This will output the base URL configured for the API requestor.
    """
    params = params or {}
    return api_requestor.APIRequestor(
        *get_api_config(params)
    )

def to_object(cls, retrieve_params, response, extra_keys=None):
    """
    Converts a response dictionary into an instance of the specified class.

    Args:
        cls (type): The class to instantiate. It must implement a constructor
            that accepts (retrieve_params, response_body), and a `class_name()` method.
        retrieve_params (dict): Parameters originally used to retrieve the data.
        response (dict): The response dictionary received from an API call.
        extra_keys (list[str], optional): List of keys to extract from the top-level
            of the response and merge into the response body. Defaults to None.

    Returns:
        object or None: An instance of `cls` populated with the response data,
        or None if the response is invalid or missing the expected key.

    Example:
        >>> from everysk.api.utils import to_object
        >>> from everysk.api.api_resources import Calculation

        >>> response = {'calculation': {'some': 'data'}, 'metadata': {'id': 123}}
        >>> retrieve_params = {'param1': 'value1'}

        >>> calculation_object = to_object(Calculation, retrieve_params, response, extra_keys=['metadata'])
        # Creates a Calculation instance with data: {'some': 'data', 'metadata': {'id': 123}}
    """
    key = cls.class_name()
    result = None
    if response and key in response and isinstance(response[key], dict):
        response_body = response[key]

        if extra_keys and isinstance(extra_keys, list):
            for key in extra_keys:
                if key in response:
                    response_body[key] = response[key]

        result = cls(retrieve_params, response_body)
    return result

def to_list(cls, retrieve_params, response):
    """
    Convert a response dictionary into a list of objects of the given class.

    Args:
        cls (class): The class of the objects to be created.
        retrieve_params (dict): The retrieve parameters used to fetch the response.
        response (dict): The response dictionary.

    Returns:
        list: A list of objects of the given class, created from the response dictionary.
              If the response is empty, the key is missing, or the value is not a list,
              None is returned.

    Example:
        >>> from unittest.mock import MagicMock
        >>> from everysk.api.utils import to_list
        >>> mock_class = MagicMock()

        >>> mock_class.class_name_list.return_value = 'valid_key'

        >>> response = {'valid_key': [{'some': 'data'}, {'more': 'data'}]}
        >>> retrieve_params = {'param1': 'value1'}

        >>> result = to_list(mock_class, retrieve_params, response)
    """
    key = cls.class_name_list()
    result = None
    if response and key in response and isinstance(response[key], list):
        result = EveryskList(retrieve_params, response, key, cls)
    return result

def sleep(t) -> None:
    """
    Sleeps for the specified number of seconds.

    Args:
        t (float): The number of seconds to sleep.
    """
    time.sleep(t)
