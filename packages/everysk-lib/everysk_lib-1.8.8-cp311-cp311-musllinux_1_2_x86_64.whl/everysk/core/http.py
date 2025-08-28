###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import json
import time
from os.path import dirname
from random import SystemRandom
from types import TracebackType
from typing import Any, Self

import httpx

from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.exceptions import HttpError, InvalidArgumentError
from everysk.core.fields import BoolField, DictField, IntField, ListField, StrField, Field
from everysk.core.log import Logger, _get_gcp_headers
from everysk.core.object import BaseObject, BaseObjectConfig
from everysk.core.serialize import loads


log = Logger(name='everysk-lib-core-http-log')


###############################################################################
#   HttpConnectionConfig Class Implementation
###############################################################################
class HttpConnectionConfig(BaseObjectConfig):
    # Number of connections to keep opened in the pool.
    pool_connections_min = IntField(default=20, min_size=1)

    # Maximum number of connections in the pool.
    pool_connections_max = IntField(default=100)

    # Timeout to wait before closing idle connections.
    pool_connections_timeout = IntField(default=5)

    # If the connection should follow the redirects automatic or raise HTTP Redirect error.
    follow_redirects = BoolField(default=True)

    # If the connection accepts HTTP 1 protocol.
    use_http1 = BoolField(default=True)

    # If the connection accepts HTTP 2 protocol.
    use_http2 = BoolField(default=True)

    # Keep the full path to the file with the user agents.
    user_agents_file = StrField()

    # List of user agents to be used in the requests.
    user_agents = ListField()

    # Activate/deactivate the use of the verify flag on HTTP requests.
    # By default this is defined in settings.HTTP_REQUESTS_VERIFY
    # but could be defined in the class configuration too.
    ssl_verify = BoolField(default=settings.HTTP_DEFAULT_SSL_VERIFY)

    # Limit for retries
    retry_limit = IntField(default=settings.HTTP_DEFAULT_RETRY_LIMIT)

    # Times that randrange will use to do the next retry
    retry_end_seconds = IntField(default=settings.HTTP_DEFAULT_RETRY_END_SECONDS)
    retry_start_seconds = IntField(default=settings.HTTP_DEFAULT_RETRY_START_SECONDS)

    def __after_init__(self) -> None:
        # Load the user agents from the file
        if self.user_agents_file is None:
            base_dir = dirname(__file__)
            self.user_agents_file = f'{base_dir}/fixtures/user_agents.json'

        if self.user_agents is None:
            with open(self.user_agents_file, 'r', encoding='utf-8') as fd:
                self.user_agents = json.load(fd)

    def get_client(self) -> httpx.Client:
        """
        Returns a httpx.Client object with the configurations set in the class.
        """
        limits = httpx.Limits(
            max_keepalive_connections=self.pool_connections_min,
            max_connections=self.pool_connections_max,
            keepalive_expiry=self.pool_connections_timeout
        )
        return httpx.Client(
            follow_redirects=self.follow_redirects,
            limits=limits,
            http1=self.use_http1,
            http2=self.use_http2,
            verify=self.get_ssl_verify()
        )

    def get_ssl_verify(self) -> bool:
        """
        Returns a boolean indicating whether the SSL value
        is set.

        Returns:
            bool: True if the SSL verify is set, False otherwise.

        Example:
            >>> http_connection_config = HttpConnectionConfig()
            >>> http_connection_config.get_ssl_verify()
            True
        """
        return self.ssl_verify if settings.HTTP_REQUESTS_VERIFY is Undefined else settings.HTTP_REQUESTS_VERIFY

    def get_random_agent(self) -> str:
        """
        Return a random user agent from the list of user agents.
        """
        random = SystemRandom()
        return random.choice(self.user_agents)


