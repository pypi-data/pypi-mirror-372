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

from typing import Any

from everysk.config import settings
from everysk.api import http_client
from everysk.core.exceptions import APIError

###############################################################################
#   APIRequestor Implementation
###############################################################################
class APIRequestor(object):

    def __init__(self, api_entry, api_version, api_sid, api_token, verify_ssl_certs) -> None:
        """
        Initializes an APIRequestor object with the necessary parameters to make HTTP requests to an API.

        This constructors sets up the APIRequestor with custom headers, including authorization, content type and user agent details.

        Args:
            api_entry (str): The base URL of the API endpoint.
            api_version (str): The current version of the API.
            api_sid (str): The API SID (identifier) for authentication.
            api_token (str): The API token for authentication.
            verify_ssl_certs (bool): Specified whether SSL certificates should be verified.

        Raises:
            Exception: If any of the parameters are invalid.

        Example:
            >>> from everysk.api.api_requestor import APIRequestor

            >>> api_requestor = APIRequestor(
            >>> ... api_entry='https://api.example.com',
            >>> ... api_version='v2',
            >>> ... api_sid='your_api_sid',
            >>> ... api_token='your_api_token',
            >>> ... verify_ssl_certs=True
            >>> ... )
        """
        if not api_entry:
            raise ValueError('Empty api_entry.') # pylint: disable=broad-exception-raised
        if api_version != 'v2':
            raise ValueError('Invalid api_version (supported version: "v2").') # pylint: disable=broad-exception-raised
        if not api_sid:
            raise ValueError('Invalid api_sid.') # pylint: disable=broad-exception-raised
        if not api_token:
            raise ValueError('Invalid api_token.') # pylint: disable=broad-exception-raised

        self.headers = settings.HTTP_DEFAULT_HEADERS.copy()
        self.headers.update(
            {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_sid}:{api_token}',
                'User-Agent': f'Everysk PythonBindings/{api_version}'
            }
        )
        self.base_url = f'{api_entry}/{api_version}'
        self.client = http_client.new_default_http_client(
            timeout=3600,
            verify_ssl_certs=verify_ssl_certs,
            allow_redirects=False
        )

    def _clean_response(self, code: int, response: str) -> Any:
        if code not in settings.HTTP_SUCCESS_STATUS_CODES:
            raise APIError(code, response)
        return json.loads(response)

    def get(self, path, params):
        """
        Sends a GET request to the specified path with the given parameters.

        Args:
            path (str): The path to send the GET request to.
            params (dict): The parameters to include in the GET request.

        Returns:
            dict: The JSON response from the GET request.

        Raises:
            APIError: If the response code is not in the HTTP_SUCCESS_STATUS_CODES list.
        """
        url = f'{self.base_url}{path}'
        code, response = self.client.request(
            'GET',
            url,
            headers=self.headers,
            params=params
        )
        return self._clean_response(code, response)

    def post(self, path, payload):
        """
        Sends a POST request to the specified path with the given payload.

        Args:
            path (str): The path to send the request to.
            payload (dict): The payload to include in the request.

        Raises:
            APIError: If the response code is not in the HTTP_SUCCESS_STATUS_CODES list.

        Returns:
            dict: The JSON response from the API.
        """
        url = f'{self.base_url}{path}'
        code, response = self.client.request(
            'POST',
            url,
            headers=self.headers,
            payload=payload
        )
        return self._clean_response(code, response)

    def delete(self, path):
        """
        Sends a DELETE request to the specified path.

        Args:
            path (str): The path to send the DELETE request to.

        Raises:
            APIError: If the response code is not in the HTTP_SUCCESS_STATUS_CODES list.

        Returns:
            dict: The JSON response from the server.
        """
        url = f'{self.base_url}{path}'
        code, response = self.client.request(
            'DELETE',
            url,
            headers=self.headers
        )
        return self._clean_response(code, response)

    def put(self, path, payload):
        """
        Sends a PUT request to the specified path with the given payload.

        Args:
            path (str): The path to send the request to.
            payload (dict): The payload to include in the request.

        Raises:
            APIError: If the response code is not in the HTTP_SUCCESS_STATUS_CODES list.

        Returns:
            dict: The JSON response from the server.
        """
        url = f'{self.base_url}{path}'
        code, response = self.client.request(
            'PUT',
            url,
            headers=self.headers,
            payload=payload
        )
        return self._clean_response(code, response)
