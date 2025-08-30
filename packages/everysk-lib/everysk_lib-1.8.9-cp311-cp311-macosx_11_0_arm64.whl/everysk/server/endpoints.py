###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['BaseEndpoint', 'JSONEndpoint']

from collections.abc import Generator
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import urlparse

from starlette.exceptions import HTTPException
from starlette.types import Receive, Scope, Send

from everysk.config import settings
from everysk.core.exceptions import HttpError
from everysk.core.log import Logger, LoggerManager, _get_trace_data
from everysk.core.object import BaseObject
from everysk.core.serialize import loads
from everysk.server.requests import JSONRequest, Request
from everysk.server.responses import DumpsParams, JSONResponse, Response

if TYPE_CHECKING:
    import httpx


log = Logger(__name__)
HTTP_METHODS = ('GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')
HTTP_METHODS_WITH_PAYLOAD = ('POST', 'PUT', 'PATCH')
HTTP_STATUS_CODES_LOG = settings.EVERYSK_SERVER_CODES_LOG


###############################################################################
#   BaseEndpoint Class Implementation
###############################################################################
class BaseEndpoint:
    # Based in starlette.endpoints.HTTPEndpoint
    ## Private attributes
    _allowed_methods: list[str] = None
    _request_class: Request = Request
    _response_class: Response = Response

    ## Public attributes
    receive: Receive = None
    request: Request = None
    scope: Scope = None
    send: Send = None

    ## Internal methods
    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Base class for all endpoints in the application.

        Args:
            scope (Scope): ASGI scope dictionary.
            receive (Receive): ASGI receive data.
            send (Send): ASGI send data.

        Raises:
            HttpError: 500 - Request is not an HTTP request.
        """
        type_request = scope.get('type', '')
        if type_request.lower() != 'http':
            raise HttpError(status_code=500, msg='Request is not an HTTP request.')

        self._allowed_methods = [method for method in HTTP_METHODS if hasattr(self, method.lower())]
        self.receive = receive
        self.request = self._request_class(scope, receive=receive)
        self.scope = scope
        self.send = send

    def __await__(self) -> Generator[Any, None, None]:
        """
        Method to allow the use of the await keyword in the class.
        This method will call the dispatch method and return the result.
        It's the default behavior of the Starlette HTTPEndpoint class.
        Don't change this method.
        """
        return self.dispatch().__await__()

    ## Private methods
    def _make_response(self, content: Any = None, status_code: int = 200) -> Response | JSONResponse:
        """
        Create a response object with the given content and status code.

        Args:
            content (Any, optional): The content to include in the response. Defaults to None.
            status_code (int, optional): The HTTP status code for the response. Defaults to 200.

        Returns:
            Response | JSONResponse: The response object.
        """
        # Create the response object with the content and status code.
        return self._response_class(content=content, status_code=status_code)

    def _has_error_handlers(self) -> bool:
        """
        Check if the application has error handlers.

        Returns:
            bool: True if error handlers are defined, False otherwise.
        """
        # https://stackoverflow.com/a/71298949
        # Inside the app we have the exception_handlers attribute that is a dictionary
        # and it contains the error handlers that are customized by the user.
        # Inside the scope we have the starlette.exception_handlers that are the default handlers
        # We could not predict when the error will be raised so we need to check every attribute
        request = getattr(self, 'request', None)
        if request is None:
            # If the request is not set, we assume there are no error handlers
            return False

        app = getattr(request, 'app', None)
        if app is None:
            # If the app is not set, we assume there are no error handlers
            return False

        exception_handlers = getattr(app, 'exception_handlers', None)
        return bool(exception_handlers)

    async def _log_error(self, error: Exception) -> None:
        """
        Log the error if it is an internal server error (500) or any other status code defined in HTTP_STATUS_CODES_LOG.

        Args:
            error (Exception): The error to log.
        """
        # We only log internal server errors in GCP
        if getattr(error, 'status_code', 500) in HTTP_STATUS_CODES_LOG:
            # Only these methods can have a payload
            if self.request.method in HTTP_METHODS_WITH_PAYLOAD:
                payload = await self.get_http_payload()
            else:
                payload = {}

            # Headers are already in the LoggerManager
            msg = str(error)
            extra = {'http_payload': payload}
            if len(msg) > settings.EVERYSK_SERVER_HTTP_ERROR_MESSAGE_SIZE:
                extra['labels'] = {'error': msg}
                msg = msg[: settings.EVERYSK_SERVER_HTTP_ERROR_MESSAGE_SIZE]

            log.error(msg, extra=extra)

    ## Public sync methods
    def get_http_headers(self) -> dict[str, str]:
        """
        Get the HTTP headers from the request.
        Returns dictionary were the key is the header name in lower case and the value is the header value.
        """
        return dict(self.request.headers)

    def get_http_method_function(self) -> callable:
        """
        Get the function that for the http method of the request.
        If the function doesn't exist, it will return the method_not_allowed function.
        """
        name = self.get_http_method_name()
        # Check if the method is allowed, we create a list of allowed methods in the __init__ method
        if name.upper() not in self._allowed_methods:
            return self.method_not_allowed

        return getattr(self, name)

    def get_http_method_name(self) -> str:
        """
        Get the name of the HTTP method from the request.
        If the request method is HEAD and the class doesn't
        have a head method, it will return get instead.
        """
        if self.request.method == 'HEAD' and not hasattr(self, 'head'):
            name = 'get'
        else:
            name = self.request.method.lower()

        return name

    ## Public async methods
    async def dispatch(self) -> None:
        """
        Main method that will always be executed for each request, takes
        the function related to the HTTP method of the request and executes it.
        """
        # Because the ASGI protocol copy the context to the event loop
        # for every request, we create an empty LoggerManager to avoid
        # shared values between requests.
        with LoggerManager(http_headers={}, http_payload={}, labels={}, stacklevel=None, traceback=''):
            headers = self.get_http_headers()
            # Insert the headers in the Logger Context to propagate them to the logs
            with LoggerManager(http_headers=headers):
                try:
                    response = await self.get_http_response()
                except Exception as error:  # pylint: disable=broad-except
                    # If something goes wrong, we catch the exception and return a response
                    response = await self.get_http_exception_response(error)

                    # Log the error if it is an internal server error
                    await self._log_error(error)

                    # If we have error handlers, we raise the error again to be handled by them
                    # and all errors must be raised as HTTPException
                    if self._has_error_handlers():
                        # To be compatible with the starlette error handlers and catch
                        # the correct status code, we need to raise an HTTPException
                        if isinstance(error, HttpError):
                            raise HTTPException(status_code=error.status_code, detail=error.msg) from error

                        raise

                await response(self.scope, self.receive, self.send)

        # To avoid shared values between requests, we reset the LoggerManager
        LoggerManager.reset()

    async def get_http_exception_response(self, error: Exception) -> Response:
        """
        Method to return a response when an exception is raised during the request.

        Args:
            error (Exception): The exception raised during the request.
        """
        status_code = getattr(error, 'status_code', 500)
        return self._make_response(content=str(error), status_code=status_code)

    async def get_http_payload(self) -> bytes:
        """
        Get the HTTP payload from the request.
        The payload is the body of the request and it's a bytes object.
        """
        return await self.request.body()

    async def get_http_response(self) -> Response:
        """
        Get the correct function for the HTTP method of the request
        and execute it to create a response.
        If the method doesn't exist, it will return a 405 response.
        """
        method_function = self.get_http_method_function()
        response = await method_function()

        if not isinstance(response, Response):
            response = self._make_response(content=response)

        return response

    async def method_not_allowed(self) -> None:
        """
        Default method for when the HTTP method is not found in the class.

        Raises:
            HttpError: 405 - Method not allowed
        """
        raise HttpError(status_code=405, msg=f'Method {self.request.method} not allowed.')


###############################################################################
#   JSONEndpoint Class Implementation
###############################################################################
class LoadsParams(BaseObject):
    date_format: str | None = None
    datetime_format: str | None = None
    instantiate_object: bool = True
    protocol: Literal['json', 'orjson'] = 'json'
    use_undefined: bool = True

    def __init__(
        self,
        *,
        date_format: str | None = None,
        datetime_format: str | None = None,
        instantiate_object: bool = True,
        protocol: Literal['json', 'orjson'] = 'json',
        use_undefined: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            date_format=date_format,
            datetime_format=datetime_format,
            instantiate_object=instantiate_object,
            protocol=protocol,
            use_undefined=use_undefined,
            **kwargs,
        )

    def to_dict(self) -> dict:
        dct = super().to_dict(add_class_path=True, recursion=True)
        # we remove all private keys because we don't want them in the serialized output
        return {key: value for key, value in dct.items() if not key.startswith('_')}


class JSONEndpoint(BaseEndpoint):
    ## Private attributes
    _request_class: JSONRequest = JSONRequest
    _response_class: JSONResponse = JSONResponse
    _serialize_dumps_params: DumpsParams = DumpsParams()
    _serialize_loads_params: LoadsParams = LoadsParams()

    ## Public attributes
    rest_key_name: str = Undefined
    rest_key_value: str = Undefined

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Class to handle JSON requests and responses.
        Inherit from this class and implement the HTTP methods to create an endpoint.

        Args:
            scope (Scope): ASGI scope dictionary.
            receive (Receive): ASGI receive data.
            send (Send): ASGI send data.
        """
        super().__init__(scope, receive, send)

        if self.rest_key_name is Undefined:
            self.rest_key_name = settings.EVERYSK_SERVER_REST_KEY_NAME

        if self.rest_key_value is Undefined:
            self.rest_key_value = settings.EVERYSK_SERVER_REST_KEY_VALUE

    def check_rest_key(self) -> bool:
        """
        Check if the rest key is present in the request headers and if it's the correct value.
        If the rest key name or value is not set, it will always return True.
        """
        if not self.rest_key_name or not self.rest_key_value:
            return True

        rest_key_value = self.request.headers.get(self.rest_key_name)
        return rest_key_value == self.rest_key_value

    def _make_response(self, content: Any = None, status_code: int = 200) -> JSONResponse:
        """
        Create a JSONResponse object with the content and status code.
        The content is serialized to JSON using the specified serializer.

        Args:
            content (Any): The content to be serialized and returned in the response.
            status_code (int): The HTTP status code for the response.
        """
        return self._response_class(
            content=content, status_code=status_code, serialize_dumps_params=self._serialize_dumps_params
        )

    async def get_http_exception_response(self, error: Exception) -> JSONResponse:
        """
        Method to return a JSONResponse when an exception is raised during the request.
        The trace_id is added to the response to help with debugging.

        Args:
            error (Exception): The exception raised during the request.

        Returns:
            JSONResponse: A JSONResponse with the error message, status code and trace_id.
        """
        trace_data = _get_trace_data(headers=self.get_http_headers())
        msg = str(error)
        status_code = getattr(error, 'status_code', 500)
        return self._make_response(
            content={'error': msg, 'code': status_code, 'trace_id': trace_data['trace_id']}, status_code=status_code
        )

    async def get_http_payload(self) -> Any:
        """
        Get the HTTP payload from the request and deserialize it to a
        Python object or raises a HttpError if the body is empty and is
        not an instance of string or bytes.

        Raises:
            HttpError: When we have an empty json payload.
        """
        body = await super().get_http_payload()

        if body and isinstance(body, (bytes, str)):
            return loads(body, **self._serialize_loads_params.to_dict())

        raise HttpError(status_code=400, msg='Invalid Payload')

    async def get_http_response(self) -> JSONResponse:
        """
        Changes the return of the get_http_response method to return a JSONResponse.
        If the response is not a Response object, it will be converted to a JSONResponse
        otherwise it will be returned as is.
        If the rest key is incorrect, it will raise a 401 error.

        Raises:
            HttpError: 401 - Unauthorized access to this resource.
        """
        if not self.check_rest_key():
            raise HttpError(status_code=401, msg='Unauthorized access to this resource.')

        return await super().get_http_response()


