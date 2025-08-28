###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['Middleware', 'GZipMiddleware', 'SecurityHeadersMiddleware']

from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware

from everysk.config import settings


GZIP_MINIMUM_SIZE = settings.EVERYSK_SERVER_GZIP_MINIMUM_SIZE
GZIP_COMPRESS_LEVEL = settings.EVERYSK_SERVER_GZIP_COMPRESS_LEVEL


###############################################################################
#   Public Functions Implementation
###############################################################################
def update_with_default_middlewares(middlewares: list[Middleware]) -> list[Middleware]:
    """
    Update the given middleware list with the default ones.
    The default middleware are the GZipMiddleware and SecurityHeadersMiddleware.
    """
    if middlewares is None:
        middlewares = []

    if settings.EVERYSK_SERVER_GZIP_MIDDLEWARE_ENABLED:
        middlewares.insert(0, Middleware(GZipMiddleware, minimum_size=GZIP_MINIMUM_SIZE, compresslevel=GZIP_COMPRESS_LEVEL))

    if settings.EVERYSK_SERVER_SECURITY_MIDDLEWARE_ENABLED:
        middlewares.append(Middleware(SecurityHeadersMiddleware))

    return middlewares


###############################################################################
#   SecurityHeadersMiddleware Class Implementation
###############################################################################
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to the response.
    These headers are used to protect the application against
    some types of attacks and will be added to every response.
    """

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-DNS-Prefetch-Control
        response.headers['X-DNS-Prefetch-Control'] = 'off'

        # https://webtechsurvey.com/response-header/x-download-options
        # Only works on IE8
        response.headers['X-Download-Options'] = 'noopen'

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
        response.headers['X-Frame-Options'] = 'DENY'

        # https://webtechsurvey.com/response-header/x-permitted-cross-domain-policies
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection
        # Warning: Even though this feature can protect users of older web browsers that don't yet support CSP, in some cases,
        # XSS protection can create XSS vulnerabilities in otherwise safe websites. See the section below for more information.
        # response.headers['X-XSS-Protection'] = '1; mode=block'

        return response
