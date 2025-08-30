###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['Route', 'RouteLazy']

from starlette.routing import Route, compile_path
from starlette.types import Receive, Scope, Send

from everysk.core.string import import_from_string


###############################################################################
#   RouteLazy Class Implementation
###############################################################################
class RouteLazy(Route):
    app: callable = None
    endpoint: str = None
    include_in_schema: bool = True
    methods: set = None
    name: str = None
    path: str = None

    def __init__(self, path: str, endpoint: str, name: str | None = None) -> None: # pylint: disable=super-init-not-called
        """
        Route class that will lazy load the endpoint class.

        Args:
            path (str): The path of the route always start with '/'.
            endpoint (str): Full doted class path of the endpoint.
            name (str | None, optional): A name for this endpoint. Defaults to the same value in endpoint.

        Raises:
            ValueError: If the path doesn't start with '/'.
        """
        if not path.startswith('/'):
            raise ValueError("Routed paths must start with '/'")

        self.path = path
        self.endpoint = endpoint
        self.name = endpoint if name is None else name
        self.path_regex, self.path_format, self.param_convertors = compile_path(path)

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Method to handle the incoming request and execute it.
        If the endpoint is a string, it will import the endpoint class and execute it.

        Args:
            scope (Scope): ASGI scope dictionary.
            receive (Receive): ASGI receive data.
            send (Send): ASGI send data.
        """
        if isinstance(self.endpoint, str):
            self.app = import_from_string(self.endpoint)
        else:
            self.app = self.endpoint

        await self.app(scope, receive, send)
