###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # pylint: disable=import-error

from everysk.core.datetime.date_settings import DEFAULT_DATE_FORMAT, DEFAULT_DATE_TIME_FORMAT
from everysk.core.serialize import dumps

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # pylint: disable=no-member


###############################################################################
#   HTTPClient Implementation
###############################################################################
class HTTPClient:
    def __init__(self, timeout=3600, verify_ssl_certs=True, allow_redirects=False) -> None:
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.verify_ssl_certs = verify_ssl_certs

    def request(self, method, url, headers, params=None, payload=None):
        raise NotImplementedError('HTTPClient subclasses must implement `request`.')


###############################################################################
#   Requests Client Implementation
###############################################################################
class RequestsClient(HTTPClient):
    def request(self, method, url, headers, params=None, payload=None):
        _args = {
            'method': method,
            'url': url,
            'headers': headers,
            'params': params,
            'timeout': self.timeout,
            'verify': self.verify_ssl_certs,
            'allow_redirects': self.allow_redirects,
        }

        if payload:
            _args['data'] = dumps(
                payload,
                date_format=DEFAULT_DATE_FORMAT,
                datetime_format=DEFAULT_DATE_TIME_FORMAT,
                use_undefined=False,
                add_class_path=False,
                decode_bytes=True,
            )

        response = requests.request(**_args)

        return (response.status_code, response.content)


def new_default_http_client(*args, **kwargs):
    return RequestsClient(*args, **kwargs)
