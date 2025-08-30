###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['create_application']

from starlette.applications import Starlette

from everysk.config import settings
from everysk.server.middlewares import Middleware, update_with_default_middlewares
from everysk.server.routing import Route


###############################################################################
#   Public functions Implementation
###############################################################################
def create_application(
    *, # This disables positional arguments for the function
    routes: list[Route],
    debug: bool = settings.EVERYSK_SERVER_DEBUG,
    middlewares: list[Middleware] = None,
    exception_handlers: dict[int | Exception, callable] = None
) -> Starlette:
    """
    Create a Starlette application with the given routes, middleware and exception handlers.
    By default the first middleware is the GZipMiddleware and SecurityHeadersMiddleware is the last one,
    so you don't need to add them in the list.
    Routes could be normal Starlette routes or the RouteLazy class that will lazy load the endpoint class.

    Args:
        routes (list[Route]): A list of routes to serve incoming HTTP and WebSocket requests.
        debug (bool, optional): Boolean indicating if debug tracebacks should be returned on errors. Defaults to False.
        middleware (list[Middleware], optional): A list of middleware to run for every request. Defaults to None.
        exception_handlers (dict[int, callable], optional): A mapping of either integer status codes, or exception class types onto callables which handle the exceptions. Defaults to None.

    """
    middlewares = update_with_default_middlewares(middlewares)

    return Starlette(debug=debug, routes=routes, middleware=middlewares, exception_handlers=exception_handlers)
