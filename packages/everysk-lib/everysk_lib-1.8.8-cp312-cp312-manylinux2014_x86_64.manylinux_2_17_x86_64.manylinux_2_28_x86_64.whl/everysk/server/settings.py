###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

EVERYSK_SERVER_DEBUG: bool = False

# Used to check access on JSONEndpoints
EVERYSK_SERVER_REST_KEY_NAME: str = 'X-Rest-Key'
EVERYSK_SERVER_REST_KEY_VALUE: str = '12345'

# Used by the GZipMiddleware to compress the response
EVERYSK_SERVER_GZIP_MINIMUM_SIZE: int = 1024
EVERYSK_SERVER_GZIP_COMPRESS_LEVEL: int = 9

# The codes that will be logged by the Logger
EVERYSK_SERVER_CODES_LOG: tuple = (500,)

# URL to use in the redirect response
EVERYSK_SERVER_REDIRECT_URL: str = None

# To enable GZipMiddleware
EVERYSK_SERVER_GZIP_MIDDLEWARE_ENABLED: bool = True

# To enable SecurityMiddleware
EVERYSK_SERVER_SECURITY_MIDDLEWARE_ENABLED: bool = True

# Size of the error message to log in the HTTP error response
# If the error message is larger than this size, it will be truncated
# and the full message will be in the extra context of the log
EVERYSK_SERVER_HTTP_ERROR_MESSAGE_SIZE: int = 256
