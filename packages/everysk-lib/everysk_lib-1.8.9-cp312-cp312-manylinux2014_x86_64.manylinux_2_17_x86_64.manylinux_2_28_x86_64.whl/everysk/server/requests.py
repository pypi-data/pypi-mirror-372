###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['JSONRequest', 'Request']

from starlette.requests import Request as _Request

from everysk.core.compress import decompress
from everysk.core.log import Logger
from everysk.core.serialize import loads


log = Logger(__name__)


###############################################################################
#   Request Class Implementation
###############################################################################
class Request(_Request):

    async def body(self) -> bytes:
        """
        Method to return the body of the request.
        If we receive a request with a Content-Encoding header, we decompress the body.
        """
        # If self._body is set then body was already read.
        if not hasattr(self, '_body'):
            body = await super().body()
            # We only decompress the body if it is not empty.
            if body:
                content_encoding = self.headers.get('Content-Encoding', '').lower()
                if 'gzip' in content_encoding:
                    try:
                        body = decompress(body, protocol='gzip', serialize=None )
                    except Exception: # pylint: disable=broad-except
                        log.error('Error decompressing the request body.', extra={'labels': {'body': body}})

            self._body = body # pylint: disable=attribute-defined-outside-init
        return self._body


###############################################################################
#   JSONRequest Class Implementation
###############################################################################
class JSONRequest(Request):

    async def json(self):
        """
        Method to return the JSON content of the request body.
        It uses the loads function from the core.serialize module to parse the body.
        """
        if not hasattr(self, '_json'):
            body = await self.body()
            self._json = loads(body, protocol='json', use_undefined=True) # pylint: disable=attribute-defined-outside-init

        return self._json