###############################################################################
#   HealthCheckEndpoint Class Implementation
###############################################################################
class HealthCheckEndpoint(JSONEndpoint):
    """
    Endpoint to check if the service is running.
    By default, it will return a JSONResponse with the status 'SENTA_A_PUA'.
    """

    default_response: dict = {'status': 'SENTA_A_PUA'}  # noqa: RUF012
    # These are set to None so the endpoint can be accessed without the rest key
    rest_key_name: str = None
    rest_key_value: str = None

    async def get(self) -> JSONResponse:
        return JSONResponse(self.default_response)

    async def post(self) -> JSONResponse:
        return JSONResponse(self.default_response)


###############################################################################
#   RedirectEndpoint Class Implementation
###############################################################################
## WARNING:
# httpx imports are placed inside the functions to load this module only for this class
class RedirectEndpoint(BaseEndpoint):
    """
    Endpoint to redirect requests to another host.
    We use this endpoint to redirect requests to another host
    and return the response to the client, acting as a proxy.

    Raises:
        ValueError: If the host_url is not set in the class.
    """

    host_url: str = settings.EVERYSK_SERVER_REDIRECT_URL
    timeout: int = 600

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        super().__init__(scope, receive, send)
        if not self.host_url:
            raise ValueError('host_url is required for redirect endpoint.')

    def _get_client(self) -> 'httpx.Client':
        from httpx import Client  # noqa: PLC0415

        return Client(headers=self.get_request_headers())

    def get_full_url(self) -> str:
        """
        Get the full URL to be used in the connection.
        This method will return the URL with the host, path and query string.
        """
        url = self.request.url
        result = f'{self.host_url}{url.path}'
        if url.query:
            result = f'{result}?{url.query}'
        return result

    def get_host(self) -> str:
        """Get the host from the host_url attribute."""
        url = urlparse(self.host_url)
        return url.netloc

    def get_request_headers(self) -> dict:
        """Get the headers received in the request and update the Host header with the destination host."""
        headers = dict(self.request.headers)

        # We need to update the Host header with the destination host
        headers['host'] = self.get_host()

        return headers

    def get_response_headers(self, response: 'httpx.Response') -> dict:
        """
        Get the headers from the redirected response and keep only the content_type to be used in the response.

        Args:
            response (httpx.Response): The response from the redirect request.
        """
        return {'content-type': response.headers.get('content-type')}

    def get_timeout(self) -> 'httpx.Timeout':
        """Return the timeout to be used in the connection."""
        from httpx import Timeout  # noqa: PLC0415

        return Timeout(
            timeout=30,  # Default timeout for all operations
            read=self.timeout,  # Timeout for reading the response
        )

    def make_response(self, response: 'httpx.Response') -> Response | JSONResponse:
        """
        Create a Response or JSONResponse object based on the content type of the response.

        Args:
            response (httpx.Response): The response from the redirect request.
        """
        content_type = response.headers.get('content-type')
        cls = Response if 'json' in content_type else JSONResponse
        headers = self.get_response_headers(response=response)

        return cls(status_code=response.status_code, content=response.content, headers=headers)

    async def get(self) -> Response | JSONResponse:
        """HTTP GET method to redirect the request to another host."""
        with self._get_client() as connection:
            response = connection.get(self.get_full_url(), timeout=self.get_timeout())

        return self.make_response(response=response)

    async def post(self) -> Response | JSONResponse:
        """HTTP POST method to redirect the request to another host."""
        body = await self.request.body()
        with self._get_client() as connection:
            response = connection.post(self.get_full_url(), content=body, timeout=self.get_timeout())

        return self.make_response(response=response)
