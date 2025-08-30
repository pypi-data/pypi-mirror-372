###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import tempfile

from everysk.core.fields import BoolField, ChoiceField, DictField, FloatField, IntField, ListField, StrField

## Project settings
DEBUG = BoolField(default=True)

# PROD | DEV | LOCAL
PROFILE = ChoiceField(default='DEV', choices=('PROD', 'DEV', 'LOCAL'))

## Redis
REDIS_HOST = StrField(default='0.0.0.0')  # noqa: S104
REDIS_PORT = IntField(default=6379)
REDIS_NAMESPACE = StrField()
REDIS_HEALTH_CHECK_INTERVAL = IntField(default=30)  # seconds
REDIS_RETRY_ATTEMPTS = IntField(default=3)
REDIS_RETRY_BACKOFF_MIN = FloatField(default=0.05)  # Minimum backoff between each retry in seconds
REDIS_RETRY_BACKOFF_MAX = FloatField(default=0.5)  # Maximum backoff between each retry in seconds
REDIS_RETRY_EXTRA_ERROR_LIST = ListField()  # Added more errors to retry
REDIS_SOCKET_KEEPALIVE = BoolField(default=True)
REDIS_SOCKET_TIMEOUT = IntField(default=120)  # seconds
REDIS_SHOW_LOGS = BoolField(default=False)

## Everysk SIGNING key is used to verify the integrity of the data
EVERYSK_SIGNING_KEY = StrField(default=None)

## Google Cloud
EVERYSK_GOOGLE_CLOUD_LOCATION = StrField(default='us-central1')
EVERYSK_GOOGLE_CLOUD_PROJECT = StrField()

## Logger settings
# This is the default app server to infer the headers and payload
LOGGING_APP_SERVER = StrField(default='flask')

# This is the default string to create the Google Cloud Trace ID
LOGGING_GOOGLE_CLOUD_TRACE_ID = StrField(default='projects/{EVERYSK_GOOGLE_CLOUD_PROJECT}/traces')

# This is the default Formatter for the logs
LOGGING_JSON = BoolField(default=False)

## Slack URL to send messages
SLACK_URL = StrField()

## Activate/deactivate HTTP Log for every request/response
EVERYSK_HTTP_LOG_RESPONSE = BoolField(default=False)

## Activate/deactivate HTTP Log for retry connections
EVERYSK_HTTP_LOG_RETRY = BoolField(default=False)

## List of HTTP Success status codes that do not raise HTTPError
HTTP_SUCCESS_STATUS_CODES = ListField(default=[200, 201, 202, 204, 303], readonly=True)

## HTTP default headers used to send requests
HTTP_DEFAULT_HEADERS = DictField(
    default={
        'Accept-Encoding': 'gzip',
        'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
        'Cache-control': 'no-cache',
        'Content-Type': 'text/html; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',  # noqa: E501
    },
    readonly=True,
)
HTTP_DEFAULT_TIMEOUT = IntField(default=30)
HTTP_DEFAULT_SSL_VERIFY = BoolField(default=True)
HTTP_DEFAULT_RETRY_LIMIT = IntField(default=5)
HTTP_DEFAULT_RETRY_END_SECONDS = IntField(default=30)
HTTP_DEFAULT_RETRY_START_SECONDS = IntField(default=5)

## Serialization settings
SERIALIZE_CONVERT_METHOD_NAME = StrField(default='to_native')
SERIALIZE_DATE_KEY = StrField(default='__date__')
SERIALIZE_DATETIME_KEY = StrField('__datetime__')
SERIALIZE_UNDEFINED_KEY = StrField('__undefined__')
SERIALIZE_USE_UNDEFINED = BoolField(default=False)

## Activate/deactivate the use of the verify flag on HTTP requests.
# By default the value is Undefined and the value comes from the self._config.ssl_verify
# attribute in the HttpConnection class, if it is defined we use it.
HTTP_REQUESTS_VERIFY = BoolField(default=Undefined)

# Activate/deactivate the use of random user agents on HTTP requests
HTTP_USE_RANDOM_USER_AGENT = BoolField(default=False)

# Default directory to use the known_hosts file and other SFTP configurations
EVERYSK_SFTP_DIR = StrField(default=f'{tempfile.gettempdir()}/sftp')