###############################################################################
#   HttpConnection Class Implementation
###############################################################################
class HttpConnection(BaseObject):
    """
    Base class to use for HTTP connections, has two attributes:
        - timeout: It's in and represent seconds, defaults to 30.
        - url: It's string and will be the destination.
    """
    class Config(HttpConnectionConfig):
        pass

    ## Private attributes
    _client: httpx.Client = None
    _config: Config = None # To autocomplete correctly
    _retry_count = IntField(default=1) # Used to control how many times this connection was retry

    ## Public attributes
    headers = DictField(default=None)
    timeout = IntField(default=settings.HTTP_DEFAULT_TIMEOUT) # This is read timeout
    url = StrField(default=None)

    ## Private methods
    def __call__(self, **kwargs: dict) -> Self:
        """
        Set the attributes of the class with the values passed as kwargs.
        We use this method together with the with statement to set the values of the class.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

        return self

    def __enter__(self) -> Self:
        """
        Create and set the HTTP client to be used in the connection so we could reuse the connection.
        """
        self._client = self._config.get_client()
        return self

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        """
        Close the HTTP client to free the resources.

        Returns:
            bool | None: If return is False any exception will be raised.
        """
        self._client.close()
        self._client = None
        return False

    def _clean_response(self, response: httpx.Response) -> httpx.Response:
        """
        Checks status_code for response, if status_code is different than 200 throws an exception.

        Args:
            response (httpx.Response): Http response from server.

        Raises:
            HttpError: If something goes wrong raise exception with status_code and content.
        """
        if getattr(response, 'status_code', settings.HTTP_SUCCESS_STATUS_CODES[0]) not in settings.HTTP_SUCCESS_STATUS_CODES:
            raise HttpError(status_code=response.status_code, msg=response.content)

        return response

    def _get_headers(self) -> dict:
        try:
            # We try to get the GCP headers to send the request
            # The first attempt is to get from a context var
            # If it fails we try to get from the server running
            gcp_headers = _get_gcp_headers()
        except Exception: # pylint: disable=broad-exception-caught
            gcp_headers = {}

        # Get the headers from the class or child classes
        headers = self.get_headers()

        # Update GCP headers with the headers from the class
        # so if the class has the same key it will be overwritten
        gcp_headers.update(headers)

        return gcp_headers

    def _get_response_from_url(self) -> httpx.Response:
        """
        This will be implemented on child classes to really do the connection.
        """
        return None

    ## Public methods
    def get_headers(self) -> dict:
        """
        Headers needed to send HTTP methods.
        Below are the most common Headers used by browsers,
        we use them to look less like a Bot and more like a valid access.

        Returns:
            dict: A dictionary containing the headers information.

        Example:
            >>> http_connection = HttpConnection()
            >>> http_connection.get_headers()
            {
                'Accept-Encoding': 'gzip, deflate;q=0.9',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Connection': 'close',
                'Content-Type': 'text/html; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
        """
        headers = settings.HTTP_DEFAULT_HEADERS.copy()
        if settings.HTTP_USE_RANDOM_USER_AGENT:
            headers['User-Agent'] = self._config.get_random_agent()

        if self.headers is not None:
            headers.update(self.headers)

        return headers

    def get_url(self) -> str:
        """
        Generate the correct url to fetch data from vendor on POST/GET requests.

        Returns:
            str: Containing the correct URL.
        """
        return self.url

    def get_timeout(self) -> httpx.Timeout:
        """
        Return the timeout to be used in the connection.
        """
        timeout = httpx.Timeout(
            timeout=30, # Default timeout for all operations
            read=self.timeout # Timeout for reading the response
        )
        return timeout

    def message_error_check(self, message: str, status_code: int) -> bool: # pylint: disable=unused-argument
        """
        If this method returns True, the connection will be tried again.

        Args:
            message (str): The error message that occurred on the connection.
            status_code (int): The status code of the response.
        """
        return False

    def get_response(self) -> httpx.Response:
        """
        Try to fetch data from self.get_url and calling self._get_response_from_url for the complete response.
        On HttpError, if self.message_error_check is True we will try connect again for a few more times.
        """
        try:
            response = self._clean_response(self._get_response_from_url())
            # After a success we set the value to 1 again
            self._retry_count = 1
        except Exception as error: # pylint: disable=broad-exception-caught
            # Sometimes it can happen that the server is busy, if this happen the error message must be tested
            # and must return true to enable recursion and we will try again the connection.
            message = str(error).lower()
            status_code = getattr(error, 'status_code', 500)
            if self.message_error_check(message, status_code) and self._retry_count < self._config.retry_limit:
                self._retry_count += 1
                # As we have several processes, we use a random number to avoid collision between them.
                random = SystemRandom()
                time.sleep(random.randint(self._config.retry_start_seconds, self._config.retry_end_seconds))
                if settings.EVERYSK_HTTP_LOG_RETRY:
                    log.debug(f'Retry: {self.get_url()} - {message}.')

                response = self.get_response()
            else:
                raise error

        return response


###############################################################################
#   HttpGETConnection Class Implementation
###############################################################################
class HttpGETConnection(HttpConnection):
    """
    Class that implements a interface for HTTP GET connections
    """
    params = DictField()
    user = StrField()
    password = StrField()
    method = StrField(default='GET', readonly=True)

    def __init__(self, url: str = None, headers: dict = None, params: dict = None, timeout: int = None, user: str = None, password: str = None, **kwargs) -> None:
        """
        HTTP GET Connection used to fetch data from a URL.
        Url could be passed on the constructor, set in the class or set later.

        Args:
            url (str, optional): The URL to fetch data from.
            headers (dict, optional): Extra headers added in the connection. Defaults to None.
            params (dict, optional): Parameters added in the url as query. Defaults to None.
            timeout (int, optional): Time when the connection stops to wait and raise an Exception. Defaults to 30 seconds.
            user (str, optional): Username if needed for authentication. Defaults to None.
            password (str, optional): _description_. Defaults to None.
        """
        # We only sent to the super the values that are not None
        # to not overwrite the default values or the ones that are set in the class.
        if url is not None:
            kwargs['url'] = url
        if headers is not None:
            kwargs['headers'] = headers
        if params is not None:
            kwargs['params'] = params
        if timeout is not None:
            kwargs['timeout'] = timeout
        if user is not None:
            kwargs['user'] = user
        if password is not None:
            kwargs['password'] = password

        super().__init__(**kwargs)

    def get_params(self) -> dict:
        """
        This method is used to make the correct params to pass on GET request.
        These params will be added to the URL with & separating then.
        """
        return self.params

    def get_request_params(self) -> dict:
        """
        Constructs and returns the parameters for an HTTP GET request.

        Returns:
            dict: A dictionary containing the URL, headers, parameters, and timeout for the request.
                  If a user is specified, the dictionary will also include authentication credentials.
        """
        params = {
            'url': self.get_url(),
            'headers': self._get_headers(),
            'params': self.get_params(),
            'timeout': self.get_timeout()
        }
        if self.user:
            params['auth'] = (self.user, self.password)

        return params

    def _get_response_from_url(self) -> httpx.Response:
        """
        Try to fetch data from url using GET request.
        Note that any dictionary key whose value is None will not be added to the URL's query string.
        """
        # If the client is already set and not closed we use it
        # otherwise we create a new client and close it after the request.
        params = self.get_request_params()

        if settings.EVERYSK_HTTP_LOG_RESPONSE:
            dct = params
            # To remove the password in the logs
            if 'auth' in params:
                dct = params.copy()
                dct['auth'] = (params['auth'][0], '***********')

            log.debug('HTTP %s request: %s', self.method, self.get_url(), extra={'labels': dct})

        if self._client and not self._client.is_closed:
            response = getattr(self._client, self.method.lower())(**params)
        else:
            with self._config.get_client() as client:
                response = getattr(client, self.method.lower())(**params)

        if settings.EVERYSK_HTTP_LOG_RESPONSE:
            dct = {
                'status_code': response.status_code,
                'time': response.elapsed.total_seconds(),
                'headers': response.headers,
                'content': response.content
            }
            log.debug('HTTP %s response: %s', self.method, self.get_url(), extra={'labels': dct})

        return response


###############################################################################
#   HttpPOSTConnection Class Implementation
###############################################################################
class HttpPOSTConnection(HttpConnection):
    """
    Class that implements a interface for HTTP POST connections.
    If self.is_json is True the POST method will be a JSON POST,
    otherwise will be a Form POST Data.
    """
    is_json = BoolField(default=True)
    payload = Field()
    method = StrField(default='POST', readonly=True)

    def __init__(self, url: str = None, headers: dict = None, payload: dict = None, timeout: int = None, is_json: bool = None, **kwargs) -> None:
        """
        HTTP POST Connection used to send data to a URL.
        Url could be passed on the constructor, set in the class or set later.

        Args:
            url (str, optional): The URL to send data.
            headers (dict, optional): Extra headers added in the connection. Defaults to None.
            payload (dict, optional): Data to send in the POST request. Defaults to None.
            timeout (int, optional): Time when the connection stops to wait and raise an Exception. Defaults to 30 seconds.
            is_json (bool, optional): If the POST method will be a JSON POST or a Form POST Data. Defaults to True.
        """
        # We only sent to the super the values that are not None
        # to not overwrite the default values or the ones that are set in the class.
        if url is not None:
            kwargs['url'] = url
        if headers is not None:
            kwargs['headers'] = headers
        if payload is not None:
            kwargs['payload'] = payload
        if timeout is not None:
            kwargs['timeout'] = timeout
        if is_json is not None:
            kwargs['is_json'] = is_json

        super().__init__(**kwargs)

    def get_payload(self) -> Any:
        """
        Make the correct payload body to pass on POST request.

        Returns:
            dict: With all the payload information to send alongside the request.
        """
        return self.payload

    def get_request_params(self) -> dict:
        """
        Constructs and returns the parameters for an HTTP request.

        Returns:
            dict: A dictionary containing the URL (str), headers (dict), timeout (int), and payload (dict)
                  for the HTTP request. The payload is included as either JSON or
                  form data based on the `is_json` attribute.
        """
        params = {
            'url': self.get_url(),
            'headers': self._get_headers(),
            'timeout': self.get_timeout()
        }

        # Discover if the content_type header is the Default
        # This means that the header was not changed or not set so we need to put the correct one
        is_default_content_type = params['headers'].get('Content-Type') == settings.HTTP_DEFAULT_HEADERS['Content-Type']

        # Get the payload for this request and set the correct headers and params
        payload = self.get_payload()
        if self.is_json:
            params['json'] = payload
            if is_default_content_type:
                params['headers']['Content-Type'] = 'application/json; charset=utf-8'

        elif isinstance(payload, dict):
            params['data'] = payload
            if is_default_content_type:
                params['headers']['Content-Type'] = 'application/x-www-form-urlencoded'

        else:
            # Here we accept the Content-Type that returned from the get_headers method and do not change it.
            params['content'] = payload


        return params

    def _get_response_from_url(self) -> httpx.Response:
        """
        Try to get/set data on url using POST request.
        """
        params = self.get_request_params()

        if settings.EVERYSK_HTTP_LOG_RESPONSE:
            log.debug('HTTP %s request: %s', self.method, self.get_url(), extra={'labels': params})

        # If the client is already set and not closed we use it
        # otherwise we create a new client and close it after the request.
        if self._client and not self._client.is_closed:
            response = getattr(self._client, self.method.lower())(**params)
        else:
            with self._config.get_client() as client:
                response = getattr(client, self.method.lower())(**params)

        if settings.EVERYSK_HTTP_LOG_RESPONSE:
            dct = {
                'status_code': response.status_code,
                'time': response.elapsed.total_seconds(),
                'headers': response.headers,
                'content': response.content
            }
            log.debug('HTTP %s response: %s', self.method, self.get_url(), extra={'labels': dct})

        return response


###############################################################################
#   HttpPOSTCompressedConnection Class Implementation
###############################################################################
class HttpPOSTCompressedConnection(HttpPOSTConnection):

    def get_headers(self) -> dict:
        """
        Headers needed to send HTTP Post methods.
        """
        headers = super().get_headers()
        headers['Content-Encoding'] = 'gzip'
        return headers

    def get_payload(self) -> dict:
        """
        Make the correct payload body to pass on POST request.
        """
        return compress(self.payload, protocol='gzip', serialize='json', use_undefined=True, add_class_path=True)


###############################################################################
#   HttpSDKPOSTConnection Class Implementation
###############################################################################
class HttpSDKPOSTConnection(HttpPOSTCompressedConnection):

    is_json = BoolField(default=False, readonly=True)

    class_name = StrField()
    method_name = StrField()
    self_obj: Any = None
    params = DictField()
    timeout = IntField(default=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT)

    def get_url(self) -> str:
        return f'{settings.EVERYSK_SDK_URL}/{settings.EVERYSK_SDK_VERSION}/{settings.EVERYSK_SDK_ROUTE}'

    def get_payload(self) -> dict:
        """
        Make the correct payload body to pass on POST request.
        """
        self.payload = {
            'class_name': self.class_name,
            'method_name': self.method_name,
            'self_obj': self.self_obj,
            'params': self.params
        }
        return super().get_payload()

    def get_headers(self) -> dict:
        """ Headers needed to send HTTP Post methods. """
        headers = super().get_headers()
        everysk_api_sid = settings.EVERYSK_API_SID
        everysk_api_token = settings.EVERYSK_API_TOKEN

        if not everysk_api_sid:
            raise InvalidArgumentError('Invalid API SID.')
        if not everysk_api_token:
            raise InvalidArgumentError('Invalid API TOKEN.')

        headers['Authorization'] = f'Bearer {everysk_api_sid}:{everysk_api_token}'

        return headers

    def get_response(self) -> dict:
        """
        Try to fetch data from self.get_url and calling self._get_response_from_url for the complete response.
        On HttpError, if self.message_error_check is True we will try connect again more 5 times.
        Decompress the response.content
        """
        response = super().get_response()
        return loads(response.content, use_undefined=True, instantiate_object=True)


###############################################################################
#   HttpDELETEConnection Class Implementation
###############################################################################
class HttpDELETEConnection(HttpGETConnection):
    """
    HttpDELETEConnection is a class that extends HttpGETConnection to handle HTTP DELETE requests.
    """
    method = StrField(default='DELETE', readonly=True)


###############################################################################
#   HttpHEADConnection Class Implementation
###############################################################################
class HttpHEADConnection(HttpGETConnection):
    """
    HttpHEADConnection is a class that extends HttpGETConnection to handle HTTP HEAD requests.
    """
    method = StrField(default='HEAD', readonly=True)


###############################################################################
#   HttpOPTIONSConnection Class Implementation
###############################################################################
class HttpOPTIONSConnection(HttpGETConnection):
    """
    HttpOPTIONSConnection is a class that extends HttpGETConnection to handle HTTP OPTIONS requests.
    """
    method = StrField(default='OPTIONS', readonly=True)


###############################################################################
#   HttpPATCHConnection Class Implementation
###############################################################################
class HttpPATCHConnection(HttpPOSTConnection):
    """
    Class that implements a interface for HTTP PATCH connections.
    If self.is_json is True the PATCH method will be a JSON PATCH,
    otherwise will be a Form PATCH Data.
    """
    method = StrField(default='PATCH', readonly=True)


###############################################################################
#   HttpPUTConnection Class Implementation
###############################################################################
class HttpPUTConnection(HttpPOSTConnection):
    """
    HttpPUTConnection is a class that extends HttpPOSTConnection to handle HTTP PUT requests.
    If self.is_json is True the PUT method will be a JSON PUT,
    otherwise will be a Form PUT Data.
    """
    method = StrField(default='PUT', readonly=True)
